import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:just_audio/just_audio.dart';
import 'package:uuid/uuid.dart';
import '../utils/constants.dart';
import '../services/tts_service.dart';
import '../models/history_model.dart';
import '../widgets/mint_card.dart';
import '../widgets/waveform_widget.dart';
import 'history_screen.dart';
import 'settings_screen.dart';

// ═══════════════════════════════════════════════
//  STUDIO SCREEN — Main TTS Interface
// ═══════════════════════════════════════════════

class StudioScreen extends StatefulWidget {
  const StudioScreen({super.key});
  @override
  State<StudioScreen> createState() => _StudioState();
}

class _StudioState extends State<StudioScreen> {
  // State
  String _language = 'Urdu';
  String _gender = 'Male';
  String _emotion = 'Normal';
  String _character = '';
  String _preset = '';
  double _speed = 50;
  double _pitch = 0;
  bool _generating = false;
  bool _audioReady = false;
  bool _playing = false;
  String _status = 'Ready to generate voice';
  double _progress = 0;

  // Advanced
  bool _useBreaths = false;
  bool _adaptivePacing = false;
  bool _ssmlMode = false;
  bool _lowLatency = false;

  // Text
  final _textCtrl = TextEditingController();
  File? _audioFile;
  final _player = AudioPlayer();

  @override
  void dispose() {
    _textCtrl.dispose();
    _player.dispose();
    super.dispose();
  }

  // ── LANGUAGE VALIDATION ─────────────────────
  bool _validateTextForLanguage(String text) {
    if (text.trim().isEmpty) return false;

    if (_language == 'Urdu') {
      // Urdu text should contain Arabic/Urdu script chars
      final urduRange = RegExp(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]');
      return urduRange.hasMatch(text);
    }
    if (_language == 'Hindi') {
      // Hindi text should contain Devanagari
      final hindiRange = RegExp(r'[\u0900-\u097F]');
      return hindiRange.hasMatch(text);
    }
    // English: should not be pure non-Latin
    return true;
  }

  String _getHintText() {
    switch (_language) {
      case 'Urdu': return 'یہاں اردو میں لکھیں...';
      case 'Hindi': return 'यहाँ हिंदी में लिखें...';
      default: return 'Type your text here in English...';
    }
  }

  TextDirection _getTextDir() {
    return kLanguages[_language]?.isRtl == true ? TextDirection.rtl : TextDirection.ltr;
  }

  // ── GENERATE ────────────────────────────────
  Future<void> _generate() async {
    final text = _textCtrl.text.trim();
    if (text.isEmpty) {
      _showSnack('Please enter some text first!', isError: true);
      return;
    }

    if (!_validateTextForLanguage(text)) {
      _showLangError(text);
      return;
    }

    setState(() {
      _generating = true;
      _audioReady = false;
      _progress = 0;
      _status = 'Starting voice generation...';
    });

    // Progress animation
    _animateProgress();

    final result = await TtsService.generate(
      text: text,
      language: _language,
      gender: _gender,
      speedPct: _speed.round(),
      pitchVal: _pitch.round(),
      emotion: _emotion,
      character: _character,
      preset: _preset,
      useBreaths: _useBreaths,
      adaptivePacing: _adaptivePacing,
      ssmlMode: _ssmlMode,
      lowLatency: _lowLatency,
    );

    if (!mounted) return;

    if (result.ok) {
      _audioFile = result.file;
      await _player.setFilePath(result.file!.path);
      setState(() {
        _generating = false;
        _audioReady = true;
        _progress = 1.0;
        _status = 'Audio ready! Tap Preview to listen.';
      });
    } else {
      setState(() {
        _generating = false;
        _progress = 0;
        _status = result.error ?? 'Generation failed';
      });
      _showSnack(result.error ?? 'Failed', isError: true);
    }
  }

  void _animateProgress() async {
    final steps = [0.1, 0.25, 0.45, 0.65, 0.80, 0.90];
    final labels = ['Selecting voice...', 'Checking connection...', 'Generating audio...', 'Processing...', 'Almost done...', 'Finalizing...'];
    for (int i = 0; i < steps.length; i++) {
      await Future.delayed(const Duration(milliseconds: 400));
      if (!mounted || !_generating) break;
      setState(() { _progress = steps[i]; _status = labels[i]; });
    }
  }

  // ── LANG ERROR DIALOG ───────────────────────
  void _showLangError(String text) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: cBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(children: [
          Icon(Icons.warning_rounded, color: cAmber, size: 26),
          const SizedBox(width: 10),
          const Text('Wrong Language', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cText)),
        ]),
        content: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(
            _language == 'Urdu'
                ? 'You selected Urdu but the text doesn\'t appear to be in Urdu script (اردو).\n\nPlease type in Urdu or switch to English/Hindi.'
                : 'You selected Hindi but the text doesn\'t contain Hindi (Devanagari) script.\n\nPlease type in Hindi or switch to another language.',
            style: const TextStyle(fontSize: 14, color: cText, height: 1.5),
          ),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('OK', style: TextStyle(color: cGreen, fontWeight: FontWeight.w700))),
        ],
      ),
    );
  }

  // ── PLAY / STOP ─────────────────────────────
  Future<void> _togglePlay() async {
    if (!_audioReady || _audioFile == null) return;
    if (_playing) {
      await _player.stop();
      setState(() => _playing = false);
    } else {
      await _player.seek(Duration.zero);
      await _player.play();
      setState(() => _playing = true);
      _player.playerStateStream.listen((state) {
        if (state.processingState == ProcessingState.completed && mounted) {
          setState(() => _playing = false);
        }
      });
    }
  }

  // ── SAVE ────────────────────────────────────
  Future<void> _save() async {
    if (!_audioReady || _audioFile == null) return;
    final ts = DateTime.now().millisecondsSinceEpoch;
    final fname = 'Titan_${_language}_${_gender}_$ts.mp3';
    try {
      final saved = await TtsService.savePermanent(_audioFile!, fname);
      await HistoryService.add(HistoryEntry(
        id: const Uuid().v4(),
        filename: fname,
        path: saved.path,
        language: _language,
        gender: _gender,
        emotion: _emotion,
        timestamp: DateTime.now().toString().substring(0, 16),
      ));
      if (mounted) _showSaveSuccess(fname, saved.path);
    } catch (e) {
      if (mounted) _showSnack('Save failed: $e', isError: true);
    }
  }

  void _showSaveSuccess(String fname, String path) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: cBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(children: [
          Icon(Icons.check_circle_rounded, color: cGreen, size: 26),
          SizedBox(width: 10),
          Text('Saved!', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: cText)),
        ]),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          Text(fname, style: const TextStyle(fontSize: 13, color: cText, fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          Text(path, style: const TextStyle(fontSize: 11, color: cMuted)),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Great!', style: TextStyle(color: cGreen, fontWeight: FontWeight.w700))),
        ],
      ),
    );
  }

  void _showSnack(String msg, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg, style: const TextStyle(color: Colors.white)),
      backgroundColor: isError ? cRed : cGreen,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.all(12),
    ));
  }

  // ── APPLY CHARACTER ─────────────────────────
  void _applyCharacter(String name) {
    // FIX: Character keeps current preset if set
    final c = kCharacters[name]!;
    setState(() {
      _character = name;
      _preset = '';
      _gender = c.gender;
      _speed = c.speed.toDouble();
      _pitch = c.pitch.toDouble();
      _emotion = c.emotion;
    });
  }

  // ── APPLY PRESET ────────────────────────────
  void _applyPreset(String name) {
    final p = kPresets[name]!;
    setState(() {
      _preset = name;
      // FIX: Keep character — preset applies on top of character
      _speed = p.speed.toDouble();
      _pitch = p.pitch.toDouble();
      _emotion = p.emotion;
    });
  }

  // ═══════════════════════════════════════════
  //  BUILD
  // ═══════════════════════════════════════════
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: cBg,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _buildCharacters(),
                    const SizedBox(height: 12),
                    _buildPresets(),
                    const SizedBox(height: 12),
                    _buildLangGender(),
                    const SizedBox(height: 12),
                    _buildEmotions(),
                    const SizedBox(height: 12),
                    _buildSpeedPitch(),
                    const SizedBox(height: 12),
                    _buildAdvanced(),
                    const SizedBox(height: 12),
                    _buildTextInput(),
                    const SizedBox(height: 12),
                    _buildStatusCard(),
                    const SizedBox(height: 14),
                    _buildGenerateBtn(),
                    const SizedBox(height: 10),
                    _buildPlaySave(),
                    const SizedBox(height: 10),
                    _buildNavRow(),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── HEADER ───────────────────────────────────
  Widget _buildHeader() => Container(
    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
    decoration: const BoxDecoration(color: cBg2, border: Border(bottom: BorderSide(color: cBorder))),
    child: Row(children: [
      Container(
        width: 42, height: 42,
        decoration: BoxDecoration(color: cCard, borderRadius: BorderRadius.circular(12), border: Border.all(color: cBorder), boxShadow: [BoxShadow(color: cGreen.withOpacity(0.3), blurRadius: 14)]),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: Image.asset(
            'assets/icons/logo.png',
            fit: BoxFit.contain,
            errorBuilder: (_, __, ___) => const Center(
              child: Text('T', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Colors.white)),
            ),
          ),
        ),
      ),
      const SizedBox(width: 10),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Titan Studio PRO', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: cText)),
        const Text('v2.0  ·  Always Free', style: TextStyle(fontSize: 11, color: cMuted)),
      ])),
      GestureDetector(
        onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())),
        child: Container(
          width: 42, height: 42,
          decoration: BoxDecoration(color: cCard, borderRadius: BorderRadius.circular(12), border: Border.all(color: cBorder)),
          child: const Icon(Icons.settings_rounded, color: cGreen, size: 22),
        ),
      ),
    ]),
  );

  // ── CHARACTERS ───────────────────────────────
  Widget _buildCharacters() => MintCard(
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const SectionHeader('Characters'),
      const SizedBox(height: 10),
      SizedBox(
        height: 90,
        child: ListView(
          scrollDirection: Axis.horizontal,
          children: kCharacters.entries.map((e) {
            final selected = _character == e.key;
            return GestureDetector(
              onTap: () => _applyCharacter(e.key),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                margin: const EdgeInsets.only(right: 10),
                width: 72,
                decoration: BoxDecoration(
                  color: selected ? cGreen : cSurface,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: selected ? cGreen : cBorder, width: 1.5),
                ),
                child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Text(e.value.icon, style: const TextStyle(fontSize: 26)),
                  const SizedBox(height: 4),
                  Text(e.key, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: selected ? Colors.white : cText)),
                  Text(e.value.gender[0], style: TextStyle(fontSize: 10, color: selected ? Colors.white70 : cMuted)),
                ]),
              ),
            );
          }).toList(),
        ),
      ),
    ]),
  );

  // ── PRESETS ───────────────────────────────────
  Widget _buildPresets() => MintCard(
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const SectionHeader('Voice Presets'),
      const SizedBox(height: 10),
      SizedBox(
        height: 80,
        child: ListView(
          scrollDirection: Axis.horizontal,
          children: kPresets.entries.map((e) {
            final selected = _preset == e.key;
            return GestureDetector(
              onTap: () => _applyPreset(e.key),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                margin: const EdgeInsets.only(right: 10),
                width: 76,
                decoration: BoxDecoration(
                  color: selected ? cGreen2 : cSurface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: selected ? cGreen2 : cBorder),
                ),
                child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Text(e.value.icon, style: const TextStyle(fontSize: 22)),
                  const SizedBox(height: 4),
                  Text(e.key, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: selected ? Colors.white : cText)),
                ]),
              ),
            );
          }).toList(),
        ),
      ),
    ]),
  );

  // ── LANGUAGE + GENDER ────────────────────────
  Widget _buildLangGender() => Row(children: [
    Expanded(
      child: MintCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const SectionHeader('Language'),
          const SizedBox(height: 8),
          ...kLanguages.keys.map((lang) {
            final cfg = kLanguages[lang]!;
            final sel = _language == lang;
            return GestureDetector(
              onTap: () => setState(() { _language = lang; _textCtrl.clear(); _audioReady = false; }),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                margin: const EdgeInsets.only(bottom: 6),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: sel ? cGreen : cSurface,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: sel ? cGreen : cBorder),
                ),
                child: Row(children: [
                  Text(cfg.flag, style: const TextStyle(fontSize: 16)),
                  const SizedBox(width: 8),
                  Text(lang, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: sel ? Colors.white : cText)),
                  const Spacer(),
                  Text(cfg.label, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: sel ? Colors.white70 : cMuted)),
                ]),
              ),
            );
          }),
        ]),
      ),
    ),
    const SizedBox(width: 10),
    SizedBox(
      width: 120,
      child: MintCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const SectionHeader('Gender'),
          const SizedBox(height: 8),
          ...['Male', 'Female'].map((g) {
            final sel = _gender == g;
            return GestureDetector(
              onTap: () => setState(() { _gender = g; _character = ''; }),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                margin: const EdgeInsets.only(bottom: 6),
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: BoxDecoration(
                  color: sel ? cGreen : cSurface,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: sel ? cGreen : cBorder),
                ),
                child: Center(child: Column(children: [
                  Text(g == 'Male' ? '👨' : '👩', style: const TextStyle(fontSize: 20)),
                  const SizedBox(height: 4),
                  Text(g, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: sel ? Colors.white : cText)),
                ])),
              ),
            );
          }),
        ]),
      ),
    ),
  ]);

  // ── EMOTIONS ─────────────────────────────────
  Widget _buildEmotions() => MintCard(
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const SectionHeader('Emotion & Mood'),
      const SizedBox(height: 10),
      Wrap(
        spacing: 8, runSpacing: 8,
        children: kEmotions.entries.map((e) {
          final sel = _emotion == e.key;
          return GestureDetector(
            onTap: () => setState(() { _emotion = e.key; _character = ''; _preset = ''; }),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: sel ? e.value.color : cSurface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: sel ? e.value.color : cBorder),
              ),
              child: Row(mainAxisSize: MainAxisSize.min, children: [
                Text(e.value.icon, style: const TextStyle(fontSize: 14)),
                const SizedBox(width: 5),
                Text(e.key, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: sel ? Colors.white : cText)),
              ]),
            ),
          );
        }).toList(),
      ),
    ]),
  );

  // ── SPEED + PITCH ─────────────────────────────
  Widget _buildSpeedPitch() => Column(children: [
    MintCard(
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const SectionHeader('Speed'),
          const Spacer(),
          Text('${_speed.round()}%', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cGreen)),
        ]),
        Row(children: [
          const Text('Slow', style: TextStyle(fontSize: 11, color: cMuted)),
          Expanded(child: SliderTheme(
            data: SliderTheme.of(context).copyWith(activeTrackColor: cGreen, thumbColor: cGreen, inactiveTrackColor: cBorder, overlayColor: cGreen.withOpacity(0.1), trackHeight: 4),
            child: Slider(min: 10, max: 100, divisions: 18, value: _speed, onChanged: (v) => setState(() { _speed = v; _character = ''; _preset = ''; })),
          )),
          const Text('Fast', style: TextStyle(fontSize: 11, color: cMuted)),
        ]),
      ]),
    ),
    const SizedBox(height: 10),
    MintCard(
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const SectionHeader('Pitch'),
          const Spacer(),
          Text('${_pitch >= 0 ? '+' : ''}${_pitch.round()}', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cGreen)),
        ]),
        Row(children: [
          const Text('Low', style: TextStyle(fontSize: 11, color: cMuted)),
          Expanded(child: SliderTheme(
            data: SliderTheme.of(context).copyWith(activeTrackColor: cGreen, thumbColor: cGreen, inactiveTrackColor: cBorder, overlayColor: cGreen.withOpacity(0.1), trackHeight: 4),
            child: Slider(min: -10, max: 10, divisions: 20, value: _pitch, onChanged: (v) => setState(() { _pitch = v; _character = ''; _preset = ''; })),
          )),
          const Text('High', style: TextStyle(fontSize: 11, color: cMuted)),
        ]),
      ]),
    ),
  ]);

  // ── ADVANCED OPTIONS ─────────────────────────
  Widget _buildAdvanced() {
    return MintCard(
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const SectionHeader('Advanced Options'),
        const SizedBox(height: 8),
        _advToggle('Dynamic Breath Simulation', _useBreaths, (v) => setState(() => _useBreaths = v)),
        _advToggle('Adaptive Pacing (long text)', _adaptivePacing, (v) => setState(() => _adaptivePacing = v)),
        _advToggle('SSML Markup Support', _ssmlMode, (v) => setState(() => _ssmlMode = v)),
        _advToggle('Ultra-Low Latency Mode', _lowLatency, (v) => setState(() => _lowLatency = v)),
      ]),
    );
  }

  Widget _advToggle(String label, bool val, ValueChanged<bool> onChanged) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 4),
    child: Row(children: [
      Expanded(child: Text(label, style: const TextStyle(fontSize: 13, color: cText2))),
      Switch.adaptive(
        value: val, onChanged: onChanged,
        activeColor: cGreen, activeTrackColor: cGreenL.withOpacity(0.4),
        inactiveThumbColor: cMuted2, inactiveTrackColor: cBorder,
      ),
    ]),
  );

  // ── TEXT INPUT ───────────────────────────────
  Widget _buildTextInput() {
    final langCfg = kLanguages[_language]!;
    return MintCard(
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          SectionHeader('Input Text'),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(color: cGreen.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
            child: Text(langCfg.flag + ' ' + _language, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: cGreen)),
          ),
          const Spacer(),
          Text('${_textCtrl.text.length} chars', style: const TextStyle(fontSize: 11, color: cMuted)),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: () => setState(() => _textCtrl.clear()),
            child: Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(color: cRed.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
              child: const Icon(Icons.clear_rounded, color: cRed, size: 16),
            ),
          ),
        ]),
        if (langCfg.isRtl) ...[
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(color: cAmber.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
            child: Row(children: [
              const Icon(Icons.info_outline_rounded, color: cAmber, size: 14),
              const SizedBox(width: 6),
              Expanded(child: Text('RTL Mode — Please write in ${_language} script only', style: const TextStyle(fontSize: 11, color: cAmber))),
            ]),
          ),
        ],
        const SizedBox(height: 10),
        Directionality(
          textDirection: _getTextDir(),
          child: TextField(
            controller: _textCtrl,
            maxLines: 6,
            style: const TextStyle(fontSize: 15, color: cText2, height: 1.5),
            textDirection: _getTextDir(),
            textAlign: langCfg.isRtl ? TextAlign.right : TextAlign.left,
            decoration: InputDecoration(
              hintText: _getHintText(),
              hintStyle: TextStyle(color: cMuted2, fontSize: 14),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: cBorder)),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: cGreen, width: 2)),
              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: cBorder)),
              filled: true, fillColor: cCard2,
              contentPadding: const EdgeInsets.all(12),
            ),
            onChanged: (_) => setState(() {}),
          ),
        ),
      ]),
    );
  }

  // ── STATUS CARD ──────────────────────────────
  Widget _buildStatusCard() => MintCard(
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: Icon(_generating ? Icons.hourglass_top_rounded : (_audioReady ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded),
            key: ValueKey(_generating ? 0 : (_audioReady ? 1 : 2)),
            color: _generating ? cAmber : (_audioReady ? cGreen : cMuted), size: 18),
        ),
        const SizedBox(width: 8),
        Expanded(child: Text(_status, style: const TextStyle(fontSize: 13, color: cText2))),
      ]),
      const SizedBox(height: 10),
      ClipRRect(
        borderRadius: BorderRadius.circular(6),
        child: LinearProgressIndicator(
          value: _generating ? null : _progress,
          backgroundColor: cBorder,
          valueColor: AlwaysStoppedAnimation<Color>(_generating ? cAmber : cGreen),
          minHeight: 5,
        ),
      ),
      const SizedBox(height: 8),
      WaveformWidget(active: _generating || _playing),
    ]),
  );

  // ── GENERATE BUTTON ──────────────────────────
  Widget _buildGenerateBtn() => GestureDetector(
    onTap: _generating ? null : _generate,
    child: AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      height: 64,
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: _generating ? [cMuted, cMuted2] : [cGreen, cGreen2]),
        borderRadius: BorderRadius.circular(18),
        boxShadow: _generating ? [] : [BoxShadow(color: cGreen.withOpacity(0.35), blurRadius: 16, offset: const Offset(0, 6))],
      ),
      child: Center(child: _generating
        ? const Row(mainAxisSize: MainAxisSize.min, children: [
            SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5)),
            SizedBox(width: 12),
            Text('Generating...', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Colors.white)),
          ])
        : const Row(mainAxisSize: MainAxisSize.min, children: [
            Icon(Icons.graphic_eq_rounded, color: Colors.white, size: 28),
            SizedBox(width: 10),
            Text('Generate Audio', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Colors.white)),
          ]),
      ),
    ),
  );

  // ── PLAY + SAVE ───────────────────────────────
  Widget _buildPlaySave() => Row(children: [
    Expanded(child: GestureDetector(
      onTap: _audioReady ? _togglePlay : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        height: 54,
        decoration: BoxDecoration(
          color: _audioReady ? (_playing ? cAmber : cTeal) : cSurface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: _audioReady ? Colors.transparent : cBorder),
        ),
        child: Center(child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(_playing ? Icons.stop_rounded : Icons.play_arrow_rounded, color: _audioReady ? Colors.white : cMuted, size: 22),
          const SizedBox(width: 6),
          Text(_playing ? 'Stop' : 'Preview', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: _audioReady ? Colors.white : cMuted)),
        ])),
      ),
    )),
    const SizedBox(width: 10),
    Expanded(child: GestureDetector(
      onTap: _audioReady ? _save : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        height: 54,
        decoration: BoxDecoration(
          color: _audioReady ? cGreen2 : cSurface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: _audioReady ? Colors.transparent : cBorder),
        ),
        child: Center(child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.save_alt_rounded, color: _audioReady ? Colors.white : cMuted, size: 20),
          const SizedBox(width: 6),
          Text('Save Voice', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: _audioReady ? Colors.white : cMuted)),
        ])),
      ),
    )),
  ]);

  // ── NAV ROW ───────────────────────────────────
  Widget _buildNavRow() => Row(children: [
    Expanded(child: GestureDetector(
      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const HistoryScreen())),
      child: Container(
        height: 50, decoration: BoxDecoration(color: cPurple.withOpacity(0.1), borderRadius: BorderRadius.circular(14), border: Border.all(color: cPurple.withOpacity(0.3))),
        child: const Center(child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.history_rounded, color: cPurple, size: 20),
          SizedBox(width: 8),
          Text('History', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: cPurple)),
        ])),
      ),
    )),
  ]);
}
