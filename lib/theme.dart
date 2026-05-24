import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── DARK PALETTE ──────────────────────────────────
  static const Color bg         = Color(0xFF0F172A);
  static const Color bg2        = Color(0xFF1E293B);
  static const Color green      = Color(0xFF38BDF8);
  static const Color green2     = Color(0xFF7DD3FC);
  static const Color text       = Color(0xFFF1F5F9);
  static const Color text2      = Color(0xFF94A3B8);
  static const Color muted      = Color(0xFF64748B);
  static const Color border     = Color(0xFF1E3A5F);
  static const Color red        = Color(0xFFFDA4AF);
  static const Color amber      = Color(0xFFFFD32A);

  // ── DARK THEME ────────────────────────────────────
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
      error: red,
    ),
    scaffoldBackgroundColor: bg,
    textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).apply(
      bodyColor: text,
      displayColor: text,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: bg2,
      foregroundColor: text,
      elevation: 0,
    ),
    cardTheme: CardTheme(
      color: bg2,
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
    ),
    sliderTheme: SliderThemeData(
      activeTrackColor: green,
      inactiveTrackColor: border,
      thumbColor: green,
      overlayColor: green.withOpacity(0.15),
      trackHeight: 3,
    ),
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((s) =>
        s.contains(WidgetState.selected) ? bg : muted),
      trackColor: WidgetStateProperty.resolveWith((s) =>
        s.contains(WidgetState.selected) ? green : border),
    ),
  );

  // lightTheme same as dark (light mode removed)
  static ThemeData get lightTheme => theme;
}
