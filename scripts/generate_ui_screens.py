import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "doc_assets"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------------
# Helper: University Logo / Emblem
# -------------------------------------------------------------------
def generate_university_logo():
    fig, ax = plt.subplots(figsize=(6, 2.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Draw stylized university crest
    # Wreath leaves (olive)
    ax.plot([14, 11, 10, 11, 14, 18], [15, 20, 26, 31, 35, 37], color='#D97706', lw=2)
    ax.plot([30, 33, 34, 33, 30, 26], [15, 20, 26, 31, 35, 37], color='#D97706', lw=2)
    # Pillars
    for px in [16, 22, 28]:
        p = FancyBboxPatch((px-1.5, 12), 3, 16, boxstyle="square,pad=0", edgecolor='#1E3A8A', facecolor='#1E3A8A')
        ax.add_patch(p)
    # Mortarboard cap
    cap = patches.Polygon([[14, 30], [22, 34], [30, 30], [22, 26]], closed=True, edgecolor='#DC2626', facecolor='#DC2626')
    ax.add_patch(cap)
    # Star arc
    for sx, sy in [(13, 38), (17, 39.5), (22, 40), (27, 39.5), (31, 38)]:
        star = patches.RegularPolygon((sx, sy), numVertices=5, radius=1.2, orientation=0, facecolor='#D97706', edgecolor='#D97706')
        ax.add_patch(star)

    # University text
    ax.text(38, 26, "MALLA REDDY", fontsize=20, weight='heavy', color='#1E3A8A', fontfamily='sans-serif')
    ax.text(38, 13, "UNIVERSITY", fontsize=18, weight='heavy', color='#1E3A8A', fontfamily='sans-serif')
    ax.text(38, 4, "(Telangana State Private Universities Act No.13 of 2020 and G.O.Ms.No.14)", fontsize=6.5, color='#475569')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "malla_reddy_logo.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("University Logo generated.")

# -------------------------------------------------------------------
# SCREEN 1: QRadar Home Overview Hub
# -------------------------------------------------------------------
def generate_screen1():
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#0B1220')
    ax.set_facecolor('#0B1220')

    # Topbar
    topbar = Rectangle((0, 90), 100, 10, facecolor='#162235', edgecolor='#334155')
    ax.add_patch(topbar)
    ax.text(5, 95, "🛡️ QRadar — Real-Time Quishing Detection & Defense", fontsize=11, weight='bold', color='#38BDF8', va='center')
    ax.text(95, 95, "● ENGINE ONLINE (FastAPI)", fontsize=8, weight='bold', color='#22C55E', va='center', ha='right')

    # Hero card
    hero = FancyBboxPatch((5, 52), 90, 34, boxstyle="round,pad=1.2,rounding_size=2",
                          facecolor='#162235', edgecolor='#38BDF8', lw=1.5)
    ax.add_patch(hero)
    ax.text(8, 79, "DEFENSE-IN-DEPTH QUISHING SECURITY GATEWAY", fontsize=8.5, weight='bold', color='#38BDF8')
    ax.text(8, 72, "Scan a QR code before you trust the destination.", fontsize=14, weight='bold', color='#F8FAFC')
    ax.text(8, 64, "Intercept physical & digital QR codes across Heuristics, 18-Feature Random Forest ML (99.59%),\nand Live Threat Intelligence before navigating to untrusted endpoints.", fontsize=8.5, color='#94A3B8')

    # Badges
    badges = [("12 Security Heuristics", "#38BDF8"), ("18-Feature ML Model", "#A855F7"), ("Zero URL Auto-Open Policy", "#22C55E"), ("SSRF Protection", "#F59E0B")]
    for i, (b_txt, b_col) in enumerate(badges):
        bp = FancyBboxPatch((8 + i*22, 55), 20, 5, boxstyle="round,pad=0.4,rounding_size=1", facecolor='#1E293B', edgecolor=b_col, lw=1)
        ax.add_patch(bp)
        ax.text(18 + i*22, 57.5, b_txt, ha='center', va='center', fontsize=7.2, weight='bold', color=b_col)

    # 3 Action Cards (Bottom)
    cards = [
        ("Live Camera Scanner", "Inspect physical QR codes in real time with laser guide", "#38BDF8", 5),
        ("Upload QR Code Image", "Drop PNG/JPG/WebP files or select from gallery", "#A855F7", 36),
        ("Manual URL Threat Check", "Directly evaluate raw web destinations & schemes", "#10B981", 67)
    ]
    for title, desc, col, x in cards:
        cp = FancyBboxPatch((x, 10), 28, 36, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#334155', lw=1.2)
        ax.add_patch(cp)
        # Header icon line
        hp = FancyBboxPatch((x+2, 38), 24, 6, boxstyle="round,pad=0.4,rounding_size=1", facecolor='#1E293B', edgecolor=col, lw=1)
        ax.add_patch(hp)
        ax.text(x+14, 41, title, ha='center', va='center', fontsize=8.5, weight='bold', color=col)
        ax.text(x+14, 26, desc, ha='center', va='center', fontsize=7.8, color='#94A3B8')
        # Button
        btn = FancyBboxPatch((x+4, 13), 20, 6, boxstyle="round,pad=0.4,rounding_size=1", facecolor=col, edgecolor=col)
        ax.add_patch(btn)
        ax.text(x+14, 16, "Launch Scanner →", ha='center', va='center', fontsize=7.8, weight='bold', color='#0B1220')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "screen1_home_hub.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Screen 1 generated.")

# -------------------------------------------------------------------
# SCREEN 2: Live QR Scanner & Dropzone
# -------------------------------------------------------------------
def generate_screen2():
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#0B1220')
    ax.set_facecolor('#0B1220')

    # Topbar
    topbar = Rectangle((0, 90), 100, 10, facecolor='#162235', edgecolor='#334155')
    ax.add_patch(topbar)
    ax.text(5, 95, "📷 Live Scanner & Ingestion Hub", fontsize=11, weight='bold', color='#38BDF8', va='center')

    # Viewfinder Card (Left)
    vf = FancyBboxPatch((5, 12), 43, 72, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#334155', lw=1.2)
    ax.add_patch(vf)
    ax.text(26.5, 79, "Live Camera Viewfinder", ha='center', fontsize=10, weight='bold', color='#F8FAFC')
    
    # Camera area
    cam = FancyBboxPatch((9, 28), 35, 46, boxstyle="square,pad=0", facecolor='#0F172A', edgecolor='#38BDF8', lw=1.5)
    ax.add_patch(cam)
    # Targeting reticle
    for rx, ry, dx, dy in [(12, 70, 5, 0), (12, 70, 0, -5), (41, 70, -5, 0), (41, 70, 0, -5),
                           (12, 32, 5, 0), (12, 32, 0, 5), (41, 32, -5, 0), (41, 32, 0, 5)]:
        ax.plot([rx, rx+dx], [ry, ry+dy], color='#38BDF8', lw=2)
    # Laser beam
    ax.plot([10, 43], [51, 51], color='#22D3EE', lw=2.5, linestyle='-')
    ax.text(26.5, 47, "ALIGN QR CODE WITHIN FRAME", ha='center', fontsize=7, color='#38BDF8', weight='bold')

    # Toggle camera button
    btn_cam = FancyBboxPatch((13, 16), 27, 7, boxstyle="round,pad=0.5,rounding_size=1", facecolor='#38BDF8', edgecolor='#38BDF8')
    ax.add_patch(btn_cam)
    ax.text(26.5, 19.5, "Start Video Stream", ha='center', va='center', fontsize=8.5, weight='bold', color='#0B1220')

    # Drag-Drop & Test Section (Right)
    dd_box = FancyBboxPatch((52, 48), 43, 36, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#38BDF8', lw=1.5, linestyle='--')
    ax.add_patch(dd_box)
    ax.text(73.5, 74, "📁 Drag & Drop QR Image", ha='center', fontsize=10.5, weight='bold', color='#38BDF8')
    ax.text(73.5, 66, "Drop QR Code image file here\nor browse from local directory", ha='center', fontsize=8, color='#94A3B8')
    ax.text(73.5, 57, "[ Browse File / Choose Photo ]", ha='center', fontsize=8, weight='bold', color='#22D3EE')

    # Sample Test QRs
    test_box = FancyBboxPatch((52, 12), 43, 32, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#334155', lw=1.2)
    ax.add_patch(test_box)
    ax.text(73.5, 39, "⚡ Instant Test Samples (Click to Evaluate)", ha='center', fontsize=9, weight='bold', color='#F8FAFC')

    sample_tests = [
        ("Safe Google HTTPS", "#16A34A", 32),
        ("Typosquatting PayPal (paypa1-verify.xyz)", "#DC2626", 24),
        ("Raw IP Address Host (http://192.168.1.50/login)", "#EA580C", 16)
    ]
    for s_txt, s_col, sy in sample_tests:
        sp = FancyBboxPatch((55, sy-2.5), 37, 5.5, boxstyle="round,pad=0.4,rounding_size=0.8", facecolor='#1E293B', edgecolor=s_col, lw=1)
        ax.add_patch(sp)
        ax.text(57, sy+0.25, s_txt, fontsize=7.2, color='#F8FAFC', weight='bold', va='center')
        ax.text(90, sy+0.25, "TEST", fontsize=7, color=s_col, weight='bold', va='center', ha='right')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "screen2_live_scanner.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Screen 2 generated.")

# -------------------------------------------------------------------
# SCREEN 3: Explainable Threat Evaluation Result (Risk Gauge)
# -------------------------------------------------------------------
def generate_screen3():
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#0B1220')
    ax.set_facecolor('#0B1220')

    # Topbar
    topbar = Rectangle((0, 90), 100, 10, facecolor='#162235', edgecolor='#334155')
    ax.add_patch(topbar)
    ax.text(5, 95, "🔍 Security Scan Result & Authoritative Verdict", fontsize=11, weight='bold', color='#38BDF8', va='center')

    # Main Result Card
    card = FancyBboxPatch((8, 10), 84, 75, boxstyle="round,pad=1.5,rounding_size=2.5", facecolor='#162235', edgecolor='#EF4444', lw=2)
    ax.add_patch(card)

    # Risk Gauge Circle (Left)
    gauge_circle = Circle((28, 55), 18, facecolor='#1E293B', edgecolor='#EF4444', lw=4.5)
    ax.add_patch(gauge_circle)
    ax.text(28, 60, "95", ha='center', va='center', fontsize=26, weight='heavy', color='#EF4444')
    ax.text(28, 48, "/ 100\nRISK SCORE", ha='center', va='center', fontsize=7.5, weight='bold', color='#94A3B8')

    # Verdict Badge & Target details (Right)
    badge = FancyBboxPatch((50, 68), 38, 9, boxstyle="round,pad=0.5,rounding_size=1.2", facecolor='#450A0A', edgecolor='#EF4444', lw=1.5)
    ax.add_patch(badge)
    ax.text(69, 72.5, "VERDICT: MALICIOUS (BLOCK)", ha='center', va='center', fontsize=9.5, weight='bold', color='#EF4444')

    ax.text(50, 62, "Scanned URL Destination:", fontsize=8.5, weight='bold', color='#94A3B8')
    ax.text(50, 56, "http://paypa1-account-verification.xyz/login.php", fontsize=8.5, weight='bold', color='#38BDF8')

    ax.text(50, 48, "Primary Threat Rationale:", fontsize=8.5, weight='bold', color='#94A3B8')
    ax.text(50, 42, "• High-confidence brand typosquatting targeting PayPal", fontsize=8, color='#EF4444')
    ax.text(50, 37, "• Random Forest Phishing Probability: 99.8%", fontsize=8, color='#EF4444')
    ax.text(50, 32, "• Unencrypted HTTP transport exposing credentials", fontsize=8, color='#EF4444')

    # Action Gate Banner (Bottom)
    action_banner = FancyBboxPatch((12, 14), 76, 12, boxstyle="round,pad=0.5,rounding_size=1.2", facecolor='#7F1D1D', edgecolor='#EF4444', lw=1.5)
    ax.add_patch(action_banner)
    ax.text(50, 22, "⛔ ZERO AUTO-OPEN ENFORCED: NAVIGATION IS STRICTLY BLOCKED", ha='center', va='center', fontsize=9, weight='heavy', color='#FEE2E2')
    ax.text(50, 16.5, "This QR destination has been intercepted. The browser will not open this malicious portal.", ha='center', va='center', fontsize=7.5, color='#FCA5A5')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "screen3_evaluation_result.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Screen 3 generated.")

# -------------------------------------------------------------------
# SCREEN 4: Heuristics & 18-Feature ML Breakdown
# -------------------------------------------------------------------
def generate_screen4():
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#0B1220')
    ax.set_facecolor('#0B1220')

    # Topbar
    topbar = Rectangle((0, 90), 100, 10, facecolor='#162235', edgecolor='#334155')
    ax.add_patch(topbar)
    ax.text(5, 95, "📊 Detailed Heuristic & Machine Learning Attribution", fontsize=11, weight='bold', color='#38BDF8', va='center')

    # Heuristic signals card (Left)
    card_h = FancyBboxPatch((5, 10), 43, 75, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#334155', lw=1.2)
    ax.add_patch(card_h)
    ax.text(26.5, 80, "12 Deterministic Heuristic Signals", ha='center', fontsize=9.5, weight='bold', color='#F8FAFC')

    heuristics = [
        ("LOOKALIKE_TYPOSQUATTING", "+35 pts", "#EF4444", "Triggered"),
        ("SUSPICIOUS_KEYWORDS (login)", "+15 pts", "#EF4444", "Triggered"),
        ("HTTPS_CHECK (Unencrypted HTTP)", "+8 pts", "#F59E0B", "Triggered"),
        ("IP_ADDRESS_HOST", "+0 pts", "#22C55E", "Clean"),
        ("USERINFO_TRICK (@ Symbol)", "+0 pts", "#22C55E", "Clean"),
        ("URL_SHORTENER", "+0 pts", "#22C55E", "Clean"),
        ("PUNYCODE_IDN", "+0 pts", "#22C55E", "Clean")
    ]
    for i, (h_name, pts, col, st) in enumerate(heuristics):
        hp = FancyBboxPatch((8, 69 - i*8), 37, 6.2, boxstyle="round,pad=0.3,rounding_size=0.8", facecolor='#1E293B', edgecolor=col, lw=1)
        ax.add_patch(hp)
        ax.text(10, 72.1 - i*8, h_name, fontsize=7.2, color='#F8FAFC', weight='bold')
        ax.text(43, 72.1 - i*8, f"{st} ({pts})", fontsize=7, color=col, weight='bold', ha='right')

    # Machine Learning card (Right)
    card_ml = FancyBboxPatch((52, 10), 43, 75, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#334155', lw=1.2)
    ax.add_patch(card_ml)
    ax.text(73.5, 80, "18-Feature Random Forest Classifier", ha='center', fontsize=9.5, weight='bold', color='#F8FAFC')

    ax.text(56, 73, "Holdout Model Accuracy: 99.59%", fontsize=8.2, weight='bold', color='#10B981')
    ax.text(56, 68, "Phishing Confidence Probability:", fontsize=8, color='#94A3B8')

    # Probability progress bar
    bar_bg = FancyBboxPatch((56, 60), 35, 5, boxstyle="round,pad=0.2,rounding_size=0.5", facecolor='#0F172A', edgecolor='#334155')
    ax.add_patch(bar_bg)
    bar_fill = FancyBboxPatch((56, 60), 34.8, 5, boxstyle="round,pad=0.2,rounding_size=0.5", facecolor='#EF4444', edgecolor='#EF4444')
    ax.add_patch(bar_fill)
    ax.text(73.5, 62.5, "99.8% PHISHING", ha='center', va='center', fontsize=7.2, weight='bold', color='white')

    ax.text(56, 53, "Key Extracted Feature Vector Values:", fontsize=8, weight='bold', color='#38BDF8')
    feat_samples = [
        ("url_length", "47 characters"),
        ("hostname_length", "33 characters"),
        ("shannon_entropy", "4.21 bits/char"),
        ("num_sensitive_keywords", "1 ('login')"),
        ("has_ip_host", "0 (False)"),
        ("is_https", "0 (False)")
    ]
    for i, (f_k, f_v) in enumerate(feat_samples):
        ax.text(56, 46 - i*5.5, f"• {f_k}:", fontsize=7.2, color='#CBD5E1')
        ax.text(90, 46 - i*5.5, f_v, fontsize=7.2, color='#38BDF8', weight='bold', ha='right')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "screen4_heuristic_breakdown.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Screen 4 generated.")

# -------------------------------------------------------------------
# SCREEN 5: Scan History Logs & Incident Audit View
# -------------------------------------------------------------------
def generate_screen5():
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#0B1220')
    ax.set_facecolor('#0B1220')

    # Topbar
    topbar = Rectangle((0, 90), 100, 10, facecolor='#162235', edgecolor='#334155')
    ax.add_patch(topbar)
    ax.text(5, 95, "📋 Scan History & Threat Audit Trail", fontsize=11, weight='bold', color='#38BDF8', va='center')
    ax.text(95, 95, "[ Export CSV Audit Log ]", fontsize=8, weight='bold', color='#10B981', va='center', ha='right')

    # Table Card
    card = FancyBboxPatch((5, 10), 90, 75, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#334155', lw=1.2)
    ax.add_patch(card)

    # Table Header
    th_bg = Rectangle((7, 76), 86, 6, facecolor='#1E293B', edgecolor='#334155')
    ax.add_patch(th_bg)
    ax.text(9, 79, "TIMESTAMP", fontsize=7.2, weight='bold', color='#94A3B8')
    ax.text(25, 79, "DESTINATION TARGET / URL", fontsize=7.2, weight='bold', color='#94A3B8')
    ax.text(62, 79, "SCORE", fontsize=7.2, weight='bold', color='#94A3B8')
    ax.text(73, 79, "VERDICT", fontsize=7.2, weight='bold', color='#94A3B8')
    ax.text(85, 79, "ACTION GATE", fontsize=7.2, weight='bold', color='#94A3B8')

    # Rows
    rows = [
        ("14:02:18", "http://paypa1-account-verification.xyz/login.php", "95", "MALICIOUS", "BLOCK", "#EF4444"),
        ("13:58:45", "https://www.google.com/search?q=cybersecurity", "0", "SAFE", "ALLOW", "#22C55E"),
        ("13:45:10", "http://192.168.1.100/admin/dashboard", "78", "MALICIOUS", "BLOCK", "#EF4444"),
        ("13:20:04", "https://tinyurl.com/fast-promo-offer", "45", "SUSPICIOUS", "WARN", "#F59E0B"),
        ("12:55:33", "javascript:alert('XSS Exploit')", "98", "MALICIOUS", "BLOCK", "#EF4444"),
        ("12:30:19", "https://github.com/malla-reddy-cyber", "5", "SAFE", "ALLOW", "#22C55E"),
        ("12:10:02", "upi://pay?pa=store@bank&pn=Canteen&am=150", "0", "SAFE", "ALLOW", "#22C55E")
    ]
    for i, (ts, url, score, verd, act, col) in enumerate(rows):
        ry = 68 - i*8
        row_bg = Rectangle((7, ry-2), 86, 7, facecolor='#162235' if i%2==0 else '#1E293B', edgecolor='#334155', lw=0.5)
        ax.add_patch(row_bg)
        ax.text(9, ry+1.5, ts, fontsize=7, color='#CBD5E1')
        short_url = url if len(url) < 38 else url[:35] + "..."
        ax.text(25, ry+1.5, short_url, fontsize=7.2, color='#F8FAFC', weight='bold')
        ax.text(64, ry+1.5, score, fontsize=7.2, color=col, weight='bold')
        # Badge
        bp = FancyBboxPatch((72, ry-0.5), 10, 4.5, boxstyle="round,pad=0.2,rounding_size=0.6", facecolor='#1E293B', edgecolor=col, lw=1)
        ax.add_patch(bp)
        ax.text(77, ry+1.8, verd, fontsize=6.2, weight='bold', color=col, ha='center', va='center')
        ax.text(88, ry+1.5, act, fontsize=7, color=col, weight='bold')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "screen5_scan_history.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Screen 5 generated.")

# -------------------------------------------------------------------
# SCREEN 6: Security Analytics Dashboard
# -------------------------------------------------------------------
def generate_screen6():
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#0B1220')
    ax.set_facecolor('#0B1220')

    # Topbar
    topbar = Rectangle((0, 90), 100, 10, facecolor='#162235', edgecolor='#334155')
    ax.add_patch(topbar)
    ax.text(5, 95, "📈 Security Operations Analytics & KPI Center", fontsize=11, weight='bold', color='#38BDF8', va='center')

    # 4 KPI Stat Cards
    kpis = [
        ("TOTAL SCANS", "4,515", "#38BDF8", 5),
        ("THREATS BLOCKED", "948", "#EF4444", 28),
        ("SUSPICIOUS INTERCEPTED", "668", "#F59E0B", 51),
        ("SAFE VERIFIED", "2,899", "#22C55E", 74)
    ]
    for label, val, col, x in kpis:
        kp = FancyBboxPatch((x, 68), 21, 18, boxstyle="round,pad=1,rounding_size=1.5", facecolor='#162235', edgecolor='#334155', lw=1.2)
        ax.add_patch(kp)
        ax.text(x+10.5, 80, label, ha='center', fontsize=7.2, weight='bold', color='#94A3B8')
        ax.text(x+10.5, 72, val, ha='center', fontsize=15, weight='heavy', color=col)

    # 2 Mini charts in dashboard
    # Left Mini Chart: Attack Categories
    c_left = FancyBboxPatch((5, 10), 43, 53, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#334155', lw=1.2)
    ax.add_patch(c_left)
    ax.text(26.5, 57, "Detected Attack Vectors", ha='center', fontsize=9, weight='bold', color='#F8FAFC')
    cat_bars = [("Typosquatting", 35, "#EF4444"), ("IP Addresses", 25, "#F97316"), ("URL Shorteners", 20, "#3B82F6"), ("Dangerous Schemes", 12, "#8B5CF6")]
    for i, (c_label, pct, b_col) in enumerate(cat_bars):
        by = 48 - i*9
        ax.text(8, by+3.5, c_label, fontsize=7.2, color='#CBD5E1')
        ax.text(45, by+3.5, f"{pct}%", fontsize=7.2, color=b_col, weight='bold', ha='right')
        bar_bg = FancyBboxPatch((8, by), 37, 3, boxstyle="round,pad=0.1,rounding_size=0.4", facecolor='#0F172A', edgecolor='#334155')
        ax.add_patch(bar_bg)
        bar_f = FancyBboxPatch((8, by), 37 * (pct/40), 3, boxstyle="round,pad=0.1,rounding_size=0.4", facecolor=b_col, edgecolor=b_col)
        ax.add_patch(bar_f)

    # Right Mini Chart: Real-Time Protection Performance
    c_right = FancyBboxPatch((52, 10), 43, 53, boxstyle="round,pad=1.2,rounding_size=2", facecolor='#162235', edgecolor='#334155', lw=1.2)
    ax.add_patch(c_right)
    ax.text(73.5, 57, "Engine Latency & Scalability", ha='center', fontsize=9, weight='bold', color='#F8FAFC')
    
    metrics = [
        ("QR Decoding Latency", "18 ms", "#10B981"),
        ("12-Heuristic Check", "8 ms", "#10B981"),
        ("18-Feature ML Inference", "14 ms", "#10B981"),
        ("SQLite Threat Cache Hit", "5 ms", "#10B981"),
        ("Holdout Test Accuracy", "99.59%", "#38BDF8"),
        ("Zero Auto-Open Compliance", "100%", "#22C55E")
    ]
    for i, (m_lbl, m_val, m_col) in enumerate(metrics):
        my = 50 - i*6.5
        ax.text(56, my, m_lbl, fontsize=7.5, color='#CBD5E1')
        ax.text(91, my, m_val, fontsize=7.5, color=m_col, weight='bold', ha='right')
        ax.plot([56, 91], [my-1.8, my-1.8], color='#334155', lw=0.6)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "screen6_security_dashboard.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Screen 6 generated.")

# -------------------------------------------------------------------
# SCREEN 7: Threat Intelligence & Settings Panel
# -------------------------------------------------------------------
def generate_screen7():
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#0B1220')
    ax.set_facecolor('#0B1220')

    # Topbar
    topbar = Rectangle((0, 90), 100, 10, facecolor='#162235', edgecolor='#334155')
    ax.add_patch(topbar)
    ax.text(5, 95, "⚙️ Threat Intelligence Configuration & System Settings", fontsize=11, weight='bold', color='#38BDF8', va='center')

    # Settings Card
    card = FancyBboxPatch((8, 10), 84, 75, boxstyle="round,pad=1.5,rounding_size=2.5", facecolor='#162235', edgecolor='#334155', lw=1.2)
    ax.add_patch(card)

    fields = [
        ("VirusTotal v3 API Key:", "••••••••••••••••••••••••••••••••", "ACTIVE / VERIFIED (24h TTL)", "#10B981"),
        ("Google Safe Browsing v4 Key:", "••••••••••••••••••••••••••••••••", "ACTIVE / VERIFIED", "#10B981"),
        ("Threat Intel Cache Duration:", "24 Hours (SQLite Local TTL Engine)", "ENABLED", "#38BDF8"),
        ("ML Decision Engine:", "RandomForestClassifier (18 Features)", "HOLD-OUT ACC: 99.59%", "#38BDF8"),
        ("Zero URL Auto-Open Gate:", "Mandatory Prompt on SAFE; Block on MALICIOUS", "ENFORCED", "#22C55E"),
        ("Data Retention Period:", "30 Days Automatic Log Expiry & Scrubbing", "COMPLIANT", "#F59E0B")
    ]
    for i, (title, val, st, col) in enumerate(fields):
        fy = 74 - i*10
        ax.text(12, fy+3, title, fontsize=8, weight='bold', color='#F8FAFC')
        # Input box
        ib = FancyBboxPatch((12, fy-3.5), 52, 5.5, boxstyle="round,pad=0.3,rounding_size=0.6", facecolor='#1E293B', edgecolor='#334155')
        ax.add_patch(ib)
        ax.text(15, fy-0.7, val, fontsize=7.5, color='#CBD5E1')
        # Status pill
        sp = FancyBboxPatch((67, fy-3.5), 21, 5.5, boxstyle="round,pad=0.3,rounding_size=0.6", facecolor='#1E293B', edgecolor=col)
        ax.add_patch(sp)
        ax.text(77.5, fy-0.7, st, ha='center', fontsize=6.8, weight='bold', color=col)

    # Save Settings Button
    s_btn = FancyBboxPatch((35, 14), 30, 6.5, boxstyle="round,pad=0.4,rounding_size=1", facecolor='#38BDF8', edgecolor='#38BDF8')
    ax.add_patch(s_btn)
    ax.text(50, 17.2, "Save Configuration Settings", ha='center', va='center', fontsize=8.5, weight='bold', color='#0B1220')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "screen7_threat_settings.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Screen 7 generated.")

# -------------------------------------------------------------------
# POSTER PRESENTATION (Matching Page 33 / 41)
# -------------------------------------------------------------------
def generate_poster():
    fig, ax = plt.subplots(figsize=(8.5, 11), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 130)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    # Poster Banner Header
    banner = FancyBboxPatch((3, 110), 94, 16, boxstyle="round,pad=1,rounding_size=1.5", facecolor='#0F172A', edgecolor='#38BDF8', lw=2)
    ax.add_patch(banner)
    ax.text(50, 121, "QRADAR", ha='center', va='center', fontsize=18, weight='heavy', color='#38BDF8')
    ax.text(50, 115, "REAL-TIME QUISHING DETECTION & DEFENSE SYSTEM", ha='center', va='center', fontsize=11, weight='bold', color='white')
    ax.text(50, 111.5, "Malla Reddy University — Department of CSE (Cyber Security)", ha='center', va='center', fontsize=8, color='#94A3B8')

    # Team & Repo bar
    t_box = FancyBboxPatch((3, 99), 45, 9, boxstyle="round,pad=0.5,rounding_size=1", facecolor='#EFF6FF', edgecolor='#3B82F6', lw=1.2)
    ax.add_patch(t_box)
    ax.text(25.5, 105, "PRESENTED BY:", ha='center', fontsize=7.5, weight='bold', color='#1E40AF')
    ax.text(25.5, 101.5, "Banda Priyanka (2411CS040011) & Team", ha='center', fontsize=7.2, weight='bold', color='#0F172A')

    g_box = FancyBboxPatch((52, 99), 45, 9, boxstyle="round,pad=0.5,rounding_size=1", facecolor='#EFF6FF', edgecolor='#3B82F6', lw=1.2)
    ax.add_patch(g_box)
    ax.text(74.5, 105, "GITHUB REPOSITORY:", ha='center', fontsize=7.5, weight='bold', color='#1E40AF')
    ax.text(74.5, 101.5, "https://github.com/bandapriyanka934/QRadar", ha='center', fontsize=7, color='#1E40AF', weight='bold')

    # Left Column: Abstract & Introduction & Architecture
    # Abstract
    ab_box = FancyBboxPatch((3, 76), 45, 21, boxstyle="round,pad=0.8,rounding_size=1.2", facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=1.2)
    ax.add_patch(ab_box)
    ab_hdr = FancyBboxPatch((3, 93), 45, 4, boxstyle="round,pad=0.2,rounding_size=0.6", facecolor='#1E40AF', edgecolor='#1E40AF')
    ax.add_patch(ab_hdr)
    ax.text(25.5, 95, "ABSTRACT", ha='center', va='center', fontsize=8.5, weight='bold', color='white')
    ax.text(5, 84, "QRadar is an authoritative defense system designed to\ndetect and defend against Quishing (QR code phishing).\nBy combining 12 Heuristics, 18-Feature Random Forest\nML (99.59% accuracy), and Threat Intelligence,\nit intercepts dangerous physical and digital QR scans.", fontsize=6.8, color='#334155')

    # Architecture Overview
    arch_box = FancyBboxPatch((3, 20), 45, 54, boxstyle="round,pad=0.8,rounding_size=1.2", facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=1.2)
    ax.add_patch(arch_box)
    arch_hdr = FancyBboxPatch((3, 70), 45, 4, boxstyle="round,pad=0.2,rounding_size=0.6", facecolor='#1E40AF', edgecolor='#1E40AF')
    ax.add_patch(arch_hdr)
    ax.text(25.5, 72, "SYSTEM ARCHITECTURE", ha='center', va='center', fontsize=8.5, weight='bold', color='white')
    
    arch_layers = [
        ("Client Viewfinder & File Ingestion", "#DBEAFE", "#1E40AF"),
        ("FastAPI Gateway & SSRF Guard", "#E0E7FF", "#4338CA"),
        ("12 Heuristic Threat Rules", "#FEF3C7", "#D97706"),
        ("18-Feature Random Forest ML", "#FEE2E2", "#DC2626"),
        ("Threat Intel Engine & SQLite Cache", "#EDE9FE", "#7C3AED"),
        ("Multi-Layer Risk Engine (0-100)", "#DCFCE7", "#16A34A"),
        ("Strict Zero Auto-Open Enforcer", "#0F172A", "#38BDF8")
    ]
    for i, (l_txt, bg_c, fg_c) in enumerate(arch_layers):
        lp = FancyBboxPatch((5, 62 - i*6.5), 41, 5, boxstyle="round,pad=0.3,rounding_size=0.6", facecolor=bg_c, edgecolor=fg_c, lw=1)
        ax.add_patch(lp)
        t_col = 'white' if bg_c == '#0F172A' else '#0F172A'
        ax.text(25.5, 64.5 - i*6.5, l_txt, ha='center', va='center', fontsize=6.8, weight='bold', color=t_col)

    # Right Column: Results & Key Findings & Conclusion
    res_box = FancyBboxPatch((52, 42), 45, 55, boxstyle="round,pad=0.8,rounding_size=1.2", facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=1.2)
    ax.add_patch(res_box)
    res_hdr = FancyBboxPatch((52, 93), 45, 4, boxstyle="round,pad=0.2,rounding_size=0.6", facecolor='#1E40AF', edgecolor='#1E40AF')
    ax.add_patch(res_hdr)
    ax.text(74.5, 95, "EXPERIMENTAL RESULTS", ha='center', va='center', fontsize=8.5, weight='bold', color='white')

    res_metrics = [
        ("Holdout Test Accuracy", "99.59% (978 / 982)"),
        ("Detection Precision", "99.38% (482 TP / 3 FP)"),
        ("Detection Recall", "99.79% (482 TP / 1 FN)"),
        ("ROC-AUC Score", "1.0000 (Perfect discrimination)"),
        ("Engine Response Time", "45 ms (Cache Hit)"),
        ("Zero Auto-Open Safety", "100% Policy Enforcement")
    ]
    for i, (k, v) in enumerate(res_metrics):
        ax.text(55, 87 - i*7, f"• {k}:", fontsize=7.2, color='#1E293B', weight='bold')
        ax.text(94, 87 - i*7, v, fontsize=7.2, color='#2563EB', weight='heavy', ha='right')

    # Conclusion
    c_box = FancyBboxPatch((52, 20), 45, 20, boxstyle="round,pad=0.8,rounding_size=1.2", facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=1.2)
    ax.add_patch(c_box)
    c_hdr = FancyBboxPatch((52, 36), 45, 4, boxstyle="round,pad=0.2,rounding_size=0.6", facecolor='#1E40AF', edgecolor='#1E40AF')
    ax.add_patch(c_hdr)
    ax.text(74.5, 38, "CONCLUSION", ha='center', va='center', fontsize=8.5, weight='bold', color='white')
    ax.text(54, 27, "QRadar successfully neutralizes modern quishing\nthreats by combining deterministic security heuristics,\nRandom Forest classification, and real-time threat\nintelligence with strict zero-open action gates.", fontsize=6.8, color='#334155')

    # Guide Footer
    f_box = FancyBboxPatch((3, 4), 94, 13, boxstyle="round,pad=0.8,rounding_size=1.2", facecolor='#F1F5F9', edgecolor='#94A3B8', lw=1)
    ax.add_patch(f_box)
    ax.text(50, 12, "UNDER THE GUIDANCE OF", ha='center', fontsize=8, weight='bold', color='#475569')
    ax.text(50, 8, "Mrs. T. Suneetha, Assistant Professor", ha='center', fontsize=9.5, weight='heavy', color='#0F172A')
    ax.text(50, 5, "Department of Computer Science & Engineering (Cyber Security) | Malla Reddy University", ha='center', fontsize=7.5, color='#64748B')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "poster_presentation.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Poster Presentation generated.")

if __name__ == '__main__':
    generate_university_logo()
    generate_screen1()
    generate_screen2()
    generate_screen3()
    generate_screen4()
    generate_screen5()
    generate_screen6()
    generate_screen7()
    generate_poster()
    print("All UI screens and presentation poster generated successfully!")
