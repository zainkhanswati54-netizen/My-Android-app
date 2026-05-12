// lib/theme.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── Cyber Mint Palette ──────────────────────────────────
  static const Color bg         = Color(0xFFFFFFFF);
  static const Color bg2        = Color(0xFFF0FDF4);
  static const Color card       = Color(0xFFF0FDF4);
  static const Color card2      = Color(0xFFDCFCE7);
  static const Color green      = Color(0xFF10B981);
  static const Color green2     = Color(0xFF059669);
  static const Color green3     = Color(0xFF064E3B);
  static const Color greenLight = Color(0xFF34D399);
  static const Color text       = Color(0xFF334155);
  static const Color text2      = Color(0xFF1E293B);
  static const Color muted      = Color(0xFF64748B);
  static const Color muted2     = Color(0xFF94A3B8);
  static const Color border     = Color(0xFFD1FAE5);
  static const Color red        = Color(0xFFEF4444);
  static const Color amber      = Color(0xFFF59E0B);
  static const Color purple     = Color(0xFF7C3AED);
  static const Color indigo     = Color(0xFF6366F1);
  static const Color teal       = Color(0xFF0D9488);
  static const Color surface    = Color(0xFFECFDF5);

  static ThemeData get theme => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: green,
      brightness: Brightness.light,
    ),
    scaffoldBackgroundColor: bg,
    textTheme: GoogleFonts.poppinsTextTheme(),
    appBarTheme: const AppBarTheme(
      backgroundColor: bg2,
      foregroundColor: text2,
      elevation: 0,
    ),
  );
}
