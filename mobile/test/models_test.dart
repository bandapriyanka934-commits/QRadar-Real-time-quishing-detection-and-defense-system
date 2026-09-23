import 'package:flutter_test/flutter_test.dart';
import 'package:qradar_mobile/models/scan_result.dart';
import 'package:qradar_mobile/models/heuristic_indicator.dart';
import 'package:qradar_mobile/models/scan_history_item.dart';
import 'package:qradar_mobile/models/dashboard_stats.dart';

void main() {
  group('Flutter Data Models Test', () {
    test('HeuristicIndicator serialization and deserialization', () {
      final json = {
        'indicator': 'LOOKALIKE_TYPOSQUATTING',
        'name': 'Brand Typosquatting',
        'triggered': true,
        'severity': 'HIGH',
        'score_contribution': 35,
        'explanation': 'Resembles PayPal',
        'evidence': 'paypa1.com',
      };

      final indicator = HeuristicIndicator.fromJson(json);
      expect(indicator.indicator, 'LOOKALIKE_TYPOSQUATTING');
      expect(indicator.triggered, true);
      expect(indicator.severity, 'HIGH');
      expect(indicator.scoreContribution, 35);
      expect(indicator.evidence, 'paypa1.com');

      final serialized = indicator.toJson();
      expect(serialized['indicator'], 'LOOKALIKE_TYPOSQUATTING');
      expect(serialized['score_contribution'], 35);
    });

    test('SecurityResult parsing and verdict properties', () {
      final json = {
        'scan_id': 'test-uuid-1234',
        'analyzed_at': '2026-09-11T12:00:00Z',
        'content_type': 'url',
        'original_content': 'https://paypa1-verify.xyz/login',
        'normalized_url': 'https://paypa1-verify.xyz/login',
        'domain': 'paypa1-verify.xyz',
        'scheme': 'https',
        'verdict': 'MALICIOUS',
        'risk_score': 92,
        'recommended_action': 'BLOCK',
        'reasons': ['Resembles PayPal', 'High ML Phishing Probability'],
        'heuristics': [
          {
            'indicator': 'LOOKALIKE_TYPOSQUATTING',
            'name': 'Brand Typosquatting',
            'triggered': true,
            'severity': 'HIGH',
            'score_contribution': 35,
            'explanation': 'Resembles PayPal',
            'evidence': 'paypa1-verify.xyz',
          }
        ],
        'ml': {
          'available': true,
          'is_phishing': true,
          'phishing_probability': 0.94,
          'model_version': '1.0.0'
        },
        'threat_intelligence': {
          'status': 'KNOWN_MALICIOUS',
          'provider': 'Mock Provider',
          'details': 'Simulated threat record',
          'cached': false
        },
        'is_degraded': false
      };

      final result = SecurityResult.fromJson(json);
      expect(result.scanId, 'test-uuid-1234');
      expect(result.isMalicious, true);
      expect(result.isSafe, false);
      expect(result.isBlock, true);
      expect(result.riskScore, 92);
      expect(result.heuristics.length, 1);
      expect(result.ml.phishingProbability, 0.94);
      expect(result.threatIntelligence.status, 'KNOWN_MALICIOUS');
    });

    test('ScanHistoryItem parsing', () {
      final json = {
        'scan_id': 'hist-1',
        'created_at': '2026-09-11T10:00:00Z',
        'content_type': 'url',
        'original_content': 'https://google.com',
        'normalized_url': 'https://google.com',
        'domain': 'google.com',
        'verdict': 'SAFE',
        'risk_score': 10,
        'recommended_action': 'ALLOW',
        'reasons': ['No indicators detected'],
        'threat_intel_status': 'CLEAN',
        'ml_probability': 0.02,
      };

      final item = ScanHistoryItem.fromJson(json);
      expect(item.isSafe, true);
      expect(item.riskScore, 10);
      expect(item.domain, 'google.com');
    });

    test('DashboardStats parsing', () {
      final json = {
        'total_scans': 25,
        'verdict_counts': {'safe': 15, 'suspicious': 6, 'malicious': 4},
        'risk_distribution': {'safe': 15, 'suspicious': 6, 'malicious': 4},
        'average_risk_score': 28.5,
        'blocked_threats_count': 4,
        'timeline': [
          {'date': '2026-09-11', 'total': 25, 'safe': 15, 'suspicious': 6, 'malicious': 4}
        ],
        'top_scanned_domains': [
          {'domain': 'google.com', 'count': 10, 'highest_risk': 10},
          {'domain': 'paypa1.com', 'count': 4, 'highest_risk': 90}
        ]
      };

      final stats = DashboardStats.fromJson(json);
      expect(stats.totalScans, 25);
      expect(stats.verdictCounts.safe, 15);
      expect(stats.verdictCounts.malicious, 4);
      expect(stats.topScannedDomains.length, 2);
    });
  });
}
