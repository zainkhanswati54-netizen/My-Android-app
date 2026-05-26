import 'dart:math';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/email_otp_service.dart';
import '../services/auth_service.dart';
import '../services/account_service.dart';
import '../utils/constants.dart';
import 'studio_screen.dart';

// ─────────────────────────────────────────────────────────
//  Email OTP Verification Screen
//  FREE - EmailJS + Firebase DB
//  Called after register button tap
// ─────────────────────────────────────────────────────────

class EmailOtpScreen extends StatefulWidget {
  final String email;
  final String name;
  final String password;

  const EmailOtpScreen({
    super.key,
    required this.email,
    required this.name,
    required this.password,
  });

  @override
  State<EmailOtpScreen> createState() => _EmailOtpScreenState();
}

class _EmailOtpScreenState extends State<EmailOtpScreen>
    with SingleTickerProviderStateMixin {
  final List<TextEditingController> _ctrls =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _nodes =
      List.generate(6, (_) => FocusNode());

  bool _loading    = false;
  bool _resending  = false;
  String? _errorMsg;
  int _resendCountdown = 60;
  Timer? _timer;

  late AnimationController _shakeCtrl;
  late Animation<double>   _shakeAnim;

  @override
  void initState() {
    super.initState();
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

  String get _otp => _ctrls.map((c) => c.text.trim()).join();

  // ── Digit typed ───────────────────────────────────────
  void _onDigitChanged(int index, String val) {
    if (val.length > 1) {
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
        _verify();
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

  // ── Verify OTP ────────────────────────────────────────
  Future<void> _verify() async {
    if (_otp.length < 6) {
      setState(() => _errorMsg = 'Please enter all 6 digits');
      return;
    }

    setState(() { _loading = true; _errorMsg = null; });

    final result = await EmailOtpService.completeRegistration(
      email:    widget.email,
      password: widget.password,
      name:     widget.name,
      otp:      _otp,
    );

    if (!mounted) return;

    if (result.ok) {
      // Save user to admin + account service
      if (result.user != null) {
        await AccountService.saveCurrentUser(result.user!);
      }
      Navigator.of(context).pushAndRemoveUntil(
        PageRouteBuilder(
          transitionDuration: const Duration(milliseconds: 500),
          pageBuilder: (_, __, ___) => const StudioScreen(),
          transitionsBuilder: (_, anim, __, child) =>
              FadeTransition(opacity: anim, child: child),
        ),
        (r) => false,
      );
    } else {
      setState(() {
        _loading  = false;
        _errorMsg = result.error;
      });
      _shakeCtrl.forward(from: 0);
      for (final c in _ctrls) c.clear();
      _nodes[0].requestFocus();
    }
  }

  // ── Resend OTP ────────────────────────────────────────
  Future<void> _resend() async {
    if (_resendCountdown > 0 || _resending) return;
    setState(() { _resending = true; _errorMsg = null; });

    final result = await EmailOtpService.resendOtp(
      email: widget.email,
      name:  widget.name,
    );

    if (!mounted) return;
    setState(() => _resending = false);

    if (result.ok) {
      _startCountdown();
      for (final c in _ctrls) c.clear();
      _nodes[0].requestFocus();
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: const Text('New OTP sent to your email!'),
        backgroundColor: cGreen,
        behavior: SnackBarBehavior.floating,
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.all(12),
      ));
    } else {
      setState(() => _errorMsg = result.message);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor    = isDark ? cBg    : const Color(0xFFF8FAFC);
    final cardColor  = isDark ? cCard  : Colors.white;
    final textColor  = isDark ? cText  : const Color(0xFF1E293B);
    final mutedColor = isDark ? cMuted : const Color(0xFF64748B);
    final accentColor= isDark ? cGreen : const Color(0xFF0EA5E9);
    final borderColor= isDark ? cBorder: const Color(0xFFE2E8F0);

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: bgColor,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_rounded,
              color: textColor, size: 20),
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

              // ── Email icon ─────────────────────────────
              Center(
                child: Container(
                  width: 86, height: 86,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        accentColor.withOpacity(0.15),
                        accentColor.withOpacity(0.05),
                      ],
                    ),
                    shape: BoxShape.circle,
                    border: Border.all(
                        color: accentColor.withOpacity(0.3),
                        width: 1.5),
                  ),
                  child: Center(
                    child: Icon(Icons.mark_email_unread_rounded,
                        color: accentColor, size: 40),
                  ),
                ),
              ),

              const SizedBox(height: 24),

              Text('Verify Your Email',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: textColor)),

              const SizedBox(height: 10),

              RichText(
                textAlign: TextAlign.center,
                text: TextSpan(children: [
                  TextSpan(
                    text: 'We sent a 6-digit code to\n',
                    style: TextStyle(
                        fontSize: 14, color: mutedColor, height: 1.6),
                  ),
                  TextSpan(
                    text: widget.email,
                    style: TextStyle(
                        fontSize: 14,
                        color: accentColor,
                        fontWeight: FontWeight.w700,
                        height: 1.6),
                  ),
                ]),
              ),

              const SizedBox(height: 40),

              // ── OTP Boxes ──────────────────────────────
              AnimatedBuilder(
                animation: _shakeAnim,
                builder: (_, child) => Transform.translate(
                  offset: Offset(sin(_shakeAnim.value * pi * 6) * 10, 0),
                  child: child,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: List.generate(6, (i) => SizedBox(
                    width: 46, height: 56,
                    child: RawKeyboardListener(
                      focusNode: FocusNode(),
                      onKey: (e) => _onBackspace(i, e),
                      child: TextField(
                        controller: _ctrls[i],
                        focusNode: _nodes[i],
                        keyboardType: TextInputType.number,
                        textAlign: TextAlign.center,
                        maxLength: i == 0 ? 6 : 1,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly
                        ],
                        style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                            color: textColor),
                        decoration: InputDecoration(
                          counterText: '',
                          filled: true,
                          fillColor: cardColor,
                          contentPadding: EdgeInsets.zero,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                            borderSide:
                                BorderSide(color: borderColor),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                            borderSide:
                                BorderSide(color: borderColor),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                            borderSide: BorderSide(
                                color: accentColor, width: 2),
                          ),
                        ),
                        onChanged: (v) => _onDigitChanged(i, v),
                      ),
                    ),
                  )),
                ),
              ),

              const SizedBox(height: 20),

              // ── Error ──────────────────────────────────
              if (_errorMsg != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: cRed.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border:
                        Border.all(color: cRed.withOpacity(0.3)),
                  ),
                  child: Row(children: [
                    const Icon(Icons.error_outline_rounded,
                        color: cRed, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(_errorMsg!,
                          style: const TextStyle(
                              fontSize: 13, color: cRed)),
                    ),
                  ]),
                ),

              const SizedBox(height: 28),

              // ── Verify button ──────────────────────────
              GestureDetector(
                onTap: _loading ? null : _verify,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  height: 54,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: _loading
                          ? [cMuted, cMuted2]
                          : [accentColor, accentColor.withOpacity(0.8)],
                    ),
                    borderRadius: BorderRadius.circular(14),
                    boxShadow: _loading
                        ? []
                        : [
                            BoxShadow(
                              color: accentColor.withOpacity(0.4),
                              blurRadius: 16,
                              offset: const Offset(0, 6),
                            )
                          ],
                  ),
                  child: Center(
                    child: _loading
                        ? const SizedBox(
                            width: 22, height: 22,
                            child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 2.5))
                        : const Text('Verify & Create Account',
                            style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                                color: Colors.white)),
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // ── Resend ─────────────────────────────────
              Center(
                child: GestureDetector(
                  onTap: _resendCountdown == 0 ? _resend : null,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: RichText(
                      text: TextSpan(children: [
                        TextSpan(
                          text: "Didn't receive? ",
                          style: TextStyle(
                              fontSize: 14, color: mutedColor),
                        ),
                        if (_resendCountdown > 0)
                          TextSpan(
                            text: 'Resend in ${_resendCountdown}s',
                            style: TextStyle(
                                fontSize: 14, color: mutedColor),
                          )
                        else if (_resending)
                          TextSpan(
                            text: 'Sending...',
                            style: TextStyle(
                                fontSize: 14, color: accentColor),
                          )
                        else
                          TextSpan(
                            text: 'Resend OTP',
                            style: TextStyle(
                                fontSize: 14,
                                color: accentColor,
                                fontWeight: FontWeight.w700),
                          ),
                      ]),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // ── Spam note ──────────────────────────────
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: accentColor.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                      color: accentColor.withOpacity(0.2)),
                ),
                child: Row(children: [
                  Icon(Icons.info_outline_rounded,
                      color: accentColor, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Check spam/junk folder if not received in inbox.',
                      style: TextStyle(
                          fontSize: 12, color: mutedColor),
                    ),
                  ),
                ]),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
