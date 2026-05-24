import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/history_model.dart';

// ═══════════════════════════════════════════════════════
//  HISTORY SERVICE v2.2 — Fixed: field mismatch + cloud restore
//
//  Fixes:
//   1. filePath field mismatch → now uses HistoryEntry.filePath correctly
//   2. Login ke baad Firebase se history restore hoti hai
//   3. Duplicate HistoryService in history_model removed
//   4. File existence check only filters display, not delete from prefs
// ═══════════════════════════════════════════════════════

class HistoryService {
  static const String _dbUrl =
      'https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com';

  // Per-user key — logout/login history separate rehti hai
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
  //  LOAD — local first, then filter by file existence
  //  FIX: removed premature deletion from prefs on missing file
  // ══════════════════════════════════════════════════════
  static Future<List<HistoryEntry>> load() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_key);
      if (raw == null || raw.isEmpty) return [];
      final list = jsonDecode(raw) as List;
      return list
          .map((e) => HistoryEntry.fromJson(e as Map<String, dynamic>))
          .where((e) => e.filePath.isNotEmpty)
          // Only show entries where audio file still exists on device
          .where((e) => File(e.filePath).existsSync())
          .toList();
    } catch (_) {
      return [];
    }
  }

  /// Load ALL entries from prefs (including missing files) — for internal use
  static Future<List<HistoryEntry>> _loadAll() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_key);
      if (raw == null || raw.isEmpty) return [];
      final list = jsonDecode(raw) as List;
      return list
          .map((e) => HistoryEntry.fromJson(e as Map<String, dynamic>))
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
    final current = await _loadAll();
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
      final uri = Uri.parse(
        token != null
            ? '$_dbUrl/user_history/$uid/${entry.id}.json?auth=$token'
            : '$_dbUrl/user_history/$uid/${entry.id}.json',
      );

      await http.put(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'id':        entry.id,
          'filename':  entry.filename,
          'filePath':  entry.filePath,
          'text': entry.text.length > 300
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
  //  RESTORE FROM FIREBASE — call this after login
  //  Merges cloud metadata with local prefs (metadata only,
  //  audio files are device-only)
  // ══════════════════════════════════════════════════════
  static Future<void> restoreFromCloud() async {
    try {
      final uid = FirebaseAuth.instance.currentUser?.uid;
      if (uid == null) return;

      final token = await _token();
      final url = token != null
          ? '$_dbUrl/user_history/$uid.json?auth=$token'
          : '$_dbUrl/user_history/$uid.json';

      final res = await http
          .get(Uri.parse(url))
          .timeout(const Duration(seconds: 10));

      if (res.statusCode != 200 || res.body == 'null') return;

      final Map<String, dynamic> data =
          jsonDecode(res.body) as Map<String, dynamic>;

      // Build entries from cloud data
      final cloudEntries = data.values
          .map((e) {
            try {
              return HistoryEntry.fromJson(e as Map<String, dynamic>);
            } catch (_) {
              return null;
            }
          })
          .whereType<HistoryEntry>()
          .toList();

      if (cloudEntries.isEmpty) return;

      // Merge with local — prefer local, add missing cloud entries
      final localAll = await _loadAll();
      final localIds = localAll.map((e) => e.id).toSet();

      final merged = [...localAll];
      for (final ce in cloudEntries) {
        if (!localIds.contains(ce.id)) {
          merged.add(ce);
        }
      }

      // Sort by timestamp descending and save
      merged.sort((a, b) => b.timestamp.compareTo(a.timestamp));

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
          _key, jsonEncode(merged.take(200).map((e) => e.toJson()).toList()));
    } catch (_) {
      // Silent fail — local history still works
    }
  }

  // ══════════════════════════════════════════════════════
  //  DELETE
  // ══════════════════════════════════════════════════════
  static Future<void> delete(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final current = await _loadAll();
    final updated = current.where((e) => e.id != id).toList();
    await prefs.setString(
        _key, jsonEncode(updated.map((e) => e.toJson()).toList()));

    try {
      final uid = FirebaseAuth.instance.currentUser?.uid;
      if (uid == null) return;
      final token = await _token();
      final uri = Uri.parse(
        token != null
            ? '$_dbUrl/user_history/$uid/$id.json?auth=$token'
            : '$_dbUrl/user_history/$uid/$id.json',
      );
      await http.delete(uri).timeout(const Duration(seconds: 8));
    } catch (_) {}
  }

  // ══════════════════════════════════════════════════════
  //  CLEAR ALL
  // ══════════════════════════════════════════════════════
  static Future<void> clear() async => clearAll();

  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    final current = await _loadAll();
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
      final res =
          await http.get(Uri.parse(url)).timeout(const Duration(seconds: 8));
      if (res.statusCode != 200 || res.body == 'null') return 0;
      final data = jsonDecode(res.body);
      if (data is Map) return data.length;
      return 0;
    } catch (_) {
      return 0;
    }
  }
}
