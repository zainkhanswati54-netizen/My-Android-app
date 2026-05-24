// lib/theme.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── DARK PALETTE (unchanged) ──────────────────────
  static const Color bg         = Color(0xFF0F172A);  // Deep Slate
  static const Color bg2        = Color(0xFF1E293B);  // Slate 800
  static const Color card       = Color(0xFF1E293B);
  static const Color card2      = Color(0xFF253347);
  static const Color green      = Color(0xFF38BDF8);  // Sky Blue accent
  static const Color green2     = Color(0xFF7DD3FC);
  static const Color green3     = Color(0xFF0369A1);
  static const Color greenLight = Color(0xFFBAE6FD);
  static const Color text       = Color(0xFFF1F5F9);  // Near White
  static const Color text2      = Color(0xFF94A3B8);
  static const Color muted      = Color(0xFF64748B);
  static const Color muted2     = Color(0xFF334155);
  static const Color border     = Color(0xFF1E3A5F);
  static const Color red        = Color(0xFFFDA4AF);  // Muted Rose
  static const Color amber      = Color(0xFFFFD32A);
  static const Color purple     = Color(0xFF9C27B0);
  static const Color surface    = Color(0xFF253347);

  // ── LIGHT PALETTE ─────────────────────────────────
  static const Color lBg        = Color(0xFFF8FAFC);  // Slate 50
  static const Color lBg2       = Color(0xFFFFFFFF);  // Pure White
  static const Color lCard      = Color(0xFFFFFFFF);
  static const Color lCard2     = Color(0xFFF1F5F9);
  static const Color lBorder    = Color(0xFFE2E8F0);
  static const Color lText      = Color(0xFF0F172A);  // Dark Slate
  static const Color lText2     = Color(0xFF475569);
  static const Color lMuted     = Color(0xFF94A3B8);
  static const Color lSurface   = Color(0xFFF1F5F9);
  static const Color lAccent    = Color(0xFF0284C7);  // Deep Sky Blue
  static const Color lRed       = Color(0xFFE11D48);  // Rose 600

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

  // ── LIGHT THEME ───────────────────────────────────
  static ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(
      seedColor: lAccent,
      brightness: Brightness.light,
    ).copyWith(
      surface: lBg,
      onSurface: lText,
      primary: lAccent,
      secondary: const Color(0xFF0EA5E9),
      error: lRed,
    ),
    scaffoldBackgroundColor: lBg,
    textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme).apply(
      bodyColor: lText,
      displayColor: lText,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: lBg2,
      foregroundColor: lText,
      elevation: 0,
    ),
    sliderTheme: SliderThemeData(
      activeTrackColor: lAccent,
      inactiveTrackColor: lBorder,
      thumbColor: lAccent,
      overlayColor: lAccent.withOpacity(0.12),
      trackHeight: 3,
    ),
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((s) =>
        s.contains(WidgetState.selected) ? Colors.white : lMuted),
      trackColor: WidgetStateProperty.resolveWith((s) =>
        s.contains(WidgetState.selected) ? lAccent : lBorder),
    ),
  );
}
