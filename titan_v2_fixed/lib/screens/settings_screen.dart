import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../widgets/mint_card.dart';
import '../services/tts_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsState();
}

class _SettingsState extends State<SettingsScreen> {
  String _folder = 'Loading...';

  @override
  void initState() { super.initState(); _loadFolder(); }

  Future<void> _loadFolder() async {
    final f = await TtsService.getAudioFolder();
    if (mounted) setState(() => _folder = f);
  }

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
              Text(e.value.flag, style: const TextStyle(fontSize: 18)),
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
            '🚀  Titan Studio PRO v1.0',
            '🌐  Always Free — No API Key Required',
            '🇵🇰  Urdu, 🇮🇳 Hindi, 🇺🇸 English Support',
            '👥  8 Characters + 8 Voice Presets',
            '🎭  8 Emotions + Speed/Pitch Control',
            '© 2025 Titan Studio PRO',
          ].map((line) => Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(line, style: const TextStyle(fontSize: 13, color: cText, height: 1.5)),
          )),
        ])),
        const SizedBox(height: 20),
      ],
    ),
  );
}
