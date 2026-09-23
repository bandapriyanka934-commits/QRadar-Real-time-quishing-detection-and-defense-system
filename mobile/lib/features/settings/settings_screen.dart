import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/config/env_config.dart';
import '../../services/scan_api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final ScanApiService _apiService = ScanApiService();
  final TextEditingController _urlController = TextEditingController();

  bool _isTesting = false;
  String? _testResult;
  bool _testSuccess = false;

  @override
  void initState() {
    super.initState();
    _urlController.text = EnvConfig.baseUrl;
  }

  Future<void> _saveAndTest() async {
    final inputUrl = _urlController.text.trim();
    if (inputUrl.isEmpty) return;

    await EnvConfig.setBaseUrl(inputUrl);

    setState(() {
      _isTesting = true;
      _testResult = 'Pinging $inputUrl/health ...';
      _testSuccess = false;
    });

    try {
      final res = await _apiService.checkHealth();
      if (mounted) {
        setState(() {
          _isTesting = false;
          _testSuccess = true;
          _testResult = 'Connected Successfully!\nService: ${res['service']}\nML Phishing Model: ${res['ml_model_available'] == true ? "ACTIVE (Online)" : "DEGRADED (Fallback)"}';
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isTesting = false;
          _testSuccess = false;
          _testResult = 'Connection Failed: $e';
        });
      }
    }
  }

  void _applyPreset(String url) {
    setState(() {
      _urlController.text = url;
    });
    _saveAndTest();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: QRadarColors.primaryBackground,
      appBar: AppBar(
        title: const Text('Settings & Info'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Section 1: Backend Connection
            const Text(
              'FASTAPI BACKEND NETWORK CONFIG',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 1.0,
                color: QRadarColors.textSecondary,
              ),
            ),
            const SizedBox(height: 12),

            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: QRadarColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: QRadarColors.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'API Base URL:',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: QRadarColors.textPrimary),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _urlController,
                    decoration: InputDecoration(
                      hintText: 'http://127.0.0.1:8000',
                      prefixIcon: const Icon(Icons.dns_rounded, color: QRadarColors.primaryBlue),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.save_rounded, color: QRadarColors.primaryBlue),
                        onPressed: _saveAndTest,
                        tooltip: 'Save and Test',
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),

                  const Text(
                    'Quick Environment Presets:',
                    style: TextStyle(fontSize: 11, color: QRadarColors.textSecondary, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _PresetChip(
                        label: 'Android Emulator (10.0.2.2)',
                        onTap: () => _applyPreset('http://10.0.2.2:8000'),
                      ),
                      _PresetChip(
                        label: 'Localhost (127.0.0.1)',
                        onTap: () => _applyPreset('http://127.0.0.1:8000'),
                      ),
                      _PresetChip(
                        label: 'LAN Host (192.168.1.100)',
                        onTap: () => _applyPreset('http://192.168.1.100:8000'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      icon: _isTesting
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2, color: QRadarColors.primaryBackground),
                            )
                          : const Icon(Icons.network_check_rounded),
                      label: Text(_isTesting ? 'Testing Connectivity...' : 'Ping & Test Backend Connection'),
                      onPressed: _isTesting ? null : _saveAndTest,
                    ),
                  ),

                  if (_testResult != null) ...[
                    const SizedBox(height: 14),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: _testSuccess ? QRadarColors.safeBg : QRadarColors.maliciousBg,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: _testSuccess ? QRadarColors.safe.withOpacity(0.4) : QRadarColors.malicious.withOpacity(0.4),
                        ),
                      ),
                      child: Text(
                        _testResult!,
                        style: TextStyle(
                          fontSize: 12,
                          color: _testSuccess ? QRadarColors.safe : QRadarColors.malicious,
                          fontWeight: FontWeight.w600,
                          height: 1.3,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(height: 26),

            // Section 2: Security Architecture & Scoring Policy
            const Text(
              'SECURITY SCORING POLICY REFERENCE',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 1.0,
                color: QRadarColors.textSecondary,
              ),
            ),
            const SizedBox(height: 12),

            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: QRadarColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: QRadarColors.border),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _PolicyRow(
                    range: '0 – 29',
                    verdict: 'SAFE',
                    action: 'ALLOW',
                    color: QRadarColors.safe,
                    desc: 'Clean heuristic signals, low ML probability, and verified reputable domain status.',
                  ),
                  Divider(color: QRadarColors.border, height: 20),
                  _PolicyRow(
                    range: '30 – 69',
                    verdict: 'SUSPICIOUS',
                    action: 'WARN',
                    color: QRadarColors.suspicious,
                    desc: 'Anomalous structure, shortened URLs, or moderate ML probability requiring explicit user confirmation.',
                  ),
                  Divider(color: QRadarColors.border, height: 20),
                  _PolicyRow(
                    range: '70 – 100',
                    verdict: 'MALICIOUS',
                    action: 'BLOCK',
                    color: QRadarColors.malicious,
                    desc: 'Dangerous execution schemes, typosquatting homoglyphs, rogue IP hosts, high ML probability, or threat feed matches.',
                  ),
                ],
              ),
            ),

            const SizedBox(height: 26),

            // Section 3: About QRadar
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: QRadarColors.surfaceElevated,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: QRadarColors.border),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'QRadar Quishing Defense Platform v1.0.0',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: QRadarColors.textPrimary),
                  ),
                  SizedBox(height: 6),
                  Text(
                    'Authoritative defense-in-depth cybersecurity suite featuring OpenCV multi-QR decoding, 12+ deterministic heuristic indicators, Levenshtein distance typosquatting, Random Forest ML classification, and threat intelligence synthesis.',
                    style: TextStyle(fontSize: 12, color: QRadarColors.textSecondary, height: 1.45),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }
}

class _PresetChip extends StatelessWidget {
  final String label;
  final VoidCallback onTap;

  const _PresetChip({required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: QRadarColors.surfaceElevated,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: QRadarColors.border),
        ),
        child: Text(
          label,
          style: const TextStyle(fontSize: 11, color: QRadarColors.textSubtle, fontWeight: FontWeight.w500),
        ),
      ),
    );
  }
}

class _PolicyRow extends StatelessWidget {
  final String range;
  final String verdict;
  final String action;
  final Color color;
  final String desc;

  const _PolicyRow({
    required this.range,
    required this.verdict,
    required this.action,
    required this.color,
    required this.desc,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: color.withOpacity(0.12),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: color.withOpacity(0.4)),
              ),
              child: Text(
                '$range pts',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '$verdict • $action',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: color),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          desc,
          style: const TextStyle(fontSize: 12, color: QRadarColors.textSecondary, height: 1.35),
        ),
      ],
    );
  }
}
