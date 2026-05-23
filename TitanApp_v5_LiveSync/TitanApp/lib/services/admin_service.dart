import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';

// ═══════════════════════════════════════════════════════
//  TITAN ADMIN SERVICE v2.0
//  Firebase Realtime Database: Real read/write
//  DB URL: https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com
// ═══════════════════════════════════════════════════════

class AdminService {
  static const String _dbUrl =
      'https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com';

  // ── Admin PIN ────────────────────────────────────────
  static const String _adminPin = '1234';
  static bool verifyPin(String pin) => pin == _adminPin;

  // ══════════════════════════════════════════════════════
  //  HELPERS
  // ══════════════════════════════════════════════════════

  static Future<String?> _getToken() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) return null;
      return await user.getIdToken(true); // force refresh
    } catch (_) {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> _get(String path) async {
    try {
      final token = await _getToken();
      final uri = token != null
          ? Uri.parse('$_dbUrl/$path.json?auth=$token')
          : Uri.parse('$_dbUrl/$path.json');
      final res = await http.get(uri).timeout(const Duration(seconds: 15));
      if (res.statusCode == 200) {
        final body = res.body.trim();
        if (body == 'null' || body.isEmpty) return {};
        final decoded = jsonDecode(body);
        if (decoded is Map<String, dynamic>) return decoded;
        return {};
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  static Future<bool> _set(String path, dynamic data) async {
    try {
      final token = await _getToken();
      final uri = token != null
          ? Uri.parse('$_dbUrl/$path.json?auth=$token')
          : Uri.parse('$_dbUrl/$path.json');
      final res = await http
          .put(uri,
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode(data))
          .timeout(const Duration(seconds: 15));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> _patch(String path, Map<String, dynamic> data) async {
    try {
      final token = await _getToken();
      final uri = token != null
          ? Uri.parse('$_dbUrl/$path.json?auth=$token')
          : Uri.parse('$_dbUrl/$path.json');
      final res = await http
          .patch(uri,
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode(data))
          .timeout(const Duration(seconds: 15));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ══════════════════════════════════════════════════════
  //  1. MAINTENANCE MODE
  // ══════════════════════════════════════════════════════

  static Future<AdminMaintenanceData> getMaintenanceData() async {
    final data = await _get('admin/maintenance');
    return AdminMaintenanceData.fromMap(data ?? {});
  }

  static Future<bool> setMaintenanceMode({
    required bool enabled,
    required String message,
    String? allowedVersion,
  }) async {
    return await _set('admin/maintenance', {
      'enabled': enabled,
      'message': message,
      'allowedVersion': allowedVersion ?? '',
      'updatedAt': DateTime.now().millisecondsSinceEpoch,
    });
  }

  // ══════════════════════════════════════════════════════
  //  2. CHARACTER CONTROL
  // ══════════════════════════════════════════════════════

  static Future<Map<String, bool>> getCharacterStates() async {
    final data = await _get('admin/characters');
    if (data == null || data.isEmpty) return {};
    return data.map((k, v) => MapEntry(k, v == true));
  }

  static Future<bool> setCharacterEnabled(String name, bool enabled) async {
    return await _patch('admin/characters', {name: enabled});
  }

  static Future<bool> setAllCharacters(bool enabled) async {
    final all = {
      'Adam': enabled, 'Luna': enabled, 'Nova': enabled, 'Zara': enabled,
      'Rex': enabled, 'Aria': enabled, 'Bolt': enabled, 'Sage': enabled,
      'Kai': enabled, 'Amara': enabled, 'Echo': enabled, 'Lyra': enabled,
      'Titan': enabled, 'Mira': enabled, 'Vox': enabled, 'Zephyr': enabled,
      'Noor': enabled, 'Spark': enabled, 'Atlas': enabled, 'Seraph': enabled,
    };
    return await _set('admin/characters', all);
  }

  // ══════════════════════════════════════════════════════
  //  3. LIMITS
  // ══════════════════════════════════════════════════════

  static Future<AdminLimitsData> getLimitsData() async {
    final data = await _get('admin/limits');
    return AdminLimitsData.fromMap(data ?? {});
  }

  static Future<bool> setLimits(AdminLimitsData limits) async {
    return await _set('admin/limits', limits.toMap());
  }

  // ══════════════════════════════════════════════════════
  //  4. PREMIUM FEATURES LOCK
  // ══════════════════════════════════════════════════════

  static Future<AdminPremiumData> getPremiumData() async {
    final data = await _get('admin/premium');
    return AdminPremiumData.fromMap(data ?? {});
  }

  static Future<bool> setPremiumData(AdminPremiumData data) async {
    return await _set('admin/premium', data.toMap());
  }

  // ══════════════════════════════════════════════════════
  //  5. ADMOB / AD CONTROL
  // ══════════════════════════════════════════════════════

  static Future<AdminAdData> getAdData() async {
    final data = await _get('admin/ads');
    return AdminAdData.fromMap(data ?? {});
  }

  static Future<bool> setAdData(AdminAdData data) async {
    return await _set('admin/ads', data.toMap());
  }

  // ══════════════════════════════════════════════════════
  //  6. USER ACCOUNTS AUDIT
  // ══════════════════════════════════════════════════════

  static Future<List<AdminUserRecord>> getUserAudit() async {
    try {
      final token = await _getToken();
      final uri = token != null
          ? Uri.parse('$_dbUrl/admin/users.json?auth=$token')
          : Uri.parse('$_dbUrl/admin/users.json');
      final res = await http.get(uri).timeout(const Duration(seconds: 15));
      if (res.statusCode != 200 || res.body == 'null') return [];
      final raw = jsonDecode(res.body);
      if (raw is! Map) return [];
      final List<AdminUserRecord> users = [];
      raw.forEach((uid, data) {
        if (data is Map<String, dynamic>) {
          users.add(AdminUserRecord.fromMap(uid, data));
        }
      });
      users.sort((a, b) => b.lastActive.compareTo(a.lastActive));
      return users;
    } catch (_) {
      return [];
    }
  }

  static Future<bool> banUser(String uid, bool banned) async {
    return await _patch('admin/users/$uid', {'banned': banned});
  }

  static Future<bool> setPremiumUser(String uid, bool premium) async {
    return await _patch('admin/users/$uid', {'isPremium': premium});
  }

  // ══════════════════════════════════════════════════════
  //  7. API ABUSE PREVENTION
  // ══════════════════════════════════════════════════════

  static Future<AdminAbuseData> getAbuseData() async {
    final data = await _get('admin/abuse');
    return AdminAbuseData.fromMap(data ?? {});
  }

  static Future<bool> setAbuseData(AdminAbuseData data) async {
    return await _set('admin/abuse', data.toMap());
  }

  static Future<List<AdminRequestLog>> getRequestLogs() async {
    try {
      final token = await _getToken();
      final uri = token != null
          ? Uri.parse(
              '$_dbUrl/admin/request_logs.json?auth=$token&orderBy="\$key"&limitToLast=50')
          : Uri.parse(
              '$_dbUrl/admin/request_logs.json?orderBy="\$key"&limitToLast=50');
      final res = await http.get(uri).timeout(const Duration(seconds: 15));
      if (res.statusCode != 200 || res.body == 'null') return [];
      final raw = jsonDecode(res.body);
      if (raw is! Map) return [];
      final List<AdminRequestLog> logs = [];
      raw.forEach((key, data) {
        if (data is Map<String, dynamic>) {
          logs.add(AdminRequestLog.fromMap(data));
        }
      });
      logs.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      return logs;
    } catch (_) {
      return [];
    }
  }
} // END AdminService

// ═══════════════════════════════════════════════════════
//  DATA MODELS
// ═══════════════════════════════════════════════════════

class AdminMaintenanceData {
  final bool enabled;
  final String message;
  final String allowedVersion;
  final int updatedAt;

  const AdminMaintenanceData({
    this.enabled = false,
    this.message = 'App is under maintenance. Please check back later.',
    this.allowedVersion = '',
    this.updatedAt = 0,
  });

  factory AdminMaintenanceData.fromMap(Map<String, dynamic> m) =>
      AdminMaintenanceData(
        enabled: m['enabled'] == true,
        message: m['message'] ?? 'App is under maintenance.',
        allowedVersion: m['allowedVersion'] ?? '',
        updatedAt: m['updatedAt'] ?? 0,
      );

  Map<String, dynamic> toMap() => {
        'enabled': enabled,
        'message': message,
        'allowedVersion': allowedVersion,
        'updatedAt': updatedAt,
      };
}

class AdminLimitsData {
  final int freeCharLimit;
  final int premiumCharLimit;
  final int freeDailyLimit;
  final int premiumDailyLimit;
  final int freeHistoryLimit;
  final int premiumHistoryLimit;

  const AdminLimitsData({
    this.freeCharLimit = 300,
    this.premiumCharLimit = 3000,
    this.freeDailyLimit = 10,
    this.premiumDailyLimit = 200,
    this.freeHistoryLimit = 20,
    this.premiumHistoryLimit = 500,
  });

  factory AdminLimitsData.fromMap(Map<String, dynamic> m) => AdminLimitsData(
        freeCharLimit: m['freeCharLimit'] ?? 300,
        premiumCharLimit: m['premiumCharLimit'] ?? 3000,
        freeDailyLimit: m['freeDailyLimit'] ?? 10,
        premiumDailyLimit: m['premiumDailyLimit'] ?? 200,
        freeHistoryLimit: m['freeHistoryLimit'] ?? 20,
        premiumHistoryLimit: m['premiumHistoryLimit'] ?? 500,
      );

  Map<String, dynamic> toMap() => {
        'freeCharLimit': freeCharLimit,
        'premiumCharLimit': premiumCharLimit,
        'freeDailyLimit': freeDailyLimit,
        'premiumDailyLimit': premiumDailyLimit,
        'freeHistoryLimit': freeHistoryLimit,
        'premiumHistoryLimit': premiumHistoryLimit,
      };
}

class AdminPremiumData {
  final bool hdVoiceLocked;
  final bool autoEmotionLocked;
  final bool wordBoundaryLocked;
  final bool ssmlModeLocked;
  final bool adaptivePacingLocked;
  final bool breathingLocked;
  final bool premiumCharactersLocked;
  final bool exportLocked;

  const AdminPremiumData({
    this.hdVoiceLocked = true,
    this.autoEmotionLocked = false,
    this.wordBoundaryLocked = true,
    this.ssmlModeLocked = false,
    this.adaptivePacingLocked = false,
    this.breathingLocked = true,
    this.premiumCharactersLocked = false,
    this.exportLocked = false,
  });

  factory AdminPremiumData.fromMap(Map<String, dynamic> m) => AdminPremiumData(
        hdVoiceLocked: m['hdVoiceLocked'] ?? true,
        autoEmotionLocked: m['autoEmotionLocked'] ?? false,
        wordBoundaryLocked: m['wordBoundaryLocked'] ?? true,
        ssmlModeLocked: m['ssmlModeLocked'] ?? false,
        adaptivePacingLocked: m['adaptivePacingLocked'] ?? false,
        breathingLocked: m['breathingLocked'] ?? true,
        premiumCharactersLocked: m['premiumCharactersLocked'] ?? false,
        exportLocked: m['exportLocked'] ?? false,
      );

  Map<String, dynamic> toMap() => {
        'hdVoiceLocked': hdVoiceLocked,
        'autoEmotionLocked': autoEmotionLocked,
        'wordBoundaryLocked': wordBoundaryLocked,
        'ssmlModeLocked': ssmlModeLocked,
        'adaptivePacingLocked': adaptivePacingLocked,
        'breathingLocked': breathingLocked,
        'premiumCharactersLocked': premiumCharactersLocked,
        'exportLocked': exportLocked,
      };
}

class AdminAdData {
  final bool adsEnabled;
  final bool bannerEnabled;
  final bool interstitialEnabled;
  final bool rewardedEnabled;
  final String bannerAdUnitId;
  final String interstitialAdUnitId;
  final String rewardedAdUnitId;
  final int interstitialFrequency;
  final bool testMode;

  const AdminAdData({
    this.adsEnabled = false,
    this.bannerEnabled = false,
    this.interstitialEnabled = false,
    this.rewardedEnabled = false,
    this.bannerAdUnitId = '',
    this.interstitialAdUnitId = '',
    this.rewardedAdUnitId = '',
    this.interstitialFrequency = 5,
    this.testMode = true,
  });

  factory AdminAdData.fromMap(Map<String, dynamic> m) => AdminAdData(
        adsEnabled: m['adsEnabled'] ?? false,
        bannerEnabled: m['bannerEnabled'] ?? false,
        interstitialEnabled: m['interstitialEnabled'] ?? false,
        rewardedEnabled: m['rewardedEnabled'] ?? false,
        bannerAdUnitId: m['bannerAdUnitId'] ?? '',
        interstitialAdUnitId: m['interstitialAdUnitId'] ?? '',
        rewardedAdUnitId: m['rewardedAdUnitId'] ?? '',
        interstitialFrequency: m['interstitialFrequency'] ?? 5,
        testMode: m['testMode'] ?? true,
      );

  Map<String, dynamic> toMap() => {
        'adsEnabled': adsEnabled,
        'bannerEnabled': bannerEnabled,
        'interstitialEnabled': interstitialEnabled,
        'rewardedEnabled': rewardedEnabled,
        'bannerAdUnitId': bannerAdUnitId,
        'interstitialAdUnitId': interstitialAdUnitId,
        'rewardedAdUnitId': rewardedAdUnitId,
        'interstitialFrequency': interstitialFrequency,
        'testMode': testMode,
      };
}

class AdminUserRecord {
  final String uid;
  final String email;
  final String displayName;
  final int lastActive;
  final int createdAt;
  final bool isPremium;
  final bool banned;
  final int totalRequests;
  final int todayRequests;

  const AdminUserRecord({
    required this.uid,
    required this.email,
    required this.displayName,
    required this.lastActive,
    required this.createdAt,
    this.isPremium = false,
    this.banned = false,
    this.totalRequests = 0,
    this.todayRequests = 0,
  });

  factory AdminUserRecord.fromMap(String uid, Map<String, dynamic> m) =>
      AdminUserRecord(
        uid: uid,
        email: m['email'] ?? '',
        displayName: m['displayName'] ?? 'User',
        lastActive: m['lastActive'] ?? 0,
        createdAt: m['createdAt'] ?? 0,
        isPremium: m['isPremium'] == true,
        banned: m['banned'] == true,
        totalRequests: m['totalRequests'] ?? 0,
        todayRequests: m['todayRequests'] ?? 0,
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
    final dt = DateTime.fromMillisecondsSinceEpoch(lastActive);
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inHours < 1) return '${diff.inMinutes}m ago';
    if (diff.inDays < 1) return '${diff.inHours}h ago';
    if (diff.inDays < 30) return '${diff.inDays}d ago';
    return '${dt.day}/${dt.month}/${dt.year}';
  }
}

class AdminAbuseData {
  final bool rateLimitEnabled;
  final int maxRequestsPerMinute;
  final int maxRequestsPerHour;
  final int maxCharsPerRequest;
  final bool blockVpn;
  final bool blockTor;
  final int suspiciousThreshold;
  final List<String> blockedIps;

  const AdminAbuseData({
    this.rateLimitEnabled = true,
    this.maxRequestsPerMinute = 5,
    this.maxRequestsPerHour = 30,
    this.maxCharsPerRequest = 3000,
    this.blockVpn = false,
    this.blockTor = false,
    this.suspiciousThreshold = 50,
    this.blockedIps = const [],
  });

  factory AdminAbuseData.fromMap(Map<String, dynamic> m) => AdminAbuseData(
        rateLimitEnabled: m['rateLimitEnabled'] ?? true,
        maxRequestsPerMinute: m['maxRequestsPerMinute'] ?? 5,
        maxRequestsPerHour: m['maxRequestsPerHour'] ?? 30,
        maxCharsPerRequest: m['maxCharsPerRequest'] ?? 3000,
        blockVpn: m['blockVpn'] ?? false,
        blockTor: m['blockTor'] ?? false,
        suspiciousThreshold: m['suspiciousThreshold'] ?? 50,
        blockedIps: List<String>.from(m['blockedIps'] ?? []),
      );

  Map<String, dynamic> toMap() => {
        'rateLimitEnabled': rateLimitEnabled,
        'maxRequestsPerMinute': maxRequestsPerMinute,
        'maxRequestsPerHour': maxRequestsPerHour,
        'maxCharsPerRequest': maxCharsPerRequest,
        'blockVpn': blockVpn,
        'blockTor': blockTor,
        'suspiciousThreshold': suspiciousThreshold,
        'blockedIps': blockedIps,
      };
}

class AdminRequestLog {
  final String uid;
  final String email;
  final String character;
  final String language;
  final int charCount;
  final int timestamp;
  final bool success;
  final String ip;

  const AdminRequestLog({
    required this.uid,
    required this.email,
    required this.character,
    required this.language,
    required this.charCount,
    required this.timestamp,
    required this.success,
    required this.ip,
  });

  factory AdminRequestLog.fromMap(Map<String, dynamic> m) => AdminRequestLog(
        uid: m['uid'] ?? '',
        email: m['email'] ?? '',
        character: m['character'] ?? '',
        language: m['language'] ?? '',
        charCount: m['charCount'] ?? 0,
        timestamp: m['timestamp'] ?? 0,
        success: m['success'] ?? true,
        ip: m['ip'] ?? '',
      );

  String get timeFormatted {
    final dt = DateTime.fromMillisecondsSinceEpoch(timestamp);
    return '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')} '
        '${dt.day}/${dt.month}';
  }
}
