// lib/widgets/widgets.dart
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';

// ── Mint Card ────────────────────────────────────────────
class MintCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final Color? color;
  final double radius;

  const MintCard({
    super.key,
    required this.child,
    this.padding,
    this.color,
    this.radius = 16,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding ?? const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color ?? AppTheme.card,
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: AppTheme.border, width: 1.5),
        boxShadow: [
          BoxShadow(
            color: AppTheme.green.withOpacity(0.06),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: child,
    );
  }
}

// ── Section Header ───────────────────────────────────────
class SectionHeader extends StatelessWidget {
  final String title;
  final IconData? icon;
  final Color? color;

  const SectionHeader({
    super.key,
    required this.title,
    this.icon,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      if (icon != null) ...[
        Icon(icon, size: 16, color: color ?? AppTheme.green),
        const SizedBox(width: 6),
      ],
      Text(
        title,
        style: TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w700,
          color: color ?? AppTheme.green,
          letterSpacing: 0.5,
        ),
      ),
    ]);
  }
}

// ── Mint Button ──────────────────────────────────────────
class MintButton extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;
  final Color? color;
  final Color? textColor;
  final double height;
  final IconData? icon;
  final bool loading;

  const MintButton({
    super.key,
    required this.label,
    this.onTap,
    this.color,
    this.textColor,
    this.height = 52,
    this.icon,
    this.loading = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: loading ? null : onTap,
      child: AnimatedContainer(
        duration: 200.ms,
        height: height,
        decoration: BoxDecoration(
          color: (onTap == null || loading)
              ? (color ?? AppTheme.green).withOpacity(0.5)
              : (color ?? AppTheme.green),
          borderRadius: BorderRadius.circular(14),
          boxShadow: onTap != null && !loading
              ? [
                  BoxShadow(
                    color: (color ?? AppTheme.green).withOpacity(0.30),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  )
                ]
              : [],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (loading) ...[
              SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: textColor ?? Colors.white,
                ),
              ),
              const SizedBox(width: 10),
            ] else if (icon != null) ...[
              Icon(icon, color: textColor ?? Colors.white, size: 20),
              const SizedBox(width: 8),
            ],
            Text(
              label,
              style: TextStyle(
                color: textColor ?? Colors.white,
                fontWeight: FontWeight.w700,
                fontSize: 15,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Waveform Visualizer ──────────────────────────────────
class WaveformWidget extends StatefulWidget {
  final bool active;
  final Color? color;

  const WaveformWidget({super.key, required this.active, this.color});

  @override
  State<WaveformWidget> createState() => _WaveformWidgetState();
}

class _WaveformWidgetState extends State<WaveformWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    if (widget.active) _ctrl.repeat();
  }

  @override
  void didUpdateWidget(WaveformWidget old) {
    super.didUpdateWidget(old);
    if (widget.active && !_ctrl.isAnimating) {
      _ctrl.repeat();
    } else if (!widget.active) {
      _ctrl.stop();
      _ctrl.reset();
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, __) {
        return CustomPaint(
          painter: _WavePainter(
            progress: _ctrl.value,
            active: widget.active,
            color: widget.color ?? AppTheme.green,
          ),
          child: const SizedBox(height: 40),
        );
      },
    );
  }
}

class _WavePainter extends CustomPainter {
  final double progress;
  final bool active;
  final Color color;
  static const int bars = 24;

  const _WavePainter({
    required this.progress,
    required this.active,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;
    final barWidth = size.width / (bars * 1.8);
    final gap = barWidth * 0.8;
    final totalW = bars * (barWidth + gap);
    var x = (size.width - totalW) / 2;

    for (int i = 0; i < bars; i++) {
      double h;
      if (active) {
        final phase = (progress * 2 * 3.14159) + i * 0.35;
        h = (0.15 + (0.5 * _abs(Math.sin(phase))) + (0.35 * _abs(Math.sin(phase * 2.7 + 1)))) * size.height;
        h = h.clamp(4, size.height);
      } else {
        h = 4;
      }
      final alpha = active ? (0.4 + (h / size.height) * 0.6) : 0.2;
      paint.color = color.withOpacity(alpha);
      final rect = RRect.fromRectAndRadius(
        Rect.fromLTWH(x, (size.height - h) / 2, barWidth, h),
        Radius.circular(barWidth / 2),
      );
      canvas.drawRRect(rect, paint);
      x += barWidth + gap;
    }
  }

  double _abs(double v) => v < 0 ? -v : v;

  @override
  bool shouldRepaint(_WavePainter old) =>
      old.progress != progress || old.active != active;
}

// ignore: avoid_classes_with_only_static_members
class Math {
  static double sin(double x) {
    // Simple sin approximation
    x = x % (2 * 3.14159265);
    double result = x;
    double term = x;
    for (int i = 1; i <= 5; i++) {
      term *= -x * x / ((2 * i) * (2 * i + 1));
      result += term;
    }
    return result;
  }
}

// ── Language Selector Card ───────────────────────────────
class LanguageChip extends StatelessWidget {
  final String label;
  final String flag;
  final bool selected;
  final VoidCallback onTap;

  const LanguageChip({
    super.key,
    required this.label,
    required this.flag,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: 200.ms,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: selected ? AppTheme.green : AppTheme.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? AppTheme.green : AppTheme.border,
            width: 1.5,
          ),
          boxShadow: selected
              ? [
                  BoxShadow(
                    color: AppTheme.green.withOpacity(0.25),
                    blurRadius: 8,
                    offset: const Offset(0, 3),
                  )
                ]
              : [],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(flag, style: const TextStyle(fontSize: 18)),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                color: selected ? Colors.white : AppTheme.text,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Emotion Chip ─────────────────────────────────────────
class EmotionChip extends StatelessWidget {
  final String label;
  final String icon;
  final bool selected;
  final Color emotionColor;
  final VoidCallback onTap;

  const EmotionChip({
    super.key,
    required this.label,
    required this.icon,
    required this.selected,
    required this.emotionColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: 180.ms,
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        decoration: BoxDecoration(
          color: selected ? emotionColor : AppTheme.surface,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: selected ? emotionColor : AppTheme.border,
            width: 1.5,
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(icon, style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                color: selected ? Colors.white : AppTheme.muted,
                fontWeight: FontWeight.w600,
                fontSize: 9,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
