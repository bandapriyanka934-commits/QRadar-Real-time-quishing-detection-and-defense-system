import 'package:intl/intl.dart';

class Formatters {
  static String formatTimestamp(String isoString) {
    if (isoString.isEmpty) return 'Unknown';
    try {
      final dt = DateTime.parse(isoString).toLocal();
      return DateFormat('MMM dd, yyyy • HH:mm:ss').format(dt);
    } catch (_) {
      return isoString;
    }
  }

  static String formatRelativeTime(String isoString) {
    if (isoString.isEmpty) return 'Just now';
    try {
      final dt = DateTime.parse(isoString).toLocal();
      final diff = DateTime.now().difference(dt);

      if (diff.inSeconds < 60) return 'Just now';
      if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
      if (diff.inHours < 24) return '${diff.inHours}h ago';
      if (diff.inDays < 7) return '${diff.inDays}d ago';
      return DateFormat('MMM dd').format(dt);
    } catch (_) {
      return isoString;
    }
  }

  static String truncate(String text, int maxLength) {
    if (text.length <= maxLength) return text;
    return '${text.substring(0, maxLength)}...';
  }
}
