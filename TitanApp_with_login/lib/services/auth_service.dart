import 'package:firebase_auth/firebase_auth.dart';

class AuthService {
  static final _auth = FirebaseAuth.instance;

  // ── Current user ──────────────────────────────────────────
  static User? get currentUser => _auth.currentUser;
  static Stream<User?> get authStateChanges => _auth.authStateChanges();

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
      return AuthResult.success(cred.user!);
    } on FirebaseAuthException catch (e) {
      return AuthResult.error(_friendlyError(e.code));
    } catch (e) {
      return AuthResult.error('Registration failed: $e');
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
      return AuthResult.success(cred.user!);
    } on FirebaseAuthException catch (e) {
      return AuthResult.error(_friendlyError(e.code));
    } catch (e) {
      return AuthResult.error('Login failed: $e');
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
      return AuthResult.error('Reset failed: $e');
    }
  }

  // ── Sign Out ──────────────────────────────────────────────
  static Future<void> signOut() async {
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
