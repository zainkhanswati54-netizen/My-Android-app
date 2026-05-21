import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import '../utils/constants.dart';

// ═══════════════════════════════════════════════
//  TTS SERVICE v1.0
//  Backend: Azure Edge TTS only (XTTS removed)
//  New API param: lang=en instead of voice=en-US-GuyNeural
//  Character tells backend which voice to pick per language
// ═══════════════════════════════════════════════

class TtsService {
  static const String _apiBase =
      'https://zainkhanswati54-titan-tts-api.hf.space/tts';

  static Future<TtsResult> generate({
    required String text,
    required String language,   // kLanguages key, e.g. "English", "Spanish"
    required String gender,     // "Male" or "Female"
    required int speedPct,
    required int pitchVal,
    required String emotion,
    String character = '',
    String preset = '',
    bool useBreaths = false,
    bool adaptivePacing = false,
    bool ssmlMode = false,
    bool lowLatency = false,
    bool hdVoice = false,
    bool autoEmotion = false,
    bool wordBoundary = false,
  }) async {
    try {
      final langConfig = kLanguages[language];
      if (langConfig == null) return TtsResult.error('Invalid language: $language');

      // ── Language code for API ──
      final langCode = langConfig.code; // e.g. "en", "es", "ur"

      // ── Gender from character (character always wins) ──
      String finalGender = gender;
      if (character.isNotEmpty && kCharacters.containsKey(character)) {
        finalGender = kCharacters[character]!.gender; // "Male" or "Female"
      }

      // ── Rate calculation ──
      int rate = _speedToRate(speedPct, emotion);
      if (adaptivePacing && text.length > 300) {
        rate = _speedToRate((speedPct - 8).clamp(10, 100), emotion);
      }

      // ── SSML preprocessing ──
      String processedText = text.trim();
      if (ssmlMode && !processedText.contains('<speak>')) {
        processedText = '<speak>$processedText</speak>';
      }

      // ── Urdu/Arabic normalization (zero-width chars) ──
      if (langConfig.isRtl) {
        processedText = _normalizeRtl(processedText);
      }

      return await _callApi(
        text:         processedText,
        langCode:     langCode,
        gender:       finalGender.toLowerCase(),
        emotion:      emotion,
        rate:         rate,
        character:    effectiveChar,
        preset:       preset,
        ssmlMode:     ssmlMode,
        lowLatency:   lowLatency,
        hdVoice:      hdVoice,
        autoEmotion:  autoEmotion,
        wordBoundary: wordBoundary,
      );
    } catch (e) {
      return TtsResult.error('Generation failed: $e');
    }
  }

  // ── RTL text normalization (Urdu, Arabic, Persian, Hebrew) ────────
  static String _normalizeRtl(String text) {
    return text
        .replaceAll('\u200C', '') // Zero-width non-joiner
        .replaceAll('\u200D', '') // Zero-width joiner
        .replaceAll('\uFEFF', '') // BOM
        .trim();
  }

  static Future<TtsResult> _callApi({
    required String text,
    required String langCode,
    required String gender,
    required String emotion,
    required int rate,
    String character = '',
    String preset = '',
    bool ssmlMode = false,
    bool lowLatency = false,
    bool hdVoice = false,
    bool autoEmotion = false,
    bool wordBoundary = false,
  }) async {
    try {
      final hasNet = await _checkInternet();
      if (!hasNet) {
        return TtsResult.error(
            'No internet connection.\nPlease turn on WiFi or mobile data.');
      }

      final params = <String, String>{
        'text':    text,
        'lang':    langCode,         // NEW: lang code instead of voice name
        'gender':  gender,           // NEW: explicit gender
        'emotion': emotion,
        'rate':    rate.toString(),
        if (character.isNotEmpty) 'character': character,
        if (preset.isNotEmpty)    'preset':    preset,
        if (ssmlMode)             'ssml_mode':     'true',
        if (lowLatency)           'low_latency':   'true',
        if (hdVoice)              'hd_voice':      'true',
        if (autoEmotion)          'auto_emotion':  'true',
        if (wordBoundary)         'word_boundary': 'true',
      };

      final uri = Uri.parse(_apiBase).replace(queryParameters: params);

      final timeout = lowLatency
          ? const Duration(seconds: 60)
          : text.length > 200
              ? const Duration(seconds: 180)
              : const Duration(seconds: 90);

      final response = await http.get(uri).timeout(timeout);

      if (response.statusCode == 200 && response.bodyBytes.length > 500) {
        final file = await _saveTemp(response.bodyBytes, '.wav');
        return TtsResult.success(file);
      } else if (response.statusCode == 503) {
        return TtsResult.error(
            'Server warming up.\nPlease wait a moment and try again.');
      } else {
        return TtsResult.error('API error: ${response.statusCode}');
      }
    } catch (e) {
      final msg = e.toString();
      if (msg.contains('TimeoutException')) {
        return TtsResult.error(
            'Server is taking longer than expected.\nPlease try again.');
      }
      return TtsResult.error('Connection failed: $e');
    }
  }

  static int _speedToRate(int speedPct, String emotion) {
    int base  = ((speedPct - 50) * 1.5).round();
    int boost = kEmotions[emotion]?.rateBoost ?? 0;
    return (base + boost).clamp(-50, 100);
  }

  static Future<File> _saveTemp(Uint8List bytes, String ext) async {
    final dir = await getTemporaryDirectory();
    final f = File(
        '${dir.path}/titan_${DateTime.now().millisecondsSinceEpoch}$ext');
    await f.writeAsBytes(bytes);
    return f;
  }

  // ── Save to Downloads folder ─────────────────────────────────────
  static Future<File> savePermanent(File temp, String filename) async {
    if (!await temp.exists()) {
      throw Exception('Source audio file not found');
    }
    final srcSize = await temp.length();
    if (srcSize < 500) {
      throw Exception('Audio too small ($srcSize bytes) — try generating again');
    }

    String finalName = filename;
    if (!finalName.endsWith('.wav') && !finalName.endsWith('.mp3')) {
      finalName = '$filename.wav';
    }

    File? dest;

    if (Platform.isAndroid) {
      try {
        final primaryDir =
            Directory('/storage/emulated/0/Download/TitanStudioPRO');
        await primaryDir.create(recursive: true);
        dest = File('${primaryDir.path}/$finalName');
        final bytes = await temp.readAsBytes();
        await dest.writeAsBytes(bytes, flush: true);
      } catch (_) {
        dest = null;
      }
    }

    if (dest == null ||
        !(await dest.exists()) ||
        (await dest.length()) < 500) {
      final fallbackDir = Directory(
          '${(await getApplicationDocumentsDirectory()).path}/TitanStudioPRO');
      await fallbackDir.create(recursive: true);
      dest = File('${fallbackDir.path}/$finalName');
      final bytes = await temp.readAsBytes();
      await dest.writeAsBytes(bytes, flush: true);
    }

    final destSize = await dest.length();
    if (destSize < 500) {
      throw Exception('Save failed — file empty ($destSize bytes)');
    }
    return dest;
  }

  static Future<String> getAudioFolder() async {
    if (Platform.isAndroid) {
      final dir =
          Directory('/storage/emulated/0/Download/TitanStudioPRO');
      await dir.create(recursive: true);
      return dir.path;
    }
    final dir = Directory(
        '${(await getApplicationDocumentsDirectory()).path}/TitanStudioPRO/Audio');
    await dir.create(recursive: true);
    return dir.path;
  }

  static Future<bool> _checkInternet() async {
    try {
      final r = await InternetAddress.lookup('huggingface.co')
          .timeout(const Duration(seconds: 5));
      return r.isNotEmpty && r.first.rawAddress.isNotEmpty;
    } catch (_) {
      return false;
    }
  }
}

class TtsResult {
  final bool ok;
  final File? file;
  final String? error;
  const TtsResult._({required this.ok, this.file, this.error});
  factory TtsResult.success(File f) => TtsResult._(ok: true, file: f);
  factory TtsResult.error(String msg) => TtsResult._(ok: false, error: msg);
}
