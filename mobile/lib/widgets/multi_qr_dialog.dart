import 'package:flutter/material.dart';
import '../models/multi_qr_response.dart';
import '../core/theme/app_theme.dart';

class MultiQRSelectionDialog extends StatelessWidget {
  final List<QRItem> qrCodes;
  final Function(int selectedIndex, String content) onSelect;

  const MultiQRSelectionDialog({
    Key? key,
    required this.qrCodes,
    required this.onSelect,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: QRadarColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: const BorderSide(color: QRadarColors.border, width: 1.2),
      ),
      child: Padding(
        padding: const EdgeInsets.all(22.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: QRadarColors.surfaceElevated,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: QRadarColors.border),
                  ),
                  child: const Icon(Icons.qr_code_2_rounded, color: QRadarColors.primaryBlue, size: 24),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Multiple QR Codes Detected',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                          color: QRadarColors.textPrimary,
                        ),
                      ),
                      Text(
                        'Select a destination payload to evaluate',
                        style: TextStyle(
                          fontSize: 12,
                          color: QRadarColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(color: QRadarColors.border, height: 1),
            const SizedBox(height: 12),
            Flexible(
              child: ListView.separated(
                shrinkWrap: true,
                itemCount: qrCodes.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final item = qrCodes[index];
                  final isDangerous = item.qrType == 'dangerous_scheme';

                  return InkWell(
                    onTap: () {
                      Navigator.of(context).pop();
                      onSelect(index, item.content);
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: QRadarColors.surfaceElevated,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isDangerous ? QRadarColors.malicious.withOpacity(0.5) : QRadarColors.border,
                        ),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 28,
                            height: 28,
                            alignment: Alignment.center,
                            decoration: BoxDecoration(
                              color: QRadarColors.primaryBackground,
                              shape: BoxShape.circle,
                              border: Border.all(color: QRadarColors.border),
                            ),
                            child: Text(
                              '${index + 1}',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: QRadarColors.primaryBlue,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: isDangerous
                                            ? QRadarColors.maliciousBg
                                            : QRadarColors.primaryBlue.withOpacity(0.12),
                                        borderRadius: BorderRadius.circular(4),
                                        border: Border.all(
                                          color: isDangerous
                                              ? QRadarColors.malicious.withOpacity(0.4)
                                              : QRadarColors.primaryBlue.withOpacity(0.3),
                                        ),
                                      ),
                                      child: Text(
                                        item.qrType.toUpperCase(),
                                        style: TextStyle(
                                          fontSize: 10,
                                          fontWeight: FontWeight.w800,
                                          color: isDangerous ? QRadarColors.malicious : QRadarColors.primaryBlue,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  item.content,
                                  style: const TextStyle(
                                    fontSize: 13,
                                    color: QRadarColors.textPrimary,
                                    fontFamily: 'monospace',
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          ),
                          const Icon(Icons.chevron_right_rounded, color: QRadarColors.textSecondary),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Cancel', style: TextStyle(color: QRadarColors.textSecondary, fontWeight: FontWeight.w600)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
