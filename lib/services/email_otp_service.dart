import 'dart:convert';
import 'dart:math';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

// ─────────────────────────────────────────────────────────
//  Email OTP Service — FREE (Firebase + EmailJS)
//
//  HOW IT WORKS:
//  1. 6-digit random OTP generate karo
//  2. Firebase Realtime DB mein store karo (10 min expiry)
//  3. EmailJS se free email bhejo (200 emails/month free)
//  4. User OTP enter kare → verify karo → register/login
//
//  SETUP STEPS (one time):
//  1. https://www.emailjs.com par free account banao
//  2. Email Service add karo (Gmail etc)
//  3. Template banao:
//     Subject: Your Titan Studio OTP
//     Body: Your OTP is {{otp}}. Valid for 10 minutes.
//  4. Neeche apne IDs update karo
// ─────────────────────────────────────────────────────────

class EmailOtpService {
  // ── EmailJS Config (apne IDs yahan daalo) ─────────────
  static const _emailjsServiceId  = 'YOUR_SERVICE_ID';   // e.g. 'service_abc123'
  static const _emailjsTemplateId = 'YOUR_TEMPLATE_ID';  // e.g. 'template_xyz789'
  static const _emailjsPublicKey  = 'YOUR_PUBLIC_KEY';   // e.g. 'user_XXXXXXXXXXXXXXX'

  // ── Firebase DB URL ────────────────────────────────────
  static const _dbUrl =
      'https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com';

  // ── OTP Settings ───────────────────────────────────────
  static const _otpExpiryMinutes = 10;
  static const _otpLength = 6;

  // ── Local storage keys ─────────────────────────────────
  static const _pendingEmailKey = 'pending_otp_email';
  static const _pendingNameKey  = 'pending_otp_name';

  // ── Generate 6-digit OTP ───────────────────────────────
  static String _generateOtp() {
    final rng = Random.secure();
    return List.generate(_otpLength, (_) => rng.nextInt(10)).join();
  }

  // ── Send OTP to email ──────────────────────────────────
  static Future<OtpResult> sendOtp({
    required String email,
    required String name,
  }) async {
    try {
      final otp = _generateOtp();
      final expiry = DateTime.now()
          .add(const Duration(minutes: _otpExpiryMinutes))
          .millisecondsSinceEpoch;

      // 1. Store OTP in Firebase DB (no auth needed for this path)
      final emailKey = email.replaceAll('.', '_').replaceAll('@', '__');
      final storeRes = await http.put(
        Uri.parse('$_dbUrl/otp_store/$emailKey.json'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'otp':    otp,
          'expiry': expiry,
          'email':  email,
          'name':   name,
        }),
      );

      if (storeRes.statusCode != 200) {
        return OtpResult.error('Failed to store OTP. Please try again.');
      }

      // 2. Send email via EmailJS (free 200/month)
      final emailRes = await http.post(
        Uri.parse('https://api.emailjs.com/api/v1.0/email/send'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'service_id':  _emailjsServiceId,
          'template_id': _emailjsTemplateId,
          'user_id':     _emailjsPublicKey,
          'template_params': {
            'to_name':  name,
            'to_email': email,
            'otp':      otp,
            'expiry':   '$_otpExpiryMinutes minutes',
            'app_name': 'Titan Studio PRO',
          },
        }),
      );

      if (emailRes.statusCode == 200) {
        // Save email/name locally for after OTP verification
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_pendingEmailKey, email);
        await prefs.setString(_pendingNameKey, name);
        return OtpResult.success('OTP sent to $email');
      } else {
        return OtpResult.error('Email delivery failed. Check your email address.');
      }
    } catch (e) {
      return OtpResult.error('Network error. Please check your connection.');
    }
  }

  // ── Verify OTP ─────────────────────────────────────────
  static Future<OtpVerifyResult> verifyOtp({
    required String email,
    required String otp,
  }) async {
    try {
      final emailKey = email.replaceAll('.', '_').replaceAll('@', '__');
      final res = await http.get(
        Uri.parse('$_dbUrl/otp_store/$emailKey.json'),
      );

      if (res.statusCode != 200 || res.body == 'null') {
        return OtpVerifyResult.error('OTP not found. Please request a new one.');
      }

      final data = jsonDecode(res.body) as Map<String, dynamic>;
      final storedOtp    = data['otp'] as String?;
      final expiry       = data['expiry'] as int?;

      // Check expiry
      if (expiry == null ||
          DateTime.now().millisecondsSinceEpoch > expiry) {
        await _deleteOtp(emailKey);
        return OtpVerifyResult.error('OTP expired. Please request a new one.');
      }

      // Check OTP match
      if (storedOtp != otp.trim()) {
        return OtpVerifyResult.error('Invalid OTP. Please check and try again.');
      }

      // ✅ OTP correct — delete it (one-time use)
      await _deleteOtp(emailKey);
      return OtpVerifyResult.success();
    } catch (e) {
      return OtpVerifyResult.error('Verification failed. Please try again.');
    }
  }

  // ── Complete Registration after OTP verify ─────────────
  static Future<OtpVerifyResult> completeRegistration({
    required String email,
    required String password,
    required String name,
    required String otp,
  }) async {
    // 1. Verify OTP first
    final verifyResult = await verifyOtp(email: email, otp: otp);
    if (!verifyResult.ok) return verifyResult;

    // 2. Create Firebase account
    try {
      final auth = FirebaseAuth.instance;
      final cred = await auth.createUserWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );
      await cred.user?.updateDisplayName(name.trim());
      await cred.user?.reload();

      // Clean up pending keys
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_pendingEmailKey);
      await prefs.remove(_pendingNameKey);

      return OtpVerifyResult.success(user: cred.user);
    } on FirebaseAuthException catch (e) {
      return OtpVerifyResult.error(_firebaseError(e.code));
    } catch (e) {
      return OtpVerifyResult.error('Registration failed. Please try again.');
    }
  }

  // ── Resend OTP ─────────────────────────────────────────
  static Future<OtpResult> resendOtp({
    required String email,
    required String name,
  }) async {
    // Delete old OTP first
    final emailKey = email.replaceAll('.', '_').replaceAll('@', '__');
    await _deleteOtp(emailKey);
    // Send new one
    return sendOtp(email: email, name: name);
  }

  // ── Delete OTP from DB ─────────────────────────────────
  static Future<void> _deleteOtp(String emailKey) async {
    try {
      await http.delete(
        Uri.parse('$_dbUrl/otp_store/$emailKey.json'),
      );
    } catch (_) {}
  }

  // ── Firebase error messages ────────────────────────────
  static String _firebaseError(String code) {
    switch (code) {
      case 'email-already-in-use': return 'This email is already registered. Please sign in.';
      case 'weak-password':        return 'Password must be at least 6 characters.';
      case 'invalid-email':        return 'Please enter a valid email address.';
      case 'network-request-failed': return 'No internet connection.';
      default: return 'Registration failed. Please try again.';
    }
  }
}

// ── Result classes ─────────────────────────────────────────
class OtpResult {
  final bool ok;
  final String message;
  const OtpResult._({required this.ok, required this.message});
  factory OtpResult.success(String msg) => OtpResult._(ok: true,  message: msg);
  factory OtpResult.error(String msg)   => OtpResult._(ok: false, message: msg);
}

class OtpVerifyResult {
  final bool ok;
  final String? error;
  final dynamic user; // FirebaseAuth User
  const OtpVerifyResult._({required this.ok, this.error, this.user});
  factory OtpVerifyResult.success({dynamic user}) =>
      OtpVerifyResult._(ok: true, user: user);
  factory OtpVerifyResult.error(String msg) =>
      OtpVerifyResult._(ok: false, error: msg);
}
