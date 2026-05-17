import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/material.dart';
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

        // ── Kaggle Server URL ──────────────────────────────
        MintCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const SectionHeader('⚡ Fast Server (Kaggle GPU)'),
          const SizedBox(height: 6),
          Text(
            'Kaggle notebook chalao → URL yahan paste karo',
            style: TextStyle(fontSize: 12, color: cMuted),
          ),
          const SizedBox(height: 10),
          _KaggleUrlField(),
          const SizedBox(height: 4),
          Text(
            'Khali chhodo = Hugging Face use hoga (slow)',
            style: TextStyle(fontSize: 11, color: cMuted),
          ),
        ])),
        const SizedBox(height: 10),

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


// ── Kaggle URL Input Widget ───────────────────────────────
class _KaggleUrlField extends StatefulWidget {
  const _KaggleUrlField();
  @override
  State<_KaggleUrlField> createState() => _KaggleUrlFieldState();
}

class _KaggleUrlFieldState extends State<_KaggleUrlField> {
  final _ctrl = TextEditingController();
  bool _saved = false;

  @override
  void initState() {
    super.initState();
    _loadSaved();
  }

  Future<void> _loadSaved() async {
    final prefs = await SharedPreferences.getInstance();
    final url = prefs.getString('kaggle_server_url') ?? '';
    _ctrl.text = url;
    if (url.isNotEmpty) TtsService.setKaggleUrl(url);
  }

  Future<void> _save() async {
    final url = _ctrl.text.trim();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('kaggle_server_url', url);
    TtsService.setKaggleUrl(url);
    setState(() => _saved = true);
    await Future.delayed(const Duration(seconds: 2));
    if (mounted) setState(() => _saved = false);
  }

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(
        child: TextField(
          controller: _ctrl,
          style: const TextStyle(color: cText, fontSize: 13),
          decoration: InputDecoration(
            hintText: 'https://xxxx.ngrok.io',
            hintStyle: TextStyle(color: cMuted.withOpacity(0.5), fontSize: 13),
            filled: true,
            fillColor: cBg,
            contentPadding: const EdgeInsets.symmetric(
                horizontal: 12, vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: cBorder),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: cBorder),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: cGreen, width: 1.5),
            ),
          ),
        ),
      ),
      const SizedBox(width: 8),
      GestureDetector(
        onTap: _save,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: _saved ? cGreen.withOpacity(0.2) : cGreen,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            _saved ? '✅' : 'Save',
            style: TextStyle(
              color: _saved ? cGreen : Colors.white,
              fontWeight: FontWeight.w700,
              fontSize: 13,
            ),
          ),
        ),
      ),
    ]);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }
}
