import 'dart:async';
import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../utils/constants.dart';

// ─────────────────────────────────────────────────────────
//  Forgot Password Screen
//  Step 1: Email enter karo → Reset link bhejo
//  Step 2: Confirmation dikhao ke email send ho gaya
// ─────────────────────────────────────────────────────────

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen>
    with SingleTickerProviderStateMixin {
  final _emailCtrl = TextEditingController();
  final _formKey   = GlobalKey<FormState>();

  bool _loading   = false;
  bool _sent      = false;  // Step 2: success state
  String? _errorMsg;

  // Resend cooldown
  int _resendCooldown = 0;
  Timer? _cooldownTimer;

  late AnimationController _animCtrl;
  late Animation<double>   _fadeAnim;
  late Animation<Offset>   _slideAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _fadeAnim  = CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(
            begin: const Offset(0, 0.08), end: Offset.zero)
        .animate(
            CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut));
    _animCtrl.forward();
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    _emailCtrl.dispose();
    _cooldownTimer?.cancel();
    super.dispose();
  }

  // ── Send reset email ──────────────────────────────────
  Future<void> _sendReset() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _loading = true; _errorMsg = null; });

    final result =
        await AuthService.sendPasswordReset(_emailCtrl.text.trim());

    if (!mounted) return;
    setState(() => _loading = false);

    if (result.ok) {
      setState(() {
        _sent = true;
        _resendCooldown = 60;
      });
      _startCooldown();
    } else {
      setState(() => _errorMsg = result.error);
    }
  }

  // ── Resend ────────────────────────────────────────────
  Future<void> _resend() async {
    if (_resendCooldown > 0 || _loading) return;
    await _sendReset();
  }

  void _startCooldown() {
    _cooldownTimer?.cancel();
    _cooldownTimer =
        Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) { t.cancel(); return; }
      setState(() {
        if (_resendCooldown > 0) {
          _resendCooldown--;
        } else {
          t.cancel();
        }
      });
    });
  }

  // ── Back to login ─────────────────────────────────────
  void _backToLogin() => Navigator.pop(context);

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor     = isDark ? cBg     : const Color(0xFFF8FAFC);
    final cardColor   = isDark ? cCard   : Colors.white;
    final textColor   = isDark ? cText   : const Color(0xFF1E293B);
    final mutedColor  = isDark ? cMuted  : const Color(0xFF64748B);
    final accentColor = isDark ? cGreen  : const Color(0xFF0EA5E9);
    final borderColor = isDark ? cBorder : const Color(0xFFE2E8F0);

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: bgColor,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_rounded,
              color: textColor, size: 20),
          onPressed: _backToLogin,
        ),
      ),
      body: SafeArea(
        child: FadeTransition(
          opacity: _fadeAnim,
          child: SlideTransition(
            position: _slideAnim,
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 28),
              child: _sent ? _buildSuccessView(
                textColor, mutedColor, accentColor, cardColor, borderColor,
              ) : _buildFormView(
                textColor, mutedColor, accentColor, cardColor, borderColor, isDark,
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ══════════════════════════════════════════════════════
  //  STEP 1: Form View
  // ══════════════════════════════════════════════════════
  Widget _buildFormView(
    Color textColor, Color mutedColor, Color accentColor,
    Color cardColor, Color borderColor, bool isDark,
  ) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 20),

          // ── Lock icon ──────────────────────────────────
          Center(
            child: Container(
              width: 90, height: 90,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    accentColor.withOpacity(0.15),
                    accentColor.withOpacity(0.05),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
                border: Border.all(
                    color: accentColor.withOpacity(0.3), width: 1.5),
              ),
              child: Center(
                child: Icon(Icons.lock_reset_rounded,
                    color: accentColor, size: 40),
              ),
            ),
          ),

          const SizedBox(height: 28),

          // ── Title ──────────────────────────────────────
          Text('Forgot Password?',
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.w800,
                  color: textColor)),

          const SizedBox(height: 10),

          Text(
            'Enter your registered email and we\'ll\nsend you a password reset link.',
            textAlign: TextAlign.center,
            style: TextStyle(
                fontSize: 14, color: mutedColor, height: 1.6),
          ),

          const SizedBox(height: 40),

          // ── Email field ────────────────────────────────
          Text('Email Address',
              style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: mutedColor)),
          const SizedBox(height: 8),

          TextFormField(
            controller: _emailCtrl,
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => _sendReset(),
            style: TextStyle(fontSize: 15, color: textColor),
            decoration: InputDecoration(
              hintText: 'your@email.com',
              hintStyle: TextStyle(color: mutedColor),
              prefixIcon:
                  Icon(Icons.email_outlined, color: mutedColor, size: 20),
              filled: true,
              fillColor: cardColor,
              contentPadding: const EdgeInsets.symmetric(
                  vertical: 16, horizontal: 16),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(color: borderColor),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(color: borderColor),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide:
                    BorderSide(color: accentColor, width: 2),
              ),
              errorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide:
                    const BorderSide(color: cRed, width: 1.5),
              ),
              focusedErrorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide:
                    const BorderSide(color: cRed, width: 2),
              ),
            ),
            validator: (v) {
              if (v == null || v.trim().isEmpty) {
                return 'Please enter your email address';
              }
              final emailRegex =
                  RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
              if (!emailRegex.hasMatch(v.trim())) {
                return 'Please enter a valid email';
              }
              return null;
            },
          ),

          // ── Error message ──────────────────────────────
          if (_errorMsg != null) ...[
            const SizedBox(height: 14),
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
          ],

          const SizedBox(height: 28),

          // ── Send button ────────────────────────────────
          GestureDetector(
            onTap: _loading ? null : _sendReset,
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
                            color: Colors.white, strokeWidth: 2.5))
                    : const Text('Send Reset Link',
                        style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: Colors.white)),
              ),
            ),
          ),

          const SizedBox(height: 24),

          // ── Back to login ──────────────────────────────
          Center(
            child: GestureDetector(
              onTap: _backToLogin,
              child: RichText(
                text: TextSpan(children: [
                  TextSpan(
                    text: 'Remember your password? ',
                    style:
                        TextStyle(fontSize: 14, color: mutedColor),
                  ),
                  TextSpan(
                    text: 'Sign In',
                    style: TextStyle(
                        fontSize: 14,
                        color: accentColor,
                        fontWeight: FontWeight.w700),
                  ),
                ]),
              ),
            ),
          ),

          const SizedBox(height: 40),
        ],
      ),
    );
  }

  // ══════════════════════════════════════════════════════
  //  STEP 2: Success View
  // ══════════════════════════════════════════════════════
  Widget _buildSuccessView(
    Color textColor, Color mutedColor, Color accentColor,
    Color cardColor, Color borderColor,
  ) {
    final email = _emailCtrl.text.trim();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 30),

        // ── Success icon ───────────────────────────────
        Center(
          child: Container(
            width: 100, height: 100,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  const Color(0xFF22C55E).withOpacity(0.2),
                  const Color(0xFF22C55E).withOpacity(0.05),
                ],
              ),
              shape: BoxShape.circle,
              border: Border.all(
                  color: const Color(0xFF22C55E).withOpacity(0.4),
                  width: 2),
            ),
            child: const Center(
              child: Icon(Icons.mark_email_read_rounded,
                  color: Color(0xFF22C55E), size: 46),
            ),
          ),
        ),

        const SizedBox(height: 28),

        Text('Email Sent!',
            textAlign: TextAlign.center,
            style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w800,
                color: textColor)),

        const SizedBox(height: 12),

        RichText(
          textAlign: TextAlign.center,
          text: TextSpan(children: [
            TextSpan(
              text: 'We sent a password reset link to\n',
              style: TextStyle(
                  fontSize: 14, color: mutedColor, height: 1.6),
            ),
            TextSpan(
              text: email,
              style: TextStyle(
                  fontSize: 14,
                  color: accentColor,
                  fontWeight: FontWeight.w700,
                  height: 1.6),
            ),
          ]),
        ),

        const SizedBox(height: 32),

        // ── Info card ──────────────────────────────────
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: cardColor,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: borderColor),
          ),
          child: Column(
            children: [
              _infoRow(Icons.inbox_rounded,
                  'Check your inbox (and spam folder)',
                  mutedColor, accentColor),
              const SizedBox(height: 12),
              _infoRow(Icons.timer_outlined,
                  'Link expires in 1 hour',
                  mutedColor, accentColor),
              const SizedBox(height: 12),
              _infoRow(Icons.open_in_new_rounded,
                  'Click the link to set a new password',
                  mutedColor, accentColor),
            ],
          ),
        ),

        const SizedBox(height: 32),

        // ── Back to login button ───────────────────────
        GestureDetector(
          onTap: _backToLogin,
          child: Container(
            height: 54,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [accentColor, accentColor.withOpacity(0.8)],
              ),
              borderRadius: BorderRadius.circular(14),
              boxShadow: [
                BoxShadow(
                  color: accentColor.withOpacity(0.4),
                  blurRadius: 16,
                  offset: const Offset(0, 6),
                )
              ],
            ),
            child: const Center(
              child: Text('Back to Sign In',
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Colors.white)),
            ),
          ),
        ),

        const SizedBox(height: 20),

        // ── Resend button ──────────────────────────────
        Center(
          child: GestureDetector(
            onTap: _resendCooldown == 0 ? _resend : null,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: _loading
                  ? Text('Sending...',
                      style: TextStyle(
                          fontSize: 14, color: accentColor))
                  : RichText(
                      text: TextSpan(children: [
                        TextSpan(
                          text: "Didn't receive it? ",
                          style: TextStyle(
                              fontSize: 14, color: mutedColor),
                        ),
                        if (_resendCooldown > 0)
                          TextSpan(
                            text: 'Resend in ${_resendCooldown}s',
                            style: TextStyle(
                                fontSize: 14, color: mutedColor),
                          )
                        else
                          TextSpan(
                            text: 'Resend Email',
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

        const SizedBox(height: 40),
      ],
    );
  }

  Widget _infoRow(
      IconData icon, String text, Color mutedColor, Color accentColor) {
    return Row(children: [
      Container(
        width: 32, height: 32,
        decoration: BoxDecoration(
          color: accentColor.withOpacity(0.1),
          shape: BoxShape.circle,
        ),
        child: Center(
          child: Icon(icon, color: accentColor, size: 16),
        ),
      ),
      const SizedBox(width: 12),
      Expanded(
        child: Text(text,
            style: TextStyle(fontSize: 13, color: mutedColor)),
      ),
    ]);
  }
}
