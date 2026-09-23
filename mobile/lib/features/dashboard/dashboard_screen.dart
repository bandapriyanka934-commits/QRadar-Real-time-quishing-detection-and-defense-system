import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../core/theme/app_theme.dart';
import '../../services/scan_api_service.dart';
import '../../models/dashboard_stats.dart';

class DashboardScreen extends StatefulWidget {
  final VoidCallback? onNavigateToScan;

  const DashboardScreen({Key? key, this.onNavigateToScan}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ScanApiService _apiService = ScanApiService();
  DashboardStats? _stats;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final stats = await _apiService.getDashboard();
      if (mounted) {
        setState(() {
          _stats = stats;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: QRadarColors.primaryBackground,
      appBar: AppBar(
        title: const Text('Security Analytics Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: QRadarColors.textSecondary),
            tooltip: 'Refresh Metrics',
            onPressed: _loadDashboardData,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboardData,
        color: QRadarColors.primaryBlue,
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: QRadarColors.primaryBlue),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.wifi_off_rounded, color: QRadarColors.malicious, size: 48),
              const SizedBox(height: 16),
              Text(
                'Dashboard Connection Error: $_errorMessage',
                style: const TextStyle(color: QRadarColors.textSecondary),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton(onPressed: _loadDashboardData, child: const Text('Retry Connection')),
            ],
          ),
        ),
      );
    }

    final stats = _stats!;

    // Empty state when no scans recorded
    if (stats.totalScans == 0) {
      return Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: Padding(
            padding: const EdgeInsets.all(32.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.all(22),
                  decoration: BoxDecoration(
                    color: QRadarColors.surfaceElevated,
                    shape: BoxShape.circle,
                    border: Border.all(color: QRadarColors.border),
                  ),
                  child: const Icon(Icons.insights_rounded, size: 48, color: QRadarColors.primaryBlue),
                ),
                const SizedBox(height: 20),
                const Text(
                  'No Security Activity Yet',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: QRadarColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Scan a QR code or evaluate a destination URL to build defensive cybersecurity telemetry.',
                  style: TextStyle(fontSize: 13, color: QRadarColors.textSecondary, height: 1.4),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 900;

        return SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Metric Summary Cards (4 in a row on wide desktop, 2x2 on mobile)
              if (isWide)
                Row(
                  children: [
                    Expanded(
                      child: _MetricCard(
                        title: 'TOTAL SCANS',
                        value: '${stats.totalScans}',
                        icon: Icons.qr_code_scanner_rounded,
                        color: QRadarColors.primaryBlue,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: _MetricCard(
                        title: 'BLOCKED THREATS',
                        value: '${stats.blockedThreatsCount}',
                        icon: Icons.gpp_bad_rounded,
                        color: QRadarColors.malicious,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: _MetricCard(
                        title: 'SAFE TARGETS',
                        value: '${stats.verdictCounts.safe}',
                        icon: Icons.check_circle_rounded,
                        color: QRadarColors.safe,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: _MetricCard(
                        title: 'SUSPICIOUS WARNS',
                        value: '${stats.verdictCounts.suspicious}',
                        icon: Icons.warning_rounded,
                        color: QRadarColors.suspicious,
                      ),
                    ),
                  ],
                )
              else
                Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: _MetricCard(
                            title: 'TOTAL SCANS',
                            value: '${stats.totalScans}',
                            icon: Icons.qr_code_scanner_rounded,
                            color: QRadarColors.primaryBlue,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _MetricCard(
                            title: 'BLOCKED THREATS',
                            value: '${stats.blockedThreatsCount}',
                            icon: Icons.gpp_bad_rounded,
                            color: QRadarColors.malicious,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: _MetricCard(
                            title: 'SAFE TARGETS',
                            value: '${stats.verdictCounts.safe}',
                            icon: Icons.check_circle_rounded,
                            color: QRadarColors.safe,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _MetricCard(
                            title: 'SUSPICIOUS WARNS',
                            value: '${stats.verdictCounts.suspicious}',
                            icon: Icons.warning_rounded,
                            color: QRadarColors.suspicious,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),

              const SizedBox(height: 24),

              // Charts Grid: Side by side on Desktop, stacked on Mobile
              if (isWide)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: _buildVerdictChartCard(stats)),
                    const SizedBox(width: 20),
                    Expanded(child: _buildRiskDistributionCard(stats)),
                  ],
                )
              else ...[
                _buildVerdictChartCard(stats),
                const SizedBox(height: 20),
                _buildRiskDistributionCard(stats),
              ],

              const SizedBox(height: 26),

              // Top Scanned Domains Table
              const Text(
                'TOP INSPECTED DOMAINS & DESTINATIONS',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.0,
                  color: QRadarColors.textSecondary,
                ),
              ),
              const SizedBox(height: 12),

              if (stats.topScannedDomains.isEmpty)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: QRadarColors.surface,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: QRadarColors.border),
                  ),
                  child: const Text('No domains recorded yet.', style: TextStyle(color: QRadarColors.textSecondary)),
                )
              else
                Container(
                  decoration: BoxDecoration(
                    color: QRadarColors.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: QRadarColors.border),
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: stats.topScannedDomains.length,
                    separatorBuilder: (_, __) => const Divider(color: QRadarColors.border, height: 1),
                    itemBuilder: (context, index) {
                      final domainItem = stats.topScannedDomains[index];
                      final riskColor = AppTheme.getScoreColor(domainItem.highestRisk);

                      return Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Row(
                          children: [
                            Container(
                              width: 28,
                              height: 28,
                              alignment: Alignment.center,
                              decoration: BoxDecoration(
                                color: QRadarColors.surfaceElevated,
                                shape: BoxShape.circle,
                                border: Border.all(color: QRadarColors.border),
                              ),
                              child: Text(
                                '${index + 1}',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: QRadarColors.textSecondary),
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Text(
                                domainItem.domain,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: QRadarColors.textPrimary,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: riskColor.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: riskColor.withOpacity(0.4)),
                              ),
                              child: Text(
                                'Risk ${domainItem.highestRisk}',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: riskColor),
                              ),
                            ),
                            const SizedBox(width: 14),
                            Text(
                              '${domainItem.count}x',
                              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: QRadarColors.primaryBlue),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),

              const SizedBox(height: 30),
            ],
          ),
        );
      },
    );
  }

  Widget _buildVerdictChartCard(DashboardStats stats) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: QRadarColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: QRadarColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'VERDICT BREAKDOWN',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1.0, color: QRadarColors.textSecondary),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 180,
            child: PieChart(
              PieChartData(
                sectionsSpace: 3,
                centerSpaceRadius: 46,
                sections: [
                  PieChartSectionData(
                    color: QRadarColors.safe,
                    value: stats.verdictCounts.safe.toDouble(),
                    title: stats.verdictCounts.safe > 0 ? '${stats.verdictCounts.safe}' : '',
                    radius: 46,
                    titleStyle: const TextStyle(fontWeight: FontWeight.bold, color: Colors.black, fontSize: 13),
                  ),
                  PieChartSectionData(
                    color: QRadarColors.suspicious,
                    value: stats.verdictCounts.suspicious.toDouble(),
                    title: stats.verdictCounts.suspicious > 0 ? '${stats.verdictCounts.suspicious}' : '',
                    radius: 46,
                    titleStyle: const TextStyle(fontWeight: FontWeight.bold, color: Colors.black, fontSize: 13),
                  ),
                  PieChartSectionData(
                    color: QRadarColors.malicious,
                    value: stats.verdictCounts.malicious.toDouble(),
                    title: stats.verdictCounts.malicious > 0 ? '${stats.verdictCounts.malicious}' : '',
                    radius: 46,
                    titleStyle: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 13),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _LegendItem(color: QRadarColors.safe, label: 'Safe'),
              _LegendItem(color: QRadarColors.suspicious, label: 'Suspicious'),
              _LegendItem(color: QRadarColors.malicious, label: 'Malicious'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRiskDistributionCard(DashboardStats stats) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: QRadarColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: QRadarColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'RISK SCORE BRACKETS',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1.0, color: QRadarColors.textSecondary),
              ),
              const Spacer(),
              Text(
                'Avg: ${stats.averageRiskScore}/100',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w900,
                  color: AppTheme.getScoreColor(stats.averageRiskScore.toInt()),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 180,
            child: BarChart(
              BarChartData(
                alignment: BarChartAlignment.spaceAround,
                maxY: [
                  stats.riskDistribution.safe,
                  stats.riskDistribution.suspicious,
                  stats.riskDistribution.malicious,
                  5
                ].reduce((a, b) => a > b ? a : b).toDouble() + 2,
                barTouchData: BarTouchData(enabled: true),
                titlesData: FlTitlesData(
                  show: true,
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        switch (value.toInt()) {
                          case 0:
                            return const Padding(
                              padding: EdgeInsets.only(top: 8.0),
                              child: Text('0-29 Low', style: TextStyle(fontSize: 11, color: QRadarColors.textSecondary)),
                            );
                          case 1:
                            return const Padding(
                              padding: EdgeInsets.only(top: 8.0),
                              child: Text('30-69 Med', style: TextStyle(fontSize: 11, color: QRadarColors.textSecondary)),
                            );
                          case 2:
                            return const Padding(
                              padding: EdgeInsets.only(top: 8.0),
                              child: Text('70-100 High', style: TextStyle(fontSize: 11, color: QRadarColors.textSecondary)),
                            );
                          default:
                            return const Text('');
                        }
                      },
                    ),
                  ),
                  leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (val) => const FlLine(color: QRadarColors.border, strokeWidth: 1),
                ),
                borderData: FlBorderData(show: false),
                barGroups: [
                  BarChartGroupData(
                    x: 0,
                    barRods: [
                      BarChartRodData(
                        toY: stats.riskDistribution.safe.toDouble(),
                        color: QRadarColors.safe,
                        width: 32,
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ],
                  ),
                  BarChartGroupData(
                    x: 1,
                    barRods: [
                      BarChartRodData(
                        toY: stats.riskDistribution.suspicious.toDouble(),
                        color: QRadarColors.suspicious,
                        width: 32,
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ],
                  ),
                  BarChartGroupData(
                    x: 2,
                    barRods: [
                      BarChartRodData(
                        toY: stats.riskDistribution.malicious.toDouble(),
                        color: QRadarColors.malicious,
                        width: 32,
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Center(
            child: Text(
              'Distribution across Low, Medium, and High threat destinations',
              style: TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _MetricCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: QRadarColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: QRadarColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const Spacer(),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                  color: QRadarColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            value,
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w900,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: QRadarColors.textSecondary, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }
}
