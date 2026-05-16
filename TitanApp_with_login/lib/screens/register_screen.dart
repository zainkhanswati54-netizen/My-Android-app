import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../utils/constants.dart';
import 'studio_screen.dart';
import 'login_screen.dart';

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
  bool _googleLoading = false;
  bool _obscurePass   = true;
  bool _obscureConf   = true;
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

  Future<void> _googleRegister() async {
    setState(() { _googleLoading = true; _errorMsg = null; });
    final result = await AuthService.loginWithGoogle();
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
    return Scaffold(
      backgroundColor: cBg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: cText,
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
                    const Text(
                      'Create Account',
                      style: TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.w800,
                          color: cText),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Join Titan Studio PRO — Always Free',
                      style: TextStyle(fontSize: 14, color: cMuted),
                    ),

                    const SizedBox(height: 32),

                    // ── Error box ─────────────────────────────
                    if (_errorMsg != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: cRed.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: cRed.withOpacity(0.3)),
                        ),
                        child: Row(children: [
                          const Icon(Icons.error_outline_rounded,
                              color: cRed, size: 18),
                          const SizedBox(width: 10),
                          Expanded(child: Text(_errorMsg!,
                              style:
                                  const TextStyle(fontSize: 13, color: cRed))),
                        ]),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // ── Name ──────────────────────────────────
                    _buildLabel('Full Name'),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _nameCtrl,
                      textCapitalization: TextCapitalization.words,
                      style: const TextStyle(color: cText, fontSize: 15),
                      decoration: _inputDecor(
                          hint: 'Zain Khan',
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
                      style: const TextStyle(color: cText, fontSize: 15),
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
                      style: const TextStyle(color: cText, fontSize: 15),
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
                      style: const TextStyle(color: cText, fontSize: 15),
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

                    // ── Register button ───────────────────────
                    _GreenButton(
                      label: 'Create Account',
                      loading: _loading,
                      onTap: _register,
                    ),

                    const SizedBox(height: 20),

                    // ── Divider ───────────────────────────────
                    Row(children: [
                      const Expanded(child: Divider(color: cBorder)),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Text('or',
                            style: TextStyle(
                                fontSize: 12,
                                color: cMuted.withOpacity(0.8))),
                      ),
                      const Expanded(child: Divider(color: cBorder)),
                    ]),

                    const SizedBox(height: 20),

                    // ── Google button ─────────────────────────
                    _GoogleButton(
                      loading: _googleLoading,
                      onTap: _googleRegister,
                    ),

                    const SizedBox(height: 28),

                    // ── Login link ────────────────────────────
                    Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                      const Text('Already have an account? ',
                          style: TextStyle(fontSize: 14, color: cMuted)),
                      GestureDetector(
                        onTap: () => Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(
                              builder: (_) => const LoginScreen()),
                        ),
                        child: const Text('Sign In',
                            style: TextStyle(
                                fontSize: 14,
                                color: cGreen,
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

  Widget _buildLabel(String text) => Text(
        text,
        style: const TextStyle(
            fontSize: 13, fontWeight: FontWeight.w600, color: cText2),
      );

  InputDecoration _inputDecor({
    required String hint,
    required IconData icon,
    Widget? suffix,
  }) =>
      InputDecoration(
        hintText: hint,
        hintStyle: TextStyle(color: cMuted.withOpacity(0.6), fontSize: 14),
        prefixIcon: Icon(icon, color: cMuted, size: 20),
        suffixIcon: suffix,
        filled: true,
        fillColor: cCard,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: cBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: cBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: cGreen, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: cRed),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: cRed, width: 1.5),
        ),
        errorStyle: const TextStyle(color: cRed, fontSize: 12),
      );
}

// ── Reusable widgets (same as login_screen) ───────────────────
class _GreenButton extends StatelessWidget {
  final String label;
  final bool loading;
  final VoidCallback onTap;
  const _GreenButton(
      {required this.label, required this.loading, required this.onTap});

  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: loading ? null : onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          height: 54,
          decoration: BoxDecoration(
            gradient: LinearGradient(
                colors: loading ? [cMuted, cMuted2] : [cGreen, cGreen2]),
            borderRadius: BorderRadius.circular(14),
            boxShadow: loading
                ? []
                : [
                    BoxShadow(
                        color: cGreen.withOpacity(0.35),
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

class _GoogleButton extends StatelessWidget {
  final bool loading;
  final VoidCallback onTap;
  const _GoogleButton({required this.loading, required this.onTap});

  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: loading ? null : onTap,
        child: Container(
          height: 54,
          decoration: BoxDecoration(
            color: cCard,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: cBorder),
          ),
          child: Center(
            child: loading
                ? const SizedBox(
                    width: 22, height: 22,
                    child: CircularProgressIndicator(
                        color: cGreen, strokeWidth: 2.5))
                : Row(mainAxisSize: MainAxisSize.min, children: [
                    SizedBox(
                        width: 22,
                        height: 22,
                        child: CustomPaint(painter: _GoogleLogoPainter())),
                    const SizedBox(width: 12),
                    const Text('Continue with Google',
                        style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: cText)),
                  ]),
          ),
        ),
      );
}

class _GoogleLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final c = Offset(size.width / 2, size.height / 2);
    final r = size.width / 2;
    final colors = [
      const Color(0xFF4285F4),
      const Color(0xFF34A853),
      const Color(0xFFFBBC05),
      const Color(0xFFEA4335),
    ];
    final starts = [0.0, 90.0, 180.0, 270.0];
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = size.width * 0.18;
    for (int i = 0; i < 4; i++) {
      paint.color = colors[i];
      canvas.drawArc(Rect.fromCircle(center: c, radius: r * 0.72),
          _d(starts[i]), _d(80), false, paint);
    }
    canvas.drawCircle(c, r * 0.45, Paint()..color = const Color(0xFF131F17));
    canvas.drawRect(
        Rect.fromLTWH(c.dx, c.dy - size.height * 0.09, r * 0.7, size.height * 0.18),
        Paint()..color = const Color(0xFF4285F4));
  }
  double _d(double d) => d * 3.14159265 / 180;
  @override
  bool shouldRepaint(_) => false;
}
