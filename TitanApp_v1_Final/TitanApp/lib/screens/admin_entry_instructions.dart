// ══════════════════════════════════════════════════════════════
//  SETTINGS SCREEN MEIN ADMIN ENTRY — Yeh code add karna hai
//  File: lib/screens/settings_screen.dart
//
//  Step 1: Admin ko settings screen se access karo
//          "About" section ke title pe 7 baar tap karo
//          Admin Dashboard khul jaayega
// ══════════════════════════════════════════════════════════════

// ── STEP 1: Import add karo settings_screen.dart ke top mein ──
// import '../screens/admin_dashboard_screen.dart';

// ── STEP 2: _SettingsState class mein yeh variables add karo ──

/*
  // Admin secret tap counter
  int _adminTapCount = 0;
  DateTime? _lastAdminTap;

  void _onAdminSecretTap() {
    final now = DateTime.now();
    if (_lastAdminTap != null &&
        now.difference(_lastAdminTap!).inSeconds > 3) {
      _adminTapCount = 0; // reset if too slow
    }
    _lastAdminTap = now;
    _adminTapCount++;

    if (_adminTapCount >= 7) {
      _adminTapCount = 0;
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const AdminDashboardScreen()),
      );
    } else if (_adminTapCount >= 4) {
      // Subtle hint after 4 taps
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${7 - _adminTapCount} more taps...'),
          duration: const Duration(milliseconds: 800),
          backgroundColor: cCard,
        ),
      );
    }
  }
*/

// ── STEP 3: About section ka SectionHeader wrap karo GestureDetector mein ──

/*
  // Existing About section ka code is tarah change karo:
  MintCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    GestureDetector(          // ← Yeh wrap karo
      onTap: _onAdminSecretTap,
      child: const SectionHeader('About'),   // ← Sirf title pe tap hoga
    ),
    const SizedBox(height: 10),
    // ... baaki about rows same rahenge
  ])),
*/


// ══════════════════════════════════════════════════════════════
//  USER TRACKING CODE — auth_service.dart mein add karo
//  Yeh Firebase mein user data likhega taake Admin Dashboard
//  mein Users tab mein data dikhaye
// ══════════════════════════════════════════════════════════════

// ── auth_service.dart mein _saveLoginTime() ke baad yeh add karo ──

/*
  static Future<void> _trackUserInAdmin(User user) async {
    try {
      final url = 'https://titanstudiopro-ec4f3-default-rtdb.firebaseio.com'
          '/admin/users/${user.uid}.json';
      final token = await user.getIdToken();
      await http.patch(
        Uri.parse('$url?auth=$token'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': user.email ?? '',
          'displayName': user.displayName ?? '',
          'lastActive': DateTime.now().millisecondsSinceEpoch,
          'createdAt': user.metadata.creationTime?.millisecondsSinceEpoch ?? 0,
        }),
      );
    } catch (_) {}
  }
*/

// ── Aur loginWithEmail() ke andar _saveLoginTime() ke baad add karo: ──
// await _trackUserInAdmin(cred.user!);

// ── signInWithGoogle() mein bhi same: ──
// await _trackUserInAdmin(cred.user!);

// ── registerWithEmail() mein bhi: ──
// await _trackUserInAdmin(cred.user!);

// ── imports jo auth_service.dart mein add karne honge ──
// import 'dart:convert';
// import 'package:http/http.dart' as http;
