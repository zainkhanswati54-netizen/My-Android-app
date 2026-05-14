import 'dart:io';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import '../utils/constants.dart';
import '../models/history_model.dart';
import '../widgets/mint_card.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});
  @override
  State<HistoryScreen> createState() => _HistoryState();
}

class _HistoryState extends State<HistoryScreen> {
  List<HistoryEntry> _history = [];
  bool _loading = true;
  String? _playingId;
  final _player = AudioPlayer();

  @override
  void initState() { super.initState(); _load(); }

  @override
  void dispose() { _player.dispose(); super.dispose(); }

  Future<void> _load() async {
    final h = await HistoryService.load();
    if (mounted) setState(() { _history = h; _loading = false; });
  }

  Future<void> _play(HistoryEntry e) async {
    if (_playingId == e.id) {
      await _player.stop();
      setState(() => _playingId = null);
      return;
    }
    if (!File(e.path).existsSync()) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('File not found'), backgroundColor: cRed, behavior: SnackBarBehavior.floating));
      return;
    }
    await _player.setFilePath(e.path);
    await _player.play();
    setState(() => _playingId = e.id);
    _player.playerStateStream.listen((s) {
      if (s.processingState == ProcessingState.completed && mounted) setState(() => _playingId = null);
    });
  }

  Color _langColor(String lang) {
    switch (lang) {
      case 'Urdu': return cPurple;
      case 'Hindi': return cOrange;
      default: return cBlue;
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: cBg,
    appBar: AppBar(
      backgroundColor: cBg2, elevation: 0, foregroundColor: cText,
      title: const Text('Voice History', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: cText)),
      actions: [
        if (_history.isNotEmpty)
          TextButton(
            onPressed: () async {
              await HistoryService.clear();
              _load();
            },
            child: const Text('Clear All', style: TextStyle(color: cRed, fontWeight: FontWeight.w700)),
          ),
      ],
      bottom: PreferredSize(preferredSize: const Size.fromHeight(1), child: Container(color: cBorder, height: 1)),
    ),
    body: _loading
      ? const Center(child: CircularProgressIndicator(color: cGreen))
      : _history.isEmpty
        ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
            const Text('🎙️', style: TextStyle(fontSize: 48)),
            const SizedBox(height: 16),
            const Text('No recordings yet', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cText2)),
            const SizedBox(height: 6),
            const Text('Generate and save your first voice!', style: TextStyle(fontSize: 13, color: cMuted)),
          ]))
        : ListView.builder(
            padding: const EdgeInsets.all(14),
            itemCount: _history.length,
            itemBuilder: (_, i) {
              final e = _history[i];
              final exists = File(e.path).existsSync();
              final isPlaying = _playingId == e.id;
              final lc = _langColor(e.language);
              return Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: MintCard(
                  padding: const EdgeInsets.all(12),
                  child: Row(children: [
                    Container(
                      width: 44, height: 44,
                      decoration: BoxDecoration(color: lc.withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
                      child: Center(child: Text(kLanguages[e.language]?.flag ?? '🎙️', style: const TextStyle(fontSize: 22))),
                    ),
                    const SizedBox(width: 12),
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text(e.filename, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: cText), maxLines: 1, overflow: TextOverflow.ellipsis),
                      const SizedBox(height: 3),
                      Wrap(spacing: 6, children: [
                        _tag(e.language, lc),
                        _tag(e.gender, cGreen),
                        _tag(e.emotion, kEmotions[e.emotion]?.color ?? cMuted),
                      ]),
                      const SizedBox(height: 3),
                      Text(e.timestamp, style: const TextStyle(fontSize: 11, color: cMuted)),
                    ])),
                    const SizedBox(width: 8),
                    if (exists)
                      GestureDetector(
                        onTap: () => _play(e),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 40, height: 40,
                          decoration: BoxDecoration(color: isPlaying ? cAmber : cGreen, borderRadius: BorderRadius.circular(20)),
                          child: Icon(isPlaying ? Icons.stop_rounded : Icons.play_arrow_rounded, color: Colors.white, size: 22),
                        ),
                      )
                    else
                      const Text('[Missing]', style: TextStyle(fontSize: 10, color: cRed)),
                  ]),
                ),
              );
            },
          ),
  );

  Widget _tag(String label, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
    decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
    child: Text(label, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: color)),
  );
}
