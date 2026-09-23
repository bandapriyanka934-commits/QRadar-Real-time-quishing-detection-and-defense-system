class QRItem {
  final String content;
  final String qrType; // "url", "text", "dangerous_scheme"
  final List<List<double>>? polygon;

  QRItem({
    required this.content,
    required this.qrType,
    this.polygon,
  });

  factory QRItem.fromJson(Map<String, dynamic> json) {
    List<List<double>>? poly;
    if (json['polygon'] != null) {
      poly = (json['polygon'] as List<dynamic>)
          .map((p) => (p as List<dynamic>).map((coord) => (coord as num).toDouble()).toList())
          .toList();
    }
    return QRItem(
      content: json['content'] ?? '',
      qrType: json['qr_type'] ?? 'url',
      polygon: poly,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'content': content,
      'qr_type': qrType,
      'polygon': polygon,
    };
  }
}

class MultiQRDecodeResponse {
  final int totalFound;
  final List<QRItem> qrCodes;

  MultiQRDecodeResponse({
    required this.totalFound,
    required this.qrCodes,
  });

  factory MultiQRDecodeResponse.fromJson(Map<String, dynamic> json) {
    return MultiQRDecodeResponse(
      totalFound: json['total_found'] ?? 0,
      qrCodes: (json['qr_codes'] as List<dynamic>?)
              ?.map((item) => QRItem.fromJson(item as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_found': totalFound,
      'qr_codes': qrCodes.map((e) => e.toJson()).toList(),
    };
  }
}
