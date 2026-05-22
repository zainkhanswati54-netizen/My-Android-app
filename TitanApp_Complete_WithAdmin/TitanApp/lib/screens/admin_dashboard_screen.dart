import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../utils/constants.dart';
import '../services/admin_service.dart';

// ═══════════════════════════════════════════════════════
//  TITAN ADMIN DASHBOARD v1.0
//  Access: Settings → secret tap sequence → PIN entry
//  Features: Character Control, Maintenance, Limits,
//            Premium Lock, Ads, User Audit, Abuse Prevention
// ═══════════════════════════════════════════════════════

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen>
    with SingleTickerProviderStateMixin {
  bool _unlocked = false;
  int _selectedTab = 0;

  late TabController _tabController;

  final List<_AdminTab> _tabs = const [
    _AdminTab(icon: Icons.theater_comedy_rounded,   label: 'Characters'),
    _AdminTab(icon: Icons.build_circle_rounded,     label: 'Maintenance'),
    _AdminTab(icon: Icons.tune_rounded,             label: 'Limits'),
    _AdminTab(icon: Icons.diamond_rounded,          label: 'Premium'),
    _AdminTab(icon: Icons.ad_units_rounded,         label: 'Ads'),
    _AdminTab(icon: Icons.people_rounded,           label: 'Users'),
    _AdminTab(icon: Icons.shield_rounded,           label: 'Abuse'),
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        setState(() => _selectedTab = _tabController.index);
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_unlocked) {
      return _PinScreen(onUnlocked: () => setState(() => _unlocked = true));
    }
    return _DashboardBody(
      tabs: _tabs,
      tabController: _tabController,
      selectedTab: _selectedTab,
    );
  }
}

// ═══════════════════════════════════════════════════════
//  PIN SCREEN
// ═══════════════════════════════════════════════════════

class _PinScreen extends StatefulWidget {
  final VoidCallback onUnlocked;
  const _PinScreen({required this.onUnlocked});

  @override
  State<_PinScreen> createState() => _PinScreenState();
}

class _PinScreenState extends State<_PinScreen>
    with SingleTickerProviderStateMixin {
  String _pin = '';
  bool _error = false;
  bool _checking = false;
  late AnimationController _shakeCtrl;
  late Animation<double> _shakeAnim;

  @override
  void initState() {
    super.initState();
    _shakeCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _shakeAnim = Tween(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _shakeCtrl, curve: Curves.elasticIn),
    );
  }

  @override
  void dispose() {
    _shakeCtrl.dispose();
    super.dispose();
  }

  void _addDigit(String d) {
    if (_pin.length >= 6 || _checking) return;
    setState(() {
      _pin += d;
      _error = false;
    });
    if (_pin.length == 6 || (_pin.length == 4 && AdminService.verifyPin(_pin))) {
      _checkPin();
    }
  }

  void _removeDigit() {
    if (_pin.isEmpty || _checking) return;
    setState(() => _pin = _pin.substring(0, _pin.length - 1));
  }

  Future<void> _checkPin() async {
    // Try 4-digit first, then 6-digit
    if (_pin.length < 4) return;
    setState(() => _checking = true);
    await Future.delayed(const Duration(milliseconds: 200));
    if (AdminService.verifyPin(_pin)) {
      HapticFeedback.heavyImpact();
      widget.onUnlocked();
    } else if (_pin.length >= 6) {
      // Wrong PIN
      HapticFeedback.vibrate();
      _shakeCtrl.forward(from: 0);
      setState(() {
        _error = true;
        _checking = false;
        _pin = '';
      });
    } else {
      setState(() => _checking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cBg,
      body: SafeArea(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Lock icon
            Container(
              width: 80, height: 80,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const LinearGradient(
                  colors: [Color(0xFF00F2FE), Color(0xFF4FACFE)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                boxShadow: [
                  BoxShadow(
                    color: cGreen.withOpacity(0.3),
                    blurRadius: 24,
                    spreadRadius: 4,
                  ),
                ],
              ),
              child: const Icon(Icons.admin_panel_settings_rounded,
                  color: Colors.white, size: 36),
            ),
            const SizedBox(height: 24),
            const Text(
              'Admin Dashboard',
              style: TextStyle(
                  fontSize: 22, fontWeight: FontWeight.w800, color: cText),
            ),
            const SizedBox(height: 6),
            Text(
              'Enter your PIN to continue',
              style: TextStyle(fontSize: 14, color: cText2),
            ),
            const SizedBox(height: 40),

            // PIN dots
            AnimatedBuilder(
              animation: _shakeAnim,
              builder: (_, child) => Transform.translate(
                offset: Offset(
                    _error ? (_shakeAnim.value < 0.5 ? -8 : 8) * 4 : 0, 0),
                child: child,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(6, (i) {
                  final filled = i < _pin.length;
                  return AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    margin: const EdgeInsets.symmetric(horizontal: 8),
                    width: 16, height: 16,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: filled
                          ? (_error ? cRed : cGreen)
                          : cBorder,
                      border: Border.all(
                        color: filled
                            ? (_error ? cRed : cGreen)
                            : cMuted,
                        width: 1.5,
                      ),
                    ),
                  );
                }),
              ),
            ),

            if (_error) ...[
              const SizedBox(height: 12),
              Text(
                'Wrong PIN. Try again.',
                style: TextStyle(fontSize: 13, color: cRed),
              ),
            ],

            const SizedBox(height: 40),

            // Numpad
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 60),
              child: Column(
                children: [
                  for (final row in [
                    ['1', '2', '3'],
                    ['4', '5', '6'],
                    ['7', '8', '9'],
                    ['', '0', '⌫'],
                  ])
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: row.map((d) {
                        if (d.isEmpty) return const SizedBox(width: 72, height: 72);
                        return _PinKey(
                          label: d,
                          onTap: () {
                            if (d == '⌫') {
                              _removeDigit();
                            } else {
                              _addDigit(d);
                            }
                          },
                        );
                      }).toList(),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PinKey extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const _PinKey({required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isBack = label == '⌫';
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 72, height: 72,
        margin: const EdgeInsets.symmetric(vertical: 6),
        decoration: BoxDecoration(
          color: cCard,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: cBorder),
        ),
        child: Center(
          child: isBack
              ? const Icon(Icons.backspace_rounded, color: cText2, size: 22)
              : Text(
                  label,
                  style: const TextStyle(
                      fontSize: 24, fontWeight: FontWeight.w700, color: cText),
                ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  DASHBOARD BODY
// ═══════════════════════════════════════════════════════

class _DashboardBody extends StatelessWidget {
  final List<_AdminTab> tabs;
  final TabController tabController;
  final int selectedTab;

  const _DashboardBody({
    required this.tabs,
    required this.tabController,
    required this.selectedTab,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cBg,
      appBar: AppBar(
        backgroundColor: cBg2,
        elevation: 0,
        foregroundColor: cText,
        title: Row(children: [
          Icon(Icons.admin_panel_settings_rounded, color: cGreen, size: 22),
          const SizedBox(width: 10),
          const Text(
            'Admin Dashboard',
            style: TextStyle(
                fontSize: 17, fontWeight: FontWeight.w800, color: cText),
          ),
        ]),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(50),
          child: Container(
            color: cBg2,
            child: TabBar(
              controller: tabController,
              isScrollable: true,
              tabAlignment: TabAlignment.start,
              indicatorColor: cGreen,
              indicatorWeight: 2,
              labelColor: cGreen,
              unselectedLabelColor: cMuted,
              labelStyle: const TextStyle(
                  fontSize: 11, fontWeight: FontWeight.w700),
              tabs: tabs
                  .map((t) => Tab(
                        icon: Icon(t.icon, size: 18),
                        text: t.label,
                        iconMargin: const EdgeInsets.only(bottom: 2),
                      ))
                  .toList(),
            ),
          ),
        ),
      ),
      body: TabBarView(
        controller: tabController,
        children: const [
          _CharactersTab(),
          _MaintenanceTab(),
          _LimitsTab(),
          _PremiumTab(),
          _AdsTab(),
          _UsersTab(),
          _AbuseTab(),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  TAB 1: CHARACTER CONTROL
// ═══════════════════════════════════════════════════════

class _CharactersTab extends StatefulWidget {
  const _CharactersTab();
  @override
  State<_CharactersTab> createState() => _CharactersTabState();
}

class _CharactersTabState extends State<_CharactersTab> {
  Map<String, bool> _states = {};
  bool _loading = true;
  bool _saving = false;
  Timer? _refreshTimer;

  static const _allChars = [
    'Adam', 'Luna', 'Nova', 'Zara', 'Rex', 'Aria', 'Bolt', 'Sage',
    'Kai', 'Amara', 'Echo', 'Lyra', 'Titan', 'Mira', 'Vox', 'Zephyr',
    'Noor', 'Spark', 'Atlas', 'Seraph',
  ];

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
    final data = await AdminService.getCharacterStates();
    if (mounted) {
      // For chars not yet in DB, default to enabled
      final merged = {for (final c in _allChars) c: data[c] ?? true};
      setState(() {
        _states = merged;
        _loading = false;
      });
    }
  }

  Future<void> _toggle(String name, bool val) async {
    setState(() {
      _states[name] = val;
      _saving = true;
    });
    await AdminService.setCharacterEnabled(name, val);
    if (mounted) setState(() => _saving = false);
  }

  Future<void> _setAll(bool val) async {
    setState(() => _saving = true);
    await AdminService.setAllCharacters(val);
    await _load();
    if (mounted) setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    return _TabWrapper(
      title: 'Character Control',
      subtitle: '${_states.values.where((v) => v).length}/${_allChars.length} enabled',
      onRefresh: _load,
      saving: _saving,
      loading: _loading,
      actions: [
        _ActionBtn(label: 'Enable All', color: cGreen, onTap: () => _setAll(true)),
        const SizedBox(width: 8),
        _ActionBtn(label: 'Disable All', color: cRed, onTap: () => _setAll(false)),
      ],
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 2.6,
          crossAxisSpacing: 8,
          mainAxisSpacing: 8,
        ),
        itemCount: _allChars.length,
        itemBuilder: (_, i) {
          final name = _allChars[i];
          final enabled = _states[name] ?? true;
          return _CharTile(
            name: name,
            enabled: enabled,
            onToggle: (v) => _toggle(name, v),
          );
        },
      ),
    );
  }
}

class _CharTile extends StatelessWidget {
  final String name;
  final bool enabled;
  final ValueChanged<bool> onToggle;
  const _CharTile(
      {required this.name, required this.enabled, required this.onToggle});

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      decoration: BoxDecoration(
        color: enabled ? cCard : cBg2,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: enabled ? cGreen.withOpacity(0.4) : cBorder,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(children: [
          Icon(
            Icons.record_voice_over_rounded,
            color: enabled ? cGreen : cMuted,
            size: 18,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              name,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: enabled ? cText : cMuted,
              ),
            ),
          ),
          Switch(
            value: enabled,
            onChanged: onToggle,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
        ]),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  TAB 2: MAINTENANCE MODE
// ═══════════════════════════════════════════════════════

class _MaintenanceTab extends StatefulWidget {
  const _MaintenanceTab();
  @override
  State<_MaintenanceTab> createState() => _MaintenanceTabState();
}

class _MaintenanceTabState extends State<_MaintenanceTab> {
  AdminMaintenanceData? _data;
  bool _loading = true;
  bool _saving = false;
  late TextEditingController _msgCtrl;
  late TextEditingController _versionCtrl;
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _msgCtrl = TextEditingController();
    _versionCtrl = TextEditingController();
    _load();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) => _load());
  }

  @override
  void dispose() {
    _msgCtrl.dispose();
    _versionCtrl.dispose();
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final d = await AdminService.getMaintenanceData();
    if (mounted) {
      setState(() {
        _data = d;
        _msgCtrl.text = d.message;
        _versionCtrl.text = d.allowedVersion;
        _loading = false;
      });
    }
  }

  Future<void> _save(bool enabled) async {
    setState(() => _saving = true);
    await AdminService.setMaintenanceMode(
      enabled: enabled,
      message: _msgCtrl.text.trim(),
      allowedVersion: _versionCtrl.text.trim(),
    );
    await _load();
    if (mounted) setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    final enabled = _data?.enabled ?? false;
    return _TabWrapper(
      title: 'Maintenance Mode',
      subtitle: enabled ? '🔴 ACTIVE — App is DOWN' : '🟢 App is LIVE',
      onRefresh: _load,
      saving: _saving,
      loading: _loading,
      child: Column(children: [
        // Big toggle
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: enabled
                ? cRed.withOpacity(0.1)
                : cGreen.withOpacity(0.07),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: enabled ? cRed.withOpacity(0.5) : cGreen.withOpacity(0.3),
            ),
          ),
          child: Row(children: [
            Icon(
              enabled ? Icons.warning_amber_rounded : Icons.check_circle_rounded,
              color: enabled ? cRed : cGreen,
              size: 32,
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    enabled ? 'Maintenance Active' : 'App is Live',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: enabled ? cRed : cGreen,
                    ),
                  ),
                  Text(
                    enabled
                        ? 'Users cannot access the app'
                        : 'All users can access normally',
                    style: const TextStyle(fontSize: 12, color: cText2),
                  ),
                ],
              ),
            ),
            Switch(value: enabled, onChanged: _saving ? null : _save),
          ]),
        ),
        const SizedBox(height: 16),

        // Message
        _AdminField(
          label: 'Maintenance Message',
          hint: 'Shown to users when app is in maintenance...',
          controller: _msgCtrl,
          maxLines: 3,
          icon: Icons.message_rounded,
        ),
        const SizedBox(height: 12),

        // Allowed version
        _AdminField(
          label: 'Allowed Version (optional)',
          hint: 'e.g. 1.2.0 — this version bypasses maintenance',
          controller: _versionCtrl,
          icon: Icons.new_releases_rounded,
        ),
        const SizedBox(height: 16),

        SizedBox(
          width: double.infinity,
          child: _SaveBtn(
            label: 'Save Settings',
            onTap: () => _save(enabled),
            saving: _saving,
          ),
        ),
      ]),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  TAB 3: CHARACTER LIMITS
// ═══════════════════════════════════════════════════════

class _LimitsTab extends StatefulWidget {
  const _LimitsTab();
  @override
  State<_LimitsTab> createState() => _LimitsTabState();
}

class _LimitsTabState extends State<_LimitsTab> {
  AdminLimitsData _data = const AdminLimitsData();
  bool _loading = true;
  bool _saving = false;
  Timer? _refreshTimer;

  // Controllers
  late TextEditingController _freeCharCtrl, _premCharCtrl;
  late TextEditingController _freeDailyCtrl, _premDailyCtrl;
  late TextEditingController _freeHistCtrl, _premHistCtrl;

  @override
  void initState() {
    super.initState();
    _freeCharCtrl = TextEditingController();
    _premCharCtrl = TextEditingController();
    _freeDailyCtrl = TextEditingController();
    _premDailyCtrl = TextEditingController();
    _freeHistCtrl = TextEditingController();
    _premHistCtrl = TextEditingController();
    _load();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) => _load());
  }

  @override
  void dispose() {
    for (final c in [
      _freeCharCtrl, _premCharCtrl, _freeDailyCtrl,
      _premDailyCtrl, _freeHistCtrl, _premHistCtrl
    ]) {
      c.dispose();
    }
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final d = await AdminService.getLimitsData();
    if (mounted) {
      setState(() {
        _data = d;
        _freeCharCtrl.text = d.freeCharLimit.toString();
        _premCharCtrl.text = d.premiumCharLimit.toString();
        _freeDailyCtrl.text = d.freeDailyLimit.toString();
        _premDailyCtrl.text = d.premiumDailyLimit.toString();
        _freeHistCtrl.text = d.freeHistoryLimit.toString();
        _premHistCtrl.text = d.premiumHistoryLimit.toString();
        _loading = false;
      });
    }
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    final updated = AdminLimitsData(
      freeCharLimit: int.tryParse(_freeCharCtrl.text) ?? _data.freeCharLimit,
      premiumCharLimit: int.tryParse(_premCharCtrl.text) ?? _data.premiumCharLimit,
      freeDailyLimit: int.tryParse(_freeDailyCtrl.text) ?? _data.freeDailyLimit,
      premiumDailyLimit: int.tryParse(_premDailyCtrl.text) ?? _data.premiumDailyLimit,
      freeHistoryLimit: int.tryParse(_freeHistCtrl.text) ?? _data.freeHistoryLimit,
      premiumHistoryLimit: int.tryParse(_premHistCtrl.text) ?? _data.premiumHistoryLimit,
    );
    await AdminService.setLimits(updated);
    await _load();
    if (mounted) setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    return _TabWrapper(
      title: 'Character & Usage Limits',
      subtitle: 'Free: ${_data.freeCharLimit} chars · Premium: ${_data.premiumCharLimit} chars',
      onRefresh: _load,
      saving: _saving,
      loading: _loading,
      child: Column(children: [
        _LimitRow(
          label: 'Chars Per Request',
          freeCtrl: _freeCharCtrl,
          premCtrl: _premCharCtrl,
          icon: Icons.text_fields_rounded,
        ),
        const SizedBox(height: 14),
        _LimitRow(
          label: 'Daily Requests',
          freeCtrl: _freeDailyCtrl,
          premCtrl: _premDailyCtrl,
          icon: Icons.today_rounded,
        ),
        const SizedBox(height: 14),
        _LimitRow(
          label: 'History Entries',
          freeCtrl: _freeHistCtrl,
          premCtrl: _premHistCtrl,
          icon: Icons.history_rounded,
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: _SaveBtn(label: 'Save Limits', onTap: _save, saving: _saving),
        ),
      ]),
    );
  }
}

class _LimitRow extends StatelessWidget {
  final String label;
  final TextEditingController freeCtrl, premCtrl;
  final IconData icon;
  const _LimitRow({
    required this.label,
    required this.freeCtrl,
    required this.premCtrl,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cBorder),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(icon, color: cGreen, size: 18),
          const SizedBox(width: 8),
          Text(label,
              style: const TextStyle(
                  fontSize: 13, fontWeight: FontWeight.w700, color: cText)),
        ]),
        const SizedBox(height: 12),
        Row(children: [
          Expanded(
            child: _CompactField(
              label: 'Free',
              controller: freeCtrl,
              color: cAmber,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: _CompactField(
              label: 'Premium',
              controller: premCtrl,
              color: cGreen,
            ),
          ),
        ]),
      ]),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  TAB 4: PREMIUM FEATURES LOCK
// ═══════════════════════════════════════════════════════

class _PremiumTab extends StatefulWidget {
  const _PremiumTab();
  @override
  State<_PremiumTab> createState() => _PremiumTabState();
}

class _PremiumTabState extends State<_PremiumTab> {
  AdminPremiumData _data = const AdminPremiumData();
  bool _loading = true;
  bool _saving = false;
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
    final d = await AdminService.getPremiumData();
    if (mounted) setState(() { _data = d; _loading = false; });
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    await AdminService.setPremiumData(_data);
    await _load();
    if (mounted) setState(() => _saving = false);
  }

  void _toggle(String feature, bool val) {
    setState(() {
      switch (feature) {
        case 'hdVoice':        _data = AdminPremiumData(hdVoiceLocked: val, autoEmotionLocked: _data.autoEmotionLocked, wordBoundaryLocked: _data.wordBoundaryLocked, ssmlModeLocked: _data.ssmlModeLocked, adaptivePacingLocked: _data.adaptivePacingLocked, breathingLocked: _data.breathingLocked, premiumCharactersLocked: _data.premiumCharactersLocked, exportLocked: _data.exportLocked); break;
        case 'autoEmotion':    _data = AdminPremiumData(hdVoiceLocked: _data.hdVoiceLocked, autoEmotionLocked: val, wordBoundaryLocked: _data.wordBoundaryLocked, ssmlModeLocked: _data.ssmlModeLocked, adaptivePacingLocked: _data.adaptivePacingLocked, breathingLocked: _data.breathingLocked, premiumCharactersLocked: _data.premiumCharactersLocked, exportLocked: _data.exportLocked); break;
        case 'wordBoundary':   _data = AdminPremiumData(hdVoiceLocked: _data.hdVoiceLocked, autoEmotionLocked: _data.autoEmotionLocked, wordBoundaryLocked: val, ssmlModeLocked: _data.ssmlModeLocked, adaptivePacingLocked: _data.adaptivePacingLocked, breathingLocked: _data.breathingLocked, premiumCharactersLocked: _data.premiumCharactersLocked, exportLocked: _data.exportLocked); break;
        case 'ssmlMode':       _data = AdminPremiumData(hdVoiceLocked: _data.hdVoiceLocked, autoEmotionLocked: _data.autoEmotionLocked, wordBoundaryLocked: _data.wordBoundaryLocked, ssmlModeLocked: val, adaptivePacingLocked: _data.adaptivePacingLocked, breathingLocked: _data.breathingLocked, premiumCharactersLocked: _data.premiumCharactersLocked, exportLocked: _data.exportLocked); break;
        case 'adaptivePacing': _data = AdminPremiumData(hdVoiceLocked: _data.hdVoiceLocked, autoEmotionLocked: _data.autoEmotionLocked, wordBoundaryLocked: _data.wordBoundaryLocked, ssmlModeLocked: _data.ssmlModeLocked, adaptivePacingLocked: val, breathingLocked: _data.breathingLocked, premiumCharactersLocked: _data.premiumCharactersLocked, exportLocked: _data.exportLocked); break;
        case 'breathing':      _data = AdminPremiumData(hdVoiceLocked: _data.hdVoiceLocked, autoEmotionLocked: _data.autoEmotionLocked, wordBoundaryLocked: _data.wordBoundaryLocked, ssmlModeLocked: _data.ssmlModeLocked, adaptivePacingLocked: _data.adaptivePacingLocked, breathingLocked: val, premiumCharactersLocked: _data.premiumCharactersLocked, exportLocked: _data.exportLocked); break;
        case 'premChars':      _data = AdminPremiumData(hdVoiceLocked: _data.hdVoiceLocked, autoEmotionLocked: _data.autoEmotionLocked, wordBoundaryLocked: _data.wordBoundaryLocked, ssmlModeLocked: _data.ssmlModeLocked, adaptivePacingLocked: _data.adaptivePacingLocked, breathingLocked: _data.breathingLocked, premiumCharactersLocked: val, exportLocked: _data.exportLocked); break;
        case 'export':         _data = AdminPremiumData(hdVoiceLocked: _data.hdVoiceLocked, autoEmotionLocked: _data.autoEmotionLocked, wordBoundaryLocked: _data.wordBoundaryLocked, ssmlModeLocked: _data.ssmlModeLocked, adaptivePacingLocked: _data.adaptivePacingLocked, breathingLocked: _data.breathingLocked, premiumCharactersLocked: _data.premiumCharactersLocked, exportLocked: val); break;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final features = [
      _FeatureRow(icon: Icons.hd_rounded,             label: 'HD Voice',             sub: 'High-quality neural voices',       key_: 'hdVoice',        locked: _data.hdVoiceLocked),
      _FeatureRow(icon: Icons.psychology_rounded,     label: 'Auto Emotion AI',      sub: 'AI-powered emotion detection',     key_: 'autoEmotion',    locked: _data.autoEmotionLocked),
      _FeatureRow(icon: Icons.closed_caption_rounded, label: 'Word Boundary',        sub: 'Karaoke / Avatar sync',            key_: 'wordBoundary',   locked: _data.wordBoundaryLocked),
      _FeatureRow(icon: Icons.code_rounded,           label: 'SSML Mode',            sub: 'Full SSML markup support',         key_: 'ssmlMode',       locked: _data.ssmlModeLocked),
      _FeatureRow(icon: Icons.speed_rounded,          label: 'Adaptive Pacing',      sub: 'Smart speed adjustment',           key_: 'adaptivePacing', locked: _data.adaptivePacingLocked),
      _FeatureRow(icon: Icons.air_rounded,            label: 'Natural Breathing',    sub: 'Breathing & pause control',        key_: 'breathing',      locked: _data.breathingLocked),
      _FeatureRow(icon: Icons.stars_rounded,          label: 'Premium Characters',   sub: 'Titan, Seraph, Atlas, etc.',       key_: 'premChars',      locked: _data.premiumCharactersLocked),
      _FeatureRow(icon: Icons.download_rounded,       label: 'Audio Export',         sub: 'Save & share audio files',         key_: 'export',         locked: _data.exportLocked),
    ];

    return _TabWrapper(
      title: 'Premium Features Lock',
      subtitle: '${features.where((f) => f.locked).length} features locked',
      onRefresh: _load,
      saving: _saving,
      loading: _loading,
      child: Column(children: [
        ...features.map((f) => Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: _FeatureTile(
            icon: f.icon,
            label: f.label,
            sub: f.sub,
            locked: f.locked,
            onToggle: (v) => _toggle(f.key_, v),
          ),
        )),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: _SaveBtn(label: 'Save Premium Config', onTap: _save, saving: _saving),
        ),
      ]),
    );
  }
}

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
    return _TabWrapper(
      title: 'User Accounts Audit',
      subtitle: '${_users.length} registered users',
      onRefresh: _load,
      loading: _loading,
      child: Column(children: [
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
            padding: const EdgeInsets.all(24),
            child: Column(children: [
              Icon(Icons.people_outline_rounded, color: cMuted, size: 48),
              const SizedBox(height: 12),
              const Text('No users yet', style: TextStyle(color: cMuted, fontSize: 14)),
              const SizedBox(height: 8),
              const Text(
                'Users appear here when they log in.\nMake sure the app writes to admin/users in Firebase.',
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
                await AdminService.banUser(u.uid, !u.banned);
                _load();
              },
              onPremium: () async {
                await AdminService.setPremiumUser(u.uid, !u.isPremium);
                _load();
              },
            ),
          )),
      ]),
    );
  }
}

class _UserTile extends StatelessWidget {
  final AdminUserRecord user;
  final VoidCallback onBan, onPremium;
  const _UserTile({required this.user, required this.onBan, required this.onPremium});

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
      child: Row(children: [
        // Avatar
        Container(
          width: 40, height: 40,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              colors: user.banned
                  ? [cRed, cRed.withOpacity(0.6)]
                  : (user.isPremium
                      ? [cAmber, cOrange]
                      : [cGreen, cGreen2]),
            ),
          ),
          child: Center(child: Text(user.initials,
              style: const TextStyle(fontSize: 14,
                  fontWeight: FontWeight.w800, color: Colors.white))),
        ),
        const SizedBox(width: 10),
        Expanded(child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Expanded(child: Text(
                user.displayName.isNotEmpty ? user.displayName : user.email,
                style: const TextStyle(fontSize: 13,
                    fontWeight: FontWeight.w700, color: cText),
                overflow: TextOverflow.ellipsis,
              )),
              if (user.isPremium)
                _Badge(label: 'PRO', color: cAmber),
              if (user.banned)
                _Badge(label: 'BANNED', color: cRed),
            ]),
            Text(user.email,
                style: const TextStyle(fontSize: 11, color: cMuted),
                overflow: TextOverflow.ellipsis),
            Text('Active: ${user.lastActiveFormatted} · ${user.totalRequests} requests',
                style: const TextStyle(fontSize: 10, color: cMuted2)),
          ],
        )),
        Column(children: [
          _MiniBtn(
            icon: user.isPremium ? Icons.star_rounded : Icons.star_border_rounded,
            color: cAmber,
            onTap: onPremium,
          ),
          const SizedBox(height: 4),
          _MiniBtn(
            icon: user.banned ? Icons.lock_open_rounded : Icons.block_rounded,
            color: cRed,
            onTap: onBan,
          ),
        ]),
      ]),
    );
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
        width: 30, height: 30,
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Icon(icon, color: color, size: 15),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════
//  TAB 7: API ABUSE PREVENTION
// ═══════════════════════════════════════════════════════

class _AbuseTab extends StatefulWidget {
  const _AbuseTab();
  @override
  State<_AbuseTab> createState() => _AbuseTabState();
}

class _AbuseTabState extends State<_AbuseTab> {
  AdminAbuseData _data = const AdminAbuseData();
  bool _loading = true;
  bool _saving = false;
  Timer? _refreshTimer;

  late TextEditingController _rpmCtrl, _rphCtrl, _maxCharsCtrl, _thresholdCtrl;

  @override
  void initState() {
    super.initState();
    _rpmCtrl = TextEditingController();
    _rphCtrl = TextEditingController();
    _maxCharsCtrl = TextEditingController();
    _thresholdCtrl = TextEditingController();
    _load();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) => _load());
  }

  @override
  void dispose() {
    _rpmCtrl.dispose(); _rphCtrl.dispose();
    _maxCharsCtrl.dispose(); _thresholdCtrl.dispose();
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final d = await AdminService.getAbuseData();
    if (mounted) {
      setState(() {
        _data = d;
        _rpmCtrl.text = d.maxRequestsPerMinute.toString();
        _rphCtrl.text = d.maxRequestsPerHour.toString();
        _maxCharsCtrl.text = d.maxCharsPerRequest.toString();
        _thresholdCtrl.text = d.suspiciousThreshold.toString();
        _loading = false;
      });
    }
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    final updated = AdminAbuseData(
      rateLimitEnabled: _data.rateLimitEnabled,
      maxRequestsPerMinute: int.tryParse(_rpmCtrl.text) ?? _data.maxRequestsPerMinute,
      maxRequestsPerHour: int.tryParse(_rphCtrl.text) ?? _data.maxRequestsPerHour,
      maxCharsPerRequest: int.tryParse(_maxCharsCtrl.text) ?? _data.maxCharsPerRequest,
      blockVpn: _data.blockVpn,
      blockTor: _data.blockTor,
      suspiciousThreshold: int.tryParse(_thresholdCtrl.text) ?? _data.suspiciousThreshold,
      blockedIps: _data.blockedIps,
    );
    await AdminService.setAbuseData(updated);
    await _load();
    if (mounted) setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    return _TabWrapper(
      title: 'API Abuse Prevention',
      subtitle: _data.rateLimitEnabled ? '🛡️ Protection Active' : '⚠️ Protection OFF',
      onRefresh: _load,
      saving: _saving,
      loading: _loading,
      child: Column(children: [
        _SwitchTile(
          icon: Icons.shield_rounded,
          label: 'Rate Limiting',
          sub: 'Enable request rate limits',
          value: _data.rateLimitEnabled,
          color: cGreen,
          onChanged: (v) => setState(() => _data = AdminAbuseData(rateLimitEnabled: v, maxRequestsPerMinute: _data.maxRequestsPerMinute, maxRequestsPerHour: _data.maxRequestsPerHour, maxCharsPerRequest: _data.maxCharsPerRequest, blockVpn: _data.blockVpn, blockTor: _data.blockTor, suspiciousThreshold: _data.suspiciousThreshold, blockedIps: _data.blockedIps)),
        ),
        const SizedBox(height: 8),
        _SwitchTile(
          icon: Icons.vpn_lock_rounded,
          label: 'Block VPN',
          sub: 'Block requests from VPN IPs',
          value: _data.blockVpn,
          color: cOrange,
          onChanged: (v) => setState(() => _data = AdminAbuseData(rateLimitEnabled: _data.rateLimitEnabled, maxRequestsPerMinute: _data.maxRequestsPerMinute, maxRequestsPerHour: _data.maxRequestsPerHour, maxCharsPerRequest: _data.maxCharsPerRequest, blockVpn: v, blockTor: _data.blockTor, suspiciousThreshold: _data.suspiciousThreshold, blockedIps: _data.blockedIps)),
        ),
        const SizedBox(height: 8),
        _SwitchTile(
          icon: Icons.dark_mode_rounded,
          label: 'Block Tor',
          sub: 'Block Tor network exit nodes',
          value: _data.blockTor,
          color: cRed,
          onChanged: (v) => setState(() => _data = AdminAbuseData(rateLimitEnabled: _data.rateLimitEnabled, maxRequestsPerMinute: _data.maxRequestsPerMinute, maxRequestsPerHour: _data.maxRequestsPerHour, maxCharsPerRequest: _data.maxCharsPerRequest, blockVpn: _data.blockVpn, blockTor: v, suspiciousThreshold: _data.suspiciousThreshold, blockedIps: _data.blockedIps)),
        ),
        const SizedBox(height: 16),
        Row(children: [
          Expanded(child: _CompactField(label: 'Max/Minute', controller: _rpmCtrl, color: cGreen)),
          const SizedBox(width: 10),
          Expanded(child: _CompactField(label: 'Max/Hour', controller: _rphCtrl, color: cBlue)),
        ]),
        const SizedBox(height: 10),
        Row(children: [
          Expanded(child: _CompactField(label: 'Max Chars/Req', controller: _maxCharsCtrl, color: cAmber)),
          const SizedBox(width: 10),
          Expanded(child: _CompactField(label: 'Suspicious Threshold', controller: _thresholdCtrl, color: cOrange)),
        ]),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: _SaveBtn(label: 'Save Protection Config', onTap: _save, saving: _saving),
        ),
      ]),
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
