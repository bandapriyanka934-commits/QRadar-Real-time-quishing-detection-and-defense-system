import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../core/config/env_config.dart';

class OfflineBanner extends StatelessWidget {
  final VoidCallback onRetry;
  final String? errorMessage;

  const OfflineBanner({
    Key? key,
    required this.onRetry,
    this.errorMessage,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: QRadarColors.maliciousBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: QRadarColors.malicious.withOpacity(0.4), width: 1.2),
      ),
      child: Row(
        children: [
          const Icon(Icons.cloud_off_rounded, color: QRadarColors.malicious, size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Backend Service Offline',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 13,
                    color: QRadarColors.malicious,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  errorMessage ?? 'Unable to connect to ${EnvConfig.baseUrl}. Please verify your connection or Settings.',
                  style: const TextStyle(
                    fontSize: 11,
                    color: QRadarColors.textSecondary,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh_rounded, color: QRadarColors.primaryBlue, size: 20),
            tooltip: 'Retry Connection',
          ),
        ],
      ),
    );
  }
}
