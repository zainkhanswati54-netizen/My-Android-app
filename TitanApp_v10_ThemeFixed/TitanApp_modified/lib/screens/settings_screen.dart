import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../utils/constants.dart';
import '../widgets/mint_card.dart';
import '../services/tts_service.dart';
import '../services/auth_service.dart';
import '../main.dart' show themeNotifier;
import 'profile_screen.dart';
import 'admin_dashboard_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsState();
}

class _SettingsState extends State<SettingsScreen> {
  String _folder = 'Loading...';

  // ── Admin secret tap ──────────────────────────────────────
  int _adminTapCount = 0;
  DateTime? _lastAdminTap;

  void _onAdminSecretTap() {
    final now = DateTime.now();
    if (_lastAdminTap != null &&
        now.difference(_lastAdminTap!).inSeconds > 3) {
      _adminTapCount = 0;
    }
    _lastAdminTap = now;
    _adminTapCount++;
    if (_adminTapCount >= 7) {
      _adminTapCount = 0;
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const AdminDashboardScreen()),
      );
    }
  }

  @override
  void initState() { super.initState(); _loadFolder(); }

  String _getInitials() {
    final user = AuthService.currentUser;
    final nm = (user?.displayName ?? '').trim();
    final em = user?.email ?? 'U';
    final n = nm.isNotEmpty ? nm : em;
    final parts = n.split(' ');
    if (parts.length >= 2 && parts[0].isNotEmpty && parts[1].isNotEmpty) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return n.isNotEmpty ? n[0].toUpperCase() : 'U';
  }

  String _getName() => AuthService.currentUser?.displayName ?? 'User';
  String _getEmail() => AuthService.currentUser?.email ?? '';

  Future<void> _loadFolder() async {
    final f = await TtsService.getAudioFolder();
    if (mounted) setState(() => _folder = f);
  }


  Widget _aboutRow(BuildContext context, IconData ic, String text) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? cText : const Color(0xFF0F1B2D);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(children: [
        Icon(ic, size: 16, color: cGreen),
        const SizedBox(width: 10),
        Expanded(child: Text(text, style: TextStyle(fontSize: 13, color: textColor, height: 1.4))),
      ]),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark    = Theme.of(context).brightness == Brightness.dark;
    final bgColor   = isDark ? cBg    : const Color(0xFFF5F7FA);
    final bg2Color  = isDark ? cBg2   : const Color(0xFFFFFFFF);
    final cardColor = isDark ? cCard  : const Color(0xFFFFFFFF);
    final textColor = isDark ? cText  : const Color(0xFF0F1B2D);
    final mutedColor= isDark ? cMuted : const Color(0xFF8A99AD);
    final borderCol = isDark ? cBorder: const Color(0xFFD0D9E8);

    return Scaffold(
    backgroundColor: bgColor,
    appBar: AppBar(
      backgroundColor: bg2Color, elevation: 0, foregroundColor: textColor,
      title: Text('Settings', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: textColor)),
      bottom: PreferredSize(preferredSize: const Size.fromHeight(1), child: Container(color: borderCol, height: 1)),
    ),
    body: ListView(
      padding: const EdgeInsets.all(14),
      children: [
        // ── Profile Card ──────────────────────────────────
        GestureDetector(
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const ProfileScreen())),
          child: Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: borderCol),
            ),
            child: Row(children: [
              Container(
                width: 50, height: 50,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(colors: [cGreen, cGreen2]),
                ),
                child: Center(child: Text(
                  _getInitials(),
                  style: const TextStyle(fontSize: 20,
                      fontWeight: FontWeight.w800, color: Colors.white),
                )),
              ),
              const SizedBox(width: 14),
              Expanded(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(_getName(), style: TextStyle(
                      fontSize: 15, fontWeight: FontWeight.w700, color: textColor)),
                  Text(_getEmail(), style: TextStyle(
                      fontSize: 12, color: mutedColor)),
                  const SizedBox(height: 3),
                  const Text('Tap to view profile →',
                      style: TextStyle(fontSize: 11, color: cGreen)),
                ],
              )),
            ]),
          ),
        ),

        // ── Theme Toggle Card ─────────────────────────
        ValueListenableBuilder<ThemeMode>(
          valueListenable: themeNotifier,
          builder: (ctx2, mode, __) {
            final isDarkMode = mode == ThemeMode.dark;
            final tText  = isDarkMode ? cText  : const Color(0xFF0F1B2D);
            final tMuted = isDarkMode ? cMuted : const Color(0xFF8A99AD);
            return MintCard(
              child: Row(children: [
                Container(
                  width: 40, height: 40,
                  decoration: BoxDecoration(
                    color: isDarkMode
                        ? const Color(0xFF1C2840)
                        : const Color(0xFFE8F4FD),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    isDarkMode ? Icons.dark_mode_rounded : Icons.light_mode_rounded,
                    color: isDarkMode ? cGreen : const Color(0xFFFF9500),
                    size: 22,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isDarkMode ? 'Dark Mode' : 'Light Mode',
                      style: TextStyle(fontSize: 14,
                          fontWeight: FontWeight.w700, color: tText),
                    ),
                    Text(
                      isDarkMode ? 'Switch to light theme' : 'Switch to dark theme',
                      style: TextStyle(fontSize: 11, color: tMuted),
                    ),
                  ],
                )),
                GestureDetector(
                  onTap: () {
                    themeNotifier.value = isDarkMode
                        ? ThemeMode.light
                        : ThemeMode.dark;
                  },
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    curve: Curves.easeInOut,
                    width: 52,
                    height: 28,
                    decoration: BoxDecoration(
                      color: isDark ? cGreen : const Color(0xFFFF9500),
                      borderRadius: BorderRadius.circular(14),
                      boxShadow: [
                        BoxShadow(
                          color: (isDark ? cGreen : const Color(0xFFFF9500))
                              .withOpacity(0.4),
                          blurRadius: 8,
                        ),
                      ],
                    ),
                    child: AnimatedAlign(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeInOut,
                      alignment: isDarkMode
                          ? Alignment.centerRight
                          : Alignment.centerLeft,
                      child: Container(
                        width: 22, height: 22,
                        margin: const EdgeInsets.symmetric(horizontal: 3),
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          isDarkMode ? Icons.nights_stay_rounded : Icons.wb_sunny_rounded,
                          size: 13,
                          color: isDarkMode ? cGreen : const Color(0xFFFF9500),
                        ),
                      ),
                    ),
                  ),
                ),
              ]),
            );
          },
        ),
        const SizedBox(height: 12),

        MintCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const SectionHeader('Save Location'),
          const SizedBox(height: 10),
          Row(children: [
            const Icon(Icons.folder_rounded, color: cGreen, size: 22),
            const SizedBox(width: 10),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('TitanStudioPRO/Audio/', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: mutedColor)),
              Text(_folder, style: TextStyle(fontSize: 11, color: mutedColor)),
            ])),
          ]),
          const SizedBox(height: 8),
          Text('All generated audio files are saved here automatically.', style: TextStyle(fontSize: 12, color: mutedColor)),
        ])),
        const SizedBox(height: 12),
        MintCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const SectionHeader('Supported Languages'),
          const SizedBox(height: 10),
          ...kLanguages.entries.map((e) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(children: [
              SvgPicture.asset(e.value.flag, width: 22, height: 22),
              const SizedBox(width: 12),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(e.key, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: textColor)),
                Text('Male: ${e.value.maleVoice}', style: TextStyle(fontSize: 10, color: mutedColor)),
                Text('Female: ${e.value.femaleVoice}', style: TextStyle(fontSize: 10, color: mutedColor)),
              ])),
              if (e.value.isRtl)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                  decoration: BoxDecoration(color: cAmber.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
                  child: const Text('RTL', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: cAmber)),
                ),
            ]),
          )),
        ])),
        const SizedBox(height: 12),
        MintCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          GestureDetector(
            onTap: _onAdminSecretTap,
            child: const SectionHeader('About'),
          ),
          const SizedBox(height: 10),
          ...[
            _aboutRow(context, Icons.rocket_launch_rounded,       'Titan Studio PRO  v1.0'),
            _aboutRow(context, Icons.public_rounded,              'Always Free — No API Key Required'),
            _aboutRow(context, Icons.language_rounded,            '39 Languages — Azure Edge TTS'),
            _aboutRow(context, Icons.people_rounded,              '20 Characters + 8 Voice Presets'),
            _aboutRow(context, Icons.sentiment_satisfied_rounded, '8 Emotions + Speed/Pitch Control'),
            _aboutRow(context, Icons.hd_rounded,                  'HD Neural Voices'),
            _aboutRow(context, Icons.psychology_rounded,          'Auto Emotion Detection (AI)'),
            _aboutRow(context, Icons.closed_caption_rounded,      'Word-Boundary Sync (Karaoke/Avatar)'),
            _aboutRow(context, Icons.code_rounded,                'Full SSML Markup Support'),
            _aboutRow(context, Icons.record_voice_over_rounded,   'Custom Neural Voice (CNV) — Beta'),
            _aboutRow(context, Icons.translate_rounded,           'Cross-Lingual Voice Persona'),
            _aboutRow(context, Icons.campaign_rounded,            'Brand Voice Persona System'),
          ],
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text('© 2026 Titan Studio PRO', style: TextStyle(fontSize: 12, color: mutedColor)),
          ),
        ])),
        const SizedBox(height: 20),
      ],
    ),
  );
}
