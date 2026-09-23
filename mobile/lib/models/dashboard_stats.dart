class RiskDistribution {
  final int safe;
  final int suspicious;
  final int malicious;

  RiskDistribution({
    required this.safe,
    required this.suspicious,
    required this.malicious,
  });

  factory RiskDistribution.fromJson(Map<String, dynamic> json) {
    return RiskDistribution(
      safe: json['safe'] ?? 0,
      suspicious: json['suspicious'] ?? 0,
      malicious: json['malicious'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'safe': safe,
      'suspicious': suspicious,
      'malicious': malicious,
    };
  }
}

class VerdictCounts {
  final int safe;
  final int suspicious;
  final int malicious;

  VerdictCounts({
    required this.safe,
    required this.suspicious,
    required this.malicious,
  });

  factory VerdictCounts.fromJson(Map<String, dynamic> json) {
    return VerdictCounts(
      safe: json['safe'] ?? 0,
      suspicious: json['suspicious'] ?? 0,
      malicious: json['malicious'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'safe': safe,
      'suspicious': suspicious,
      'malicious': malicious,
    };
  }
}

class ThreatTimelinePoint {
  final String date;
  final int total;
  final int safe;
  final int suspicious;
  final int malicious;

  ThreatTimelinePoint({
    required this.date,
    required this.total,
    required this.safe,
    required this.suspicious,
    required this.malicious,
  });

  factory ThreatTimelinePoint.fromJson(Map<String, dynamic> json) {
    return ThreatTimelinePoint(
      date: json['date'] ?? '',
      total: json['total'] ?? 0,
      safe: json['safe'] ?? 0,
      suspicious: json['suspicious'] ?? 0,
      malicious: json['malicious'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date,
      'total': total,
      'safe': safe,
      'suspicious': suspicious,
      'malicious': malicious,
    };
  }
}

class TopDomainItem {
  final String domain;
  final int count;
  final int highestRisk;

  TopDomainItem({
    required this.domain,
    required this.count,
    required this.highestRisk,
  });

  factory TopDomainItem.fromJson(Map<String, dynamic> json) {
    return TopDomainItem(
      domain: json['domain'] ?? '',
      count: json['count'] ?? 0,
      highestRisk: json['highest_risk'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'domain': domain,
      'count': count,
      'highest_risk': highestRisk,
    };
  }
}

class DashboardStats {
  final int totalScans;
  final VerdictCounts verdictCounts;
  final RiskDistribution riskDistribution;
  final double averageRiskScore;
  final int blockedThreatsCount;
  final List<ThreatTimelinePoint> timeline;
  final List<TopDomainItem> topScannedDomains;

  DashboardStats({
    required this.totalScans,
    required this.verdictCounts,
    required this.riskDistribution,
    required this.averageRiskScore,
    required this.blockedThreatsCount,
    required this.timeline,
    required this.topScannedDomains,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalScans: json['total_scans'] ?? 0,
      verdictCounts: json['verdict_counts'] != null
          ? VerdictCounts.fromJson(json['verdict_counts'])
          : VerdictCounts(safe: 0, suspicious: 0, malicious: 0),
      riskDistribution: json['risk_distribution'] != null
          ? RiskDistribution.fromJson(json['risk_distribution'])
          : RiskDistribution(safe: 0, suspicious: 0, malicious: 0),
      averageRiskScore: (json['average_risk_score'] as num?)?.toDouble() ?? 0.0,
      blockedThreatsCount: json['blocked_threats_count'] ?? 0,
      timeline: (json['timeline'] as List<dynamic>?)
              ?.map((e) => ThreatTimelinePoint.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      topScannedDomains: (json['top_scanned_domains'] as List<dynamic>?)
              ?.map((e) => TopDomainItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_scans': totalScans,
      'verdict_counts': verdictCounts.toJson(),
      'risk_distribution': riskDistribution.toJson(),
      'average_risk_score': averageRiskScore,
      'blocked_threats_count': blockedThreatsCount,
      'timeline': timeline.map((e) => e.toJson()).toList(),
      'top_scanned_domains': topScannedDomains.map((e) => e.toJson()).toList(),
    };
  }
}
