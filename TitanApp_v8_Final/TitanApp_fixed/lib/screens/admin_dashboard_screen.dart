import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../utils/constants.dart';
import '../services/admin_service.dart';
import '../services/analytics_service.dart';



class _FeatureRow {
  final IconData icon;
  final String label, sub, key_;
  final bool locked;
  const _FeatureRow({
    required this.icon, required this.label, required this.sub,
    required this.key_, required this.locked,
  });
}

class _FeatureTile extends StatelessWidget {
  final IconData icon;
  final String label, sub;
  final bool locked;
  final ValueChanged<bool> onToggle;
  const _FeatureTile({
    required this.icon, required this.label, required this.sub,
    required this.locked, required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: cCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: locked ? cAmber.withOpacity(0.3) : cBorder,
        ),
      ),
      child: Row(children: [
        Container(
          width: 36, height: 36,
          decoration: BoxDecoration(
            color: locked
                ? cAmber.withOpacity(0.1)
                : cGreen.withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: locked ? cAmber : cGreen, size: 18),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(
                fontSize: 13, fontWeight: FontWeight.w700, color: cText)),
            Text(sub, style: const TextStyle(fontSize: 11, color: cText2)),
          ],
        )),
        Row(children: [
          Icon(
            locked ? Icons.lock_rounded : Icons.lock_open_rounded,
            color: locked ? cAmber : cMuted,
            size: 14,
          ),
          const SizedBox(width: 4),
          Switch(value: locked, onChanged: onToggle),
        ]),
      ]),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  TAB 5: ADS CONTROL
// ═══════════════════════════════════════════════════════

class _AdsTab extends StatefulWidget {
  const _AdsTab();
  @override
  State<_AdsTab> createState() => _AdsTabState();
}

class _AdsTabState extends State<_AdsTab> {
  AdminAdData _data = const AdminAdData();
  bool _loading = true;
  bool _saving = false;
  Timer? _refreshTimer;

  late TextEditingController _bannerCtrl, _interCtrl, _rewardCtrl;

  @override
  void initState() {
    super.initState();
    _bannerCtrl = TextEditingController();
    _interCtrl = TextEditingController();
    _rewardCtrl = TextEditingController();
    _load();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) => _load());
  }

  @override
  void dispose() {
    _bannerCtrl.dispose();
    _interCtrl.dispose();
    _rewardCtrl.dispose();
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final d = await AdminService.getAdData();
    if (mounted) {
      setState(() {
        _data = d;
        _bannerCtrl.text = d.bannerAdUnitId;
        _interCtrl.text = d.interstitialAdUnitId;
        _rewardCtrl.text = d.rewardedAdUnitId;
        _loading = false;
      });
    }
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    final updated = AdminAdData(
      adsEnabled: _data.adsEnabled,
      bannerEnabled: _data.bannerEnabled,
      interstitialEnabled: _data.interstitialEnabled,
      rewardedEnabled: _data.rewardedEnabled,
      bannerAdUnitId: _bannerCtrl.text.trim(),
      interstitialAdUnitId: _interCtrl.text.trim(),
      rewardedAdUnitId: _rewardCtrl.text.trim(),
      interstitialFrequency: _data.interstitialFrequency,
      testMode: _data.testMode,
    );
    await AdminService.setAdData(updated);
    await _load();
    if (mounted) setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    return _TabWrapper(
      title: 'AdMob / Ad Networks',
      subtitle: _data.adsEnabled ? '🟢 Ads Active' : '🔴 Ads Disabled',
      onRefresh: _load,
      saving: _saving,
      loading: _loading,
      child: Column(children: [
        // Master toggle
        _SwitchTile(
          icon: Icons.ad_units_rounded,
          label: 'Enable All Ads',
          sub: 'Master on/off switch',
          value: _data.adsEnabled,
          color: cGreen,
          onChanged: (v) => setState(() => _data = AdminAdData(
            adsEnabled: v, bannerEnabled: _data.bannerEnabled,
            interstitialEnabled: _data.interstitialEnabled,
            rewardedEnabled: _data.rewardedEnabled,
            bannerAdUnitId: _data.bannerAdUnitId,
            interstitialAdUnitId: _data.interstitialAdUnitId,
            rewardedAdUnitId: _data.rewardedAdUnitId,
            interstitialFrequency: _data.interstitialFrequency,
            testMode: _data.testMode,
          )),
        ),
        const SizedBox(height: 8),
        _SwitchTile(
          icon: Icons.view_headline_rounded,
          label: 'Banner Ads',
          sub: 'Bottom of screen banner',
          value: _data.bannerEnabled,
          color: cBlue,
          onChanged: (v) => setState(() => _data = AdminAdData(adsEnabled: _data.adsEnabled, bannerEnabled: v, interstitialEnabled: _data.interstitialEnabled, rewardedEnabled: _data.rewardedEnabled, bannerAdUnitId: _data.bannerAdUnitId, interstitialAdUnitId: _data.interstitialAdUnitId, rewardedAdUnitId: _data.rewardedAdUnitId, interstitialFrequency: _data.interstitialFrequency, testMode: _data.testMode)),
        ),
        const SizedBox(height: 8),
        _SwitchTile(
          icon: Icons.fullscreen_rounded,
          label: 'Interstitial Ads',
          sub: 'Full-screen between generations',
          value: _data.interstitialEnabled,
          color: cOrange,
          onChanged: (v) => setState(() => _data = AdminAdData(adsEnabled: _data.adsEnabled, bannerEnabled: _data.bannerEnabled, interstitialEnabled: v, rewardedEnabled: _data.rewardedEnabled, bannerAdUnitId: _data.bannerAdUnitId, interstitialAdUnitId: _data.interstitialAdUnitId, rewardedAdUnitId: _data.rewardedAdUnitId, interstitialFrequency: _data.interstitialFrequency, testMode: _data.testMode)),
        ),
        const SizedBox(height: 8),
        _SwitchTile(
          icon: Icons.card_giftcard_rounded,
          label: 'Rewarded Ads',
          sub: 'Watch ad for extra requests',
          value: _data.rewardedEnabled,
          color: cAmber,
          onChanged: (v) => setState(() => _data = AdminAdData(adsEnabled: _data.adsEnabled, bannerEnabled: _data.bannerEnabled, interstitialEnabled: _data.interstitialEnabled, rewardedEnabled: v, bannerAdUnitId: _data.bannerAdUnitId, interstitialAdUnitId: _data.interstitialAdUnitId, rewardedAdUnitId: _data.rewardedAdUnitId, interstitialFrequency: _data.interstitialFrequency, testMode: _data.testMode)),
        ),
        const SizedBox(height: 8),
        _SwitchTile(
          icon: Icons.bug_report_rounded,
          label: 'Test Mode',
          sub: 'Use test ad unit IDs (safe for testing)',
          value: _data.testMode,
          color: cPurple,
          onChanged: (v) => setState(() => _data = AdminAdData(adsEnabled: _data.adsEnabled, bannerEnabled: _data.bannerEnabled, interstitialEnabled: _data.interstitialEnabled, rewardedEnabled: _data.rewardedEnabled, bannerAdUnitId: _data.bannerAdUnitId, interstitialAdUnitId: _data.interstitialAdUnitId, rewardedAdUnitId: _data.rewardedAdUnitId, interstitialFrequency: _data.interstitialFrequency, testMode: v)),
        ),
        const SizedBox(height: 16),
        _AdminField(label: 'Banner Ad Unit ID', hint: 'ca-app-pub-xxx/xxx', controller: _bannerCtrl, icon: Icons.view_headline_rounded),
        const SizedBox(height: 10),
        _AdminField(label: 'Interstitial Ad Unit ID', hint: 'ca-app-pub-xxx/xxx', controller: _interCtrl, icon: Icons.fullscreen_rounded),
        const SizedBox(height: 10),
        _AdminField(label: 'Rewarded Ad Unit ID', hint: 'ca-app-pub-xxx/xxx', controller: _rewardCtrl, icon: Icons.card_giftcard_rounded),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: _SaveBtn(label: 'Save Ad Config', onTap: _save, saving: _saving),
        ),
      ]),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  TAB 6: USER ACCOUNTS AUDIT
// ═══════════════════════════════════════════════════════

class _UsersTab extends StatefulWidget {
  const _UsersTab();
  @override
  State<_UsersTab> createState() => _UsersTabState();
}

class _UsersTabState extends State<_UsersTab> {
  List<AdminUserRecord> _users = [];
  bool _loading = true;
  String _search = '';
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _load();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) => _load());
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final data = await AdminService.getUserAudit();
    if (mounted) setState(() { _users = data; _loading = false; });
  }

  List<AdminUserRecord> get _filtered {
    if (_search.isEmpty) return _users;
    final q = _search.toLowerCase();
    return _users.where((u) =>
      u.email.toLowerCase().contains(q) ||
      u.displayName.toLowerCase().contains(q)).toList();
  }

  @override
  Widget build(BuildContext context) {
    final totalUsers = _users.length;
    final activeToday = _users.where((u) {
      final diff = DateTime.now().difference(
        DateTime.fromMillisecondsSinceEpoch(u.lastActive));
      return diff.inHours < 24;
    }).length;

    return _TabWrapper(
      title: 'User Accounts',
      subtitle: '$totalUsers total · $activeToday active today',
      onRefresh: _load,
      loading: _loading,
      child: Column(children: [
        // Stats row
        if (_users.isNotEmpty) ...[
          Row(children: [
            Expanded(child: _StatBox(
              icon: Icons.people_rounded,
              label: 'Total Users',
              value: '$totalUsers',
              color: cGreen,
            )),
            const SizedBox(width: 8),
            Expanded(child: _StatBox(
              icon: Icons.today_rounded,
              label: 'Active Today',
              value: '$activeToday',
              color: cBlue,
            )),
            const SizedBox(width: 8),
            Expanded(child: _StatBox(
              icon: Icons.block_rounded,
              label: 'Banned',
              value: '${_users.where((u) => u.banned).length}',
              color: cRed,
            )),
          ]),
          const SizedBox(height: 12),
        ],

        // Search
        Container(
          margin: const EdgeInsets.only(bottom: 12),
          decoration: BoxDecoration(
            color: cCard, borderRadius: BorderRadius.circular(12),
            border: Border.all(color: cBorder),
          ),
          child: TextField(
            style: const TextStyle(color: cText, fontSize: 13),
            decoration: const InputDecoration(
              hintText: 'Search by email or name...',
              hintStyle: TextStyle(color: cMuted),
              prefixIcon: Icon(Icons.search_rounded, color: cMuted, size: 20),
              border: InputBorder.none,
              contentPadding: EdgeInsets.symmetric(vertical: 12),
            ),
            onChanged: (v) => setState(() => _search = v),
          ),
        ),

        if (_users.isEmpty && !_loading)
          Container(
            padding: const EdgeInsets.all(32),
            child: Column(children: [
              Icon(Icons.people_outline_rounded, color: cMuted, size: 52),
              const SizedBox(height: 14),
              const Text('No users yet',
                  style: TextStyle(color: cText2, fontSize: 15,
                      fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              const Text(
                'Users will appear here when they\nlog in to the app.',
                textAlign: TextAlign.center,
                style: TextStyle(color: cMuted, fontSize: 12),
              ),
            ]),
          )
        else
          ..._filtered.map((u) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _UserTile(
              user: u,
              onBan: () async {
                if (!u.banned) {
                  // Suspending: show dialog to enter reason
                  final reasonCtrl = TextEditingController();
                  final confirmed = await showDialog<bool>(
                    context: context,
                    builder: (_) => AlertDialog(
                      backgroundColor: cBg2,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16)),
                      title: const Text('Suspend Account',
                          style: TextStyle(
                              color: cText, fontWeight: FontWeight.w800)),
                      content: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Suspending: ${u.displayName.isNotEmpty ? u.displayName : u.email}',
                            style: const TextStyle(fontSize: 13, color: cText2),
                          ),
                          const SizedBox(height: 16),
                          const Text('Reason (optional):',
                              style: TextStyle(
                                  fontSize: 12,
                                  color: cMuted,
                                  fontWeight: FontWeight.w600)),
                          const SizedBox(height: 8),
                          TextField(
                            controller: reasonCtrl,
                            maxLines: 3,
                            style: const TextStyle(color: cText, fontSize: 13),
                            decoration: InputDecoration(
                              hintText: 'e.g. Violated terms of service...',
                              hintStyle: const TextStyle(
                                  color: cMuted, fontSize: 12),
                              filled: true,
                              fillColor: cSurface,
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide: const BorderSide(color: cBorder),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide: const BorderSide(color: cRed),
                              ),
                              contentPadding: const EdgeInsets.all(12),
                            ),
                          ),
                        ],
                      ),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context, false),
                          child: const Text('Cancel',
                              style: TextStyle(color: cMuted)),
                        ),
                        TextButton(
                          onPressed: () => Navigator.pop(context, true),
                          child: const Text('Suspend',
                              style: TextStyle(
                                  color: cRed,
                                  fontWeight: FontWeight.w700)),
                        ),
                      ],
                    ),
                  );
                  if (confirmed == true) {
                    await AdminService.banUser(
                      u.uid,
                      true,
                      reason: reasonCtrl.text.trim(),
                    );
                    _load();
                  }
                } else {
                  // Unsuspending: no dialog needed
                  await AdminService.banUser(u.uid, false);
                  _load();
                }
              },
            ),
          )),
      ]),
    );
  }
}

class _StatBox extends StatelessWidget {
  final IconData icon;
  final String label, value;
  final Color color;
  const _StatBox({required this.icon, required this.label,
      required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 90, // fixed equal height for all boxes
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.07),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.25)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(value, style: TextStyle(
                fontSize: 18, fontWeight: FontWeight.w900, color: color)),
          ),
          Text(label, style: const TextStyle(fontSize: 9, color: cMuted),
              textAlign: TextAlign.center, maxLines: 1, overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }
}

class _UserTile extends StatelessWidget {
  final AdminUserRecord user;
  final VoidCallback onBan;
  const _UserTile({required this.user, required this.onBan});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: user.banned ? cRed.withOpacity(0.06) : cCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: user.banned ? cRed.withOpacity(0.4) : cBorder,
        ),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          // Avatar
          Container(
            width: 42, height: 42,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: user.banned
                    ? [cRed, cRed.withOpacity(0.6)]
                    : [cGreen, cGreen2],
              ),
            ),
            child: Center(child: Text(user.initials,
                style: const TextStyle(fontSize: 15,
                    fontWeight: FontWeight.w800, color: Colors.white))),
          ),
          const SizedBox(width: 10),
          Expanded(child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Expanded(child: Text(
                  user.displayName.isNotEmpty ? user.displayName : 'No Name',
                  style: const TextStyle(fontSize: 13,
                      fontWeight: FontWeight.w700, color: cText),
                  overflow: TextOverflow.ellipsis,
                )),
                if (user.banned)
                  _Badge(label: 'BANNED', color: cRed),
              ]),
              Text(user.email,
                  style: const TextStyle(fontSize: 11, color: cGreen),
                  overflow: TextOverflow.ellipsis),
            ],
          )),
          _MiniBtn(
            icon: user.banned ? Icons.lock_open_rounded : Icons.block_rounded,
            color: cRed,
            onTap: onBan,
          ),
        ]),
        const SizedBox(height: 8),
        // Info row
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
          decoration: BoxDecoration(
            color: cBg2,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(children: [
            _InfoChip(icon: Icons.access_time_rounded,
                label: 'Last Active', value: user.lastActiveFormatted),
            const SizedBox(width: 12),
            _InfoChip(icon: Icons.mic_rounded,
                label: 'Requests', value: '${user.totalRequests}'),
            const SizedBox(width: 12),
            _InfoChip(icon: Icons.today_rounded,
                label: 'Today', value: '${user.todayRequests}'),
          ]),
        ),
        const SizedBox(height: 6),
        // UID row (copyable)
        GestureDetector(
          onTap: () {
            Clipboard.setData(ClipboardData(text: user.uid));
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
              content: Text('UID copied!'),
              duration: Duration(seconds: 1),
            ));
          },
          child: Row(children: [
            const Icon(Icons.fingerprint_rounded, color: cMuted, size: 13),
            const SizedBox(width: 4),
            Expanded(child: Text(
              'UID: ${user.uid}',
              style: const TextStyle(fontSize: 10, color: cMuted),
              overflow: TextOverflow.ellipsis,
            )),
            const Icon(Icons.copy_rounded, color: cMuted, size: 12),
          ]),
        ),
        // Suspend reason chip
        if (user.banned && user.suspendReason.isNotEmpty) ...[
          const SizedBox(height: 6),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: cRed.withOpacity(0.08),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: cRed.withOpacity(0.25)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.info_outline_rounded, color: cRed, size: 12),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    user.suspendReason,
                    style: const TextStyle(
                        fontSize: 11, color: cText2, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
        ],
      ]),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label, value;
  const _InfoChip({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Icon(icon, color: cGreen, size: 11),
        const SizedBox(width: 3),
        Text(label, style: const TextStyle(fontSize: 9, color: cMuted)),
      ]),
      Text(value, style: const TextStyle(
          fontSize: 12, fontWeight: FontWeight.w700, color: cText)),
    ]);
  }
}

class _Badge extends StatelessWidget {
  final String label;
  final Color color;
  const _Badge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(left: 6),
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Text(label,
          style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: color)),
    );
  }
}

class _MiniBtn extends StatelessWidget {
  final IconData icon;
  final Color color;
  final VoidCallback onTap;
  const _MiniBtn({required this.icon, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 32, height: 32,
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Icon(icon, color: color, size: 16),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  SHARED WIDGETS
// ═══════════════════════════════════════════════════════

class _TabWrapper extends StatelessWidget {
  final String title, subtitle;
  final VoidCallback onRefresh;
  final bool loading;
  final bool saving;
  final Widget child;
  final List<Widget>? actions;

  const _TabWrapper({
    required this.title,
    required this.subtitle,
    required this.onRefresh,
    required this.child,
    this.loading = false,
    this.saving = false,
    this.actions,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(children: [
      SingleChildScrollView(
        padding: const EdgeInsets.all(14),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          // Header
          Row(children: [
            Expanded(child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(
                    fontSize: 16, fontWeight: FontWeight.w800, color: cText)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 12, color: cText2)),
              ],
            )),
            if (actions != null) ...actions!,
            const SizedBox(width: 8),
            GestureDetector(
              onTap: onRefresh,
              child: Container(
                width: 36, height: 36,
                decoration: BoxDecoration(
                  color: cCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: cBorder),
                ),
                child: const Icon(Icons.refresh_rounded, color: cGreen, size: 18),
              ),
            ),
          ]),
          const SizedBox(height: 16),

          if (loading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(color: cGreen, strokeWidth: 2),
              ),
            )
          else
            child,

          const SizedBox(height: 30),
        ]),
      ),

      // Saving overlay
      if (saving)
        Positioned(
          top: 0, right: 0, left: 0,
          child: LinearProgressIndicator(
            backgroundColor: cBorder,
            color: cGreen,
            minHeight: 2,
          ),
        ),
    ]);
  }
}

class _AdminField extends StatelessWidget {
  final String label, hint;
  final TextEditingController controller;
  final IconData icon;
  final int maxLines;

  const _AdminField({
    required this.label,
    required this.hint,
    required this.controller,
    required this.icon,
    this.maxLines = 1,
  });

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Icon(icon, color: cGreen, size: 14),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(
            fontSize: 12, fontWeight: FontWeight.w700, color: cText2)),
      ]),
      const SizedBox(height: 6),
      Container(
        decoration: BoxDecoration(
          color: cCard,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: cBorder),
        ),
        child: TextField(
          controller: controller,
          maxLines: maxLines,
          style: const TextStyle(color: cText, fontSize: 13),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(color: cMuted, fontSize: 12),
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(
                horizontal: 12, vertical: 10),
          ),
        ),
      ),
    ]);
  }
}

class _CompactField extends StatelessWidget {
  final String label;
  final TextEditingController controller;
  final Color color;
  const _CompactField(
      {required this.label, required this.controller, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: TextStyle(
          fontSize: 11, fontWeight: FontWeight.w700, color: color)),
      const SizedBox(height: 4),
      Container(
        decoration: BoxDecoration(
          color: cCard,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: cBorder),
        ),
        child: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
          style: const TextStyle(color: cText, fontSize: 14,
              fontWeight: FontWeight.w700),
          decoration: const InputDecoration(
            border: InputBorder.none,
            contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 10),
          ),
        ),
      ),
    ]);
  }
}

class _SwitchTile extends StatelessWidget {
  final IconData icon;
  final String label, sub;
  final bool value;
  final Color color;
  final ValueChanged<bool> onChanged;
  const _SwitchTile({
    required this.icon, required this.label, required this.sub,
    required this.value, required this.color, required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: cCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: value ? color.withOpacity(0.3) : cBorder),
      ),
      child: Row(children: [
        Container(
          width: 34, height: 34,
          decoration: BoxDecoration(
            color: value ? color.withOpacity(0.12) : cBg2,
            borderRadius: BorderRadius.circular(9),
          ),
          child: Icon(icon, color: value ? color : cMuted, size: 18),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(
                fontSize: 13, fontWeight: FontWeight.w700, color: cText)),
            Text(sub, style: const TextStyle(fontSize: 11, color: cText2)),
          ],
        )),
        Switch(value: value, onChanged: onChanged),
      ]),
    );
  }
}

class _SaveBtn extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  final bool saving;
  const _SaveBtn({required this.label, required this.onTap, this.saving = false});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: saving ? null : onTap,
      child: Container(
        height: 46,
        decoration: BoxDecoration(
          gradient: saving ? null : kNeonGradient,
          color: saving ? cCard : null,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: saving
              ? const SizedBox(
                  width: 20, height: 20,
                  child: CircularProgressIndicator(
                      color: cGreen, strokeWidth: 2))
              : Text(label, style: const TextStyle(
                  fontSize: 14, fontWeight: FontWeight.w800,
                  color: Colors.white)),
        ),
      ),
    );
  }
}

class _ActionBtn extends StatelessWidget {
  final String label;
  final Color color;
  final VoidCallback onTap;
  const _ActionBtn(
      {required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Text(label, style: TextStyle(
            fontSize: 11, fontWeight: FontWeight.w700, color: color)),
      ),
    );
  }
}

// ── Data model for tabs ──────────────────────────────────
class _AdminTab {
  final IconData icon;
  final String label;
  const _AdminTab({required this.icon, required this.label});
}

// ═══════════════════════════════════════════════════════
//  ANALYTICS TAB — Full User Activity Dashboard
// ═══════════════════════════════════════════════════════

class _AnalyticsTab extends StatefulWidget {
  const _AnalyticsTab();
  @override
  State<_AnalyticsTab> createState() => _AnalyticsTabState();
}

class _AnalyticsTabState extends State<_AnalyticsTab> {
  List<UserAnalyticsSummary> _users = [];
  bool _loading = true;
  String _search = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final data = await AnalyticsService.getAllUsersSummary();
    if (mounted) setState(() { _users = data; _loading = false; });
  }

  List<UserAnalyticsSummary> get _filtered {
    if (_search.isEmpty) return _users;
    final q = _search.toLowerCase();
    return _users.where((u) =>
      u.email.toLowerCase().contains(q) ||
      u.displayName.toLowerCase().contains(q)).toList();
  }

  // ── Totals ───────────────────────────────────────────
  int get _totalGenerations => _users.fold(0, (s, u) => s + u.totalRequests);
  int get _totalChars       => _users.fold(0, (s, u) => s + u.totalChars);
  int get _activeToday {
    final today = DateTime.now();
    final todayKey = '${today.year}-${today.month.toString().padLeft(2,'0')}-${today.day.toString().padLeft(2,'0')}';
    return _users.where((u) {
      final diff = DateTime.now().difference(DateTime.fromMillisecondsSinceEpoch(u.lastActive));
      return diff.inHours < 24;
    }).length;
  }

  @override
  Widget build(BuildContext context) {
    return _TabWrapper(
      title: 'User Analytics',
      subtitle: '${_users.length} users · $_totalGenerations total generations',
      onRefresh: _load,
      loading: _loading,
      child: Column(children: [
        // ── Overview Stats ─────────────────────────────
        if (_users.isNotEmpty) ...[
          Row(children: [
            Expanded(child: _StatBox(icon: Icons.people_rounded,        label: 'Total Users',    value: '${_users.length}',      color: cGreen)),
            const SizedBox(width: 8),
            Expanded(child: _StatBox(icon: Icons.mic_rounded,           label: 'Generations',    value: '$_totalGenerations',    color: cBlue)),
            const SizedBox(width: 8),
            Expanded(child: _StatBox(icon: Icons.today_rounded,         label: 'Active Today',   value: '$_activeToday',         color: cAmber)),
          ]),
          const SizedBox(height: 8),
          Row(children: [
            Expanded(child: _StatBox(icon: Icons.text_fields_rounded,   label: 'Total Chars',    value: _fmtNum(_totalChars),    color: cPurple)),
            const SizedBox(width: 8),
            Expanded(child: _StatBox(icon: Icons.emoji_events_rounded,  label: 'Top User Gens',  value: _users.isNotEmpty ? '${_users.first.totalRequests}' : '0', color: cOrange)),
            const SizedBox(width: 8),
            Expanded(child: _StatBox(icon: Icons.block_rounded,         label: 'Banned',         value: '${_users.where((u) => u.banned).length}', color: cRed)),
          ]),
          const SizedBox(height: 14),
        ],

        // ── Search ─────────────────────────────────────
        Container(
          margin: const EdgeInsets.only(bottom: 12),
          decoration: BoxDecoration(
            color: cCard, borderRadius: BorderRadius.circular(12),
            border: Border.all(color: cBorder),
          ),
          child: TextField(
            style: const TextStyle(color: cText, fontSize: 13),
            decoration: const InputDecoration(
              hintText: 'Search by name or email...',
              hintStyle: TextStyle(color: cMuted),
              prefixIcon: Icon(Icons.search_rounded, color: cMuted, size: 20),
              border: InputBorder.none,
              contentPadding: EdgeInsets.symmetric(vertical: 12),
            ),
            onChanged: (v) => setState(() => _search = v),
          ),
        ),

        if (_users.isEmpty && !_loading)
          Center(child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(children: [
              Icon(Icons.analytics_outlined, color: cMuted, size: 52),
              const SizedBox(height: 14),
              const Text('No data yet', style: TextStyle(color: cText2, fontSize: 15, fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              const Text('User activity will appear here\nafter first generation.', textAlign: TextAlign.center, style: TextStyle(color: cMuted, fontSize: 12)),
            ]),
          ))
        else
          ..._filtered.map((u) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: _UserAnalyticsTile(user: u),
          )),
      ]),
    );
  }

  String _fmtNum(int n) {
    if (n >= 1000000) return '${(n / 1000000).toStringAsFixed(1)}M';
    if (n >= 1000)    return '${(n / 1000).toStringAsFixed(1)}K';
    return '$n';
  }
}

// ═══════════════════════════════════════════════════════
//  USER ANALYTICS TILE — tapping opens detail view
// ═══════════════════════════════════════════════════════

class _UserAnalyticsTile extends StatelessWidget {
  final UserAnalyticsSummary user;
  const _UserAnalyticsTile({required this.user});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.push(context, MaterialPageRoute(
        builder: (_) => _UserDetailScreen(user: user),
      )),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: cCard,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: user.banned ? cRed.withOpacity(0.4) : cBorder),
        ),
        child: Row(children: [
          // Avatar
          Container(
            width: 46, height: 46,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: user.banned ? [cRed, cRed.withOpacity(0.6)] : [cGreen, cGreen2],
              ),
            ),
            child: Center(child: Text(user.initials,
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Colors.white))),
          ),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Expanded(child: Text(
                user.displayName.isNotEmpty ? user.displayName : 'No Name',
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cText),
                overflow: TextOverflow.ellipsis,
              )),
              if (user.banned) Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(color: cRed.withOpacity(0.15), borderRadius: BorderRadius.circular(6), border: Border.all(color: cRed.withOpacity(0.4))),
                child: const Text('BANNED', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: cRed)),
              ),
            ]),
            Text(user.email, style: const TextStyle(fontSize: 11, color: cGreen), overflow: TextOverflow.ellipsis),
            const SizedBox(height: 6),
            Row(children: [
              _MicroChip(icon: Icons.mic_rounded,      label: '${user.totalRequests} gens',   color: cBlue),
              const SizedBox(width: 6),
              _MicroChip(icon: Icons.today_rounded,    label: '${user.todayRequests} today',  color: cAmber),
              const SizedBox(width: 6),
              _MicroChip(icon: Icons.access_time_rounded, label: user.lastActiveFormatted, color: cMuted),
            ]),
          ])),
          const SizedBox(width: 8),
          const Icon(Icons.chevron_right_rounded, color: cMuted, size: 20),
        ]),
      ),
    );
  }
}

class _MicroChip extends StatelessWidget {
  final IconData icon; final String label; final Color color;
  const _MicroChip({required this.icon, required this.label, required this.color});
  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
    Icon(icon, color: color, size: 11),
    const SizedBox(width: 3),
    Text(label, style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.w600)),
  ]);
}

// ═══════════════════════════════════════════════════════
//  USER DETAIL SCREEN — full per-user analytics
// ═══════════════════════════════════════════════════════

class _UserDetailScreen extends StatefulWidget {
  final UserAnalyticsSummary user;
  const _UserDetailScreen({required this.user});
  @override
  State<_UserDetailScreen> createState() => _UserDetailScreenState();
}

class _UserDetailScreenState extends State<_UserDetailScreen> {
  List<TtsLog> _logs = [];
  bool _loading = true;
  _DateFilter _filter = _DateFilter.today;
  DateTimeRange? _customRange;

  @override
  void initState() {
    super.initState();
    _loadLogs();
  }

  DateTime get _fromDate {
    final now = DateTime.now();
    switch (_filter) {
      case _DateFilter.today:   return DateTime(now.year, now.month, now.day);
      case _DateFilter.week:    return now.subtract(const Duration(days: 7));
      case _DateFilter.month:   return now.subtract(const Duration(days: 30));
      case _DateFilter.three:   return now.subtract(const Duration(days: 90));
      case _DateFilter.six:     return now.subtract(const Duration(days: 180));
      case _DateFilter.all:     return DateTime(2020);
      case _DateFilter.custom:  return _customRange?.start ?? DateTime(2020);
    }
  }

  DateTime get _toDate {
    if (_filter == _DateFilter.custom && _customRange != null) {
      return _customRange!.end.add(const Duration(days: 1));
    }
    return DateTime.now().add(const Duration(days: 1));
  }

  Future<void> _loadLogs() async {
    setState(() => _loading = true);
    final logs = await AnalyticsService.getUserLogs(
      widget.user.uid,
      from: _fromDate,
      to:   _toDate,
    );
    if (mounted) setState(() { _logs = logs; _loading = false; });
  }

  Future<void> _pickCustomRange() async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2024),
      lastDate:  DateTime.now(),
      builder:   (ctx, child) => Theme(
        data: Theme.of(ctx).copyWith(
          colorScheme: ColorScheme.dark(primary: cGreen, surface: cBg2),
        ),
        child: child!,
      ),
    );
    if (picked != null) {
      setState(() { _customRange = picked; _filter = _DateFilter.custom; });
      _loadLogs();
    }
  }

  // ── Stats for filtered logs ──────────────────────────
  int get _totalGens     => _logs.length;
  int get _successGens   => _logs.where((l) => l.success).length;
  int get _totalChars    => _logs.fold(0, (s, l) => s + l.charCount);
  int get _avgDuration   => _logs.isEmpty ? 0 : _logs.fold(0, (s, l) => s + l.durationMs) ~/ _logs.length;

  Map<String, int> get _charUsage {
    final map = <String, int>{};
    for (final l in _logs) {
      if (l.character.isEmpty) continue;
      map[l.character] = (map[l.character] ?? 0) + 1;
    }
    final sorted = Map.fromEntries(map.entries.toList()..sort((a, b) => b.value.compareTo(a.value)));
    return sorted;
  }

  Map<String, int> get _langUsage {
    final map = <String, int>{};
    for (final l in _logs) {
      if (l.language.isEmpty) continue;
      map[l.language] = (map[l.language] ?? 0) + 1;
    }
    return map;
  }

  Map<String, int> get _emotionUsage {
    final map = <String, int>{};
    for (final l in _logs) {
      if (l.emotion.isEmpty) continue;
      map[l.emotion] = (map[l.emotion] ?? 0) + 1;
    }
    return map;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cBg,
      appBar: AppBar(
        backgroundColor: cBg2,
        foregroundColor: cText,
        title: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(widget.user.displayName.isNotEmpty ? widget.user.displayName : 'User',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: cText)),
          Text(widget.user.email, style: const TextStyle(fontSize: 11, color: cGreen)),
        ]),
      ),
      body: Column(children: [
        // ── Filter chips ──────────────────────────────
        Container(
          color: cBg2,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(children: [
              ..._DateFilter.values.where((f) => f != _DateFilter.custom).map((f) =>
                Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: GestureDetector(
                    onTap: () { setState(() => _filter = f); _loadLogs(); },
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                      decoration: BoxDecoration(
                        color: _filter == f ? cGreen : cCard,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: _filter == f ? cGreen : cBorder),
                      ),
                      child: Text(_filterLabel(f),
                          style: TextStyle(
                            fontSize: 12, fontWeight: FontWeight.w700,
                            color: _filter == f ? Colors.black : cText2,
                          )),
                    ),
                  ),
                ),
              ),
              GestureDetector(
                onTap: _pickCustomRange,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                  decoration: BoxDecoration(
                    color: _filter == _DateFilter.custom ? cGreen : cCard,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _filter == _DateFilter.custom ? cGreen : cBorder),
                  ),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    Icon(Icons.date_range_rounded, size: 14,
                        color: _filter == _DateFilter.custom ? Colors.black : cText2),
                    const SizedBox(width: 4),
                    Text(_filter == _DateFilter.custom && _customRange != null
                        ? '${_customRange!.start.day}/${_customRange!.start.month} – ${_customRange!.end.day}/${_customRange!.end.month}'
                        : 'Custom',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700,
                            color: _filter == _DateFilter.custom ? Colors.black : cText2)),
                  ]),
                ),
              ),
            ]),
          ),
        ),

        // ── Body ─────────────────────────────────────
        Expanded(child: _loading
          ? const Center(child: CircularProgressIndicator(color: cGreen, strokeWidth: 2))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(14),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [

                // ── Summary stats ──────────────────────
                Row(children: [
                  Expanded(child: _StatBox(icon: Icons.mic_rounded,           label: 'Generations',  value: _totalGens > 0 ? '$_totalGens' : '${widget.user.totalRequests}', color: cGreen)),
                  const SizedBox(width: 8),
                  Expanded(child: _StatBox(icon: Icons.check_circle_rounded,  label: 'Success',      value: _totalGens > 0 ? '$_successGens' : '${widget.user.totalRequests}', color: cBlue)),
                  const SizedBox(width: 8),
                  Expanded(child: _StatBox(icon: Icons.text_fields_rounded,   label: 'Chars',        value: _fmtNum(_totalGens > 0 ? _totalChars : widget.user.totalChars), color: cAmber)),
                ]),
                const SizedBox(height: 8),
                Row(children: [
                  Expanded(child: _StatBox(icon: Icons.timer_rounded,         label: 'Avg Speed',    value: '${(_avgDuration/1000).toStringAsFixed(1)}s', color: cPurple)),
                  const SizedBox(width: 8),
                  Expanded(child: _StatBox(icon: Icons.calendar_today_rounded, label: 'Member Since', value: widget.user.memberSince,         color: cOrange)),
                  const SizedBox(width: 8),
                  Expanded(child: _StatBox(icon: Icons.access_time_rounded,   label: 'Last Active',  value: widget.user.lastActiveFormatted, color: cMuted)),
                ]),

                const SizedBox(height: 18),

                // ── Character usage ────────────────────
                if (_charUsage.isNotEmpty) ...[
                  _SectionHeader(icon: Icons.theater_comedy_rounded, label: 'Characters Used'),
                  const SizedBox(height: 8),
                  Wrap(spacing: 8, runSpacing: 8, children: _charUsage.entries.take(10).map((e) =>
                    _UsageBadge(label: e.key, count: e.value, total: _totalGens, color: cGreen),
                  ).toList()),
                  const SizedBox(height: 16),
                ],

                // ── Language usage ─────────────────────
                if (_langUsage.isNotEmpty) ...[
                  _SectionHeader(icon: Icons.language_rounded, label: 'Languages Used'),
                  const SizedBox(height: 8),
                  Wrap(spacing: 8, runSpacing: 8, children: _langUsage.entries.map((e) =>
                    _UsageBadge(label: e.key, count: e.value, total: _totalGens, color: cBlue),
                  ).toList()),
                  const SizedBox(height: 16),
                ],

                // ── Emotion usage ──────────────────────
                if (_emotionUsage.isNotEmpty) ...[
                  _SectionHeader(icon: Icons.mood_rounded, label: 'Emotions Used'),
                  const SizedBox(height: 8),
                  Wrap(spacing: 8, runSpacing: 8, children: _emotionUsage.entries.map((e) =>
                    _UsageBadge(label: e.key, count: e.value, total: _totalGens, color: cAmber),
                  ).toList()),
                  const SizedBox(height: 16),
                ],

                // ── Generation log ─────────────────────
                _SectionHeader(icon: Icons.history_rounded, label: 'Generation History (${_logs.length})'),
                const SizedBox(height: 8),

                if (_logs.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(color: cCard, borderRadius: BorderRadius.circular(14), border: Border.all(color: cBorder)),
                    child: const Center(child: Text('No generations in this period', style: TextStyle(color: cMuted, fontSize: 13))),
                  )
                else
                  ..._logs.map((log) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: _LogTile(log: log),
                  )),

                const SizedBox(height: 30),
              ]),
            ),
        ),
      ]),
    );
  }

  String _filterLabel(_DateFilter f) {
    switch (f) {
      case _DateFilter.today:  return 'Today';
      case _DateFilter.week:   return '7 Days';
      case _DateFilter.month:  return '1 Month';
      case _DateFilter.three:  return '3 Months';
      case _DateFilter.six:    return '6 Months';
      case _DateFilter.all:    return 'All Time';
      case _DateFilter.custom: return 'Custom';
    }
  }

  String _fmtNum(int n) {
    if (n >= 1000000) return '${(n / 1000000).toStringAsFixed(1)}M';
    if (n >= 1000)    return '${(n / 1000).toStringAsFixed(1)}K';
    return '$n';
  }
}

enum _DateFilter { today, week, month, three, six, all, custom }

// ─────────────────────────────────────────────────────
//  Section Header
// ─────────────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  final IconData icon; final String label;
  const _SectionHeader({required this.icon, required this.label});
  @override
  Widget build(BuildContext context) => Row(children: [
    Icon(icon, color: cGreen, size: 16),
    const SizedBox(width: 8),
    Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: cText)),
  ]);
}

// ─────────────────────────────────────────────────────
//  Usage Badge  (character / language / emotion)
// ─────────────────────────────────────────────────────

class _UsageBadge extends StatelessWidget {
  final String label; final int count; final int total; final Color color;
  const _UsageBadge({required this.label, required this.count, required this.total, required this.color});

  @override
  Widget build(BuildContext context) {
    final pct = total > 0 ? (count / total * 100).round() : 0;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: color)),
        const SizedBox(width: 6),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(color: color.withOpacity(0.2), borderRadius: BorderRadius.circular(10)),
          child: Text('$count ($pct%)', style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.w800)),
        ),
      ]),
    );
  }
}

// ─────────────────────────────────────────────────────
//  Log Tile — single generation entry
// ─────────────────────────────────────────────────────

class _LogTile extends StatefulWidget {
  final TtsLog log;
  const _LogTile({required this.log});
  @override
  State<_LogTile> createState() => _LogTileState();
}

class _LogTileState extends State<_LogTile> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final log = widget.log;
    return GestureDetector(
      onTap: () => setState(() => _expanded = !_expanded),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: log.success ? cCard : cRed.withOpacity(0.06),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: log.success ? cBorder : cRed.withOpacity(0.3)),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          // ── Header row ──────────────────────────────
          Row(children: [
            Icon(log.success ? Icons.check_circle_rounded : Icons.error_rounded,
                color: log.success ? cGreen : cRed, size: 16),
            const SizedBox(width: 8),
            Expanded(child: Text(
              log.character.isNotEmpty ? '${log.character} · ${log.language}' : log.language,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cText),
            )),
            Text(log.durationFormatted, style: const TextStyle(fontSize: 11, color: cMuted)),
            const SizedBox(width: 8),
            Icon(_expanded ? Icons.expand_less_rounded : Icons.expand_more_rounded, color: cMuted, size: 18),
          ]),
          const SizedBox(height: 6),

          // ── Quick chips ──────────────────────────────
          Row(children: [
            if (log.emotion.isNotEmpty) _MicroChip(icon: Icons.mood_rounded,          label: log.emotion,             color: cAmber),
            if (log.emotion.isNotEmpty) const SizedBox(width: 6),
            _MicroChip(icon: Icons.text_fields_rounded,  label: '${log.charCount} chars', color: cBlue),
            const SizedBox(width: 6),
            _MicroChip(icon: Icons.access_time_rounded,  label: log.timeFormatted,        color: cMuted),
          ]),

          // ── Expanded detail ──────────────────────────
          if (_expanded) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(color: cBg2, borderRadius: BorderRadius.circular(10)),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                // Text preview
                if (log.text.isNotEmpty) ...[
                  const Text('Text:', style: TextStyle(fontSize: 11, color: cMuted, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 4),
                  Text(log.text, style: const TextStyle(fontSize: 12, color: cText, height: 1.4)),
                  const SizedBox(height: 10),
                ],
                // Settings row
                Wrap(spacing: 8, runSpacing: 6, children: [
                  if (log.preset.isNotEmpty) _DetailChip(label: 'Preset: ${log.preset}'),
                  _DetailChip(label: 'Speed: ${log.speedPct}%'),
                  _DetailChip(label: 'Pitch: ${log.pitchVal}'),
                  if (log.hdVoice)        _DetailChip(label: '✦ HD Voice',        color: cAmber),
                  if (log.ssmlMode)       _DetailChip(label: '✦ SSML',            color: cBlue),
                  if (log.useBreaths)     _DetailChip(label: '✦ Breathing',       color: cGreen),
                  if (log.adaptivePacing) _DetailChip(label: '✦ Adaptive Pacing', color: cPurple),
                ]),
              ]),
            ),
          ],
        ]),
      ),
    );
  }
}

class _DetailChip extends StatelessWidget {
  final String label; final Color? color;
  const _DetailChip({required this.label, this.color});
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    decoration: BoxDecoration(
      color: (color ?? cMuted).withOpacity(0.1),
      borderRadius: BorderRadius.circular(6),
      border: Border.all(color: (color ?? cMuted).withOpacity(0.3)),
    ),
    child: Text(label, style: TextStyle(fontSize: 10, color: color ?? cText2, fontWeight: FontWeight.w600)),
  );
}
