// lib/models/models.dart

enum AppLanguage { english, hindi, urdu }

enum VoiceGender { male, female }

enum VoiceEmotion {
  normal, happy, sad, whisper, shout,
  excited, calm, serious, sarcasm, fearful,
}

class LanguageConfig {
  final String name;
  final String code;
  final String flag;
  final bool isRTL;
  final String hintText;
  final String keyboardLocale;
  final String maleVoice;
  final String femaleVoice;

  const LanguageConfig({
    required this.name,
    required this.code,
    required this.flag,
    required this.isRTL,
    required this.hintText,
    required this.keyboardLocale,
    required this.maleVoice,
    required this.femaleVoice,
  });
}

// ── Supported Languages ─────────────────────────────────
const Map<AppLanguage, LanguageConfig> kLanguages = {
  AppLanguage.english: LanguageConfig(
    name: 'English',
    code: 'en',
    flag: '🇺🇸',
    isRTL: false,
    hintText: 'Type your text in English here...',
    keyboardLocale: 'en',
    maleVoice: 'en-US-GuyNeural',
    femaleVoice: 'en-US-JennyNeural',
  ),
  AppLanguage.hindi: LanguageConfig(
    name: 'Hindi',
    code: 'hi',
    flag: '🇮🇳',
    isRTL: false,
    hintText: 'यहाँ हिंदी में लिखें...',
    keyboardLocale: 'hi',
    maleVoice: 'hi-IN-MadhurNeural',
    femaleVoice: 'hi-IN-SwaraNeural',
  ),
  AppLanguage.urdu: LanguageConfig(
    name: 'Urdu',
    code: 'ur',
    flag: '🇵🇰',
    isRTL: true,
    hintText: 'یہاں اردو میں لکھیں...',
    keyboardLocale: 'ur',
    maleVoice: 'ur-PK-AsadNeural',
    femaleVoice: 'ur-PK-UzmaNeural',
  ),
};

// ── Emotion Config ───────────────────────────────────────
class EmotionConfig {
  final String label;
  final String icon;
  final Color color;
  final String volume;
  final int rateBoost;

  const EmotionConfig({
    required this.label,
    required this.icon,
    required this.color,
    required this.volume,
    required this.rateBoost,
  });
}

import 'package:flutter/material.dart';

const Map<VoiceEmotion, EmotionConfig> kEmotions = {
  VoiceEmotion.normal:  EmotionConfig(label: 'Normal',  icon: '😐', color: Color(0xFF334155), volume: '+0%',  rateBoost: 0),
  VoiceEmotion.happy:   EmotionConfig(label: 'Happy',   icon: '😊', color: Color(0xFF10B981), volume: '+10%', rateBoost: 5),
  VoiceEmotion.sad:     EmotionConfig(label: 'Sad',     icon: '😢', color: Color(0xFF38BDF8), volume: '-15%', rateBoost: -8),
  VoiceEmotion.whisper: EmotionConfig(label: 'Whisper', icon: '🤫', color: Color(0xFF7C3AED), volume: '-60%', rateBoost: -10),
  VoiceEmotion.shout:   EmotionConfig(label: 'Shout',   icon: '📢', color: Color(0xFFEF4444), volume: '+30%', rateBoost: 10),
  VoiceEmotion.excited: EmotionConfig(label: 'Excited', icon: '🤩', color: Color(0xFFF97316), volume: '+20%', rateBoost: 15),
  VoiceEmotion.calm:    EmotionConfig(label: 'Calm',    icon: '😌', color: Color(0xFF0D9488), volume: '-10%', rateBoost: -12),
  VoiceEmotion.serious: EmotionConfig(label: 'Serious', icon: '🎙️', color: Color(0xFF6366F1), volume: '+0%',  rateBoost: -3),
  VoiceEmotion.sarcasm: EmotionConfig(label: 'Sarcasm', icon: '😏', color: Color(0xFFF59E0B), volume: '+5%',  rateBoost: 0),
  VoiceEmotion.fearful: EmotionConfig(label: 'Fearful', icon: '😨', color: Color(0xFFEC4899), volume: '-20%', rateBoost: -5),
};

// ── Voice Characters ─────────────────────────────────────
class VoiceCharacter {
  final String id;
  final String name;
  final String description;
  final String icon;
  final AppLanguage language;
  final VoiceGender gender;
  final VoiceEmotion defaultEmotion;
  final double defaultSpeed;  // 0.5 to 2.0
  final double defaultPitch;  // -20 to +20 Hz

  const VoiceCharacter({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    required this.language,
    required this.gender,
    required this.defaultEmotion,
    required this.defaultSpeed,
    required this.defaultPitch,
  });
}

const List<VoiceCharacter> kCharacters = [
  // ── English Characters ──────────────────────────────
  VoiceCharacter(
    id: 'en_narrator',
    name: 'Adam',
    description: 'Professional Narrator',
    icon: '🎙️',
    language: AppLanguage.english,
    gender: VoiceGender.male,
    defaultEmotion: VoiceEmotion.calm,
    defaultSpeed: 0.9,
    defaultPitch: 0,
  ),
  VoiceCharacter(
    id: 'en_news',
    name: 'James',
    description: 'News Anchor',
    icon: '📰',
    language: AppLanguage.english,
    gender: VoiceGender.male,
    defaultEmotion: VoiceEmotion.serious,
    defaultSpeed: 1.0,
    defaultPitch: -5,
  ),
  VoiceCharacter(
    id: 'en_sarah',
    name: 'Sarah',
    description: 'Friendly Guide',
    icon: '👩‍💼',
    language: AppLanguage.english,
    gender: VoiceGender.female,
    defaultEmotion: VoiceEmotion.happy,
    defaultSpeed: 1.0,
    defaultPitch: 5,
  ),
  VoiceCharacter(
    id: 'en_storyteller',
    name: 'Emily',
    description: 'Storyteller',
    icon: '📖',
    language: AppLanguage.english,
    gender: VoiceGender.female,
    defaultEmotion: VoiceEmotion.excited,
    defaultSpeed: 0.85,
    defaultPitch: 3,
  ),
  // ── Hindi Characters ────────────────────────────────
  VoiceCharacter(
    id: 'hi_ravi',
    name: 'Ravi',
    description: 'हिंदी उद्घोषक',
    icon: '🎤',
    language: AppLanguage.hindi,
    gender: VoiceGender.male,
    defaultEmotion: VoiceEmotion.serious,
    defaultSpeed: 0.95,
    defaultPitch: 0,
  ),
  VoiceCharacter(
    id: 'hi_priya',
    name: 'Priya',
    description: 'हिंदी कहानीकार',
    icon: '🌸',
    language: AppLanguage.hindi,
    gender: VoiceGender.female,
    defaultEmotion: VoiceEmotion.happy,
    defaultSpeed: 1.0,
    defaultPitch: 5,
  ),
  VoiceCharacter(
    id: 'hi_kumar',
    name: 'Kumar',
    description: 'समाचार वाचक',
    icon: '📺',
    language: AppLanguage.hindi,
    gender: VoiceGender.male,
    defaultEmotion: VoiceEmotion.calm,
    defaultSpeed: 0.9,
    defaultPitch: -3,
  ),
  // ── Urdu Characters ─────────────────────────────────
  VoiceCharacter(
    id: 'ur_asad',
    name: 'Asad',
    description: 'اردو مرد آواز',
    icon: '🎙️',
    language: AppLanguage.urdu,
    gender: VoiceGender.male,
    defaultEmotion: VoiceEmotion.serious,
    defaultSpeed: 0.9,
    defaultPitch: 0,
  ),
  VoiceCharacter(
    id: 'ur_uzma',
    name: 'Uzma',
    description: 'اردو خاتون آواز',
    icon: '🌹',
    language: AppLanguage.urdu,
    gender: VoiceGender.female,
    defaultEmotion: VoiceEmotion.calm,
    defaultSpeed: 0.95,
    defaultPitch: 5,
  ),
  VoiceCharacter(
    id: 'ur_khalid',
    name: 'Khalid',
    description: 'خبریں پڑھنے والا',
    icon: '📻',
    language: AppLanguage.urdu,
    gender: VoiceGender.male,
    defaultEmotion: VoiceEmotion.normal,
    defaultSpeed: 0.85,
    defaultPitch: -5,
  ),
];

// ── History Entry ─────────────────────────────────────────
class HistoryEntry {
  final String id;
  final String fileName;
  final String filePath;
  final String text;
  final AppLanguage language;
  final VoiceGender gender;
  final VoiceEmotion emotion;
  final DateTime createdAt;
  final int durationMs;

  const HistoryEntry({
    required this.id,
    required this.fileName,
    required this.filePath,
    required this.text,
    required this.language,
    required this.gender,
    required this.emotion,
    required this.createdAt,
    required this.durationMs,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'fileName': fileName,
    'filePath': filePath,
    'text': text,
    'language': language.index,
    'gender': gender.index,
    'emotion': emotion.index,
    'createdAt': createdAt.millisecondsSinceEpoch,
    'durationMs': durationMs,
  };

  factory HistoryEntry.fromJson(Map<String, dynamic> j) => HistoryEntry(
    id: j['id'],
    fileName: j['fileName'],
    filePath: j['filePath'],
    text: j['text'],
    language: AppLanguage.values[j['language']],
    gender: VoiceGender.values[j['gender']],
    emotion: VoiceEmotion.values[j['emotion']],
    createdAt: DateTime.fromMillisecondsSinceEpoch(j['createdAt']),
    durationMs: j['durationMs'] ?? 0,
  );
}
