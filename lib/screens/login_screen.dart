import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:io';
import '../services/auth_service.dart';
import '../utils/constants.dart';
import 'register_screen.dart';
import 'studio_screen.dart';
import 'admin_dashboard_screen.dart';

// Google Sign-In is handled in AuthService via google_sign_in package

class LoginScreen extends StatefulWidget {
  final bool showInactiveMessage;
  final String? prefillEmail;
  const LoginScreen({super.key, this.showInactiveMessage = false, this.prefillEmail});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with SingleTickerProviderStateMixin {
  final _emailCtrl    = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _formKey      = GlobalKey<FormState>();

  bool _loading        = false;
  bool _googleLoading  = false;
  bool _obscurePass    = true;
  String? _errorMsg;

  late AnimationController _animCtrl;
  late Animation<double>   _fadeAnim;
  late Animation<Offset>   _slideAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 700));
    _fadeAnim  = CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(begin: const Offset(0, 0.08), end: Offset.zero)
        .animate(CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut));
    _animCtrl.forward();
    if (widget.prefillEmail != null && widget.prefillEmail!.isNotEmpty) {
      _emailCtrl.text = widget.prefillEmail!;
    }
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<bool> _hasInternet() async {
    try {
      final r = await InternetAddress.lookup('google.com')
          .timeout(const Duration(seconds: 5));
      return r.isNotEmpty && r.first.rawAddress.isNotEmpty;
    } catch (_) {
      return false;
    }
  }

  void _showNoInternet() {
    setState(() => _errorMsg = null);
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: cBg2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          Container(
            width: 64, height: 64,
            decoration: BoxDecoration(
              color: cAmber.withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(color: cAmber.withOpacity(0.4)),
            ),
            child: const Icon(Icons.wifi_off_rounded, color: cAmber, size: 30),
          ),
          const SizedBox(height: 16),
          Text('No Internet Connection',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800,
                  color: cText),
              textAlign: TextAlign.center),
          const SizedBox(height: 8),
          Text('Please turn on WiFi or mobile data to continue.',
              style: TextStyle(fontSize: 13,
                  color: cText2, height: 1.5),
              textAlign: TextAlign.center),
          const SizedBox(height: 20),
          GestureDetector(
            onTap: () => Navigator.pop(context),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                gradient: kNeonGradient,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(child: Text('OK',
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700))),
            ),
          ),
        ]),
      ),
    );
  }

  Future<void> _loginEmail() async {
    if (!_formKey.currentState!.validate()) return;
    if (!await _hasInternet()) { _showNoInternet(); return; }
    setState(() { _loading = true; _errorMsg = null; });

    final result = await AuthService.loginWithEmail(
      email:    _emailCtrl.text,
      password: _passwordCtrl.text,
    );

    if (!mounted) return;
    setState(() => _loading = false);

    if (result.ok) {
      _goToStudio();
    } else {
      setState(() => _errorMsg = result.error);
    }
  }

  Future<void> _forgotPassword() async {
    final email = _emailCtrl.text.trim();
    if (email.isEmpty) {
      setState(() => _errorMsg = 'Enter your email above first.');
      return;
    }
    final result = await AuthService.sendPasswordReset(email);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(result.ok
          ? 'Reset link sent to $email'
          : result.error ?? 'Failed'),
      backgroundColor: result.ok
          ? (cGreen)
          : (cRed),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.all(12),
    ));
  }

  Future<void> _loginGoogle() async {
    if (!await _hasInternet()) { _showNoInternet(); return; }
    setState(() => _googleLoading = true);
    final result = await AuthService.signInWithGoogle();
    if (!mounted) return;
    setState(() => _googleLoading = false);
    if (result.ok) {
      _goToStudio();
    } else {
      setState(() => _errorMsg = result.error);
    }
  }

  void _goToStudio() {
    Navigator.of(context).pushReplacement(
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 500),
        pageBuilder: (_, __, ___) => const StudioScreen(),
        transitionsBuilder: (_, anim, __, child) =>
            FadeTransition(opacity: anim, child: child),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Dark theme only
    const isDark = true;
    final bgColor     = cBg;
    final cardColor   = cCard;
    final textColor   = cText;
    final text2Color  = cText2;
    final mutedColor  = cMuted;
    final borderColor = cBorder;
    final accentColor = cGreen;
    final redColor    = cRed;

    return Scaffold(
      backgroundColor: bgColor,
      body: SafeArea(
        child: FadeTransition(
          opacity: _fadeAnim,
          child: SlideTransition(
            position: _slideAnim,
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 60),

                    // ── Logo ──────────────────────────
                    Center(
                      child: Container(
                        width: 80, height: 80,
                        decoration: BoxDecoration(
                          color: cardColor,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: borderColor),
                          boxShadow: [
                            BoxShadow(
                              color: accentColor.withOpacity(0.25),
                              blurRadius: 30,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(18),
                          child: Image.asset(
                            'assets/icons/logo.png',
                            fit: BoxFit.contain,
                            errorBuilder: (_, __, ___) => Center(
                              child: Text('T',
                                  style: TextStyle(
                                      fontSize: 40,
                                      fontWeight: FontWeight.w900,
                                      color: textColor)),
                            ),
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 20),

                    Text(
                      'Welcome Back',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 26, fontWeight: FontWeight.w800,
                        color: textColor,
                      ),
                    ),
                    const SizedBox(height: 6),
                    _SecretTitleText(textColor: mutedColor),

                    const SizedBox(height: 40),

                    // ── Inactive logout message ──────────────
                    if (widget.showInactiveMessage) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFF9800).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                              color: const Color(0xFFFF9800).withOpacity(0.4)),
                        ),
                        child: Row(children: [
                          const Icon(Icons.access_time_rounded,
                              color: Color(0xFFFF9800), size: 18),
                          const SizedBox(width: 10),
                          const Expanded(
                            child: Text(
                              'You were logged out due to 7 days of inactivity.',
                              style: TextStyle(
                                  fontSize: 13, color: Color(0xFFFF9800)),
                            ),
                          ),
                        ]),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // ── Error box ─────────────────────────────
                    if (_errorMsg != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: redColor.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: redColor.withOpacity(0.3)),
                        ),
                        child: Row(children: [
                          Icon(Icons.error_outline_rounded,
                              color: redColor, size: 18),
                          const SizedBox(width: 10),
                          Expanded(child: Text(_errorMsg!,
                              style: TextStyle(
                                  fontSize: 13, color: redColor))),
                        ]),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // ── Email field ───────────────────────────
                    _buildLabel('Email', text2Color),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _emailCtrl,
                      keyboardType: TextInputType.emailAddress,
                      style: TextStyle(color: textColor, fontSize: 15),
                      decoration: _inputDecor(
                          hint: 'you@example.com',
                          icon: Icons.email_outlined,
                          isDark: isDark,
                          cardColor: cardColor,
                          borderColor: borderColor,
                          accentColor: accentColor,
                          mutedColor: mutedColor,
                          redColor: redColor),
                      validator: (v) {
                        if (v == null || v.trim().isEmpty) {
                          return 'Email is required';
                        }
                        if (!v.contains('@')) return 'Enter a valid email';
                        return null;
                      },
                    ),

                    const SizedBox(height: 18),

                    // ── Password field ────────────────────────
                    _buildLabel('Password', text2Color),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _passwordCtrl,
                      obscureText: _obscurePass,
                      style: TextStyle(color: textColor, fontSize: 15),
                      decoration: _inputDecor(
                        hint: '••••••••',
                        icon: Icons.lock_outline_rounded,
                        isDark: isDark,
                        cardColor: cardColor,
                        borderColor: borderColor,
                        accentColor: accentColor,
                        mutedColor: mutedColor,
                        redColor: redColor,
                        suffix: IconButton(
                          icon: Icon(
                            _obscurePass
                                ? Icons.visibility_outlined
                                : Icons.visibility_off_outlined,
                            color: mutedColor, size: 20,
                          ),
                          onPressed: () =>
                              setState(() => _obscurePass = !_obscurePass),
                        ),
                      ),
                      validator: (v) {
                        if (v == null || v.isEmpty) return 'Password is required';
                        if (v.length < 6) return 'Minimum 6 characters';
                        return null;
                      },
                      onFieldSubmitted: (_) => _loginEmail(),
                    ),

                    // ── Forgot password ───────────────────────
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: _forgotPassword,
                        style: TextButton.styleFrom(
                            padding: const EdgeInsets.symmetric(
                                vertical: 4, horizontal: 0)),
                        child: Text('Forgot password?',
                            style: TextStyle(
                                fontSize: 13,
                                color: accentColor,
                                fontWeight: FontWeight.w600)),
                      ),
                    ),

                    const SizedBox(height: 8),

                    // ── Login button ──────────────────────────
                    _GreenButton(
                      label: 'Sign In',
                      loading: _loading,
                      onTap: _loginEmail,
                      isDark: isDark,
                    ),

                    const SizedBox(height: 20),

                    // ── OR divider ────────────────────────────
                    Row(children: [
                      Expanded(child: Container(height: 1, color: borderColor)),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 14),
                        child: Text('OR',
                            style: TextStyle(
                                fontSize: 12,
                                color: mutedColor,
                                fontWeight: FontWeight.w600)),
                      ),
                      Expanded(child: Container(height: 1, color: borderColor)),
                    ]),

                    const SizedBox(height: 16),

                    // ── Google Sign-In button ─────────────────
                    _GoogleButton(
                      loading: _googleLoading,
                      onTap: _loginGoogle,
                      isDark: isDark,
                      cardColor: cardColor,
                      borderColor: borderColor,
                      textColor: textColor,
                      accentColor: accentColor,
                    ),

                    const SizedBox(height: 24),

                    // ── Register link ─────────────────────────
                    Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                      Text("Don't have an account? ",
                          style: TextStyle(fontSize: 14, color: mutedColor)),
                      GestureDetector(
                        onTap: () => Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (_) => const RegisterScreen()),
                        ),
                        child: Text('Sign Up',
                            style: TextStyle(
                                fontSize: 14,
                                color: accentColor,
                                fontWeight: FontWeight.w700)),
                      ),
                    ]),

                    const SizedBox(height: 40),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLabel(String text, Color color) => Text(
    text,
    style: TextStyle(
        fontSize: 13, fontWeight: FontWeight.w600, color: color),
  );

  InputDecoration _inputDecor({
    required String hint,
    required IconData icon,
    required bool isDark,
    required Color cardColor,
    required Color borderColor,
    required Color accentColor,
    required Color mutedColor,
    required Color redColor,
    Widget? suffix,
  }) =>
      InputDecoration(
        hintText: hint,
        hintStyle: TextStyle(color: mutedColor.withOpacity(0.6), fontSize: 14),
        prefixIcon: Icon(icon, color: mutedColor, size: 20),
        suffixIcon: suffix,
        filled: true,
        fillColor: cardColor,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
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
          borderSide: BorderSide(color: accentColor, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: redColor),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: redColor, width: 1.5),
        ),
        errorStyle: TextStyle(color: redColor, fontSize: 12),
      );
}

// ── Reusable green button ─────────────────────────────────────
class _GreenButton extends StatelessWidget {
  final String label;
  final bool loading;
  final bool isDark;
  final VoidCallback onTap;
  const _GreenButton(
      {required this.label, required this.loading,
       required this.onTap, required this.isDark});

  @override
  Widget build(BuildContext context) {
    final accentColor = cGreen;
    final accent2Color = cGreen2;
    return GestureDetector(
      onTap: loading ? null : () {
        HapticFeedback.lightImpact();
        onTap();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        height: 54,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: loading
                ? [cMuted, cMuted2]
                : [accentColor, accent2Color],
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
          ),
          borderRadius: BorderRadius.circular(14),
          boxShadow: loading
              ? []
              : [
                  BoxShadow(
                      color: accentColor.withOpacity(0.35),
                      blurRadius: 20,
                      offset: const Offset(0, 6)),
                ],
        ),
        child: Center(
          child: loading
              ? const SizedBox(
                  width: 22, height: 22,
                  child: CircularProgressIndicator(
                      color: Colors.white, strokeWidth: 2.5))
              : Text(label,
                  style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Colors.white)),
        ),
      ),
    );
  }
}

// ── Google sign-in button ─────────────────────────────────────
class _GoogleButton extends StatelessWidget {
  final bool loading;
  final bool isDark;
  final Color cardColor;
  final Color borderColor;
  final Color textColor;
  final Color accentColor;
  final VoidCallback onTap;
  const _GoogleButton({
    required this.loading, required this.onTap,
    required this.isDark, required this.cardColor,
    required this.borderColor, required this.textColor,
    required this.accentColor,
  });

  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: loading ? null : onTap,
        child: Container(
          height: 54,
          decoration: BoxDecoration(
            color: cardColor,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: borderColor),
            boxShadow: [],
          ),
          child: Center(
            child: loading
                ? SizedBox(
                    width: 22, height: 22,
                    child: CircularProgressIndicator(
                        color: accentColor, strokeWidth: 2.5))
                : Row(mainAxisSize: MainAxisSize.min, children: [
                    Image.asset(
                      'assets/icons/google_logo.png',
                      width: 22,
                      height: 22,
                    ),
                    const SizedBox(width: 12),
                    Text(
                      'Continue with Google',
                      style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: textColor),
                    ),
                  ]),
          ),
        ),
      );
}

// ═══════════════════════════════════════════════════════
//  SECRET ADMIN — 10 taps on subtitle → Admin Dashboard
// ═══════════════════════════════════════════════════════

class _SecretTitleText extends StatefulWidget {
  final Color textColor;
  const _SecretTitleText({required this.textColor});
  @override
  State<_SecretTitleText> createState() => _SecretTitleTextState();
}

class _SecretTitleTextState extends State<_SecretTitleText> {
  int _taps = 0;
  static const int _required = 10;

  void _onTap() {
    _taps++;
    if (_taps >= _required) {
      _taps = 0;
      Navigator.push(
        context,
        PageRouteBuilder(
          transitionDuration: const Duration(milliseconds: 400),
          pageBuilder: (_, __, ___) => const AdminDashboardScreen(),
          transitionsBuilder: (_, anim, __, child) => FadeTransition(
            opacity: CurvedAnimation(parent: anim, curve: Curves.easeOut),
            child: child,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _onTap,
      behavior: HitTestBehavior.opaque,
      child: Text(
        'Sign in to Titan Studio PRO',
        textAlign: TextAlign.center,
        style: TextStyle(
          fontSize: 14,
          color: widget.textColor,
          fontWeight: FontWeight.w400,
        ),
      ),
    );
  }
}
