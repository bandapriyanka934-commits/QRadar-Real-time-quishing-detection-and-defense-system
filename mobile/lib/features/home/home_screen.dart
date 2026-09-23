import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../services/scan_api_service.dart';
import '../../models/scan_result.dart';
import '../scanner/scanner_screen.dart';
import '../results/result_screen.dart';
import '../../widgets/offline_banner.dart';

class HomeScreen extends StatefulWidget {
  final Function(int index) onNavigateTab;

  const HomeScreen({Key? key, required this.onNavigateTab}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ScanApiService _apiService = ScanApiService();
  final TextEditingController _urlController = TextEditingController();
  
  bool _isConnecting = false;
  bool _isBackendOnline = true;
  String? _backendError;
  bool _isAnalyzing = false;

  @override
  void initState() {
    super.initState();
    _checkBackendStatus();
  }

  Future<void> _checkBackendStatus() async {
    setState(() => _isConnecting = true);
    try {
      final res = await _apiService.checkHealth();
      if (mounted) {
        setState(() {
          _isBackendOnline = res['status'] == 'healthy';
          _backendError = null;
          _isConnecting = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isBackendOnline = false;
          _backendError = e.toString();
          _isConnecting = false;
        });
      }
    }
  }

  Future<void> _analyzeDirectUrl(String url) async {
    if (url.trim().isEmpty) return;
    setState(() => _isAnalyzing = true);
    try {
      final result = await _apiService.scanUrl(url.trim(), source: 'manual');
      if (!mounted) return;
      setState(() => _isAnalyzing = false);
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isAnalyzing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Scan evaluation error: $e'),
          backgroundColor: QRadarColors.malicious,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: QRadarColors.primaryBackground,
      appBar: AppBar(
        backgroundColor: QRadarColors.surface,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                color: QRadarColors.surfaceElevated,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: QRadarColors.border),
              ),
              child: const Icon(Icons.shield_rounded, color: QRadarColors.primaryBlue, size: 18),
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'QRadar',
                  style: TextStyle(
                    fontWeight: FontWeight.w900,
                    fontSize: 18,
                    letterSpacing: 0.3,
                    color: QRadarColors.textPrimary,
                  ),
                ),
                Text(
                  'Quishing Detection & Defense System',
                  style: TextStyle(fontSize: 10, color: QRadarColors.textSecondary, fontWeight: FontWeight.normal),
                ),
              ],
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _isBackendOnline ? QRadarColors.safeBg : QRadarColors.maliciousBg,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: _isBackendOnline ? QRadarColors.safe.withOpacity(0.4) : QRadarColors.malicious.withOpacity(0.4),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 7,
                  height: 7,
                  decoration: BoxDecoration(
                    color: _isBackendOnline ? QRadarColors.safe : QRadarColors.malicious,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  _isBackendOnline ? 'PROTECTED' : 'OFFLINE',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.5,
                    color: _isBackendOnline ? QRadarColors.safe : QRadarColors.malicious,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _checkBackendStatus,
        color: QRadarColors.primaryBlue,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(22),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (!_isBackendOnline)
                OfflineBanner(
                  onRetry: _checkBackendStatus,
                  errorMessage: _backendError,
                ),

              // Hero Panel Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: QRadarColors.surface,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: QRadarColors.border, width: 1.2),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                          decoration: BoxDecoration(
                            color: QRadarColors.surfaceElevated,
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: QRadarColors.border),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.lock_outline_rounded, size: 12, color: QRadarColors.primaryBlue),
                              SizedBox(width: 6),
                              Text(
                                'DEFENSE-IN-DEPTH SECURITY LAYER',
                                style: TextStyle(
                                  color: QRadarColors.primaryBlue,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.8,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Spacer(),
                        const Icon(Icons.verified_user_rounded, color: QRadarColors.primaryBlue, size: 20),
                      ],
                    ),
                    const SizedBox(height: 14),
                    const Text(
                      'Scan a QR code before you trust the destination.',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        color: QRadarColors.textPrimary,
                        letterSpacing: -0.3,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      'QRadar intercepts physical and digital QR codes, evaluating destinations across 12+ deterministic heuristics, Random Forest Machine Learning, and Threat Intelligence to prevent quishing attacks and credential theft.',
                      style: TextStyle(
                        fontSize: 13,
                        color: QRadarColors.textSecondary,
                        height: 1.45,
                      ),
                    ),
                    const SizedBox(height: 20),
                    Row(
                      children: [
                        ElevatedButton.icon(
                          icon: const Icon(Icons.qr_code_scanner_rounded, size: 18),
                          label: const Text('Open Live Scanner'),
                          onPressed: () => widget.onNavigateTab(1),
                        ),
                        const SizedBox(width: 12),
                        OutlinedButton.icon(
                          icon: const Icon(Icons.insights_rounded, size: 18, color: QRadarColors.primaryBlue),
                          label: const Text('View Analytics'),
                          onPressed: () => widget.onNavigateTab(3),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Primary Scanning Actions (Slate Cards with Clean Blue Accents)
              const Text(
                'QUICK SCAN MODES',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.0,
                  color: QRadarColors.textSecondary,
                ),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: _ScanActionCard(
                      icon: Icons.camera_alt_rounded,
                      title: 'Live Camera Scanner',
                      subtitle: 'Continuous optical viewfinder',
                      onTap: () => widget.onNavigateTab(1),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: _ScanActionCard(
                      icon: Icons.photo_library_rounded,
                      title: 'Scan from Image',
                      subtitle: 'PNG, JPG, WebP Multi-QR',
                      onTap: () => widget.onNavigateTab(1),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 26),

              // Direct Security Analyzer & Safe Demo Test Cases
              const Text(
                'QUICK URL TESTBENCH & DEMO CASES',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.0,
                  color: QRadarColors.textSecondary,
                ),
              ),
              const SizedBox(height: 12),

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
                    TextField(
                      controller: _urlController,
                      decoration: InputDecoration(
                        hintText: 'Enter URL or raw QR text (e.g. https://www.google.com)...',
                        prefixIcon: const Icon(Icons.link_rounded, color: QRadarColors.primaryBlue),
                        suffixIcon: IconButton(
                          icon: _isAnalyzing
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: QRadarColors.primaryBlue),
                                )
                              : const Icon(Icons.arrow_forward_rounded, color: QRadarColors.primaryBlue),
                          onPressed: _isAnalyzing ? null : () => _analyzeDirectUrl(_urlController.text),
                        ),
                      ),
                      onSubmitted: _analyzeDirectUrl,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Security Testbench Examples:',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: QRadarColors.textSecondary),
                    ),
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _DemoChip(
                          label: 'Safe: Google Search',
                          statusColor: QRadarColors.safe,
                          onTap: () {
                            _urlController.text = 'https://www.google.com/search?q=cybersecurity';
                            _analyzeDirectUrl(_urlController.text);
                          },
                        ),
                        _DemoChip(
                          label: 'Typosquat: PayPa1 Lookalike',
                          statusColor: QRadarColors.suspicious,
                          onTap: () {
                            _urlController.text = 'http://paypa1-account-update.xyz/login.php';
                            _analyzeDirectUrl(_urlController.text);
                          },
                        ),
                        _DemoChip(
                          label: 'Rogue IP Host (:8080)',
                          statusColor: QRadarColors.malicious,
                          onTap: () {
                            _urlController.text = 'http://192.168.1.105:8080/secure/paypal_login.htm';
                            _analyzeDirectUrl(_urlController.text);
                          },
                        ),
                        _DemoChip(
                          label: 'Userinfo @ Evasion',
                          statusColor: QRadarColors.malicious,
                          onTap: () {
                            _urlController.text = 'https://paypal.com@evil-phishing-gate.ru/login';
                            _analyzeDirectUrl(_urlController.text);
                          },
                        ),
                        _DemoChip(
                          label: 'Dangerous Scheme (javascript:)',
                          statusColor: QRadarColors.block,
                          onTap: () {
                            _urlController.text = 'javascript:alert("Quishing Execution Blocked")';
                            _analyzeDirectUrl(_urlController.text);
                          },
                        ),
                        _DemoChip(
                          label: 'Shortener (bit.ly)',
                          statusColor: QRadarColors.suspicious,
                          onTap: () {
                            _urlController.text = 'http://bit.ly/3xSampleShortener';
                            _analyzeDirectUrl(_urlController.text);
                          },
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Navigation shortcuts
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      icon: const Icon(Icons.history_rounded, color: QRadarColors.primaryBlue, size: 18),
                      label: const Text('Scan Logs'),
                      onPressed: () => widget.onNavigateTab(2),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      icon: const Icon(Icons.insights_rounded, color: QRadarColors.accentCyan, size: 18),
                      label: const Text('Security Analytics'),
                      onPressed: () => widget.onNavigateTab(3),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ScanActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _ScanActionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      hoverColor: QRadarColors.surfaceElevated,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: QRadarColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: QRadarColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: QRadarColors.surfaceElevated,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: QRadarColors.border),
              ),
              child: Icon(icon, color: QRadarColors.primaryBlue, size: 22),
            ),
            const SizedBox(height: 14),
            Text(
              title,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w800,
                color: QRadarColors.textPrimary,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 12,
                color: QRadarColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DemoChip extends StatelessWidget {
  final String label;
  final Color statusColor;
  final VoidCallback onTap;

  const _DemoChip({
    required this.label,
    required this.statusColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        decoration: BoxDecoration(
          color: QRadarColors.surfaceElevated,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: QRadarColors.border),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 7,
              height: 7,
              decoration: BoxDecoration(
                color: statusColor,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 7),
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: QRadarColors.textSubtle,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
