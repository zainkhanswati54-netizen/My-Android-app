// lib/theme.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── OBSIDIAN NEON Palette ──────────────────────
  static const Color bg         = Color(0xFF0B0F19);  // Deep Obsidian Black
  static const Color bg2        = Color(0xFF0E1320);
  static const Color card       = Color(0xFF161F30);  // Dark Charcoal
  static const Color card2      = Color(0xFF1C2840);
  static const Color green      = Color(0xFF00F2FE);  // Neon Cyan
  static const Color green2     = Color(0xFF4FACFE);  // Electric Blue
  static const Color green3     = Color(0xFF003A55);
  static const Color greenLight = Color(0xFF80F8FF);
  static const Color text       = Color(0xFFFFFFFF);  // Pure White
  static const Color text2      = Color(0xFF8A99AD);  // Muted Slate
  static const Color muted      = Color(0xFF5A6A7E);
  static const Color muted2     = Color(0xFF2D3D52);
  static const Color border     = Color(0xFF1E2D45);
  static const Color red        = Color(0xFFFF4757);
  static const Color amber      = Color(0xFFFFD32A);
  static const Color purple     = Color(0xFF9C27B0);
  static const Color indigo     = Color(0xFF5C6BC0);
  static const Color teal       = Color(0xFF00B4D8);
  static const Color surface    = Color(0xFF1C2840);

  static ThemeData get theme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: green,
      brightness: Brightness.dark,
    ).copyWith(
      surface: bg,
      onSurface: text,
      primary: green,
      secondary: green2,
    ),
    scaffoldBackgroundColor: bg,
    // Inter font — strict 7:1 contrast ratio via pure white on obsidian
    textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).apply(
      bodyColor: text,
      displayColor: text,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: bg2,
      foregroundColor: text,
      elevation: 0,
    ),
    // Slider neon styling
    sliderTheme: SliderThemeData(
      activeTrackColor: green,
      inactiveTrackColor: border,
      thumbColor: green,
      overlayColor: green.withOpacity(0.15),
      trackHeight: 3,
    ),
    // Switch neon
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((s) =>
        s.contains(WidgetState.selected) ? bg : muted),
      trackColor: WidgetStateProperty.resolveWith((s) =>
        s.contains(WidgetState.selected) ? green : border),
    ),
  );
}
