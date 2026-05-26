import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/auth_service.dart';
import '../utils/constants.dart';
import 'studio_screen.dart';
import 'login_screen.dart';
import 'terms_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen>
    with SingleTickerProviderStateMixin {
  final _nameCtrl     = TextEditingController();
  final _emailCtrl    = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmCtrl  = TextEditingController();
  final _formKey      = GlobalKey<FormState>();

  bool _loading       = false;
  bool _googleLoading  = false;
  bool _obscurePass   = true;
  bool _obscureConf   = true;
  bool _agreeTerms    = false;
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
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    if (!_agreeTerms) {
      setState(() => _errorMsg = 'Please agree to the Terms & Conditions to continue.');
      return;
    }
    setState(() { _loading = true; _errorMsg = null; });

    final result = await AuthService.registerWithEmail(
      email:       _emailCtrl.text,
      password:    _passwordCtrl.text,
      displayName: _nameCtrl.text,
    );

    if (!mounted) return;
    setState(() => _loading = false);

    if (result.ok) {
      _goToStudio();
    } else {
      setState(() => _errorMsg = result.error);
    }
  }

  Future<void> _loginGoogle() async {
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
    Navigator.of(context).pushAndRemoveUntil(
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 500),
        pageBuilder: (_, __, ___) => const StudioScreen(),
        transitionsBuilder: (_, anim, __, child) =>
            FadeTransition(opacity: anim, child: child),
      ),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark    = Theme.of(context).brightness == Brightness.dark;
    final bgColor   = cBg;
    final textColor = cText;
    final mutedColor= cMuted;

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: textColor,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
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
                    const SizedBox(height: 10),

                    // ── Title ─────────────────────────────────
                    Text(
                      'Create Account',
                      style: TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.w800,
                          color: textColor),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Join Titan Studio PRO — Always Free',
                      style: TextStyle(fontSize: 14, color: mutedColor),
                    ),

                    const SizedBox(height: 32),
                    // ── Error box ─────────────────────────────
                    if (_errorMsg != null) ...[
                      Builder(builder: (ctx) {
                        final dk = Theme.of(ctx).brightness == Brightness.dark;
                        final red = dk ? cRed : cRed;
                        return Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: red.withOpacity(0.08),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: red.withOpacity(0.3)),
                          ),
                          child: Row(children: [
                            Icon(Icons.error_outline_rounded,
                                color: red, size: 18),
                            const SizedBox(width: 10),
                            Expanded(child: Text(_errorMsg!,
                                style: TextStyle(fontSize: 13, color: red))),
                          ]),
                        );
                      }),
                      const SizedBox(height: 16),
                    ],

                    // ── Name ──────────────────────────────────
                    _buildLabel('Full Name'),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _nameCtrl,
                      textCapitalization: TextCapitalization.words,
                      style: TextStyle(color: Theme.of(context).colorScheme.onSurface, fontSize: 15),
                      decoration: _inputDecor(
                          hint: 'Your full name',
                          icon: Icons.person_outline_rounded),
                      validator: (v) {
                        if (v == null || v.trim().isEmpty) {
                          return 'Name is required';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 16),

                    // ── Email ─────────────────────────────────
                    _buildLabel('Email'),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _emailCtrl,
                      keyboardType: TextInputType.emailAddress,
                      style: TextStyle(color: Theme.of(context).colorScheme.onSurface, fontSize: 15),
                      decoration: _inputDecor(
                          hint: 'you@example.com',
                          icon: Icons.email_outlined),
                      validator: (v) {
                        if (v == null || v.trim().isEmpty) {
                          return 'Email is required';
                        }
                        if (!v.contains('@')) return 'Enter a valid email';
                        return null;
                      },
                    ),

                    const SizedBox(height: 16),

                    // ── Password ──────────────────────────────
                    _buildLabel('Password'),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _passwordCtrl,
                      obscureText: _obscurePass,
                      style: TextStyle(color: Theme.of(context).colorScheme.onSurface, fontSize: 15),
                      decoration: _inputDecor(
                        hint: 'Min. 6 characters',
                        icon: Icons.lock_outline_rounded,
                        suffix: IconButton(
                          icon: Icon(
                            _obscurePass
                                ? Icons.visibility_outlined
                                : Icons.visibility_off_outlined,
                            color: cMuted, size: 20,
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
                    ),

                    const SizedBox(height: 16),

                    // ── Confirm Password ──────────────────────
                    _buildLabel('Confirm Password'),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _confirmCtrl,
                      obscureText: _obscureConf,
                      style: TextStyle(color: Theme.of(context).colorScheme.onSurface, fontSize: 15),
                      decoration: _inputDecor(
                        hint: 'Re-enter password',
                        icon: Icons.lock_outline_rounded,
                        suffix: IconButton(
                          icon: Icon(
                            _obscureConf
                                ? Icons.visibility_outlined
                                : Icons.visibility_off_outlined,
                            color: cMuted, size: 20,
                          ),
                          onPressed: () =>
                              setState(() => _obscureConf = !_obscureConf),
                        ),
                      ),
                      validator: (v) {
                        if (v == null || v.isEmpty) {
                          return 'Please confirm your password';
                        }
                        if (v != _passwordCtrl.text) {
                          return 'Passwords do not match';
                        }
                        return null;
                      },
                      onFieldSubmitted: (_) => _register(),
                    ),

                    const SizedBox(height: 28),

                    // ── Terms & Conditions checkbox ───────────
                    Builder(builder: (context) {
                      final isDark = Theme.of(context).brightness == Brightness.dark;
                      final accent = cGreen;
                      final text2  = cText2;
                      final border = cBorder;
                      return GestureDetector(
                        onTap: () => setState(() => _agreeTerms = !_agreeTerms),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              width: 22, height: 22,
                              decoration: BoxDecoration(
                                color: _agreeTerms ? accent : Colors.transparent,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                    color: _agreeTerms ? accent : border,
                                    width: 2),
                              ),
                              child: _agreeTerms
                                  ? const Icon(Icons.check_rounded,
                                      color: Colors.white, size: 14)
                                  : null,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: RichText(
                                text: TextSpan(
                                  style: TextStyle(
                                      fontSize: 13, color: text2, height: 1.5),
                                  children: [
                                    const TextSpan(text: 'I agree to the '),
                                    WidgetSpan(
                                      child: GestureDetector(
                                        onTap: () => Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder: (_) => const TermsScreen(mustAccept: false),
                                          ),
                                        ),
                                        child: Text(
                                          'Terms & Conditions',
                                          style: TextStyle(
                                            color: accent,
                                            fontWeight: FontWeight.w600,
                                            fontSize: 13,
                                          ),
                                        ),
                                      ),
                                    ),
                                    const TextSpan(
                                        text: ' and Privacy Policy of Titan Studio PRO'),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    }),

                    const SizedBox(height: 20),

                    // ── Register button ───────────────────────
                    _GreenButton(
                      label: 'Create Account',
                      loading: _loading,
                      onTap: _register,
                    ),

                    const SizedBox(height: 20),

                    // ── OR divider ────────────────────────────
                    Builder(builder: (ctx) {
                      final dk = Theme.of(ctx).brightness == Brightness.dark;
                      return Row(children: [
                        Expanded(child: Container(height: 1, color: cBorder)),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 14),
                          child: Text('OR',
                              style: TextStyle(
                                  fontSize: 12,
                                  color: cMuted,
                                  fontWeight: FontWeight.w600)),
                        ),
                        Expanded(child: Container(height: 1, color: cBorder)),
                      ]);
                    }),
                    const SizedBox(height: 16),

                    _GoogleButton(
                      loading: _googleLoading,
                      onTap: _loginGoogle,
                    ),

                    const SizedBox(height: 24),

                    // ── Login link ────────────────────────────
                    Builder(builder: (ctx) {
                      final dk = Theme.of(ctx).brightness == Brightness.dark;
                      return Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                        Text('Already have an account? ',
                            style: TextStyle(fontSize: 14, color: cMuted)),
                        GestureDetector(
                          onTap: () => Navigator.pushReplacement(
                            context,
                            MaterialPageRoute(
                                builder: (_) => const LoginScreen()),
                          ),
                          child: Text('Sign In',
                              style: TextStyle(
                                  fontSize: 14,
                                  color: cGreen,
                                  fontWeight: FontWeight.w700)),
                        ),
                      ]);
                    }),

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

  Widget _buildLabel(String text) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Text(
      text,
      style: TextStyle(
          fontSize: 13, fontWeight: FontWeight.w600,
          color: cText2),
    );
  }

  InputDecoration _inputDecor({
    required String hint,
    required IconData icon,
    Widget? suffix,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor   = cCard;
    final borderColor = cBorder;
    final accentColor = cGreen;
    final mutedColor  = cMuted;
    final redColor    = isDark ? cRed    : cRed;
    return InputDecoration(
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
}

// ── Reusable widgets (same as login_screen) ───────────────────
class _GreenButton extends StatelessWidget {
  final String label;
  final bool loading;
  final VoidCallback onTap;
  const _GreenButton(
      {required this.label, required this.loading, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final accent = cGreen;
    final accent2 = cGreen2;
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
                  : [accent, accent2]),
          borderRadius: BorderRadius.circular(14),
          boxShadow: loading
              ? []
              : [
                  BoxShadow(
                      color: accent.withOpacity(0.35),
                      blurRadius: 16,
                      offset: const Offset(0, 6))
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

class _GoogleButton extends StatelessWidget {
  final bool loading;
  final VoidCallback onTap;
  const _GoogleButton({required this.loading, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = cCard;
    final borderColor = cBorder;
    final textColor = cText;
    final accentColor = cGreen;
    return GestureDetector(
      onTap: loading ? null : onTap,
      child: Container(
        height: 54,
        decoration: BoxDecoration(
          color: cardColor,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: borderColor),
          boxShadow: isDark ? [] : [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
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
                    width: 22, height: 22,
                  ),
                  const SizedBox(width: 12),
                  Text('Continue with Google',
                      style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: textColor)),
                ]),
        ),
      ),
    );
  }
}
