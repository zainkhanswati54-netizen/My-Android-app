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
      // Server-side SSML parser will handle the tags correctly.
      // XTTS tags ko strip karta hai lekin hints use karta hai.
      String processedText = text;
      if (ssmlMode && !processedText.contains('<speak>')) {
        processedText = '<speak>$processedText</speak>';
      }

      // ── Urdu → normalize for XTTS pronunciation ──
      if (language == 'Urdu') {
        processedText = _urduToArabicPronunciation(processedText);
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
        // ── FIX: Teen features ab server ko properly bhej rahe hain ──
        useBreaths: useBreaths,
        ssmlMode: ssmlMode,
        lowLatency: lowLatency,
      );
    } catch (e) {
      return TtsResult.error('Generation failed: $e');
    }
  }

  // ── Urdu text preprocessing for XTTS ──────────
  static String _urduToArabicPronunciation(String text) {
    return text
        .replaceAll('ک', 'ك')
        .replaceAll('ی', 'ي')
        .replaceAll('ے', 'ي')
        .replaceAll('ہ', 'ه')
        .replaceAll('ں', 'ن')
        .replaceAll('ؤ', 'و')
        .replaceAll('ئ', 'ي')
        .replaceAll('آ', 'ا')
        .replaceAll('ۃ', 'ة')
        .replaceAll('\u06CC', '\u064A') // Farsi Yeh → Arabic Yeh
        .replaceAll('\u06A9', '\u0643') // Keheh → Kaf
        .replaceAll('\u06BE', '\u0647'); // Heh Doachashmee → Heh
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
    // ── FIX: Teen naye parameters ──
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
        // ── FIX 1: Dynamic Breath Simulation → server ko bhejo ──
        if (useBreaths)  'use_breaths': 'true',
        // ── FIX 2: SSML Mode → server ko bhejo ──
        if (ssmlMode)    'ssml_mode':   'true',
        // ── FIX 3: Ultra-Low Latency → server ko bhejo ──
        if (lowLatency)  'low_latency': 'true',
      };

      final uri = Uri.parse(_apiBase).replace(queryParameters: params);

      // Low latency 60s, normal text 180s, long text (>200 chars) 360s
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
    Directory? saveDir;

    if (Platform.isAndroid) {
      saveDir = Directory('/storage/emulated/0/Download/TitanStudioPRO');
    }

    saveDir ??= Directory(
        '${(await getApplicationDocumentsDirectory()).path}/TitanStudioPRO/Audio');

    await saveDir.create(recursive: true);

    // ── FIX: ensure .wav extension on saved file ──
    String finalName = filename;
    if (!finalName.endsWith('.wav') && !finalName.endsWith('.mp3')) {
      finalName = '$filename.wav';
    }

    final dest = File('${saveDir.path}/$finalName');
    await temp.copy(dest.path);
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
