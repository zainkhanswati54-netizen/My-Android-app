import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../services/account_manager.dart';
import '../utils/constants.dart';
import 'login_screen.dart';
import 'studio_screen.dart';

class AccountSwitchScreen extends StatefulWidget {
  final String currentUid;
  const AccountSwitchScreen({super.key, required this.currentUid});
  @override
  State<AccountSwitchScreen> createState() => _AccountSwitchScreenState();
}

class _AccountSwitchScreenState extends State<AccountSwitchScreen> {
  List<SavedAccount> _accounts = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final accounts = await AccountManager.loadAccounts();
    setState(() {
      _accounts = accounts;
      _loading = false;
    });
  }

  // ── Switch to saved account (re-login required) ───────────
  Future<void> _switchTo(SavedAccount account) async {
    await AuthService.signOut();
    if (!mounted) return;
    // Pre-fill email on login screen
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (_) => LoginScreen(prefillEmail: account.email),
      ),
      (route) => false,
    );
  }

  // ── Add new account ───────────────────────────────────────
  Future<void> _addNew() async {
    await AuthService.signOut();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  // ── Remove saved account ──────────────────────────────────
  Future<void> _remove(SavedAccount account) async {
    await AccountManager.removeAccount(account.uid);
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cBg,
      appBar: AppBar(
        backgroundColor: cBg2,
        title: const Text('Switch Account',
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
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: cGreen))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                const SizedBox(height: 8),

                // ── Saved accounts ────────────────────────────
                if (_accounts.isNotEmpty) ...[
                  const Text('Saved Accounts',
                      style: TextStyle(
                          fontSize: 13,
                          color: cMuted,
                          fontWeight: FontWeight.w600)),
                  const SizedBox(height: 12),

                  ..._accounts.map((acc) {
                    final isCurrent = acc.uid == widget.currentUid;
                    return Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      decoration: BoxDecoration(
                        color: cCard,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: isCurrent
                              ? cGreen.withOpacity(0.5)
                              : cBorder,
                        ),
                      ),
                      child: ListTile(
                        contentPadding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 6),
                        leading: Container(
                          width: 46, height: 46,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              colors: isCurrent
                                  ? [cGreen, cGreen2]
                                  : [cMuted, cMuted2],
                            ),
                          ),
                          child: Center(
                            child: Text(acc.initials,
                                style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w800,
                                    color: Colors.white)),
                          ),
                        ),
                        title: Row(children: [
                          Text(acc.displayName,
                              style: const TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w700,
                                  color: cText)),
                          if (isCurrent) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: cGreen.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(100),
                              ),
                              child: const Text('Active',
                                  style: TextStyle(
                                      fontSize: 10,
                                      color: cGreen,
                                      fontWeight: FontWeight.w700)),
                            ),
                          ],
                        ]),
                        subtitle: Text(acc.email,
                            style: const TextStyle(
                                fontSize: 12, color: cMuted)),
                        trailing: isCurrent
                            ? const Icon(Icons.check_circle_rounded,
                                color: cGreen)
                            : Row(mainAxisSize: MainAxisSize.min, children: [
                                IconButton(
                                  icon: const Icon(Icons.login_rounded,
                                      color: cGreen, size: 22),
                                  onPressed: () => _switchTo(acc),
                                  tooltip: 'Switch',
                                ),
                                IconButton(
                                  icon: Icon(Icons.close_rounded,
                                      color: cMuted.withOpacity(0.6),
                                      size: 20),
                                  onPressed: () => _remove(acc),
                                  tooltip: 'Remove',
                                ),
                              ]),
                      ),
                    );
                  }),

                  const SizedBox(height: 20),
                ],

                // ── Add new account ───────────────────────────
                GestureDetector(
                  onTap: _addNew,
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: cCard,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                          color: cGreen.withOpacity(0.3),
                          style: BorderStyle.solid),
                    ),
                    child: Row(children: [
                      Container(
                        width: 46, height: 46,
                        decoration: BoxDecoration(
                          color: cGreen.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.add_rounded,
                            color: cGreen, size: 26),
                      ),
                      const SizedBox(width: 14),
                      const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                        Text('Add Another Account',
                            style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w700,
                                color: cGreen)),
                        Text('Login with a different email',
                            style:
                                TextStyle(fontSize: 12, color: cMuted)),
                      ]),
                    ]),
                  ),
                ),

                const SizedBox(height: 40),
              ],
            ),
    );
  }
}
