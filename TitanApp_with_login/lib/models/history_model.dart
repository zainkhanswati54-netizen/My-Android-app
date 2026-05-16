import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class HistoryEntry {
  final String id, filename, path, language, gender, emotion, timestamp;
  const HistoryEntry({
    required this.id, required this.filename, required this.path,
    required this.language, required this.gender, required this.emotion,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() => {
    'id': id, 'filename': filename, 'path': path,
    'language': language, 'gender': gender, 'emotion': emotion,
    'timestamp': timestamp,
  };

  factory HistoryEntry.fromJson(Map<String, dynamic> j) => HistoryEntry(
    id: j['id'] ?? '', filename: j['filename'] ?? '',
    path: j['path'] ?? '', language: j['language'] ?? '',
    gender: j['gender'] ?? '', emotion: j['emotion'] ?? '',
    timestamp: j['timestamp'] ?? '',
  );
}

class HistoryService {
  static const _key = 'titan_history_v2';

  static Future<List<HistoryEntry>> load() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_key);
      if (raw == null) return [];
      final list = jsonDecode(raw) as List;
      return list.map((e) => HistoryEntry.fromJson(e)).toList();
    } catch (_) { return []; }
  }

  static Future<void> add(HistoryEntry e) async {
    final list = await load();
    list.insert(0, e);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, jsonEncode(list.take(200).map((x) => x.toJson()).toList()));
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
