import 'dart:math';
import 'package:flutter/material.dart';
import '../utils/constants.dart';

// ═══════════════════════════════════════════════════════════
//  TITAN VISUAL WAVEFORM WIDGET — OBSIDIAN NEON EDITION
//  3 modes:
//   • idle    — gentle breathing (minimal)
//   • loading — cyan pulse wave (generating)
//   • playing — Neon Cyan dancing bars
// ═══════════════════════════════════════════════════════════

enum WaveformMode { idle, loading, playing }

class WaveformWidget extends StatefulWidget {
  final bool active;
  final WaveformMode mode;
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
  late List<double> _seeds;

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
    if (_ctrl.duration != _durationForMode(newMode)) {
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
    // Neon Cyan default
    final baseColor = widget.color ?? cGreen;
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, __) => CustomPaint(
        painter: _WaveformPainter(
          t: _ctrl.value,
          mode: _resolvedMode,
          seeds: _seeds,
          color: baseColor,
          accentColor: cGreen2,
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
  final Color accentColor;
  final int bars;

  _WaveformPainter({
    required this.t,
    required this.mode,
    required this.seeds,
    required this.color,
    required this.accentColor,
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
          ratio = 0.05 + sin(phase * 0.4 + seed) * 0.03;

        case WaveformMode.loading:
          final centerFactor = 1.0 - ((i - bars / 2).abs() / (bars / 2)) * 0.5;
          ratio = (0.12 + sin(phase + seed * 0.5) * 0.22) * centerFactor;
          ratio = ratio.clamp(0.04, 0.85);

        case WaveformMode.playing:
          final f1 = sin(phase * 2.1 + seed);
          final f2 = sin(phase * 3.7 + seed * 1.3 + i * 0.25);
          final f3 = sin(phase * 1.3 + seed * 0.7 + i * 0.12);
          ratio = (f1.abs() * 0.50 + f2.abs() * 0.30 + f3.abs() * 0.20)
              .clamp(0.06, 1.0);
      }

      final barH = ratio * size.height;
      final x = i * (barW + gap) + gap / 2;
      final y = midY - barH / 2;

      final alpha = mode == WaveformMode.idle
          ? 0.20
          : (0.35 + ratio * 0.65).clamp(0.0, 1.0);

      // Neon gradient: center bars blend toward Electric Blue
      final centerBlend = 1.0 - ((i - bars / 2).abs() / (bars / 2)).clamp(0.0, 1.0);
      final barColor = Color.lerp(
        color.withOpacity(alpha),
        accentColor.withOpacity(alpha),
        centerBlend * ratio * 0.5,
      )!;

      final paint = Paint()
        ..color = barColor
        ..style = PaintingStyle.fill;

      // Neon glow effect for playing bars
      if (mode == WaveformMode.playing && ratio > 0.5) {
        final glowPaint = Paint()
          ..color = color.withOpacity(0.08)
          ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
        canvas.drawRRect(
          RRect.fromRectAndRadius(
            Rect.fromLTWH(x - 2, y - 2, barW + 4, barH + 4),
            Radius.circular(barW / 2),
          ),
          glowPaint,
        );
      }

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
    const bars = 20;
    final barW = size.width / bars * 0.5;
    final gap  = size.width / bars * 0.5;
    final midY = size.height / 2;
    final phase = t * 2 * pi;

    for (int i = 0; i < bars; i++) {
      final seed = seeds[i % seeds.length];
      double ratio;

      if (!active) {
        ratio = 0.08 + (i % 3 == 0 ? 0.06 : 0.0);
      } else {
        final f1 = sin(phase * 2.5 + seed).abs();
        final f2 = sin(phase * 1.8 + seed * 1.5).abs();
        ratio = (f1 * 0.6 + f2 * 0.4).clamp(0.08, 1.0);
      }

      final barH = ratio * size.height;
      final x = i * (barW + gap);
      final y = midY - barH / 2;
      final alpha = active ? (0.4 + ratio * 0.6) : 0.25;

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
