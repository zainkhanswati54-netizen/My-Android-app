import 'package:firebase_auth/firebase_auth.dart';
import 'account_manager.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static final _auth = FirebaseAuth.instance;
  static const _lastLoginKey = 'last_login_timestamp';
  static const _inactiveDays = 7; // 7 din baad auto logout

  // ── Current user ──────────────────────────────────────────
  static User? get currentUser => _auth.currentUser;
  static Stream<User?> get authStateChanges => _auth.authStateChanges();

  // ── Check karo 7 din se zyada hua? ───────────────────────
  static Future<bool> checkInactiveLogout() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final lastLogin = prefs.getInt(_lastLoginKey);
      if (lastLogin == null) return false;
      final lastDate = DateTime.fromMillisecondsSinceEpoch(lastLogin);
      final diff = DateTime.now().difference(lastDate).inDays;
      if (diff >= _inactiveDays) {
        await signOut();
        await prefs.remove(_lastLoginKey);
        return true; // logout hua
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  // ── Login timestamp save karo ─────────────────────────────
  static Future<void> _saveLoginTime() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(
        _lastLoginKey, DateTime.now().millisecondsSinceEpoch);
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
      // Account save karo for switching
      final u = cred.user!;
      await AccountManager.saveAccount(SavedAccount(
        uid: u.uid,
        email: u.email ?? '',
        displayName: u.displayName ?? '',
        initials: AccountManager.getInitials(u.displayName ?? '', u.email ?? ''),
        lastLogin: DateTime.now().millisecondsSinceEpoch,
      ));
      return AuthResult.success(u);
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
      // Account save karo for switching
      final u = cred.user!;
      await AccountManager.saveAccount(SavedAccount(
        uid: u.uid,
        email: u.email ?? '',
        displayName: u.displayName ?? '',
        initials: AccountManager.getInitials(u.displayName ?? '', u.email ?? ''),
        lastLogin: DateTime.now().millisecondsSinceEpoch,
      ));
      return AuthResult.success(u);
    } on FirebaseAuthException catch (e) {
      return AuthResult.error(_friendlyError(e.code));
    } catch (e) {
      return AuthResult.error('Login failed. Please try again.');
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
      case 'operation-not-allowed':  return 'Email sign-in is not enabled. Please contact support.';
      default:                       return 'Something went wrong. Please try again.';
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
