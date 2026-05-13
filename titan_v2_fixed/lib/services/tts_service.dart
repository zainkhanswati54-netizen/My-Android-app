import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import '../utils/constants.dart';

// ═══════════════════════════════════════════════
//  TTS SERVICE — Microsoft Neural Voices
//  via Titan TTS API (Hugging Face Space)
// ═══════════════════════════════════════════════

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
    bool useBreaths = false,
    bool adaptivePacing = false,
    bool ssmlMode = false,
    bool lowLatency = false,
  }) async {
    try {
      final langConfig = kLanguages[language];
      if (langConfig == null) return TtsResult.error('Invalid language');

      // voice key: "en-Male", "hi-Female" etc.
      final langCode = langConfig.code; // en, hi, ur
      final voiceKey = '$langCode-$gender';

      int rate = speedToRateInt(speedPct, emotion);
      int pitch = pitchVal * 15;
      int volume = emotionVolumeInt(emotion);

      if (adaptivePacing && text.length > 500) {
        rate = speedToRateInt((speedPct - 5).clamp(10, 100), emotion);
      }

      return await _callApi(
        text: text,
        voiceKey: voiceKey,
        rate: rate,
        pitch: pitch,
        volume: volume,
      );
    } catch (e) {
      return TtsResult.error('Generation failed: $e');
    }
  }

  static Future<TtsResult> _callApi({
    required String text,
    required String voiceKey,
    required int rate,
    required int pitch,
    required int volume,
  }) async {
    try {
      final hasNet = await _checkInternet();
      if (!hasNet) {
        return TtsResult.error(
            'No internet connection.\nPlease turn on WiFi or mobile data.');
      }

      final uri = Uri.parse(_apiBase).replace(queryParameters: {
        'text': text,
        'voice': voiceKey,
        'rate': rate.toString(),
        'pitch': pitch.toString(),
        'volume': volume.toString(),
      });

      final response = await http.get(uri).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200 && response.bodyBytes.length > 500) {
        final file = await _saveTemp(response.bodyBytes);
        return TtsResult.success(file);
      } else {
        return TtsResult.error('API error: ${response.statusCode}');
      }
    } catch (e) {
      return TtsResult.error('Connection failed: $e');
    }
  }

  // ── Helpers ──────────────────────────────────
  static int speedToRateInt(int speedPct, String emotion) {
    int base = ((speedPct - 50) * 1.5).round();
    int boost = kEmotions[emotion]?.rateBoost ?? 0;
    return (base + boost).clamp(-50, 100);
  }

  static int emotionVolumeInt(String emotion) {
    final vol = kEmotions[emotion]?.volume ?? '+0%';
    return int.tryParse(vol.replaceAll('%', '').replaceAll('+', '')) ?? 0;
  }

  static Future<File> _saveTemp(Uint8List bytes) async {
    final dir = await getTemporaryDirectory();
    final f = File(
        '${dir.path}/titan_${DateTime.now().millisecondsSinceEpoch}.mp3');
    await f.writeAsBytes(bytes);
    return f;
  }

  static Future<File> savePermanent(File temp, String filename) async {
    final dir = await getApplicationDocumentsDirectory();
    final audioDir = Directory('${dir.path}/TitanStudioPRO/Audio');
    await audioDir.create(recursive: true);
    final dest = File('${audioDir.path}/$filename');
    await temp.copy(dest.path);
    return dest;
  }

  static Future<String> getAudioFolder() async {
    final dir = await getApplicationDocumentsDirectory();
    final audioDir = Directory('${dir.path}/TitanStudioPRO/Audio');
    await audioDir.create(recursive: true);
    return audioDir.path;
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
