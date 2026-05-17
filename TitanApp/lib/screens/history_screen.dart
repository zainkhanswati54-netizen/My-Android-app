import 'dart:io';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import '../utils/constants.dart';
import '../models/history_model.dart';
import '../widgets/mint_card.dart';
import '../services/tts_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});
  @override
  State<HistoryScreen> createState() => _HistoryState();
}

class _HistoryState extends State<HistoryScreen> {
  List<HistoryEntry> _history = [];
  bool _loading = true;

  // Player state
  String? _playingId;
  bool _isPaused = false;
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;
  final _player = AudioPlayer();

  // Download state
  final Set<String> _savingIds = {};
  final Map<String, double> _saveProgress = {};

  @override
  void initState() {
    super.initState();
    _load();
    _setupPlayerListeners();
  }

  void _setupPlayerListeners() {
    // Track position
    _player.positionStream.listen((pos) {
      if (mounted) setState(() => _position = pos);
    });
    // Track duration
    _player.durationStream.listen((dur) {
      if (mounted && dur != null) setState(() => _duration = dur);
    });
    // Track completion
    _player.playerStateStream.listen((state) {
      if (state.processingState == ProcessingState.completed && mounted) {
        setState(() {
          _playingId = null;
          _isPaused = false;
          _position = Duration.zero;
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
      // Same track: toggle pause/resume
      if (_isPaused) {
        await _player.play();
        setState(() => _isPaused = false);
      } else {
        await _player.pause();
        setState(() => _isPaused = true);
      }
      return;
    }

    // Different track: stop current and play new
    await _player.stop();
    await _player.setFilePath(e.path);
    await _player.play();
    setState(() {
      _playingId = e.id;
      _isPaused = false;
      _position = Duration.zero;
    });
  }

  Future<void> _stopPlayer() async {
    await _player.stop();
    setState(() {
      _playingId = null;
      _isPaused = false;
      _position = Duration.zero;
    });
  }

  // Seek on progress bar tap
  Future<void> _seekTo(double fraction, Duration total) async {
    final target = Duration(
      milliseconds: (fraction * total.inMilliseconds).round(),
    );
    await _player.seek(target);
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
        await Future.delayed(const Duration(milliseconds: 120));
        if (!mounted) return;
        setState(() => _saveProgress[e.id] = p);
      }

      final saved = await TtsService.savePermanent(File(e.path), e.filename);

      if (!mounted) return;
      setState(() => _saveProgress[e.id] = 1.0);
      await Future.delayed(const Duration(milliseconds: 300));
      if (!mounted) return;
      setState(() {
        _savingIds.remove(e.id);
        _saveProgress.remove(e.id);
      });

      _showSnack('Saved: ${saved.path.split('/').last}');
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
      content: Text(msg),
      backgroundColor: isError ? cRed : cGreen,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.all(12),
    ));
  }

  Color _langColor(String lang) {
    switch (lang) {
      case 'Urdu':  return cPurple;
      case 'Hindi': return cOrange;
      default:      return cBlue;
    }
  }

  String _formatDuration(Duration d) {
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$m:$s';
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
              await HistoryService.clear();
              _load();
            },
            child: const Text('Clear All',
                style: TextStyle(color: cRed, fontWeight: FontWeight.w700)),
          ),
      ],
      bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(color: cBorder, height: 1)),
    ),
    body: _loading
      ? const Center(child: CircularProgressIndicator(color: cGreen))
      : _history.isEmpty
        ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
            const Text('📥', style: TextStyle(fontSize: 48)),
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
            itemBuilder: (_, i) {
              final e = _history[i];
              final exists = File(e.path).existsSync();
              final isThisPlaying = _playingId == e.id;
              final isSaving = _savingIds.contains(e.id);
              final progress = _saveProgress[e.id] ?? 0.0;
              final lc = _langColor(e.language);

              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: MintCard(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // ── Top row: flag + info + download btn ──
                      Row(children: [
                        Container(
                          width: 44, height: 44,
                          decoration: BoxDecoration(
                              color: lc.withOpacity(0.12),
                              borderRadius: BorderRadius.circular(12)),
                          child: Center(
                            child: Text(
                              kLanguages[e.language]?.flag ?? '🎙️',
                              style: const TextStyle(fontSize: 22),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(e.filename,
                                style: const TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    color: cText),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis),
                            const SizedBox(height: 3),
                            Wrap(spacing: 6, children: [
                              _tag(e.language, lc),
                              _tag(e.gender, cGreen),
                              _tag(e.emotion, kEmotions[e.emotion]?.color ?? cMuted),
                            ]),
                            const SizedBox(height: 3),
                            Text(e.timestamp,
                                style: const TextStyle(fontSize: 11, color: cMuted)),
                          ],
                        )),
                        const SizedBox(width: 8),

                        // ── Download button (only if file exists and not saving) ──
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
                      ]),

                      // ── Saving progress bar ───────────────────
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
                        const SizedBox(height: 6),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: progress < 1.0 ? progress : null,
                            backgroundColor: cBorder,
                            valueColor:
                                const AlwaysStoppedAnimation<Color>(cGreen),
                            minHeight: 4,
                          ),
                        ),
                      ],

                      // ── Built-in Audio Player ─────────────────
                      if (exists) ...[
                        const SizedBox(height: 14),
                        _AudioPlayerWidget(
                          entry: e,
                          isPlaying: isThisPlaying && !_isPaused,
                          isPaused: isThisPlaying && _isPaused,
                          position: isThisPlaying ? _position : Duration.zero,
                          duration: isThisPlaying ? _duration : Duration.zero,
                          onPlayPause: () => _handlePlay(e),
                          onStop: isThisPlaying ? _stopPlayer : null,
                          onSeek: isThisPlaying
                              ? (frac) => _seekTo(frac, _duration)
                              : null,
                          formatDuration: _formatDuration,
                        ),
                      ],
                    ],
                  ),
                ),
              );
            },
          ),
  );

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

// ═══════════════════════════════════════════════════════
//  BUILT-IN AUDIO PLAYER WIDGET
// ═══════════════════════════════════════════════════════
class _AudioPlayerWidget extends StatelessWidget {
  final HistoryEntry entry;
  final bool isPlaying;
  final bool isPaused;
  final Duration position;
  final Duration duration;
  final VoidCallback onPlayPause;
  final VoidCallback? onStop;
  final void Function(double fraction)? onSeek;
  final String Function(Duration) formatDuration;

  const _AudioPlayerWidget({
    required this.entry,
    required this.isPlaying,
    required this.isPaused,
    required this.position,
    required this.duration,
    required this.onPlayPause,
    required this.formatDuration,
    this.onStop,
    this.onSeek,
  });

  @override
  Widget build(BuildContext context) {
    final isActive = isPlaying || isPaused;
    final totalMs = duration.inMilliseconds;
    final posMs = position.inMilliseconds;
    final fraction = (totalMs > 0) ? (posMs / totalMs).clamp(0.0, 1.0) : 0.0;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: isActive
            ? cGreen.withOpacity(0.08)
            : cBg.withOpacity(0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isActive ? cGreen.withOpacity(0.3) : cBorder,
        ),
      ),
      child: Column(
        children: [
          Row(children: [
            // Play/Pause button
            GestureDetector(
              onTap: onPlayPause,
              child: Container(
                width: 38, height: 38,
                decoration: BoxDecoration(
                  color: isPlaying ? cAmber : cGreen,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  isPlaying
                      ? Icons.pause_rounded
                      : isPaused
                          ? Icons.play_arrow_rounded
                          : Icons.play_arrow_rounded,
                  color: Colors.white,
                  size: 22,
                ),
              ),
            ),
            const SizedBox(width: 10),

            // Progress bar
            Expanded(
              child: GestureDetector(
                onTapDown: onSeek == null
                    ? null
                    : (details) {
                        final box = context.findRenderObject() as RenderBox?;
                        if (box == null) return;
                        // Rough width (container width minus icon and padding)
                        final barWidth = box.size.width - 80;
                        final frac =
                            (details.localPosition.dx / barWidth).clamp(0.0, 1.0);
                        onSeek!(frac);
                      },
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Waveform-style progress bar
                    Stack(children: [
                      // Background
                      Container(
                        height: 4,
                        decoration: BoxDecoration(
                          color: cBorder,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      // Progress fill
                      FractionallySizedBox(
                        widthFactor: fraction,
                        child: Container(
                          height: 4,
                          decoration: BoxDecoration(
                            color: isPlaying ? cAmber : cGreen,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                      ),
                    ]),
                    const SizedBox(height: 4),
                    // Time labels
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(formatDuration(position),
                            style: TextStyle(
                                fontSize: 10,
                                color: isActive ? cGreen : cMuted,
                                fontWeight: FontWeight.w600)),
                        Text(
                          totalMs > 0
                              ? formatDuration(duration)
                              : '--:--',
                          style: const TextStyle(
                              fontSize: 10, color: cMuted),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            // Stop button (only when active)
            if (isActive && onStop != null) ...[
              const SizedBox(width: 8),
              GestureDetector(
                onTap: onStop,
                child: Container(
                  width: 32, height: 32,
                  decoration: BoxDecoration(
                    color: cRed.withOpacity(0.1),
                    shape: BoxShape.circle,
                    border: Border.all(color: cRed.withOpacity(0.3)),
                  ),
                  child: const Icon(Icons.stop_rounded, color: cRed, size: 16),
                ),
              ),
            ],
          ]),
        ],
      ),
    );
  }
}
