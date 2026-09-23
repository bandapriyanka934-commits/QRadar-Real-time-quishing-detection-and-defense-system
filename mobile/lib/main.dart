import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'core/theme/app_theme.dart';
import 'core/config/env_config.dart';
import 'services/scan_api_service.dart';
import 'features/home/home_screen.dart';
import 'features/scanner/scanner_screen.dart';
import 'features/history/history_screen.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'features/settings/settings_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: QRadarColors.primaryBackground,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  await EnvConfig.init();
  runApp(const QRadarApp());
}

class QRadarApp extends StatelessWidget {
  const QRadarApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QRadar — Quishing Detection & Defense',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const ResponsiveMainShell(),
    );
  }
}

class ResponsiveMainShell extends StatefulWidget {
  const ResponsiveMainShell({Key? key}) : super(key: key);

  @override
  State<ResponsiveMainShell> createState() => _ResponsiveMainShellState();
}

class _ResponsiveMainShellState extends State<ResponsiveMainShell> {
  int _currentIndex = 0;
  final ScanApiService _apiService = ScanApiService();
  bool _isBackendOnline = true;

  @override
  void initState() {
    super.initState();
    _checkHealth();
  }

  Future<void> _checkHealth() async {
    try {
      final res = await _apiService.checkHealth();
      if (mounted) {
        setState(() {
          _isBackendOnline = res['status'] == 'healthy';
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _isBackendOnline = false;
        });
      }
    }
  }

  void _onSelectTab(int index) {
    setState(() => _currentIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> pages = [
      HomeScreen(onNavigateTab: _onSelectTab),
      const ScannerScreen(),
      const HistoryScreen(),
      const DashboardScreen(),
      const SettingsScreen(),
    ];

    return LayoutBuilder(
      builder: (context, constraints) {
        // Desktop Layout (>= 900px)
        if (constraints.maxWidth >= 900) {
          return Scaffold(
            body: Row(
              children: [
                // Left Sidebar
                Container(
                  width: 260,
                  decoration: const BoxDecoration(
                    color: QRadarColors.sidebar,
                    border: Border(right: BorderSide(color: QRadarColors.border, width: 1)),
                  ),
                  child: Column(
                    children: [
                      const SizedBox(height: 24),
                      // Brand Header
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20),
                        child: Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: QRadarColors.surfaceElevated,
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(color: QRadarColors.border),
                              ),
                              child: const Icon(
                                Icons.shield_rounded,
                                color: QRadarColors.primaryBlue,
                                size: 22,
                              ),
                            ),
                            const SizedBox(width: 12),
                            const Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'QRadar',
                                  style: TextStyle(
                                    fontWeight: FontWeight.w900,
                                    fontSize: 19,
                                    letterSpacing: 0.5,
                                    color: QRadarColors.textPrimary,
                                  ),
                                ),
                                Text(
                                  'Quishing Defense v1.0',
                                  style: TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 18),
                      // Backend Status Indicator Badge
                      Container(
                        margin: const EdgeInsets.symmetric(horizontal: 16),
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                        decoration: BoxDecoration(
                          color: _isBackendOnline ? QRadarColors.safeBg : QRadarColors.maliciousBg,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: _isBackendOnline ? QRadarColors.safe.withOpacity(0.4) : QRadarColors.malicious.withOpacity(0.4),
                          ),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 8,
                              height: 8,
                              decoration: BoxDecoration(
                                color: _isBackendOnline ? QRadarColors.safe : QRadarColors.malicious,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              _isBackendOnline ? 'ONLINE • PROTECTED' : 'BACKEND OFFLINE',
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
                      const SizedBox(height: 16),
                      const Divider(color: QRadarColors.border, height: 1),
                      const SizedBox(height: 12),
                      // Navigation Items
                      _DesktopNavItem(
                        icon: Icons.home_filled,
                        label: 'Home Overview',
                        isSelected: _currentIndex == 0,
                        onTap: () => _onSelectTab(0),
                      ),
                      _DesktopNavItem(
                        icon: Icons.qr_code_scanner_rounded,
                        label: 'Live Scanner & Test',
                        isSelected: _currentIndex == 1,
                        onTap: () => _onSelectTab(1),
                      ),
                      _DesktopNavItem(
                        icon: Icons.history_rounded,
                        label: 'Scan History Logs',
                        isSelected: _currentIndex == 2,
                        onTap: () => _onSelectTab(2),
                      ),
                      _DesktopNavItem(
                        icon: Icons.insights_rounded,
                        label: 'Security Dashboard',
                        isSelected: _currentIndex == 3,
                        onTap: () => _onSelectTab(3),
                      ),
                      _DesktopNavItem(
                        icon: Icons.settings_rounded,
                        label: 'Settings & Info',
                        isSelected: _currentIndex == 4,
                        onTap: () => _onSelectTab(4),
                      ),
                      const Spacer(),
                      // Bottom Footer Info
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          children: [
                            const Divider(color: QRadarColors.border, height: 1),
                            const SizedBox(height: 12),
                            Text(
                              'Authoritative Defense Pipeline\nFastAPI Engine v1.0.0',
                              style: TextStyle(fontSize: 10, color: QRadarColors.textSecondary.withOpacity(0.8), height: 1.4),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                // Main Content View
                Expanded(
                  child: Container(
                    color: QRadarColors.primaryBackground,
                    child: IndexedStack(
                      index: _currentIndex,
                      children: pages,
                    ),
                  ),
                ),
              ],
            ),
          );
        }

        // Tablet Layout (600px - 899px)
        if (constraints.maxWidth >= 600) {
          return Scaffold(
            body: Row(
              children: [
                NavigationRail(
                  selectedIndex: _currentIndex,
                  onDestinationSelected: _onSelectTab,
                  backgroundColor: QRadarColors.sidebar,
                  selectedIconTheme: const IconThemeData(color: QRadarColors.primaryBlue),
                  unselectedIconTheme: const IconThemeData(color: QRadarColors.textSecondary),
                  selectedLabelTextStyle: const TextStyle(
                    color: QRadarColors.primaryBlue,
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                  ),
                  unselectedLabelTextStyle: const TextStyle(color: QRadarColors.textSecondary, fontSize: 11),
                  labelType: NavigationRailLabelType.all,
                  leading: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16.0),
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: QRadarColors.surfaceElevated,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: QRadarColors.border),
                      ),
                      child: const Icon(Icons.shield_rounded, color: QRadarColors.primaryBlue, size: 20),
                    ),
                  ),
                  destinations: const [
                    NavigationRailDestination(icon: Icon(Icons.home_filled), label: Text('Home')),
                    NavigationRailDestination(icon: Icon(Icons.qr_code_scanner_rounded), label: Text('Scan')),
                    NavigationRailDestination(icon: Icon(Icons.history_rounded), label: Text('Logs')),
                    NavigationRailDestination(icon: Icon(Icons.insights_rounded), label: Text('Analytics')),
                    NavigationRailDestination(icon: Icon(Icons.settings_rounded), label: Text('Settings')),
                  ],
                ),
                const VerticalDivider(width: 1, thickness: 1, color: QRadarColors.border),
                Expanded(
                  child: IndexedStack(
                    index: _currentIndex,
                    children: pages,
                  ),
                ),
              ],
            ),
          );
        }

        // Mobile Layout (< 600px)
        return Scaffold(
          body: IndexedStack(
            index: _currentIndex,
            children: pages,
          ),
          bottomNavigationBar: Container(
            decoration: const BoxDecoration(
              color: QRadarColors.sidebar,
              border: Border(top: BorderSide(color: QRadarColors.border, width: 1)),
            ),
            child: BottomNavigationBar(
              currentIndex: _currentIndex,
              onTap: _onSelectTab,
              type: BottomNavigationBarType.fixed,
              backgroundColor: QRadarColors.sidebar,
              selectedItemColor: QRadarColors.primaryBlue,
              unselectedItemColor: QRadarColors.textSecondary,
              selectedFontSize: 11,
              unselectedFontSize: 11,
              selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold),
              elevation: 0,
              items: const [
                BottomNavigationBarItem(
                  icon: Icon(Icons.home_filled),
                  activeIcon: Icon(Icons.home_filled, color: QRadarColors.primaryBlue),
                  label: 'Home',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.qr_code_scanner_rounded),
                  activeIcon: Icon(Icons.qr_code_scanner_rounded, color: QRadarColors.primaryBlue),
                  label: 'Scanner',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.history_rounded),
                  activeIcon: Icon(Icons.history_rounded, color: QRadarColors.primaryBlue),
                  label: 'Logs',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.insights_rounded),
                  activeIcon: Icon(Icons.insights_rounded, color: QRadarColors.primaryBlue),
                  label: 'Dashboard',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.settings_rounded),
                  activeIcon: Icon(Icons.settings_rounded, color: QRadarColors.primaryBlue),
                  label: 'Settings',
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _DesktopNavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _DesktopNavItem({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 3),
      child: Material(
        color: isSelected ? QRadarColors.surface : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(10),
          hoverColor: QRadarColors.surfaceElevated,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: isSelected ? QRadarColors.border : Colors.transparent,
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  icon,
                  size: 20,
                  color: isSelected ? QRadarColors.primaryBlue : QRadarColors.textSubtle,
                ),
                const SizedBox(width: 14),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                    color: isSelected ? QRadarColors.textPrimary : QRadarColors.textSubtle,
                  ),
                ),
                if (isSelected) ...[
                  const Spacer(),
                  Container(
                    width: 6,
                    height: 6,
                    decoration: const BoxDecoration(
                      color: QRadarColors.primaryBlue,
                      shape: BoxShape.circle,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
