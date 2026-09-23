import 'heuristic_indicator.dart';

class MLResult {
  final bool available;
  final String status; // "ANALYZED", "UNAVAILABLE", "NOT_APPLICABLE"
  final String modelName;
  final String? prediction; // "Phishing", "Legitimate", null
  final double? confidence;
  final double? phishingProbability;
  final String? modelVersion;
  final String? reason;

  MLResult({
    required this.available,
    this.status = 'ANALYZED',
    this.modelName = 'Random Forest',
    this.prediction,
    this.confidence,
    this.phishingProbability,
    this.modelVersion,
    this.reason,
  });

  factory MLResult.fromJson(Map<String, dynamic> json) {
    return MLResult(
      available: json['available'] ?? false,
      status: (json['status'] ?? (json['available'] == true ? 'ANALYZED' : 'UNAVAILABLE')).toString().toUpperCase(),
      modelName: json['model_name'] ?? 'Random Forest',
      prediction: json['prediction'],
      confidence: (json['confidence'] as num?)?.toDouble(),
      phishingProbability: (json['phishing_probability'] as num?)?.toDouble(),
      modelVersion: json['model_version'],
      reason: json['reason'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'available': available,
      'status': status,
      'model_name': modelName,
      'prediction': prediction,
      'confidence': confidence,
      'phishing_probability': phishingProbability,
      'model_version': modelVersion,
      'reason': reason,
    };
  }

  bool get isAnalyzed => status == 'ANALYZED';
  bool get isUnavailable => status == 'UNAVAILABLE';
  bool get isNotApplicable => status == 'NOT_APPLICABLE';
}

class ThreatIntelResult {
  final String status; // "THREAT_FOUND", "SUSPICIOUS", "NO_THREAT_FOUND", "NO_RECORD", "UNAVAILABLE", "NOT_CONFIGURED", "NOT_APPLICABLE"
  final String provider;
  final bool checked;
  final String? result;
  final String? message;
  final String? details;
  final String? reason;
  final String? errorReason;
  final int? maliciousCount;
  final int? suspiciousCount;
  final int? harmlessCount;
  final int? undetectedCount;
  final bool cached;

  ThreatIntelResult({
    required this.status,
    required this.provider,
    this.checked = false,
    this.result,
    this.message,
    this.details,
    this.reason,
    this.errorReason,
    this.maliciousCount,
    this.suspiciousCount,
    this.harmlessCount,
    this.undetectedCount,
    this.cached = false,
  });

  factory ThreatIntelResult.fromJson(Map<String, dynamic> json) {
    return ThreatIntelResult(
      status: (json['status'] ?? 'NO_RECORD').toString().toUpperCase(),
      provider: json['provider'] ?? 'QRadar Local Threat Engine',
      checked: json['checked'] ?? false,
      result: json['result'],
      message: json['message'],
      details: json['details'],
      reason: json['reason'],
      errorReason: json['error_reason'],
      maliciousCount: (json['malicious_count'] as num?)?.toInt(),
      suspiciousCount: (json['suspicious_count'] as num?)?.toInt(),
      harmlessCount: (json['harmless_count'] as num?)?.toInt(),
      undetectedCount: (json['undetected_count'] as num?)?.toInt(),
      cached: json['cached'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'status': status,
      'provider': provider,
      'checked': checked,
      'result': result,
      'message': message,
      'details': details,
      'reason': reason,
      'error_reason': errorReason,
      'malicious_count': maliciousCount,
      'suspicious_count': suspiciousCount,
      'harmless_count': harmlessCount,
      'undetected_count': undetectedCount,
      'cached': cached,
    };
  }

  bool get isNotApplicable => status == 'NOT_APPLICABLE';
  bool get isNotConfigured => status == 'NOT_CONFIGURED';
  bool get isUnavailable => status == 'UNAVAILABLE';
  bool get isNoRecord => status == 'NO_RECORD';
  bool get isClean => status == 'CLEAN' || status == 'NO_THREAT_FOUND';
  bool get isSuspicious => status == 'SUSPICIOUS' || (suspiciousCount != null && suspiciousCount! > 0);
  bool get isMalicious => status == 'THREAT_FOUND' || status == 'KNOWN_MALICIOUS' || (maliciousCount != null && maliciousCount! > 0);
}

class SecurityResult {
  final String scanId;
  final String analyzedAt;
  final String contentType; // "url", "text", "upi", "dangerous_scheme"
  final String originalContent;
  final String? normalizedUrl;
  final String? domain;
  final String? scheme;
  final String verdict; // "SAFE", "SUSPICIOUS", "MALICIOUS"
  final int riskScore; // 0 - 100
  final String recommendedAction; // "ALLOW", "WARN", "BLOCK"
  final List<String> reasons;
  final List<HeuristicIndicator> heuristics;
  final MLResult ml;
  final ThreatIntelResult threatIntelligence;
  final bool isDegraded;

  SecurityResult({
    required this.scanId,
    required this.analyzedAt,
    required this.contentType,
    required this.originalContent,
    this.normalizedUrl,
    this.domain,
    this.scheme,
    required this.verdict,
    required this.riskScore,
    required this.recommendedAction,
    required this.reasons,
    required this.heuristics,
    required this.ml,
    required this.threatIntelligence,
    this.isDegraded = false,
  });

  factory SecurityResult.fromJson(Map<String, dynamic> json) {
    return SecurityResult(
      scanId: json['scan_id'] ?? '',
      analyzedAt: json['analyzed_at'] ?? '',
      contentType: json['content_type'] ?? 'url',
      originalContent: json['original_content'] ?? '',
      normalizedUrl: json['normalized_url'],
      domain: json['domain'],
      scheme: json['scheme'],
      verdict: json['verdict'] ?? 'SAFE',
      riskScore: json['risk_score'] ?? 0,
      recommendedAction: json['recommended_action'] ?? 'ALLOW',
      reasons: (json['reasons'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      heuristics: (json['heuristics'] as List<dynamic>?)
              ?.map((e) => HeuristicIndicator.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      ml: json['ml'] != null
          ? MLResult.fromJson(json['ml'])
          : MLResult(available: false, status: 'NOT_APPLICABLE'),
      threatIntelligence: json['threat_intelligence'] != null
          ? ThreatIntelResult.fromJson(json['threat_intelligence'])
          : ThreatIntelResult(status: 'NOT_APPLICABLE', provider: 'QRadar Local Threat Engine'),
      isDegraded: json['is_degraded'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'scan_id': scanId,
      'analyzed_at': analyzedAt,
      'content_type': contentType,
      'original_content': originalContent,
      'normalized_url': normalizedUrl,
      'domain': domain,
      'scheme': scheme,
      'verdict': verdict,
      'risk_score': riskScore,
      'recommended_action': recommendedAction,
      'reasons': reasons,
      'heuristics': heuristics.map((e) => e.toJson()).toList(),
      'ml': ml.toJson(),
      'threat_intelligence': threatIntelligence.toJson(),
      'is_degraded': isDegraded,
    };
  }

  bool get isSafe => verdict.toUpperCase() == 'SAFE';
  bool get isSuspicious => verdict.toUpperCase() == 'SUSPICIOUS';
  bool get isMalicious => verdict.toUpperCase() == 'MALICIOUS';
  bool get isBlock => recommendedAction.toUpperCase() == 'BLOCK';
}
