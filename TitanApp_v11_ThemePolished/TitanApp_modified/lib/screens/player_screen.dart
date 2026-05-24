import 'dart:io';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter/services.dart';
import 'package:just_audio/just_audio.dart';
import '../utils/constants.dart';
import '../models/history_model.dart';
import '../widgets/widgets.dart';
import '../services/tts_service.dart';

class PlayerScreen extends StatefulWidget {
  final HistoryEntry entry;
  final List<HistoryEntry> playlist; // saari history = playlist
  final int initialIndex;

  const PlayerScreen({
    super.key,
    required this.entry,
    required this.playlist,
    required this.initialIndex,
  });

  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen>
    with TickerProviderStateMixin {
  final _player = AudioPlayer();

  late int _currentIndex;
  HistoryEntry get _current => widget.playlist[_currentIndex];

  bool _isPlaying = false;
  bool _isSaving  = false;
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;

  // Animations
  late AnimationController _pulseCtrl;
  late AnimationController _rotateCtrl;
  late Animation<double>   _pulseAnim;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;

    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _rotateCtrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 8),
    );
    _pulseAnim = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );

    _setupListeners();
    _loadAndPlay(_currentIndex);
  }

  void _setupListeners() {
    _player.positionStream.listen((p) {
      if (mounted) setState(() => _position = p);
    });
    _player.durationStream.listen((d) {
      if (mounted && d != null) setState(() => _duration = d);
    });
    _player.playerStateStream.listen((state) {
      if (!mounted) return;
      final playing = state.playing &&
          state.processingState != ProcessingState.completed;
      setState(() => _isPlaying = playing);

      if (playing) {
        _pulseCtrl.repeat(reverse: true);
        _rotateCtrl.repeat();
      } else {
        _pulseCtrl.stop();
        _rotateCtrl.stop();
      }

      // Auto next on completion
      if (state.processingState == ProcessingState.completed) {
        _playNext();
      }
    });
  }

  Future<void> _loadAndPlay(int index) async {
    if (index < 0 || index >= widget.playlist.length) return;
    final entry = widget.playlist[index];
    if (!File(entry.path).existsSync()) return;

    try {
      await _player.setAudioSource(AudioSource.file(entry.path), preload: true);
      await _player.play();
      setState(() {
        _currentIndex = index;
        _position = Duration.zero;
      });
    } catch (e) {
      _showSnack('Cannot play: $e', isError: true);
    }
  }

  void _playNext() {
    if (_currentIndex < widget.playlist.length - 1) {
      _loadAndPlay(_currentIndex + 1);
    }
  }

  void _playPrev() {
    if (_position.inSeconds > 3) {
      _player.seek(Duration.zero);
    } else if (_currentIndex > 0) {
      _loadAndPlay(_currentIndex - 1);
    }
  }

  Future<void> _togglePlay() async {
    HapticFeedback.lightImpact();
    if (_isPlaying) {
      await _player.pause();
    } else {
      final state = _player.processingState;
      if (state == ProcessingState.completed) {
        // Audio khatam ho gaya - start se dobara chalao
        await _player.seek(Duration.zero);
        await _player.play();
      } else if (state == ProcessingState.idle || state == ProcessingState.loading) {
        // Player idle hai - file reload karke play karo
        await _loadAndPlay(_currentIndex);
      } else {
        // Normal pause → resume
        await _player.play();
      }
    }
  }

  Future<void> _save() async {
    if (_isSaving) return;
    setState(() => _isSaving = true);
    try {
      final saved = await TtsService.savePermanent(
        File(_current.path),
        _current.filename,
      );
      _showSnack('✅ Saved: ${saved.path.split('/').last}');
    } catch (e) {
      _showSnack('Save failed: $e', isError: true);
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
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

  String _fmt(Duration d) {
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  void dispose() {
    _player.dispose();
    _pulseCtrl.dispose();
    _rotateCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final totalMs = _duration.inMilliseconds;
    final posMs   = _position.inMilliseconds;
    final frac    = totalMs > 0 ? (posMs / totalMs).clamp(0.0, 1.0) : 0.0;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      body: Stack(
        children: [
          // ── Animated background gradient ──────────────────
          AnimatedContainer(
            duration: const Duration(seconds: 1),
            decoration: BoxDecoration(
              gradient: RadialGradient(
                center: Alignment.topCenter,
                radius: 1.4,
                colors: [
                  cGreen.withOpacity(_isPlaying ? 0.18 : 0.08),
                  const Color(0xFF0A0A0A),
                ],
              ),
            ),
          ),

          SafeArea(
            child: Column(
              children: [
                // ── Top bar ────────────────────────────────
                Padding(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 12),
                  child: Row(children: [
                    GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        width: 40, height: 40,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.keyboard_arrow_down_rounded,
                            color: Colors.white, size: 26),
                      ),
                    ),
                    const Spacer(),
                    Text(
                      'Now Playing',
                      style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Colors.white.withOpacity(0.7)),
                    ),
                    const Spacer(),
                    // Download button
                    GestureDetector(
                      onTap: _isSaving ? null : _save,
                      child: Container(
                        width: 40, height: 40,
                        decoration: BoxDecoration(
                          color: cTeal.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: cTeal.withOpacity(0.3)),
                        ),
                        child: _isSaving
                            ? const Padding(
                                padding: EdgeInsets.all(10),
                                child: CircularProgressIndicator(
                                    color: cTeal, strokeWidth: 2.5))
                            : const Icon(Icons.save_alt_rounded,
                                color: cTeal, size: 20),
                      ),
                    ),
                  ]),
                ),

                const SizedBox(height: 24),

                // ── Album art — animated orb ───────────────
                Expanded(
                  flex: 5,
                  child: Center(
                    child: AnimatedBuilder(
                      animation: Listenable.merge([_pulseAnim, _rotateCtrl]),
                      builder: (_, __) {
                        return Transform.scale(
                          scale: _isPlaying ? _pulseAnim.value : 1.0,
                          child: Container(
                            width: 260, height: 260,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              gradient: RadialGradient(
                                colors: [
                                  Colors.white.withOpacity(0.9),
                                  cGreen.withOpacity(0.7),
                                  cGreen2.withOpacity(0.5),
                                  cGreen.withOpacity(0.2),
                                  Colors.transparent,
                                ],
                                stops: const [0.0, 0.25, 0.5, 0.75, 1.0],
                                center: Alignment(
                                  sin(_rotateCtrl.value * 2 * pi) * 0.2,
                                  cos(_rotateCtrl.value * 2 * pi) * 0.2,
                                ),
                                radius: 1.0,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: cGreen.withOpacity(
                                      _isPlaying ? 0.5 : 0.2),
                                  blurRadius: _isPlaying ? 60 : 30,
                                  spreadRadius: _isPlaying ? 10 : 0,
                                ),
                              ],
                            ),
                            child: Center(
                              child: SvgPicture.asset(
                                kLanguages[_current.language]?.flag ?? 'assets/svg/icon_mic.svg',
                                width: 64, height: 64,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ),

                // ── Track info ─────────────────────────────
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 28),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(children: [
                        Expanded(
                          child: Text(
                            _current.filename
                                .replaceAll('.wav', '')
                                .replaceAll('.mp3', ''),
                            style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.w800,
                                color: Colors.white),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ]),
                      const SizedBox(height: 6),
                      Row(children: [
                        _pill(_current.language,
                            kLanguages[_current.language]?.flag ?? ''),
                        const SizedBox(width: 8),
                        _pill(_current.gender, ''),
                        const SizedBox(width: 8),
                        _pill(_current.emotion, ''),
                      ]),
                      const SizedBox(height: 4),
                      Text(
                        _current.timestamp,
                        style: TextStyle(
                            fontSize: 12,
                            color: Colors.white.withOpacity(0.4)),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // ── Progress bar ───────────────────────────
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 28),
                  child: Column(children: [
                    SliderTheme(
                      data: SliderTheme.of(context).copyWith(
                        trackHeight: 3,
                        thumbShape: const RoundSliderThumbShape(
                            enabledThumbRadius: 6),
                        overlayShape:
                            const RoundSliderOverlayShape(overlayRadius: 14),
                        activeTrackColor: cGreen,
                        inactiveTrackColor:
                            Colors.white.withOpacity(0.1),
                        thumbColor: Colors.white,
                        overlayColor: cGreen.withOpacity(0.2),
                      ),
                      child: Slider(
                        value: frac,
                        onChanged: (v) {
                          if (totalMs > 0) {
                            _player.seek(Duration(
                                milliseconds: (v * totalMs).round()));
                          }
                        },
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(_fmt(_position),
                              style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.white.withOpacity(0.6))),
                          Text(
                              totalMs > 0 ? _fmt(_duration) : '--:--',
                              style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.white.withOpacity(0.4))),
                        ],
                      ),
                    ),
                  ]),
                ),

                const SizedBox(height: 24),

                // ── Controls ───────────────────────────────
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 40),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      // Previous
                      _ControlBtn(
                        icon: Icons.skip_previous_rounded,
                        size: 32,
                        onTap: _playPrev,
                        enabled: _currentIndex > 0 ||
                            _position.inSeconds > 3,
                      ),

                      // Play / Pause — big button
                      GestureDetector(
                        onTap: _togglePlay,
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 70, height: 70,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              colors: _isPlaying
                                  ? [cAmber, cAmber.withOpacity(0.8)]
                                  : [cGreen, cGreen2],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: (_isPlaying ? cGreen2 : cGreen)
                                    .withOpacity(0.5),
                                blurRadius: 24,
                                offset: const Offset(0, 6),
                              ),
                            ],
                          ),
                          child: AnimatedSwitcher(
                            duration: const Duration(milliseconds: 300),
                            transitionBuilder: (child, anim) => ScaleTransition(
                              scale: anim,
                              child: FadeTransition(opacity: anim, child: child),
                            ),
                            child: Icon(
                              _isPlaying
                                  ? Icons.pause_rounded
                                  : Icons.play_arrow_rounded,
                              key: ValueKey(_isPlaying),
                              color: Colors.white,
                              size: 38,
                            ),
                          ),
                        ),
                      ),

                      // Next
                      _ControlBtn(
                        icon: Icons.skip_next_rounded,
                        size: 32,
                        onTap: _playNext,
                        enabled:
                            _currentIndex < widget.playlist.length - 1,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 32),

                // ── Playlist indicator ─────────────────────
                if (widget.playlist.length > 1)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 20),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(
                        widget.playlist.length.clamp(0, 7),
                        (i) => AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          width: i == _currentIndex ? 20 : 6,
                          height: 6,
                          margin: const EdgeInsets.symmetric(horizontal: 3),
                          decoration: BoxDecoration(
                            color: i == _currentIndex
                                ? cGreen
                                : Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(3),
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _pill(String label, String emoji) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
    decoration: BoxDecoration(
      color: Colors.white.withOpacity(0.08),
      borderRadius: BorderRadius.circular(20),
    ),
    child: Text(
      emoji.isNotEmpty ? '$emoji $label' : label,
      style: TextStyle(
          fontSize: 11,
          color: Colors.white.withOpacity(0.7),
          fontWeight: FontWeight.w600),
    ),
  );
}

// ── Control Button ────────────────────────────────────────
class _ControlBtn extends StatelessWidget {
  final IconData icon;
  final double size;
  final VoidCallback onTap;
  final bool enabled;

  const _ControlBtn({
    required this.icon,
    required this.size,
    required this.onTap,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) => GestureDetector(
    onTap: enabled ? onTap : null,
    child: Container(
      width: 52, height: 52,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(enabled ? 0.08 : 0.03),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Icon(icon,
          color: Colors.white.withOpacity(enabled ? 0.9 : 0.3),
          size: size),
    ),
  );
}
