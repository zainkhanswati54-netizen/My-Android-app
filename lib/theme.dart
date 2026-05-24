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

  // ── LIGHT PALETTE — YouTube/ChatGPT/Claude style ──
  static const Color lBg        = Color(0xFFFFFFFF);  // Pure White
  static const Color lBg2       = Color(0xFFF9FAFB);  // Gray 50
  static const Color lCard      = Color(0xFFFFFFFF);
  static const Color lCard2     = Color(0xFFF3F4F6);  // Gray 100
  static const Color lBorder    = Color(0xFFE5E7EB);  // Gray 200
  static const Color lText      = Color(0xFF111827);  // Gray 900
  static const Color lText2     = Color(0xFF6B7280);  // Gray 500
  static const Color lMuted     = Color(0xFF9CA3AF);  // Gray 400
  static const Color lAccent    = Color(0xFF2563EB);  // Blue 600 (YouTube-ish)
  static const Color lAccent2   = Color(0xFF3B82F6);  // Blue 500
  static const Color lRed       = Color(0xFFDC2626);  // Red 600
  static const Color lGreen     = Color(0xFF16A34A);  // Green 600
  static const Color lAmber     = Color(0xFFD97706);  // Amber 600
  static const Color lSurface   = Color(0xFFF9FAFB);

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
    cardTheme: CardThemeData(
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

  // ── LIGHT THEME — Professional Clean ──────────────
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
      secondary: lAccent2,
      error: lRed,
      surfaceContainerHighest: lCard2,
    ),
    scaffoldBackgroundColor: lBg2,
    textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme).apply(
      bodyColor: lText,
      displayColor: lText,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: lBg,
      foregroundColor: lText,
      elevation: 0,
      shadowColor: Colors.transparent,
      surfaceTintColor: Colors.transparent,
    ),
    cardTheme: CardThemeData(
      color: lCard,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: lBorder, width: 1),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: lCard2,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: lBorder),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: lBorder),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: lAccent, width: 2),
      ),
      hintStyle: const TextStyle(color: lMuted),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: lAccent,
        foregroundColor: Colors.white,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
      ),
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
    dividerTheme: const DividerThemeData(
      color: lBorder,
      thickness: 1,
      space: 0,
    ),
    iconTheme: const IconThemeData(color: lText2),
    chipTheme: ChipThemeData(
      backgroundColor: lCard2,
      labelStyle: const TextStyle(color: lText, fontWeight: FontWeight.w500),
      side: const BorderSide(color: lBorder),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    ),
  );
}
