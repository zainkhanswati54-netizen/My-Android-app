import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../widgets/waveform_widget.dart';
import 'studio_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});
  @override
  State<SplashScreen> createState() => _SplashState();
}

class _SplashState extends State<SplashScreen> with TickerProviderStateMixin {
  late AnimationController _logoCtrl;
  late AnimationController _gridCtrl;
  late Animation<double> _fade, _scale, _gridFade;
  double _progress = 0;
  String _msg = 'Initializing...';
  final _msgs = [
    'Initializing...',
    'Loading voices...',
    'Preparing studio...',
    'Almost ready...'
  ];

  @override
  void initState() {
    super.initState();

    // Logo animation
    _logoCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 900));
    _fade = CurvedAnimation(parent: _logoCtrl, curve: Curves.easeIn);
    _scale = Tween(begin: 0.75, end: 1.0).animate(
        CurvedAnimation(parent: _logoCtrl, curve: Curves.elasticOut));

    // Grid pulse animation
    _gridCtrl = AnimationController(
        vsync: this, duration: const Duration(seconds: 3))
      ..repeat(reverse: true);
    _gridFade = Tween(begin: 0.03, end: 0.08).animate(_gridCtrl);

    _logoCtrl.forward();
    _startProgress();
  }

  void _startProgress() async {
    for (int i = 0; i < _msgs.length; i++) {
      await Future.delayed(Duration(milliseconds: 500 + i * 400));
      if (!mounted) return;
      setState(() {
        _progress = (i + 1) / _msgs.length;
        _msg = _msgs[i];
      });
    }
    await Future.delayed(const Duration(milliseconds: 400));
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 600),
        pageBuilder: (_, __, ___) => const StudioScreen(),
        transitionsBuilder: (_, anim, __, child) =>
            FadeTransition(opacity: anim, child: child),
      ),
    );
  }

  @override
  void dispose() {
    _logoCtrl.dispose();
    _gridCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // ── HTML-inspired DARK theme for splash ──
    const darkBg    = Color(0xFF0A0F0D);
    const darkCard  = Color(0xFF131F17);
    const darkGreen = Color(0xFF10B981);
    const darkGreen2= Color(0xFF059669);
    const darkText  = Color(0xFFE2F0E8);
    const darkMuted = Color(0xFF5A7A64);
    const darkBorder= Color(0xFF1E3A27);

    return Scaffold(
      backgroundColor: darkBg,
      body: Stack(
        children: [
          // ── Animated background grid ──
          AnimatedBuilder(
            animation: _gridFade,
            builder: (_, __) => CustomPaint(
              size: Size.infinite,
              painter: _GridPainter(opacity: _gridFade.value),
            ),
          ),

          // ── Top glow line ──
          Positioned(
            top: 0, left: 0, right: 0,
            child: Container(
              height: 2,
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [
                  Colors.transparent,
                  darkGreen,
                  Colors.transparent,
                ]),
              ),
            ),
          ),

          // ── Main content ──
          FadeTransition(
            opacity: _fade,
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // ── LOGO ──
                  ScaleTransition(
                    scale: _scale,
                    child: Container(
                      width: 120, height: 120,
                      decoration: BoxDecoration(
                        color: darkCard,
                        borderRadius: BorderRadius.circular(28),
                        border: Border.all(color: darkBorder, width: 1.5),
                        boxShadow: [
                          BoxShadow(
                            color: darkGreen.withOpacity(0.3),
                            blurRadius: 40,
                            offset: const Offset(0, 12),
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(26),
                        child: Image.asset(
                          'assets/icons/logo.png',
                          fit: BoxFit.contain,
                          errorBuilder: (_, __, ___) => const Center(
                            child: Text('T',
                                style: TextStyle(
                                    fontSize: 64,
                                    fontWeight: FontWeight.w900,
                                    color: Colors.white)),
                          ),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // ── Version badge ──
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
                    decoration: BoxDecoration(
                      color: darkGreen.withOpacity(0.12),
                      border: Border.all(color: darkGreen.withOpacity(0.3)),
                      borderRadius: BorderRadius.circular(100),
                    ),
                    child: const Text(
                      'v1.0 · ALWAYS FREE',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        color: darkGreen,
                        letterSpacing: 1.5,
                      ),
                    ),
                  ),

                  const SizedBox(height: 14),

                  // ── Title ──
                  const Text(
                    'Titan Studio PRO',
                    style: TextStyle(
                      fontSize: 30,
                      fontWeight: FontWeight.w800,
                      color: darkText,
                      letterSpacing: -0.5,
                    ),
                  ),

                  const SizedBox(height: 6),

                  const Text(
                    'Professional Voice Studio  ·  Always Free',
                    style: TextStyle(fontSize: 13, color: darkMuted),
                  ),

                  const SizedBox(height: 48),

                  // ── Waveform ──
                  const WaveformWidget(active: true),

                  const SizedBox(height: 32),

                  // ── Progress bar ──
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 64),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: LinearProgressIndicator(
                        value: _progress,
                        backgroundColor: darkBorder,
                        valueColor:
                            const AlwaysStoppedAnimation<Color>(darkGreen),
                        minHeight: 5,
                      ),
                    ),
                  ),

                  const SizedBox(height: 14),

                  // ── Status message ──
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 300),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 6, height: 6,
                          decoration: const BoxDecoration(
                            color: darkGreen,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _msg,
                          key: ValueKey(_msg),
                          style: const TextStyle(
                            fontSize: 12,
                            color: darkGreen2,
                            fontWeight: FontWeight.w500,
                            letterSpacing: 0.3,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 60),

                  const Text(
                    '© 2025 Titan Studio PRO',
                    style: TextStyle(fontSize: 11, color: darkMuted),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Animated grid painter (HTML body::before recreation) ──
class _GridPainter extends CustomPainter {
  final double opacity;
  _GridPainter({required this.opacity});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF10B981).withOpacity(opacity)
      ..strokeWidth = 0.5;

    const step = 40.0;
    for (double x = 0; x < size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(_GridPainter old) => old.opacity != opacity;
}
