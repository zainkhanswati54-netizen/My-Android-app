import 'dart:convert';
import 'dart:math';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

// ─────────────────────────────────────────────────────────
//  Email OTP Service — FREE
//  Firebase Realtime DB mein OTP store + Gmail SMTP se send
//
//  Flow:
//  1. User register kare
//  2. Firebase mein temp account banao
//  3. 6-digit OTP generate karo, DB mein save karo
//  4. Firebase Cloud Function ya direct SMTP se email bhejo
//  5. User OTP verify kare → account activate ho
//
//  Simple approach: OTP Firebase DB mein store,
//  Email Firebase default system se bhejo
// ─────────────────────────────────────────────────────────

class EmailOtpService {
  static final _auth = FirebaseAuth.instance;
  static const _dbUrl =
      'https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com';
  static const _otpExpiryMinutes = 10;

  // ── Generate 6-digit OTP ──────────────────────────────
  static String _generateOtp() {
    final rng = Random.secure();
    return List.generate(6, (_) => rng.nextInt(10)).join();
  }

  // ── Send OTP — Firebase temp register + email link ────
  static Future<OtpResult> sendOtp({
    required String email,
    required String name,
  }) async {
    try {
      final otp = _generateOtp();
      final expiry = DateTime.now()
          .add(const Duration(minutes: _otpExpiryMinutes))
          .millisecondsSinceEpoch;

      // OTP Firebase DB mein store karo (public path, temp)
      final emailKey =
          email.trim().replaceAll('.', '_').replaceAll('@', '__at__');
      final res = await http.put(
        Uri.parse('$_dbUrl/otp_pending/$emailKey.json'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'otp':    otp,
          'expiry': expiry,
          'email':  email.trim(),
          'name':   name.trim(),
        }),
      );

      if (res.statusCode != 200) {
        return OtpResult.error('Server error. Please try again.');
      }

      // Firebase se password reset jaisi email bhejo
      // (ActionCodeSettings se apni app ka link set hoga)
      // Yahan hum custom SMTP ki jagah Firebase built-in use karte hain
      // OTP email ke liye EmailJS free tier (200/month)
      final emailRes = await http.post(
        Uri.parse('https://api.emailjs.com/api/v1.0/email/send'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'service_id':  'service_a5km29n',
          'template_id': 'template_j1wtcfw',
          'user_id':     '5DMrRgZLgYEyIC3dS',
          'template_params': {
            'to_name':  name.trim(),
            'to_email': email.trim(),
            'otp':      otp,
            'expiry':   '$_otpExpiryMinutes minutes',
            'app_name': 'Titan Studio PRO',
          },
        }),
      );

      if (emailRes.statusCode == 200) {
        return OtpResult.success('OTP sent to ${email.trim()}');
      } else {
        // EmailJS fail hua — OTP DB mein hai, user ko bata do
        return OtpResult.error(
            'Email delivery failed (${emailRes.statusCode}). '
            'Check EmailJS template variables.');
      }
    } catch (e) {
      return OtpResult.error('Network error: $e');
    }
  }

  // ── Verify OTP ────────────────────────────────────────
  static Future<OtpVerifyResult> verifyOtp({
    required String email,
    required String otp,
  }) async {
    try {
      final emailKey =
          email.trim().replaceAll('.', '_').replaceAll('@', '__at__');
      final res = await http.get(
        Uri.parse('$_dbUrl/otp_pending/$emailKey.json'),
      );

      if (res.statusCode != 200 || res.body == 'null') {
        return OtpVerifyResult.error(
            'OTP not found. Please request a new one.');
      }

      final data = jsonDecode(res.body) as Map<String, dynamic>;
      final storedOtp = data['otp'] as String?;
      final expiry    = data['expiry'] as int?;

      if (expiry == null ||
          DateTime.now().millisecondsSinceEpoch > expiry) {
        await _deleteOtp(emailKey);
        return OtpVerifyResult.error(
            'OTP expired. Please request a new one.');
      }

      if (storedOtp != otp.trim()) {
        return OtpVerifyResult.error(
            'Invalid OTP. Please check and try again.');
      }

      await _deleteOtp(emailKey);
      return OtpVerifyResult.success();
    } catch (e) {
      return OtpVerifyResult.error('Verification failed. Try again.');
    }
  }

  // ── Complete Registration ─────────────────────────────
  static Future<OtpVerifyResult> completeRegistration({
    required String email,
    required String password,
    required String name,
    required String otp,
  }) async {
    final v = await verifyOtp(email: email, otp: otp);
    if (!v.ok) return v;

    try {
      final cred = await _auth.createUserWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );
      await cred.user?.updateDisplayName(name.trim());
      await cred.user?.reload();

      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('pending_otp_email');
      await prefs.remove('pending_otp_name');

      return OtpVerifyResult.success(user: cred.user);
    } on FirebaseAuthException catch (e) {
      return OtpVerifyResult.error(_fbError(e.code));
    } catch (e) {
      return OtpVerifyResult.error('Registration failed. Try again.');
    }
  }

  // ── Resend ────────────────────────────────────────────
  static Future<OtpResult> resendOtp({
    required String email,
    required String name,
  }) async {
    final emailKey =
        email.trim().replaceAll('.', '_').replaceAll('@', '__at__');
    await _deleteOtp(emailKey);
    return sendOtp(email: email, name: name);
  }

  static Future<void> _deleteOtp(String emailKey) async {
    try {
      await http.delete(
          Uri.parse('$_dbUrl/otp_pending/$emailKey.json'));
    } catch (_) {}
  }

  static String _fbError(String code) {
    switch (code) {
      case 'email-already-in-use':
        return 'This email is already registered. Please sign in.';
      case 'weak-password':
        return 'Password must be at least 6 characters.';
      case 'invalid-email':
        return 'Please enter a valid email address.';
      case 'network-request-failed':
        return 'No internet connection.';
      default:
        return 'Registration failed. Please try again.';
    }
  }
}

class OtpResult {
  final bool ok;
  final String message;
  const OtpResult._({required this.ok, required this.message});
  factory OtpResult.success(String msg) =>
      OtpResult._(ok: true, message: msg);
  factory OtpResult.error(String msg) =>
      OtpResult._(ok: false, message: msg);
}

class OtpVerifyResult {
  final bool ok;
  final String? error;
  final dynamic user;
  const OtpVerifyResult._({required this.ok, this.error, this.user});
  factory OtpVerifyResult.success({dynamic user}) =>
      OtpVerifyResult._(ok: true, user: user);
  factory OtpVerifyResult.error(String msg) =>
      OtpVerifyResult._(ok: false, error: msg);
}
