import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class QRViewfinderOverlay extends StatefulWidget {
  final double scanAreaSize;
  final VoidCallback? onToggleTorch;
  final VoidCallback? onSwitchCamera;
  final bool isTorchOn;

  const QRViewfinderOverlay({
    Key? key,
    this.scanAreaSize = 260,
    this.onToggleTorch,
    this.onSwitchCamera,
    this.isTorchOn = false,
  }) : super(key: key);

  @override
  State<QRViewfinderOverlay> createState() => _QRViewfinderOverlayState();
}

class _QRViewfinderOverlayState extends State<QRViewfinderOverlay> with SingleTickerProviderStateMixin {
  late AnimationController _laserController;
  late Animation<double> _laserAnimation;

  @override
  void initState() {
    super.initState();
    _laserController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    )..repeat(reverse: true);

    _laserAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _laserController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _laserController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Darkened background cutout
        ColorFiltered(
          colorFilter: ColorFilter.mode(
            const Color(0xFF020617).withOpacity(0.72),
            BlendMode.srcOut,
          ),
          child: Stack(
            children: [
              Container(
                decoration: const BoxDecoration(
                  color: Colors.transparent,
                  backgroundBlendMode: BlendMode.dstOut,
                ),
              ),
              Center(
                child: Container(
                  width: widget.scanAreaSize,
                  height: widget.scanAreaSize,
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
              ),
            ],
          ),
        ),

        // Corner brackets & Animated Laser
        Center(
          child: SizedBox(
            width: widget.scanAreaSize,
            height: widget.scanAreaSize,
            child: Stack(
              children: [
                // Corner Borders (Electric Blue)
                CustomPaint(
                  size: Size(widget.scanAreaSize, widget.scanAreaSize),
                  painter: _CornerBracketPainter(),
                ),

                // Animated Laser Line (Cyan Accent)
                AnimatedBuilder(
                  animation: _laserAnimation,
                  builder: (context, child) {
                    final topOffset = _laserAnimation.value * (widget.scanAreaSize - 24) + 12;
                    return Positioned(
                      top: topOffset,
                      left: 14,
                      right: 14,
                      child: Container(
                        height: 2.0,
                        decoration: BoxDecoration(
                          color: QRadarColors.accentCyan,
                          boxShadow: [
                            BoxShadow(
                              color: QRadarColors.accentCyan.withOpacity(0.6),
                              blurRadius: 8,
                              spreadRadius: 1,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),

        // Top guidance text
        Positioned(
          top: 36,
          left: 20,
          right: 20,
          child: Center(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: QRadarColors.surface.withOpacity(0.92),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: QRadarColors.border),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.qr_code_scanner_rounded, color: QRadarColors.primaryBlue, size: 16),
                  SizedBox(width: 8),
                  Text(
                    'Align QR code within optical frame',
                    style: TextStyle(
                      color: QRadarColors.textPrimary,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),

        // Bottom Controls (Torch & Switch)
        Positioned(
          bottom: 30,
          left: 0,
          right: 0,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (widget.onToggleTorch != null)
                _CircleIconButton(
                  icon: widget.isTorchOn ? Icons.flash_on_rounded : Icons.flash_off_rounded,
                  label: 'Torch',
                  isActive: widget.isTorchOn,
                  onPressed: widget.onToggleTorch!,
                ),
              const SizedBox(width: 24),
              if (widget.onSwitchCamera != null)
                _CircleIconButton(
                  icon: Icons.flip_camera_ios_rounded,
                  label: 'Flip',
                  onPressed: widget.onSwitchCamera!,
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class _CircleIconButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onPressed;
  final bool isActive;

  const _CircleIconButton({
    required this.icon,
    required this.label,
    required this.onPressed,
    this.isActive = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(26),
          child: Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: isActive ? QRadarColors.primaryBlue : QRadarColors.surface,
              shape: BoxShape.circle,
              border: Border.all(
                color: isActive ? QRadarColors.primaryBlue : QRadarColors.border,
                width: 1.2,
              ),
            ),
            child: Icon(
              icon,
              color: isActive ? QRadarColors.primaryBackground : QRadarColors.textPrimary,
              size: 22,
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          label,
          style: const TextStyle(
            color: QRadarColors.textSecondary,
            fontSize: 11,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}

class _CornerBracketPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    const strokeWidth = 3.5;
    const cornerLength = 26.0;
    const radius = 14.0;

    final paint = Paint()
      ..color = QRadarColors.primaryBlue
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final w = size.width;
    final h = size.height;

    // Top-Left
    final pathTL = Path()
      ..moveTo(0, cornerLength)
      ..lineTo(0, radius)
      ..arcToPoint(const Offset(radius, 0), radius: const Radius.circular(radius))
      ..lineTo(cornerLength, 0);
    canvas.drawPath(pathTL, paint);

    // Top-Right
    final pathTR = Path()
      ..moveTo(w - cornerLength, 0)
      ..lineTo(w - radius, 0)
      ..arcToPoint(Offset(w, radius), radius: const Radius.circular(radius))
      ..lineTo(w, cornerLength);
    canvas.drawPath(pathTR, paint);

    // Bottom-Left
    final pathBL = Path()
      ..moveTo(0, h - cornerLength)
      ..lineTo(0, h - radius)
      ..arcToPoint(Offset(radius, h), radius: const Radius.circular(radius))
      ..lineTo(cornerLength, h);
    canvas.drawPath(pathBL, paint);

    // Bottom-Right
    final pathBR = Path()
      ..moveTo(w - cornerLength, h)
      ..lineTo(w - radius, h)
      ..arcToPoint(Offset(w, h - radius), radius: const Radius.circular(radius))
      ..lineTo(w, h - cornerLength);
    canvas.drawPath(pathBR, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
