import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../widgets/waveform_widget.dart';
import 'studio_screen.dart';

class SplashScreen extends StatefulWidget {
  final bool autoNavigate;
  const SplashScreen({super.key, this.autoNavigate = true});
  @override
  State<SplashScreen> createState() => _SplashState();
}

class _SplashState extends State<SplashScreen> with TickerProviderStateMixin {
  late AnimationController _logoCtrl;
  late AnimationController _gridCtrl;
  late AnimationController _glowCtrl;
  late Animation<double> _fade, _scale, _gridFade, _glowAnim;
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

    // Logo fade + scale
    _logoCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 900));
    _fade  = CurvedAnimation(parent: _logoCtrl, curve: Curves.easeIn);
    _scale = Tween(begin: 0.72, end: 1.0).animate(
        CurvedAnimation(parent: _logoCtrl, curve: Curves.elasticOut));

    // Obsidian grid pulse
    _gridCtrl = AnimationController(
        vsync: this, duration: const Duration(seconds: 3))
      ..repeat(reverse: true);
    _gridFade = Tween(begin: 0.025, end: 0.07).animate(_gridCtrl);

    // Neon logo glow pulse
    _glowCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 1800))
      ..repeat(reverse: true);
    _glowAnim = Tween(begin: 0.25, end: 0.55).animate(
        CurvedAnimation(parent: _glowCtrl, curve: Curves.easeInOut));

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
    if (widget.autoNavigate) {
      Navigator.of(context).pushReplacement(
        PageRouteBuilder(
          transitionDuration: const Duration(milliseconds: 600),
          pageBuilder: (_, __, ___) => const StudioScreen(),
          transitionsBuilder: (_, anim, __, child) =>
              FadeTransition(opacity: anim, child: child),
        ),
      );
    }
  }

  @override
  void dispose() {
    _logoCtrl.dispose();
    _gridCtrl.dispose();
    _glowCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cBg,
      body: Stack(
        children: [
          // ── Animated Obsidian grid ──
          AnimatedBuilder(
            animation: _gridFade,
            builder: (_, __) => CustomPaint(
              size: Size.infinite,
              painter: _ObsidianGridPainter(opacity: _gridFade.value),
            ),
          ),

          // ── Top neon glow line ──
          Positioned(
            top: 0, left: 0, right: 0,
            child: Container(
              height: 2,
              decoration: const BoxDecoration(
                gradient: LinearGradient(colors: [
                  Colors.transparent,
                  cGreen,
                  cGreen2,
                  Colors.transparent,
                ]),
              ),
            ),
          ),

          // ── Bottom neon glow line ──
          Positioned(
            bottom: 0, left: 0, right: 0,
            child: Container(
              height: 1,
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [
                  Colors.transparent,
                  cGreen2.withOpacity(0.4),
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
                  // ── LOGO with neon glow ──
                  AnimatedBuilder(
                    animation: _glowAnim,
                    builder: (_, child) => Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(32),
                        boxShadow: [
                          BoxShadow(
                            color: cGreen.withOpacity(_glowAnim.value),
                            blurRadius: 60,
                            spreadRadius: 8,
                          ),
                          BoxShadow(
                            color: cGreen2.withOpacity(_glowAnim.value * 0.6),
                            blurRadius: 100,
                            spreadRadius: 16,
                          ),
                        ],
                      ),
                      child: child,
                    ),
                    child: ScaleTransition(
                      scale: _scale,
                      child: Container(
                        width: 120, height: 120,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFF161F30), Color(0xFF1C2840)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(28),
                          border: Border.all(
                            color: cGreen.withOpacity(0.5),
                            width: 1.5,
                          ),
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
                  ),

                  const SizedBox(height: 32),

                  // ── Neon version badge ──
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          cGreen.withOpacity(0.12),
                          cGreen2.withOpacity(0.08),
                        ],
                      ),
                      border: Border.all(color: cGreen.withOpacity(0.35)),
                      borderRadius: BorderRadius.circular(100),
                    ),
                    child: const Text(
                      'v1.0 · Titan Studio PRO',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        color: cGreen,
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
                      color: cText,
                      letterSpacing: -0.5,
                    ),
                  ),

                  const SizedBox(height: 6),

                  // ── Subtitle with neon dot ──
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 6, height: 6,
                        decoration: const BoxDecoration(
                          color: cGreen,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        '39 Languages · 20 Characters · Always Free',
                        style: TextStyle(fontSize: 13, color: cText2),
                      ),
                    ],
                  ),

                  const SizedBox(height: 48),

                  // ── Neon Cyan Waveform ──
                  const WaveformWidget(active: true),

                  const SizedBox(height: 32),

                  // ── Neon progress bar ──
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 64),
                    child: Stack(
                      children: [
                        // Background track
                        Container(
                          height: 5,
                          decoration: BoxDecoration(
                            color: cBorder,
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        // Neon fill
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 400),
                          curve: Curves.easeOut,
                          height: 5,
                          width: (MediaQuery.of(context).size.width - 128) * _progress,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [cGreen, cGreen2],
                            ),
                            borderRadius: BorderRadius.circular(8),
                            boxShadow: [
                              BoxShadow(
                                color: cGreen.withOpacity(0.6),
                                blurRadius: 8,
                                offset: const Offset(0, 0),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // ── Status message ──
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 300),
                    child: Row(
                      key: ValueKey(_msg),
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 6, height: 6,
                          decoration: const BoxDecoration(
                            color: cGreen,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _msg,
                          style: const TextStyle(
                            fontSize: 12,
                            color: cGreen2,
                            fontWeight: FontWeight.w500,
                            letterSpacing: 0.3,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 60),

                  Text(
                    '© 2026 Titan Studio PRO',
                    style: TextStyle(fontSize: 11, color: cMuted),
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

// ── Obsidian Grid Painter ─────────────────────────────────
class _ObsidianGridPainter extends CustomPainter {
  final double opacity;
  _ObsidianGridPainter({required this.opacity});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF00F2FE).withOpacity(opacity)
      ..strokeWidth = 0.4;

    const step = 44.0;
    for (double x = 0; x < size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(_ObsidianGridPainter old) => old.opacity != opacity;
}
