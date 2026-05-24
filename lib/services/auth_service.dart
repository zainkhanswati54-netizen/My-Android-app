import 'dart:convert';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'account_service.dart';
import 'history_service.dart';

class AuthService {
  static final _auth         = FirebaseAuth.instance;
  static final _googleSignIn = GoogleSignIn();
  static const _lastLoginKey = 'last_login_timestamp';
  static const _inactiveDays = 7;

  // ── Current user ──────────────────────────────────────────
  static User? get currentUser => _auth.currentUser;
  static Stream<User?> get authStateChanges => _auth.authStateChanges();

  // ── Check inactive logout ─────────────────────────────────
  static Future<bool> checkInactiveLogout() async {
    try {
      final prefs     = await SharedPreferences.getInstance();
      final lastLogin = prefs.getInt(_lastLoginKey);
      if (lastLogin == null) return false;
      final diff = DateTime.now()
          .difference(DateTime.fromMillisecondsSinceEpoch(lastLogin))
          .inDays;
      if (diff >= _inactiveDays) {
        await signOut();
        await prefs.remove(_lastLoginKey);
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  static Future<void> _saveLoginTime() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_lastLoginKey, DateTime.now().millisecondsSinceEpoch);
  }

  // ── Track user in Admin Dashboard ────────────────────────
  static Future<void> _trackUserInAdmin(User user) async {
    try {
      const dbUrl =
          'https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com';
      final token = await user.getIdToken();
      await http.patch(
        Uri.parse('$dbUrl/admin/users/${user.uid}.json?auth=$token'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email':       user.email ?? '',
          'displayName': user.displayName ?? '',
          'lastActive':  DateTime.now().millisecondsSinceEpoch,
          'createdAt':   user.metadata.creationTime?.millisecondsSinceEpoch ?? 0,
        }),
      );
    } catch (_) {}
  }

  // ── Email + Password: Register ────────────────────────────
  static Future<AuthResult> registerWithEmail({
    required String email,
    required String password,
    required String displayName,
  }) async {
    try {
      final cred = await _auth.createUserWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );
      await cred.user?.updateDisplayName(displayName.trim());
      await cred.user?.reload();
      await _saveLoginTime();
      if (cred.user != null) await AccountService.saveCurrentUser(cred.user!);
      if (cred.user != null) await _trackUserInAdmin(cred.user!);
      // Restore cloud history after login
      HistoryService.restoreFromCloud();
      return AuthResult.success(cred.user!);
    } on FirebaseAuthException catch (e) {
      return AuthResult.error(_friendlyError(e.code));
    } catch (e) {
      return AuthResult.error('Registration failed. Please try again.');
    }
  }

  // ── Email + Password: Login ───────────────────────────────
  static Future<AuthResult> loginWithEmail({
    required String email,
    required String password,
  }) async {
    try {
      final cred = await _auth.signInWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );
      await _saveLoginTime();
      if (cred.user != null) await AccountService.saveCurrentUser(cred.user!);
      if (cred.user != null) await _trackUserInAdmin(cred.user!);
      // Restore cloud history after login
      HistoryService.restoreFromCloud();
      return AuthResult.success(cred.user!);
    } on FirebaseAuthException catch (e) {
      return AuthResult.error(_friendlyError(e.code));
    } catch (e) {
      return AuthResult.error('Login failed. Please try again.');
    }
  }

  // ── Google Sign-In ────────────────────────────────────────
  static Future<AuthResult> signInWithGoogle() async {
    try {
      await _googleSignIn.signOut();
      final googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        return AuthResult.error('Google sign-in cancelled.');
      }
      final googleAuth = await googleUser.authentication;
      if (googleAuth.idToken == null) {
        return AuthResult.error(
            'Google sign-in failed. Please try again or use email login.');
      }
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken:     googleAuth.idToken,
      );
      final cred = await _auth.signInWithCredential(credential);
      await _saveLoginTime();
      if (cred.user != null) await AccountService.saveCurrentUser(cred.user!);
      if (cred.user != null) await _trackUserInAdmin(cred.user!);
      // Restore cloud history after login
      HistoryService.restoreFromCloud();
      return AuthResult.success(cred.user!);
    } on FirebaseAuthException catch (e) {
      return AuthResult.error(_friendlyError(e.code));
    } catch (e) {
      final s = e.toString();
      if (s.contains('10:') || s.contains('DEVELOPER_ERROR')) {
        return AuthResult.error(
            'Google sign-in is not available right now. Please use email login.');
      }
      return AuthResult.error('Google sign-in failed. Please try again.');
    }
  }

  // ── Forgot Password ───────────────────────────────────────
  static Future<AuthResult> sendPasswordReset(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email.trim());
      return AuthResult.success(null);
    } on FirebaseAuthException catch (e) {
      return AuthResult.error(_friendlyError(e.code));
    } catch (e) {
      return AuthResult.error('Reset failed. Please try again.');
    }
  }

  // ── Sign Out ──────────────────────────────────────────────
  static Future<void> signOut() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_lastLoginKey);
    await _googleSignIn.signOut().catchError((_) {});
    await _auth.signOut();
  }

  // ── Firebase error → human readable ──────────────────────
  static String _friendlyError(String code) {
    switch (code) {
      case 'user-not-found':         return 'No account found with this email.';
      case 'wrong-password':         return 'Incorrect password. Please try again.';
      case 'email-already-in-use':   return 'This email is already registered.';
      case 'weak-password':          return 'Password must be at least 6 characters.';
      case 'invalid-email':          return 'Please enter a valid email address.';
      case 'user-disabled':          return 'This account has been disabled.';
      case 'too-many-requests':      return 'Too many attempts. Please try again later.';
      case 'network-request-failed': return 'No internet connection.';
      case 'invalid-credential':     return 'Invalid email or password.';
      case 'account-exists-with-different-credential':
        return 'Account exists with different sign-in method.';
      default: return 'Something went wrong. Please try again.';
    }
  }
}

// ── Result wrapper ────────────────────────────────────────
class AuthResult {
  final bool ok;
  final User? user;
  final String? error;
  const AuthResult._({required this.ok, this.user, this.error});
  factory AuthResult.success(User? u) => AuthResult._(ok: true,  user: u);
  factory AuthResult.error(String msg) => AuthResult._(ok: false, error: msg);
}
