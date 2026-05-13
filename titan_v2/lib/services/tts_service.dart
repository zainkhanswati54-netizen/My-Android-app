import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import '../utils/constants.dart';

class TtsService {
  static const int _maxRetries = 3;

  static Future<TtsResult> generate({
    required String text,
    required String language,
    required String gender,
    required int speedPct,
    required int pitchVal,
    required String emotion,
    bool useBreaths = false,
    bool adaptivePacing = false,
  }) async {
    try {
      final langConfig = kLanguages[language];
      if (langConfig == null) return TtsResult.error('Invalid language');

      final voice = gender == 'Male' ? langConfig.maleVoice : langConfig.femaleVoice;
      String rate = speedToRate(speedPct, emotion);
      String pitch = pitchToHz(pitchVal);
      String volume = emotionVolume(emotion);

      String processedText = text;
      if (useBreaths) {
        processedText = processedText.replaceAllMapped(
          RegExp(r'([.!?])\s+'), (m) => '${m[1]}  ');
      }
      if (adaptivePacing && text.length > 500) {
        rate = speedToRate((speedPct - 5).clamp(10, 100), emotion);
      }

      return await _callEdgeTts(
        text: processedText,
        voice: voice,
        rate: rate,
        pitch: pitch,
        volume: volume,
      );
    } catch (e) {
      return TtsResult.error('Generation failed: $e');
    }
  }

  static Future<TtsResult> _callEdgeTts({
    required String text,
    required String voice,
    required String rate,
    required String pitch,
    required String volume,
  }) async {
    Exception? lastError;

    for (int attempt = 0; attempt < _maxRetries; attempt++) {
      try {
        // Check internet first
        final hasNet = await _checkInternet();
        if (!hasNet) {
          return TtsResult.error(
              'No internet connection.\nPlease turn on WiFi or mobile data.');
        }

        // Try Google Translate TTS (free, no auth)
        final bytes = await _fetchGoogleTts(text: text, voice: voice);
        if (bytes != null && bytes.isNotEmpty) {
          final file = await _saveTemp(bytes);
          return TtsResult.success(file);
        }
      } catch (e) {
        lastError = e as Exception?;
        if (attempt < _maxRetries - 1) {
          await Future.delayed(Duration(seconds: attempt + 1));
        }
      }
    }
    return TtsResult.error(
        'Could not generate audio.\n${lastError?.toString() ?? "Unknown error"}\nCheck internet connection.');
  }

  // Google Translate TTS — free, no API key needed
  static Future<Uint8List?> _fetchGoogleTts({
    required String text,
    required String voice,
  }) async {
    // Extract language code from voice name (e.g. "en-US-GuyNeural" → "en")
    final langCode = voice.split('-').take(2).join('-').toLowerCase();

    // Split long text into chunks (Google TTS limit ~200 chars)
    final chunks = _splitText(text, 200);
    final List<Uint8List> parts = [];

    for (final chunk in chunks) {
      final encoded = Uri.encodeComponent(chunk);
      final uri = Uri.parse(
        'https://translate.google.com/translate_tts'
        '?ie=UTF-8&q=$encoded&tl=$langCode&client=tw-ob',
      );

      try {
        final response = await http.get(uri, headers: {
          'User-Agent':
              'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/91.0',
          'Referer': 'https://translate.google.com/',
          'Accept': 'audio/mpeg, audio/*; q=0.9, */*; q=0.8',
        }).timeout(const Duration(seconds: 20));

        if (response.statusCode == 200 && response.bodyBytes.isNotEmpty) {
          parts.add(response.bodyBytes);
        }
      } catch (_) {
        continue;
      }
    }

    if (parts.isEmpty) return null;

    // Concatenate all MP3 parts
    final totalLength = parts.fold<int>(0, (sum, b) => sum + b.length);
    final result = Uint8List(totalLength);
    int offset = 0;
    for (final part in parts) {
      result.setRange(offset, offset + part.length, part);
      offset += part.length;
    }
    return result;
  }

  // Split text into chunks at word boundaries
  static List<String> _splitText(String text, int maxLen) {
    if (text.length <= maxLen) return [text];
    final chunks = <String>[];
    final words = text.split(' ');
    var current = '';
    for (final word in words) {
      if ((current + ' ' + word).trim().length > maxLen) {
        if (current.isNotEmpty) chunks.add(current.trim());
        current = word;
      } else {
        current = (current + ' ' + word).trim();
      }
    }
    if (current.isNotEmpty) chunks.add(current.trim());
    return chunks;
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
      final r = await InternetAddress.lookup('translate.google.com')
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
