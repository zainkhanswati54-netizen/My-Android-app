import 'package:flutter/material.dart';

// ═══════════════════════════════════════════════
//  TITAN STUDIO PRO v2.0 — Cyber Mint Theme
// ═══════════════════════════════════════════════

// ── HTML Cyber Mint DARK Theme ──────────────────
const Color cBg      = Color(0xFF0A0F0D);   // --bg
const Color cBg2     = Color(0xFF0F1812);   // --bg2
const Color cCard    = Color(0xFF131F17);   // --card
const Color cCard2   = Color(0xFF1A2B20);   // --card2
const Color cGreen   = Color(0xFF10B981);   // --green
const Color cGreen2  = Color(0xFF059669);   // --green2
const Color cGreen3  = Color(0xFF064E3B);   // --green3
const Color cGreenL  = Color(0xFF34D399);   // greenLight
const Color cText    = Color(0xFFE2F0E8);   // --text (light on dark)
const Color cText2   = Color(0xFFA3C4AD);   // --text2
const Color cMuted   = Color(0xFF5A7A64);   // --muted
const Color cMuted2  = Color(0xFF3D5C48);   // muted2
const Color cBorder  = Color(0xFF1E3A27);   // --border
const Color cRed     = Color(0xFFEF4444);
const Color cAmber   = Color(0xFFF59E0B);
const Color cOrange  = Color(0xFFF97316);
const Color cBlue    = Color(0xFF0EA5E9);
const Color cPurple  = Color(0xFF7C3AED);
const Color cIndigo  = Color(0xFF6366F1);
const Color cTeal    = Color(0xFF0D9488);
const Color cSurface = Color(0xFF1A2B20);   // card2 as surface
const Color cDarkRed = Color(0xFF991B1B);

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
    label: 'EN', flag: '🇺🇸',
  ),
  'Hindi': LangConfig(
    name: 'Hindi', code: 'hi',
    maleVoice: 'hi-IN-MadhurNeural',
    femaleVoice: 'hi-IN-SwaraNeural',
    isRtl: false, script: LangScript.devanagari,
    label: 'HI', flag: '🇮🇳',
  ),
  'Urdu': LangConfig(
    name: 'Urdu', code: 'ur',
    maleVoice: 'ur-PK-AsadNeural',
    femaleVoice: 'ur-PK-UzmaNeural',
    isRtl: true, script: LangScript.arabic,
    label: 'UR', flag: '🇵🇰',
  ),
};

// ── EMOTIONS ────────────────────────────────────
class EmotionConfig {
  final String icon, label, volume;
  final Color color;
  final int rateBoost;
  final double speed;  // slider value (10-100)
  final int pitch;     // slider value (-10 to +10)
  const EmotionConfig({
    required this.icon, required this.label,
    required this.color, required this.volume,
    required this.rateBoost,
    required this.speed,
    required this.pitch,
  });
}

const Map<String, EmotionConfig> kEmotions = {
  'Normal':  EmotionConfig(icon: '😐', label: 'Normal',  color: cText,   volume: '+0%',  rateBoost: 0,   speed: 55,  pitch:  0),
  'Happy':   EmotionConfig(icon: '😊', label: 'Happy',   color: cGreen,  volume: '+10%', rateBoost: 5,   speed: 65,  pitch:  2),
  'Sad':     EmotionConfig(icon: '😢', label: 'Sad',     color: cBlue,   volume: '-15%', rateBoost: -8,  speed: 38,  pitch: -3),
  'Whisper': EmotionConfig(icon: '🤫', label: 'Whisper', color: cPurple, volume: '-60%', rateBoost: -10, speed: 35,  pitch: -2),
  'Shout':   EmotionConfig(icon: '😤', label: 'Shout',   color: cRed,    volume: '+30%', rateBoost: 10,  speed: 75,  pitch:  3),
  'Excited': EmotionConfig(icon: '🤩', label: 'Excited', color: cOrange, volume: '+20%', rateBoost: 15,  speed: 80,  pitch:  4),
  'Calm':    EmotionConfig(icon: '😌', label: 'Calm',    color: cTeal,   volume: '-10%', rateBoost: -12, speed: 40,  pitch: -1),
  'Serious': EmotionConfig(icon: '😑', label: 'Serious', color: cIndigo, volume: '+0%',  rateBoost: -3,  speed: 55,  pitch: -2),
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
    icon: '👨‍💼', desc: 'Professional narrator', emotion: 'Normal',
    gender: 'Male', speed: 55, pitch: 0,
    allowedEmotions: ['Normal', 'Serious', 'Calm', 'Happy', 'Sad'],
  ),
  'Luna': CharConfig(
    icon: '👩‍🎤', desc: 'Warm & expressive', emotion: 'Happy',
    gender: 'Female', speed: 50, pitch: 2,
    allowedEmotions: ['Happy', 'Excited', 'Sad', 'Normal', 'Whisper'],
  ),
  'Nova': CharConfig(
    icon: '🤖', desc: 'Futuristic AI voice', emotion: 'Serious',
    gender: 'Female', speed: 60, pitch: 5,
    allowedEmotions: ['Serious', 'Normal', 'Excited', 'Calm'],
  ),
  'Zara': CharConfig(
    icon: '👩‍💻', desc: 'News anchor style', emotion: 'Serious',
    gender: 'Female', speed: 62, pitch: 0,
    allowedEmotions: ['Serious', 'Normal', 'Calm', 'Happy'],
  ),
  'Rex': CharConfig(
    icon: '🦁', desc: 'Deep powerful voice', emotion: 'Serious',
    gender: 'Male', speed: 45, pitch: -5,
    allowedEmotions: ['Serious', 'Shout', 'Calm', 'Normal', 'Sad'],
  ),
  'Aria': CharConfig(
    icon: '🧚', desc: 'Soft storyteller', emotion: 'Calm',
    gender: 'Female', speed: 42, pitch: 3,
    allowedEmotions: ['Calm', 'Whisper', 'Sad', 'Happy', 'Normal'],
  ),
  'Bolt': CharConfig(
    icon: '⚡', desc: 'Fast energetic voice', emotion: 'Excited',
    gender: 'Male', speed: 80, pitch: 2,
    allowedEmotions: ['Excited', 'Happy', 'Shout', 'Normal'],
  ),
  'Sage': CharConfig(
    icon: '🧙', desc: 'Wise meditation voice', emotion: 'Calm',
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
  'Narrator':   PresetConfig(icon: '📖', speed: 50, pitch: 0,   emotion: 'Calm',    desc: 'Clear storytelling'),
  'Newsreader': PresetConfig(icon: '📰', speed: 60, pitch: 0,   emotion: 'Serious', desc: 'Professional news'),
  'Story':      PresetConfig(icon: '✨', speed: 45, pitch: 2,   emotion: 'Happy',   desc: 'Engaging story'),
  'Meditation': PresetConfig(icon: '🧘', speed: 30, pitch: -2,  emotion: 'Calm',    desc: 'Peaceful & slow'),
  'Commercial': PresetConfig(icon: '📢', speed: 65, pitch: 2,   emotion: 'Excited', desc: 'Upbeat & catchy'),
  'Audiobook':  PresetConfig(icon: '🎧', speed: 55, pitch: 0,   emotion: 'Normal',  desc: 'Long-form audio'),
  'Poet':       PresetConfig(icon: '🎭', speed: 40, pitch: 1,   emotion: 'Sad',     desc: 'Dramatic poetry'),
  'Kids':       PresetConfig(icon: '🧒', speed: 45, pitch: 3,   emotion: 'Happy',   desc: 'Fun & friendly'),
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
