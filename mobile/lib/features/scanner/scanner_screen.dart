import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../../core/theme/app_theme.dart';
import '../../services/scan_api_service.dart';
import '../../models/scan_result.dart';
import '../../models/multi_qr_response.dart';
import '../../widgets/qr_viewfinder.dart';
import '../../widgets/multi_qr_dialog.dart';
import '../results/result_screen.dart';

enum ScannerTabMode { camera, imageUpload, testbench }

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({Key? key}) : super(key: key);

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> with WidgetsBindingObserver {
  final ScanApiService _apiService = ScanApiService();
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _testUrlController = TextEditingController();

  late MobileScannerController _cameraController;
  ScannerTabMode _activeMode = ScannerTabMode.camera;

  bool _isAnalyzing = false;
  bool _isTorchOn = false;
  String? _lastScannedContent;
  DateTime? _lastScanTime;
  String? _statusMessage;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initScanner();
  }

  void _initScanner() {
    _cameraController = MobileScannerController(
      detectionSpeed: DetectionSpeed.noDuplicates,
      facing: CameraFacing.back,
      torchEnabled: false,
      returnImage: false,
    );
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _cameraController.start();
    } else if (state == AppLifecycleState.inactive || state == AppLifecycleState.paused) {
      _cameraController.stop();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _cameraController.dispose();
    _testUrlController.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_isAnalyzing) return;
    final barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;

    final rawValue = barcodes.first.rawValue;
    if (rawValue == null || rawValue.trim().isEmpty) return;

    // Debounce duplicate scans within 4 seconds
    final now = DateTime.now();
    if (_lastScannedContent == rawValue &&
        _lastScanTime != null &&
        now.difference(_lastScanTime!) < const Duration(seconds: 4)) {
      return;
    }

    _lastScannedContent = rawValue;
    _lastScanTime = now;

    // Pause camera scanning during authoritative backend evaluation
    _cameraController.stop();
    _processScannedPayload(rawValue, source: kIsWeb ? 'webcam' : 'camera');
  }

  Future<void> _processScannedPayload(String content, {required String source}) async {
    setState(() {
      _isAnalyzing = true;
      _statusMessage = 'Transmitting to QRadar Security Engine...';
    });

    try {
      final result = await _apiService.scanUrl(content, source: source);
      if (!mounted) return;

      setState(() {
        _isAnalyzing = false;
        _statusMessage = null;
      });

      await Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
      );

      // Resume camera after returning if camera tab is active
      if (mounted && _activeMode == ScannerTabMode.camera) {
        _cameraController.start();
      }
      _lastScannedContent = null;
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isAnalyzing = false;
        _statusMessage = null;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Security evaluation failed: $e'),
          backgroundColor: QRadarColors.malicious,
          duration: const Duration(seconds: 4),
        ),
      );

      if (_activeMode == ScannerTabMode.camera) {
        _cameraController.start();
      }
      _lastScannedContent = null;
    }
  }

  Future<void> _pickImageFromGallery() async {
    if (_isAnalyzing) return;

    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
      if (image == null) return;

      setState(() {
        _isAnalyzing = true;
        _statusMessage = 'Uploading to backend for OpenCV QR decoding...';
      });

      final Uint8List bytes = await image.readAsBytes();
      final response = await _apiService.scanImage(bytes, image.name);

      if (!mounted) return;
      setState(() {
        _isAnalyzing = false;
        _statusMessage = null;
      });

      if (response is SecurityResult) {
        await Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => ResultScreen(result: response)),
        );
      } else if (response is MultiQRDecodeResponse) {
        _showMultiQRDialog(response, bytes, image.name);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isAnalyzing = false;
        _statusMessage = null;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Image scan failed: $e'),
          backgroundColor: QRadarColors.malicious,
        ),
      );
    }
  }

  void _showMultiQRDialog(MultiQRDecodeResponse multiResponse, Uint8List imageBytes, String filename) {
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => MultiQRSelectionDialog(
        qrCodes: multiResponse.qrCodes,
        onSelect: (index, content) async {
          setState(() {
            _isAnalyzing = true;
            _statusMessage = 'Evaluating selected QR #${index + 1}...';
          });
          try {
            final result = await _apiService.scanImage(
              imageBytes,
              filename,
              selectedIndex: index,
            );
            if (!mounted) return;
            setState(() {
              _isAnalyzing = false;
              _statusMessage = null;
            });
            if (result is SecurityResult) {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
              );
            }
          } catch (err) {
            if (!mounted) return;
            setState(() {
              _isAnalyzing = false;
              _statusMessage = null;
            });
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Error: $err'), backgroundColor: QRadarColors.malicious),
            );
          }
        },
      ),
    );
  }

  void _toggleTorch() {
    setState(() => _isTorchOn = !_isTorchOn);
    _cameraController.toggleTorch();
  }

  void _switchCamera() {
    _cameraController.switchCamera();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: QRadarColors.primaryBackground,
      appBar: AppBar(
        title: Text(
          kIsWeb ? 'Live Webcam QR Scanner' : 'QR Scanner',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(50),
          child: Container(
            color: QRadarColors.surface,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            child: Row(
              children: [
                _ModeButton(
                  icon: Icons.videocam_rounded,
                  label: kIsWeb ? 'Webcam' : 'Camera',
                  isActive: _activeMode == ScannerTabMode.camera,
                  onTap: () {
                    setState(() => _activeMode = ScannerTabMode.camera);
                    _cameraController.start();
                  },
                ),
                const SizedBox(width: 8),
                _ModeButton(
                  icon: Icons.photo_library_rounded,
                  label: 'Image Upload',
                  isActive: _activeMode == ScannerTabMode.imageUpload,
                  onTap: () {
                    setState(() => _activeMode = ScannerTabMode.imageUpload);
                    _cameraController.stop();
                  },
                ),
                const SizedBox(width: 8),
                _ModeButton(
                  icon: Icons.science_rounded,
                  label: 'Testbench',
                  isActive: _activeMode == ScannerTabMode.testbench,
                  onTap: () {
                    setState(() => _activeMode = ScannerTabMode.testbench);
                    _cameraController.stop();
                  },
                ),
              ],
            ),
          ),
        ),
      ),
      body: Stack(
        children: [
          IndexedStack(
            index: _activeMode == ScannerTabMode.camera
                ? 0
                : (_activeMode == ScannerTabMode.imageUpload ? 1 : 2),
            children: [
              _buildCameraView(),
              _buildImageUploadView(),
              _buildTestbenchView(),
            ],
          ),

          // Loading & Analysis Progress Overlay
          if (_isAnalyzing)
            Container(
              color: QRadarColors.primaryBackground.withOpacity(0.85),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 28),
                  decoration: BoxDecoration(
                    color: QRadarColors.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: QRadarColors.primaryBlue.withOpacity(0.4), width: 1.2),
                    boxShadow: [
                      BoxShadow(
                        color: QRadarColors.primaryBlue.withOpacity(0.12),
                        blurRadius: 20,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const SizedBox(
                        width: 44,
                        height: 44,
                        child: CircularProgressIndicator(
                          strokeWidth: 3.0,
                          valueColor: AlwaysStoppedAnimation<Color>(QRadarColors.primaryBlue),
                        ),
                      ),
                      const SizedBox(height: 18),
                      const Text(
                        'AUTHORITATIVE SECURITY SCAN',
                        style: TextStyle(
                          color: QRadarColors.primaryBlue,
                          fontSize: 11,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1.0,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        _statusMessage ?? 'Evaluating Heuristics, ML, & Threat Feeds...',
                        style: const TextStyle(
                          color: QRadarColors.textPrimary,
                          fontSize: 13,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildCameraView() {
    return Stack(
      children: [
        MobileScanner(
          controller: _cameraController,
          onDetect: _onDetect,
          errorBuilder: (context, error, child) {
            return Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 480),
                child: Padding(
                  padding: const EdgeInsets.all(28.0),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.videocam_off_rounded, color: QRadarColors.malicious, size: 48),
                      const SizedBox(height: 16),
                      const Text(
                        'Camera Stream Unavailable',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: QRadarColors.textPrimary),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        kIsWeb
                            ? 'Please allow camera permission in your browser or use Image Upload mode.'
                            : 'Camera permission denied or device busy. Please verify permissions.',
                        style: const TextStyle(fontSize: 13, color: QRadarColors.textSecondary, height: 1.4),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 18),
                      ElevatedButton.icon(
                        icon: const Icon(Icons.photo_library_rounded, size: 18),
                        label: const Text('Switch to Image Upload'),
                        onPressed: () => setState(() => _activeMode = ScannerTabMode.imageUpload),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),

        // Animated Viewfinder
        QRViewfinderOverlay(
          scanAreaSize: 260,
          onToggleTorch: _toggleTorch,
          onSwitchCamera: _switchCamera,
          isTorchOn: _isTorchOn,
        ),
      ],
    );
  }

  Widget _buildImageUploadView() {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 680),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(32),
                decoration: BoxDecoration(
                  color: QRadarColors.surface,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: QRadarColors.border, width: 1.2),
                ),
                child: Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: QRadarColors.surfaceElevated,
                        shape: BoxShape.circle,
                        border: Border.all(color: QRadarColors.border),
                      ),
                      child: const Icon(Icons.photo_library_rounded, color: QRadarColors.primaryBlue, size: 44),
                    ),
                    const SizedBox(height: 18),
                    const Text(
                      'Upload QR Code Image or Screenshot',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: QRadarColors.textPrimary),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Select PNG, JPG, or WebP files. QRadar decodes single or multiple QR codes via OpenCV and evaluates each payload.',
                      style: TextStyle(fontSize: 13, color: QRadarColors.textSecondary, height: 1.4),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 22),
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 15),
                      ),
                      icon: const Icon(Icons.file_upload_rounded, size: 18),
                      label: const Text('Choose QR Image File'),
                      onPressed: _isAnalyzing ? null : _pickImageFromGallery,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTestbenchView() {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 720),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: QRadarColors.surface,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: QRadarColors.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.science_rounded, color: QRadarColors.primaryBlue, size: 22),
                    SizedBox(width: 10),
                    Text(
                      'DEVELOPER SECURITY TESTBENCH',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                        color: QRadarColors.textPrimary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: _testUrlController,
                  decoration: InputDecoration(
                    hintText: 'Enter URL or QR payload...',
                    prefixIcon: const Icon(Icons.link_rounded, color: QRadarColors.primaryBlue),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.send_rounded, color: QRadarColors.primaryBlue),
                      onPressed: _isAnalyzing
                          ? null
                          : () => _processScannedPayload(_testUrlController.text, source: 'manual'),
                    ),
                  ),
                  onSubmitted: (val) => _processScannedPayload(val, source: 'manual'),
                ),
                const SizedBox(height: 18),
                const Text(
                  'Quick Demonstration Fixtures:',
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
                        _testUrlController.text = 'https://www.google.com/search?q=cybersecurity+research';
                        _processScannedPayload(_testUrlController.text, source: 'manual');
                      },
                    ),
                    _DemoChip(
                      label: 'Phishing: PayPa1 Lookalike',
                      statusColor: QRadarColors.malicious,
                      onTap: () {
                        _testUrlController.text = 'http://paypa1-account-verification.xyz/login.php';
                        _processScannedPayload(_testUrlController.text, source: 'manual');
                      },
                    ),
                    _DemoChip(
                      label: 'Rogue IP Host (:8080)',
                      statusColor: QRadarColors.malicious,
                      onTap: () {
                        _testUrlController.text = 'http://192.168.1.105:8080/secure/paypal_login.htm';
                        _processScannedPayload(_testUrlController.text, source: 'manual');
                      },
                    ),
                    _DemoChip(
                      label: 'Userinfo @ Evasion',
                      statusColor: QRadarColors.malicious,
                      onTap: () {
                        _testUrlController.text = 'https://paypal.com@evil-phishing-gate.ru/login';
                        _processScannedPayload(_testUrlController.text, source: 'manual');
                      },
                    ),
                    _DemoChip(
                      label: 'Dangerous Scheme (javascript:)',
                      statusColor: QRadarColors.block,
                      onTap: () {
                        _testUrlController.text = 'javascript:alert("Quishing Attack Blocked")';
                        _processScannedPayload(_testUrlController.text, source: 'manual');
                      },
                    ),
                    _DemoChip(
                      label: 'Shortener (bit.ly)',
                      statusColor: QRadarColors.suspicious,
                      onTap: () {
                        _testUrlController.text = 'http://bit.ly/3xSampleShortener';
                        _processScannedPayload(_testUrlController.text, source: 'manual');
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ModeButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _ModeButton({
    required this.icon,
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isActive ? QRadarColors.surfaceElevated : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isActive ? QRadarColors.primaryBlue : QRadarColors.border,
              width: isActive ? 1.2 : 1.0,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 15, color: isActive ? QRadarColors.primaryBlue : QRadarColors.textSecondary),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: isActive ? FontWeight.w800 : FontWeight.w600,
                  color: isActive ? QRadarColors.primaryBlue : QRadarColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DemoChip extends StatelessWidget {
  final String label;
  final Color statusColor;
  final VoidCallback onTap;

  const _DemoChip({required this.label, required this.statusColor, required this.onTap});

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
              decoration: BoxDecoration(color: statusColor, shape: BoxShape.circle),
            ),
            const SizedBox(width: 7),
            Text(
              label,
              style: const TextStyle(
                fontSize: 11,
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
