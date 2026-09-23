class HeuristicIndicator {
  final String indicator;
  final String name;
  final bool triggered;
  final String severity; // "LOW", "MEDIUM", "HIGH", "CRITICAL"
  final int scoreContribution;
  final String explanation;
  final String? evidence;

  HeuristicIndicator({
    required this.indicator,
    required this.name,
    required this.triggered,
    required this.severity,
    required this.scoreContribution,
    required this.explanation,
    this.evidence,
  });

  factory HeuristicIndicator.fromJson(Map<String, dynamic> json) {
    return HeuristicIndicator(
      indicator: json['indicator'] ?? '',
      name: json['name'] ?? '',
      triggered: json['triggered'] ?? false,
      severity: json['severity'] ?? 'LOW',
      scoreContribution: json['score_contribution'] ?? 0,
      explanation: json['explanation'] ?? '',
      evidence: json['evidence'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'indicator': indicator,
      'name': name,
      'triggered': triggered,
      'severity': severity,
      'score_contribution': scoreContribution,
      'explanation': explanation,
      'evidence': evidence,
    };
  }
}
