import 'dart:io';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import '../utils/constants.dart';
import '../models/history_model.dart';
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

  // ── Single shared player — pre-initialized, no delay ──
  final _player = AudioPlayer();
  String? _playingId;
  bool _isPaused = false;
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;

  // Download state
  final Set<String> _savingIds = {};
  final Map<String, double> _saveProgress = {};

  @override
  void initState() {
    super.initState();
    _load();
    _initPlayer();
  }

  void _initPlayer() {
    // Pre-warm player to eliminate first-play delay
    _player.positionStream.listen((pos) {
      if (mounted) setState(() => _position = pos);
    });
    _player.durationStream.listen((dur) {
      if (mounted && dur != null) setState(() => _duration = dur);
    });
    _player.playerStateStream.listen((state) {
      if (state.processingState == ProcessingState.completed && mounted) {
        setState(() {
          _playingId = null;
          _isPaused = false;
          _position = Duration.zero;
          _duration = Duration.zero;
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

  // ── PLAY / PAUSE / RESUME ───────────────────────────────
  Future<void> _handlePlay(HistoryEntry e) async {
    if (!File(e.path).existsSync()) {
      _showSnack('File not found', isError: true);
      return;
    }

    if (_playingId == e.id) {
      // Same track — toggle pause/resume
      if (_isPaused) {
        await _player.play();
        setState(() => _isPaused = false);
      } else {
        await _player.pause();
        setState(() => _isPaused = true);
      }
      return;
    }

    // New track — stop old, load new with AudioSource (faster + reliable)
    await _player.stop();
    setState(() {
      _playingId = e.id;
      _isPaused = false;
      _position = Duration.zero;
      _duration = Duration.zero;
    });

    try {
      await _player.setAudioSource(
        AudioSource.file(e.path),
        preload: true,
      );
      await _player.play();
    } catch (err) {
      _showSnack('Cannot play this file: $err', isError: true);
      setState(() { _playingId = null; });
    }
  }

  Future<void> _stopPlayer() async {
    await _player.stop();
    setState(() {
      _playingId = null;
      _isPaused = false;
      _position = Duration.zero;
      _duration = Duration.zero;
    });
  }

  Future<void> _seekTo(double fraction) async {
    final totalMs = _duration.inMilliseconds;
    if (totalMs == 0) return;
    await _player.seek(Duration(milliseconds: (fraction * totalMs).round()));
  }

  // ── DOWNLOAD ────────────────────────────────────────────
  Future<void> _download(HistoryEntry e) async {
    if (_savingIds.contains(e.id)) return;
    if (!File(e.path).existsSync()) {
      _showSnack('File not found', isError: true);
      return;
    }

    setState(() {
      _savingIds.add(e.id);
      _saveProgress[e.id] = 0.0;
    });

    try {
      for (double p = 0.1; p <= 0.8; p += 0.2) {
        await Future.delayed(const Duration(milliseconds: 100));
        if (!mounted) return;
        setState(() => _saveProgress[e.id] = p);
      }

      final saved = await TtsService.savePermanent(File(e.path), e.filename);

      if (!mounted) return;
      setState(() { _saveProgress[e.id] = 1.0; });
      await Future.delayed(const Duration(milliseconds: 300));
      if (!mounted) return;
      setState(() {
        _savingIds.remove(e.id);
        _saveProgress.remove(e.id);
      });
      _showSnack('✅ Saved: ${saved.path.split('/').last}');
    } catch (err) {
      if (!mounted) return;
      setState(() {
        _savingIds.remove(e.id);
        _saveProgress.remove(e.id);
      });
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

  Color _langColor(String lang) {
    switch (lang) {
      case 'Urdu':  return cPurple;
      case 'Hindi': return cOrange;
      default:      return cBlue;
    }
  }

  String _fmt(Duration d) {
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: cBg,
    appBar: AppBar(
      backgroundColor: cBg2,
      elevation: 0,
      foregroundColor: cText,
      title: const Text('Download History',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: cText)),
      actions: [
        if (_history.isNotEmpty)
          TextButton(
            onPressed: () async {
              await _stopPlayer();
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
            ? _buildEmpty()
            : ListView.builder(
                padding: const EdgeInsets.all(14),
                itemCount: _history.length,
                itemBuilder: (_, i) => _buildCard(_history[i]),
              ),
  );

  Widget _buildEmpty() => Center(
    child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
      const Text('📥', style: TextStyle(fontSize: 52)),
      const SizedBox(height: 16),
      const Text('No downloads yet',
          style: TextStyle(
              fontSize: 17, fontWeight: FontWeight.w700, color: cText2)),
      const SizedBox(height: 6),
      const Text('Generate and save your first voice!',
          style: TextStyle(fontSize: 13, color: cMuted)),
    ]),
  );

  Widget _buildCard(HistoryEntry e) {
    final exists       = File(e.path).existsSync();
    final isThisActive = _playingId == e.id;
    final isPlaying    = isThisActive && !_isPaused;
    final isPaused     = isThisActive && _isPaused;
    final isSaving     = _savingIds.contains(e.id);
    final progress     = _saveProgress[e.id] ?? 0.0;
    final lc           = _langColor(e.language);

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: MintCard(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            // ── Row 1: Flag | Info | Download btn ────────────
            GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => PlayerScreen(
                      entry: e,
                      playlist: _history
                          .where((h) => File(h.path).existsSync())
                          .toList(),
                      initialIndex: _history
                          .where((h) => File(h.path).existsSync())
                          .toList()
                          .indexWhere((h) => h.id == e.id),
                    ),
                  ),
                );
              },
              child: Row(children: [
              // Flag icon
              Container(
                width: 44, height: 44,
                decoration: BoxDecoration(
                  color: lc.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    kLanguages[e.language]?.flag ?? '🎙️',
                    style: const TextStyle(fontSize: 22),
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // Info
              Expanded(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(e.filename,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: cText)),
                  const SizedBox(height: 4),
                  Wrap(spacing: 6, children: [
                    _tag(e.language, lc),
                    _tag(e.gender, cGreen),
                    _tag(e.emotion,
                        kEmotions[e.emotion]?.color ?? cMuted),
                  ]),
                  const SizedBox(height: 3),
                  Text(e.timestamp,
                      style: const TextStyle(fontSize: 11, color: cMuted)),
                ],
              )),
              const SizedBox(width: 8),

              // Download button
              if (exists)
                GestureDetector(
                  onTap: isSaving ? null : () => _download(e),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 40, height: 40,
                    decoration: BoxDecoration(
                      color: isSaving
                          ? cBorder
                          : cTeal.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: isSaving
                            ? cBorder
                            : cTeal.withOpacity(0.4),
                      ),
                    ),
                    child: isSaving
                        ? Padding(
                            padding: const EdgeInsets.all(10),
                            child: CircularProgressIndicator(
                              value: progress < 1.0 ? progress : null,
                              color: cGreen,
                              strokeWidth: 2.5,
                            ),
                          )
                        : const Icon(Icons.save_alt_rounded,
                            color: cTeal, size: 20),
                  ),
                )
              else
                const Text('[Missing]',
                    style: TextStyle(fontSize: 10, color: cRed)),
            ]),  // end Row
            ), // end GestureDetector

            // ── Download progress bar ──────────────────────
            if (isSaving) ...[
              const SizedBox(height: 10),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Saving to Downloads...',
                      style: TextStyle(fontSize: 11, color: cGreen)),
                  Text('${(progress * 100).round()}%',
                      style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: cGreen)),
                ],
              ),
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

            // ── Built-in Player with Visual Waveform ───────
            if (exists) ...[
              const SizedBox(height: 12),
              _buildPlayer(e, isPlaying: isPlaying, isPaused: isPaused),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPlayer(
    HistoryEntry e, {
    required bool isPlaying,
    required bool isPaused,
  }) {
    final isActive = isPlaying || isPaused;
    final totalMs  = _duration.inMilliseconds;
    final posMs    = _position.inMilliseconds;
    final frac     = totalMs > 0
        ? (posMs / totalMs).clamp(0.0, 1.0)
        : 0.0;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 250),
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
      decoration: BoxDecoration(
        color: isActive
            ? cGreen.withOpacity(0.08)
            : cBg.withOpacity(0.4),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isActive
              ? cGreen.withOpacity(0.35)
              : cBorder,
        ),
      ),
      child: Column(children: [

        // ── Waveform visualization ────────────────────────
        SizedBox(
          height: 40,
          child: MiniWaveform(
            isPlaying: isPlaying,
            isPaused: isPaused,
            color: isPlaying ? cGreen : (isPaused ? cAmber : cMuted),
          ),
        ),
        const SizedBox(height: 10),

        // ── Seek bar ──────────────────────────────────────
        GestureDetector(
          onTapDown: isActive
              ? (d) {
                  final w = MediaQuery.of(context).size.width - 28 - 24 - 28;
                  _seekTo((d.localPosition.dx / w).clamp(0.0, 1.0));
                }
              : null,
          child: Stack(children: [
            Container(
              height: 4,
              decoration: BoxDecoration(
                color: cBorder,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            FractionallySizedBox(
              widthFactor: frac,
              child: Container(
                height: 4,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: isPlaying
                        ? [cGreen, cGreen2]
                        : [cAmber, cAmber],
                  ),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
          ]),
        ),
        const SizedBox(height: 6),

        // ── Controls row ──────────────────────────────────
        Row(children: [
          // Time
          Text(
            isActive ? _fmt(_position) : '00:00',
            style: TextStyle(
                fontSize: 11,
                color: isActive ? cGreen : cMuted,
                fontWeight: FontWeight.w600),
          ),
          const Spacer(),

          // Stop button (only when active)
          if (isActive) ...[
            GestureDetector(
              onTap: _stopPlayer,
              child: Container(
                width: 30, height: 30,
                decoration: BoxDecoration(
                  color: cRed.withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: cRed.withOpacity(0.3)),
                ),
                child: const Icon(Icons.stop_rounded, color: cRed, size: 15),
              ),
            ),
            const SizedBox(width: 10),
          ],

          // Play / Pause button
          GestureDetector(
            onTap: () => _handlePlay(e),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 42, height: 42,
              decoration: BoxDecoration(
                color: isPlaying
                    ? cAmber
                    : isPaused
                        ? cGreen.withOpacity(0.7)
                        : cGreen,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: (isPlaying ? cAmber : cGreen).withOpacity(0.35),
                    blurRadius: 10,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: Icon(
                isPlaying
                    ? Icons.pause_rounded
                    : Icons.play_arrow_rounded,
                color: Colors.white,
                size: 24,
              ),
            ),
          ),

          const Spacer(),

          // Duration
          Text(
            isActive && totalMs > 0 ? _fmt(_duration) : '--:--',
            style: const TextStyle(fontSize: 11, color: cMuted),
          ),
        ]),
      ]),
    );
  }

  Widget _tag(String label, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
    decoration: BoxDecoration(
      color: color.withOpacity(0.1),
      borderRadius: BorderRadius.circular(6),
    ),
    child: Text(label,
        style: TextStyle(
            fontSize: 10, fontWeight: FontWeight.w700, color: color)),
  );
}
