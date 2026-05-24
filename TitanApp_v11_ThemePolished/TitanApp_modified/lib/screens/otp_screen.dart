import 'dart:math';
import 'dart:async';
kage:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../utils/constants.dart';
import 'studio_screen.dart';

// ─────────────────────────────────────────────────────────
//  OTP Verification Screen
//  - Firebase phone auth se OTP bhejna
//  - 6-digit OTP auto-read (SMS Retriever concept)
//  - Resend timer (60 sec)
//  - Auto verify jab 6 digits fill hon
// ─────────────────────────────────────────────────────────

class OtpScreen extends StatefulWidget {
  final String phoneNumber;   // e.g. "+923001234567"
  final String verificationId;
  final int? resendToken;

  const OtpScreen({
    super.key,
    required this.phoneNumber,
    required this.verificationId,
    this.resendToken,
  });

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen>
    with SingleTickerProviderStateMixin {
  final _auth = FirebaseAuth.instance;
  final List<TextEditingController> _ctrls =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _nodes =
      List.generate(6, (_) => FocusNode());

  bool _loading       = false;
  bool _resending     = false;
  String? _errorMsg;
  int _resendCountdown = 60;
  Timer? _timer;
  late String _verificationId;
  int? _resendToken;

  late AnimationController _shakeCtrl;
  late Animation<double> _shakeAnim;

  @override
  void initState() {
    super.initState();
    _verificationId = widget.verificationId;
    _resendToken    = widget.resendToken;
    _startCountdown();

    _shakeCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 400));
    _shakeAnim = Tween<double>(begin: 0, end: 1).animate(
        CurvedAnimation(parent: _shakeCtrl, curve: Curves.elasticIn));
  }

  void _startCountdown() {
    _timer?.cancel();
    setState(() => _resendCountdown = 60);
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) { t.cancel(); return; }
      setState(() {
        if (_resendCountdown > 0) {
          _resendCountdown--;
        } else {
          t.cancel();
        }
      });
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    for (final c in _ctrls) c.dispose();
    for (final n in _nodes) n.dispose();
    _shakeCtrl.dispose();
    super.dispose();
  }

  String get _otp =>
      _ctrls.map((c) => c.text.trim()).join();

  // ── When digit typed ──────────────────────────────────
  void _onDigitChanged(int index, String val) {
    if (val.length > 1) {
      // Paste case: distribute digits
      final digits = val.replaceAll(RegExp(r'\D'), '');
      for (int i = 0; i < 6 && i < digits.length; i++) {
        _ctrls[i].text = digits[i];
      }
      if (digits.length >= 6) {
        FocusScope.of(context).unfocus();
        _verify();
      } else if (digits.length < 6) {
        _nodes[digits.length.clamp(0, 5)].requestFocus();
      }
      return;
    }

    if (val.isNotEmpty) {
      if (index < 5) {
        _nodes[index + 1].requestFocus();
      } else {
        FocusScope.of(context).unfocus();
        _verify(); // auto-verify on last digit
      }
    }
  }

  void _onBackspace(int index, RawKeyEvent event) {
    if (event is RawKeyDownEvent &&
        event.logicalKey == LogicalKeyboardKey.backspace &&
        _ctrls[index].text.isEmpty &&
        index > 0) {
      _nodes[index - 1].requestFocus();
    }
  }

  // ── Verify OTP ─────────────────────────────────────────
  Future<void> _verify() async {
    if (_otp.length < 6) {
      setState(() => _errorMsg = 'Please enter all 6 digits');
      return;
    }

    setState(() { _loading = true; _errorMsg = null; });
    try {
      final credential = PhoneAuthProvider.credential(
        verificationId: _verificationId,
        smsCode: _otp,
      );
      await _auth.signInWithCredential(credential);
      if (!mounted) return;
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const StudioScreen()),
        (r) => false,
      );
    } on FirebaseAuthException catch (e) {
      if (!mounted) return;
      setState(() {
        _loading  = false;
        _errorMsg = e.code == 'invalid-verification-code'
            ? 'Invalid OTP. Please check and try again.'
            : e.code == 'session-expired'
                ? 'OTP expired. Please request a new one.'
                : 'Verification failed. Try again.';
      });
      // Shake animation on error
      _shakeCtrl.forward(from: 0);
      // Clear boxes
      for (final c in _ctrls) c.clear();
      _nodes[0].requestFocus();
    } catch (e) {
      if (!mounted) return;
      setState(() { _loading = false; _errorMsg = 'Error: $e'; });
    }
  }

  // ── Resend OTP ─────────────────────────────────────────
  Future<void> _resend() async {
    if (_resendCountdown > 0 || _resending) return;
    setState(() => _resending = true);

    await _auth.verifyPhoneNumber(
      phoneNumber: widget.phoneNumber,
      forceResendingToken: _resendToken,
      timeout: const Duration(seconds: 60),
      verificationCompleted: (credential) async {
        // Auto-verify on supported devices
        await _auth.signInWithCredential(credential);
        if (!mounted) return;
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const StudioScreen()),
          (r) => false,
        );
      },
      verificationFailed: (e) {
        if (!mounted) return;
        setState(() {
          _resending = false;
          _errorMsg  = 'Resend failed: ${e.message}';
        });
      },
      codeSent: (vId, token) {
        if (!mounted) return;
        setState(() {
          _verificationId = vId;
          _resendToken    = token;
          _resending      = false;
          _errorMsg       = null;
        });
        _startCountdown();
        for (final c in _ctrls) c.clear();
        _nodes[0].requestFocus();
      },
      codeAutoRetrievalTimeout: (_) {},
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cBg,
      appBar: AppBar(
        backgroundColor: cBg,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded,
              color: cText, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),

              // ── Icon ──────────────────────────────────────
              Center(
                child: Container(
                  width: 80, height: 80,
                  decoration: BoxDecoration(
                    color: cGreen.withOpacity(0.1),
                    shape: BoxShape.circle,
                    border: Border.all(color: cGreen.withOpacity(0.3)),
                  ),
                  child: const Center(
                    child: SvgPicture.asset('assets/svg/icon_otp.svg', width: 40, height: 40, colorFilter: const ColorFilter.mode(Color(0xFF00FFFF), BlendMode.srcIn)),
                  ),
                ),
              ),

              const SizedBox(height: 24),

              const Text('Verify Your Number',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: cText)),

              const SizedBox(height: 10),

              Text(
                'Enter the 6-digit OTP sent to\n${widget.phoneNumber}',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 14, color: cMuted, height: 1.5),
              ),

              const SizedBox(height: 40),

              // ── OTP boxes ─────────────────────────────────
              AnimatedBuilder(
                animation: _shakeAnim,
                builder: (_, child) => Transform.translate(
                  offset: Offset(
                      sin(_shakeAnim.value * pi * 6) * 10, 0),
                  child: child,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: List.generate(
                    6,
                    (i) => SizedBox(
                      width: 46, height: 56,
                      child: RawKeyboardListener(
                        focusNode: FocusNode(),
                        onKey: (e) => _onBackspace(i, e),
                        child: TextField(
                          controller: _ctrls[i],
                          focusNode: _nodes[i],
                          keyboardType: TextInputType.number,
                          textAlign: TextAlign.center,
                          maxLength: i == 0 ? 6 : 1, // first box allows paste
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly
                          ],
                          style: const TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                              color: cText),
                          decoration: InputDecoration(
                            counterText: '',
                            filled: true,
                            fillColor: cCard,
                            contentPadding: EdgeInsets.zero,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(14),
                              borderSide:
                                  const BorderSide(color: cBorder),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(14),
                              borderSide:
                                  const BorderSide(color: cBorder),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(14),
                              borderSide: const BorderSide(
                                  color: cGreen, width: 2),
                            ),
                          ),
                          onChanged: (v) => _onDigitChanged(i, v),
                        ),
                      ),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // ── Error message ──────────────────────────────
              if (_errorMsg != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: cRed.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: cRed.withOpacity(0.3)),
                  ),
                  child: Text(_errorMsg!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                          fontSize: 13, color: cRed)),
                ),

              const SizedBox(height: 28),

              // ── Verify button ──────────────────────────────
              GestureDetector(
                onTap: _loading ? null : _verify,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  height: 54,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: _loading
                          ? [cMuted, cMuted2]
                          : [cGreen, cGreen2],
                    ),
                    borderRadius: BorderRadius.circular(14),
                    boxShadow: _loading
                        ? []
                        : [
                            BoxShadow(
                                color: cGreen.withOpacity(0.35),
                                blurRadius: 16,
                                offset: const Offset(0, 6))
                          ],
                  ),
                  child: Center(
                    child: _loading
                        ? const SizedBox(
                            width: 22, height: 22,
                            child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 2.5))
                        : const Text('Verify OTP',
                            style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                                color: Colors.white)),
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // ── Resend ─────────────────────────────────────
              Center(
                child: GestureDetector(
                  onTap: _resendCountdown == 0 ? _resend : null,
                  child: RichText(
                    text: TextSpan(
                      children: [
                        const TextSpan(
                          text: "Didn't receive? ",
                          style: TextStyle(fontSize: 14, color: cMuted),
                        ),
                        if (_resendCountdown > 0)
                          TextSpan(
                            text: 'Resend in ${_resendCountdown}s',
                            style: const TextStyle(
                                fontSize: 14, color: cMuted),
                          )
                        else if (_resending)
                          const TextSpan(
                            text: 'Sending...',
                            style: TextStyle(
                                fontSize: 14, color: cGreen),
                          )
                        else
                          const TextSpan(
                            text: 'Resend OTP',
                            style: TextStyle(
                                fontSize: 14,
                                color: cGreen,
                                fontWeight: FontWeight.w700),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
