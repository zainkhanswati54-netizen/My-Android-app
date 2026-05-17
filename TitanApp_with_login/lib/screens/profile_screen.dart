import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/auth_service.dart';
import '../utils/constants.dart';
import 'login_screen.dart';
import 'account_switch_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  User? get _user => FirebaseAuth.instance.currentUser;

  // ── Avatar initials — FIXED ───────────────────────────────
  String _getInitials(String? name, String? email) {
    final n = (name != null && name.trim().isNotEmpty) ? name.trim() : (email ?? 'U');
    final parts = n.split(RegExp(r'\s+'));
    if (parts.length >= 2 && parts[0].isNotEmpty && parts[1].isNotEmpty) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    if (n.isNotEmpty) return n[0].toUpperCase();
    return 'U';
  }

  // ── Logout ────────────────────────────────────────────────
  Future<void> _logout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: cCard,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Logout',
            style: TextStyle(color: cText, fontWeight: FontWeight.w700)),
        content: const Text('Are you sure you want to logout?',
            style: TextStyle(color: cMuted)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel', style: TextStyle(color: cMuted)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Logout', style: TextStyle(color: cRed)),
          ),
        ],
      ),
    );
    if (confirm != true) return;
    await AuthService.signOut();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  // ── Switch Account ────────────────────────────────────────
  Future<void> _switchAccount() async {
    final uid = _user?.uid ?? '';
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AccountSwitchScreen(currentUid: uid),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final name  = _user?.displayName ?? '';
    final email = _user?.email ?? '';
    final initials = _getInitials(name, email);
    final displayName = name.isNotEmpty ? name : email.split('@').first;
    final createdAt = _user?.metadata.creationTime;

    return Scaffold(
      backgroundColor: cBg,
      appBar: AppBar(
        backgroundColor: cBg2,
        title: const Text('My Profile',
            style: TextStyle(
                fontSize: 18, fontWeight: FontWeight.w800, color: cText)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded, color: cText, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        elevation: 0,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(height: 1, color: cBorder),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 36),

            // ── Avatar ────────────────────────────────────────
            Center(
              child: Container(
                width: 100, height: 100,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: const LinearGradient(
                    colors: [cGreen, cGreen2],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: cGreen.withOpacity(0.4),
                      blurRadius: 28,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Center(
                  child: Text(initials,
                      style: const TextStyle(
                          fontSize: 38,
                          fontWeight: FontWeight.w800,
                          color: Colors.white)),
                ),
              ),
            ),

            const SizedBox(height: 18),

            // ── Name ──────────────────────────────────────────
            Center(
              child: Text(displayName,
                  style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: cText)),
            ),
            const SizedBox(height: 5),
            Center(
              child: Text(email,
                  style: const TextStyle(fontSize: 13, color: cMuted)),
            ),
            const SizedBox(height: 10),

            // ── Badge ─────────────────────────────────────────
            Center(
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: cGreen.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(100),
                  border: Border.all(color: cGreen.withOpacity(0.3)),
                ),
                child: const Row(mainAxisSize: MainAxisSize.min, children: [
                  Icon(Icons.verified_rounded, color: cGreen, size: 14),
                  SizedBox(width: 5),
                  Text('Verified Account',
                      style: TextStyle(
                          fontSize: 12,
                          color: cGreen,
                          fontWeight: FontWeight.w600)),
                ]),
              ),
            ),

            const SizedBox(height: 32),

            // ── Info card ─────────────────────────────────────
            Container(
              decoration: BoxDecoration(
                color: cCard,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: cBorder),
              ),
              child: Column(children: [
                _infoTile(
                    icon: Icons.person_outline_rounded,
                    label: 'Full Name',
                    value: name.isNotEmpty ? name : 'Not set'),
                Container(height: 1, color: cBorder),
                _infoTile(
                    icon: Icons.email_outlined,
                    label: 'Email',
                    value: email),
                Container(height: 1, color: cBorder),
                _infoTile(
                    icon: Icons.calendar_today_outlined,
                    label: 'Member Since',
                    value: createdAt != null
                        ? '${createdAt.day}/${createdAt.month}/${createdAt.year}'
                        : 'Unknown'),
              ]),
            ),

            const SizedBox(height: 20),

            // ── Switch Account ────────────────────────────────
            _ActionButton(
              icon: Icons.switch_account_rounded,
              label: 'Switch Account',
              subtitle: 'Login with a different account',
              color: cGreen,
              onTap: _switchAccount,
            ),

            const SizedBox(height: 12),

            // ── Logout ────────────────────────────────────────
            _ActionButton(
              icon: Icons.logout_rounded,
              label: 'Logout',
              subtitle: 'Sign out of your account',
              color: cRed,
              onTap: _logout,
            ),

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _infoTile({
    required IconData icon,
    required String label,
    required String value,
  }) =>
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(children: [
          Icon(icon, color: cGreen, size: 20),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
              Text(label,
                  style: const TextStyle(
                      fontSize: 11,
                      color: cMuted,
                      fontWeight: FontWeight.w500)),
              const SizedBox(height: 3),
              Text(value,
                  style: const TextStyle(
                      fontSize: 14,
                      color: cText,
                      fontWeight: FontWeight.w600)),
            ]),
          ),
        ]),
      );
}

// ── Action Button ─────────────────────────────────────────
class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;
  const _ActionButton({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: cCard,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: color.withOpacity(0.25)),
          ),
          child: Row(children: [
            Container(
              width: 44, height: 44,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Text(label,
                    style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: color)),
                Text(subtitle,
                    style:
                        const TextStyle(fontSize: 12, color: cMuted)),
              ]),
            ),
            Icon(Icons.arrow_forward_ios_rounded, color: color, size: 16),
          ]),
        ),
      );
}
