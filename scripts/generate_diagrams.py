import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "doc_assets"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------------
# Figure 1: Architectural Diagram of QRadar
# -------------------------------------------------------------------
def generate_arch_diagram():
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background canvas
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Title
    ax.text(50, 96, "Figure 1: Architectural Framework of QRadar Defense System", 
            ha='center', va='center', fontsize=13, weight='bold', color='#0F172A')

    # User Box (Left)
    rect_user = FancyBboxPatch((4, 52), 22, 36, boxstyle="round,pad=1.2,rounding_size=2",
                               edgecolor='#0284C7', facecolor='#F0F9FF', linewidth=1.8)
    ax.add_patch(rect_user)
    ax.text(15, 84, "USER / CLIENT", ha='center', va='center', fontsize=10.5, weight='bold', color='#0369A1')
    user_items = ["• Live Camera Viewfinder", "• Image / Gallery Picker", "• Manual URL Entry", "• Risk Score Gauge", "• Safe Navigation Gate"]
    for i, item in enumerate(user_items):
        ax.text(6, 78 - i*5.5, item, fontsize=8.5, color='#0F172A', va='center')

    # Admin Box (Right)
    rect_admin = FancyBboxPatch((74, 52), 22, 36, boxstyle="round,pad=1.2,rounding_size=2",
                                edgecolor='#7C3AED', facecolor='#F5F3FF', linewidth=1.8)
    ax.add_patch(rect_admin)
    ax.text(85, 84, "SECURITY ADMIN", ha='center', va='center', fontsize=10.5, weight='bold', color='#6D28D9')
    admin_items = ["• Threat Intel API Keys", "• Live Threat Telemetry", "• System Audit Logs", "• Cache TTL Settings", "• CSV Export & Metrics"]
    for i, item in enumerate(admin_items):
        ax.text(76, 78 - i*5.5, item, fontsize=8.5, color='#0F172A', va='center')

    # Core Security Engine Box (Center)
    rect_core = FancyBboxPatch((31, 38), 38, 50, boxstyle="round,pad=1.5,rounding_size=3",
                               edgecolor='#0F172A', facecolor='#F8FAFC', linewidth=2.2)
    ax.add_patch(rect_core)
    ax.text(50, 84.5, "FASTAPI AUTHORITATIVE SECURITY ENGINE", ha='center', va='center', fontsize=10, weight='bold', color='#0F172A')

    # Engine Layers
    layers = [
        ("Layer 1: QR Decoder & SSRF Protocol Guard", "#E0F2FE", "#0369A1"),
        ("Layer 2: 12 Heuristic Threat Rules Engine", "#FEF3C7", "#D97706"),
        ("Layer 3: 18-Feature Random Forest ML (99.59%)", "#FEE2E2", "#DC2626"),
        ("Layer 4: Threat Intelligence (VT, GSB, TTL)", "#EDE9FE", "#7C3AED"),
        ("Layer 5: Multi-Layer Risk Aggregator (0-100)", "#DCFCE7", "#16A34A")
    ]
    for i, (layer_txt, bg_col, border_col) in enumerate(layers):
        lp = FancyBboxPatch((33, 75 - i*7.5), 34, 5.8, boxstyle="round,pad=0.5,rounding_size=1",
                            edgecolor=border_col, facecolor=bg_col, linewidth=1.2)
        ax.add_patch(lp)
        ax.text(50, 78 - i*7.5, layer_txt, ha='center', va='center', fontsize=8.5, weight='bold', color='#0F172A')

    # Database & Storage Layer (Bottom Center)
    rect_db = FancyBboxPatch((35, 6), 30, 22, boxstyle="round,pad=1.2,rounding_size=2",
                             edgecolor='#059669', facecolor='#ECFDF5', linewidth=1.8)
    ax.add_patch(rect_db)
    ax.text(50, 24, "PERSISTENCE & CACHE LAYER", ha='center', va='center', fontsize=10, weight='bold', color='#047857')
    db_items = ["• SQLite Threat Intel Cache (24h TTL)", "• Scan Audit Logs & Verdict History", "• ML Model Weights & Metadata", "• Automated 30-Day Data Retention"]
    for i, item in enumerate(db_items):
        ax.text(37, 19.5 - i*4.2, item, fontsize=8, color='#064E3B', va='center')

    # Arrows
    # User -> Core
    ax.annotate("", xy=(31, 70), xytext=(26, 70),
                arrowprops=dict(arrowstyle="->", color="#0284C7", lw=2))
    ax.text(28.5, 72, "Scan / URL", ha='center', fontsize=7.5, weight='bold', color='#0284C7')

    # Core -> User
    ax.annotate("", xy=(26, 62), xytext=(31, 62),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=2))
    ax.text(28.5, 59.5, "Verdict & Gate", ha='center', fontsize=7.5, weight='bold', color='#059669')

    # Admin <-> Core
    ax.annotate("", xy=(69, 70), xytext=(74, 70),
                arrowprops=dict(arrowstyle="<->", color="#7C3AED", lw=2))
    ax.text(71.5, 72, "Config & Logs", ha='center', fontsize=7.5, weight='bold', color='#7C3AED')

    # Core <-> DB
    ax.annotate("", xy=(50, 38), xytext=(50, 28),
                arrowprops=dict(arrowstyle="<->", color="#059669", lw=2))
    ax.text(53.5, 33, "Audit & Cache", ha='left', fontsize=8, weight='bold', color='#047857')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig1_architectural_diagram.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Figure 1 generated.")

# -------------------------------------------------------------------
# Figure 2: Comprehensive Data Flow Diagram (DFD Level 1)
# -------------------------------------------------------------------
def generate_dfd_diagram():
    fig, ax = plt.subplots(figsize=(10, 8.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(50, 97, "Figure 2: Comprehensive Data Flow Diagram of QRadar (DFD Level 1)", 
            ha='center', va='center', fontsize=12.5, weight='bold', color='#0F172A')

    # Entities
    # Citizen/User
    p_user = FancyBboxPatch((3, 76), 18, 14, boxstyle="square,pad=0.8", edgecolor='#1E3A8A', facecolor='#DBEAFE', lw=1.8)
    ax.add_patch(p_user)
    ax.text(12, 83, "User / Scanner\n(Citizen)", ha='center', va='center', fontsize=9.5, weight='bold', color='#1E3A8A')

    # Admin
    p_admin = FancyBboxPatch((3, 38), 18, 14, boxstyle="square,pad=0.8", edgecolor='#6D28D9', facecolor='#EDE9FE', lw=1.8)
    ax.add_patch(p_admin)
    ax.text(12, 45, "Security Admin /\nAnalyst", ha='center', va='center', fontsize=9.5, weight='bold', color='#6D28D9')

    # External Threat Intel
    p_ti = FancyBboxPatch((80, 58), 17, 14, boxstyle="square,pad=0.8", edgecolor='#DC2626', facecolor='#FEE2E2', lw=1.8)
    ax.add_patch(p_ti)
    ax.text(88.5, 65, "Threat Intel Feeds\n(VT / GSB)", ha='center', va='center', fontsize=9, weight='bold', color='#991B1B')

    # Processes (Numbered circles/ovals)
    processes = [
        (1, "(1)\nInput Ingestion &\nValidation", 38, 83),
        (2, "(2)\nQR Decoding &\nNormalization", 60, 83),
        (3, "(3)\n12 Heuristics\nEvaluation", 40, 60),
        (4, "(4)\n18-Feature ML\nInference", 60, 60),
        (5, "(5)\nThreat Intel &\nCache Check", 60, 38),
        (6, "(6)\nRisk Synthesis &\nVerdict Gate", 40, 38),
        (7, "(7)\nAudit Logging &\nAnalytics", 40, 16)
    ]
    for num, label, x, y in processes:
        circle = patches.Ellipse((x, y), 17, 10, edgecolor='#0F172A', facecolor='#F1F5F9', lw=1.6)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=7.8, weight='bold', color='#0F172A')

    # Data Stores (D1, D2, D3)
    stores = [
        ("D1: User / Session Store", 76, 83),
        ("D2: Threat Intel TTL Cache", 80, 38),
        ("D3: Incident Audit Logs", 76, 16)
    ]
    for name, x, y in stores:
        p_store = FancyBboxPatch((x, y-4), 19, 8, boxstyle="round,pad=0.4,rounding_size=0.5",
                                 edgecolor='#059669', facecolor='#ECFDF5', lw=1.5)
        ax.add_patch(p_store)
        ax.text(x+9.5, y, name, ha='center', va='center', fontsize=8, weight='bold', color='#047857')

    # Arrows connecting flow
    def draw_arrow(x1, y1, x2, y2, label="", color="#334155", rad=0.0):
        connectionstyle = f"arc3,rad={rad}" if rad != 0.0 else "arc3"
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.4, connectionstyle=connectionstyle))
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 1.5, label, ha='center', va='center', fontsize=7, color=color, weight='bold')

    draw_arrow(21, 83, 29.5, 83, "Scan / Image")
    draw_arrow(46.5, 83, 51.5, 83, "Clean Buffer")
    draw_arrow(60, 78, 60, 65, "Extracted URL")
    draw_arrow(51.5, 80, 46.5, 65, "Payload")
    draw_arrow(60, 55, 60, 43, "Domain / Host")
    draw_arrow(71.5, 38, 79.5, 38, "Cache hit/miss")
    draw_arrow(80, 65, 68.5, 43, "API lookup", color="#DC2626")
    draw_arrow(51.5, 38, 48.5, 38, "Scores & Intel")
    draw_arrow(40, 55, 40, 43, "Heuristic Wt")
    draw_arrow(40, 33, 40, 21, "Verdict & Telemetry")
    draw_arrow(48.5, 16, 75.5, 16, "Store Record")
    draw_arrow(31.5, 38, 21, 78, "Risk Verdict Gate", color="#16A34A", rad=-0.2)
    draw_arrow(21, 45, 31.5, 45, "Admin Inquiries", color="#6D28D9")
    draw_arrow(40, 11, 21, 40, "Analytics Reports", color="#6D28D9", rad=0.2)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig2_comprehensive_dfd.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Figure 2 generated.")

# -------------------------------------------------------------------
# Figure 3: Class Diagram
# -------------------------------------------------------------------
def generate_class_diagram():
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(50, 97, "Figure 3: Class Diagram of QRadar System Entities", 
            ha='center', va='center', fontsize=12.5, weight='bold', color='#0F172A')

    def draw_class(x, y, w, h, title, attrs, methods, color='#1E40AF', bg='#EFF6FF'):
        # Outer box
        rect = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", edgecolor=color, facecolor=bg, lw=1.6)
        ax.add_patch(rect)
        # Title section
        th = 4.5
        t_rect = patches.Rectangle((x, y+h-th), w, th, edgecolor=color, facecolor=color, lw=1.6)
        ax.add_patch(t_rect)
        ax.text(x + w/2, y + h - th/2, title, ha='center', va='center', fontsize=9, weight='bold', color='white')
        
        # Attributes
        ay = y + h - th - 2.5
        for a in attrs:
            ax.text(x + 1.2, ay, a, fontsize=7.2, color='#0F172A', va='center')
            ay -= 3.0
            
        # Divider line
        div_y = y + len(methods)*3.2 + 2
        ax.plot([x, x+w], [div_y, div_y], color=color, lw=1)
        
        # Methods
        my = div_y - 2.2
        for m in methods:
            ax.text(x + 1.2, my, m, fontsize=7.2, color='#0F172A', va='center')
            my -= 3.0

    # User
    draw_class(5, 68, 26, 25, "CitizenUser",
               ["+userId: UUID", "+deviceFingerprint: str", "+scanCount: int"],
               ["+scanQRCode(img): ScanResult", "+confirmNavigation(): bool", "+reportFalsePositive(): void"])

    # SecurityAdmin
    draw_class(69, 68, 26, 25, "SecurityAdmin",
               ["+adminId: str", "+role: AdminRole", "+apiKeyMap: dict"],
               ["+updateThreatKeys(keys): bool", "+viewAuditMetrics(): Dashboard", "+exportCSVLogs(): bytes"])

    # QRScanEngine
    draw_class(37, 36, 26, 30, "AuthoritativeScanEngine",
               ["+engineId: str", "+zeroAutoOpen: bool=True", "+rateLimiter: RateLimiter"],
               ["+decodeImage(bytes): str", "+evaluateDestination(url): Verdict", "+enforceActionGate(): Action", "+persistLog(record): void"],
               color='#0F172A', bg='#F8FAFC')

    # HeuristicAnalyzer
    draw_class(5, 10, 26, 22, "HeuristicEngine",
               ["+rulesCount: int = 12", "+brandCatalog: list", "+entropyThreshold: float"],
               ["+checkTyposquatting(): int", "+checkIPHost(): int", "+computeTotalScore(): int"])

    # MLEngine
    draw_class(37, 5, 26, 22, "RandomForestMLEngine",
               ["+featureCount: int = 18", "+modelPath: str", "+holdoutAccuracy: 99.59%"],
               ["+extract18Features(url): vector", "+predictProbability(vec): float", "+getClassification(): str"])

    # ThreatIntelService
    draw_class(69, 10, 26, 22, "ThreatIntelService",
               ["+cacheTTLHours: int = 24", "+providers: list", "+dbSession: Session"],
               ["+queryCache(hash): dict", "+fetchVirusTotal(url): dict", "+fetchSafeBrowsing(url): dict"])

    # Association lines
    ax.annotate("", xy=(37, 52), xytext=(31, 75), arrowprops=dict(arrowstyle="->", color="#1E40AF", lw=1.5))
    ax.annotate("", xy=(63, 52), xytext=(69, 75), arrowprops=dict(arrowstyle="->", color="#6D28D9", lw=1.5))
    ax.annotate("", xy=(25, 32), xytext=(37, 45), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5))
    ax.annotate("", xy=(50, 27), xytext=(50, 36), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5))
    ax.annotate("", xy=(75, 32), xytext=(63, 45), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig3_class_diagram.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Figure 3 generated.")

# -------------------------------------------------------------------
# Figure 4: Use Case Diagram
# -------------------------------------------------------------------
def generate_usecase_diagram():
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(50, 97, "Figure 4: Use Case Diagram of QRadar Quishing Defense Platform", 
            ha='center', va='center', fontsize=12.5, weight='bold', color='#0F172A')

    # System boundary box
    sys_box = FancyBboxPatch((24, 6), 52, 86, boxstyle="square,pad=0.8", edgecolor='#0F172A', facecolor='#F8FAFC', lw=2)
    ax.add_patch(sys_box)
    ax.text(50, 89, "QRadar Quishing Defense System Boundary", ha='center', va='center', fontsize=10.5, weight='bold', color='#0F172A')

    # Actor functions
    def draw_actor(x, y, label, color='#1E40AF'):
        # Head
        c = patches.Circle((x, y+5), 2.2, edgecolor=color, facecolor='white', lw=1.8)
        ax.add_patch(c)
        # Body
        ax.plot([x, x], [y+2.8, y-3], color=color, lw=1.8)
        # Arms
        ax.plot([x-3.5, x+3.5], [y+1, y+1], color=color, lw=1.8)
        # Legs
        ax.plot([x, x-3], [y-3, y-8], color=color, lw=1.8)
        ax.plot([x, x+3], [y-3, y-8], color=color, lw=1.8)
        # Label
        ax.text(x, y-11.5, label, ha='center', va='center', fontsize=9, weight='bold', color=color)

    draw_actor(10, 52, "Mobile / Web\nEnd User", color='#1E40AF')
    draw_actor(90, 52, "Security\nAdministrator", color='#6D28D9')

    # Use Cases (Ovals)
    use_cases = [
        ("Scan QR via Live Camera", 50, 81),
        ("Upload QR Image File", 50, 72),
        ("Manual URL Threat Analysis", 50, 63),
        ("Inspect Explainable Risk & Heuristics", 50, 54),
        ("Execute Safe Navigation / Override Gate", 50, 45),
        ("View Scan History & Audit Logs", 50, 36),
        ("Configure Threat Intel API Keys", 50, 27),
        ("Monitor Security Analytics Dashboard", 50, 18),
        ("Export Incident Logs (CSV)", 50, 9)
    ]

    for label, cx, cy in use_cases:
        oval = patches.Ellipse((cx, cy), 32, 6.2, edgecolor='#0284C7', facecolor='#EFF6FF', lw=1.4)
        ax.add_patch(oval)
        ax.text(cx, cy, label, ha='center', va='center', fontsize=8, weight='bold', color='#0F172A')

    # Connect End User to use cases 1 to 6
    user_conn = [81, 72, 63, 54, 45, 36]
    for uy in user_conn:
        ax.plot([14, 34], [52, uy], color='#1E40AF', lw=1.2, linestyle='-')

    # Connect Admin to use cases 4, 6, 7, 8, 9
    admin_conn = [54, 36, 27, 18, 9]
    for ay in admin_conn:
        ax.plot([86, 66], [52, ay], color='#6D28D9', lw=1.2, linestyle='-')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig4_use_case_diagram.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Figure 4 generated.")

# -------------------------------------------------------------------
# Figure 5: Sequence Diagram
# -------------------------------------------------------------------
def generate_sequence_diagram():
    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(50, 97, "Figure 5: Sequence Diagram of Real-Time Quishing Detection Lifecycle", 
            ha='center', va='center', fontsize=12, weight='bold', color='#0F172A')

    # Lifelines
    lifelines = [
        ("Citizen / Client", 10),
        ("FastAPI Gateway", 28),
        ("QR & URL Analyzer", 46),
        ("Heuristic & ML Engine", 64),
        ("Threat Intel & DB", 82),
        ("Risk Engine", 95)
    ]

    for title, x in lifelines:
        p = FancyBboxPatch((x-6, 88), 12, 6, boxstyle="square,pad=0.2", edgecolor='#0F172A', facecolor='#F1F5F9', lw=1.4)
        ax.add_patch(p)
        ax.text(x, 91, title, ha='center', va='center', fontsize=7.2, weight='bold', color='#0F172A')
        # Dashed line
        ax.plot([x, x], [88, 6], color='#94A3B8', linestyle='--', lw=1)

    # Messages
    msgs = [
        (10, 28, 83, "1. Submit QR Image / URL", False),
        (28, 46, 77, "2. Decode QR & Protocol Check", False),
        (46, 28, 71, "3. Normalized URL / Dangerous Scheme Check", True),
        (28, 64, 65, "4. Extract 18 Features & Run RF Inference", False),
        (64, 82, 59, "5. Check SQLite Cache & Threat Feeds", False),
        (82, 64, 53, "6. Return Threat State (CLEAN / MALICIOUS)", True),
        (64, 95, 47, "7. Pass Heuristic Weights & ML Probability", False),
        (95, 28, 41, "8. Aggregate Risk Score (0-100) & Action Gate", True),
        (28, 82, 35, "9. Persist Scan Audit Log to SQLite", False),
        (82, 28, 29, "10. Confirm Log Persisted", True),
        (28, 10, 23, "11. Return Explainable Security JSON Response", True),
        (10, 10, 15, "12. Render Gauge & Enforce ALLOW/WARN/BLOCK", False)
    ]

    for x1, x2, y, text, is_return in msgs:
        ls = '--' if is_return else '-'
        col = '#0284C7' if not is_return else '#059669'
        if "BLOCK" in text or "Dangerous" in text:
            col = '#DC2626'
        if x1 != x2:
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.3, linestyle=ls))
            ax.text((x1+x2)/2, y+1.3, text, ha='center', va='center', fontsize=6.8, weight='bold', color=col)
        else:
            # Self call
            ax.plot([x1, x1+5, x1+5, x1], [y, y, y-3, y-3], color=col, lw=1.3)
            ax.annotate("", xy=(x1, y-3), xytext=(x1+5, y-3), arrowprops=dict(arrowstyle="->", color=col, lw=1.3))
            ax.text(x1+6, y-1.5, text, ha='left', va='center', fontsize=6.8, weight='bold', color=col)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig5_sequence_diagram.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Figure 5 generated.")

# -------------------------------------------------------------------
# Figure 6: Activity Diagram
# -------------------------------------------------------------------
def generate_activity_diagram():
    fig, ax = plt.subplots(figsize=(9, 9.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(50, 98, "Figure 6: Comprehensive Activity Diagram of QRadar Inspection Workflow", 
            ha='center', va='center', fontsize=12, weight='bold', color='#0F172A')

    # Start node (black circle)
    start = patches.Circle((50, 93), 2, facecolor='#0F172A', edgecolor='#0F172A')
    ax.add_patch(start)

    def draw_activity(x, y, w, h, text, bg='#EFF6FF', border='#0284C7'):
        p = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.5,rounding_size=1.2",
                           edgecolor=border, facecolor=bg, lw=1.4)
        ax.add_patch(p)
        ax.text(x, y, text, ha='center', va='center', fontsize=7.5, weight='bold', color='#0F172A')

    def draw_decision(x, y, w, h, text):
        diamond = patches.Polygon([[x, y+h/2], [x+w/2, y], [x, y-h/2], [x-w/2, y]],
                                  closed=True, edgecolor='#D97706', facecolor='#FEF3C7', lw=1.5)
        ax.add_patch(diamond)
        ax.text(x, y, text, ha='center', va='center', fontsize=7.2, weight='bold', color='#92400E')

    # Flow
    ax.annotate("", xy=(50, 87), xytext=(50, 91), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.3))
    draw_activity(50, 84, 38, 5, "Scan QR Code / Upload File / Enter URL")

    ax.annotate("", xy=(50, 77.5), xytext=(50, 81.5), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.3))
    draw_decision(50, 74, 18, 7, "Valid\nQR Image?")

    # No branch
    ax.annotate("", xy=(20, 74), xytext=(41, 74), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3))
    ax.text(30, 75.5, "No", ha='center', fontsize=7.5, weight='bold', color='#DC2626')
    draw_activity(20, 64, 26, 5, "Display Decoding Error", bg='#FEE2E2', border='#DC2626')

    # Yes branch
    ax.annotate("", xy=(50, 66.5), xytext=(50, 70.5), arrowprops=dict(arrowstyle="->", color="#16A34A", lw=1.3))
    ax.text(53, 68.5, "Yes", ha='left', fontsize=7.5, weight='bold', color='#16A34A')
    draw_activity(50, 63.5, 38, 5, "Protocol Normalization & SSRF Guard")

    ax.annotate("", xy=(50, 57.5), xytext=(50, 61), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.3))
    draw_decision(50, 54, 22, 7, "Dangerous\nScheme / IP?")

    # Yes dangerous
    ax.annotate("", xy=(82, 54), xytext=(61, 54), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3))
    ax.text(71, 55.5, "Yes (Trapped)", ha='center', fontsize=7.2, weight='bold', color='#DC2626')
    draw_activity(82, 44, 28, 5.5, "Assign Max Risk (98)\nVerdict: MALICIOUS", bg='#FEE2E2', border='#DC2626')

    # No dangerous
    ax.annotate("", xy=(50, 46.5), xytext=(50, 50.5), arrowprops=dict(arrowstyle="->", color="#16A34A", lw=1.3))
    ax.text(53, 48.5, "Clean Scheme", ha='left', fontsize=7.2, weight='bold', color='#16A34A')
    draw_activity(50, 43.5, 42, 5.5, "Extract 18 Features & Run 12 Heuristics")

    ax.annotate("", xy=(50, 37), xytext=(50, 40.7), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.3))
    draw_activity(50, 34, 42, 5.5, "Check Threat Intel Cache (VT/GSB 24h)")

    ax.annotate("", xy=(50, 27.5), xytext=(50, 31.2), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.3))
    draw_activity(50, 24.5, 42, 5.5, "Compute Multi-Layer Risk Score (0-100)")

    # Connect dangerous directly to persist
    ax.annotate("", xy=(72, 17), xytext=(82, 41), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3))

    ax.annotate("", xy=(50, 18), xytext=(50, 21.7), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.3))
    draw_activity(50, 15, 44, 5.5, "Enforce Action Gate: SAFE / WARN / BLOCK\n& Persist Audit Log in SQLite")

    # Connect decoding error to end
    ax.annotate("", xy=(30, 7), xytext=(20, 61.5), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3))

    # End node
    ax.annotate("", xy=(50, 8.5), xytext=(50, 12.2), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.3))
    end_outer = patches.Circle((50, 6), 2.5, facecolor='white', edgecolor='#0F172A', lw=1.5)
    end_inner = patches.Circle((50, 6), 1.6, facecolor='#0F172A', edgecolor='#0F172A')
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)
    ax.text(50, 1.8, "End", ha='center', va='center', fontsize=8, weight='bold', color='#0F172A')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig6_activity_diagram.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Figure 6 generated.")

if __name__ == '__main__':
    generate_arch_diagram()
    generate_dfd_diagram()
    generate_class_diagram()
    generate_usecase_diagram()
    generate_sequence_diagram()
    generate_activity_diagram()
    print("All 6 architecture and design diagrams successfully generated!")
