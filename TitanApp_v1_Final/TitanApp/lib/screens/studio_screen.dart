import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
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
  String _language = 'English';
  String _gender = 'Male';   // Adam default — Male
  String _emotion = 'Normal';
  String _character = 'Adam'; // ── DEFAULT: Adam always selected on open ──
  String _preset = '';
  double _speed = 55;   // Adam ka speed
  double _pitch = 0;    // Adam ka pitch
  bool _generating = false;
  bool _audioReady = false;
  bool _playing = false;
  String _status = 'Ready to generate voice';
  double _progress = 0;

  // Advanced Options
  bool _useBreaths    = false;
  bool _adaptivePacing = false;
  bool _ssmlMode      = false;
  bool _lowLatency    = false;
  // HD Neural features
  bool _hdVoice        = false;  // HD Neural quality
  bool _autoEmotion    = false;  // Auto sentiment detection
  bool _wordBoundary   = false;  // Word-level timing (karaoke/subtitles)
  bool _avatarMode     = false;  // Photorealistic avatar (future)
  // New v1.0 Voice Customization features
  bool _cnvMode        = false;  // Custom Neural Voice persona
  bool _crossLingual   = false;  // Cross-lingual voice persona
  bool _brandVoice     = false;  // Brand voice persona
  String _brandName    = '';     // Brand/persona name

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
    final cfg = kLanguages[_language];
    if (cfg == null) return true;
    switch (cfg.script) {
      case LangScript.arabic:
        final r = RegExp(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\u05D0-\u05EA]');
        return r.hasMatch(text);
      case LangScript.devanagari:
        final r = RegExp(r'[\u0900-\u097F\u0A00-\u0A7F]');
        return r.hasMatch(text);
      case LangScript.cjk:
        final r = RegExp(r'[\u3000-\u9FFF\uAC00-\uD7AF]');
        return r.hasMatch(text);
      case LangScript.cyrillic:
        final r = RegExp(r'[\u0400-\u04FF]');
        return r.hasMatch(text);
      default:
        return true;
    }
  }

  String _getHintText() => getLangHint(_language);

  String _getHintText_OLD() {
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
    HapticFeedback.lightImpact();
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
    final fname = 'Titan_${_language}_${_gender}_$ts.wav';
    try {
      final saved = await TtsService.savePermanent(_audioFile!, fname);

      // ── FIX: Verify saved file exists and has content before adding to history ──
      if (!await saved.exists() || await saved.length() < 500) {
        if (mounted) _showSnack('Save failed: file empty or missing', isError: true);
        return;
      }

      await HistoryService.add(HistoryEntry(
        id: const Uuid().v4(),
        filename: saved.path.split('/').last, // actual saved filename
        path: saved.path,                     // permanent path (not temp!)
        language: _language,
        gender: _gender,
        emotion: _emotion,
        timestamp: DateTime.now().toString().substring(0, 16),
      ));
      if (mounted) _showSaveSuccess(saved.path.split('/').last, saved.path);
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

  // ── INCOMPATIBLE CHARACTER + PRESET COMBOS ──
  // Yeh combinations select nahi ho sakti
  static const Map<String, List<String>> _blockedCombos = {
    'Sage':  ['Kids', 'Commercial', 'Story'],
    'Aria':  ['Commercial', 'Newsreader'],
    'Nova':  ['Kids', 'Meditation'],
    'Bolt':  ['Kids', 'Meditation'],
    'Rex':   ['Kids'],
    'Zara':  ['Kids'],
    'Adam':  ['Kids'],
  };

  bool _isPresetBlocked(String presetName) {
    if (_character.isEmpty) return false;
    return (_blockedCombos[_character] ?? []).contains(presetName);
  }

  // ── APPLY CHARACTER ─────────────────────────
  void _applyCharacter(String name) {
    final c = kCharacters[name]!;
    setState(() {
      _character = name;
      _emotion   = c.emotion;
      _speed     = c.speed.toDouble();
      _pitch     = c.pitch.toDouble();
      _gender    = c.gender;
      // ── Auto-select best language for this character ──
      if (c.bestLangs.isNotEmpty && !c.bestLangs.contains(_language)) {
        _language = c.bestLangs.first;
        _textCtrl.clear();
        _audioReady = false;
      }
      // ── Auto-select default preset ──
      if (c.defaultPreset.isNotEmpty) {
        _preset = c.defaultPreset;
      }
    });
  }

  // ── APPLY PRESET ────────────────────────────
  void _applyPreset(String name) {
    // Block incompatible combo
    if (_isPresetBlocked(name)) return;

    final p = kPresets[name]!;
    setState(() {
      _preset = name;
      _speed = p.speed.toDouble();
      _pitch = p.pitch.toDouble();
      _emotion = p.emotion;
      // Gender hamesha character ka hi rahega
      if (_character.isNotEmpty) {
        _gender = kCharacters[_character]!.gender;
      }
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
        const Text('v1.0  ·  Always Free', style: TextStyle(fontSize: 11, color: cMuted)),
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
        height: 100,
        child: ListView(
          scrollDirection: Axis.horizontal,
          children: kCharacters.entries.map((e) {
            final selected = _character == e.key;
            final cfg = e.value;
            return GestureDetector(
              onTap: () => _applyCharacter(e.key),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                margin: const EdgeInsets.only(right: 10),
                width: 76,
                decoration: BoxDecoration(
                  color: selected ? cGreen : cSurface,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: selected ? cGreen : cBorder, width: 1.5),
                  boxShadow: selected ? [BoxShadow(color: cGreen.withOpacity(0.3), blurRadius: 8)] : [],
                ),
                child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  SvgPicture.asset(cfg.icon, width: selected ? 30 : 26, height: selected ? 30 : 26,
                    colorFilter: const ColorFilter.mode(Color(0xFF00FFFF), BlendMode.srcIn)),
                  const SizedBox(height: 3),
                  Text(e.key, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                    color: selected ? Colors.white : cText)),
                  if (cfg.specialtyLabel.isNotEmpty)
                    Text(cfg.specialtyLabel, style: TextStyle(fontSize: 9,
                      color: selected ? cGreenL : cMuted, height: 1.2),
                      textAlign: TextAlign.center,
                      maxLines: 1, overflow: TextOverflow.ellipsis),
                ]),
              ),
            );
          }).toList(),
        ),
      ),
      // ── Specialty hint for selected character ──
      if (_character.isNotEmpty) ...[
        const SizedBox(height: 8),
        AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
          decoration: BoxDecoration(
            color: cGreen3,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: cBorder),
          ),
          child: Row(children: [
            const Icon(Icons.auto_awesome_rounded, size: 13, color: cGreen),
            const SizedBox(width: 6),
            Expanded(child: Text(
              kCharacters[_character]?.specialtyDesc ?? '',
              style: const TextStyle(fontSize: 11, color: cGreenL, height: 1.3),
            )),
          ]),
        ),
      ],
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
            final blocked = _isPresetBlocked(e.key);
            return GestureDetector(
              onTap: blocked ? null : () => _applyPreset(e.key),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                margin: const EdgeInsets.only(right: 10),
                width: 76,
                decoration: BoxDecoration(
                  color: blocked ? cSurface.withOpacity(0.4) : (selected ? cGreen2 : cSurface),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: blocked ? cBorder.withOpacity(0.3) : (selected ? cGreen2 : cBorder),
                  ),
                ),
                child: Stack(
                  children: [
                    Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                      Center(child: SvgPicture.asset(e.value.icon, width: 24, height: 24, colorFilter: ColorFilter.mode(blocked ? Colors.white24 : const Color(0xFF00FFFF), BlendMode.srcIn))),
                      const SizedBox(height: 4),
                      Center(child: Text(e.key, style: TextStyle(
                        fontSize: 10, fontWeight: FontWeight.w700,
                        color: blocked ? cMuted.withOpacity(0.3) : (selected ? Colors.white : cText),
                      ))),
                    ]),
                    // Lock icon for blocked presets
                    if (blocked)
                      const Positioned(
                        top: 4, right: 4,
                        child: Icon(Icons.lock_rounded, size: 11, color: Colors.white24),
                      ),
                  ],
                ),
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
          SizedBox(
            height: 200,
            child: ListView(
              children: kLanguages.keys.map((lang) {
                final cfg = kLanguages[lang]!;
                final sel = _language == lang;
                return GestureDetector(
                  onTap: () {
                    final compatible = getCharactersForLang(lang);
                    setState(() {
                      _language = lang;
                      _textCtrl.clear();
                      _audioReady = false;
                      if (compatible.isNotEmpty && !compatible.contains(_character)) {
                        _applyCharacter(compatible.first);
                      }
                    });
                  },
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
                      SvgPicture.asset(cfg.flag, width: 22, height: 22),
                      const SizedBox(width: 8),
                      Text(lang, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: sel ? Colors.white : cText)),
                      const Spacer(),
                      Text(cfg.label, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: sel ? Colors.white70 : cMuted)),
                    ]),
                  ),
                );
              }).toList(),
            ),
          ),
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
            return AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              margin: const EdgeInsets.only(bottom: 6),
              padding: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(
                color: sel ? cGreen : cSurface,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: sel ? cGreen : cBorder),
              ),
              child: Center(child: Column(children: [
                SvgPicture.asset(g == 'Male' ? 'assets/svg/gender_male.svg' : 'assets/svg/gender_female.svg', width: 22, height: 22, colorFilter: const ColorFilter.mode(Color(0xFF00FFFF), BlendMode.srcIn)),
                const SizedBox(height: 4),
                Text(g, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: sel ? Colors.white : cText)),
                const SizedBox(height: 2),
                // Lock icon — gender is always character-controlled
                Icon(Icons.lock_rounded, size: 10, color: sel ? Colors.white54 : cMuted.withOpacity(0.4)),
              ])),
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
          // ── Agar character selected hai to sirf uske allowed emotions active hon ──
          final allowed = _character.isEmpty
              ? true
              : (kCharacters[_character]?.allowedEmotions ?? []).contains(e.key);
          return GestureDetector(
            onTap: allowed ? () {
              final cfg = kEmotions[e.key]!;
              setState(() {
                _emotion = e.key;
                _preset  = '';
                // ── Auto speed + pitch from emotion ──
                _speed = cfg.speed;
                _pitch = cfg.pitch.toDouble();
              });
            } : null,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: !allowed
                    ? cSurface.withOpacity(0.4)
                    : sel ? e.value.color : cSurface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: !allowed
                      ? cBorder.withOpacity(0.3)
                      : sel ? e.value.color : cBorder,
                ),
              ),
              child: Row(mainAxisSize: MainAxisSize.min, children: [
                SvgPicture.asset(e.value.icon, width: 16, height: 16, colorFilter: ColorFilter.mode(allowed ? const Color(0xFF00FFFF) : Colors.white24, BlendMode.srcIn)),
                const SizedBox(width: 5),
                Text(e.key, style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: !allowed
                      ? cMuted.withOpacity(0.3)
                      : sel ? Colors.white : cText,
                )),
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
            child: Slider(min: 10, max: 100, divisions: 18, value: _speed, onChanged: (v) => setState(() { _speed = v; _preset = ''; })),
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
            child: Slider(min: -10, max: 10, divisions: 20, value: _pitch, onChanged: (v) => setState(() { _pitch = v; _preset = ''; })),
          )),
          const Text('High', style: TextStyle(fontSize: 11, color: cMuted)),
        ]),
      ]),
    ),
  ]);

  // ── ADVANCED OPTIONS ─────────────────────────
  Widget _buildAdvanced() {
    return MintCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const SectionHeader('Advanced Options'),
      const SizedBox(height: 6),

      // ── SECTION 1: Core Audio ─────────────────────────
      _sectionLabel('🔊 Core Audio', Icons.tune_rounded),
      const SizedBox(height: 6),
      _advToggle('Dynamic Breath Simulation', '(Natural breathing pauses in audio)',
        Icons.air_rounded, _useBreaths, (v) => setState(() => _useBreaths = v)),
      _advToggle('Adaptive Pacing', '(Auto slows for long text 300+ chars)',
        Icons.speed_rounded, _adaptivePacing, (v) => setState(() => _adaptivePacing = v)),
      _advToggle('Ultra-Low Latency Mode', '(Faster response, shorter texts)',
        Icons.bolt_rounded, _lowLatency, (v) => setState(() => _lowLatency = v)),

      const Divider(color: Color(0xFF1E2D45), height: 20),

      // ── SECTION 2: SSML ───────────────────────────────
      _sectionLabel('💻 SSML Markup', Icons.code_rounded),
      const SizedBox(height: 6),
      _advToggle('SSML Markup Support',
        '(Use <break>, <emphasis>, <prosody> tags)',
        Icons.code_rounded, _ssmlMode, (v) => setState(() => _ssmlMode = v)),
      _advToggle('Word-Boundary Sync',
        '(Exact word timing — karaoke, avatars, captions)',
        Icons.closed_caption_rounded, _wordBoundary, (v) => setState(() => _wordBoundary = v)),

      if (_ssmlMode) ...[
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: const Color(0xFF0B0F19),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFF1E2D45)),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('SSML Quick Reference',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF00F2FE))),
            const SizedBox(height: 4),
            ...['<break time="500ms"/>  — pause',
                '<emphasis level="strong">word</emphasis>',
                '<prosody rate="slow" pitch="high">text</prosody>',
                '<say-as interpret-as="characters">ABC</say-as>',
            ].map((t) => Padding(
              padding: const EdgeInsets.only(bottom: 2),
              child: Text(t, style: const TextStyle(
                fontSize: 10, color: Color(0xFF5A6A7E), fontFamily: 'monospace')),
            )),
          ]),
        ),
      ],

      const Divider(color: Color(0xFF1E2D45), height: 20),

      // ── SECTION 3: HD Neural AI ───────────────────────
      _sectionLabel('✨ HD Neural AI', Icons.auto_awesome_rounded),
      const SizedBox(height: 6),
      _advToggle('HD Neural Voice', '(Higher quality audio — Azure HD voices)',
        Icons.hd_rounded, _hdVoice, (v) => setState(() => _hdVoice = v)),
      _advToggle('Auto Emotion Detection',
        '(AI detects text sentiment & auto-sets emotion)',
        Icons.psychology_rounded, _autoEmotion,
        (v) => setState(() { _autoEmotion = v; if (v) _emotion = 'Normal'; })),
      _advToggle('Avatar Mode (Beta)',
        '(Photorealistic speaking avatar — coming soon)',
        Icons.face_rounded, _avatarMode,
        (v) => setState(() => _avatarMode = v), comingSoon: true),

      const Divider(color: Color(0xFF1E2D45), height: 20),

      // ── SECTION 4: Voice Persona ──────────────────────
      _sectionLabel('🎭 Voice Persona & Brand', Icons.record_voice_over_rounded),
      const SizedBox(height: 6),
      _advToggle('Custom Neural Voice (CNV)',
        '(Train branded voice — 30 min audio needed)',
        Icons.mic_rounded, _cnvMode,
        (v) => setState(() => _cnvMode = v), comingSoon: true),
      _advToggle('Cross-Lingual Persona',
        '(Same voice across all 39 languages)',
        Icons.translate_rounded, _crossLingual,
        (v) => setState(() => _crossLingual = v), comingSoon: true),
      _advToggle('Brand Voice Persona',
        '(Custom brand identity for your voice)',
        Icons.campaign_rounded, _brandVoice,
        (v) => setState(() => _brandVoice = v), comingSoon: true),

      if (_cnvMode || _crossLingual || _brandVoice) ...[
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: const Color(0xFF0B0F19),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFF1E2D45)),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Row(children: [
              Icon(Icons.info_outline_rounded, size: 12, color: Color(0xFFFFD32A)),
              SizedBox(width: 6),
              Text('Voice Persona Features',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                  color: Color(0xFFFFD32A))),
            ]),
            const SizedBox(height: 6),
            ...['• CNV: Train realistic branded voice with 30min data',
                '• Cross-Lingual: One voice persona → 39 languages',
                '• Brand Voice: Custom AI identity for your product',
                '• Word-Boundary: Sync audio with avatar lips/captions',
            ].map((t) => Padding(
              padding: const EdgeInsets.only(bottom: 3),
              child: Text(t, style: const TextStyle(
                fontSize: 10, color: Color(0xFF8A99AD), height: 1.4)),
            )),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFFFF6B35).withOpacity(0.1),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text('These features require Azure Custom Neural Voice subscription',
                style: TextStyle(fontSize: 10, color: Color(0xFFFF6B35))),
            ),
          ]),
        ),
      ],
    ]));
  }

  Widget _sectionLabel(String label, IconData icon) => Padding(
    padding: const EdgeInsets.only(bottom: 4),
    child: Row(children: [
      Icon(icon, size: 13, color: cGreen),
      const SizedBox(width: 6),
      Text(label, style: const TextStyle(
        fontSize: 12, fontWeight: FontWeight.w700, color: cGreen)),
    ]),
  );

  Widget _advToggle(
    String label,
    String subtitle,
    IconData icon,
    bool value,
    ValueChanged<bool> onChanged, {
    bool comingSoon = false,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(icon, size: 16,
          color: value ? const Color(0xFF00F2FE) : const Color(0xFF5A6A7E)),
        const SizedBox(width: 10),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Text(label, style: TextStyle(
              fontSize: 13, fontWeight: FontWeight.w600,
              color: value ? const Color(0xFFFFFFFF) : const Color(0xFF8A99AD),
            )),
            if (comingSoon) ...[
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFFFF6B35).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Text('SOON',
                  style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800,
                    color: Color(0xFFFF6B35))),
              ),
            ],
          ]),
          Text(subtitle, style: const TextStyle(
            fontSize: 10, color: Color(0xFF5A6A7E), height: 1.3)),
        ])),
        const SizedBox(width: 8),
        Transform.scale(
          scale: 0.85,
          child: Switch(
            value: comingSoon ? false : value,
            onChanged: comingSoon ? null : onChanged,
            activeColor: const Color(0xFF00F2FE),
            activeTrackColor: const Color(0xFF003A55),
            inactiveThumbColor: const Color(0xFF5A6A7E),
            inactiveTrackColor: const Color(0xFF1C2840),
          ),
        ),
      ]),
    );
  }

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
            child: Row(mainAxisSize: MainAxisSize.min, children: [SvgPicture.asset(langCfg.flag, width: 14, height: 14), const SizedBox(width: 4), Text(_language, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: cGreen))]),
          ),
          const Spacer(),
          Text(
            '${_textCtrl.text.length}/1000',
            style: TextStyle(
              fontSize: 11,
              color: _textCtrl.text.length >= 1000 ? cRed : cMuted,
              fontWeight: _textCtrl.text.length >= 1000 ? FontWeight.w700 : FontWeight.normal,
            ),
          ),
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
        // ── 1000 char limit warning ──
        if (_textCtrl.text.length >= 1000) ...[
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(color: cRed.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
            child: const Row(children: [
              Icon(Icons.warning_amber_rounded, color: cRed, size: 14),
              SizedBox(width: 6),
              Expanded(child: Text('Only 1000 characters supported', style: TextStyle(fontSize: 11, color: cRed, fontWeight: FontWeight.w600))),
            ]),
          ),
        ],
        const SizedBox(height: 10),
        Directionality(
          textDirection: _getTextDir(),
          child: TextField(
            controller: _textCtrl,
            maxLines: 6,
            maxLength: 1000,
            buildCounter: (_, {required currentLength, required isFocused, maxLength}) => null,
            style: const TextStyle(fontSize: 15, color: cText2, height: 1.5),
            textDirection: _getTextDir(),
            textAlign: langCfg.isRtl ? TextAlign.right : TextAlign.left,
            decoration: InputDecoration(
              hintText: _getHintText(),
              hintStyle: TextStyle(color: cMuted2, fontSize: 14),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: cBorder)),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: _textCtrl.text.length >= 1000 ? cRed : cGreen, width: 2),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: _textCtrl.text.length >= 1000 ? cRed.withOpacity(0.5) : cBorder),
              ),
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
      WaveformWidget(
        mode: _generating
            ? WaveformMode.loading
            : _playing
                ? WaveformMode.playing
                : WaveformMode.idle,
        height: 52,
        barCount: 36,
      ),
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
          Icon(Icons.download_rounded, color: cPurple, size: 20),
          SizedBox(width: 8),
          Text('Download History', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: cPurple)),
        ])),
      ),
    )),
  ]);
}
