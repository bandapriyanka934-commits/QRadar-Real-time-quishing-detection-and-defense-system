import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../config/env_config.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

class ApiClient {
  final http.Client _client;
  static const Duration defaultTimeout = Duration(seconds: 10);

  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  String get _baseUrl => EnvConfig.baseUrl;

  Future<Map<String, dynamic>> get(String endpoint, {Map<String, String>? queryParams}) async {
    final uri = Uri.parse('$_baseUrl$endpoint').replace(queryParameters: queryParams);
    try {
      final response = await _client.get(uri).timeout(defaultTimeout);
      return _processResponse(response);
    } on ApiException {
      rethrow;
    } on http.ClientException catch (e) {
      throw ApiException('Network connection error: ${e.message}');
    } catch (e) {
      if (e.toString().contains('SocketException') || e.toString().contains('Failed to fetch') || e.toString().contains('Connection refused')) {
        throw ApiException('Unable to connect to QRadar Backend ($_baseUrl). Ensure the backend is running and the address is correct in Settings.');
      }
      throw ApiException('Request failed: $e');
    }
  }

  Future<dynamic> post(String endpoint, {Map<String, dynamic>? body}) async {
    final uri = Uri.parse('$_baseUrl$endpoint');
    try {
      final response = await _client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: body != null ? jsonEncode(body) : null,
      ).timeout(defaultTimeout);

      return _processResponse(response);
    } on ApiException {
      rethrow;
    } on http.ClientException catch (e) {
      throw ApiException('Connection error: ${e.message}');
    } catch (e) {
      if (e.toString().contains('SocketException') || e.toString().contains('Failed to fetch') || e.toString().contains('Connection refused')) {
        throw ApiException('Unable to connect to QRadar Backend ($_baseUrl). Ensure the server is online.');
      }
      throw ApiException('Request failed: $e');
    }
  }

  Future<dynamic> uploadImage(
    String endpoint,
    Uint8List imageBytes,
    String filename, {
    int? selectedIndex,
  }) async {
    final uri = Uri.parse('$_baseUrl$endpoint');
    try {
      final safeFilename = filename.isEmpty
          ? 'qr_image.png'
          : (filename.contains('.') ? filename : '$filename.png');

      final request = http.MultipartRequest('POST', uri);
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          imageBytes,
          filename: safeFilename,
        ),
      );

      if (selectedIndex != null) {
        request.fields['selected_index'] = selectedIndex.toString();
      }

      final streamedResponse = await _client.send(request).timeout(const Duration(seconds: 15));
      final response = await http.Response.fromStream(streamedResponse);

      return _processResponse(response);
    } on ApiException {
      rethrow;
    } catch (e) {
      if (e.toString().contains('SocketException') || e.toString().contains('Failed to fetch') || e.toString().contains('Connection refused')) {
        throw ApiException('Backend connection failed ($_baseUrl).');
      }
      throw ApiException('Image upload failed: $e');
    }
  }

  Future<Map<String, dynamic>> delete(String endpoint) async {
    final uri = Uri.parse('$_baseUrl$endpoint');
    try {
      final response = await _client.delete(uri).timeout(defaultTimeout);
      return _processResponse(response);
    } on ApiException {
      rethrow;
    } catch (e) {
      if (e.toString().contains('SocketException') || e.toString().contains('Failed to fetch') || e.toString().contains('Connection refused')) {
        throw ApiException('Backend connection failed ($_baseUrl).');
      }
      throw ApiException('Delete operation failed: $e');
    }
  }

  dynamic _processResponse(http.Response response) {
    dynamic decoded;
    try {
      decoded = jsonDecode(response.body);
    } catch (_) {
      decoded = {'message': response.body};
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    } else {
      String errMsg = 'Server error (${response.statusCode})';
      if (decoded is Map && decoded.containsKey('detail')) {
        errMsg = decoded['detail'].toString();
      } else if (decoded is Map && decoded.containsKey('message')) {
        errMsg = decoded['message'].toString();
      }
      throw ApiException(errMsg, response.statusCode);
    }
  }
}
