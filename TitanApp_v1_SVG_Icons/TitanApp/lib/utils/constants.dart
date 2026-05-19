import 'package:flutter/material.dart';

// ═══════════════════════════════════════════════
//  TITAN STUDIO PRO v3.0 — OBSIDIAN NEON THEME
//  Designed for maximum visual impact & buyer WOW
// ═══════════════════════════════════════════════

// ── OBSIDIAN NEON Dark Palette ──────────────────
const Color cBg      = Color(0xFF0B0F19);   // Deep Obsidian Black
const Color cBg2     = Color(0xFF0E1320);   // Slightly lighter obsidian
const Color cCard    = Color(0xFF161F30);   // Dark Charcoal cards
const Color cCard2   = Color(0xFF1C2840);   // Elevated card surface
const Color cGreen   = Color(0xFF00F2FE);   // Neon Cyan (primary accent)
const Color cGreen2  = Color(0xFF4FACFE);   // Electric Blue (secondary accent)
const Color cGreen3  = Color(0xFF003A55);   // Deep cyan tint
const Color cGreenL  = Color(0xFF80F8FF);   // Light neon cyan
const Color cText    = Color(0xFFFFFFFF);   // Pure White
const Color cText2   = Color(0xFF8A99AD);   // Muted Slate
const Color cMuted   = Color(0xFF5A6A7E);   // Muted secondary
const Color cMuted2  = Color(0xFF2D3D52);   // Very muted
const Color cBorder  = Color(0xFF1E2D45);   // Dark border
const Color cRed     = Color(0xFFFF4757);
const Color cAmber   = Color(0xFFFFD32A);
const Color cOrange  = Color(0xFFFF6B35);
const Color cBlue    = Color(0xFF4FACFE);   // Electric Blue
const Color cPurple  = Color(0xFF9C27B0);
const Color cIndigo  = Color(0xFF5C6BC0);
const Color cTeal    = Color(0xFF00B4D8);
const Color cSurface = Color(0xFF1C2840);
const Color cDarkRed = Color(0xFF7F0000);

// ── NEON GLOW HELPERS ────────────────────────────
const Color cNeonGlow  = Color(0xFF00F2FE);
const Color cNeonGlow2 = Color(0xFF4FACFE);

// ── GRADIENT HELPERS ─────────────────────────────
const LinearGradient kNeonGradient = LinearGradient(
  colors: [Color(0xFF00F2FE), Color(0xFF4FACFE)],
);
const LinearGradient kNeonGradientDiag = LinearGradient(
  colors: [Color(0xFF00F2FE), Color(0xFF4FACFE)],
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
);
const LinearGradient kSubtleGradient = LinearGradient(
  colors: [Color(0xFF161F30), Color(0xFF1C2840)],
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
);

// ── LANGUAGES (Only 3) ──────────────────────────
enum LangScript { latin, devanagari, arabic }

class LangConfig {
  final String code, maleVoice, femaleVoice, label, flag, name;
  final bool isRtl;
  final LangScript script;
  final TextDirection textDir;
  const LangConfig({
    required this.name,
    required this.code,
    required this.maleVoice,
    required this.femaleVoice,
    required this.isRtl,
    required this.script,
    required this.label,
    required this.flag,
  }) : textDir = isRtl ? TextDirection.rtl : TextDirection.ltr;
}

const Map<String, LangConfig> kLanguages = {
  'English': LangConfig(
    name: 'English', code: 'en',
    maleVoice: 'en-US-GuyNeural',
    femaleVoice: 'en-US-JennyNeural',
    isRtl: false, script: LangScript.latin,
    label: 'EN', flag: 'assets/svg/lang_en.svg',
  ),
  'Hindi': LangConfig(
    name: 'Hindi', code: 'hi',
    maleVoice: 'hi-IN-MadhurNeural',
    femaleVoice: 'hi-IN-SwaraNeural',
    isRtl: false, script: LangScript.devanagari,
    label: 'HI', flag: 'assets/svg/lang_hi.svg',
  ),
  'Urdu': LangConfig(
    name: 'Urdu', code: 'ur',
    maleVoice: 'ur-PK-AsadNeural',
    femaleVoice: 'ur-PK-UzmaNeural',
    isRtl: true, script: LangScript.arabic,
    label: 'UR', flag: 'assets/svg/lang_ur.svg',
  ),
};

// ── EMOTIONS ────────────────────────────────────
class EmotionConfig {
  final String icon, label, volume;
  final Color color;
  final int rateBoost;
  final double speed;
  final int pitch;
  const EmotionConfig({
    required this.icon, required this.label,
    required this.color, required this.volume,
    required this.rateBoost,
    required this.speed,
    required this.pitch,
  });
}

const Map<String, EmotionConfig> kEmotions = {
  'Normal':  EmotionConfig(icon: 'assets/svg/emotion_normal.svg', label: 'Normal',  color: cText,   volume: '+0%',  rateBoost: 0,   speed: 55, pitch:  0),
  'Happy':   EmotionConfig(icon: 'assets/svg/emotion_happy.svg', label: 'Happy',   color: cGreen,  volume: '+10%', rateBoost: 5,   speed: 65, pitch:  2),
  'Sad':     EmotionConfig(icon: 'assets/svg/emotion_sad.svg', label: 'Sad',     color: cBlue,   volume: '-15%', rateBoost: -8,  speed: 38, pitch: -3),
  'Whisper': EmotionConfig(icon: 'assets/svg/emotion_whisper.svg', label: 'Whisper', color: cPurple, volume: '-60%', rateBoost: -10, speed: 35, pitch: -2),
  'Shout':   EmotionConfig(icon: 'assets/svg/emotion_shout.svg', label: 'Shout',   color: cRed,    volume: '+30%', rateBoost: 10,  speed: 75, pitch:  3),
  'Excited': EmotionConfig(icon: 'assets/svg/emotion_excited.svg', label: 'Excited', color: cOrange, volume: '+20%', rateBoost: 15,  speed: 80, pitch:  4),
  'Calm':    EmotionConfig(icon: 'assets/svg/emotion_calm.svg', label: 'Calm',    color: cTeal,   volume: '-10%', rateBoost: -12, speed: 40, pitch: -1),
  'Serious': EmotionConfig(icon: 'assets/svg/emotion_serious.svg', label: 'Serious', color: cIndigo, volume: '+0%',  rateBoost: -3,  speed: 55, pitch: -2),
};

// ── CHARACTERS ──────────────────────────────────
class CharConfig {
  final String icon, desc, emotion, gender;
  final int speed, pitch;
  final List<String> allowedEmotions;
  const CharConfig({
    required this.icon, required this.desc,
    required this.emotion, required this.gender,
    required this.speed, required this.pitch,
    required this.allowedEmotions,
  });
}

const Map<String, CharConfig> kCharacters = {
  'Adam': CharConfig(
    icon: 'assets/svg/char_adam.svg', desc: 'Professional narrator', emotion: 'Normal',
    gender: 'Male', speed: 55, pitch: 0,
    allowedEmotions: ['Normal', 'Serious', 'Calm', 'Happy', 'Sad'],
  ),
  'Luna': CharConfig(
    icon: 'assets/svg/char_luna.svg', desc: 'Warm & expressive', emotion: 'Happy',
    gender: 'Female', speed: 50, pitch: 2,
    allowedEmotions: ['Happy', 'Excited', 'Sad', 'Normal', 'Whisper'],
  ),
  'Nova': CharConfig(
    icon: 'assets/svg/char_rex.svg', desc: 'Futuristic AI voice', emotion: 'Serious',
    gender: 'Female', speed: 60, pitch: 5,
    allowedEmotions: ['Serious', 'Normal', 'Excited', 'Calm'],
  ),
  'Zara': CharConfig(
    icon: 'assets/svg/char_nova.svg', desc: 'News anchor style', emotion: 'Serious',
    gender: 'Female', speed: 62, pitch: 0,
    allowedEmotions: ['Serious', 'Normal', 'Calm', 'Happy'],
  ),
  'Rex': CharConfig(
    icon: 'assets/svg/char_bolt.svg', desc: 'Deep powerful voice', emotion: 'Serious',
    gender: 'Male', speed: 45, pitch: -5,
    allowedEmotions: ['Serious', 'Shout', 'Calm', 'Normal', 'Sad'],
  ),
  'Aria': CharConfig(
    icon: 'assets/svg/char_zara.svg', desc: 'Soft storyteller', emotion: 'Calm',
    gender: 'Female', speed: 42, pitch: 3,
    allowedEmotions: ['Calm', 'Whisper', 'Sad', 'Happy', 'Normal'],
  ),
  'Bolt': CharConfig(
    icon: 'assets/svg/char_bolt.svg', desc: 'Fast energetic voice', emotion: 'Excited',
    gender: 'Male', speed: 80, pitch: 2,
    allowedEmotions: ['Excited', 'Happy', 'Shout', 'Normal'],
  ),
  'Sage': CharConfig(
    icon: 'assets/svg/char_sage.svg', desc: 'Wise meditation voice', emotion: 'Calm',
    gender: 'Male', speed: 30, pitch: -3,
    allowedEmotions: ['Calm', 'Serious', 'Whisper', 'Sad', 'Normal'],
  ),
};

// ── PRESETS ─────────────────────────────────────
class PresetConfig {
  final String icon, emotion, desc;
  final int speed, pitch;
  const PresetConfig({
    required this.icon, required this.emotion,
    required this.desc, required this.speed, required this.pitch,
  });
}

const Map<String, PresetConfig> kPresets = {
  'Narrator':   PresetConfig(icon: 'assets/svg/preset_narrator.svg', speed: 50, pitch: 0,  emotion: 'Calm',    desc: 'Clear storytelling'),
  'Newsreader': PresetConfig(icon: 'assets/svg/preset_newsreader.svg', speed: 60, pitch: 0,  emotion: 'Serious', desc: 'Professional news'),
  'Story':      PresetConfig(icon: 'assets/svg/preset_story.svg', speed: 45, pitch: 2,  emotion: 'Happy',   desc: 'Engaging story'),
  'Meditation': PresetConfig(icon: 'assets/svg/preset_meditation.svg', speed: 30, pitch: -2, emotion: 'Calm',    desc: 'Peaceful & slow'),
  'Commercial': PresetConfig(icon: 'assets/svg/preset_commercial.svg', speed: 65, pitch: 2,  emotion: 'Excited', desc: 'Upbeat & catchy'),
  'Audiobook':  PresetConfig(icon: 'assets/svg/preset_audiobook.svg', speed: 55, pitch: 0,  emotion: 'Normal',  desc: 'Long-form audio'),
  'Poet':       PresetConfig(icon: 'assets/svg/preset_poet.svg', speed: 40, pitch: 1,  emotion: 'Sad',     desc: 'Dramatic poetry'),
  'Kids':       PresetConfig(icon: 'assets/svg/preset_kids.svg', speed: 45, pitch: 3,  emotion: 'Happy',   desc: 'Fun & friendly'),
};

// ── VOICE PARAMS HELPERS ─────────────────────────
String speedToRate(int speedPct, String emotion) {
  int base = ((speedPct - 50) * 1.5).round();
  int boost = kEmotions[emotion]?.rateBoost ?? 0;
  int total = (base + boost).clamp(-50, 100);
  return total >= 0 ? '+$total%' : '$total%';
}

String pitchToHz(int pitchVal) {
  int hz = pitchVal * 15;
  return hz >= 0 ? '+${hz}Hz' : '${hz}Hz';
}

String emotionVolume(String emotion) {
  return kEmotions[emotion]?.volume ?? '+0%';
}
