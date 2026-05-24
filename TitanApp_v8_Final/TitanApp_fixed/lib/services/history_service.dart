import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/history_model.dart';

// ═══════════════════════════════════════════════════════
//  HISTORY SERVICE v2.1 — Local + Firebase Cloud Backup
//  Local:  SharedPreferences (fast, offline)
//  Cloud:  Firebase RTDB — metadata backup
//          (Audio files are device-only — too large for cloud)
// ═══════════════════════════════════════════════════════

class HistoryService {
  static const String _dbUrl =
      'https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com';

  static String get _key {
    final uid = FirebaseAuth.instance.currentUser?.uid ?? 'guest';
    return 'titan_history_v2_$uid';
  }

  static Future<String?> _token() async {
    try {
      return await FirebaseAuth.instance.currentUser?.getIdToken();
    } catch (_) {
      return null;
    }
  }

  // ══════════════════════════════════════════════════════
  //  LOAD
  // ══════════════════════════════════════════════════════
  static Future<List<HistoryEntry>> load() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_key);
      if (raw == null) return [];
      final list = jsonDecode(raw) as List;
      return list
          .map((e) => HistoryEntry.fromJson(e as Map<String, dynamic>))
          .where((e) => File(e.filePath).existsSync())
          .toList();
    } catch (_) {
      return [];
    }
  }

  // ══════════════════════════════════════════════════════
  //  SAVE — local + Firebase metadata backup
  // ══════════════════════════════════════════════════════
  static Future<void> save(HistoryEntry entry) async {
    final prefs = await SharedPreferences.getInstance();
    final current = await load();
    current.insert(0, entry);
    final trimmed = current.take(200).toList();
    await prefs.setString(
        _key, jsonEncode(trimmed.map((e) => e.toJson()).toList()));

    // Fire-and-forget cloud backup
    _backupToFirebase(entry);
  }

  static Future<void> _backupToFirebase(HistoryEntry entry) async {
    try {
      final uid = FirebaseAuth.instance.currentUser?.uid;
      if (uid == null) return;
      final token = await _token();
      final uri = token != null
          ? Uri.parse('$_dbUrl/user_history/$uid/${entry.id}.json?auth=$token')
          : Uri.parse('$_dbUrl/user_history/$uid/${entry.id}.json');

      await http.put(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'id':        entry.id,
          'filename':  entry.filename,
          'text':      entry.text.length > 300
                         ? '${entry.text.substring(0, 300)}...'
                         : entry.text,
          'character': entry.character,
          'language':  entry.language,
          'emotion':   entry.emotion,
          'gender':    entry.gender,
          'timestamp': entry.timestamp,
          'createdAt': DateTime.now().millisecondsSinceEpoch,
        }),
      ).timeout(const Duration(seconds: 8));
    } catch (_) {
      // Silent fail — local save already succeeded
    }
  }

  // ══════════════════════════════════════════════════════
  //  DELETE
  // ══════════════════════════════════════════════════════
  static Future<void> delete(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final current = await load();
    final updated = current.where((e) => e.id != id).toList();
    await prefs.setString(
        _key, jsonEncode(updated.map((e) => e.toJson()).toList()));

    try {
      final uid = FirebaseAuth.instance.currentUser?.uid;
      if (uid == null) return;
      final token = await _token();
      final uri = token != null
          ? Uri.parse('$_dbUrl/user_history/$uid/$id.json?auth=$token')
          : Uri.parse('$_dbUrl/user_history/$uid/$id.json');
      await http.delete(uri).timeout(const Duration(seconds: 8));
    } catch (_) {}
  }

  // ══════════════════════════════════════════════════════
  //  CLEAR ALL
  // ══════════════════════════════════════════════════════
  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    final current = await load();
    for (final entry in current) {
      try {
        final f = File(entry.filePath);
        if (await f.exists()) await f.delete();
      } catch (_) {}
    }
    await prefs.remove(_key);
  }

  // ══════════════════════════════════════════════════════
  //  CLOUD COUNT  (for profile stats)
  // ══════════════════════════════════════════════════════
  static Future<int> getCloudHistoryCount() async {
    try {
      final uid = FirebaseAuth.instance.currentUser?.uid;
      if (uid == null) return 0;
      final token = await _token();
      final url = token != null
          ? '$_dbUrl/user_history/$uid.json?auth=$token&shallow=true'
          : '$_dbUrl/user_history/$uid.json?shallow=true';
      final res = await http.get(Uri.parse(url))
          .timeout(const Duration(seconds: 8));
      if (res.statusCode != 200 || res.body == 'null') return 0;
      final data = jsonDecode(res.body);
      if (data is Map) return data.length;
      return 0;
    } catch (_) {
      return 0;
    }
  }
}
