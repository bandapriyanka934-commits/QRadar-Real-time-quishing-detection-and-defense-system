import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/formatters.dart';
import '../../models/scan_result.dart';
import '../../widgets/risk_score_gauge.dart';
import '../../widgets/verdict_badge.dart';
import '../../widgets/indicator_card.dart';

class ResultScreen extends StatelessWidget {
  final SecurityResult result;

  const ResultScreen({Key? key, required this.result}) : super(key: key);

  void _copyToClipboard(BuildContext context, String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Target URL copied to clipboard'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  Future<void> _handleOpenUrl(BuildContext context) async {
    final targetUrl = result.normalizedUrl ?? result.originalContent;
    if (result.isMalicious) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Cannot open destination: Blocked by QRadar Security Policy.'),
          backgroundColor: QRadarColors.block,
        ),
      );
      return;
    }

    if (result.isSuspicious) {
      // Explicit confirmation dialog for suspicious URLs
      final confirm = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: QRadarColors.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: QRadarColors.suspicious, width: 1.5),
          ),
          title: const Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: QRadarColors.suspicious, size: 24),
              SizedBox(width: 10),
              Text('Proceed with Caution?', style: TextStyle(color: QRadarColors.textPrimary, fontSize: 17, fontWeight: FontWeight.bold)),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'This destination was flagged with SUSPICIOUS risk indicators. Visiting it may expose you to credential harvesting or phishing.',
                style: TextStyle(color: QRadarColors.textSecondary, fontSize: 13, height: 1.4),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: QRadarColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: QRadarColors.border),
                ),
                child: Text(
                  targetUrl,
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 11, color: QRadarColors.primaryBlue),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(false),
              child: const Text('Cancel / Abort', style: TextStyle(color: QRadarColors.textSecondary)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: QRadarColors.suspicious,
                foregroundColor: QRadarColors.primaryBackground,
              ),
              onPressed: () => Navigator.of(ctx).pop(true),
              child: const Text('Proceed (Confirm)'),
            ),
          ],
        ),
      );

      if (confirm != true) return;
    } else {
      // Safe confirmation
      final confirm = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: QRadarColors.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: QRadarColors.border),
          ),
          title: const Text('Open in Browser?', style: TextStyle(color: QRadarColors.textPrimary, fontSize: 17, fontWeight: FontWeight.bold)),
          content: Text(
            'You are about to navigate to:\n$targetUrl',
            style: const TextStyle(color: QRadarColors.textSecondary, fontSize: 13, height: 1.4),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(false),
              child: const Text('Cancel', style: TextStyle(color: QRadarColors.textSecondary)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: QRadarColors.primaryBlue,
                foregroundColor: QRadarColors.primaryBackground,
              ),
              onPressed: () => Navigator.of(ctx).pop(true),
              child: const Text('Open URL'),
            ),
          ],
        ),
      );

      if (confirm != true) return;
    }

    try {
      final uri = Uri.parse(targetUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not launch URL in external browser.')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to open: $e'), backgroundColor: QRadarColors.malicious),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final verdictColor = AppTheme.getVerdictColor(result.verdict);
    final triggeredCount = result.heuristics.where((h) => h.triggered).length;

    return Scaffold(
      backgroundColor: QRadarColors.primaryBackground,
      appBar: AppBar(
        title: const Text('Security Evaluation Verdict'),
        actions: [
          IconButton(
            icon: const Icon(Icons.copy_rounded, color: QRadarColors.textSecondary),
            tooltip: 'Copy URL',
            onPressed: () => _copyToClipboard(context, result.normalizedUrl ?? result.originalContent),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Verdict & Gauge Hero Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: QRadarColors.surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: verdictColor.withOpacity(0.4), width: 1.5),
                boxShadow: [
                  BoxShadow(
                    color: verdictColor.withOpacity(0.08),
                    blurRadius: 20,
                    spreadRadius: 1,
                  ),
                ],
              ),
              child: Column(
                children: [
                  VerdictBadge(verdict: result.verdict, isLarge: true),
                  const SizedBox(height: 20),
                  RiskScoreGauge(score: result.riskScore, size: 160),
                  const SizedBox(height: 18),
                  Text(
                    'RECOMMENDED ACTION: ${result.recommendedAction}',
                    style: TextStyle(
                      color: verdictColor,
                      fontSize: 13,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 1.0,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Analyzed at ${Formatters.formatTimestamp(result.analyzedAt)}',
                    style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Destination Target Box
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: QRadarColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: QRadarColors.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.link_rounded, size: 18, color: QRadarColors.primaryBlue),
                      SizedBox(width: 8),
                      Text(
                        'DESTINATION TARGET',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 0.8,
                          color: QRadarColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  SelectableText(
                    result.normalizedUrl ?? result.originalContent,
                    style: const TextStyle(
                      fontSize: 14,
                      fontFamily: 'monospace',
                      color: QRadarColors.textPrimary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (result.domain != null) ...[
                    const SizedBox(height: 6),
                    Text(
                      'Host Domain: ${result.domain}',
                      style: const TextStyle(fontSize: 12, color: QRadarColors.textSecondary),
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Primary Explainable Reasons
            if (result.reasons.isNotEmpty) ...[
              const Text(
                'EXPLAINABLE THREAT REASONS',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.0,
                  color: QRadarColors.textSecondary,
                ),
              ),
              const SizedBox(height: 10),
              ...result.reasons.map(
                (reason) => Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  decoration: BoxDecoration(
                    color: QRadarColors.surfaceElevated,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: QRadarColors.border),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        result.isSafe ? Icons.check_circle_rounded : Icons.shield_rounded,
                        color: verdictColor,
                        size: 18,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          reason,
                          style: const TextStyle(fontSize: 13, color: QRadarColors.textPrimary, height: 1.35),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Machine Learning & Threat Intel Grid
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ML Card
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: QRadarColors.surface,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: QRadarColors.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.psychology_rounded, size: 16, color: QRadarColors.primaryBlue),
                                SizedBox(width: 6),
                                Text(
                                  'MACHINE LEARNING',
                                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: QRadarColors.textSecondary),
                                ),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: result.ml.isAnalyzed
                                    ? QRadarColors.primaryBlue.withOpacity(0.15)
                                    : QRadarColors.surfaceElevated,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                result.ml.isAnalyzed ? 'Analyzed' : (result.ml.isNotApplicable ? 'NOT APPLICABLE' : 'Unavailable'),
                                style: TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.bold,
                                  color: result.ml.isAnalyzed ? QRadarColors.primaryBlue : QRadarColors.textSecondary,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        if (result.ml.isAnalyzed && result.ml.phishingProbability != null) ...[
                          Text(
                            result.ml.prediction ?? ((result.ml.phishingProbability ?? 0.0) >= 0.5 ? 'Phishing' : 'Legitimate'),
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w900,
                              color: (result.ml.phishingProbability ?? 0.0) >= 0.5
                                  ? QRadarColors.malicious
                                  : QRadarColors.safe,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Confidence: ${(((result.ml.confidence ?? result.ml.phishingProbability) ?? 0.0) * 100).toStringAsFixed(0)}% (${result.ml.modelName})',
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                          ),
                        ] else if (result.ml.isNotApplicable) ...[
                          const Text(
                            'Not Applicable',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.textSecondary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            result.ml.reason ?? 'Non-web QR payload',
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ] else ...[
                          const Text(
                            'Unavailable',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.suspicious,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            result.ml.reason ?? 'Model offline / uninitialized',
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Threat Intel Card
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: QRadarColors.surface,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: QRadarColors.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.radar_rounded, size: 16, color: QRadarColors.accentCyan),
                                SizedBox(width: 6),
                                Text(
                                  'THREAT INTEL',
                                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: QRadarColors.textSecondary),
                                ),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: result.threatIntelligence.isMalicious
                                    ? QRadarColors.malicious.withOpacity(0.15)
                                    : (result.threatIntelligence.isSuspicious || result.threatIntelligence.isNotConfigured || result.threatIntelligence.isUnavailable
                                        ? QRadarColors.suspicious.withOpacity(0.15)
                                        : (result.threatIntelligence.isClean
                                            ? QRadarColors.safe.withOpacity(0.15)
                                            : QRadarColors.surfaceElevated)),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                result.threatIntelligence.isNotApplicable
                                    ? 'NOT APPLICABLE'
                                    : (result.threatIntelligence.isNotConfigured
                                        ? 'Not Configured'
                                        : (result.threatIntelligence.isUnavailable
                                            ? 'Unavailable'
                                            : (result.threatIntelligence.isNoRecord
                                                ? 'No Record'
                                                : (result.threatIntelligence.isMalicious
                                                    ? 'Threat Found'
                                                    : (result.threatIntelligence.isSuspicious
                                                        ? 'Suspicious'
                                                        : 'Checked'))))),
                                style: TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.bold,
                                  color: result.threatIntelligence.isMalicious
                                      ? QRadarColors.malicious
                                      : (result.threatIntelligence.isSuspicious || result.threatIntelligence.isNotConfigured || result.threatIntelligence.isUnavailable
                                          ? QRadarColors.suspicious
                                          : (result.threatIntelligence.isClean ? QRadarColors.safe : QRadarColors.textSecondary)),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        if (result.threatIntelligence.isNotApplicable) ...[
                          const Text(
                            'Not Applicable',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.textSecondary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            result.threatIntelligence.message ?? result.threatIntelligence.reason ?? 'No web URL/domain to check',
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ] else if (result.threatIntelligence.isNotConfigured) ...[
                          const Text(
                            'Not Configured',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.suspicious,
                            ),
                          ),
                          const SizedBox(height: 4),
                          const Text(
                            'External threat intelligence is currently unavailable.',
                            style: TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ] else if (result.threatIntelligence.isUnavailable) ...[
                          const Text(
                            'Unavailable',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.suspicious,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${result.threatIntelligence.provider}: ${result.threatIntelligence.message ?? result.threatIntelligence.reason ?? "API request failed"}',
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ] else if (result.threatIntelligence.isMalicious) ...[
                          Text(
                            result.threatIntelligence.maliciousCount != null
                                ? 'Malicious: ${result.threatIntelligence.maliciousCount}'
                                : 'Threat Detected',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.malicious,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${result.threatIntelligence.provider}${result.threatIntelligence.suspiciousCount != null ? ' (Suspicious: ${result.threatIntelligence.suspiciousCount})' : ''}',
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ] else if (result.threatIntelligence.isSuspicious) ...[
                          Text(
                            result.threatIntelligence.suspiciousCount != null
                                ? 'Suspicious: ${result.threatIntelligence.suspiciousCount}'
                                : 'Suspicious Signal',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.suspicious,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            result.threatIntelligence.provider,
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ] else if (result.threatIntelligence.isNoRecord) ...[
                          const Text(
                            'Not Previously Seen',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.primaryBlue,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Provider: ${result.threatIntelligence.provider} (No prior record)',
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ] else ...[
                          const Text(
                            'No Threat Found',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: QRadarColors.safe,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Provider: ${result.threatIntelligence.provider}',
                            style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Heuristics Breakdown Header
            Row(
              children: [
                const Text(
                  '12 HEURISTIC SIGNAL BREAKDOWN',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.0,
                    color: QRadarColors.textSecondary,
                  ),
                ),
                const Spacer(),
                Text(
                  '$triggeredCount / ${result.heuristics.length} Triggered',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: triggeredCount > 0 ? QRadarColors.suspicious : QRadarColors.safe,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // List of Heuristic Indicators
            if (result.heuristics.isEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: QRadarColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: QRadarColors.border),
                ),
                child: const Text(
                  'No URL heuristics evaluated (plain text payload).',
                  style: TextStyle(color: QRadarColors.textSecondary, fontSize: 13),
                ),
              )
            else
              ...result.heuristics.map((h) => IndicatorCard(indicator: h)),

            const SizedBox(height: 28),

            // Action Execution Button Gate
            if (result.isMalicious)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: QRadarColors.maliciousBg,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: QRadarColors.malicious.withOpacity(0.5), width: 1.5),
                ),
                child: const Column(
                  children: [
                    Icon(Icons.block_rounded, color: QRadarColors.malicious, size: 36),
                    SizedBox(height: 10),
                    Text(
                      'DESTINATION ACCESS BLOCKED',
                      style: TextStyle(
                        color: QRadarColors.malicious,
                        fontWeight: FontWeight.w900,
                        fontSize: 15,
                        letterSpacing: 0.5,
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      'This URL has been verified as a hazardous destination. QRadar prevented navigation to safeguard your credentials and device.',
                      style: TextStyle(color: QRadarColors.textSecondary, fontSize: 12, height: 1.4),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              )
            else
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: result.isSuspicious ? QRadarColors.suspicious : QRadarColors.primaryBlue,
                    foregroundColor: QRadarColors.primaryBackground,
                  ),
                  icon: Icon(
                    result.isSuspicious ? Icons.warning_rounded : Icons.open_in_browser_rounded,
                    size: 20,
                  ),
                  label: Text(
                    result.isSuspicious ? 'PROCEED WITH CAUTION (CONFIRM)' : 'OPEN DESTINATION IN BROWSER',
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13, letterSpacing: 0.5),
                  ),
                  onPressed: () => _handleOpenUrl(context),
                ),
              ),

            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
