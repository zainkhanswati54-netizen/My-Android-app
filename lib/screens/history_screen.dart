import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:just_audio/just_audio.dart';
import '../utils/constants.dart';
import '../models/history_model.dart';
import '../services/history_service.dart';
import '../widgets/mint_card.dart';
import '../widgets/waveform_widget.dart';
import '../services/tts_service.dart';
import 'player_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});
  @override
  State<HistoryScreen> createState() => _HistoryState();
}

class _HistoryState extends State<HistoryScreen> {
  List<HistoryEntry> _history = [];
  bool _loading = true;

  // ── ONE shared player — only one plays at a time ──────
  final _player = AudioPlayer();
  String? _playingId;
  bool   _isPaused  = false;
  bool   _isMuted   = false;
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;

  // Download state
  final Set<String>        _savingIds    = {};
  final Map<String, double> _saveProgress = {};

  @override
  void initState() {
    super.initState();
    _load();
    _player.positionStream.listen((p) {
      if (mounted) setState(() => _position = p);
    });
    _player.durationStream.listen((d) {
      if (mounted && d != null) setState(() => _duration = d);
    });
    _player.playerStateStream.listen((s) {
      if (!mounted) return;
      if (s.processingState == ProcessingState.completed) {
        setState(() {
          _playingId = null;
          _isPaused  = false;
          _position  = Duration.zero;
          _duration  = Duration.zero;
        });
      }
    });
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final h = await HistoryService.load();
    if (mounted) setState(() { _history = h; _loading = false; });
  }

  // ── PLAY / PAUSE ──────────────────────────────────────
  Future<void> _handlePlay(HistoryEntry e) async {
    if (!File(e.path).existsSync()) {
      _showSnack('File not found', isError: true); return;
    }
    if (_playingId == e.id) {
      if (_isPaused) {
        await _player.play();
        setState(() => _isPaused = false);
      } else {
        await _player.pause();
        setState(() => _isPaused = true);
      }
      return;
    }
    // Stop any current, load new
    await _player.stop();
    setState(() {
      _playingId = e.id;
      _isPaused  = false;
      _position  = Duration.zero;
      _duration  = Duration.zero;
    });
    try {
      await _player.setAudioSource(AudioSource.file(e.path), preload: true);
      if (_isMuted) await _player.setVolume(0);
      await _player.play();
    } catch (err) {
      _showSnack('Cannot play: $err', isError: true);
      setState(() => _playingId = null);
    }
  }

  Future<void> _stop() async {
    await _player.stop();
    setState(() {
      _playingId = null;
      _isPaused  = false;
      _position  = Duration.zero;
      _duration  = Duration.zero;
    });
  }

  // ── SEEK ─────────────────────────────────────────────
  Future<void> _seek(double frac) async {
    final ms = _duration.inMilliseconds;
    if (ms == 0) return;
    await _player.seek(Duration(milliseconds: (frac * ms).round()));
  }

  // ── FORWARD / REWIND 10s ─────────────────────────────
  Future<void> _skip(int seconds) async {
    final cur = _position.inMilliseconds;
    final tot = _duration.inMilliseconds;
    final next = (cur + seconds * 1000).clamp(0, tot);
    await _player.seek(Duration(milliseconds: next));
  }

  // ── MUTE ─────────────────────────────────────────────
  Future<void> _toggleMute() async {
    _isMuted = !_isMuted;
    await _player.setVolume(_isMuted ? 0 : 1);
    setState(() {});
  }

  // ── DOWNLOAD ─────────────────────────────────────────
  Future<void> _download(HistoryEntry e) async {
    if (_savingIds.contains(e.id)) return;
    if (!File(e.path).existsSync()) {
      _showSnack('File not found', isError: true); return;
    }
    setState(() { _savingIds.add(e.id); _saveProgress[e.id] = 0.0; });
    try {
      for (double p = 0.2; p <= 0.8; p += 0.2) {
        await Future.delayed(const Duration(milliseconds: 120));
        if (!mounted) return;
        setState(() => _saveProgress[e.id] = p);
      }
      final saved = await TtsService.savePermanent(File(e.path), e.filename);
      if (!mounted) return;
      setState(() { _saveProgress[e.id] = 1.0; });
      await Future.delayed(const Duration(milliseconds: 400));
      if (!mounted) return;
      setState(() { _savingIds.remove(e.id); _saveProgress.remove(e.id); });
      _showSnack('✅ Saved to Downloads: ${saved.path.split('/').last}');
    } catch (err) {
      if (!mounted) return;
      setState(() { _savingIds.remove(e.id); _saveProgress.remove(e.id); });
      _showSnack('Save failed: $err', isError: true);
    }
  }

  void _showSnack(String msg, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg, style: const TextStyle(color: Colors.white, fontSize: 13)),
      backgroundColor: isError ? cRed : cGreen,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.all(12),
      duration: const Duration(seconds: 3),
    ));
  }

  String _fmt(Duration d) {
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  Color _langColor(String lang) {
    switch (lang) {
      case 'Urdu':  return cPurple;
      case 'Hindi': return cOrange;
      default:      return cBlue;
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: cBg,
    appBar: AppBar(
      backgroundColor: cBg2, elevation: 0, foregroundColor: cText,
      title: const Text('Download History',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: cText)),
      actions: [
        if (_history.isNotEmpty)
          TextButton(
            onPressed: () async {
              await _stop();
              await HistoryService.clear();
              _load();
            },
            child: const Text('Clear All',
                style: TextStyle(color: cRed, fontWeight: FontWeight.w700)),
          ),
      ],
      bottom: PreferredSize(
        preferredSize: const Size.fromHeight(1),
        child: Container(color: cBorder, height: 1),
      ),
    ),
    body: _loading
        ? const Center(child: CircularProgressIndicator(color: cGreen))
        : _history.isEmpty
            ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                SvgPicture.asset('assets/svg/icon_history_empty.svg', width: 56, height: 56, colorFilter: const ColorFilter.mode(Color(0xFF00FFFF), BlendMode.srcIn)),
                const SizedBox(height: 16),
                const Text('No downloads yet',
                    style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cText2)),
                const SizedBox(height: 6),
                const Text('Generate and save your first voice!',
                    style: TextStyle(fontSize: 13, color: cMuted)),
              ]))
            : ListView.builder(
                padding: const EdgeInsets.all(14),
                itemCount: _history.length,
                itemBuilder: (_, i) => _buildCard(_history[i]),
              ),
  );

  Widget _buildCard(HistoryEntry e) {
    final exists    = File(e.path).existsSync();
    final isActive  = _playingId == e.id;
    final isPlaying = isActive && !_isPaused;
    final isPaused  = isActive && _isPaused;
    final isSaving  = _savingIds.contains(e.id);
    final progress  = _saveProgress[e.id] ?? 0.0;
    final lc        = _langColor(e.language);
    final totalMs   = isActive ? _duration.inMilliseconds : 0;
    final posMs     = isActive ? _position.inMilliseconds : 0;
    final frac      = totalMs > 0 ? (posMs / totalMs).clamp(0.0, 1.0) : 0.0;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: MintCard(
        padding: const EdgeInsets.all(14),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [

          // ── Top row: tap to open full player ────────────
          GestureDetector(
            onTap: exists ? () => Navigator.push(context, MaterialPageRoute(
              builder: (_) => PlayerScreen(
                entry: e,
                playlist: _history.where((h) => File(h.path).existsSync()).toList(),
                initialIndex: _history.where((h) => File(h.path).existsSync()).toList().indexWhere((h) => h.id == e.id),
              ),
            )) : null,
            child: Row(children: [
              // Flag
              Container(
                width: 44, height: 44,
                decoration: BoxDecoration(color: lc.withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
                child: Center(child: SvgPicture.asset(kLanguages[e.language]?.flag ?? 'assets/svg/icon_mic.svg', width: 24, height: 24)),
              ),
              const SizedBox(width: 12),
              // Info
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(e.filename, maxLines: 1, overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: cText)),
                const SizedBox(height: 4),
                Wrap(spacing: 6, children: [
                  _tag(e.language, lc),
                  _tag(e.gender, cGreen),
                  _tag(e.emotion, kEmotions[e.emotion]?.color ?? cMuted),
                ]),
                const SizedBox(height: 3),
                Text(e.timestamp, style: const TextStyle(fontSize: 11, color: cMuted)),
              ])),
              const SizedBox(width: 8),

              // ── Download button (ONLY HERE — no duplicate) ──
              if (exists)
                GestureDetector(
                  onTap: isSaving ? null : () => _download(e),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 40, height: 40,
                    decoration: BoxDecoration(
                      color: isSaving ? cBorder : cTeal.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: isSaving ? cBorder : cTeal.withOpacity(0.4)),
                    ),
                    child: isSaving
                        ? Padding(
                            padding: const EdgeInsets.all(10),
                            child: CircularProgressIndicator(
                              value: progress < 1.0 ? progress : null,
                              color: cGreen, strokeWidth: 2.5),
                          )
                        : const Icon(Icons.save_alt_rounded, color: cTeal, size: 20),
                  ),
                )
              else
                const Text('Missing', style: TextStyle(fontSize: 10, color: cRed)),
            ]),
          ),

          // ── Save progress bar ──────────────────────────
          if (isSaving) ...[
            const SizedBox(height: 10),
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              const Text('Saving...', style: TextStyle(fontSize: 11, color: cGreen)),
              Text('${(progress * 100).round()}%',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: cGreen)),
            ]),
            const SizedBox(height: 5),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: progress < 1.0 ? progress : null,
                backgroundColor: cBorder,
                valueColor: const AlwaysStoppedAnimation<Color>(cGreen),
                minHeight: 4,
              ),
            ),
          ],

          // ── Built-in player with full controls ─────────
          if (exists) ...[
            const SizedBox(height: 12),
            AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              padding: const EdgeInsets.fromLTRB(10, 10, 10, 12),
              decoration: BoxDecoration(
                color: isActive ? cGreen.withOpacity(0.07) : cBg.withOpacity(0.4),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: isActive ? cGreen.withOpacity(0.3) : cBorder),
              ),
              child: Column(children: [

                // Waveform
                SizedBox(
                  height: 36,
                  child: MiniWaveform(
                    isPlaying: isPlaying,
                    isPaused: isPaused,
                    color: isPlaying ? cGreen : (isPaused ? cAmber : cMuted),
                  ),
                ),
                const SizedBox(height: 8),

                // Seek bar
                GestureDetector(
                  onTapDown: isActive ? (d) {
                    final w = MediaQuery.of(context).size.width - 48;
                    _seek((d.localPosition.dx / w).clamp(0.0, 1.0));
                  } : null,
                  child: Stack(children: [
                    Container(height: 3, decoration: BoxDecoration(color: cBorder, borderRadius: BorderRadius.circular(2))),
                    FractionallySizedBox(
                      widthFactor: frac,
                      child: Container(
                        height: 3,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(colors: isPlaying ? [cGreen, cGreen2] : [cAmber, cAmber]),
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    ),
                  ]),
                ),
                const SizedBox(height: 6),

                // Time row
                Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                  Text(isActive ? _fmt(_position) : '00:00',
                      style: TextStyle(fontSize: 10, color: isActive ? cGreen : cMuted, fontWeight: FontWeight.w600)),
                  Text(isActive && totalMs > 0 ? _fmt(_duration) : '--:--',
                      style: const TextStyle(fontSize: 10, color: cMuted)),
                ]),
                const SizedBox(height: 8),

                // ── Controls row ───────────────────────────
                Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [

                  // Mute
                  _ctrl(
                    icon: _isMuted ? Icons.volume_off_rounded : Icons.volume_up_rounded,
                    color: _isMuted ? cRed : cMuted,
                    onTap: _toggleMute,
                    size: 20,
                  ),

                  // Rewind 10s
                  _ctrl(
                    icon: Icons.replay_10_rounded,
                    color: isActive ? cText : cMuted,
                    onTap: isActive ? () => _skip(-10) : null,
                    size: 24,
                  ),

                  // Play / Pause — main button
                  GestureDetector(
                    onTap: () => _handlePlay(e),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      width: 46, height: 46,
                      decoration: BoxDecoration(
                        color: isPlaying ? cAmber : isPaused ? cGreen.withOpacity(0.7) : cGreen,
                        shape: BoxShape.circle,
                        boxShadow: [BoxShadow(
                          color: (isPlaying ? cAmber : cGreen).withOpacity(0.4),
                          blurRadius: 12, offset: const Offset(0, 3),
                        )],
                      ),
                      child: Icon(
                        isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                        color: Colors.white, size: 26,
                      ),
                    ),
                  ),

                  // Forward 10s
                  _ctrl(
                    icon: Icons.forward_10_rounded,
                    color: isActive ? cText : cMuted,
                    onTap: isActive ? () => _skip(10) : null,
                    size: 24,
                  ),

                  // Stop
                  _ctrl(
                    icon: Icons.stop_rounded,
                    color: isActive ? cRed : cMuted,
                    onTap: isActive ? _stop : null,
                    size: 20,
                  ),
                ]),
              ]),
            ),
          ],
        ]),
      ),
    );
  }

  Widget _ctrl({required IconData icon, required Color color, VoidCallback? onTap, double size = 22}) =>
    GestureDetector(
      onTap: onTap,
      child: Container(
        width: 36, height: 36,
        decoration: BoxDecoration(
          color: color.withOpacity(onTap != null ? 0.1 : 0.04),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: color.withOpacity(onTap != null ? 1 : 0.3), size: size),
      ),
    );

  Widget _tag(String label, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
    decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
    child: Text(label, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: color)),
  );
}
