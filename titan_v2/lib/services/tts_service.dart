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
        processedText = processedText.replaceAllMapped(RegExp(r'([.!?])\s+'), (m) => '${m[1]}  ');
      }
      if (adaptivePacing && text.length > 500) {
        rate = speedToRate((speedPct - 5).clamp(10, 100), emotion);
      }

      return await _callEdgeTts(text: processedText, voice: voice, rate: rate, pitch: pitch, volume: volume);
    } catch (e) {
      return TtsResult.error('Generation failed: $e');
    }
  }

  static Future<TtsResult> _callEdgeTts({
    required String text, required String voice,
    required String rate, required String pitch, required String volume,
  }) async {
    final String ssml = _buildSsml(text: text, voice: voice, rate: rate, pitch: pitch, volume: volume);
    Exception? lastError;

    for (int attempt = 0; attempt < _maxRetries; attempt++) {
      try {
        final hasNet = await _checkInternet();
        if (!hasNet) return TtsResult.error('No internet connection.\nPlease turn on WiFi or mobile data.');

        final bytes = await _fetchEdgeTts(voice: voice, ssml: ssml);
        if (bytes != null && bytes.isNotEmpty) {
          final file = await _saveTemp(bytes);
          return TtsResult.success(file);
        }
      } catch (e) {
        lastError = e as Exception?;
        if (attempt < _maxRetries - 1) await Future.delayed(Duration(seconds: attempt + 1));
      }
    }
    return TtsResult.error('Could not generate audio.\n${lastError?.toString() ?? "Unknown error"}\nCheck internet connection.');
  }

  static Future<Uint8List?> _fetchEdgeTts({required String voice, required String ssml}) async {
    final ts = DateTime.now().millisecondsSinceEpoch;
    final uri = Uri.parse(
      'https://speech.platform.bing.com/consumer/speech/synthesize/readspeaker/edge/v1'
      '?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4&ConnectionId=$ts',
    );
    try {
      final response = await http.post(uri, headers: {
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Origin': 'chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold',
        'Accept': '*/*',
      }, body: ssml).timeout(const Duration(seconds: 30));
      if (response.statusCode == 200 && response.bodyBytes.isNotEmpty) return response.bodyBytes;
    } catch (_) {}
    return null;
  }

  static String _buildSsml({
    required String text, required String voice,
    required String rate, required String pitch, required String volume,
  }) {
    final safe = text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
    return '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
        '<voice name="$voice"><prosody rate="$rate" pitch="$pitch" volume="$volume">$safe</prosody></voice></speak>';
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
      final r = await InternetAddress.lookup('speech.platform.bing.com').timeout(const Duration(seconds: 5));
      return r.isNotEmpty && r.first.rawAddress.isNotEmpty;
    } catch (_) { return false; }
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
