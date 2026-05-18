import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import '../utils/constants.dart';

class TtsService {
  static const String _apiBase =
      'https://zainkhanswati54-titan-tts-api.hf.space/tts';

  static Future<TtsResult> generate({
    required String text,
    required String language,
    required String gender,
    required int speedPct,
    required int pitchVal,
    required String emotion,
    String character = '',
    String preset = '',
    bool useBreaths = false,
    bool adaptivePacing = false,
    bool ssmlMode = false,
    bool lowLatency = false,
  }) async {
    try {
      final langConfig = kLanguages[language];
      if (langConfig == null) return TtsResult.error('Invalid language');

      // ── Voice key from language config ──
      final voiceKey = gender == 'Male'
          ? langConfig.maleVoice
          : langConfig.femaleVoice;

      // ── Character overrides gender/voice ──
      String finalCharacter = character;
      String finalVoice = voiceKey;
      if (character.isNotEmpty) {
        final charCfg = kCharacters[character];
        if (charCfg != null) {
          final charLangCfg = kLanguages[language]!;
          finalVoice = charCfg.gender == 'Male'
              ? charLangCfg.maleVoice
              : charLangCfg.femaleVoice;
        }
      }

      // ── Preset applies on top, does not clear character ──
      if (preset.isNotEmpty && character.isEmpty) {
        finalCharacter = '';
      }

      int rate  = _speedToRate(speedPct, emotion);
      // ── pitch: app -10 to +10, server bhi same range accept karta hai ──
      int pitch = pitchVal.clamp(-10, 10);
      int volume = _emotionVolume(emotion);

      // ── Adaptive pacing for long text ──
      if (adaptivePacing && text.length > 300) {
        rate = _speedToRate((speedPct - 8).clamp(10, 100), emotion);
      }

      // ── FIX: SSML Mode — wrap text in <speak> tag ──
      String processedText = text;
      if (ssmlMode && !processedText.contains('<speak>')) {
        processedText = '<speak>$processedText</speak>';
      }

      // ── FIX: Urdu preprocessing — sirf zaroori normalization, Arabic conversion NAHI ──
      // XTTS Urdu/Hindi voice ko Nastaliq script as-is behtar samajhti hai
      if (language == 'Urdu') {
        processedText = _normalizeUrdu(processedText);
      }

      return await _callApi(
        text: processedText,
        voiceKey: finalVoice,
        emotion: emotion,
        rate: rate,
        pitch: pitch,
        volume: volume,
        character: finalCharacter,
        preset: preset,
        useBreaths: useBreaths,
        ssmlMode: ssmlMode,
        lowLatency: lowLatency,
      );
    } catch (e) {
      return TtsResult.error('Generation failed: $e');
    }
  }

  // ── FIX: Urdu normalization — Arabic conversion HATAI GAYI ──────────
  // Pehle Arabic characters mein convert karte the (غalat) —
  // XTTS Hindi/Urdu voice Urdu Nastaliq directly samajhti hai.
  // Sirf woh replacements jo genuinely pronunciation improve karte hain:
  static String _normalizeUrdu(String text) {
    return text
        .replaceAll('ں', 'ن')     // Noon ghunna → Noon (XTTS handle karta)
        .replaceAll('ۃ', 'ت')     // Teh marbuta → Teh
        .replaceAll('\u200C', '') // Zero-width non-joiner hatao
        .replaceAll('\u200D', '') // Zero-width joiner hatao
        .trim();
  }

  static Future<TtsResult> _callApi({
    required String text,
    required String voiceKey,
    required String emotion,
    required int rate,
    required int pitch,
    required int volume,
    String character = '',
    String preset = '',
    bool useBreaths = false,
    bool ssmlMode = false,
    bool lowLatency = false,
  }) async {
    try {
      final hasNet = await _checkInternet();
      if (!hasNet) {
        return TtsResult.error(
            'No internet connection.\nPlease turn on WiFi or mobile data.');
      }

      final params = {
        'text':    text,
        'voice':   voiceKey,
        'emotion': emotion,
        'rate':    rate.toString(),
        'pitch':   pitch.toString(),
        'volume':  volume.toString(),
        if (character.isNotEmpty) 'character': character,
        if (preset.isNotEmpty)    'preset':    preset,
        if (useBreaths)  'use_breaths': 'true',
        if (ssmlMode)    'ssml_mode':   'true',
        if (lowLatency)  'low_latency': 'true',
      };

      final uri = Uri.parse(_apiBase).replace(queryParameters: params);

      final timeout = lowLatency
          ? const Duration(seconds: 60)
          : text.length > 200
              ? const Duration(seconds: 360)
              : const Duration(seconds: 180);

      final response = await http.get(uri).timeout(timeout);

      if (response.statusCode == 200 && response.bodyBytes.length > 500) {
        final file = await _saveTemp(response.bodyBytes, '.wav');
        return TtsResult.success(file);
      } else if (response.statusCode == 503) {
        return TtsResult.error(
            'Server warming up.\nPlease wait 30 seconds and try again.');
      } else {
        return TtsResult.error('API error: ${response.statusCode}');
      }
    } catch (e) {
      final msg = e.toString();
      if (msg.contains('TimeoutException')) {
        return TtsResult.error(
            'Server is processing your request.\nPlease try again — long text takes more time.');
      }
      return TtsResult.error('Connection failed: $e');
    }
  }

  static int _speedToRate(int speedPct, String emotion) {
    int base  = ((speedPct - 50) * 1.5).round();
    int boost = kEmotions[emotion]?.rateBoost ?? 0;
    return (base + boost).clamp(-50, 100);
  }

  static int _emotionVolume(String emotion) {
    final vol = kEmotions[emotion]?.volume ?? '+0%';
    return int.tryParse(
            vol.replaceAll('%', '').replaceAll('+', '')) ??
        0;
  }

  static Future<File> _saveTemp(Uint8List bytes, String ext) async {
    final dir = await getTemporaryDirectory();
    final f = File(
        '${dir.path}/titan_${DateTime.now().millisecondsSinceEpoch}$ext');
    await f.writeAsBytes(bytes);
    return f;
  }

  // ── Save to Downloads folder (visible in file manager) ──
  static Future<File> savePermanent(File temp, String filename) async {
    // 1. Source file check
    if (!await temp.exists()) {
      throw Exception('Source audio file not found');
    }
    final srcSize = await temp.length();
    if (srcSize < 500) {
      throw Exception('Audio too small ($srcSize bytes) — try generating again');
    }

    // 2. Filename
    String finalName = filename;
    if (!finalName.endsWith('.wav') && !finalName.endsWith('.mp3')) {
      finalName = '$filename.wav';
    }

    // 3. Try saving — primary path, then fallback
    File? dest;

    if (Platform.isAndroid) {
      // Primary: /storage/emulated/0/Download/TitanStudioPRO
      try {
        final primaryDir = Directory('/storage/emulated/0/Download/TitanStudioPRO');
        await primaryDir.create(recursive: true);
        dest = File('${primaryDir.path}/$finalName');
        final bytes = await temp.readAsBytes();
        await dest.writeAsBytes(bytes, flush: true);
      } catch (_) {
        dest = null; // fallback try karo
      }
    }

    // Fallback: app documents directory (always writable, no permission needed)
    if (dest == null || !(await dest.exists()) || (await dest.length()) < 500) {
      final fallbackDir = Directory(
          '${(await getApplicationDocumentsDirectory()).path}/TitanStudioPRO');
      await fallbackDir.create(recursive: true);
      dest = File('${fallbackDir.path}/$finalName');
      final bytes = await temp.readAsBytes();
      await dest.writeAsBytes(bytes, flush: true);
    }

    // 4. Final verify
    final destSize = await dest.length();
    if (destSize < 500) {
      throw Exception('Save failed — file empty ($destSize bytes)');
    }
    return dest;
  }
    final srcSize = await temp.length();
    if (srcSize < 500) {
      throw Exception('Audio too small (\$srcSize bytes)');
    }

    // 2. Destination folder
    Directory? saveDir;
    if (Platform.isAndroid) {
      saveDir = Directory('/storage/emulated/0/Download/TitanStudioPRO');
    }
    saveDir ??= Directory(
        '${(await getApplicationDocumentsDirectory()).path}/TitanStudioPRO/Audio');
    await saveDir.create(recursive: true);

    // 3. Filename
    String finalName = filename;
    if (!finalName.endsWith('.wav') && !finalName.endsWith('.mp3')) {
      finalName = '\$filename.wav';
    }

    // 4. Read bytes and write (more reliable than copy)
    final dest = File('\${saveDir.path}/\$finalName');
    final bytes = await temp.readAsBytes();
    await dest.writeAsBytes(bytes, flush: true);

    // 5. Verify
    final destSize = await dest.length();
    if (destSize < 500) {
      throw Exception('Save failed — file empty (\$destSize bytes)');
    }
    return dest;
  }

  static Future<String> getAudioFolder() async {
    if (Platform.isAndroid) {
      final dir = Directory('/storage/emulated/0/Download/TitanStudioPRO');
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
