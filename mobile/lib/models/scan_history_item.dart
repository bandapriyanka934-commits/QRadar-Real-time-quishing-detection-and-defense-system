class ScanHistoryItem {
  final String scanId;
  final String createdAt;
  final String contentType;
  final String originalContent;
  final String? normalizedUrl;
  final String? domain;
  final String verdict;
  final int riskScore;
  final String recommendedAction;
  final List<String> reasons;
  final String threatIntelStatus;
  final double? mlProbability;

  ScanHistoryItem({
    required this.scanId,
    required this.createdAt,
    required this.contentType,
    required this.originalContent,
    this.normalizedUrl,
    this.domain,
    required this.verdict,
    required this.riskScore,
    required this.recommendedAction,
    required this.reasons,
    required this.threatIntelStatus,
    this.mlProbability,
  });

  factory ScanHistoryItem.fromJson(Map<String, dynamic> json) {
    return ScanHistoryItem(
      scanId: json['scan_id'] ?? '',
      createdAt: json['created_at'] ?? '',
      contentType: json['content_type'] ?? 'url',
      originalContent: json['original_content'] ?? '',
      normalizedUrl: json['normalized_url'],
      domain: json['domain'],
      verdict: json['verdict'] ?? 'SAFE',
      riskScore: json['risk_score'] ?? 0,
      recommendedAction: json['recommended_action'] ?? 'ALLOW',
      reasons: (json['reasons'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      threatIntelStatus: json['threat_intel_status'] ?? 'NOT_FOUND',
      mlProbability: (json['ml_probability'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'scan_id': scanId,
      'created_at': createdAt,
      'content_type': contentType,
      'original_content': originalContent,
      'normalized_url': normalizedUrl,
      'domain': domain,
      'verdict': verdict,
      'risk_score': riskScore,
      'recommended_action': recommendedAction,
      'reasons': reasons,
      'threat_intel_status': threatIntelStatus,
      'ml_probability': mlProbability,
    };
  }

  bool get isSafe => verdict.toUpperCase() == 'SAFE';
  bool get isSuspicious => verdict.toUpperCase() == 'SUSPICIOUS';
  bool get isMalicious => verdict.toUpperCase() == 'MALICIOUS';
}
