import 'dart:io';
import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
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
import '../services/admin_service.dart';

// ═══════════════════════════════════════════════
//  STUDIO SCREEN — Main TTS Interface
// ═══════════════════════════════════════════════

class StudioScreen extends StatefulWidget {
  const StudioScreen({super.key});
  @override
  State<StudioScreen> createState() => _StudioState();
}

class _StudioState extends State<StudioScreen>
    with WidgetsBindingObserver {
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
  // Voice Persona & Brand — fully functional
  bool _cnvMode        = false;
  bool _crossLingual   = false;
  bool _brandVoice     = false;
  // CNV Persona saved settings
  String _personaName  = '';
  int    _personaSpeed = 55;
  int    _personaPitch = 0;
  String _personaEmotion = 'Normal';
  String _personaGender  = 'Male';
  // Brand Voice saved settings
  String _brandName    = '';
  String _brandPreset  = 'Narrator';
  // Cross-lingual: lock character voice across languages
  String _crossChar    = '';
  // UX helpers
  String _langSearch     = '';
  bool   _showAllChars   = false;

  // ── Admin: disabled characters from Firebase ──
  Set<String> _disabledChars = {};
  int _charLimit = 300; // default, loaded from Firebase admin
  Timer? _adminRefreshTimer;

  // Text
  final _textCtrl = TextEditingController();
  File? _audioFile;
  final _player = AudioPlayer();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    // Load saved persona settings after first frame
    Future.microtask(() => _loadPersona());
    // Load disabled characters + limits from Firebase Admin
    Future.microtask(() => _loadDisabledChars());
    // Refresh admin config every 30 seconds (picks up live changes)
    _adminRefreshTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _loadDisabledChars(),
    );
  }

  // Re-load admin config when app comes back to foreground
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _loadDisabledChars();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _adminRefreshTimer?.cancel();
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

    // ── Internet check ──
    final hasNet = await _checkInternet();
    if (!hasNet) {
      _showNoInternetBanner();
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

    // ── Show saving progress snackbar ──
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Row(children: [
          SizedBox(width: 16, height: 16,
            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)),
          SizedBox(width: 12),
          Text('Saving audio file...', style: TextStyle(color: Colors.white)),
        ]),
        backgroundColor: Color(0xFF003A55),
        duration: Duration(seconds: 10),
      ));
    }

    final ts = DateTime.now().millisecondsSinceEpoch;
    final fname = 'Titan_${_character}_${_language}_$ts.wav';

    try {
      // ── Verify source file ──
      if (!await _audioFile!.exists()) {
        if (mounted) {
          ScaffoldMessenger.of(context).hideCurrentSnackBar();
          _showSnack('Error: audio file missing. Generate again.', isError: true);
        }
        return;
      }

      final srcSize = await _audioFile!.length();
      if (srcSize < 500) {
        if (mounted) {
          ScaffoldMessenger.of(context).hideCurrentSnackBar();
          _showSnack('Error: audio too small ($srcSize bytes). Generate again.', isError: true);
        }
        return;
      }

      // ── Save to Downloads ──
      final saved = await TtsService.savePermanent(_audioFile!, fname);

      // ── Double check saved file ──
      if (!await saved.exists() || await saved.length() < 500) {
        if (mounted) {
          ScaffoldMessenger.of(context).hideCurrentSnackBar();
          _showSnack('Save failed: file not written properly', isError: true);
        }
        return;
      }

      final savedSize = await saved.length();

      // ── Add to history with real path ──
      await HistoryService.add(HistoryEntry(
        id: const Uuid().v4(),
        filename: fname,
        path: saved.path,
        language: _language,
        gender: _gender,
        emotion: _emotion,
        timestamp: DateTime.now().toString().substring(0, 16),
      ));

      if (mounted) {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        _showSaveSuccess(fname, saved.path, savedSize);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        _showSnack('Save failed: $e', isError: true);
      }
    }
  }

  void _showSaveSuccess(String fname, String path, [int sizeBytes = 0]) {
    final sizeKb = (sizeBytes / 1024).toStringAsFixed(1);
    final folder = path.contains('Download')
        ? 'Downloads/TitanStudioPRO/'
        : 'App Documents/TitanStudioPRO/';
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
        content: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          // File name
          Row(children: [
            const Icon(Icons.audio_file_rounded, size: 14, color: cGreen),
            const SizedBox(width: 6),
            Expanded(child: Text(fname,
              style: const TextStyle(fontSize: 12, color: cText, fontWeight: FontWeight.w600))),
          ]),
          const SizedBox(height: 6),
          // Folder
          Row(children: [
            const Icon(Icons.folder_rounded, size: 14, color: cAmber),
            const SizedBox(width: 6),
            Text(folder, style: const TextStyle(fontSize: 11, color: cAmber)),
          ]),
          const SizedBox(height: 6),
          // File size
          if (sizeBytes > 0) Row(children: [
            const Icon(Icons.straighten_rounded, size: 14, color: cMuted),
            const SizedBox(width: 6),
            Text('File size: $sizeKb KB',
              style: const TextStyle(fontSize: 11, color: cMuted)),
          ]),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: cGreen3, borderRadius: BorderRadius.circular(8)),
            child: const Row(children: [
              Icon(Icons.info_outline_rounded, size: 13, color: cGreen),
              SizedBox(width: 6),
              Expanded(child: Text(
                'Find your file in Files app → Downloads → TitanStudioPRO',
                style: TextStyle(fontSize: 10, color: cGreenL, height: 1.4))),
            ]),
          ),
        ]),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Great!', style: TextStyle(color: cGreen, fontWeight: FontWeight.w700))),
        ],
      ),
    );
  }

  // ── Internet helpers ─────────────────────────────────────
  Future<bool> _checkInternet() async {
    try {
      final r = await InternetAddress.lookup('huggingface.co')
          .timeout(const Duration(seconds: 5));
      return r.isNotEmpty && r.first.rawAddress.isNotEmpty;
    } catch (_) {
      return false;
    }
  }

  void _showNoInternetBanner() {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: cBg2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          Container(
            width: 64, height: 64,
            decoration: BoxDecoration(
              color: cAmber.withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(color: cAmber.withOpacity(0.4)),
            ),
            child: const Icon(Icons.wifi_off_rounded, color: cAmber, size: 30),
          ),
          const SizedBox(height: 16),
          const Text('No Internet Connection',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: cText),
              textAlign: TextAlign.center),
          const SizedBox(height: 8),
          const Text('Please turn on WiFi or mobile data to generate audio.',
              style: TextStyle(fontSize: 13, color: cText2, height: 1.5),
              textAlign: TextAlign.center),
          const SizedBox(height: 20),
          GestureDetector(
            onTap: () => Navigator.pop(context),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                gradient: kNeonGradient,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(child: Text('OK',
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700))),
            ),
          ),
        ]),
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
  // ── PERSONA PERSISTENCE ──────────────────────────────
  Future<void> _savePersona() async {
    final p = await SharedPreferences.getInstance();
    await p.setString('persona_name',    _personaName);
    await p.setInt   ('persona_speed',   _personaSpeed);
    await p.setInt   ('persona_pitch',   _personaPitch);
    await p.setString('persona_emotion', _personaEmotion);
    await p.setString('persona_gender',  _personaGender);
    await p.setString('brand_name',      _brandName);
    await p.setString('brand_preset',    _brandPreset);
    await p.setString('cross_char',      _crossChar);
  }

  // ── Load disabled characters from Firebase Admin ──────────
  Future<void> _loadDisabledChars() async {
    try {
      final states = await AdminService.getCharacterStates();
      final limits = await AdminService.getLimitsData();
      if (mounted) {
        setState(() {
          _disabledChars = states.entries
              .where((e) => e.value == false)
              .map((e) => e.key)
              .toSet();
          _charLimit = limits.freeCharLimit;
        });
        if (_disabledChars.contains(_character)) {
          final first = kCharacters.keys
              .firstWhere((k) => !_disabledChars.contains(k), orElse: () => 'Adam');
          _applyCharacter(first);
        }
      }
    } catch (_) {}
  }

  Future<void> _loadPersona() async {
    final p = await SharedPreferences.getInstance();
    setState(() {
      _personaName    = p.getString('persona_name')    ?? '';
      _personaSpeed   = p.getInt   ('persona_speed')   ?? 55;
      _personaPitch   = p.getInt   ('persona_pitch')   ?? 0;
      _personaEmotion = p.getString('persona_emotion') ?? 'Normal';
      _personaGender  = p.getString('persona_gender')  ?? 'Male';
      _brandName      = p.getString('brand_name')      ?? '';
      _brandPreset    = p.getString('brand_preset')    ?? 'Narrator';
      _crossChar      = p.getString('cross_char')      ?? '';
    });
  }

  void _applyPersonaToStudio() {
    setState(() {
      _speed   = _personaSpeed.toDouble();
      _pitch   = _personaPitch.toDouble();
      _emotion = _personaEmotion;
      _gender  = _personaGender;
      if (_brandPreset.isNotEmpty) _preset = _brandPreset;
    });
  }

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
                    _buildTextInput(),
                    const SizedBox(height: 12),
                    _buildCharacters(),
                    const SizedBox(height: 12),
                    _buildLangGender(),
                    const SizedBox(height: 12),
                    _buildEmotions(),
                    const SizedBox(height: 12),
                    _buildPresets(),
                    const SizedBox(height: 12),
                    _buildSpeedPitch(),
                    const SizedBox(height: 12),
                    _buildAdvanced(),
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
        const SizedBox(height: 2),
        if (_character.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: cGreen3,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: cBorder),
            ),
            child: Text('$_character · $_language',
              style: const TextStyle(fontSize: 10, color: cGreen, fontWeight: FontWeight.w700)),
          )
        else
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
          children: [
            ...kCharacters.entries.take(_showAllChars ? 20 : 8).map((e) {
              final selected = _character == e.key;
              final cfg = e.value;
              final disabled = _disabledChars.contains(e.key);
              return GestureDetector(
                onTap: () => disabled ? null : _applyCharacter(e.key),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.only(right: 10),
                  width: 76,
                  decoration: BoxDecoration(
                    color: disabled ? cBg2 : (selected ? cGreen : cSurface),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: disabled ? cBorder.withOpacity(0.3) : (selected ? cGreen : cBorder), width: 1.5),
                    boxShadow: selected && !disabled ? [BoxShadow(color: cGreen.withOpacity(0.3), blurRadius: 8)] : [],
                  ),
                  child: Stack(children: [
                    SizedBox(
                      width: double.infinity,
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          SvgPicture.asset(cfg.icon, width: selected ? 30 : 26, height: selected ? 30 : 26,
                            colorFilter: ColorFilter.mode(disabled ? cMuted : const Color(0xFF00FFFF), BlendMode.srcIn)),
                          const SizedBox(height: 3),
                          Text(e.key, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                            color: disabled ? cMuted : (selected ? Colors.white : cText)),
                            textAlign: TextAlign.center),
                          if (cfg.specialtyLabel.isNotEmpty)
                            Text(cfg.specialtyLabel, style: TextStyle(fontSize: 9,
                              color: disabled ? cMuted : (selected ? cGreenL : cMuted), height: 1.2),
                              textAlign: TextAlign.center,
                              maxLines: 1, overflow: TextOverflow.ellipsis),
                        ],
                      ),
                    ),
                    if (disabled)
                      Positioned.fill(child: Container(
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.45),
                          borderRadius: BorderRadius.circular(13),
                        ),
                        child: const Center(child: Icon(Icons.lock_rounded, color: Colors.white54, size: 18)),
                      )),
                  ]),
                ),
              );
            }),
            // Show More / Less button
            GestureDetector(
              onTap: () => setState(() => _showAllChars = !_showAllChars),
              child: Container(
                width: 60,
                margin: const EdgeInsets.only(right: 4),
                decoration: BoxDecoration(
                  color: cSurface,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: cBorder),
                ),
                child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Icon(_showAllChars ? Icons.chevron_left_rounded : Icons.more_horiz_rounded,
                    color: cGreen, size: 22),
                  const SizedBox(height: 2),
                  Text(_showAllChars ? 'Less' : '+${20 - 8} more',
                    style: const TextStyle(fontSize: 9, color: cGreen, fontWeight: FontWeight.w700)),
                ]),
              ),
            ),
          ],
        ),
      ),
      // ── Specialty hint + Cross-lingual quick lock ──
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
            const SizedBox(width: 6),
            // Quick cross-lingual lock toggle
            GestureDetector(
              onTap: () => setState(() {
                _crossLingual = !_crossLingual;
                _crossChar = _crossLingual ? _character : '';
              }),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: _crossLingual ? cBlue.withOpacity(0.2) : cSurface,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: _crossLingual ? cBlue : cBorder),
                ),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  Icon(_crossLingual ? Icons.lock_rounded : Icons.lock_open_rounded,
                    size: 11, color: _crossLingual ? cBlue : cMuted),
                  const SizedBox(width: 3),
                  Text(_crossLingual ? 'Locked' : 'Lock',
                    style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700,
                      color: _crossLingual ? cBlue : cMuted)),
                ]),
              ),
            ),
          ]),
        ),
        if (_crossLingual) ...[
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: cBlue.withOpacity(0.08),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: cBlue.withOpacity(0.3)),
            ),
            child: Row(children: [
              const Icon(Icons.language_rounded, size: 11, color: cBlue),
              const SizedBox(width: 4),
              Text('$_crossChar voice across all 39 languages',
                style: const TextStyle(fontSize: 10, color: cBlue)),
            ]),
          ),
        ],
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
  Widget _buildLangGender() => IntrinsicHeight(child: Row(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
    Expanded(
      child: MintCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const SectionHeader('Language'),
          const SizedBox(height: 8),
          // Search box
          TextField(
            onChanged: (v) => setState(() => _langSearch = v.toLowerCase()),
            style: const TextStyle(fontSize: 12, color: cText),
            decoration: InputDecoration(
              hintText: 'Search language...',
              hintStyle: const TextStyle(fontSize: 12, color: cMuted),
              prefixIcon: const Icon(Icons.search_rounded, size: 16, color: cMuted),
              suffixIcon: _langSearch.isNotEmpty
                  ? GestureDetector(
                      onTap: () => setState(() => _langSearch = ''),
                      child: const Icon(Icons.close_rounded, size: 16, color: cMuted),
                    )
                  : null,
              contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              isDense: true,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: cBorder)),
              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: cBorder)),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: cGreen)),
              filled: true, fillColor: cSurface,
            ),
          ),
          const SizedBox(height: 6),
          SizedBox(
            height: 190,
            child: Builder(builder: (ctx) {
              final filtered = kLanguages.keys.where((lang) =>
                _langSearch.isEmpty ||
                lang.toLowerCase().contains(_langSearch) ||
                (kLanguages[lang]?.label.toLowerCase().contains(_langSearch) ?? false)
              ).toList();
              if (filtered.isEmpty) {
                return const Center(child: Text('No language found',
                    style: TextStyle(fontSize: 12, color: cMuted)));
              }
              return ListView(
                children: filtered.map((lang) {
                  final cfg = kLanguages[lang]!;
                  final sel = _language == lang;
                  return GestureDetector(
                    onTap: () {
                      final compatible = getCharactersForLang(lang);
                      setState(() {
                        _language = lang;
                        _textCtrl.clear();
                        _audioReady = false;
                        _langSearch = '';
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
                        SvgPicture.asset(cfg.flag, width: 20, height: 20),
                        const SizedBox(width: 8),
                        Text(lang, style: TextStyle(fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: sel ? Colors.white : cText)),
                        const Spacer(),
                        Text(cfg.label, style: TextStyle(fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: sel ? Colors.white70 : cMuted)),
                        if (sel) ...[
                          const SizedBox(width: 4),
                          const Icon(Icons.check_rounded, size: 14, color: Colors.white),
                        ],
                      ]),
                    ),
                  );
                }).toList(),
              );
            }),
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
          Expanded(
            child: Column(
              children: ['Male', 'Female'].map((g) {
                final sel = _gender == g;
                return Expanded(
                  child: GestureDetector(
                    onTap: () => setState(() => _gender = g),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      margin: const EdgeInsets.only(bottom: 6),
                      decoration: BoxDecoration(
                        color: sel ? cGreen : cSurface,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: sel ? cGreen : cBorder),
                      ),
                      child: Center(child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SvgPicture.asset(
                            g == 'Male'
                                ? 'assets/svg/gender_male.svg'
                                : 'assets/svg/gender_female.svg',
                            width: 20, height: 20,
                            colorFilter: const ColorFilter.mode(
                                Color(0xFF00FFFF), BlendMode.srcIn)),
                          const SizedBox(height: 3),
                          Text(g, style: TextStyle(fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: sel ? Colors.white : cText)),
                          const SizedBox(height: 2),
                          Icon(Icons.lock_rounded, size: 10,
                              color: sel
                                  ? Colors.white54
                                  : cMuted.withOpacity(0.4)),
                        ],
                      )),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ]),
      ),
    ),
  ]));

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
      _sectionLabel('Core Audio', Icons.tune_rounded),
      const SizedBox(height: 6),
      // Breath & Adaptive Pacing are disabled when Ultra-Low Latency is ON
      _advToggle('Dynamic Breath Simulation', '(Natural breathing pauses in audio)',
        Icons.air_rounded, _useBreaths,
        _lowLatency ? null : (v) => setState(() {
          _useBreaths = v;
          if (v) _adaptivePacing = false; // Breath + AdaptivePacing conflict
        }),
        lockedMsg: _lowLatency ? 'Disabled in Ultra-Low Latency mode' : null),
      _advToggle('Adaptive Pacing', '(Auto slows for long text 300+ chars)',
        Icons.speed_rounded, _adaptivePacing,
        (_lowLatency || _useBreaths) ? null : (v) => setState(() => _adaptivePacing = v),
        lockedMsg: _lowLatency ? 'Disabled in Ultra-Low Latency mode'
                 : _useBreaths ? 'Conflicts with Breath Simulation' : null),
      _advToggle('Ultra-Low Latency Mode', '(Faster response, shorter texts)',
        Icons.bolt_rounded, _lowLatency,
        (v) => setState(() {
          _lowLatency = v;
          if (v) { _useBreaths = false; _adaptivePacing = false; } // Latency disables both
        })),

      const Divider(color: Color(0xFF1E2D45), height: 20),

      // ── SECTION 2: SSML ───────────────────────────────
      _sectionLabel('SSML Markup', Icons.code_rounded),
      const SizedBox(height: 6),
      // SSML disabled in Ultra-Low Latency (parsing overhead)
      _advToggle('SSML Markup Support',
        '(Use <break>, <emphasis>, <prosody> tags)',
        Icons.code_rounded, _ssmlMode,
        _lowLatency ? null : (v) => setState(() => _ssmlMode = v),
        lockedMsg: _lowLatency ? 'Disabled in Ultra-Low Latency mode' : null),
      // Word-Boundary needs extra processing — disabled with Ultra-Low Latency
      _advToggle('Word-Boundary Sync',
        '(Exact word timing — karaoke, avatars, captions)',
        Icons.closed_caption_rounded, _wordBoundary,
        _lowLatency ? null : (v) => setState(() => _wordBoundary = v),
        lockedMsg: _lowLatency ? 'Disabled in Ultra-Low Latency mode' : null),

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
      _sectionLabel('HD Neural AI', Icons.auto_awesome_rounded),
      const SizedBox(height: 6),
      // HD Voice = higher quality but slower — conflicts with Ultra-Low Latency
      _advToggle('HD Neural Voice', '(Higher quality audio — Azure HD voices)',
        Icons.hd_rounded, _hdVoice,
        _lowLatency ? null : (v) => setState(() => _hdVoice = v),
        lockedMsg: _lowLatency ? 'Disabled in Ultra-Low Latency mode' : null),
      // Auto Emotion — disables manual emotion picker when ON
      _advToggle('Auto Emotion Detection',
        '(AI detects text sentiment & auto-sets emotion)',
        Icons.psychology_rounded, _autoEmotion,
        (v) => setState(() { _autoEmotion = v; if (v) _emotion = 'Normal'; })),
      if (_autoEmotion) ...[ 
        Padding(
          padding: const EdgeInsets.only(left: 12, bottom: 4),
          child: Row(children: [
            Icon(Icons.info_outline_rounded, size: 13, color: cAmber),
            const SizedBox(width: 6),
            const Text('Manual emotion selector is auto-controlled',
              style: TextStyle(fontSize: 11, color: cAmber)),
          ]),
        ),
      ],
      _advToggle('Avatar Mode (Beta)',
        '(Photorealistic speaking avatar — coming soon)',
        Icons.face_rounded, _avatarMode,
        (v) => setState(() => _avatarMode = v), comingSoon: true),

      const Divider(color: Color(0xFF1E2D45), height: 20),

      // ── SECTION 4: Voice Persona & Brand ─────────────
      _sectionLabel('Voice Persona & Brand', Icons.record_voice_over_rounded),
      const SizedBox(height: 6),

      // ── CNV Toggle ──────────────────────────────────────
      _advToggle(
        'Custom Neural Voice (CNV)',
        '(Save your own voice profile — speed, pitch, emotion)',
        Icons.mic_rounded, _cnvMode,
        (v) => setState(() { _cnvMode = v; if (v) _loadPersona(); }),
      ),

      // ── CNV Panel — shown when ON ──────────────────────
      if (_cnvMode) ...[
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFF0B0F19),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: cGreen.withOpacity(0.3)),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Your Voice Persona', style: TextStyle(
              fontSize: 12, fontWeight: FontWeight.w700, color: cGreen)),
            const SizedBox(height: 8),
            // Persona name
            TextField(
              onChanged: (v) => _personaName = v,
              style: const TextStyle(fontSize: 12, color: cText),
              decoration: InputDecoration(
                hintText: 'Persona name (e.g. "Zain Voice")',
                hintStyle: const TextStyle(fontSize: 12, color: cMuted),
                contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cBorder)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cBorder)),
                focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cGreen)),
                filled: true, fillColor: cCard,
              ),
            ),
            const SizedBox(height: 8),
            // Speed
            Row(children: [
              const Text('Speed', style: TextStyle(fontSize: 11, color: cMuted)),
              Expanded(child: SliderTheme(
                data: SliderTheme.of(context).copyWith(
                  activeTrackColor: cGreen, thumbColor: cGreen,
                  inactiveTrackColor: cBorder, trackHeight: 3),
                child: Slider(
                  min: 10, max: 100, divisions: 18,
                  value: _personaSpeed.toDouble(),
                  onChanged: (v) => setState(() => _personaSpeed = v.round()),
                ),
              )),
              Text('${_personaSpeed}%', style: const TextStyle(fontSize: 11, color: cGreen)),
            ]),
            // Pitch
            Row(children: [
              const Text('Pitch ', style: TextStyle(fontSize: 11, color: cMuted)),
              Expanded(child: SliderTheme(
                data: SliderTheme.of(context).copyWith(
                  activeTrackColor: cGreen, thumbColor: cGreen,
                  inactiveTrackColor: cBorder, trackHeight: 3),
                child: Slider(
                  min: -10, max: 10, divisions: 20,
                  value: _personaPitch.toDouble(),
                  onChanged: (v) => setState(() => _personaPitch = v.round()),
                ),
              )),
              Text('${_personaPitch >= 0 ? '+' : ''}$_personaPitch',
                style: const TextStyle(fontSize: 11, color: cGreen)),
            ]),
            // Emotion dropdown
            DropdownButtonFormField<String>(
              value: _personaEmotion,
              dropdownColor: cCard,
              style: const TextStyle(fontSize: 12, color: cText),
              decoration: InputDecoration(
                labelText: 'Default Emotion',
                labelStyle: const TextStyle(fontSize: 11, color: cMuted),
                contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cBorder)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cBorder)),
                filled: true, fillColor: cCard,
              ),
              items: kEmotions.keys.map((e) => DropdownMenuItem(
                value: e, child: Text(e))).toList(),
              onChanged: (v) => setState(() => _personaEmotion = v!),
            ),
            const SizedBox(height: 10),
            // Buttons
            Row(children: [
              Expanded(child: GestureDetector(
                onTap: () async {
                  await _savePersona();
                  if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Persona "${_personaName}" saved!'),
                      backgroundColor: cGreen3, duration: const Duration(seconds: 2)));
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(color: cGreen,
                    borderRadius: BorderRadius.circular(8)),
                  child: const Center(child: Text('Save Persona',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700,
                      color: Colors.white))),
                ),
              )),
              const SizedBox(width: 8),
              Expanded(child: GestureDetector(
                onTap: _applyPersonaToStudio,
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(color: cCard2, border: Border.all(color: cGreen),
                    borderRadius: BorderRadius.circular(8)),
                  child: const Center(child: Text('Apply to Studio',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: cGreen))),
                ),
              )),
            ]),
          ]),
        ),
        const SizedBox(height: 10),
      ],

      // ── Cross-Lingual Toggle ─────────────────────────────
      _advToggle(
        'Cross-Lingual Persona',
        '(Lock current character voice across all 39 languages)',
        Icons.translate_rounded, _crossLingual,
        (v) => setState(() {
          _crossLingual = v;
          if (v) _crossChar = _character;
        }),
      ),

      if (_crossLingual && _crossChar.isNotEmpty) ...[
        const SizedBox(height: 6),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: const Color(0xFF0B0F19),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: cBlue.withOpacity(0.4)),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              const Icon(Icons.lock_rounded, size: 13, color: cBlue),
              const SizedBox(width: 6),
              Text('Voice locked: $_crossChar',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: cBlue)),
            ]),
            const SizedBox(height: 4),
            const Text(
              'Switch any language — the same character voice will be used automatically.',
              style: TextStyle(fontSize: 10, color: cMuted, height: 1.4)),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () => setState(() { _crossLingual = false; _crossChar = ''; }),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 6),
                decoration: BoxDecoration(color: cCard2,
                  border: Border.all(color: cBlue.withOpacity(0.4)),
                  borderRadius: BorderRadius.circular(6)),
                child: const Center(child: Text('Unlock Voice',
                  style: TextStyle(fontSize: 11, color: cBlue, fontWeight: FontWeight.w600))),
              ),
            ),
          ]),
        ),
        const SizedBox(height: 8),
      ],

      // ── Brand Voice Toggle ───────────────────────────────
      _advToggle(
        'Brand Voice Persona',
        '(Save brand name + preset profile for consistent output)',
        Icons.campaign_rounded, _brandVoice,
        (v) => setState(() { _brandVoice = v; }),
      ),

      if (_brandVoice) ...[
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFF0B0F19),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: cOrange.withOpacity(0.3)),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Brand Profile', style: TextStyle(
              fontSize: 12, fontWeight: FontWeight.w700, color: cOrange)),
            const SizedBox(height: 8),
            TextField(
              onChanged: (v) => _brandName = v,
              style: const TextStyle(fontSize: 12, color: cText),
              decoration: InputDecoration(
                hintText: 'Brand name (e.g. "TechCorp AI")',
                hintStyle: const TextStyle(fontSize: 12, color: cMuted),
                contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cBorder)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cBorder)),
                focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: cOrange)),
                filled: true, fillColor: cCard,
              ),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _brandPreset,
              dropdownColor: cCard,
              style: const TextStyle(fontSize: 12, color: cText),
              decoration: InputDecoration(
                labelText: 'Brand Default Preset',
                labelStyle: const TextStyle(fontSize: 11, color: cMuted),
                contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cBorder)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: cBorder)),
                filled: true, fillColor: cCard,
              ),
              items: kPresets.keys.map((p) => DropdownMenuItem(
                value: p, child: Text(p))).toList(),
              onChanged: (v) => setState(() { _brandPreset = v!; _preset = v; }),
            ),
            const SizedBox(height: 10),
            Row(children: [
              Expanded(child: GestureDetector(
                onTap: () async {
                  await _savePersona();
                  setState(() => _preset = _brandPreset);
                  if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Brand "${_brandName}" saved & applied!'),
                      backgroundColor: cGreen3, duration: const Duration(seconds: 2)));
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(color: cOrange,
                    borderRadius: BorderRadius.circular(8)),
                  child: const Center(child: Text('Save & Apply Brand',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700,
                      color: Colors.white))),
                ),
              )),
            ]),
            if (_brandName.isNotEmpty) ...[
              const SizedBox(height: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: cOrange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(6)),
                child: Row(children: [
                  Icon(Icons.check_circle_rounded, size: 12, color: cOrange),
                  const SizedBox(width: 4),
                  Text('Active brand: $_brandName  |  Preset: $_brandPreset',
                    style: TextStyle(fontSize: 10, color: cOrange)),
                ]),
              ),
            ],
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
    ValueChanged<bool>? onChanged, {
    bool comingSoon = false,
    String? lockedMsg,
  }) {
    final isLocked = lockedMsg != null || comingSoon;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(icon, size: 16,
          color: isLocked
            ? const Color(0xFF3A4A5E)
            : value ? const Color(0xFF00F2FE) : const Color(0xFF5A6A7E)),
        const SizedBox(width: 10),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Flexible(child: Text(label, style: TextStyle(
              fontSize: 13, fontWeight: FontWeight.w600,
              color: isLocked
                ? const Color(0xFF3A4A5E)
                : value ? const Color(0xFFFFFFFF) : const Color(0xFF8A99AD),
            ))),
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
            if (lockedMsg != null) ...[
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFF5A6A7E).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Text('OFF',
                  style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800,
                    color: Color(0xFF5A6A7E))),
              ),
            ],
          ]),
          Text(subtitle, style: const TextStyle(
            fontSize: 10, color: Color(0xFF5A6A7E), height: 1.3)),
          if (lockedMsg != null) ...[
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
              decoration: BoxDecoration(
                color: cAmber.withOpacity(0.08),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: cAmber.withOpacity(0.3)),
              ),
              child: Row(mainAxisSize: MainAxisSize.min, children: [
                const Icon(Icons.warning_amber_rounded,
                    size: 11, color: cAmber),
                const SizedBox(width: 4),
                Flexible(child: Text(lockedMsg,
                  style: const TextStyle(
                    fontSize: 9,
                    color: cAmber,
                    height: 1.3,
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.w600,
                  ))),
              ]),
            ),
          ],
        ])),
        const SizedBox(width: 8),
        Transform.scale(
          scale: 0.85,
          child: Switch(
            value: isLocked ? false : value,
            onChanged: isLocked ? null : onChanged,
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
            '${_textCtrl.text.length}/$_charLimit',
            style: TextStyle(
              fontSize: 11,
              color: _textCtrl.text.length >= _charLimit ? cRed : cMuted,
              fontWeight: _textCtrl.text.length >= _charLimit ? FontWeight.w700 : FontWeight.normal,
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
        if (_textCtrl.text.length >= _charLimit) ...[
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
            maxLength: _charLimit,
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
                borderSide: BorderSide(color: _textCtrl.text.length >= _charLimit ? cRed : cGreen, width: 2),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: _textCtrl.text.length >= _charLimit ? cRed.withOpacity(0.5) : cBorder),
              ),
              filled: true, fillColor: cCard2,
              contentPadding: const EdgeInsets.all(12),
            ),
            onChanged: (_) => setState(() {}),
          ),
        ),
        const SizedBox(height: 8),
        // ── Quick Actions inside text card ──────────
        Row(children: [
          Expanded(child: GestureDetector(
            onTap: () => setState(() {
              _textCtrl.clear();
              _audioReady = false;
            }),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 9),
              decoration: BoxDecoration(
                color: cRed.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: cRed.withOpacity(0.35))),
              child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                Icon(Icons.refresh_rounded, size: 15, color: cRed),
                SizedBox(width: 5),
                Text('Clear', style: TextStyle(fontSize: 12, color: cRed, fontWeight: FontWeight.w700)),
              ]),
            ),
          )),
          const SizedBox(width: 8),
          Expanded(child: GestureDetector(
            onTap: () async {
              final data = await Clipboard.getData('text/plain');
              if (data?.text != null && data!.text!.isNotEmpty) {
                final text = data.text!.length > _charLimit
                    ? data.text!.substring(0, _charLimit) : data.text!;
                setState(() => _textCtrl.text = text);
              }
            },
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 9),
              decoration: BoxDecoration(
                color: cGreen.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: cGreen.withOpacity(0.35))),
              child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                Icon(Icons.content_paste_rounded, size: 15, color: cGreen),
                SizedBox(width: 5),
                Text('Paste', style: TextStyle(fontSize: 12, color: cGreen, fontWeight: FontWeight.w700)),
              ]),
            ),
          )),
        ]),
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
  Widget _buildQuickActions() => Row(children: [
    // Reset All
    Expanded(child: GestureDetector(
      onTap: () => setState(() {
        _textCtrl.clear();
        _audioReady = false;
        _character = 'Adam';
        _language  = 'English';
        _emotion   = 'Normal';
        _preset    = '';
        _speed     = 55;
        _pitch     = 0;
        _gender    = 'Male';
      }),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: cRed.withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: cRed.withOpacity(0.4))),
        child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(Icons.refresh_rounded, size: 15, color: cRed),
          SizedBox(width: 4),
          Text('Reset', style: TextStyle(fontSize: 12, color: cRed, fontWeight: FontWeight.w700)),
        ]),
      ),
    )),
    const SizedBox(width: 8),
    // Paste from clipboard
    Expanded(child: GestureDetector(
      onTap: () async {
        final data = await Clipboard.getData('text/plain');
        if (data?.text != null && data!.text!.isNotEmpty) {
          final text = data.text!.length > _charLimit
              ? data.text!.substring(0, _charLimit) : data.text!;
          setState(() => _textCtrl.text = text);
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: cGreen.withOpacity(0.12),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: cGreen.withOpacity(0.5))),
        child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(Icons.content_paste_rounded, size: 15, color: cGreen),
          SizedBox(width: 4),
          Text('Paste', style: TextStyle(fontSize: 12, color: cGreen, fontWeight: FontWeight.w700)),
        ]),
      ),
    )),
  ]);

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
