# QRadar — Real-Time Quishing Detection & Defense System

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Scikit-Learn](https://img.shields.io/badge/ML-Random%20Forest%2018--Feature-F7931E?style=flat&logo=scikitlearn)](https://scikit-learn.org)
[![OpenCV](https://img.shields.io/badge/Computer%20Vision-OpenCV%20QR-5C3EE8?style=flat&logo=opencv)](https://opencv.org)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter%203-02569B?style=flat&logo=flutter)](https://flutter.dev)
[![Docker](https://img.shields.io/badge/Container-Docker%20Compose-2496ED?style=flat&logo=docker)](https://www.docker.com)
[![Tests](https://img.shields.io/badge/Tests-58%20Passing%20(100%25)-success?style=flat)](./backend/tests)

> **QRadar** is an authoritative, defense-in-depth cybersecurity platform designed to detect and defend against **Quishing (QR Code Phishing)** attacks in real time. It intercepts the physical and digital scanning workflow, evaluating destinations across **Heuristics, Machine Learning, and Threat Intelligence** before users navigate to potentially malicious sites.

---

## 1. Problem Statement & Threat Model

Attackers routinely replace legitimate QR codes in public spaces (e.g., parking meters, restaurant menus, payment counters, transit stations, MFA enrollment flyers) with malicious codes. When scanned, these malicious codes redirect victims to:
- **Credential Harvesting Portals** (spoofing PayPal, Google, Microsoft, Apple, Banks)
- **Rogue IP Servers** hosting exploit kits and phishing forms
- **Obfuscated / Cloaked URL Shorteners** concealing malicious infrastructure
- **Dangerous URI Scheme Execution** (`javascript:`, `data:`, `blob:`, `intent:`, `file:`, `vbscript:`, `content:`)
- **Internal Network Pivoting / SSRF Targets** (`127.0.0.1`, `192.168.x.x`, `10.x.x.x`, `169.254.x.x`)

### The QRadar Architectural Guarantee
QRadar acts as an **authoritative security proxy** between the physical QR code and the web browser:
1. **Single Authoritative Engine**: The FastAPI backend is the *sole* authoritative security engine. Mobile clients, web interfaces, and third-party consumers **never** compute risk scores, ML probabilities, heuristics, or verdicts independently.
2. **Strict Zero URL Auto-Open Policy**: Destinations are **never** automatically launched in a browser.
   - **`SAFE` (0–29)**: Requires explicit user click to confirm opening.
   - **`SUSPICIOUS` (30–69)**: Intercepted by a prominent confirmation warning modal requiring conscious user override.
   - **`MALICIOUS` (70–100)**: Navigation is strictly blocked. No open action is permitted.

---

## 2. System Architecture & Authoritative Data Flow

```
+-------------------------------------------------------------------------------+
|                       CLIENT INTERFACES (MOBILE & WEB UI)                     |
|                                                                               |
|  [ Live Camera Viewfinder ]      [ Image / Gallery Picker ]   [ Manual Input] |
|              \                               /                      /         |
|               \                             /                      /          |
|                +---------------------------+----------------------+           |
|                                            |                                  |
|                             REST API / Multipart Upload                       |
+--------------------------------------------|----------------------------------+
                                             v
+-------------------------------------------------------------------------------+
|                        FASTAPI AUTHORITATIVE SECURITY ENGINE                  |
|                                                                               |
|  +--------------------+     +---------------------+     +------------------+  |
|  |  LAYER 1:          |     |  LAYER 2:           |     |  LAYER 3:        |  |
|  |  QR Decoder &      | --> |  12 Heuristic       | --> |  Random Forest   |  |
|  |  URL Analyzer      |     |  Security Signals   |     |  18-Feature ML   |  |
|  +--------------------+     +---------------------+     +------------------+  |
|            |                           |                          |           |
|     (Traps dangerous                   | (Typosquatting           | (18-feat  |
|      schemes & private                 |  homoglyphs, IP host,    |  vector:  |
|      IP / SSRF hosts)                  |  shortener, @ trick)     |  0.0-1.0) |
|            \                           |                          /           |
|             \                          v                         /            |
|              +--------------->  LAYER 4: Threat Intel   <-------+             |
|                                 (GSB / VirusTotal / Mock)                     |
|                                 (SQLite TTL Cache 24h)                        |
|                                        |                                      |
|                                        v                                      |
|                             LAYER 5: Multi-Layer Risk Engine                  |
|                                (Risk Score: 0 - 100)                          |
|                                (SAFE / SUSPICIOUS / MALICIOUS)                |
|                                        |                                      |
|                                        v                                      |
|                             LAYER 6: Persistence & Analytics                  |
|                                (SQLite Scan Logs & Dashboard)                 |
+----------------------------------------|--------------------------------------+
                                         v
+-------------------------------------------------------------------------------+
|                            JSON SECURITY EVALUATION                           |
|                                        |                                      |
|                                        v                                      |
|  +-------------------------------------------------------------------------+  |
|  |                        EXPLAINABLE CLIENT PRESENTATION                  |  |
|  |  • Animated Risk Score Radial Gauge (0-100)                             |  |
|  |  • Authoritative Verdict Badge (SAFE / SUSPICIOUS / MALICIOUS)          |  |
|  |  • Plain-English Threat Reasons & Extracted Evidence                    |  |
|  |  • 12 Heuristic Signal Breakdown (Triggered vs Clean)                   |  |
|  |  • Machine Learning Probability (Phishing vs Legitimate)                |  |
|  |  • Threat Intelligence Provider Status & Detection Count                |  |
|  |  • Action Gate: ALLOW (Confirm) / WARN (Confirm Gate) / BLOCK (Blocked) |  |
|  +-------------------------------------------------------------------------+  |
+-------------------------------------------------------------------------------+
```

---

## 3. Machine Learning Pipeline & 18-Feature Architecture

### 3.1 Dataset Provenance & Preprocessing
The machine learning training pipeline utilizes a curated, balanced dataset of **4,515 verified URLs** with rigorous provenance tracking:
- **Benign Samples (50.5%)**: Extracted from the authoritative [Tranco Top Sites](https://tranco-list.eu/) ranking feed (`tranco_top_benign`).
- **Phishing Samples (49.5%)**: Extracted from active, community-verified [PhishTank](https://phishtank.org/) feeds (`phishtank_verified_feed`) and targeted synthetic quishing patterns (`synthetic_quishing_vector`).

**Data Preprocessing**:
- Strict URL normalization and schema validation.
- De-duplication and registered root-domain extraction.
- **Group-Aware Splitting**: Uses `GroupShuffleSplit` on registered domains (80% train, 20% test) to enforce **zero domain overlap / data leakage** between training and holdout evaluation sets.

### 3.2 18-Feature Lexical & Structural Vector
The feature extraction logic is shared with 100% parity between training (`ml/src/feature_extraction.py`) and live inference (`backend/app/services/ml_engine.py`):

| # | Feature Name | Type | Description |
|---|---|---|---|
| 1 | `url_length` | Integer | Total character count of full URL string |
| 2 | `hostname_length` | Integer | Character count of network authority / domain |
| 3 | `path_length` | Integer | Character count of URL path component |
| 4 | `query_length` | Integer | Character count of URL query parameters |
| 5 | `num_dots` | Integer | Count of `.` characters across entire URL |
| 6 | `num_hyphens` | Integer | Count of `-` characters across entire URL |
| 7 | `num_underscores` | Integer | Count of `_` characters across entire URL |
| 8 | `num_slashes` | Integer | Count of `/` separator characters |
| 9 | `num_question_marks` | Integer | Count of `?` query initiator characters |
| 10 | `num_equal_signs` | Integer | Count of `=` query key-value separators |
| 11 | `num_at_symbols` | Integer | Count of `@` userinfo authority characters |
| 12 | `num_percent_signs` | Integer | Count of `%` URL encoding characters |
| 13 | `num_digits` | Integer | Count of numeric characters `0-9` |
| 14 | `num_subdomains` | Integer | Number of subdomain hierarchy levels |
| 15 | `is_https` | Binary (0/1) | Whether protocol scheme is encrypted HTTPS |
| 16 | `has_ip_host` | Binary (0/1) | Whether host authority is a raw IPv4/IPv6 address |
| 17 | `num_sensitive_keywords` | Integer | Occurrences of tokens: `login`, `verify`, `account`, `bank`, `secure`, `update`, `wallet`, `signin` |
| 18 | `shannon_entropy` | Float | Calculated character entropy of the URL string: $H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$ |

### 3.3 Model Training & True Measured Metrics
- **Model**: Scikit-Learn `RandomForestClassifier` (100 estimators, `max_depth=None`, `class_weight='balanced'`).
- **Artifacts**: Serialized model (`ml/models/phishing_rf_model.joblib`) and metadata schema (`ml/models/model_metadata.json`).
- **Holdout Test Evaluation (982 samples, 0 domain leakage)**:

| Metric | Measured Score | Details |
|---|---|---|
| **Holdout Accuracy** | **99.59%** | 978 correct / 982 total test samples |
| **Precision** | **99.38%** | 482 True Positives / (482 TP + 3 FP) |
| **Recall (Sensitivity)** | **99.79%** | 482 True Positives / (482 TP + 1 FN) |
| **F1-Score** | **0.9959** | Harmonic mean of Precision & Recall |
| **ROC-AUC** | **1.0000** | Area Under Receiver Operating Characteristic Curve |
| **Full Dataset Accuracy** | **99.91%** | 4,511 correct / 4,515 total samples |

**Confusion Matrix (Holdout Test Set)**:
- **True Negatives (TN)**: 496
- **False Positives (FP)**: 3
- **False Negatives (FN)**: 1
- **True Positives (TP)**: 482

---

## 4. The 12 Deterministic Heuristic Signals

QRadar evaluates 12 independent security heuristics, providing granular scoring contributions and plain-English explanations:

| # | Indicator Code | Default Weight | Category | Trigger Condition & Explanation |
|---|---|---|---|---|
| 1 | `HTTPS_CHECK` | +8 pts | Transport | Scheme is unencrypted `http://`, vulnerable to MITM interception. |
| 2 | `IP_ADDRESS_HOST` | +28 pts | Host Structure | Destination is a raw IPv4 or IPv6 address instead of a registered domain name. |
| 3 | `URL_SHORTENER` | +18 pts | Obfuscation | Domain is a known shortening service (`bit.ly`, `tinyurl.com`, `t.co`, `cutt.ly`, etc.) concealing true destination. |
| 4 | `USERINFO_TRICK` | +32 pts | Evasion | URL contains an `@` symbol in authority to trick victims into misreading the host (`paypal.com@evil.com`). |
| 5 | `EXCESSIVE_SUBDOMAINS` | +14 pts | DNS Structure | Domain contains $\ge 3$ subdomain levels (e.g. `login.secure.update.bank.com`). |
| 6 | `UNUSUAL_URL_LENGTH` | +10 pts | Structure | URL length exceeds 80 characters (mild) or 120 characters (+10 pts). |
| 7 | `EXCESSIVE_SPECIAL_CHARS` | +10 pts | Structure | URL contains $\ge 5$ hyphens, underscores, or delimiter characters. |
| 8 | `SUSPICIOUS_ENCODING` | +18 pts | Obfuscation | Contains double percent-encoding (`%2520`) or hex path traversal tokens (`%2e%2e`). |
| 9 | `SUSPICIOUS_PORT` | +16 pts | Network | URL specifies non-standard web ports (`:8080`, `:8443`, `:8888`, `:2082`, `:2083`, `:7080`). |
| 10 | `PUNYCODE_IDN` | +22 pts | Homograph | Host uses Punycode (`xn--...`) for internationalized homoglyph spoofing. |
| 11 | `SUSPICIOUS_KEYWORDS` | +15 pts | Semantic | Path or query parameters contain sensitive targets (`login`, `verify`, `account`, `wallet`, `bank`). |
| 12 | `LOOKALIKE_TYPOSQUATTING` | +35 pts | Brand Defense | Levenshtein edit distance $\le 2$ or 1337-speak character substitutions against protected high-profile brands (PayPal, Google, Apple, Microsoft, Amazon, Netflix, Chase, Bank of America, Binance, Coinbase, etc.). |

---

## 5. Threat Intelligence Engine & SQLite TTL Caching

QRadar provides a pluggable threat intelligence layer supporting **Google Safe Browsing v4**, **VirusTotal v3**, and a zero-dependency **Local Threat Engine (Offline DB)**:

### 5.1 Standardized Threat Intelligence States
All providers map strictly into one of seven normalized states:
- `MALICIOUS`: Confirmed threat found in security blacklist or threat intelligence feed.
- `CLEAN`: Queried provider explicitly checked the entity and found no malicious indicators.
- `SUSPICIOUS`: Provider flagged suspicious attributes or low reputation.
- `NO_RECORD`: URL/Domain is valid, but the external provider has no prior telemetry on it.
- `NOT_AVAILABLE`: Provider timed out or network connectivity failed (gracefully degraded).
- `NOT_CONFIGURED`: API key was not provided in `.env` (gracefully degraded).
- `NOT_APPLICABLE`: Payload is not a web URL (e.g., WiFi, UPI, vCard, plain text).

### 5.2 SQLite TTL Caching
To minimize external API quota consumption and ensure sub-second response times:
- Cached in database table `ThreatIntelCache` with composite key `(provider, url_hash)`.
- Default TTL is **24 hours** (configurable via `THREAT_INTEL_CACHE_TTL_HOURS`).
- Expired cache entries are automatically evicted or refreshed upon subsequent lookups.

---

## 6. Multi-Layer Risk Scoring Engine

The Risk Engine synthesizes signals from all four detection layers into an explainable integer score $R \in [0, 100]$:

### 6.1 Mathematical Formulation
$$\text{Base Risk} = \min(55, \sum H_i) + \text{round}(35 \times P_{\text{ML}}) + \text{TI Contribution}$$

Where:
- $\sum H_i$: Sum of triggered heuristic signal weights (capped at 55).
- $P_{\text{ML}}$: Random Forest phishing probability ($0.0 \le P_{\text{ML}} \le 1.0$).
- $\text{TI Contribution}$:
  - `MALICIOUS`: $+88$ pts
  - `SUSPICIOUS`: $+25$ pts
  - `CLEAN`: $-8$ pts (safety discount, only applied when heuristics are clean)
  - `NO_RECORD` / `NOT_AVAILABLE` / `NOT_CONFIGURED`: $+0$ pts

### 6.2 Deterministic Precedence Overrides
To ensure mission-critical safety, the following rules take strict precedence over raw scoring:
1. **Dangerous Schemes**: `javascript:`, `file:`, `data:`, `blob:`, `intent:`, `vbscript:` $\rightarrow$ **Risk Score: 98, Verdict: MALICIOUS, Action: BLOCK**.
2. **Confirmed Malicious Threat Intel**: Known threat feed hit $\rightarrow$ **Risk Score: $\ge 88$, Verdict: MALICIOUS, Action: BLOCK**.
3. **SSRF / Private IP Targets**: Host points to private RFC 1918 or loopback IP $\rightarrow$ **Risk Score: $\ge 75$, Verdict: MALICIOUS, Action: BLOCK**.
4. **Strong Heuristics Dominance**: If heuristics score $\ge 30$, low ML probability cannot suppress the verdict to `SAFE`.

### 6.3 Authoritative Verdict Thresholds
- **`0 – 29` : `SAFE` $\rightarrow$ `ALLOW`** (User may open after confirmation prompt)
- **`30 – 69` : `SUSPICIOUS` $\rightarrow$ `WARN`** (Requires explicit confirmation warning gate)
- **`70 – 100` : `MALICIOUS` $\rightarrow$ `BLOCK`** (Strictly blocked, zero auto-open)

---

## 7. Security Hardening & Privacy Defenses

- **SSRF & DNS Rebinding Protection**: Traps loopback (`127.0.0.0/8`, `::1`), private RFC 1918 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), Carrier-Grade NAT (`100.64.0.0/10`), link-local (`169.254.0.0/16`, `fe80::/10`), multicast (`224.0.0.0/4`), and `localhost`.
- **In-Memory Rate Limiting**: Enforces rate limiting on `/api/v1/scan/*` endpoints (60 req/min per IP by default), returning `HTTP 429 Too Many Requests` with a `Retry-After` header.
- **Privacy & Data Retention**: Configurable `RETENTION_DAYS` (default 30 days) automatically purges older scan records. Sensitive credential query parameters (`password`, `token`, `key`, `auth`) are stripped from stored non-malicious scans.

---

## 8. Deployment & Online Configuration

### 8.1 Online Website Architecture
QRadar is fully configured to operate as a real online website. The frontend and backend can be hosted together or deployed to separated domains:

- **Frontend Domain Example**: `https://qradar.yourdomain.com`
- **Backend API Domain Example**: `https://api.qradar.yourdomain.com`

```
User Browser
    ↓
QRadar Frontend (HTTPS)
    ↓ API Requests
FastAPI Backend (Authoritative Security Engine)
    ├── Layer 1: URL Analyzer & SSRF Guard
    ├── Layer 2: 12 Heuristic Threat Rules
    ├── Layer 3: Random Forest Machine Learning (18 features)
    ├── Layer 4: Live Threat Intelligence (VirusTotal / Google Safe Browsing)
    └── Layer 5: Unified Risk Engine (0-100 Scorer)
    ↓
SQLite Database (Persistent Scans, Cache & Analytics)
    ↓
Results, History Logs, and Dashboard
```

### 8.2 Production Environment Configuration (.env)
Copy `backend/.env.example` to `backend/.env` and configure your production parameters:

```bash
# Environment
ENVIRONMENT=production
DEBUG=False

# Database
DATABASE_URL=sqlite+aiosqlite:///./qradar.db
SYNC_DATABASE_URL=sqlite:///./qradar.db

# CORS Configuration (Set your exact frontend production domain(s))
CORS_ORIGINS=https://qradar.yourdomain.com,https://app.yourdomain.com

# Threat Intelligence (VirusTotal v3 or Google Safe Browsing v4)
THREAT_INTEL_PROVIDER=virustotal
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
GSB_API_KEY=your_google_safe_browsing_api_key_here
THREAT_INTEL_TIMEOUT_SECONDS=3.0
THREAT_INTEL_CACHE_TTL_HOURS=24

# Security Guards
RESOLVE_SHORTENERS=False
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
```

### 8.3 Running the Application

#### Option A: Production Server (HTTPS / Reverse Proxy)
Run Uvicorn behind a production reverse proxy (Nginx, Caddy, Cloudflare) terminating TLS:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Option B: Local Development
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --app-dir . --host 127.0.0.1 --port 8000 --reload
```
- **Web Application & Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 9. Safe Evaluator Demo Test Cases

High-resolution generated QR images are available in [`demo_assets/`](file:///c:/Users/banda/OneDrive/QRader%202/demo_assets):

| Asset | Target Payload | Expected Verdict | Primary Detected Signals |
|---|---|---|---|
| `1_safe_google_qr.png` | `https://www.google.com/search?q=cybersecurity+research` | **SAFE (Risk: 0)** | Valid HTTPS, top reputation, clean heuristics |
| `2_typosquatting_paypal_qr.png` | `http://paypa1-account-verification.xyz/login.php` | **MALICIOUS (Risk: 90)** | Typosquatting (PayPal), homoglyph `1` $\rightarrow$ `l`, sensitive keywords, ML: 100% |
| `3_ip_address_host_qr.png` | `http://192.168.1.105:8080/secure/paypal_login.htm` | **MALICIOUS (Risk: 89)** | Direct IP host, non-standard port :8080, SSRF alert, threat feed match |
| `4_userinfo_at_trick_qr.png` | `https://paypal.com@evil-phishing-gate.ru/login` | **MALICIOUS (Risk: 88)** | Userinfo `@` evasion trick, ML phishing score: 92% |
| `5_dangerous_scheme_qr.png` | `javascript:alert('Quishing Attack Blocked by QRadar')` | **MALICIOUS (Risk: 98)** | Dangerous execution scheme trapped, local execution prevented |
| `6_url_shortener_qr.png` | `http://bit.ly/3xSampleShortener` | **SUSPICIOUS (Risk: 34)** | Shortener cloaking, anomalous destination, warning gate |
| `7_multi_qr_sample.png` | Dual QR code image | **Interactive Disambiguation** | Disambiguates into QR #1 (PayPal Lookalike) & QR #2 (Google) |

---

## 10. Test & Verification Matrix

Run the automated test suite across all modules:
```bash
python -m pytest backend/tests -v
```

| Test Suite / Component | Scope | Tests | Status |
|---|---|---|---|
| `test_online_website_e2e.py` | 18 Required Online Tests: Health, Scanner, Heuristics, ML, TI, Cache, SSRF, CORS, Rate Limiting | 18 | **18 / 18 PASS** |
| `test_api_endpoints.py` | Health check, scan endpoints, image upload, history pagination, dashboard | 6 | **6 / 6 PASS** |
| `test_heuristics.py` | Levenshtein distance, homoglyphs, all 12 individual indicators | 13 | **13 / 13 PASS** |
| `test_ml_engine.py` | Shannon entropy, 18-feature vector extraction, inference, non-web payloads | 4 | **4 / 4 PASS** |
| `test_risk_engine.py` | 0–29 / 30–69 / 70–100 boundary thresholds, precedence rules, overrides | 7 | **7 / 7 PASS** |
| `test_threat_intel_scenarios.py` | 7 normalized TI states, timeouts, rate limits, SQLite TTL caching | 14 | **14 / 14 PASS** |
| `test_offline_resilience.py` | Offline DB fallback, complete pipeline scan without internet, static assets | 4 | **4 / 4 PASS** |
| `test_ssrf_and_ratelimit.py` | Private/loopback IPv4 & IPv6, hop-limited resolution, in-memory rate limiter | 5 | **5 / 5 PASS** |
| `test_url_analyzer.py` | Scheme trapping, contact formats, IPv6 parsing, public domain resolution | 5 | **5 / 5 PASS** |
| **Total Automated Tests** | **Full End-to-End Online Security Engine Verification** | **76** | **76 / 76 PASS (100%)** |

---

## 11. Known Limitations & Deployment Notes

1. **Client-Side Rendering in Headless Mode**: Headless web page visual inspection (DOM rendering, screenshot similarity comparison) requires browser automation (e.g. Playwright) not enabled in lightweight microservices.
2. **DNS Record WHOIS Telemetry**: Domain age lookups require WHOIS network queries which are subject to external rate-limiting and timeouts.
3. **Active Link Traversal**: Active multi-hop redirect following is disabled by default to eliminate Server-Side Request Forgery (SSRF) risks and prevent alerting attackers.

---

## 12. Academic Integrity & License

Developed as a University Capstone Project in Advanced Defensive Cybersecurity, Machine Learning, and Mobile Application Development. Designed for defensive educational demonstrations, security research, and real-world quishing defense.

