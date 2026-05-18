import 'dart:math';
import 'package:flutter/material.dart';
import '../utils/constants.dart';

// ═══════════════════════════════════════════════════════════
//  TITAN VISUAL WAVEFORM WIDGET
//  3 modes:
//   • idle    — flat/minimal bars (generating nahi hai)
//   • loading — breathing pulse (generating ho raha hai)
//   • playing — animated dancing bars (audio play ho raha hai)
// ═══════════════════════════════════════════════════════════

enum WaveformMode { idle, loading, playing }

class WaveformWidget extends StatefulWidget {
  final bool active;        // legacy support (true = playing)
  final WaveformMode mode;  // new: explicit mode
  final Color? color;
  final double height;
  final int barCount;

  const WaveformWidget({
    super.key,
    this.active = false,
    this.mode = WaveformMode.idle,
    this.color,
    this.height = 48,
    this.barCount = 32,
  });

  // Convenience constructors
  const WaveformWidget.idle({super.key, this.color, this.height = 48, this.barCount = 32})
      : active = false, mode = WaveformMode.idle;

  const WaveformWidget.loading({super.key, this.color, this.height = 48, this.barCount = 32})
      : active = true, mode = WaveformMode.loading;

  const WaveformWidget.playing({super.key, this.color, this.height = 48, this.barCount = 32})
      : active = true, mode = WaveformMode.playing;

  @override
  State<WaveformWidget> createState() => _WaveformWidgetState();
}

class _WaveformWidgetState extends State<WaveformWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  final _rng = Random(42);
  late List<double> _seeds; // per-bar random seeds for organic feel

  @override
  void initState() {
    super.initState();
    _seeds = List.generate(64, (_) => _rng.nextDouble() * 2 * pi);

    _ctrl = AnimationController(
      vsync: this,
      duration: _durationForMode(widget.mode),
    )..repeat();
  }

  @override
  void didUpdateWidget(WaveformWidget old) {
    super.didUpdateWidget(old);
    final newMode = _resolvedMode;
    final oldMode = old.active != widget.active || old.mode != widget.mode
        ? newMode
        : old.mode;
    if (newMode != oldMode || _ctrl.duration != _durationForMode(newMode)) {
      _ctrl.duration = _durationForMode(newMode);
      if (!_ctrl.isAnimating) _ctrl.repeat();
    }
  }

  WaveformMode get _resolvedMode {
    if (widget.mode != WaveformMode.idle) return widget.mode;
    return widget.active ? WaveformMode.playing : WaveformMode.idle;
  }

  Duration _durationForMode(WaveformMode m) {
    switch (m) {
      case WaveformMode.loading: return const Duration(milliseconds: 1800);
      case WaveformMode.playing: return const Duration(milliseconds: 1000);
      case WaveformMode.idle:    return const Duration(milliseconds: 3000);
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = widget.color ?? cGreen;
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, __) => CustomPaint(
        painter: _WaveformPainter(
          t: _ctrl.value,
          mode: _resolvedMode,
          seeds: _seeds,
          color: color,
          bars: widget.barCount,
        ),
        size: Size(double.infinity, widget.height),
      ),
    );
  }
}

class _WaveformPainter extends CustomPainter {
  final double t;
  final WaveformMode mode;
  final List<double> seeds;
  final Color color;
  final int bars;

  _WaveformPainter({
    required this.t,
    required this.mode,
    required this.seeds,
    required this.color,
    required this.bars,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final phase = t * 2 * pi;
    final barW = (size.width / bars) * 0.55;
    final gap   = (size.width / bars) * 0.45;
    final midY  = size.height / 2;

    for (int i = 0; i < bars; i++) {
      final seed = seeds[i % seeds.length];
      double ratio;

      switch (mode) {
        case WaveformMode.idle:
          // Gentle slow breathing — very short bars
          ratio = 0.06 + sin(phase * 0.5 + seed) * 0.04;

        case WaveformMode.loading:
          // Smooth breathing pulse — center bars taller
          final centerFactor = 1.0 - ((i - bars / 2).abs() / (bars / 2)) * 0.5;
          ratio = (0.15 + sin(phase + seed * 0.5) * 0.20) * centerFactor;
          ratio = ratio.clamp(0.04, 0.80);

        case WaveformMode.playing:
          // Multi-frequency organic dance
          final f1 = sin(phase * 2.1 + seed);
          final f2 = sin(phase * 3.7 + seed * 1.3 + i * 0.25);
          final f3 = sin(phase * 1.3 + seed * 0.7 + i * 0.12);
          ratio = (f1.abs() * 0.50 + f2.abs() * 0.30 + f3.abs() * 0.20)
              .clamp(0.06, 1.0);
      }

      final barH = ratio * size.height;
      final x = i * (barW + gap) + gap / 2;
      final y = midY - barH / 2;

      // Color per bar: brighter when taller
      final alpha = mode == WaveformMode.idle
          ? 0.25
          : (0.30 + ratio * 0.70).clamp(0.0, 1.0);

      // Gradient effect: center bars get accent color tint
      final centerBlend = 1.0 - ((i - bars / 2).abs() / (bars / 2));
      final barColor = Color.lerp(
        color.withOpacity(alpha),
        Colors.white.withOpacity(alpha * 0.9),
        centerBlend * ratio * 0.3,
      )!;

      final paint = Paint()
        ..color = barColor
        ..style = PaintingStyle.fill;

      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTWH(x, y, barW, barH),
          Radius.circular(barW / 2),
        ),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(_WaveformPainter o) =>
      o.t != t || o.mode != mode || o.color != color;
}

// ═══════════════════════════════════════════════════════════
//  MINI WAVEFORM — history card ke liye (slim version)
// ═══════════════════════════════════════════════════════════
class MiniWaveform extends StatefulWidget {
  final bool isPlaying;
  final bool isPaused;
  final Color? color;

  const MiniWaveform({
    super.key,
    required this.isPlaying,
    required this.isPaused,
    this.color,
  });

  @override
  State<MiniWaveform> createState() => _MiniWaveformState();
}

class _MiniWaveformState extends State<MiniWaveform>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  final _seeds = List.generate(20, (i) => i * 0.47 + 0.3);

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = widget.color ?? cGreen;
    final active = widget.isPlaying && !widget.isPaused;

    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, __) => CustomPaint(
        painter: _MiniWavePainter(
          t: _ctrl.value,
          active: active,
          seeds: _seeds,
          color: color,
        ),
        size: const Size(double.infinity, 28),
      ),
    );
  }
}

class _MiniWavePainter extends CustomPainter {
  final double t;
  final bool active;
  final List<double> seeds;
  final Color color;

  _MiniWavePainter({
    required this.t,
    required this.active,
    required this.seeds,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final bars = 20;
    final barW = size.width / bars * 0.5;
    final gap  = size.width / bars * 0.5;
    final midY = size.height / 2;
    final phase = t * 2 * pi;

    for (int i = 0; i < bars; i++) {
      final seed = seeds[i % seeds.length];
      double ratio;

      if (!active) {
        ratio = 0.08 + (i % 3 == 0 ? 0.06 : 0.0); // static pattern
      } else {
        final f1 = sin(phase * 2.5 + seed).abs();
        final f2 = sin(phase * 1.8 + seed * 1.5).abs();
        ratio = (f1 * 0.6 + f2 * 0.4).clamp(0.08, 1.0);
      }

      final barH = ratio * size.height;
      final x = i * (barW + gap);
      final y = midY - barH / 2;
      final alpha = active ? (0.4 + ratio * 0.6) : 0.3;

      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTWH(x, y, barW, barH),
          Radius.circular(barW / 2),
        ),
        Paint()..color = color.withOpacity(alpha),
      );
    }
  }

  @override
  bool shouldRepaint(_MiniWavePainter o) =>
      o.t != t || o.active != active || o.color != color;
}
