// lib/widgets/widgets.dart — OBSIDIAN NEON EDITION
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../utils/constants.dart';

// ── Neon Card (Glassmorphism) ─────────────────────────────
class MintCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final Color? color;
  final double radius;
  final bool neonBorder;

  const MintCard({
    super.key,
    required this.child,
    this.padding,
    this.color,
    this.radius = 16,
    this.neonBorder = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding ?? const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF161F30), Color(0xFF1A2540)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(
          color: neonBorder
              ? cGreen.withOpacity(0.5)
              : cBorder,
          width: neonBorder ? 1.5 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: neonBorder
                ? cGreen.withOpacity(0.12)
                : cGreen.withOpacity(0.04),
            blurRadius: neonBorder ? 20 : 12,
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
    final c = color ?? cGreen;
    return Row(children: [
      if (icon != null) ...[
        Container(
          padding: const EdgeInsets.all(4),
          decoration: BoxDecoration(
            color: c.withOpacity(0.12),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Icon(icon, size: 14, color: c),
        ),
        const SizedBox(width: 8),
      ],
      Text(
        title,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          color: c,
          letterSpacing: 0.8,
        ),
      ),
    ]);
  }
}

// ── Neon Button ──────────────────────────────────────────
class MintButton extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;
  final Color? color;
  final Color? textColor;
  final double height;
  final IconData? icon;
  final bool loading;
  final bool outlined;

  const MintButton({
    super.key,
    required this.label,
    this.onTap,
    this.color,
    this.textColor,
    this.height = 52,
    this.icon,
    this.loading = false,
    this.outlined = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDisabled = onTap == null || loading;
    final accentColor = color ?? cGreen;

    return GestureDetector(
      onTap: isDisabled ? null : () {
        HapticFeedback.lightImpact();
        onTap?.call();
      },
      child: AnimatedContainer(
        duration: 200.ms,
        height: height,
        decoration: outlined
            ? BoxDecoration(
                color: Colors.transparent,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDisabled
                      ? accentColor.withOpacity(0.3)
                      : accentColor,
                  width: 1.5,
                ),
              )
            : BoxDecoration(
                gradient: isDisabled
                    ? LinearGradient(colors: [cMuted, cMuted2])
                    : LinearGradient(
                        colors: [accentColor, cGreen2],
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                      ),
                borderRadius: BorderRadius.circular(14),
                boxShadow: isDisabled ? [] : [
                  BoxShadow(
                    color: accentColor.withOpacity(0.35),
                    blurRadius: 18,
                    offset: const Offset(0, 6),
                  ),
                  BoxShadow(
                    color: accentColor.withOpacity(0.15),
                    blurRadius: 30,
                    offset: const Offset(0, 0),
                  ),
                ],
              ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (loading) ...[
              SizedBox(
                width: 18, height: 18,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: textColor ?? Colors.white,
                ),
              ),
              const SizedBox(width: 10),
            ] else if (icon != null) ...[
              Icon(icon, color: outlined ? accentColor : (textColor ?? Colors.white), size: 20),
              const SizedBox(width: 8),
            ],
            Text(
              label,
              style: TextStyle(
                color: outlined ? accentColor : (textColor ?? Colors.white),
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

// ── Animated Play/Pause Icon ─────────────────────────────
/// Smoothly morphs between Play and Pause icons
class NeonPlayPauseButton extends StatelessWidget {
  final bool isPlaying;
  final VoidCallback onTap;
  final double size;
  final Color? color;

  const NeonPlayPauseButton({
    super.key,
    required this.isPlaying,
    required this.onTap,
    this.size = 64,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final accentColor = color ?? cGreen;
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        onTap();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: LinearGradient(
            colors: [accentColor, cGreen2],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          boxShadow: [
            BoxShadow(
              color: accentColor.withOpacity(0.45),
              blurRadius: 24,
              offset: const Offset(0, 8),
            ),
            BoxShadow(
              color: accentColor.withOpacity(0.20),
              blurRadius: 40,
              spreadRadius: 4,
            ),
          ],
        ),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          transitionBuilder: (child, anim) => ScaleTransition(
            scale: anim,
            child: FadeTransition(opacity: anim, child: child),
          ),
          child: Icon(
            isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
            key: ValueKey(isPlaying),
            color: Colors.white,
            size: size * 0.50,
          ),
        ),
      ),
    );
  }
}

// ── Waveform Visualizer (legacy support) ─────────────────
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
            color: widget.color ?? cGreen,
            accentColor: cGreen2,
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
  final Color accentColor;
  static const int bars = 24;

  const _WavePainter({
    required this.progress,
    required this.active,
    required this.color,
    required this.accentColor,
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
        h = (0.15 + (0.5 * _abs(_sin(phase))) + (0.35 * _abs(_sin(phase * 2.7 + 1)))) * size.height;
        h = h.clamp(4, size.height);
      } else {
        h = 4;
      }
      final alpha = active ? (0.4 + (h / size.height) * 0.6) : 0.18;
      // Blend cyan -> electric blue across bars
      final blend = i / bars;
      paint.color = Color.lerp(
        color.withOpacity(alpha),
        accentColor.withOpacity(alpha),
        blend * 0.5,
      )!;
      final rect = RRect.fromRectAndRadius(
        Rect.fromLTWH(x, (size.height - h) / 2, barWidth, h),
        Radius.circular(barWidth / 2),
      );
      canvas.drawRRect(rect, paint);
      x += barWidth + gap;
    }
  }

  double _abs(double v) => v < 0 ? -v : v;
  double _sin(double x) {
    x = x % (2 * 3.14159265);
    double result = x;
    double term = x;
    for (int i = 1; i <= 5; i++) {
      term *= -x * x / ((2 * i) * (2 * i + 1));
      result += term;
    }
    return result;
  }

  @override
  bool shouldRepaint(_WavePainter old) =>
      old.progress != progress || old.active != active;
}

// ── Language Selector Chip (Neon style) ──────────────────
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
      onTap: () {
        HapticFeedback.lightImpact();
        onTap();
      },
      child: AnimatedContainer(
        duration: 200.ms,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          gradient: selected ? kNeonGradient : null,
          color: selected ? null : cSurface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? cGreen : cBorder,
            width: 1.5,
          ),
          boxShadow: selected ? [
            BoxShadow(
              color: cGreen.withOpacity(0.30),
              blurRadius: 12,
              offset: const Offset(0, 3),
            ),
          ] : [],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(flag, style: const TextStyle(fontSize: 18)),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                color: selected ? Colors.white : cText,
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
      onTap: () {
        HapticFeedback.lightImpact();
        onTap();
      },
      child: AnimatedContainer(
        duration: 180.ms,
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        decoration: BoxDecoration(
          color: selected ? emotionColor : cSurface,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: selected ? emotionColor : cBorder,
            width: 1.5,
          ),
          boxShadow: selected ? [
            BoxShadow(
              color: emotionColor.withOpacity(0.30),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ] : [],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(icon, style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                color: selected ? Colors.white : cMuted,
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

// ── Neon Text Highlighter ─────────────────────────────────
/// Shows text with one word highlighted in Neon Cyan.
/// Used during audio playback to show the current word.
class NeonTextHighlight extends StatelessWidget {
  final String text;
  final int highlightWordIndex;    // -1 = no highlight
  final TextStyle? baseStyle;
  final TextDirection textDir;

  const NeonTextHighlight({
    super.key,
    required this.text,
    this.highlightWordIndex = -1,
    this.baseStyle,
    this.textDir = TextDirection.ltr,
  });

  @override
  Widget build(BuildContext context) {
    final words = text.split(' ');
    final spans = <TextSpan>[];

    for (int i = 0; i < words.length; i++) {
      final isActive = i == highlightWordIndex;
      spans.add(TextSpan(
        text: i < words.length - 1 ? '${words[i]} ' : words[i],
        style: (baseStyle ?? const TextStyle(fontSize: 15, color: cText))
            .copyWith(
          color: isActive ? cGreen : (baseStyle?.color ?? cText),
          fontWeight: isActive ? FontWeight.w700 : (baseStyle?.fontWeight ?? FontWeight.w400),
          shadows: isActive ? [
            Shadow(
              color: cGreen.withOpacity(0.7),
              blurRadius: 8,
            ),
          ] : null,
        ),
      ));
    }

    return RichText(
      textDirection: textDir,
      text: TextSpan(children: spans),
    );
  }
}

// ── Animated Char Counter ─────────────────────────────────
/// Shows character count; turns Neon Cyan as it fills up.
class NeonCharCounter extends StatelessWidget {
  final int current;
  final int max;

  const NeonCharCounter({
    super.key,
    required this.current,
    required this.max,
  });

  @override
  Widget build(BuildContext context) {
    final ratio = current / max;
    final Color counterColor;
    if (ratio > 0.9) {
      counterColor = cRed;
    } else if (ratio > 0.7) {
      counterColor = cAmber;
    } else if (ratio > 0.3) {
      counterColor = cGreen;
    } else {
      counterColor = cMuted;
    }

    return AnimatedDefaultTextStyle(
      duration: const Duration(milliseconds: 300),
      style: TextStyle(
        fontSize: 12,
        fontWeight: ratio > 0.7 ? FontWeight.w700 : FontWeight.w400,
        color: counterColor,
      ),
      child: Text('$current / $max'),
    );
  }
}

// ── Neon Stat Badge ──────────────────────────────────────
/// Small neon-colored badge for displaying stats/metadata
class NeonBadge extends StatelessWidget {
  final String label;
  final Color? color;
  final IconData? icon;

  const NeonBadge({
    super.key,
    required this.label,
    this.color,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final c = color ?? cGreen;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: c.withOpacity(0.10),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: c.withOpacity(0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 11, color: c),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: c,
              letterSpacing: 0.3,
            ),
          ),
        ],
      ),
    );
  }
}
