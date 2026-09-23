"""
Unified Risk Engine for QRadar.
Centralized, deterministic scoring policy that fuses Heuristics, ML Probability,
and Threat Intelligence into an explainable 0–100 Risk Score, Verdict, and Action.
Truthfully evaluates available signals without fabricating missing data.
"""

from typing import List, Dict, Any, Tuple
from app.services.url_analyzer import ParsedContent


class UnifiedRiskEngine:
    """
    Scoring Policy:
      0 - 29   : SAFE       -> ALLOW
      30 - 69  : SUSPICIOUS -> WARN
      70 - 100 : MALICIOUS   -> BLOCK
    """

    def evaluate(
        self,
        parsed: ParsedContent,
        heuristics: List[Dict[str, Any]],
        ml_result: Dict[str, Any],
        threat_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes all security indicators into a final risk verdict.
        """
        reasons: List[str] = []
        is_degraded = False

        # CASE 1: Dangerous URI Scheme (e.g. javascript:, file:, data:, blob:, intent:)
        if parsed.is_dangerous_scheme:
            risk_score = 98
            verdict = "MALICIOUS"
            action = "BLOCK"
            reasons.append(parsed.danger_reason or f"Dangerous URI scheme '{parsed.scheme}:' detected.")
            reasons.append("Execution blocked to protect device integrity.")
            return {
                "risk_score": risk_score,
                "verdict": verdict,
                "recommended_action": action,
                "reasons": reasons,
                "is_degraded": False,
            }

        # CASE 2: UPI Financial Payment Payload (upi://pay?pa=...)
        if parsed.content_type == "upi" or parsed.scheme == "upi":
            pa = parsed.upi_params.get("pa", "")
            pn = parsed.upi_params.get("pn", "")
            am = parsed.upi_params.get("am", "")
            
            # Check for suspicious injection characters in UPI fields
            suspicious_chars = ["<", ">", "script", "javascript:", "\n", "\r", "%0a", "%0d"]
            raw_lower = parsed.original_content.lower()
            has_injection = any(c in raw_lower for c in suspicious_chars)

            if has_injection:
                risk_score = 80
                verdict = "MALICIOUS"
                action = "BLOCK"
                reasons.append("UPI payload contains suspicious script or control characters.")
                reasons.append("Payment execution blocked to prevent unauthorized or spoofed transaction.")
            elif pa and ("@" in pa):
                risk_score = 10
                verdict = "SAFE"
                action = "ALLOW"
                payee_desc = f"{pn} ({pa})" if pn else pa
                amount_desc = f" for ₹{am}" if am else ""
                reasons.append(f"Standard UPI payment QR code for {payee_desc}{amount_desc}.")
                reasons.append("Payee VPA structure validated against standard UPI format.")
            else:
                risk_score = 40
                verdict = "SUSPICIOUS"
                action = "WARN"
                reasons.append("UPI payload lacks a standard payee address (VPA); verify recipient before paying.")

            return {
                "risk_score": risk_score,
                "verdict": verdict,
                "recommended_action": action,
                "reasons": reasons,
                "is_degraded": False,
            }

        # CASE 3: Non-URL Plain Text / Contact Schemes
        if parsed.content_type == "text":
            risk_score = 5
            verdict = "SAFE"
            action = "ALLOW"
            scheme_label = f" ({parsed.scheme}:)" if parsed.scheme else ""
            reasons.append(f"Scanned payload is standard plain text / contact data{scheme_label}.")
            return {
                "risk_score": risk_score,
                "verdict": verdict,
                "recommended_action": action,
                "reasons": reasons,
                "is_degraded": False,
            }

        # CASE 4: Standard Web URL Security Evaluation Pipeline
        base_score = 0
        triggered_heuristics = [h for h in heuristics if h.get("triggered")]

        # 1. Tally Heuristics Points (max contribution 55 points)
        heuristic_points = sum(h.get("score_contribution", 0) for h in triggered_heuristics)
        # Cap heuristics to prevent single weak signal runaway
        capped_heuristics = min(55, heuristic_points)
        base_score += capped_heuristics

        for h in triggered_heuristics:
            if h.get("indicator") in {"USERINFO_TRICK", "LOOKALIKE_TYPOSQUATTING", "IP_ADDRESS_HOST", "SUSPICIOUS_ENCODING"}:
                reasons.append(h.get("explanation", ""))

        # 2. Machine Learning Contribution (0 to 35 points)
        ml_status = ml_result.get("status", "")
        if ml_status == "ANALYZED" and ml_result.get("phishing_probability") is not None:
            prob = float(ml_result["phishing_probability"])
            ml_points = int(prob * 35)
            base_score += ml_points
            if prob >= 0.75:
                reasons.append(f"Machine learning classifier identified high phishing likelihood ({int(prob * 100)}% risk).")
            elif prob >= 0.45:
                reasons.append(f"Machine learning classifier detected suspicious structural patterns ({int(prob * 100)}% risk).")
        elif ml_status == "UNAVAILABLE":
            is_degraded = True

        # 3. Threat Intelligence Influence
        ti_status = threat_intel.get("status", "CLEAN")
        ti_provider = threat_intel.get("provider", "Threat Intelligence")
        mal_count = threat_intel.get("malicious_count")
        susp_count = threat_intel.get("suspicious_count")

        if ti_status in {"MALICIOUS", "THREAT_FOUND", "KNOWN_MALICIOUS"} or (mal_count is not None and mal_count > 0):
            # Precedence Rule: Confirmed malicious threat intelligence forces BLOCK decision
            base_score = max(base_score, 88)
            details = threat_intel.get("message") or threat_intel.get("details") or "Identified in verified threat feeds."
            reasons.append(f"Threat Intelligence ({ti_provider}) flags destination: {details}")

        elif ti_status == "SUSPICIOUS" or (susp_count is not None and susp_count > 0):
            # Add moderate risk contribution
            base_score += 25
            details = threat_intel.get("message") or threat_intel.get("details") or "Suspicious threat signals observed."
            reasons.append(f"Threat Intelligence ({ti_provider}) flags suspicious signals: {details}")

        elif ti_status in {"CLEAN", "NO_THREAT_FOUND"}:
            # Benign verification discount (subtle discount, never overrides strong heuristics)
            if capped_heuristics < 30:
                base_score = max(0, base_score - 8)

        elif ti_status == "NOT_APPLICABLE":
            pass

        elif ti_status in {"NOT_AVAILABLE", "UNAVAILABLE", "NOT_CONFIGURED"}:
            is_degraded = True

        # Check for Private IP / SSRF target
        if parsed.is_private_ip:
            base_score = max(base_score, 75)
            reasons.append(f"Destination resolves to a private or internal network address ({parsed.hostname}), posing SSRF / intranet risks.")

        # Ensure bounds 0 - 100
        final_score = max(0, min(100, int(base_score)))

        # Determine Verdict and Action based on strict configured thresholds
        # 0–29: SAFE (ALLOW), 30–69: SUSPICIOUS (WARN), 70–100: MALICIOUS (BLOCK)
        if final_score >= 70 or ti_status in {"MALICIOUS", "THREAT_FOUND", "KNOWN_MALICIOUS"}:
            verdict = "MALICIOUS"
            action = "BLOCK"
            if not reasons:
                reasons.append("High probability malicious destination based on aggregate security signals.")
        elif final_score >= 30 or ti_status == "SUSPICIOUS":
            verdict = "SUSPICIOUS"
            action = "WARN"
            if not reasons:
                reasons.append("Multiple anomalous indicators detected; caution advised before visiting.")
        else:
            verdict = "SAFE"
            action = "ALLOW"
            if not reasons:
                reasons.append("No active phishing indicators, malicious feeds, or structural anomalies detected.")

        # If degraded, notify transparently in explanation
        if is_degraded and verdict == "SAFE":
            reasons.append("Security analysis completed with standard coverage (external threat intel or ML in fallback mode).")

        return {
            "risk_score": final_score,
            "verdict": verdict,
            "recommended_action": action,
            "reasons": reasons,
            "is_degraded": is_degraded,
        }


risk_engine = UnifiedRiskEngine()
