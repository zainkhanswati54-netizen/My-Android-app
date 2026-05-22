import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/auth_service.dart';
import '../services/account_service.dart';
import '../utils/constants.dart';
import 'login_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  User? get _user => FirebaseAuth.instance.currentUser;
  List<SavedAccount> _savedAccounts = [];

  @override
  void initState() {
    super.initState();
    _loadAccounts();
    if (_user != null) {
      AccountService.saveCurrentUser(_user!);
    }
  }

  Future<void> _loadAccounts() async {
    final accounts = await AccountService.loadAll();
    if (mounted) setState(() => _savedAccounts = accounts);
  }

  String _getInitials(String? name, String? email) {
    return SavedAccount.buildInitials(name, email);
  }

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

  Future<void> _switchAccount() async {
    final others = _savedAccounts
        .where((a) => a.uid != (_user?.uid ?? ''))
        .toList();

    await showModalBottomSheet(
      context: context,
      backgroundColor: cCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (ctx) => _AccountSwitcherSheet(
        currentUser: _user,
        savedAccounts: others,
        onSwitchToSaved: (account) async {
          Navigator.pop(ctx);
          await AuthService.signOut();
          if (!mounted) return;
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(
              builder: (_) => LoginScreen(prefillEmail: account.email),
            ),
            (route) => false,
          );
        },
        onAddNew: () async {
          Navigator.pop(ctx);
          await AuthService.signOut();
          if (!mounted) return;
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(builder: (_) => const LoginScreen()),
            (route) => false,
          );
        },
        onRemoveAccount: (account) async {
          await AccountService.removeAccount(account.uid);
          await _loadAccounts();
        },
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
    final otherAccounts = _savedAccounts.where((a) => a.uid != _user?.uid).toList();

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

            // Avatar
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

            // Badge
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

            // Info card
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

            // Saved accounts preview (only if others exist)
            if (otherAccounts.isNotEmpty) ...[
              GestureDetector(
                onTap: _switchAccount,
                child: Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: cCard,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: cGreen.withOpacity(0.2)),
                  ),
                  child: Row(children: [
                    const Icon(Icons.people_alt_rounded, color: cGreen, size: 18),
                    const SizedBox(width: 10),
                    const Text('Saved Accounts',
                        style: TextStyle(
                            fontSize: 13, fontWeight: FontWeight.w700, color: cText)),
                    const Spacer(),
                    ...otherAccounts.take(3).map((a) => Container(
                      width: 28, height: 28,
                      margin: const EdgeInsets.only(right: 4),
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: LinearGradient(colors: [cGreen, cGreen2]),
                      ),
                      child: Center(
                        child: Text(a.initials,
                            style: const TextStyle(
                                fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white)),
                      ),
                    )),
                    const SizedBox(width: 4),
                    const Icon(Icons.arrow_forward_ios_rounded, color: cMuted, size: 14),
                  ]),
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Switch Account button
            _ActionButton(
              icon: Icons.switch_account_rounded,
              label: 'Switch Account',
              subtitle: otherAccounts.isNotEmpty
                  ? '${otherAccounts.length} other account(s) saved'
                  : 'Login with a different account',
              color: cGreen,
              onTap: _switchAccount,
            ),

            const SizedBox(height: 12),

            // Logout
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

// ── Account Switcher Bottom Sheet ─────────────────────────
class _AccountSwitcherSheet extends StatelessWidget {
  final User? currentUser;
  final List<SavedAccount> savedAccounts;
  final void Function(SavedAccount) onSwitchToSaved;
  final VoidCallback onAddNew;
  final void Function(SavedAccount) onRemoveAccount;

  const _AccountSwitcherSheet({
    required this.currentUser,
    required this.savedAccounts,
    required this.onSwitchToSaved,
    required this.onAddNew,
    required this.onRemoveAccount,
  });

  @override
  Widget build(BuildContext context) {
    final currentName = currentUser?.displayName ?? '';
    final currentEmail = currentUser?.email ?? '';
    final currentInitials = SavedAccount.buildInitials(currentName, currentEmail);

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40, height: 4,
              decoration: BoxDecoration(
                color: cBorder,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text('Switch Account',
              style: TextStyle(
                  fontSize: 18, fontWeight: FontWeight.w800, color: cText)),
          const SizedBox(height: 4),
          const Text('Select an account or add a new one',
              style: TextStyle(fontSize: 13, color: cMuted)),
          const SizedBox(height: 20),

          // Current account (active)
          _AccountTile(
            initials: currentInitials,
            name: currentName.isNotEmpty
                ? currentName
                : currentEmail.split('@').first,
            email: currentEmail,
            isActive: true,
            onTap: () => Navigator.pop(context),
            onRemove: null,
          ),

          // Other saved accounts
          ...savedAccounts.map((acc) => Padding(
            padding: const EdgeInsets.only(top: 10),
            child: _AccountTile(
              initials: acc.initials,
              name: acc.displayName.isNotEmpty
                  ? acc.displayName
                  : acc.email.split('@').first,
              email: acc.email,
              isActive: false,
              onTap: () => onSwitchToSaved(acc),
              onRemove: () => onRemoveAccount(acc),
            ),
          )),

          const SizedBox(height: 16),
          const Divider(color: cBorder),
          const SizedBox(height: 8),

          // Add new account
          GestureDetector(
            onTap: onAddNew,
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: cGreen.withOpacity(0.08),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: cGreen.withOpacity(0.25)),
              ),
              child: const Row(children: [
                Icon(Icons.add_circle_outline_rounded, color: cGreen, size: 22),
                SizedBox(width: 14),
                Text('Add another account',
                    style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: cGreen)),
              ]),
            ),
          ),
        ],
      ),
    );
  }
}

class _AccountTile extends StatelessWidget {
  final String initials;
  final String name;
  final String email;
  final bool isActive;
  final VoidCallback onTap;
  final VoidCallback? onRemove;

  const _AccountTile({
    required this.initials,
    required this.name,
    required this.email,
    required this.isActive,
    required this.onTap,
    this.onRemove,
  });

  @override
  Widget build(BuildContext context) => GestureDetector(
    onTap: onTap,
    child: Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isActive ? cGreen.withOpacity(0.08) : cCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isActive ? cGreen.withOpacity(0.4) : cBorder,
        ),
      ),
      child: Row(children: [
        Container(
          width: 46, height: 46,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              colors: isActive
                  ? [cGreen, cGreen2]
                  : [cMuted.withOpacity(0.4), cMuted.withOpacity(0.2)],
            ),
          ),
          child: Center(
            child: Text(initials,
                style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: Colors.white)),
          ),
        ),
        const SizedBox(width: 14),
        Expanded(child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(name,
                style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: isActive ? cGreen : cText)),
            const SizedBox(height: 3),
            Text(email,
                style: const TextStyle(fontSize: 12, color: cMuted)),
          ],
        )),
        if (isActive)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: cGreen.withOpacity(0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text('Active',
                style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: cGreen)),
          )
        else if (onRemove != null)
          GestureDetector(
            onTap: onRemove,
            child: const Padding(
              padding: EdgeInsets.all(6),
              child: Icon(Icons.close_rounded, color: cMuted, size: 18),
            ),
          ),
      ]),
    ),
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
