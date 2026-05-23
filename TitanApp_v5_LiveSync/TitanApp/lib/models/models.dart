import 'package:flutter/material.dart';

enum AppLanguage { english, hindi, urdu }
enum VoiceGender { male, female }
enum VoiceEmotion {
  normal, happy, sad, whisper, shout,
  excited, calm, serious, sarcasm, fearful,
}

class LanguageConfig {
  final String name, code, flag, hintText, keyboardLocale, maleVoice, femaleVoice;
  final bool isRTL;
  const LanguageConfig({
    required this.name, required this.code, required this.flag,
    required this.isRTL, required this.hintText, required this.keyboardLocale,
    required this.maleVoice, required this.femaleVoice,
  });
}

const Map<AppLanguage, LanguageConfig> kLangConfigs = {
  AppLanguage.english: LanguageConfig(
    name: 'English', code: 'en', flag: 'assets/svg/lang_en.svg', isRTL: false,
    hintText: 'Type your text in English here...',
    keyboardLocale: 'en', maleVoice: 'en-US-GuyNeural', femaleVoice: 'en-US-JennyNeural',
  ),
  AppLanguage.hindi: LanguageConfig(
    name: 'Hindi', code: 'hi', flag: 'assets/svg/lang_hi.svg', isRTL: false,
    hintText: 'यहाँ हिंदी में लिखें...',
    keyboardLocale: 'hi', maleVoice: 'hi-IN-MadhurNeural', femaleVoice: 'hi-IN-SwaraNeural',
  ),
  AppLanguage.urdu: LanguageConfig(
    name: 'Urdu', code: 'ur', flag: 'assets/svg/lang_ur.svg', isRTL: true,
    hintText: 'یہاں اردو میں لکھیں...',
    keyboardLocale: 'ur', maleVoice: 'ur-PK-AsadNeural', femaleVoice: 'ur-PK-UzmaNeural',
  ),
};

class EmotionConfig {
  final String label, icon, volume;
  final Color color;
  final int rateBoost;
  const EmotionConfig({
    required this.label, required this.icon, required this.color,
    required this.volume, required this.rateBoost,
  });
}

const Map<VoiceEmotion, EmotionConfig> kEmotionConfigs = {
  VoiceEmotion.normal:  EmotionConfig(label: 'Normal',  icon: 'assets/svg/emotion_normal.svg', color: Color(0xFF334155), volume: '+0%',  rateBoost: 0),
  VoiceEmotion.happy:   EmotionConfig(label: 'Happy',   icon: 'assets/svg/emotion_happy.svg', color: Color(0xFF10B981), volume: '+10%', rateBoost: 5),
  VoiceEmotion.sad:     EmotionConfig(label: 'Sad',     icon: 'assets/svg/emotion_sad.svg', color: Color(0xFF38BDF8), volume: '-15%', rateBoost: -8),
  VoiceEmotion.whisper: EmotionConfig(label: 'Whisper', icon: 'assets/svg/emotion_whisper.svg', color: Color(0xFF7C3AED), volume: '-60%', rateBoost: -10),
  VoiceEmotion.shout:   EmotionConfig(label: 'Shout',   icon: 'assets/svg/preset_commercial.svg', color: Color(0xFFEF4444), volume: '+30%', rateBoost: 10),
  VoiceEmotion.excited: EmotionConfig(label: 'Excited', icon: 'assets/svg/emotion_excited.svg', color: Color(0xFFF97316), volume: '+20%', rateBoost: 15),
  VoiceEmotion.calm:    EmotionConfig(label: 'Calm',    icon: 'assets/svg/emotion_calm.svg', color: Color(0xFF0D9488), volume: '-10%', rateBoost: -12),
  VoiceEmotion.serious: EmotionConfig(label: 'Serious', icon: 'assets/svg/emotion_serious.svg', color: Color(0xFF6366F1), volume: '+0%',  rateBoost: -3),
  VoiceEmotion.sarcasm: EmotionConfig(label: 'Sarcasm', icon: 'assets/svg/emotion_serious.svg', color: Color(0xFFF59E0B), volume: '+5%',  rateBoost: 0),
  VoiceEmotion.fearful: EmotionConfig(label: 'Fearful', icon: 'assets/svg/emotion_sad.svg', color: Color(0xFFEC4899), volume: '-20%', rateBoost: -5),
};

class HistoryEntry {
  final String id, fileName, filePath, text;
  final AppLanguage language;
  final VoiceGender gender;
  final VoiceEmotion emotion;
  final DateTime createdAt;
  final int durationMs;

  const HistoryEntry({
    required this.id, required this.fileName, required this.filePath,
    required this.text, required this.language, required this.gender,
    required this.emotion, required this.createdAt, required this.durationMs,
  });

  Map<String, dynamic> toJson() => {
    'id': id, 'fileName': fileName, 'filePath': filePath, 'text': text,
    'language': language.index, 'gender': gender.index, 'emotion': emotion.index,
    'createdAt': createdAt.millisecondsSinceEpoch, 'durationMs': durationMs,
  };

  factory HistoryEntry.fromJson(Map<String, dynamic> j) => HistoryEntry(
    id: j['id'], fileName: j['fileName'], filePath: j['filePath'], text: j['text'],
    language: AppLanguage.values[j['language']],
    gender: VoiceGender.values[j['gender']],
    emotion: VoiceEmotion.values[j['emotion']],
    createdAt: DateTime.fromMillisecondsSinceEpoch(j['createdAt']),
    durationMs: j['durationMs'] ?? 0,
  );
}
