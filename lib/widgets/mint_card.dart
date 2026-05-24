import 'package:flutter/material.dart';
import '../utils/constants.dart';

// Dark cyber mint card — matches HTML .fix-card style
class MintCard extends StatefulWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final Color? color;
  final double radius;
  final VoidCallback? onTap;
  const MintCard({super.key, required this.child, this.padding,
      this.color, this.radius = 16, this.onTap});

  @override
  State<MintCard> createState() => _MintCardState();
}

class _MintCardState extends State<MintCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 100));
    _scale = Tween(begin: 1.0, end: 0.985)
        .animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOut));
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardBg = cCard;
    final borderColor = cBorder;

    final card = ScaleTransition(
      scale: _scale,
      child: Container(
        padding: widget.padding ?? const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: widget.color ?? cardBg,
          borderRadius: BorderRadius.circular(widget.radius),
          border: Border.all(color: borderColor, width: 1.5),
          boxShadow: [
            BoxShadow(
              color: cGreen.withOpacity(isDark ? 0.06 : 0.04),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: widget.child,
      ),
    );
    if (widget.onTap == null) return card;
    return GestureDetector(
      onTapDown: (_) => _ctrl.forward(),
      onTapUp: (_) { _ctrl.reverse(); widget.onTap?.call(); },
      onTapCancel: () => _ctrl.reverse(),
      child: card,
    );
  }
}

class MintBtn extends StatefulWidget {
  final String label;
  final VoidCallback? onTap;
  final Color? bg;
  final Color? fg;
  final double height;
  final double? width;
  final double fontSize;
  final IconData? icon;
  final bool disabled;
  const MintBtn({
    super.key, required this.label, this.onTap,
    this.bg, this.fg, this.height = 52, this.width,
    this.fontSize = 15, this.icon, this.disabled = false,
  });

  @override
  State<MintBtn> createState() => _MintBtnState();
}

class _MintBtnState extends State<MintBtn> with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 80));
    _scale = Tween(begin: 1.0, end: 0.95).animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOut));
  }

  @override
  void dispose() { _ctrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final defaultBg = cGreen;
    final bg = widget.disabled ? (cMuted) : (widget.bg ?? defaultBg);
    final fg = widget.fg ?? Colors.white;
    return ScaleTransition(
      scale: _scale,
      child: GestureDetector(
        onTapDown: (_) { if (!widget.disabled) _ctrl.forward(); },
        onTapUp: (_) { _ctrl.reverse(); widget.onTap?.call(); },
        onTapCancel: () => _ctrl.reverse(),
        child: Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(14),
            boxShadow: widget.disabled ? [] : [
              BoxShadow(color: bg.withOpacity(0.35), blurRadius: 10, offset: const Offset(0, 4)),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: widget.width == null ? MainAxisSize.max : MainAxisSize.min,
            children: [
              if (widget.icon != null) ...[
                Icon(widget.icon, color: fg, size: 20),
                const SizedBox(width: 8),
              ],
              Text(widget.label, style: TextStyle(color: fg, fontSize: widget.fontSize, fontWeight: FontWeight.w700)),
            ],
          ),
        ),
      ),
    );
  }
}

// Green section header like HTML theme
class SectionHeader extends StatelessWidget {
  final String title;
  final Color? color;
  const SectionHeader(this.title, {super.key, this.color});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Text(
    title,
    style: TextStyle(
      fontSize: 13,
      fontWeight: FontWeight.w700,
      color: color ?? (cGreen),
      letterSpacing: 0.5,
    ),
  );
  }
}

class TitanDivider extends StatelessWidget {
  const TitanDivider({super.key});
  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
    height: 1, color: cBorder,
    margin: const EdgeInsets.symmetric(vertical: 2),
  );
  }
}
