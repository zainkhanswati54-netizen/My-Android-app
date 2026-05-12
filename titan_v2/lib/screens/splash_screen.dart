import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../widgets/waveform_widget.dart';
import 'studio_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});
  @override
  State<SplashScreen> createState() => _SplashState();
}

class _SplashState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _fade, _scale;
  double _progress = 0;
  String _msg = 'Initializing...';
  final _msgs = ['Initializing...', 'Loading voices...', 'Preparing studio...', 'Almost ready...'];

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 800));
    _fade = CurvedAnimation(parent: _ctrl, curve: Curves.easeIn);
    _scale = Tween(begin: 0.85, end: 1.0).animate(CurvedAnimation(parent: _ctrl, curve: Curves.elasticOut));
    _ctrl.forward();
    _startProgress();
  }

  void _startProgress() async {
    for (int i = 0; i < _msgs.length; i++) {
      await Future.delayed(Duration(milliseconds: 500 + i * 400));
      if (!mounted) return;
      setState(() { _progress = (i + 1) / _msgs.length; _msg = _msgs[i]; });
    }
    await Future.delayed(const Duration(milliseconds: 400));
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 500),
        pageBuilder: (_, __, ___) => const StudioScreen(),
        transitionsBuilder: (_, anim, __, child) => FadeTransition(opacity: anim, child: child),
      ),
    );
  }

  @override
  void dispose() { _ctrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cBg2,
      body: FadeTransition(
        opacity: _fade,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ScaleTransition(
                scale: _scale,
                child: Container(
                  width: 110, height: 110,
                  decoration: BoxDecoration(
                    color: cGreen, borderRadius: BorderRadius.circular(28),
                    boxShadow: [BoxShadow(color: cGreen.withOpacity(0.35), blurRadius: 30, offset: const Offset(0, 10))],
                  ),
                  child: const Center(
                    child: Text('T', style: TextStyle(fontSize: 64, fontWeight: FontWeight.w900, color: Colors.white)),
                  ),
                ),
              ),
              const SizedBox(height: 28),
              const Text('Titan Studio PRO', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: cText2, letterSpacing: -0.5)),
              const SizedBox(height: 6),
              const Text('v2.0  Cyber Mint Edition', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cGreen2, letterSpacing: 1)),
              const SizedBox(height: 8),
              const Text('Professional Voice Studio  ·  Always Free', style: TextStyle(fontSize: 13, color: cMuted)),
              const SizedBox(height: 48),
              const WaveformWidget(active: true),
              const SizedBox(height: 28),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 64),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: _progress,
                    backgroundColor: cBorder,
                    valueColor: const AlwaysStoppedAnimation<Color>(cGreen),
                    minHeight: 6,
                  ),
                ),
              ),
              const SizedBox(height: 14),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                child: Text(_msg, key: ValueKey(_msg), style: const TextStyle(fontSize: 13, color: cGreen, fontWeight: FontWeight.w500)),
              ),
              const SizedBox(height: 60),
              const Text('© 2025 Titan Studio PRO', style: TextStyle(fontSize: 11, color: cMuted2)),
            ],
          ),
        ),
      ),
    );
  }
}
