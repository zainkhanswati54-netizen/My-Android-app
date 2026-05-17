// lib/theme.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── HTML Cyber Mint DARK Palette ────────────────────────
  static const Color bg         = Color(0xFF0A0F0D);
  static const Color bg2        = Color(0xFF0F1812);
  static const Color card       = Color(0xFF131F17);
  static const Color card2      = Color(0xFF1A2B20);
  static const Color green      = Color(0xFF10B981);
  static const Color green2     = Color(0xFF059669);
  static const Color green3     = Color(0xFF064E3B);
  static const Color greenLight = Color(0xFF34D399);
  static const Color text       = Color(0xFFE2F0E8);
  static const Color text2      = Color(0xFFA3C4AD);
  static const Color muted      = Color(0xFF5A7A64);
  static const Color muted2     = Color(0xFF3D5C48);
  static const Color border     = Color(0xFF1E3A27);
  static const Color red        = Color(0xFFEF4444);
  static const Color amber      = Color(0xFFF59E0B);
  static const Color purple     = Color(0xFF7C3AED);
  static const Color indigo     = Color(0xFF6366F1);
  static const Color teal       = Color(0xFF0D9488);
  static const Color surface    = Color(0xFF1A2B20);

  static ThemeData get theme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: green,
      brightness: Brightness.dark,
    ).copyWith(surface: bg, onSurface: text),
    scaffoldBackgroundColor: bg,
    textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
    appBarTheme: const AppBarTheme(
      backgroundColor: bg2,
      foregroundColor: text,
      elevation: 0,
    ),
  );
}
