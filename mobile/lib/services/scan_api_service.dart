import 'dart:typed_data';
import '../core/network/api_client.dart';
import '../models/scan_result.dart';
import '../models/scan_history_item.dart';
import '../models/dashboard_stats.dart';
import '../models/multi_qr_response.dart';

class ScanApiService {
  final ApiClient _client;

  ScanApiService({ApiClient? client}) : _client = client ?? ApiClient();

  /// Scans a raw URL or text string through backend authoritative pipeline
  Future<SecurityResult> scanUrl(String url, {String source = 'manual'}) async {
    final response = await _client.post(
      '/api/v1/scan/url',
      body: {'url': url, 'source': source},
    );
    return SecurityResult.fromJson(response as Map<String, dynamic>);
  }

  /// Uploads an image for QR extraction & analysis
  /// Can return either a [SecurityResult] (if single QR) or [MultiQRDecodeResponse] (if multiple QRs)
  Future<dynamic> scanImage(
    Uint8List imageBytes,
    String filename, {
    int? selectedIndex,
  }) async {
    final response = await _client.uploadImage(
      '/api/v1/scan/image',
      imageBytes,
      filename,
      selectedIndex: selectedIndex,
    );

    if (response is Map<String, dynamic>) {
      if (response.containsKey('total_found') && response.containsKey('qr_codes')) {
        return MultiQRDecodeResponse.fromJson(response);
      } else if (response.containsKey('scan_id')) {
        return SecurityResult.fromJson(response);
      }
    }
    throw ApiException('Unexpected response format from scan image endpoint.');
  }

  /// Fast decode-only endpoint for image inspection
  Future<MultiQRDecodeResponse> decodeOnly(Uint8List imageBytes, String filename) async {
    final response = await _client.uploadImage(
      '/api/v1/scan/decode-only',
      imageBytes,
      filename,
    );
    return MultiQRDecodeResponse.fromJson(response as Map<String, dynamic>);
  }

  /// Fetches paginated scan history
  Future<List<ScanHistoryItem>> getHistory({int limit = 50, int offset = 0, String? verdict}) async {
    final queryParams = <String, String>{
      'limit': limit.toString(),
      'offset': offset.toString(),
    };
    if (verdict != null && verdict.isNotEmpty) {
      queryParams['verdict'] = verdict;
    }

    final response = await _client.get('/api/v1/scans', queryParams: queryParams);
    if (response is List) {
      return response.map((e) => ScanHistoryItem.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }

  /// Fetches full scan details by ID
  Future<SecurityResult> getScanDetails(String scanId) async {
    final response = await _client.get('/api/v1/scans/$scanId');
    return SecurityResult.fromJson(response);
  }

  /// Deletes a specific scan record
  Future<void> deleteScan(String scanId) async {
    await _client.delete('/api/v1/scans/$scanId');
  }

  /// Clears all scan history
  Future<void> clearAllHistory() async {
    await _client.delete('/api/v1/scans');
  }

  /// Fetches aggregated dashboard analytics
  Future<DashboardStats> getDashboard() async {
    final response = await _client.get('/api/v1/dashboard');
    return DashboardStats.fromJson(response);
  }

  /// Performs backend connectivity and ML health check
  Future<Map<String, dynamic>> checkHealth() async {
    return await _client.get('/health');
  }
}
