import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "doc_assets"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Generating assets into {OUTPUT_DIR}")

# -------------------------------------------------------------
# GRAPH 1: Quishing Attack Category & Threat Distribution (Pie Chart)
# -------------------------------------------------------------
def generate_graph1():
    labels = ['Typosquatting / Homoglyphs', 'Raw IP Address Host', 'Obfuscated Shortener', 'Dangerous Scheme (JS/File)', 'Suspicious Target Keywords']
    sizes = [35.0, 25.0, 20.0, 12.0, 8.0]
    colors = ['#EF4444', '#F97316', '#3B82F6', '#8B5CF6', '#10B981']
    explode = (0.05, 0.03, 0, 0, 0)

    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        startangle=140, colors=colors, textprops=dict(color="#1E293B", fontsize=10, weight='bold'),
        wedgeprops=dict(width=0.8, edgecolor='white', linewidth=1.5)
    )
    for at in autotexts:
        at.set_color('white')
        at.set_weight('bold')
        at.set_fontsize(10)
    
    ax.set_title("Attack Category Wise Quishing Threat Distribution", fontsize=13, weight='bold', pad=15, color='#0F172A')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "graph1_attack_distribution.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Graph 1 generated.")

# -------------------------------------------------------------
# GRAPH 2: Incident Detection & Verification Response Timeline (Line Chart)
# -------------------------------------------------------------
def generate_graph2():
    days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5']
    scans_evaluated = [52, 70, 65, 92, 88]
    threats_neutralized = [12, 19, 14, 28, 22]

    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=300)
    ax.plot(days, scans_evaluated, marker='o', color='#2563EB', linewidth=2.5, markersize=8, label='Total Scans Evaluated', zorder=4)
    ax.plot(days, threats_neutralized, marker='s', color='#DC2626', linewidth=2.5, markersize=8, linestyle='--', label='Quishing Threats Blocked', zorder=4)

    for i, txt in enumerate(scans_evaluated):
        ax.annotate(str(txt), (days[i], scans_evaluated[i] + 2), ha='center', fontsize=9, weight='bold', color='#1E40AF')
    for i, txt in enumerate(threats_neutralized):
        ax.annotate(str(txt), (days[i], threats_neutralized[i] + 2), ha='center', fontsize=9, weight='bold', color='#991B1B')

    ax.set_title("QRadar Incident Detection & Verification Timeline", fontsize=13, weight='bold', pad=15, color='#0F172A')
    ax.set_xlabel("Operational Deployment Timeline", fontsize=11, weight='bold', labelpad=8)
    ax.set_ylabel("Number of Scans / Detections", fontsize=11, weight='bold', labelpad=8)
    ax.set_ylim(0, 105)
    ax.grid(True, linestyle=':', alpha=0.6, zorder=1)
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#CBD5E1', fontsize=10)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "graph2_incident_timeline.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Graph 2 generated.")

# -------------------------------------------------------------
# GRAPH 3: Threat Risk Score & Severity Distribution (Bar Chart)
# -------------------------------------------------------------
def generate_graph3():
    categories = ['Critical (90-100)', 'High (70-89)', 'Medium (30-69)', 'Low (0-29)']
    counts = [18, 42, 35, 120]
    colors = ['#DC2626', '#EA580C', '#EAB308', '#16A34A']

    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=300)
    bars = ax.bar(categories, counts, color=colors, width=0.55, edgecolor='#334155', linewidth=1, zorder=3)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, weight='bold', color='#0F172A')

    ax.set_title("Threat Risk Score Severity Distribution", fontsize=13, weight='bold', pad=15, color='#0F172A')
    ax.set_xlabel("Risk Score Category & Security Action", fontsize=11, weight='bold', labelpad=8)
    ax.set_ylabel("Number of QR Targets Scanned", fontsize=11, weight='bold', labelpad=8)
    ax.set_ylim(0, 140)
    ax.grid(axis='y', linestyle=':', alpha=0.6, zorder=1)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "graph3_priority_distribution.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Graph 3 generated.")

# -------------------------------------------------------------
# GRAPH 4: Scan Verdict Classification Distribution (Pie Chart)
# -------------------------------------------------------------
def generate_graph4():
    labels = ['SAFE (Allow Navigation)', 'MALICIOUS (Blocked)', 'SUSPICIOUS (Warning Gate)']
    sizes = [64.2, 21.0, 14.8]
    colors = ['#22C55E', '#EF4444', '#F59E0B']
    explode = (0.04, 0.06, 0.04)

    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        startangle=130, colors=colors, textprops=dict(color="#0F172A", fontsize=10, weight='bold'),
        wedgeprops=dict(width=0.8, edgecolor='white', linewidth=1.5)
    )
    for at in autotexts:
        at.set_color('white')
        at.set_weight('bold')
        at.set_fontsize(11)

    ax.set_title("Overall Scan Verdict Classification Distribution", fontsize=13, weight='bold', pad=15, color='#0F172A')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "graph4_status_distribution.png")
    plt.savefig(path, dpi=300)
    plt.close()
    print("Graph 4 generated.")

if __name__ == '__main__':
    generate_graph1()
    generate_graph2()
    generate_graph3()
    generate_graph4()
    print("All 4 graphs successfully generated!")
