import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class SavedAccount {
  final String uid;
  final String email;
  final String displayName;
  final String initials;
  final int lastLogin;

  const SavedAccount({
    required this.uid,
    required this.email,
    required this.displayName,
    required this.initials,
    required this.lastLogin,
  });

  Map<String, dynamic> toJson() => {
    'uid': uid, 'email': email,
    'displayName': displayName, 'initials': initials,
    'lastLogin': lastLogin,
  };

  factory SavedAccount.fromJson(Map<String, dynamic> j) => SavedAccount(
    uid: j['uid'] ?? '',
    email: j['email'] ?? '',
    displayName: j['displayName'] ?? '',
    initials: j['initials'] ?? 'U',
    lastLogin: j['lastLogin'] ?? 0,
  );
}

class AccountManager {
  static const _key = 'titan_saved_accounts';

  // ── Saved accounts load karo ──────────────────────────────
  static Future<List<SavedAccount>> loadAccounts() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_key);
      if (raw == null) return [];
      final list = jsonDecode(raw) as List;
      return list.map((e) => SavedAccount.fromJson(e)).toList();
    } catch (_) {
      return [];
    }
  }

  // ── Account save karo (login ke baad) ────────────────────
  static Future<void> saveAccount(SavedAccount account) async {
    final prefs = await SharedPreferences.getInstance();
    final accounts = await loadAccounts();
    // Remove if already exists
    accounts.removeWhere((a) => a.uid == account.uid);
    // Add at top
    accounts.insert(0, account);
    // Max 5 accounts
    final trimmed = accounts.take(5).toList();
    await prefs.setString(_key, jsonEncode(trimmed.map((a) => a.toJson()).toList()));
  }

  // ── Account remove karo ───────────────────────────────────
  static Future<void> removeAccount(String uid) async {
    final prefs = await SharedPreferences.getInstance();
    final accounts = await loadAccounts();
    accounts.removeWhere((a) => a.uid == uid);
    await prefs.setString(_key, jsonEncode(accounts.map((a) => a.toJson()).toList()));
  }

  // ── Initials helper ───────────────────────────────────────
  static String getInitials(String name, String email) {
    final n = name.trim().isNotEmpty ? name.trim() : email;
    final parts = n.split(' ');
    if (parts.length >= 2 && parts[0].isNotEmpty && parts[1].isNotEmpty) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return n.isNotEmpty ? n[0].toUpperCase() : 'U';
  }
}
