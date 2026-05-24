import 'package:flutter/material.dart';

// ═══════════════════════════════════════════════
//  TITAN STUDIO PRO v1.0 — OBSIDIAN NEON THEME
// ═══════════════════════════════════════════════

// ── OBSIDIAN NEON Dark Palette ──────────────────
const Color cBg      = Color(0xFF0F172A);  // Deep Slate
const Color cBg2     = Color(0xFF1E293B);  // Slate 800
const Color cCard    = Color(0xFF1E293B);
const Color cCard2   = Color(0xFF253347);
const Color cGreen   = Color(0xFF38BDF8);  // Sky Blue
const Color cGreen2  = Color(0xFF7DD3FC);
const Color cGreen3  = Color(0xFF0369A1);
const Color cGreenL  = Color(0xFFBAE6FD);
const Color cText    = Color(0xFFF1F5F9);  // Near White
const Color cText2   = Color(0xFF94A3B8);
const Color cMuted   = Color(0xFF64748B);
const Color cMuted2  = Color(0xFF334155);
const Color cBorder  = Color(0xFF1E3A5F);
const Color cRed     = Color(0xFFFDA4AF);  // Muted Rose
const Color cAmber   = Color(0xFFFFD32A);
const Color cOrange  = Color(0xFFFF6B35);
const Color cBlue    = Color(0xFF7DD3FC);
const Color cPurple  = Color(0xFF9C27B0);
const Color cIndigo  = Color(0xFF5C6BC0);
const Color cTeal    = Color(0xFF38BDF8);
const Color cSurface = Color(0xFF253347);
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


// ═══════════════════════════════════════════════
//  LIGHT THEME PALETTE — Professional Clean
//  YouTube / ChatGPT / Claude style
// ═══════════════════════════════════════════════
const Color cLBg      = Color(0xFFFFFFFF);  // Pure White
const Color cLBg2     = Color(0xFFF9FAFB);  // Gray 50
const Color cLCard    = Color(0xFFFFFFFF);
const Color cLCard2   = Color(0xFFF3F4F6);  // Gray 100
const Color cLBorder  = Color(0xFFE5E7EB);  // Gray 200
const Color cLText    = Color(0xFF111827);  // Gray 900
const Color cLText2   = Color(0xFF6B7280);  // Gray 500
const Color cLMuted   = Color(0xFF9CA3AF);  // Gray 400
const Color cLSurface = Color(0xFFF9FAFB);
const Color cLAccent  = Color(0xFF2563EB);  // Blue 600
const Color cLAccent2 = Color(0xFF3B82F6);  // Blue 500
const Color cLRed     = Color(0xFFDC2626);  // Red 600
const Color cLGreen   = Color(0xFF16A34A);  // Green 600
const Color cLAmber   = Color(0xFFD97706);  // Amber 600

// ═══════════════════════════════════════════════
//  LANGUAGES — 39 languages, Azure Edge TTS
//  "flag" asset: lang_en.svg, lang_hi.svg, lang_ur.svg
//  exist already; others use lang_default.svg fallback.
//  Add real flag SVGs later per language as needed.
// ═══════════════════════════════════════════════

enum LangScript { latin, devanagari, arabic, cjk, cyrillic, other }

class LangConfig {
  final String code, maleVoice, femaleVoice, label, flag, name, hintText;
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
    required this.hintText,
  }) : textDir = isRtl ? TextDirection.rtl : TextDirection.ltr;
}

const Map<String, LangConfig> kLanguages = {
  // ── Most popular first (shown first in list) ──────────────────────
  'English': LangConfig(
    name: 'English', code: 'en', label: 'EN',
    maleVoice: 'en-US-GuyNeural', femaleVoice: 'en-US-JennyNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_en.svg',
    hintText: 'Type your text in English here...',
  ),
  'Hindi': LangConfig(
    name: 'Hindi', code: 'hi', label: 'HI',
    maleVoice: 'hi-IN-MadhurNeural', femaleVoice: 'hi-IN-SwaraNeural',
    isRtl: false, script: LangScript.devanagari,
    flag: 'assets/svg/lang_hi.svg',
    hintText: 'यहाँ हिंदी में लिखें...',
  ),
  'Urdu': LangConfig(
    name: 'Urdu', code: 'ur', label: 'UR',
    maleVoice: 'ur-PK-AsadNeural', femaleVoice: 'ur-PK-UzmaNeural',
    isRtl: true, script: LangScript.arabic,
    flag: 'assets/svg/lang_ur.svg',
    hintText: 'یہاں اردو میں لکھیں...',
  ),
  'Arabic': LangConfig(
    name: 'Arabic', code: 'ar', label: 'AR',
    maleVoice: 'ar-SA-HamedNeural', femaleVoice: 'ar-SA-ZariyahNeural',
    isRtl: true, script: LangScript.arabic,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'اكتب النص هنا...',
  ),
  'Spanish': LangConfig(
    name: 'Spanish', code: 'es', label: 'ES',
    maleVoice: 'es-ES-AlvaroNeural', femaleVoice: 'es-ES-ElviraNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Escribe tu texto en español aquí...',
  ),
  'French': LangConfig(
    name: 'French', code: 'fr', label: 'FR',
    maleVoice: 'fr-FR-HenriNeural', femaleVoice: 'fr-FR-DeniseNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Écrivez votre texte en français ici...',
  ),
  'German': LangConfig(
    name: 'German', code: 'de', label: 'DE',
    maleVoice: 'de-DE-ConradNeural', femaleVoice: 'de-DE-KatjaNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Schreiben Sie hier Ihren deutschen Text...',
  ),
  'Portuguese': LangConfig(
    name: 'Portuguese', code: 'pt', label: 'PT',
    maleVoice: 'pt-BR-AntonioNeural', femaleVoice: 'pt-BR-FranciscaNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Digite seu texto em português aqui...',
  ),
  'Russian': LangConfig(
    name: 'Russian', code: 'ru', label: 'RU',
    maleVoice: 'ru-RU-DmitryNeural', femaleVoice: 'ru-RU-SvetlanaNeural',
    isRtl: false, script: LangScript.cyrillic,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Введите текст на русском здесь...',
  ),
  'Chinese': LangConfig(
    name: 'Chinese', code: 'zh', label: 'ZH',
    maleVoice: 'zh-CN-YunxiNeural', femaleVoice: 'zh-CN-XiaoxiaoNeural',
    isRtl: false, script: LangScript.cjk,
    flag: 'assets/svg/lang_default.svg',
    hintText: '在这里输入中文...',
  ),
  'Japanese': LangConfig(
    name: 'Japanese', code: 'ja', label: 'JA',
    maleVoice: 'ja-JP-KeitaNeural', femaleVoice: 'ja-JP-NanamiNeural',
    isRtl: false, script: LangScript.cjk,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'ここに日本語のテキストを入力してください...',
  ),
  'Korean': LangConfig(
    name: 'Korean', code: 'ko', label: 'KO',
    maleVoice: 'ko-KR-InJoonNeural', femaleVoice: 'ko-KR-SunHiNeural',
    isRtl: false, script: LangScript.cjk,
    flag: 'assets/svg/lang_default.svg',
    hintText: '여기에 한국어 텍스트를 입력하세요...',
  ),
  'Italian': LangConfig(
    name: 'Italian', code: 'it', label: 'IT',
    maleVoice: 'it-IT-DiegoNeural', femaleVoice: 'it-IT-ElsaNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Scrivi il tuo testo in italiano qui...',
  ),
  'Turkish': LangConfig(
    name: 'Turkish', code: 'tr', label: 'TR',
    maleVoice: 'tr-TR-AhmetNeural', femaleVoice: 'tr-TR-EmelNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Türkçe metninizi buraya yazın...',
  ),
  'Dutch': LangConfig(
    name: 'Dutch', code: 'nl', label: 'NL',
    maleVoice: 'nl-NL-MaartenNeural', femaleVoice: 'nl-NL-ColetteNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Typ hier uw Nederlandse tekst...',
  ),
  'Polish': LangConfig(
    name: 'Polish', code: 'pl', label: 'PL',
    maleVoice: 'pl-PL-MarekNeural', femaleVoice: 'pl-PL-ZofiaNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Wpisz swój tekst po polsku tutaj...',
  ),
  'Swedish': LangConfig(
    name: 'Swedish', code: 'sv', label: 'SV',
    maleVoice: 'sv-SE-MattiasNeural', femaleVoice: 'sv-SE-SofieNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Skriv din svenska text här...',
  ),
  'Danish': LangConfig(
    name: 'Danish', code: 'da', label: 'DA',
    maleVoice: 'da-DK-JeppeNeural', femaleVoice: 'da-DK-ChristelNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Skriv din danske tekst her...',
  ),
  'Norwegian': LangConfig(
    name: 'Norwegian', code: 'no', label: 'NO',
    maleVoice: 'nb-NO-FinnNeural', femaleVoice: 'nb-NO-PernilleNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Skriv din norske tekst her...',
  ),
  'Finnish': LangConfig(
    name: 'Finnish', code: 'fi', label: 'FI',
    maleVoice: 'fi-FI-HarriNeural', femaleVoice: 'fi-FI-NooraNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Kirjoita suomenkielinen teksti tähän...',
  ),
  'Indonesian': LangConfig(
    name: 'Indonesian', code: 'id', label: 'ID',
    maleVoice: 'id-ID-ArdiNeural', femaleVoice: 'id-ID-GadisNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Ketik teks Bahasa Indonesia Anda di sini...',
  ),
  'Malay': LangConfig(
    name: 'Malay', code: 'ms', label: 'MS',
    maleVoice: 'ms-MY-OsmanNeural', femaleVoice: 'ms-MY-YasminNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Taip teks Bahasa Melayu anda di sini...',
  ),
  'Thai': LangConfig(
    name: 'Thai', code: 'th', label: 'TH',
    maleVoice: 'th-TH-NiwatNeural', femaleVoice: 'th-TH-PremwadeeNeural',
    isRtl: false, script: LangScript.other,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'พิมพ์ข้อความภาษาไทยที่นี่...',
  ),
  'Vietnamese': LangConfig(
    name: 'Vietnamese', code: 'vi', label: 'VI',
    maleVoice: 'vi-VN-NamMinhNeural', femaleVoice: 'vi-VN-HoaiMyNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Nhập văn bản tiếng Việt của bạn tại đây...',
  ),
  'Romanian': LangConfig(
    name: 'Romanian', code: 'ro', label: 'RO',
    maleVoice: 'ro-RO-EmilNeural', femaleVoice: 'ro-RO-AlinaNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Tastați textul în română aici...',
  ),
  'Hungarian': LangConfig(
    name: 'Hungarian', code: 'hu', label: 'HU',
    maleVoice: 'hu-HU-TamasNeural', femaleVoice: 'hu-HU-NoemiNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Írja be a magyar szöveget ide...',
  ),
  'Czech': LangConfig(
    name: 'Czech', code: 'cs', label: 'CS',
    maleVoice: 'cs-CZ-AntoninNeural', femaleVoice: 'cs-CZ-VlastaNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Zadejte svůj český text zde...',
  ),
  'Ukrainian': LangConfig(
    name: 'Ukrainian', code: 'uk', label: 'UK',
    maleVoice: 'uk-UA-OstapNeural', femaleVoice: 'uk-UA-PolinaNeural',
    isRtl: false, script: LangScript.cyrillic,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Введіть текст українською тут...',
  ),
  'Greek': LangConfig(
    name: 'Greek', code: 'el', label: 'EL',
    maleVoice: 'el-GR-NestorasNeural', femaleVoice: 'el-GR-AthinaNeural',
    isRtl: false, script: LangScript.other,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Πληκτρολογήστε το κείμενό σας στα ελληνικά εδώ...',
  ),
  'Hebrew': LangConfig(
    name: 'Hebrew', code: 'he', label: 'HE',
    maleVoice: 'he-IL-AvriNeural', femaleVoice: 'he-IL-HilaNeural',
    isRtl: true, script: LangScript.arabic,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'הקלד את הטקסט שלך בעברית כאן...',
  ),
  'Bengali': LangConfig(
    name: 'Bengali', code: 'bn', label: 'BN',
    maleVoice: 'bn-BD-PradeepNeural', femaleVoice: 'bn-BD-NabanitaNeural',
    isRtl: false, script: LangScript.other,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'এখানে বাংলায় লিখুন...',
  ),
  'Tamil': LangConfig(
    name: 'Tamil', code: 'ta', label: 'TA',
    maleVoice: 'ta-IN-ValluvarNeural', femaleVoice: 'ta-IN-PallaviNeural',
    isRtl: false, script: LangScript.other,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'இங்கே தமிழில் தட்டச்சு செய்யுங்கள்...',
  ),
  'Telugu': LangConfig(
    name: 'Telugu', code: 'te', label: 'TE',
    maleVoice: 'te-IN-MohanNeural', femaleVoice: 'te-IN-ShrutiNeural',
    isRtl: false, script: LangScript.other,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'ఇక్కడ తెలుగులో టైప్ చేయండి...',
  ),
  'Marathi': LangConfig(
    name: 'Marathi', code: 'mr', label: 'MR',
    maleVoice: 'mr-IN-ManoharNeural', femaleVoice: 'mr-IN-AarohiNeural',
    isRtl: false, script: LangScript.devanagari,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'इथे मराठीत टाइप करा...',
  ),
  'Gujarati': LangConfig(
    name: 'Gujarati', code: 'gu', label: 'GU',
    maleVoice: 'gu-IN-NiranjanNeural', femaleVoice: 'gu-IN-DhwaniNeural',
    isRtl: false, script: LangScript.other,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'અહીં ગુજરાતીમાં ટાઇપ કરો...',
  ),
  'Punjabi': LangConfig(
    name: 'Punjabi', code: 'pa', label: 'PA',
    maleVoice: 'pa-IN-OjasNeural', femaleVoice: 'pa-IN-VaaniNeural',
    isRtl: false, script: LangScript.other,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'ਇੱਥੇ ਪੰਜਾਬੀ ਵਿੱਚ ਟਾਈਪ ਕਰੋ...',
  ),
  'Persian': LangConfig(
    name: 'Persian', code: 'fa', label: 'FA',
    maleVoice: 'fa-IR-FaridNeural', femaleVoice: 'fa-IR-DilaraNeural',
    isRtl: true, script: LangScript.arabic,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'متن فارسی خود را اینجا بنویسید...',
  ),
  'Swahili': LangConfig(
    name: 'Swahili', code: 'sw', label: 'SW',
    maleVoice: 'sw-KE-RafikiNeural', femaleVoice: 'sw-KE-ZuriNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Andika maandishi yako kwa Kiswahili hapa...',
  ),
  'Afrikaans': LangConfig(
    name: 'Afrikaans', code: 'af', label: 'AF',
    maleVoice: 'af-ZA-WillemNeural', femaleVoice: 'af-ZA-AdriNeural',
    isRtl: false, script: LangScript.latin,
    flag: 'assets/svg/lang_default.svg',
    hintText: 'Tik u Afrikaanse teks hier in...',
  ),
};

// ── Helper: get default hint for selected language ───────────
String getLangHint(String langName) =>
    kLanguages[langName]?.hintText ?? 'Type your text here...';

// ── Helper: is this language RTL? ───────────────────────────
bool isLangRtl(String langName) =>
    kLanguages[langName]?.isRtl ?? false;

// ═══════════════════════════════════════════════
//  EMOTIONS
// ═══════════════════════════════════════════════

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
  'Normal':  EmotionConfig(icon: 'assets/svg/emotion_normal.svg',  label: 'Normal',  color: cText,   volume: '+0%',  rateBoost: 0,   speed: 55, pitch:  0),
  'Happy':   EmotionConfig(icon: 'assets/svg/emotion_happy.svg',   label: 'Happy',   color: cGreen,  volume: '+10%', rateBoost: 5,   speed: 65, pitch:  2),
  'Sad':     EmotionConfig(icon: 'assets/svg/emotion_sad.svg',     label: 'Sad',     color: cBlue,   volume: '-15%', rateBoost: -8,  speed: 38, pitch: -3),
  'Whisper': EmotionConfig(icon: 'assets/svg/emotion_whisper.svg', label: 'Whisper', color: cPurple, volume: '-60%', rateBoost: -10, speed: 35, pitch: -2),
  'Shout':   EmotionConfig(icon: 'assets/svg/emotion_shout.svg',   label: 'Shout',   color: cRed,    volume: '+30%', rateBoost: 10,  speed: 75, pitch:  3),
  'Excited': EmotionConfig(icon: 'assets/svg/emotion_excited.svg', label: 'Excited', color: cOrange, volume: '+20%', rateBoost: 15,  speed: 80, pitch:  4),
  'Calm':    EmotionConfig(icon: 'assets/svg/emotion_calm.svg',    label: 'Calm',    color: cTeal,   volume: '-10%', rateBoost: -12, speed: 40, pitch: -1),
  'Serious': EmotionConfig(icon: 'assets/svg/emotion_serious.svg', label: 'Serious', color: cIndigo, volume: '+0%',  rateBoost: -3,  speed: 55, pitch: -2),
};

// ═══════════════════════════════════════════════
//  CHARACTERS — language-aware
//  bestLangs: first lang = default/recommended
// ═══════════════════════════════════════════════

class CharConfig {
  final String icon, desc, emotion, gender;
  final String specialtyLabel;  // Short tag e.g. "🎙️ Narrator"
  final String specialtyDesc;   // Button hint e.g. "Best for: English, Hindi"
  final String defaultPreset;   // Auto-select preset
  final int speed, pitch;
  final List<String> allowedEmotions;
  final List<String> bestLangs;
  const CharConfig({
    required this.icon, required this.desc,
    required this.emotion, required this.gender,
    required this.speed, required this.pitch,
    required this.allowedEmotions,
    required this.bestLangs,
    this.specialtyLabel = '',
    this.specialtyDesc  = '',
    this.defaultPreset  = '',
  });
}

const Map<String, CharConfig> kCharacters = {
  // ── Original characters — kept exactly as before ──────────────────
  'Adam': CharConfig(
    icon: 'assets/svg/char_adam.svg', desc: 'Professional narrator', emotion: 'Normal',
    gender: 'Male', speed: 55, pitch: 0,
    allowedEmotions: ['Normal', 'Serious', 'Calm', 'Happy', 'Sad'],
    bestLangs: ['English', 'Hindi', 'Urdu', 'Arabic', 'French', 'German', 'Spanish'],
    specialtyLabel: 'Narrator',
    specialtyDesc:  'Best for: English, Hindi, Urdu • Preset: Narrator',
    defaultPreset:  'Narrator',
  ),
  'Luna': CharConfig(
    icon: 'assets/svg/char_luna.svg', desc: 'Warm & expressive', emotion: 'Happy',
    gender: 'Female', speed: 50, pitch: 2,
    allowedEmotions: ['Happy', 'Excited', 'Sad', 'Normal', 'Whisper'],
    bestLangs: ['English', 'French', 'Spanish', 'Italian', 'Portuguese', 'German'],
    specialtyLabel: 'Romance',
    specialtyDesc:  'Best for: French, Spanish, Italian • Preset: Story',
    defaultPreset:  'Story',
  ),
  'Nova': CharConfig(
    icon: 'assets/svg/char_nova.svg', desc: 'Futuristic AI voice', emotion: 'Serious',
    gender: 'Female', speed: 60, pitch: 5,
    allowedEmotions: ['Serious', 'Normal', 'Excited', 'Calm'],
    bestLangs: ['English', 'Chinese', 'Japanese', 'Korean', 'Indonesian', 'Malay', 'Vietnamese', 'Thai'],
    specialtyLabel: 'Asian AI',
    specialtyDesc:  'Best for: Chinese, Japanese, Korean • Preset: Newsreader',
    defaultPreset:  'Newsreader',
  ),
  'Zara': CharConfig(
    icon: 'assets/svg/char_zara.svg', desc: 'South Asian & Middle East', emotion: 'Serious',
    gender: 'Female', speed: 62, pitch: 0,
    allowedEmotions: ['Serious', 'Normal', 'Calm', 'Happy'],
    bestLangs: ['Urdu', 'Arabic', 'Hindi', 'Persian', 'Bengali', 'Punjabi'],
    specialtyLabel: 'South Asian',
    specialtyDesc:  'Best for: Urdu, Arabic, Hindi • Preset: Narrator',
    defaultPreset:  'Narrator',
  ),
  'Rex': CharConfig(
    icon: 'assets/svg/char_rex.svg', desc: 'Deep powerful voice', emotion: 'Serious',
    gender: 'Male', speed: 45, pitch: -5,
    allowedEmotions: ['Serious', 'Shout', 'Calm', 'Normal', 'Sad'],
    bestLangs: ['English', 'Russian', 'German', 'Polish', 'Czech', 'Ukrainian', 'Swedish', 'Norwegian', 'Danish', 'Finnish'],
    specialtyLabel: 'European',
    specialtyDesc:  'Best for: Russian, German, Polish • Preset: Audiobook',
    defaultPreset:  'Audiobook',
  ),
  'Aria': CharConfig(
    icon: 'assets/svg/char_aria.svg', desc: 'Indian languages specialist', emotion: 'Calm',
    gender: 'Female', speed: 42, pitch: 3,
    allowedEmotions: ['Calm', 'Whisper', 'Sad', 'Happy', 'Normal'],
    bestLangs: ['English', 'Tamil', 'Telugu', 'Marathi', 'Gujarati', 'Bengali', 'Hindi', 'Punjabi'],
    specialtyLabel: 'Indian',
    specialtyDesc:  'Best for: Tamil, Telugu, Marathi • Preset: Story',
    defaultPreset:  'Story',
  ),
  'Bolt': CharConfig(
    icon: 'assets/svg/char_bolt.svg', desc: 'Fast energetic voice', emotion: 'Excited',
    gender: 'Male', speed: 80, pitch: 2,
    allowedEmotions: ['Excited', 'Happy', 'Shout', 'Normal'],
    bestLangs: ['English', 'Spanish', 'Portuguese', 'Italian', 'French', 'Turkish'],
    specialtyLabel: 'Energetic',
    specialtyDesc:  'Best for: Spanish, Portuguese • Preset: Commercial',
    defaultPreset:  'Commercial',
  ),
  'Sage': CharConfig(
    icon: 'assets/svg/char_sage.svg', desc: 'Wise meditation voice', emotion: 'Calm',
    gender: 'Male', speed: 30, pitch: -3,
    allowedEmotions: ['Calm', 'Serious', 'Whisper', 'Sad', 'Normal'],
    bestLangs: ['English', 'Spanish', 'Portuguese', 'Italian', 'French', 'Romanian', 'Dutch', 'Turkish'],
    specialtyLabel: 'Meditation',
    specialtyDesc:  'Best for: English, Spanish • Preset: Meditation',
    defaultPreset:  'Meditation',
  ),
  // ── New characters ──────────────────────────────────────────────────
  'Kai': CharConfig(
    icon: 'assets/svg/char_kai.svg', desc: 'East Asian specialist', emotion: 'Normal',
    gender: 'Male', speed: 58, pitch: 0,
    allowedEmotions: ['Normal', 'Happy', 'Serious', 'Calm', 'Excited'],
    bestLangs: ['Chinese', 'Japanese', 'Korean', 'Indonesian', 'Malay', 'Vietnamese', 'Thai'],
    specialtyLabel: 'East Asian',
    specialtyDesc:  'Best for: Chinese, Japanese, Korean • Preset: Narrator',
    defaultPreset:  'Narrator',
  ),
  'Amara': CharConfig(
    icon: 'assets/svg/char_amara.svg', desc: 'African & Arabic specialist', emotion: 'Happy',
    gender: 'Female', speed: 52, pitch: 1,
    allowedEmotions: ['Happy', 'Normal', 'Calm', 'Excited', 'Sad'],
    bestLangs: ['Swahili', 'Afrikaans', 'Arabic', 'French', 'English'],
    specialtyLabel: 'African',
    specialtyDesc:  'Best for: Swahili, Afrikaans, Arabic • Preset: Story',
    defaultPreset:  'Story',
  ),

  // ── NEW HD & SPECIALIST CHARACTERS ─────────────────────────────────
  'Echo': CharConfig(
    icon: 'assets/svg/char_echo.svg',
    desc: 'HD Neural — auto emotion detection',
    emotion: 'Normal',
    gender: 'Male', speed: 55, pitch: 0,
    allowedEmotions: ['Normal', 'Happy', 'Sad', 'Excited', 'Calm', 'Serious', 'Whisper', 'Shout'],
    bestLangs: ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese'],
    specialtyLabel: 'HD Neural',
    specialtyDesc:  'Best for: All emotions • Preset: Narrator',
    defaultPreset:  'Narrator',
  ),
  'Lyra': CharConfig(
    icon: 'assets/svg/char_lyra.svg',
    desc: 'HD Neural — cinematic storyteller',
    emotion: 'Calm',
    gender: 'Female', speed: 48, pitch: 2,
    allowedEmotions: ['Calm', 'Whisper', 'Sad', 'Happy', 'Normal', 'Serious'],
    bestLangs: ['English', 'French', 'Italian', 'Spanish', 'Portuguese', 'Romanian'],
    specialtyLabel: 'Cinematic',
    specialtyDesc:  'Best for: French, Italian, Spanish • Preset: Audiobook',
    defaultPreset:  'Audiobook',
  ),
  'Titan': CharConfig(
    icon: 'assets/svg/char_titan.svg',
    desc: 'Deep broadcast — news & documentaries',
    emotion: 'Serious',
    gender: 'Male', speed: 50, pitch: -4,
    allowedEmotions: ['Serious', 'Calm', 'Normal', 'Shout'],
    bestLangs: ['English', 'Russian', 'German', 'Polish', 'Ukrainian', 'Czech'],
    specialtyLabel: 'Broadcast',
    specialtyDesc:  'Best for: English, Russian, German • Preset: Newsreader',
    defaultPreset:  'Newsreader',
  ),
  'Mira': CharConfig(
    icon: 'assets/svg/char_mira.svg',
    desc: 'Soft ASMR & meditation specialist',
    emotion: 'Whisper',
    gender: 'Female', speed: 28, pitch: 3,
    allowedEmotions: ['Whisper', 'Calm', 'Sad', 'Normal'],
    bestLangs: ['English', 'Japanese', 'Korean', 'Chinese', 'Thai', 'Vietnamese'],
    specialtyLabel: 'ASMR',
    specialtyDesc:  'Best for: Japanese, Korean, Thai • Preset: Meditation',
    defaultPreset:  'Meditation',
  ),
  'Vox': CharConfig(
    icon: 'assets/svg/char_vox.svg',
    desc: 'Ultra-fast commercial & ads voice',
    emotion: 'Excited',
    gender: 'Male', speed: 85, pitch: 1,
    allowedEmotions: ['Excited', 'Happy', 'Shout', 'Normal'],
    bestLangs: ['English', 'Spanish', 'Portuguese', 'Turkish', 'Indonesian', 'Malay'],
    specialtyLabel: 'Ads & Promo',
    specialtyDesc:  'Best for: English, Spanish • Preset: Commercial',
    defaultPreset:  'Commercial',
  ),
  'Zephyr': CharConfig(
    icon: 'assets/svg/char_zephyr.svg',
    desc: 'SSML expert — karaoke & subtitles',
    emotion: 'Normal',
    gender: 'Male', speed: 52, pitch: 0,
    allowedEmotions: ['Normal', 'Happy', 'Serious', 'Calm', 'Excited', 'Sad'],
    bestLangs: ['English', 'Hindi', 'Bengali', 'Tamil', 'Telugu', 'Marathi', 'Gujarati', 'Punjabi'],
    specialtyLabel: 'Karaoke',
    specialtyDesc:  'Best for: Indian Languages • SSML ready',
    defaultPreset:  'Narrator',
  ),
  'Noor': CharConfig(
    icon: 'assets/svg/char_noor.svg',
    desc: 'Islamic & Arabic recitation voice',
    emotion: 'Calm',
    gender: 'Female', speed: 40, pitch: 1,
    allowedEmotions: ['Calm', 'Serious', 'Normal', 'Whisper', 'Sad'],
    bestLangs: ['Arabic', 'Urdu', 'Persian', 'Hindi'],
    specialtyLabel: 'Recitation',
    specialtyDesc:  'Best for: Arabic, Urdu, Persian • Preset: Meditation',
    defaultPreset:  'Meditation',
  ),
  'Spark': CharConfig(
    icon: 'assets/svg/char_spark.svg',
    desc: 'Kids & education — fun & friendly',
    emotion: 'Happy',
    gender: 'Female', speed: 45, pitch: 4,
    allowedEmotions: ['Happy', 'Excited', 'Normal', 'Calm'],
    bestLangs: ['English', 'Hindi', 'Urdu', 'Arabic', 'Spanish', 'French', 'Turkish'],
    specialtyLabel: 'Kids',
    specialtyDesc:  'Best for: All languages • Preset: Kids',
    defaultPreset:  'Kids',
  ),
  'Atlas': CharConfig(
    icon: 'assets/svg/char_atlas.svg',
    desc: 'Multilingual world traveler voice',
    emotion: 'Normal',
    gender: 'Male', speed: 56, pitch: 0,
    allowedEmotions: ['Normal', 'Happy', 'Serious', 'Excited', 'Calm'],
    bestLangs: ['English', 'Chinese', 'Japanese', 'Korean', 'Thai', 'Vietnamese', 'Indonesian', 'Malay', 'Swahili', 'Afrikaans'],
    specialtyLabel: 'World Voice',
    specialtyDesc:  'Best for: 10+ Asian & African langs • Preset: Narrator',
    defaultPreset:  'Narrator',
  ),
  'Seraph': CharConfig(
    icon: 'assets/svg/char_seraph.svg',
    desc: 'Dramatic poetry & audiobooks',
    emotion: 'Serious',
    gender: 'Female', speed: 38, pitch: 1,
    allowedEmotions: ['Serious', 'Sad', 'Whisper', 'Calm', 'Normal', 'Happy'],
    bestLangs: ['English', 'French', 'Italian', 'Spanish', 'German', 'Russian', 'Greek', 'Hebrew'],
    specialtyLabel: 'Poetry',
    specialtyDesc:  'Best for: French, Italian, Greek • Preset: Poet',
    defaultPreset:  'Poet',
  ),
};

// ── Helper: get characters best suited for a language ────────
List<String> getCharactersForLang(String langName) =>
    kCharacters.entries
        .where((e) => e.value.bestLangs.contains(langName))
        .map((e) => e.key)
        .toList();

// ═══════════════════════════════════════════════
//  PRESETS — unchanged
// ═══════════════════════════════════════════════

class PresetConfig {
  final String icon, emotion, desc;
  final int speed, pitch;
  const PresetConfig({
    required this.icon, required this.emotion,
    required this.desc, required this.speed, required this.pitch,
  });
}

const Map<String, PresetConfig> kPresets = {
  'Narrator':   PresetConfig(icon: 'assets/svg/preset_narrator.svg',   speed: 50, pitch: 0,  emotion: 'Calm',    desc: 'Clear storytelling'),
  'Newsreader': PresetConfig(icon: 'assets/svg/preset_newsreader.svg', speed: 60, pitch: 0,  emotion: 'Serious', desc: 'Professional news'),
  'Story':      PresetConfig(icon: 'assets/svg/preset_story.svg',      speed: 45, pitch: 2,  emotion: 'Happy',   desc: 'Engaging story'),
  'Meditation': PresetConfig(icon: 'assets/svg/preset_meditation.svg', speed: 30, pitch: -2, emotion: 'Calm',    desc: 'Peaceful & slow'),
  'Commercial': PresetConfig(icon: 'assets/svg/preset_commercial.svg', speed: 65, pitch: 2,  emotion: 'Excited', desc: 'Upbeat & catchy'),
  'Audiobook':  PresetConfig(icon: 'assets/svg/preset_audiobook.svg',  speed: 55, pitch: 0,  emotion: 'Normal',  desc: 'Long-form audio'),
  'Poet':       PresetConfig(icon: 'assets/svg/preset_poet.svg',       speed: 40, pitch: 1,  emotion: 'Sad',     desc: 'Dramatic poetry'),
  'Kids':       PresetConfig(icon: 'assets/svg/preset_kids.svg',       speed: 45, pitch: 3,  emotion: 'Happy',   desc: 'Fun & friendly'),
};

// ═══════════════════════════════════════════════
//  VOICE PARAM HELPERS — unchanged
// ═══════════════════════════════════════════════

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
