import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class VerdictBadge extends StatelessWidget {
  final String verdict;
  final bool isLarge;

  const VerdictBadge({
    Key? key,
    required this.verdict,
    this.isLarge = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final color = AppTheme.getVerdictColor(verdict);
    final bgColor = AppTheme.getVerdictBgColor(verdict);

    IconData icon;
    String prefixSymbol = '';
    switch (verdict.toUpperCase()) {
      case 'SAFE':
        icon = Icons.check_circle_rounded;
        prefixSymbol = '✓ ';
        break;
      case 'SUSPICIOUS':
        icon = Icons.warning_rounded;
        prefixSymbol = '⚠ ';
        break;
      case 'MALICIOUS':
        icon = Icons.gpp_bad_rounded;
        prefixSymbol = '✕ ';
        break;
      case 'BLOCK':
      case 'BLOCKED':
        icon = Icons.block_rounded;
        prefixSymbol = '⛔ ';
        break;
      default:
        icon = Icons.help_outline_rounded;
    }

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isLarge ? 16 : 10,
        vertical: isLarge ? 7 : 4,
      ),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(isLarge ? 10 : 6),
        border: Border.all(color: color.withOpacity(0.45), width: 1.2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: isLarge ? 18 : 13),
          const SizedBox(width: 6),
          Text(
            verdict.toUpperCase(),
            style: TextStyle(
              color: color,
              fontSize: isLarge ? 14 : 11,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.8,
            ),
          ),
        ],
      ),
    );
  }
}
