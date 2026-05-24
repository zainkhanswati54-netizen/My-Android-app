import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';

// ═══════════════════════════════════════════════════════
//  TITAN ANALYTICS SERVICE v1.0
//  Saves per-generation logs to:
//    tts_logs/{uid}/{timestamp} — full generation record
//    admin/users/{uid}          — summary counters
// ═══════════════════════════════════════════════════════

class AnalyticsService {
  static const String _dbUrl =
      'https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com';

  // ── Get auth token ───────────────────────────────────
  static Future<String?> _token() async {
    try {
      return await FirebaseAuth.instance.currentUser?.getIdToken(true);
    } catch (_) {
      return null;
    }
  }

  // ══════════════════════════════════════════════════════
  //  LOG A GENERATION
  //  Call this right after TtsService.generate() succeeds
  // ══════════════════════════════════════════════════════

  static Future<void> logGeneration({
    required String text,
    required String character,
    required String language,
    required String emotion,
    required String preset,
    required int speedPct,
    required int pitchVal,
    required bool success,
    required int durationMs, // how long generation took
    bool hdVoice = false,
    bool ssmlMode = false,
    bool useBreaths = false,
    bool adaptivePacing = false,
  }) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) return;

      final token = await _token();
      final now = DateTime.now();
      final tsKey = now.millisecondsSinceEpoch.toString();
      final dateKey = '${now.year}-${now.month.toString().padLeft(2,'0')}-${now.day.toString().padLeft(2,'0')}';

      // ── 1. Save full log entry ───────────────────────
      final logEntry = {
        'uid':            user.uid,
        'email':          user.email ?? '',
        'displayName':    user.displayName ?? '',
        'text':           text.length > 200 ? '${text.substring(0, 200)}...' : text,
        'charCount':      text.length,
        'character':      character,
        'language':       language,
        'emotion':        emotion,
        'preset':         preset,
        'speedPct':       speedPct,
        'pitchVal':       pitchVal,
        'hdVoice':        hdVoice,
        'ssmlMode':       ssmlMode,
        'useBreaths':     useBreaths,
        'adaptivePacing': adaptivePacing,
        'success':        success,
        'durationMs':     durationMs,
        'timestamp':      now.millisecondsSinceEpoch,
        'dateKey':        dateKey,
        'hour':           now.hour,
      };

      final logUri = token != null
          ? Uri.parse('$_dbUrl/tts_logs/${user.uid}/$tsKey.json?auth=$token')
          : Uri.parse('$_dbUrl/tts_logs/${user.uid}/$tsKey.json');

      await http.put(
        logUri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(logEntry),
      ).timeout(const Duration(seconds: 10));

      // ── 2. Update user summary counters ─────────────
      // Read current counters first
      final userUri = token != null
          ? Uri.parse('$_dbUrl/admin/users/${user.uid}.json?auth=$token')
          : Uri.parse('$_dbUrl/admin/users/${user.uid}.json');

      final getRes = await http.get(userUri)
          .timeout(const Duration(seconds: 8));

      Map<String, dynamic> userData = {};
      if (getRes.statusCode == 200 && getRes.body != 'null') {
        final decoded = jsonDecode(getRes.body);
        if (decoded is Map<String, dynamic>) userData = decoded;
      }

      // Today's date key check
      final existingDateKey = userData['lastActiveDate'] ?? '';
      final todayRequests   = (existingDateKey == dateKey)
          ? ((userData['todayRequests'] ?? 0) as int) + 1
          : 1;

      final updatedUser = {
        ...userData,
        'uid':          user.uid,
        'email':        user.email ?? '',
        'displayName':  user.displayName ?? '',
        'lastActive':   now.millisecondsSinceEpoch,
        'lastActiveDate': dateKey,
        'todayRequests':  todayRequests,
        'totalRequests':  ((userData['totalRequests'] ?? 0) as int) + 1,
        'totalChars':     ((userData['totalChars'] ?? 0) as int) + text.length,
        'createdAt':      userData['createdAt'] ?? now.millisecondsSinceEpoch,
        // favourite tracking
        'lastCharacter':  character,
        'lastLanguage':   language,
      };

      await http.put(
        userUri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(updatedUser),
      ).timeout(const Duration(seconds: 10));

    } catch (_) {
      // Silent fail — never block the user
    }
  }

  // ══════════════════════════════════════════════════════
  //  FETCH USER LOGS  (with date filter)
  // ══════════════════════════════════════════════════════

  static Future<List<TtsLog>> getUserLogs(
    String uid, {
    DateTime? from,
    DateTime? to,
  }) async {
    try {
      final token = await _token();
      String url = '$_dbUrl/tts_logs/$uid.json';
      if (token != null) url += '?auth=$token';

      final res = await http.get(Uri.parse(url))
          .timeout(const Duration(seconds: 15));

      if (res.statusCode != 200 || res.body == 'null') return [];

      final raw = jsonDecode(res.body);
      if (raw is! Map) return [];

      final logs = <TtsLog>[];
      raw.forEach((key, val) {
        if (val is Map<String, dynamic>) {
          final log = TtsLog.fromMap(val);
          if (from != null && log.timestamp < from.millisecondsSinceEpoch) return;
          if (to   != null && log.timestamp > to.millisecondsSinceEpoch)   return;
          logs.add(log);
        }
      });

      logs.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      return logs;
    } catch (_) {
      return [];
    }
  }

  // ══════════════════════════════════════════════════════
  //  FETCH ALL USERS SUMMARY  (for analytics overview)
  // ══════════════════════════════════════════════════════

  static Future<List<UserAnalyticsSummary>> getAllUsersSummary() async {
    try {
      final token = await _token();
      final url = token != null
          ? '$_dbUrl/admin/users.json?auth=$token'
          : '$_dbUrl/admin/users.json';

      final res = await http.get(Uri.parse(url))
          .timeout(const Duration(seconds: 15));

      if (res.statusCode != 200 || res.body == 'null') return [];

      final raw = jsonDecode(res.body);
      if (raw is! Map) return [];

      final List<UserAnalyticsSummary> list = [];
      raw.forEach((uid, data) {
        if (data is Map<String, dynamic>) {
          list.add(UserAnalyticsSummary.fromMap(uid, data));
        }
      });

      list.sort((a, b) => b.totalRequests.compareTo(a.totalRequests));
      return list;
    } catch (_) {
      return [];
    }
  }
}

// ═══════════════════════════════════════════════════════
//  DATA MODELS
// ═══════════════════════════════════════════════════════

class TtsLog {
  final String uid;
  final String email;
  final String displayName;
  final String text;
  final int charCount;
  final String character;
  final String language;
  final String emotion;
  final String preset;
  final int speedPct;
  final int pitchVal;
  final bool hdVoice;
  final bool ssmlMode;
  final bool useBreaths;
  final bool adaptivePacing;
  final bool success;
  final int durationMs;
  final int timestamp;
  final String dateKey;
  final int hour;

  const TtsLog({
    required this.uid,
    required this.email,
    required this.displayName,
    required this.text,
    required this.charCount,
    required this.character,
    required this.language,
    required this.emotion,
    required this.preset,
    required this.speedPct,
    required this.pitchVal,
    required this.hdVoice,
    required this.ssmlMode,
    required this.useBreaths,
    required this.adaptivePacing,
    required this.success,
    required this.durationMs,
    required this.timestamp,
    required this.dateKey,
    required this.hour,
  });

  factory TtsLog.fromMap(Map<String, dynamic> m) => TtsLog(
    uid:            m['uid']           ?? '',
    email:          m['email']         ?? '',
    displayName:    m['displayName']   ?? '',
    text:           m['text']          ?? '',
    charCount:      m['charCount']     ?? 0,
    character:      m['character']     ?? '',
    language:       m['language']      ?? '',
    emotion:        m['emotion']       ?? '',
    preset:         m['preset']        ?? '',
    speedPct:       m['speedPct']      ?? 100,
    pitchVal:       m['pitchVal']      ?? 0,
    hdVoice:        m['hdVoice']       == true,
    ssmlMode:       m['ssmlMode']      == true,
    useBreaths:     m['useBreaths']    == true,
    adaptivePacing: m['adaptivePacing']== true,
    success:        m['success']       != false,
    durationMs:     m['durationMs']    ?? 0,
    timestamp:      m['timestamp']     ?? 0,
    dateKey:        m['dateKey']       ?? '',
    hour:           m['hour']          ?? 0,
  );

  String get timeFormatted {
    final dt = DateTime.fromMillisecondsSinceEpoch(timestamp);
    final h = dt.hour.toString().padLeft(2,'0');
    final m = dt.minute.toString().padLeft(2,'0');
    return '$h:$m  ${dt.day}/${dt.month}/${dt.year}';
  }

  String get durationFormatted {
    if (durationMs < 1000) return '${durationMs}ms';
    return '${(durationMs / 1000).toStringAsFixed(1)}s';
  }
}

class UserAnalyticsSummary {
  final String uid;
  final String email;
  final String displayName;
  final int totalRequests;
  final int todayRequests;
  final int totalChars;
  final int lastActive;
  final int createdAt;
  final String lastCharacter;
  final String lastLanguage;
  final bool banned;

  const UserAnalyticsSummary({
    required this.uid,
    required this.email,
    required this.displayName,
    required this.totalRequests,
    required this.todayRequests,
    required this.totalChars,
    required this.lastActive,
    required this.createdAt,
    required this.lastCharacter,
    required this.lastLanguage,
    required this.banned,
  });

  factory UserAnalyticsSummary.fromMap(String uid, Map<String, dynamic> m) =>
      UserAnalyticsSummary(
        uid:            uid,
        email:          m['email']          ?? '',
        displayName:    m['displayName']    ?? '',
        totalRequests:  m['totalRequests']  ?? 0,
        todayRequests:  m['todayRequests']  ?? 0,
        totalChars:     m['totalChars']     ?? 0,
        lastActive:     m['lastActive']     ?? 0,
        createdAt:      m['createdAt']      ?? 0,
        lastCharacter:  m['lastCharacter']  ?? '',
        lastLanguage:   m['lastLanguage']   ?? '',
        banned:         m['banned']         == true,
      );

  String get initials {
    final n = displayName.isNotEmpty ? displayName : email;
    final parts = n.trim().split(' ');
    if (parts.length >= 2 && parts[0].isNotEmpty && parts[1].isNotEmpty) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return n.isNotEmpty ? n[0].toUpperCase() : 'U';
  }

  String get lastActiveFormatted {
    if (lastActive == 0) return 'Never';
    final dt   = DateTime.fromMillisecondsSinceEpoch(lastActive);
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inHours   < 1) return '${diff.inMinutes}m ago';
    if (diff.inDays    < 1) return '${diff.inHours}h ago';
    if (diff.inDays   < 30) return '${diff.inDays}d ago';
    return '${dt.day}/${dt.month}/${dt.year}';
  }

  String get memberSince {
    if (createdAt == 0) return 'Unknown';
    final dt = DateTime.fromMillisecondsSinceEpoch(createdAt);
    return '${dt.day}/${dt.month}/${dt.year}';
  }
}
