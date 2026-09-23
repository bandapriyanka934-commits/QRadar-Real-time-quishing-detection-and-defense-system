import 'package:flutter/material.dart';
import '../models/heuristic_indicator.dart';
import '../core/theme/app_theme.dart';

class IndicatorCard extends StatelessWidget {
  final HeuristicIndicator indicator;

  const IndicatorCard({Key? key, required this.indicator}) : super(key: key);

  Color _getSeverityColor(String severity) {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return QRadarColors.malicious;
      case 'MEDIUM':
        return QRadarColors.suspicious;
      case 'LOW':
      default:
        return QRadarColors.safe;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isTriggered = indicator.triggered;
    final sevColor = _getSeverityColor(indicator.severity);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: isTriggered ? sevColor.withOpacity(0.08) : QRadarColors.surfaceElevated,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isTriggered ? sevColor.withOpacity(0.45) : QRadarColors.border,
          width: isTriggered ? 1.2 : 1.0,
        ),
      ),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isTriggered ? Icons.report_problem_rounded : Icons.check_circle_outline_rounded,
                color: isTriggered ? sevColor : QRadarColors.safe,
                size: 20,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  indicator.name,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: QRadarColors.textPrimary,
                  ),
                ),
              ),
              if (isTriggered)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: sevColor.withOpacity(0.18),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: sevColor.withOpacity(0.4), width: 1),
                  ),
                  child: Text(
                    '+${indicator.scoreContribution} pts',
                    style: TextStyle(
                      color: sevColor,
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                )
              else
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: QRadarColors.safeBg,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: QRadarColors.safe.withOpacity(0.3), width: 1),
                  ),
                  child: const Text(
                    'CLEAN',
                    style: TextStyle(
                      color: QRadarColors.safe,
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            indicator.explanation,
            style: TextStyle(
              fontSize: 13,
              color: isTriggered ? QRadarColors.textSubtle : QRadarColors.textSecondary,
              height: 1.35,
            ),
          ),
          if (isTriggered && indicator.evidence != null && indicator.evidence!.isNotEmpty) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: QRadarColors.primaryBackground,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: QRadarColors.border),
              ),
              child: Row(
                children: [
                  const Icon(Icons.code_rounded, size: 14, color: QRadarColors.textSecondary),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      indicator.evidence!,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 11,
                        color: QRadarColors.primaryBlue,
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
