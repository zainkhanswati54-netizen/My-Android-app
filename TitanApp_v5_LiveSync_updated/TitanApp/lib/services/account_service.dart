import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_auth/firebase_auth.dart';

// ── Saved Account Model ───────────────────────────────────
class SavedAccount {
  final String uid;
  final String email;
  final String displayName;
  final String initials;
  final int lastUsed; // millisecondsSinceEpoch

  const SavedAccount({
    required this.uid,
    required this.email,
    required this.displayName,
    required this.initials,
    required this.lastUsed,
  });

  Map<String, dynamic> toJson() => {
    'uid': uid,
    'email': email,
    'displayName': displayName,
    'initials': initials,
    'lastUsed': lastUsed,
  };

  factory SavedAccount.fromJson(Map<String, dynamic> j) => SavedAccount(
    uid: j['uid'] ?? '',
    email: j['email'] ?? '',
    displayName: j['displayName'] ?? '',
    initials: j['initials'] ?? 'U',
    lastUsed: j['lastUsed'] ?? 0,
  );

  static String buildInitials(String? name, String? email) {
    final n = (name != null && name.trim().isNotEmpty)
        ? name.trim()
        : (email ?? 'U');
    final parts = n.split(RegExp(r'\s+'));
    if (parts.length >= 2 && parts[0].isNotEmpty && parts[1].isNotEmpty) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    if (n.isNotEmpty) return n[0].toUpperCase();
    return 'U';
  }
}

// ── Account Service ───────────────────────────────────────
class AccountService {
  static const _key = 'titan_saved_accounts_v1';

  // ── Load all saved accounts ───────────────────────────────
  static Future<List<SavedAccount>> loadAll() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_key);
      if (raw == null) return [];
      final list = jsonDecode(raw) as List;
      final accounts = list
          .map((e) => SavedAccount.fromJson(e as Map<String, dynamic>))
          .toList();
      // Sort: most recently used first
      accounts.sort((a, b) => b.lastUsed.compareTo(a.lastUsed));
      return accounts;
    } catch (_) {
      return [];
    }
  }

  // ── Save current user to saved accounts ──────────────────
  static Future<void> saveCurrentUser(User user) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final accounts = await loadAll();

      final newAccount = SavedAccount(
        uid: user.uid,
        email: user.email ?? '',
        displayName: user.displayName ?? '',
        initials: SavedAccount.buildInitials(user.displayName, user.email),
        lastUsed: DateTime.now().millisecondsSinceEpoch,
      );

      // Remove old entry for this uid if exists
      final updated = accounts.where((a) => a.uid != user.uid).toList();
      updated.insert(0, newAccount);

      // Keep max 5 accounts
      final trimmed = updated.take(5).toList();
      await prefs.setString(
          _key, jsonEncode(trimmed.map((a) => a.toJson()).toList()));
    } catch (_) {}
  }

  // ── Update lastUsed for a uid ─────────────────────────────
  static Future<void> updateLastUsed(String uid) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final accounts = await loadAll();
      final idx = accounts.indexWhere((a) => a.uid == uid);
      if (idx < 0) return;
      final updated = List<SavedAccount>.from(accounts);
      final old = updated[idx];
      updated[idx] = SavedAccount(
        uid: old.uid,
        email: old.email,
        displayName: old.displayName,
        initials: old.initials,
        lastUsed: DateTime.now().millisecondsSinceEpoch,
      );
      updated.sort((a, b) => b.lastUsed.compareTo(a.lastUsed));
      await prefs.setString(
          _key, jsonEncode(updated.map((a) => a.toJson()).toList()));
    } catch (_) {}
  }

  // ── Remove a saved account ────────────────────────────────
  static Future<void> removeAccount(String uid) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final accounts = await loadAll();
      final updated = accounts.where((a) => a.uid != uid).toList();
      await prefs.setString(
          _key, jsonEncode(updated.map((a) => a.toJson()).toList()));
    } catch (_) {}
  }

  // ── Clear all saved accounts ──────────────────────────────
  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
