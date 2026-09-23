import 'package:flutter/material.dart';
import '../../services/scan_api_service.dart';
import '../../models/scan_result.dart';
import '../../core/theme/app_theme.dart';
import '../results/result_screen.dart';

class HistoryDetailScreen extends StatefulWidget {
  final String scanId;

  const HistoryDetailScreen({Key? key, required this.scanId}) : super(key: key);

  @override
  State<HistoryDetailScreen> createState() => _HistoryDetailScreenState();
}

class _HistoryDetailScreenState extends State<HistoryDetailScreen> {
  final ScanApiService _apiService = ScanApiService();
  late Future<SecurityResult> _futureResult;

  @override
  void initState() {
    super.initState();
    _futureResult = _apiService.getScanDetails(widget.scanId);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<SecurityResult>(
      future: _futureResult,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Scaffold(
            backgroundColor: QRadarColors.primaryBackground,
            appBar: AppBar(title: const Text('Scan Log Details')),
            body: const Center(
              child: CircularProgressIndicator(color: QRadarColors.primaryBlue),
            ),
          );
        } else if (snapshot.hasError) {
          return Scaffold(
            backgroundColor: QRadarColors.primaryBackground,
            appBar: AppBar(title: const Text('Scan Log Details')),
            body: Center(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline_rounded, color: QRadarColors.malicious, size: 48),
                    const SizedBox(height: 16),
                    Text(
                      'Failed to load scan details: ${snapshot.error}',
                      style: const TextStyle(color: QRadarColors.textSecondary),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        setState(() {
                          _futureResult = _apiService.getScanDetails(widget.scanId);
                        });
                      },
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
          );
        } else if (snapshot.hasData) {
          return ResultScreen(result: snapshot.data!);
        }
        return const SizedBox.shrink();
      },
    );
  }
}
