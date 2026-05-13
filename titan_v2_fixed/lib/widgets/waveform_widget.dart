import 'dart:math';
import 'package:flutter/material.dart';
import '../utils/constants.dart';

class WaveformWidget extends StatefulWidget {
  final bool active;
  const WaveformWidget({super.key, this.active = false});
  @override
  State<WaveformWidget> createState() => _WaveformState();
}

class _WaveformState extends State<WaveformWidget> with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  final int _bars = 24;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))
      ..repeat();
  }

  @override
  void dispose() { _ctrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: _ctrl,
    builder: (_, __) => CustomPaint(
      painter: _WavePainter(t: _ctrl.value, active: widget.active, bars: _bars),
      size: const Size(double.infinity, 44),
    ),
  );
}

class _WavePainter extends CustomPainter {
  final double t;
  final bool active;
  final int bars;
  _WavePainter({required this.t, required this.active, required this.bars});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;
    final barW = size.width / (bars * 1.7);
    final gap = barW * 0.7;
    final total = bars * (barW + gap);
    final startX = (size.width - total) / 2;

    for (int i = 0; i < bars; i++) {
      final phase = t * 2 * pi + i * 0.4;
      double ratio = active
          ? (sin(phase).abs() * 0.65 + sin(phase * 2.7 + 1).abs() * 0.35).clamp(0.05, 1.0)
          : 0.07;
      final barH = ratio * size.height;
      final x = startX + i * (barW + gap);
      final y = (size.height - barH) / 2;
      final alpha = (0.35 + ratio * 0.65).clamp(0.0, 1.0);

      paint.color = cGreenL.withOpacity(alpha);
      canvas.drawRRect(
        RRect.fromRectAndRadius(Rect.fromLTWH(x, y, barW, barH), Radius.circular(barW / 2)),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(_WavePainter o) => o.t != t || o.active != active;
}
