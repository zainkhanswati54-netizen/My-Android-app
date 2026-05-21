import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../utils/constants.dart';
import '../widgets/mint_card.dart';
import '../services/tts_service.dart';
import '../services/auth_service.dart';
import 'profile_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsState();
}

class _SettingsState extends State<SettingsScreen> {
  String _folder = 'Loading...';

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


  Widget _aboutRow(IconData ic, String text) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: Row(children: [
      Icon(ic, size: 16, color: cGreen),
      const SizedBox(width: 10),
      Expanded(child: Text(text, style: const TextStyle(fontSize: 13, color: cText, height: 1.4))),
    ]),
  );

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: cBg,
    appBar: AppBar(
      backgroundColor: cBg2, elevation: 0, foregroundColor: cText,
      title: const Text('Settings', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: cText)),
      bottom: PreferredSize(preferredSize: const Size.fromHeight(1), child: Container(color: cBorder, height: 1)),
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
              color: cCard,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: cBorder),
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
                  Text(_getName(), style: const TextStyle(
                      fontSize: 15, fontWeight: FontWeight.w700, color: cText)),
                  Text(_getEmail(), style: const TextStyle(
                      fontSize: 12, color: cMuted)),
                  const SizedBox(height: 3),
                  const Text('Tap to view profile →',
                      style: TextStyle(fontSize: 11, color: cGreen)),
                ],
              )),
            ]),
          ),
        ),

        MintCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const SectionHeader('Save Location'),
          const SizedBox(height: 10),
          Row(children: [
            const Icon(Icons.folder_rounded, color: cGreen, size: 22),
            const SizedBox(width: 10),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('TitanStudioPRO/Audio/', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cText2)),
              Text(_folder, style: const TextStyle(fontSize: 11, color: cMuted)),
            ])),
          ]),
          const SizedBox(height: 8),
          const Text('All generated audio files are saved here automatically.', style: TextStyle(fontSize: 12, color: cMuted)),
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
                Text(e.key, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cText)),
                Text('Male: ${e.value.maleVoice}', style: const TextStyle(fontSize: 10, color: cMuted)),
                Text('Female: ${e.value.femaleVoice}', style: const TextStyle(fontSize: 10, color: cMuted)),
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
          const SectionHeader('About'),
          const SizedBox(height: 10),
          ...[
            _aboutRow(Icons.rocket_launch_rounded,      'Titan Studio PRO  v2.0'),
            _aboutRow(Icons.public_rounded,             'Always Free — No API Key Required'),
            _aboutRow(Icons.language_rounded,           '39 Languages — Azure Edge TTS'),
            _aboutRow(Icons.people_rounded,             '20 Characters + 8 Voice Presets'),
            _aboutRow(Icons.sentiment_satisfied_rounded,'8 Emotions + Speed/Pitch Control'),
            _aboutRow(Icons.hd_rounded,                 'HD Neural Voices'),
            _aboutRow(Icons.psychology_rounded,         'Auto Emotion Detection (AI)'),
            _aboutRow(Icons.closed_caption_rounded,     'Word-Boundary Sync (Karaoke)'),
            _aboutRow(Icons.code_rounded,               'Full SSML Markup Support'),
          ],
          const Padding(
            padding: EdgeInsets.only(top: 4),
            child: Text('© 2026 Titan Studio PRO', style: TextStyle(fontSize: 12, color: cMuted)),
          ),
        ])),
        const SizedBox(height: 20),
      ],
    ),
  );
}
