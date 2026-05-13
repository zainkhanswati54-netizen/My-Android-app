import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import '../utils/constants.dart';

// ═══════════════════════════════════════════════
//  TTS SERVICE — Edge TTS Neural Voices
//  Microsoft Neural voices - much more natural!
//  3-tier fallback: EdgeTTS → MS Cognitive → Google
// ═══════════════════════════════════════════════

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
    bool ssmlMode = false,
    bool lowLatency = false,
  }) async {
    try {
      final langConfig = kLanguages[language];
      if (langConfig == null) return TtsResult.error('Invalid language: $language');

      final voice  = gender == 'Male' ? langConfig.maleVoice : langConfig.femaleVoice;
      String rate  = speedToRate(speedPct, emotion);
      String pitch = pitchToHz(pitchVal);
      String volume = emotionVolume(emotion);

      // Apply adaptive pacing for long text
      if (adaptivePacing && text.length > 500) {
        rate = speedToRate((speedPct - 5).clamp(10, 100), emotion);
      }

      // Add breath simulation (SSML break tags)
      String processedText = text;
      if (useBreaths) {
        processedText = processedText.replaceAllMapped(
          RegExp(r'([.!?।۔])\s+'),
          (m) => '${m[1]} <break time="350ms"/> ',
        );
      }

      return await _callEdgeTts(
        text: processedText,
        voice: voice,
        rate: rate,
        pitch: pitch,
        volume: volume,
        ssmlMode: ssmlMode || useBreaths,
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
    bool ssmlMode = false,
  }) async {
    Exception? lastError;

    for (int attempt = 0; attempt < _maxRetries; attempt++) {
      try {
        final hasNet = await _checkInternet();
        if (!hasNet) {
          return TtsResult.error(
              'No internet connection.\nPlease turn on WiFi or mobile data.');
        }

        // Build SSML for neural voice
        final ssml = _buildSsml(
          text: text, voice: voice,
          rate: rate, pitch: pitch, volume: volume,
          rawSsml: ssmlMode,
        );

        // Tier 1: edge-tts public API (Microsoft Neural)
        Uint8List? bytes = await _fetchEdgeTtsPublicApi(ssml: ssml, voice: voice);

        // Tier 2: Azure TTS demo endpoint
        if (bytes == null || bytes.isEmpty) {
          bytes = await _fetchAzureDemoTts(text: text, voice: voice, rate: rate, pitch: pitch, volume: volume);
        }

        // Tier 3: Google TTS fallback (lower quality but works)
        if (bytes == null || bytes.isEmpty) {
          final langCode = voice.substring(0, 5).toLowerCase();
          bytes = await _fetchGoogleTts(text: text, langCode: langCode);
        }

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

  // ── SSML Builder ────────────────────────────
  static String _buildSsml({
    required String text,
    required String voice,
    required String rate,
    required String pitch,
    required String volume,
    bool rawSsml = false,
  }) {
    final lang = voice.length >= 5 ? voice.substring(0, 5) : 'en-US';
    final innerText = rawSsml ? text : _escapeXml(text);
    return '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="$lang">'
        '<voice name="$voice">'
        '<prosody rate="$rate" pitch="$pitch" volume="$volume">'
        '$innerText'
        '</prosody></voice></speak>';
  }

  static String _escapeXml(String text) => text
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&apos;');

  // ── Tier 1: edge-tts open API ───────────────
  // Free public edge-tts REST wrapper
  static Future<Uint8List?> _fetchEdgeTtsPublicApi({
    required String ssml,
    required String voice,
  }) async {
    try {
      // Using the publicly accessible edge-tts API
      final uri = Uri.parse('https://edgetts.deno.dev/v1/audio/speech');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: '{"model":"tts-1","input":${_jsonString(ssml)},"voice":"$voice","response_format":"mp3","speed":1.0}',
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200 && response.bodyBytes.length > 500) {
        return response.bodyBytes;
      }

      // Try alternate endpoint
      final uri2 = Uri.parse('https://edge-tts.deno.dev/tts?voice=$voice&rate=0%25&pitch=0Hz');
      final response2 = await http.post(
        uri2,
        headers: {'Content-Type': 'text/plain; charset=utf-8'},
        body: ssml,
      ).timeout(const Duration(seconds: 30));

      if (response2.statusCode == 200 && response2.bodyBytes.length > 500) {
        return response2.bodyBytes;
      }
    } catch (_) {}
    return null;
  }

  // ── Tier 2: Azure TTS demo ──────────────────
  static Future<Uint8List?> _fetchAzureDemoTts({
    required String text,
    required String voice,
    required String rate,
    required String pitch,
    required String volume,
  }) async {
    try {
      final ssml = _buildSsml(text: text, voice: voice, rate: rate, pitch: pitch, volume: volume);
      // Microsoft's public Speech Studio demo endpoint
      final regions = ['eastus', 'westus2', 'eastasia'];
      for (final region in regions) {
        try {
          final uri = Uri.parse(
              'https://$region.tts.speech.microsoft.com/cognitiveservices/v1');
          final response = await http.post(
            uri,
            headers: {
              'Content-Type': 'application/ssml+xml',
              'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
              'User-Agent': 'TitanStudioPRO/2.0',
            },
            body: ssml,
          ).timeout(const Duration(seconds: 15));

          if (response.statusCode == 200 && response.bodyBytes.length > 500) {
            return response.bodyBytes;
          }
        } catch (_) {
          continue;
        }
      }
    } catch (_) {}
    return null;
  }

  // ── Tier 3: Google TTS fallback ─────────────
  static Future<Uint8List?> _fetchGoogleTts({
    required String text,
    required String langCode,
  }) async {
    final shortCode = langCode.split('-').first; // 'hi-in' -> 'hi'
    final chunks = _splitText(text, 190);
    final parts = <Uint8List>[];

    for (final chunk in chunks) {
      try {
        final encoded = Uri.encodeComponent(chunk);
        final uri = Uri.parse(
          'https://translate.google.com/translate_tts?ie=UTF-8&q=$encoded&tl=$shortCode&client=tw-ob',
        );
        final response = await http.get(uri, headers: {
          'User-Agent':
              'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
          'Referer': 'https://translate.google.com/',
          'Accept': 'audio/mpeg,audio/*;q=0.9,*/*;q=0.8',
        }).timeout(const Duration(seconds: 20));

        if (response.statusCode == 200 && response.bodyBytes.isNotEmpty) {
          parts.add(response.bodyBytes);
        }
      } catch (_) {
        continue;
      }
    }

    if (parts.isEmpty) return null;
    final totalLen = parts.fold<int>(0, (s, b) => s + b.length);
    final result = Uint8List(totalLen);
    var offset = 0;
    for (final part in parts) {
      result.setRange(offset, offset + part.length, part);
      offset += part.length;
    }
    return result;
  }

  // ── Utils ────────────────────────────────────
  static String _jsonString(String s) =>
      '"${s.replaceAll('\\', '\\\\').replaceAll('"', '\\"').replaceAll('\n', '\\n').replaceAll('\r', '\\r').replaceAll('\t', '\\t')}"';

  static List<String> _splitText(String text, int maxLen) {
    if (text.length <= maxLen) return [text];
    final chunks = <String>[];
    final words = text.split(' ');
    var current = '';
    for (final word in words) {
      final next = current.isEmpty ? word : '$current $word';
      if (next.length > maxLen) {
        if (current.isNotEmpty) chunks.add(current);
        current = word;
      } else {
        current = next;
      }
    }
    if (current.isNotEmpty) chunks.add(current);
    return chunks;
  }

  static Future<File> _saveTemp(Uint8List bytes) async {
    final dir = await getTemporaryDirectory();
    final f = File('${dir.path}/titan_${DateTime.now().millisecondsSinceEpoch}.mp3');
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
      final r = await InternetAddress.lookup('microsoft.com')
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
