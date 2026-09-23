import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/utils/formatters.dart';
import '../../services/scan_api_service.dart';
import '../../models/scan_history_item.dart';
import '../../widgets/verdict_badge.dart';
import 'history_detail_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({Key? key}) : super(key: key);

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final ScanApiService _apiService = ScanApiService();
  final TextEditingController _searchController = TextEditingController();

  List<ScanHistoryItem> _items = [];
  bool _isLoading = true;
  String? _errorMessage;
  String _selectedFilter = 'ALL'; // ALL, SAFE, SUSPICIOUS, MALICIOUS
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final verdictParam = _selectedFilter == 'ALL' ? null : _selectedFilter;
      final history = await _apiService.getHistory(verdict: verdictParam);
      if (mounted) {
        setState(() {
          _items = history;
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

  Future<void> _deleteItem(String scanId, int index) async {
    final removed = _items[index];
    setState(() {
      _items.removeAt(index);
    });

    try {
      await _apiService.deleteScan(scanId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Scan log deleted'), duration: Duration(seconds: 2)),
      );
    } catch (e) {
      // Revert if failed
      if (mounted) {
        setState(() {
          _items.insert(index, removed);
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Delete failed: $e'), backgroundColor: QRadarColors.malicious),
        );
      }
    }
  }

  Future<void> _clearAll() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: QRadarColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: QRadarColors.border),
        ),
        title: const Text('Clear All Scan Logs?', style: TextStyle(color: QRadarColors.textPrimary)),
        content: const Text(
          'This will permanently delete all scan records from the local database.',
          style: TextStyle(color: QRadarColors.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancel', style: TextStyle(color: QRadarColors.textSecondary)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: QRadarColors.block, foregroundColor: Colors.white),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Clear All'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await _apiService.clearAllHistory();
      _fetchHistory();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Clear failed: $e'), backgroundColor: QRadarColors.malicious),
      );
    }
  }

  List<ScanHistoryItem> get _filteredItems {
    if (_searchQuery.isEmpty) return _items;
    return _items.where((item) {
      final text = '${item.originalContent} ${item.domain ?? ""} ${item.verdict}'.toLowerCase();
      return text.contains(_searchQuery.toLowerCase());
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: QRadarColors.primaryBackground,
      appBar: AppBar(
        title: const Text('Scan History Logs'),
        actions: [
          if (_items.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_sweep_rounded, color: QRadarColors.textSecondary),
              tooltip: 'Clear History',
              onPressed: _clearAll,
            ),
        ],
      ),
      body: Column(
        children: [
          // Search & Filter Bar
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search by domain or destination URL...',
                prefixIcon: const Icon(Icons.search_rounded, color: QRadarColors.textSecondary),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear_rounded, size: 18),
                        onPressed: () {
                          _searchController.clear();
                          setState(() => _searchQuery = '');
                        },
                      )
                    : null,
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
              onChanged: (val) => setState(() => _searchQuery = val),
            ),
          ),

          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            child: Row(
              children: [
                _FilterChip(
                  label: 'ALL SCANS',
                  isSelected: _selectedFilter == 'ALL',
                  onTap: () {
                    setState(() => _selectedFilter = 'ALL');
                    _fetchHistory();
                  },
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: 'SAFE ONLY',
                  statusColor: QRadarColors.safe,
                  isSelected: _selectedFilter == 'SAFE',
                  onTap: () {
                    setState(() => _selectedFilter = 'SAFE');
                    _fetchHistory();
                  },
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: 'SUSPICIOUS',
                  statusColor: QRadarColors.suspicious,
                  isSelected: _selectedFilter == 'SUSPICIOUS',
                  onTap: () {
                    setState(() => _selectedFilter = 'SUSPICIOUS');
                    _fetchHistory();
                  },
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: 'MALICIOUS',
                  statusColor: QRadarColors.malicious,
                  isSelected: _selectedFilter == 'MALICIOUS',
                  onTap: () {
                    setState(() => _selectedFilter = 'MALICIOUS');
                    _fetchHistory();
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 6),

          // Log List
          Expanded(
            child: _buildList(),
          ),
        ],
      ),
    );
  }

  Widget _buildList() {
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
              const Icon(Icons.error_outline_rounded, color: QRadarColors.malicious, size: 48),
              const SizedBox(height: 16),
              Text(
                'Failed to load history logs:\n$_errorMessage',
                style: const TextStyle(color: QRadarColors.textSecondary),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton(onPressed: _fetchHistory, child: const Text('Retry')),
            ],
          ),
        ),
      );
    }

    final filtered = _filteredItems;

    if (filtered.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: QRadarColors.surfaceElevated,
                  shape: BoxShape.circle,
                  border: Border.all(color: QRadarColors.border),
                ),
                child: const Icon(Icons.history_toggle_off_rounded, size: 42, color: QRadarColors.textSecondary),
              ),
              const SizedBox(height: 16),
              const Text(
                'No Scan Records Found',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: QRadarColors.textPrimary),
              ),
              const SizedBox(height: 6),
              Text(
                _searchQuery.isNotEmpty
                    ? 'No results match your search query.'
                    : 'Scanned QR destinations will appear in this log.',
                style: const TextStyle(fontSize: 12, color: QRadarColors.textSecondary),
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _fetchHistory,
      color: QRadarColors.primaryBlue,
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: filtered.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (context, index) {
          final item = filtered[index];
          final scoreColor = AppTheme.getScoreColor(item.riskScore);

          return Dismissible(
            key: Key(item.id),
            direction: DismissDirection.endToStart,
            background: Container(
              alignment: Alignment.centerRight,
              padding: const EdgeInsets.only(right: 20),
              decoration: BoxDecoration(
                color: QRadarColors.block,
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Icon(Icons.delete_outline_rounded, color: Colors.white, size: 24),
            ),
            onDismissed: (_) => _deleteItem(item.id, index),
            child: InkWell(
              onTap: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => HistoryDetailScreen(scanId: item.id)),
                );
              },
              borderRadius: BorderRadius.circular(14),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: QRadarColors.surface,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: QRadarColors.border),
                ),
                child: Row(
                  children: [
                    // Risk Score Badge Container
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: scoreColor.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: scoreColor.withOpacity(0.4), width: 1.2),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            '${item.riskScore}',
                            style: TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.w900,
                              color: scoreColor,
                              height: 1.0,
                            ),
                          ),
                          const SizedBox(height: 2),
                          const Text(
                            'RISK',
                            style: TextStyle(
                              fontSize: 8,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.5,
                              color: QRadarColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 14),
                    // Destination Text & Details
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item.normalizedUrl ?? item.originalContent,
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: QRadarColors.textPrimary,
                              fontFamily: 'monospace',
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 6),
                          Row(
                            children: [
                              Text(
                                Formatters.formatTimestamp(item.createdAt),
                                style: const TextStyle(fontSize: 11, color: QRadarColors.textSecondary),
                              ),
                              if (item.source != null) ...[
                                const SizedBox(width: 8),
                                const Text('•', style: TextStyle(color: QRadarColors.textSecondary, fontSize: 10)),
                                const SizedBox(width: 8),
                                Text(
                                  item.source!.toUpperCase(),
                                  style: const TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: QRadarColors.textSecondary,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 10),
                    VerdictBadge(verdict: item.verdict),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final Color? statusColor;
  final bool isSelected;
  final VoidCallback onTap;

  const _FilterChip({
    required this.label,
    this.statusColor,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final activeColor = statusColor ?? QRadarColors.primaryBlue;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color: isSelected ? activeColor.withOpacity(0.14) : QRadarColors.surfaceElevated,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? activeColor : QRadarColors.border,
            width: isSelected ? 1.2 : 1.0,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (statusColor != null) ...[
              Container(
                width: 7,
                height: 7,
                decoration: BoxDecoration(color: statusColor, shape: BoxShape.circle),
              ),
              const SizedBox(width: 6),
            ],
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                color: isSelected ? activeColor : QRadarColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
