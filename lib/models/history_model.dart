// ═══════════════════════════════════════════════════════
//  HISTORY MODEL v2.2 — Fixed field names
// ═══════════════════════════════════════════════════════

class HistoryEntry {
  final String id;
  final String filename;
  final String filePath;   // was "path" — now consistent with history_service
  final String language;
  final String gender;
  final String emotion;
  final String character;
  final String text;
  final String timestamp;

  const HistoryEntry({
    required this.id,
    required this.filename,
    required this.filePath,
    required this.language,
    required this.gender,
    required this.emotion,
    this.character = '',
    this.text = '',
    required this.timestamp,
  });

  Map<String, dynamic> toJson() => {
    'id':        id,
    'filename':  filename,
    'filePath':  filePath,
    'path':      filePath,   // backward compat — old saves used "path"
    'language':  language,
    'gender':    gender,
    'emotion':   emotion,
    'character': character,
    'text':      text,
    'timestamp': timestamp,
  };

  factory HistoryEntry.fromJson(Map<String, dynamic> j) => HistoryEntry(
    id:        j['id']        ?? '',
    filename:  j['filename']  ?? '',
    filePath:  j['filePath']  ?? j['path'] ?? '',  // support both old + new
    language:  j['language']  ?? '',
    gender:    j['gender']    ?? '',
    emotion:   j['emotion']   ?? '',
    character: j['character'] ?? '',
    text:      j['text']      ?? '',
    timestamp: j['timestamp'] ?? '',
  );

  /// Convenience: the "path" getter so old code still compiles
  String get path => filePath;
}
