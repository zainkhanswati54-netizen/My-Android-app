import 'dart:convert';
import 'dart:io';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/history_model.dart';

class HistoryService {
  // ── User-specific key — har user ki apni history ──────────
  static String get _key {
    final uid = FirebaseAuth.instance.currentUser?.uid ?? 'guest';
    return 'titan_history_v2_$uid';
  }

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

  static Future<void> save(HistoryEntry entry) async {
    final prefs = await SharedPreferences.getInstance();
    final current = await load();
    current.insert(0, entry);
    final trimmed = current.take(200).toList();
    await prefs.setString(
        _key, jsonEncode(trimmed.map((e) => e.toJson()).toList()));
  }

  static Future<void> delete(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final current = await load();
    final updated = current.where((e) => e.id != id).toList();
    await prefs.setString(
        _key, jsonEncode(updated.map((e) => e.toJson()).toList()));
  }

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
}
