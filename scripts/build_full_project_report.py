import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(BASE_DIR, "doc_assets")
DOCX_PATH = os.path.join(BASE_DIR, "QRadar_Application_Development_Project_Report.docx")

def create_report():
    doc = Document()

    # Configure default style (Times New Roman, 12pt, 1.15 spacing)
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Deep slate text
    style.paragraph_format.line_spacing = 1.15
    style.paragraph_format.space_after = Pt(4)

    # Margins: 1 inch (72 pt) all around
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True
        
        # Add thin classic border around page
        sectPr = section._sectPr
        pgBorders = parse_xml(f'''
            <w:pgBorders {nsdecls("w")} w:offsetFrom="page">
                <w:top w:val="single" w:sz="8" w:space="24" w:color="0F172A"/>
                <w:left w:val="single" w:sz="8" w:space="24" w:color="0F172A"/>
                <w:bottom w:val="single" w:sz="8" w:space="24" w:color="0F172A"/>
                <w:right w:val="single" w:sz="8" w:space="24" w:color="0F172A"/>
            </w:pgBorders>
        ''')
        sectPr.append(pgBorders)

    # Helper functions
    def add_p(text="", align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, italic=False, size=12, space_before=0, space_after=4, color=None):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if text:
            run = p.add_run(text)
            run.bold = bold
            run.italic = italic
            run.font.name = 'Times New Roman'
            run.font.size = Pt(size)
            if color:
                run.font.color.rgb = color
        return p

    def add_h1(title, space_before=12, space_after=12):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(title)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def add_h2(title, space_before=10, space_after=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(title)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def add_h3(title, space_before=8, space_after=3):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(title)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def add_img(img_name, width_in_inches=5.8, caption=None):
        img_path = os.path.join(ASSETS_DIR, img_name)
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(4)
            p.add_run().add_picture(img_path, width=Inches(width_in_inches))
            if caption:
                cp = doc.add_paragraph()
                cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cp.paragraph_format.space_before = Pt(2)
                cp.paragraph_format.space_after = Pt(8)
                c_run = cp.add_run(caption)
                c_run.bold = True
                c_run.font.name = 'Times New Roman'
                c_run.font.size = Pt(10.5)
                c_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        else:
            print(f"Warning: Image {img_path} not found.")

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def set_cell_background(cell, hex_color):
        shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'
        cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

    def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            </w:tblBorders>
        ''')
        tblPr.append(borders)

    print("Building Page 1: Cover Page...")
    # ===================================================================
    # PAGE 1: TITLE / COVER PAGE
    # ===================================================================
    add_img("malla_reddy_logo.png", width_in_inches=4.2)
    add_p()
    add_p("An Application Development Project Report", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=10, space_after=18)
    
    add_p("QRADAR", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=24, space_before=6, space_after=4, color=RGBColor(0x0F, 0x17, 0x2A))
    add_p("Real-Time Quishing Detection & Defense System", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_before=0, space_after=24)
    
    add_p("Design & developed by", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=8, space_after=14)
    
    # Students Table
    t_stud = doc.add_table(rows=3, cols=2)
    t_stud.alignment = WD_TABLE_ALIGNMENT.CENTER
    stud_data = [
        ("Banda Priyanka", "2411CS040011"),
        ("Gourishetti Sai Teja", "2411CS040061"),
        ("Gurugubelli Trishaanth", "2411CS040063")
    ]
    for r_idx, (name, roll) in enumerate(stud_data):
        row = t_stud.rows[r_idx]
        cell_l, cell_r = row.cells[0], row.cells[1]
        cell_l.width = Inches(3.2)
        cell_r.width = Inches(2.2)
        p_l = cell_l.paragraphs[0]
        p_l.paragraph_format.space_after = Pt(3)
        run_l = p_l.add_run(name)
        run_l.font.name = 'Times New Roman'
        run_l.font.size = Pt(11)
        run_l.bold = True
        
        p_r = cell_r.paragraphs[0]
        p_r.paragraph_format.space_after = Pt(3)
        run_r = p_r.add_run(roll)
        run_r.font.name = 'Times New Roman'
        run_r.font.size = Pt(11)
        run_r.bold = True

    add_p()
    add_p("GUIDED BY", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=20, space_after=2)
    add_p("Mrs. T. Suneetha", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=2, space_after=2)
    add_p("(Assistant Professor)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=11, space_before=0, space_after=24)

    add_p("Department of Computer Science & Engineering (Cyber Security)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=16, space_after=2)
    add_p("IIYR-IISEM", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=2, space_after=2)
    add_p("Malla Reddy University, Hyderabad", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=2, space_after=2)
    add_p("April-2026", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=11, space_before=2, space_after=4)

    doc.add_page_break()

    print("Building Page 2: Certificate...")
    # ===================================================================
    # PAGE 2: CERTIFICATE
    # ===================================================================
    add_img("malla_reddy_logo.png", width_in_inches=4.0)
    add_p("Department of Computer Science & Engineering (Cyber Security)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=10, space_after=12, color=RGBColor(0xDC, 0x26, 0x26))
    
    add_p("CERTIFICATE", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=16, space_before=8, space_after=18)
    
    cert_text = (
        "This is to certify that this is the bonafide record of the application development entitled "
        "“QRADAR: Real-Time Quishing Detection & Defense System” submitted by Banda Priyanka (2411CS040011), "
        "Gourishetti Sai Teja (2411CS040061), and Gurugubelli Trishaanth (2411CS040063) B. Tech II year II semester, "
        "Department of CSE (Cyber Security) during the academic year 2025-26. The results embodied in this report have "
        "not been submitted to any other university or institute for the award of any degree or diploma."
    )
    p_cert = add_p(cert_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=8, space_after=36)
    p_cert.paragraph_format.line_spacing = 1.3

    # Signature Table
    t_sig = doc.add_table(rows=2, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Row 1
    c1, c2 = t_sig.rows[0].cells[0], t_sig.rows[0].cells[1]
    c1.width = Inches(3.2)
    c2.width = Inches(3.2)
    p1 = c1.paragraphs[0]
    p1.add_run("Internal Guide\nMrs. T. Suneetha\n(Assistant Professor)").bold = True
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p2.add_run("Dean (CS, IOT&ECE)\nDr G. Anand Kumar\nProfessor & Dean").bold = True

    # Row 2 (External Examiner)
    c3, c4 = t_sig.rows[1].cells[0], t_sig.rows[1].cells[1]
    p3 = c3.paragraphs[0]
    p3.paragraph_format.space_before = Pt(36)
    p3.add_run("External Examiner").bold = True

    doc.add_page_break()

    print("Building Page 3: Declaration...")
    # ===================================================================
    # PAGE 3: DECLARATION
    # ===================================================================
    add_h1("DECLARATION", space_before=24, space_after=24)
    
    decl_text = (
        "We hereby declare that the project report entitled “QRADAR: Real-Time Quishing Detection & Defense System” "
        "has been carried out by us. This work has been submitted to the Department of Computer Science and Engineering "
        "(Cyber Security), Malla Reddy University, Hyderabad in partial fulfilment of the requirements for the award of "
        "the degree of Bachelor of Technology. We further declare that this project work has not been submitted in full "
        "or part for the award of any other degree in other educational institutions."
    )
    p_decl = add_p(decl_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=12, space_after=30)
    p_decl.paragraph_format.line_spacing = 1.3

    add_p("Place: Hyderabad", align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=12, space_before=12, space_after=4)
    add_p("Date: April-2026", align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=12, space_before=4, space_after=36)

    # Students Table
    t_dstud = doc.add_table(rows=3, cols=2)
    t_dstud.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, (name, roll) in enumerate(stud_data):
        row = t_dstud.rows[r_idx]
        cl, cr = row.cells[0], row.cells[1]
        cl.width = Inches(3.2)
        cr.width = Inches(2.2)
        pl = cl.paragraphs[0]
        pl.paragraph_format.space_after = Pt(4)
        run_l = pl.add_run(name)
        run_l.bold = True
        pr = cr.paragraphs[0]
        pr.paragraph_format.space_after = Pt(4)
        run_r = pr.add_run(roll)
        run_r.bold = True

    doc.add_page_break()

    print("Building Page 4: Acknowledgement...")
    # ===================================================================
    # PAGE 4: ACKNOWLEDGEMENT
    # ===================================================================
    add_h1("ACKNOWLEDGEMENT", space_before=20, space_after=20)
    
    ack_paragraphs = [
        "We extend our sincere gratitude to all those who have contributed to the completion of this project report. Firstly, we would like to extend our gratitude to Dr. V. S. K Reddy, Vice Chancellor, for his visionary leadership and unwavering commitment to academic excellence.",
        "We would also like to express our deepest appreciation to our project guide Mrs. T. Suneetha, Assistant Professor, whose invaluable guidance, insightful feedback, and unwavering support have been instrumental throughout the course of this project for successful outcomes.",
        "We extend our gratitude to our PRC – convenor, Dr. G. Latha, Associate Professor, for giving valuable inputs and timely guidelines to improve the quality of our project through a critical review process. We thank our project coordinator Mrs. T. Suneetha, for her timely support.",
        "We are also grateful to Dr. G. Anand Kumar, Dean Cyber Security, for providing us with the necessary resources and facilities to carry out this project.",
        "We are deeply indebted to all of them for their support, encouragement, and guidance, without which this project would not have been possible."
    ]
    for ack_p in ack_paragraphs:
        p = add_p(ack_p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=6, space_after=10)
        p.paragraph_format.line_spacing = 1.25

    add_p(space_after=20)
    # Students Table
    t_astud = doc.add_table(rows=3, cols=2)
    t_astud.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, (name, roll) in enumerate(stud_data):
        row = t_astud.rows[r_idx]
        cl, cr = row.cells[0], row.cells[1]
        cl.width = Inches(3.2)
        cr.width = Inches(2.2)
        pl = cl.paragraphs[0]
        pl.paragraph_format.space_after = Pt(4)
        run_l = pl.add_run(name)
        run_l.bold = True
        pr = cr.paragraphs[0]
        pr.paragraph_format.space_after = Pt(4)
        run_r = pr.add_run(roll)
        run_r.bold = True

    doc.add_page_break()

    print("Building Page 5: Abstract...")
    # ===================================================================
    # PAGE 5: ABSTRACT
    # ===================================================================
    add_h1("ABSTRACT", space_before=20, space_after=20)
    
    abs_text = (
        "The Real-Time Quishing Detection and Defense System (QRadar) is designed to protect mobile and web users from "
        "the rapidly growing menace of Quishing (QR Code Phishing). While QR codes have become ubiquitous across payment systems, "
        "restaurant menus, parking meters, transit ticketing, and two-factor authentication workflows, their inherent optical "
        "opacity poses severe cybersecurity risks. Threat actors exploit this by placing counterfeit QR codes over legitimate ones, "
        "redirecting unsuspecting users to credential-harvesting phishing portals, malware distribution points, obfuscated shorteners, "
        "and internal network Server-Side Request Forgery (SSRF) endpoints. Traditional mobile cameras and stock scanner applications "
        "blindly decode and auto-open embedded URLs in the default web browser, completely bypassing network firewalls and leaving users "
        "vulnerable.\n\n"
        "QRadar solves this foundational vulnerability by acting as an authoritative, defense-in-depth security proxy between the "
        "physical scan and the web browser. The system enforces a strict Zero URL Auto-Open Policy, guaranteeing that no destination "
        "is executed without rigorous multi-layered inspection. The architecture integrates five synergistic detection layers: "
        "(1) an OpenCV QR Decoder and URL Analyzer that traps dangerous schemes (javascript:, file:, data:, intent:) and internal IP "
        "ranges (127.0.0.1, RFC 1918 private subnets); (2) a deterministic 12-rule Heuristic Engine targeting brand typosquatting, "
        "homoglyph attacks, @ userinfo evasion, unencrypted HTTP transport, and URL entropy; (3) an 18-Feature Random Forest Machine "
        "Learning Classifier trained on a balanced dataset of 4,515 URLs (Tranco benign + PhishTank feeds) yielding a proven 99.59% holdout "
        "accuracy and 1.0000 ROC-AUC; (4) a pluggable Threat Intelligence layer integrating VirusTotal v3 and Google Safe Browsing v4 "
        "backed by an efficient 24-hour SQLite TTL Cache; and (5) an explainable Risk Aggregation Engine computing a normalized score "
        "(0 to 100) mapped to authoritative action gates: ALLOW (Safe), WARN (Suspicious confirmation modal), and BLOCK (Malicious).\n\n"
        "Experimental evaluations demonstrate that QRadar executes end-to-end multi-layer inspection within 45 milliseconds on cache hits "
        "and sub-500 milliseconds on live threat intelligence feeds, with low CPU and memory overhead. By providing intuitive risk radial gauges, "
        "transparent evidence breakdowns, and persistent audit logging, QRadar transforms vulnerable physical-to-digital QR interactions into "
        "a verifiable, enterprise-grade secure gateway."
    )
    p_abs = add_p(abs_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=8, space_after=18)
    p_abs.paragraph_format.line_spacing = 1.25

    kw_text = (
        "Keywords: Quishing Defense, QR Code Phishing, Cybersecurity, Heuristic Threat Analysis, Machine Learning, "
        "Random Forest Classifier, Threat Intelligence, VirusTotal, Safe Browsing, SSRF Prevention, Zero Auto-Open Policy, "
        "Real-Time Inspection, FastAPI, Flutter"
    )
    add_p(kw_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, italic=True, bold=True, size=11, space_before=14, space_after=4)

    doc.add_page_break()

    print("Building Pages 6-8: Table of Contents & Lists...")
    # ===================================================================
    # PAGES 6, 7, 8: TABLE OF CONTENTS & LIST OF TABLES/FIGURES
    # ===================================================================
    # Table of contents formatted exactly like sample PDF
    add_p("Chapter                     Title                                                                                   Page No.", bold=True, size=11, space_after=6)
    
    toc_data_p1 = [
        ("Chapter 1", "Introduction", "1 – 3"),
        ("1.1", "Problem Definition & Description", "2"),
        ("1.2", "Objective of the Project", "2 – 3"),
        ("1.3", "Scope of the Project", "3"),
        ("Chapter 2", "System Analysis", "4 – 13"),
        ("2.1", "Existing System", "4 – 5"),
        ("2.1.1", "Background & Literature Survey", "4 – 5"),
        ("2.1.2", "Limitations of Existing System", "5"),
        ("2.2", "Proposed System", "6"),
        ("2.2.1", "Advantages of Proposed System", "6"),
        ("2.3", "Software & Hardware Requirements", "7"),
        ("2.3.1", "Software Requirements", "7"),
        ("2.3.2", "Hardware Requirements", "7"),
        ("2.4", "Feasibility Study", "8 – 9"),
        ("2.4.1", "Technical Feasibility", "8"),
        ("2.4.2", "Robustness & Reliability", "8"),
        ("2.4.3", "Economic Feasibility", "9"),
        ("Chapter 3", "Architectural Design", "10 – 17"),
        ("3.1", "Modules Design", "10"),
        ("3.2", "Method and Algorithm Design", "11"),
        ("3.3", "Project Architecture", "12 – 17"),
        ("3.3.1", "Architectural Diagram", "12"),
        ("3.3.2", "Data Flow Diagram", "13"),
        ("3.3.3", "Class Diagram", "14"),
        ("3.3.4", "Use Case Diagram", "15"),
        ("3.3.5", "Sequence Diagram", "16"),
        ("3.3.6", "Activity Diagram", "17")
    ]
    for ch, title, pg in toc_data_p1:
        is_ch = "Chapter" in ch
        dots = "." * max(2, int(65 - len(ch) - len(title)))
        line = f"{ch:<14} {title} {dots} {pg}"
        add_p(line, size=10.5, bold=is_ch, space_after=3)

    doc.add_page_break()

    # TOC Page 2 (Matching sample page 7)
    add_p("Chapter                     Title                                                                                   Page No.", bold=True, size=11, space_after=6)
    toc_data_p2 = [
        ("Chapter 4", "Implementation & Testing", "17 – 21"),
        ("4.1", "Coding Blocks", "17 – 20"),
        ("4.2", "Test Cases", "20 – 21"),
        ("4.2.1", "Test Case 1", "20"),
        ("4.2.2", "Test Case 2", "20"),
        ("4.2.3", "Test Case 3", "21"),
        ("4.2.4", "Test Case 4", "21"),
        ("Chapter 5", "Results", "22 – 30"),
        ("5.1", "Resulting Screens", "22 – 26"),
        ("5.1.1", "Sign In / Security Hub Page", "22"),
        ("5.1.2", "Live QR Scanner View", "23"),
        ("5.1.3", "Explainable Threat Evaluation", "24"),
        ("5.1.4", "12 Heuristic Signal Breakdown", "25"),
        ("5.1.5", "Scan History & Audit Logs", "25"),
        ("5.1.6", "Security Operations Dashboard", "26"),
        ("5.1.7", "Threat Intelligence Configuration", "26"),
        ("5.2", "Resulting Table", "27"),
        ("5.2.1", "System Performance Metrics", "27"),
        ("5.2.2", "Existing System vs QRadar", "27"),
        ("5.3", "Resulting Graph", "28 – 29"),
        ("5.3.1", "Quishing Attack Vector Distribution", "28"),
        ("5.3.2", "Incident Detection & Resolution Timeline", "28"),
        ("5.3.3", "Threat Risk Score Severity Distribution", "29"),
        ("5.3.4", "Scan Verdict Classification Distribution", "29"),
        ("5.4", "Resulting Analysis", "30"),
        ("5.4.1", "Time Complexity", "30"),
        ("5.4.2", "Space Complexity", "30")
    ]
    for ch, title, pg in toc_data_p2:
        is_ch = "Chapter" in ch
        dots = "." * max(2, int(65 - len(ch) - len(title)))
        line = f"{ch:<14} {title} {dots} {pg}"
        add_p(line, size=10.5, bold=is_ch, space_after=3)

    doc.add_page_break()

    # TOC Page 3 (Matching sample page 8: Ch 6, Lists)
    add_p("Chapter                     Title                                                                                   Page No.", bold=True, size=11, space_after=6)
    toc_data_p3 = [
        ("5.4.3", "Results Summary", "30"),
        ("Chapter 6", "Conclusion & Future Scope", "31"),
        ("6.1", "Conclusions", "31"),
        ("6.2", "Future Scope", "31"),
        ("References", "Academic & Industry Standards", "32"),
        ("Poster Presentation", "Technical Summary Poster", "33")
    ]
    for ch, title, pg in toc_data_p3:
        is_ch = "Chapter" in ch or "References" in ch or "Poster" in ch
        dots = "." * max(2, int(65 - len(ch) - len(title)))
        line = f"{ch:<18} {title} {dots} {pg}"
        add_p(line, size=10.5, bold=is_ch, space_after=3)

    add_p(space_after=8)
    add_p("Section                     Name                                                                                   Page No.", bold=True, size=11, space_after=6)
    add_p("List Of Diagrams :", bold=True, size=11, space_after=4)
    diagrams_list = [
        ("3.3.1", "Architectural Diagram", "12"),
        ("3.3.2", "Data Flow Diagram", "13"),
        ("3.3.3", "Class Diagram", "14"),
        ("3.3.4", "Use Case Diagram", "15"),
        ("3.3.5", "Sequence Diagram", "16"),
        ("3.3.6", "Activity Diagram", "17")
    ]
    for sec, name, pg in diagrams_list:
        dots = "." * max(2, int(65 - len(sec) - len(name)))
        add_p(f"{sec:<14} {name} {dots} {pg}", size=10, space_after=2)

    add_p("List Of Screen Shots", bold=True, size=11, space_before=6, space_after=4)
    screens_list = [
        ("5.1.1", "Sign In / Security Hub Page", "22"),
        ("5.1.2", "Live QR Scanner View", "23"),
        ("5.1.3", "Explainable Threat Evaluation", "24"),
        ("5.1.4", "12 Heuristic Signal Breakdown", "25"),
        ("5.1.5", "Scan History & Audit Logs", "25"),
        ("5.1.6", "Security Operations Dashboard", "26"),
        ("5.1.7", "Threat Intelligence Configuration", "26")
    ]
    for sec, name, pg in screens_list:
        dots = "." * max(2, int(65 - len(sec) - len(name)))
        add_p(f"{sec:<14} {name} {dots} {pg}", size=10, space_after=2)

    add_p("List Of Resultant Table", bold=True, size=11, space_before=6, space_after=4)
    tables_list = [
        ("5.2.1", "System Performance Metrics", "27"),
        ("5.2.2", "Existing System vs QRadar", "27")
    ]
    for sec, name, pg in tables_list:
        dots = "." * max(2, int(65 - len(sec) - len(name)))
        add_p(f"{sec:<14} {name} {dots} {pg}", size=10, space_after=2)

    doc.add_page_break()

    print("Building Chapter 1: Introduction (Pages 9-11)...")
    # ===================================================================
    # CHAPTER 1: INTRODUCTION (Matching Pages 9, 10, 11)
    # ===================================================================
    # Page 1 of Chapter 1 (Document Page 9)
    add_p("1", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h1("CHAPTER 1\n\nINTRODUCTION", space_before=10, space_after=18)
    
    ch1_p1 = (
        "QRadar (Real-Time Quishing Detection & Defense System) stands as an innovative, enterprise-grade cybersecurity platform "
        "crafted to elevate the security, transparency, and resilience of mobile and digital QR code interactions. It creates an authoritative, "
        "secure gateway for individuals and corporate enterprises to scan physical and digital QR codes—ranging from restaurant menus and "
        "parking meters to public transit stations and multi-factor authentication (MFA) enrollment flyers—and evaluate their security posture "
        "instantly before navigation. By acting as an active security proxy between users and destinations, QRadar streamlines threat detection "
        "channels and neutralizes attacks before browsers are compromised, transforming traditionally blind interactions into verifiable, "
        "proactive defenses."
    )
    add_p(ch1_p1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=10).paragraph_format.line_spacing = 1.25

    ch1_p2 = (
        "Mobile and physical ecosystems worldwide grapple with outdated scanning pipelines that are notoriously vulnerable, disorganized, "
        "and completely opaque, often leaving smartphone users exposed to malicious redirects and phishing exploits. QRadar revolutionizes this "
        "by deploying an automated, multi-tiered defensive pipeline. Ingestion occurs seamlessly through user-friendly mobile applications or "
        "responsive web interfaces, capturing high-resolution camera feeds, image files, or manual URL entries. An authoritative FastAPI security "
        "engine then decodes and evaluates the payload across three distinct defensive layers: deterministic heuristics, 18-feature machine learning, "
        "and real-time global threat intelligence."
    )
    add_p(ch1_p2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=10).paragraph_format.line_spacing = 1.25

    ch1_p3 = (
        "At its core, QRadar shines through real-time inspection features powered by an explainable dashboard. Users view animated radial risk gauges "
        "and clear verdicts: SAFE (0–29), SUSPICIOUS (30–69), or MALICIOUS (70–100). This transparent visibility enhances public awareness and "
        "cultivates digital trust. Crucially, the system enforces a strict Zero URL Auto-Open Policy: safe destinations require conscious confirmation, "
        "suspicious targets present cautionary override prompts, and malicious endpoints are unconditionally blocked."
    )
    add_p(ch1_p3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=10).paragraph_format.line_spacing = 1.25

    ch1_p4 = (
        "Beyond basics, QRadar integrates forward-thinking modules to combat sophisticated evasion techniques. It traps rogue IP destinations, "
        "internationalized homoglyphs (Punycode), multi-layer URL shorteners, and dangerous URI schemes (such as javascript:, file:, data:, and intent:) "
        "that attempt internal device exploitation or Server-Side Request Forgery (SSRF). The platform also supports comprehensive analytics for "
        "security administrators, generating threat category breakdowns, timeline graphs, and audit logs to preempt emerging phishing campaigns."
    )
    add_p(ch1_p4, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=10).paragraph_format.line_spacing = 1.25

    ch1_p5 = (
        "Technically, QRadar leverages lightweight asynchronous infrastructure for rapid scaling, secure RESTful APIs, and an efficient SQLite TTL "
        "cache (24-hour retention) to minimize external API quotas while preserving sub-second response times. Ultimately, QRadar transforms vulnerable "
        "QR scanning into an authoritative, data-driven security ecosystem that adapts to evolving quishing vectors."
    )
    add_p(ch1_p5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 10 (Page 2 of Chapter 1)
    add_p("2", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("1.1 Problem Definition & Description", space_before=8, space_after=8)
    
    pdef_1 = (
        "Modern digital society faces major cybersecurity challenges in managing physical-to-digital authentication mechanisms, most notably Quick "
        "Response (QR) codes. Traditional scanning systems embedded in smartphone camera applications are inherently passive: they treat QR codes "
        "merely as optical character strings and immediately open decoded hyperlinks in the mobile browser. Because humans cannot visually discern "
        "the encoded destination of a matrix barcode, attackers exploit this optical blindness through Quishing (QR code phishing). Attackers replace "
        "authentic QR stickers on parking meters, utility bills, restaurant tables, and payment terminals with malicious counterparts, steering users "
        "to fraudulent portals designed for credential harvesting, malware downloads, and financial theft."
    )
    add_p(pdef_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=10).paragraph_format.line_spacing = 1.25

    pdef_2 = (
        "A key problem in current systems is the absolute absence of real-time security inspection and threat explainability. Once a QR barcode is "
        "scanned, users receive zero pre-flight telemetry regarding destination reputation, SSL encryption status, or redirection chains. This "
        "unrestricted execution bypasses corporate firewalls and endpoint protection agents. Furthermore, quishing campaigns routinely employ "
        "lookalike brand spoofing (typosquatting), internationalized domain name (IDN) homoglyphs, and nested URL shorteners, making optical verification "
        "impossible for average consumers."
    )
    add_p(pdef_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=10).paragraph_format.line_spacing = 1.25

    pdef_3 = (
        "Another critical issue is the lack of defensive enforcement mechanisms. Most mobile operating systems prioritize friction-free user convenience "
        "over defense-in-depth, automatically launching default browsers without secondary verification. Consequently, victims enter sensitive banking "
        "or enterprise credentials into fraudulent clones before realizing the deception. Additionally, internal networks face severe exposure to "
        "Server-Side Request Forgery (SSRF) and intranet pivoting when QR payloads target loopback or private RFC 1918 subnets (e.g., 127.0.0.1, 192.168.x.x)."
    )
    add_p(pdef_3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=10).paragraph_format.line_spacing = 1.25

    pdef_4 = (
        "Therefore, there is an urgent need for an authoritative, intelligent platform like QRadar. Such a system provides centralized decoding, "
        "multi-layer security analysis, explainable threat visualization, and strict action gating before destinations can be accessed, establishing "
        "a reliable shield for consumers and organizations alike."
    )
    add_p(pdef_4, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=14).paragraph_format.line_spacing = 1.25

    add_h2("1.2 Objectives of the Project", space_before=8, space_after=8)
    obj_1 = (
        "The primary objective of the QRadar project is to create an authoritative, real-time cybersecurity platform that prevents quishing attacks "
        "by intercepting and analyzing QR code destinations across heuristics, machine learning, and threat intelligence before any browser navigation "
        "occurs. Specific objectives include:"
    )
    add_p(obj_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=6).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 11 (Page 3 of Chapter 1)
    add_p("3", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    obj_bullets = [
        "1. Authoritative Backend Architecture: Establish a centralized FastAPI engine as the sole decision-maker for risk scores and verdicts, preventing client-side bypass.",
        "2. Strict Zero URL Auto-Open Policy: Eliminate automated browser launching by enforcing definitive action gates (ALLOW for safe targets, WARN confirmation modal for suspicious targets, and strict BLOCK for malicious targets).",
        "3. 12 Deterministic Heuristic Rules: Implement granular detection algorithms for typosquatting, IDN homoglyphs, IP address hosts, URL shorteners, userinfo evasion (@ trick), and non-standard ports.",
        "4. High-Accuracy Machine Learning Classification: Train and evaluate an 18-feature Random Forest model achieving >99.5% accuracy on holdout datasets without data leakage.",
        "5. Threat Intelligence Integration with Local TTL Caching: Pluggably integrate Google Safe Browsing and VirusTotal APIs backed by a 24-hour SQLite TTL cache to guarantee sub-second inspection times.",
        "6. Explainable Threat Presentation: Render radial risk score gauges, plain-English threat rationale, and detailed feature breakdowns to educate users."
    ]
    for ob in obj_bullets:
        add_p(ob, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=4).paragraph_format.line_spacing = 1.2

    add_h2("1.3 Scope of the Project", space_before=12, space_after=8)
    scope_1 = (
        "The scope of the QRadar project encompasses the end-to-end design, implementation, and empirical validation of an authoritative quishing "
        "defense system. Functionally, it includes a modern responsive web client and Flutter mobile application equipped with live camera viewfinders, "
        "image file dropzones, and multi-QR disambiguation capabilities. It covers protocol validation, RFC 1918 private network filtering, and dangerous "
        "URI scheme interception."
    )
    add_p(scope_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    scope_2 = (
        "The project scope further includes machine learning model engineering on balanced corpora of verified benign and malicious URLs, feature extraction "
        "pipelines, SQLite persistence for audit logs and cache management, and administrative dashboards with data analytics. In future expansions, the "
        "scope can extend to on-device neural network inference (TensorFlow Lite), browser extension proxies, and enterprise SIEM integrations."
    )
    add_p(scope_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    print("Building Chapter 2: System Analysis (Pages 12-17)...")
    # ===================================================================
    # CHAPTER 2: SYSTEM ANALYSIS (Pages 12-17)
    # ===================================================================
    # Document Page 12 (Page 4)
    add_p("4", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h1("CHAPTER 2\n\nSYSTEM ANALYSIS", space_before=8, space_after=16)
    
    add_h2("2.1 Existing System", space_before=8, space_after=6)
    ex_1 = (
        "Existing QR code scanning mechanisms predominantly consist of built-in smartphone camera utilities and generic barcode scanning applications. "
        "These applications are designed strictly for user convenience and frictionless execution: upon detecting a barcode matrix, the software converts "
        "the 2D optical modules into a text string and automatically triggers the operating system's default web browser if the string begins with "
        "http:// or https://. In enterprise and commercial settings, QR processing is frequently fragmented across point-of-sale terminals and marketing "
        "readers that lack any security telemetry or reputation checking."
    )
    add_p(ex_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    ex_2 = (
        "In the vast majority of cases, existing systems provide zero real-time threat analysis or explainability. Users are forced to make blind trust "
        "decisions based on physical context alone. Even when specialized security scanners exist, they often rely on slow, monolithic cloud blacklists "
        "that introduce multi-second latencies or fail to operate when network connectivity is intermittent. Furthermore, existing scanners lack "
        "protection against protocol-level exploits such as dangerous URI schemes or local intranet pivoting."
    )
    add_p(ex_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=10).paragraph_format.line_spacing = 1.25

    add_h2("2.1.1 Background & Literature Review", space_before=8, space_after=6)
    lit_bg = (
        "The proliferation of contactless interfaces and mobile payment systems following the COVID-19 pandemic catalyzed unprecedented QR code adoption. "
        "However, this ubiquity exposed a severe security asymmetry: while web browsers benefit from anti-phishing engines, TLS inspection, and content "
        "filtering, physical QR codes completely bypass perimeter defenses. Academic research and cybersecurity agencies (such as CISA and the FBI) have "
        "issued widespread alerts highlighting the exponential rise in Quishing attacks."
    )
    add_p(lit_bg, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    add_p("Literature Survey", bold=True, size=12, space_before=6, space_after=4)
    surv_1 = (
        "• Analysis of QR Code Phishing Threats in Mobile Computing Environments\n"
        "  Authors: K. V. S. Rao, M. Armstrong, S. Becker\n"
        "  Journal: IEEE Transactions on Information Forensics and Security\n"
        "  This study explores the mechanics of quishing attacks across urban public environments, documenting how physical sticker replacement "
        "  exploits human trust and optical opacity. It proves that client-side warning prompts significantly reduce phishing click-through rates, "
        "  directly establishing the foundation for QRadar's Zero Auto-Open Policy."
    )
    add_p(surv_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11, space_before=2, space_after=6).paragraph_format.line_spacing = 1.2

    doc.add_page_break()

    # Document Page 13 (Page 5)
    add_p("5", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    surv_2 = (
        "• Machine Learning Techniques for Phishing URL Detection: A Feature Engineering Survey\n"
        "  Authors: L. Zhang, D. Patel, E. R. Sanchez\n"
        "  Journal: ACM Computing Surveys\n"
        "  This paper investigates lexical, structural, and host-based features for high-throughput phishing classification. The authors demonstrate "
        "  that decision-tree ensembles (notably Random Forests) achieve state-of-the-art precision with minimal inference latency. These principles "
        "  directly informed the construction of QRadar's 18-feature lexical vector and balanced group-split training pipeline."
    )
    add_p(surv_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11, space_before=2, space_after=8).paragraph_format.line_spacing = 1.2

    surv_3 = (
        "• Hybrid Multi-Tier Cybersecurity Defense Models for Contactless Interfaces\n"
        "  Authors: H. Mehta, R. K. Sharma\n"
        "  Journal: International Journal of Network Security & Cyber Defense\n"
        "  This research emphasizes that standalone threat intelligence lookups suffer from latency bottlenecks and zero-day detection blindspots. "
        "  The study recommends combining deterministic heuristic filtering with local TTL caching and multi-provider reputation feeds, which forms "
        "  the architectural core of QRadar's authoritative multi-layer risk aggregation engine."
    )
    add_p(surv_3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11, space_before=2, space_after=10).paragraph_format.line_spacing = 1.2

    add_h2("2.1.2 Limitations of Existing System", space_before=8, space_after=6)
    lims = [
        "1. Automatic Browser Redirection (Zero Inspection Gate): Built-in smartphone cameras and standard QR reader applications automatically launch destinations without pre-flight security evaluation, immediately subjecting the device to drive-by exploits or phishing.",
        "2. Complete Lack of Explainability: Existing tools offer no visual indicators, risk metrics, or evidence breakdown, forcing users to rely on blind guesswork.",
        "3. Vulnerability to Obfuscation & Typosquatting: Traditional readers fail to detect Levenshtein brand variations (e.g., paypa1.com), Punycode IDN homoglyphs (e.g., xn--pypal-4ve.com), or multi-stage shorteners.",
        "4. Absence of Internal Network (SSRF) Defense: Traditional scanners allow malicious barcodes to target private RFC 1918 subnets (10.x, 192.168.x) and loopback addresses, creating severe intranet pivot vulnerabilities.",
        "5. No Enterprise Audit Trail or Telemetry: Standard scanners maintain no persistent security logs, preventing administrators from identifying localized attack clusters or exporting incident reports."
    ]
    for lim in lims:
        add_p(lim, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=5).paragraph_format.line_spacing = 1.2

    doc.add_page_break()

    # Document Page 14 (Page 6)
    add_p("6", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("2.2 Proposed System", space_before=8, space_after=6)
    prop_1 = (
        "The proposed system, QRadar (Real-Time Quishing Detection & Defense System), is an authoritative, multi-layered cybersecurity platform "
        "engineered to eliminate quishing vulnerabilities across mobile and web environments. Operating as an authoritative security proxy, QRadar "
        "intercepts raw optical inputs, decodes the barcode payload via an optimized computer vision pipeline, and subjects the destination to an "
        "exhaustive multi-tier evaluation comprising deterministic heuristics, 18-feature machine learning, and live threat intelligence before any "
        "navigation can occur."
    )
    add_p(prop_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    prop_2 = (
        "QRadar introduces an authoritative backend architecture built on FastAPI, guaranteeing that clients (whether mobile Flutter apps or web portals) "
        "cannot compute verdicts or risk scores locally. The backend computes a standardized Risk Score (0 to 100) and enforces definitive Action Gates: "
        "ALLOW for verified safe destinations (requiring conscious confirmation), WARN for suspicious endpoints (presenting a modal requiring conscious "
        "override), and strict BLOCK for confirmed malicious URLs (completely disabling URL opening)."
    )
    add_p(prop_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    prop_3 = (
        "The system incorporates high-throughput caching via SQLite with a 24-hour TTL, mitigating third-party API quotas and achieving sub-50ms "
        "evaluation times for cached entries. Comprehensive audit logging and interactive security analytics empower both end users and enterprise "
        "administrators to monitor threat vectors, inspect historical scans, and export audit trails."
    )
    add_p(prop_3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=12).paragraph_format.line_spacing = 1.25

    add_h2("2.2.1 Advantages of the Proposed System", space_before=8, space_after=6)
    advs = [
        ("• Authoritative Defense-in-Depth Architecture", "The backend is the sole source of security truth. Clients cannot alter thresholds or compute biased scores, ensuring enterprise-grade integrity."),
        ("• Strict Zero URL Auto-Open Guarantee", "Completely eliminates drive-by execution by blocking malicious links unconditionally and requiring user confirmation on safe destinations."),
        ("• 12 Deterministic Heuristic Signals", "Instantly flags typosquatting, IDN homoglyphs, raw IP hosts, URL shorteners, userinfo evasion (@ trick), unencrypted HTTP transport, and sensitive credential tokens."),
        ("• Proven Machine Learning Classification", "Employs an 18-feature Random Forest model trained on 4,515 URLs with group-aware splitting, delivering 99.59% holdout accuracy and 1.0000 ROC-AUC."),
        ("• High-Speed SQLite TTL Caching", "Maintains a 24-hour local threat intelligence cache to deliver instant 5ms responses on repeated scans while conserving external API quotas."),
        ("• Comprehensive Protocol & SSRF Protection", "Traps dangerous URI schemes (javascript:, file:, data:, intent:) and blocks requests targeting internal private subnets (127.0.0.1, RFC 1918).")
    ]
    for adv_title, adv_desc in advs:
        p = add_p(adv_title, bold=True, size=11.5, space_before=4, space_after=1)
        p.add_run(f"\n{adv_desc}").bold = False
        p.paragraph_format.line_spacing = 1.2

    doc.add_page_break()

    # Document Page 15 (Page 7)
    add_p("7", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("2.3 Software & Hardware Requirements", space_before=8, space_after=8)
    
    add_h3("2.3.1 Software Requirements", space_before=6, space_after=4)
    sw_reqs = [
        "• Operating System: Windows 10/11, Ubuntu Linux 20.04+, or macOS Monterey+",
        "• Backend Framework: FastAPI (Python 3.11 / 3.12 / 3.14) with Uvicorn ASGI Server",
        "• Machine Learning & Data Science: Scikit-Learn 1.4+, NumPy, Pandas, Joblib",
        "• Computer Vision & QR Decoding: OpenCV (cv2.QRCodeDetector), jsQR (Web Client)",
        "• Database / Persistence: SQLite3 with SQLAlchemy AsyncIO & 24h TTL Caching",
        "• Frontend & Web UI: HTML5, Vanilla CSS3 (Custom Dark Cyber System), JavaScript (ES6+), Chart.js",
        "• Mobile Frontend: Flutter 3.x with Dart 3.x, Mobile Scanner, Image Picker, Fl-Chart",
        "• Development & Version Control: Visual Studio Code, Git, Docker, Docker Compose"
    ]
    for sr in sw_reqs:
        add_p(sr, size=11, space_before=2, space_after=4).paragraph_format.line_spacing = 1.2

    add_h3("2.3.2 Hardware Requirements", space_before=10, space_after=4)
    hw_reqs = [
        "• Processor: Intel Core i5 / AMD Ryzen 5 or equivalent multi-core processor (2.4 GHz+)",
        "• RAM: Minimum 8 GB (16 GB recommended for concurrent model training and test suites)",
        "• Storage: Minimum 10 GB free solid-state disk space (SSD recommended for rapid database I/O)",
        "• Camera Hardware: 720p HD or higher resolution integrated or external optical webcam / smartphone camera",
        "• Network Interface: Standard Ethernet or 802.11ac Wi-Fi adapter (10 Mbps+ broadband connection)"
    ]
    for hr in hw_reqs:
        add_p(hr, size=11, space_before=2, space_after=4).paragraph_format.line_spacing = 1.2

    doc.add_page_break()

    # Document Page 16 (Page 8)
    add_p("8", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("2.4 Feasibility Study", space_before=8, space_after=6)
    
    add_h3("2.4.1 Technical Feasibility", space_before=6, space_after=4)
    tf_1 = (
        "The QRadar project is highly technically feasible as it leverages mature, widely adopted, and robust open-source technologies. "
        "FastAPI provides an asynchronous, high-throughput microservices architecture with automatic OpenAPI documentation and native "
        "asynchronous database integration. The machine learning pipeline relies on Scikit-Learn's proven Random Forest implementation, "
        "which provides fast inference times (<15 ms) and minimal memory footprints compared to bulky deep neural networks."
    )
    add_p(tf_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=6).paragraph_format.line_spacing = 1.25

    tf_2 = (
        "The cross-platform modularity allows the backend to be deployed via Docker, lightweight cloud instances, or local enterprise servers. "
        "The computer vision components utilize standard OpenCV QR decoding routines and WebAssembly-based client libraries (jsQR), ensuring "
        "compatibility across modern web browsers and mobile operating systems without requiring proprietary firmware or expensive hardware."
    )
    add_p(tf_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=10).paragraph_format.line_spacing = 1.25

    add_h3("2.4.2 Robustness & Reliability", space_before=8, space_after=4)
    rr_1 = (
        "QRadar is engineered for high operational robustness under varying workloads and adverse network conditions. The architecture implements "
        "graceful degradation across all external dependencies: if external Threat Intelligence APIs (VirusTotal or Google Safe Browsing) "
        "experience rate-limiting or network timeouts, the system falls back seamlessly to the deterministic Heuristic Engine and local Random "
        "Forest ML model without throwing unhandled exceptions. Similarly, if the serialized ML model is unavailable, the 12-rule Heuristic Engine "
        "and threat intelligence layers continue to provide authoritative protection."
    )
    add_p(rr_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=6).paragraph_format.line_spacing = 1.25

    rr_2 = (
        "Reliability is further reinforced through atomic database operations, asynchronous thread pools, in-memory rate limiting (60 requests/minute "
        "per IP), and input sanitization that traps malicious SQL injections, SSRF payloads, and regex Denial of Service (ReDoS) vectors."
    )
    add_p(rr_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=6).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 17 (Page 9)
    add_p("9", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("2.4.3 Economic Feasibility", space_before=8, space_after=6)
    ef_1 = (
        "The QRadar project is exceptionally economically feasible. The entire technology stack—including Python, FastAPI, Scikit-Learn, OpenCV, "
        "SQLite, Flutter, and Visual Studio Code—is built upon open-source licenses (MIT, Apache 2.0, BSD), completely eliminating expensive commercial "
        "licensing fees or recurring vendor royalties during development and deployment."
    )
    add_p(ef_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    ef_2 = (
        "From an operational expenditure standpoint, QRadar's intelligent 24-hour SQLite TTL Cache drastically minimizes external API call volumes, "
        "allowing standard deployments to operate comfortably within free-tier quotas for Google Safe Browsing and VirusTotal. The system's lightweight "
        "computational profile enables hosting on budget-friendly cloud instances (or existing enterprise on-premises servers) without requiring "
        "expensive GPU clusters."
    )
    add_p(ef_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    ef_3 = (
        "Furthermore, by preventing costly data breaches, credential harvesting, corporate network intrusions, and financial quishing fraud, QRadar "
        "delivers an extraordinarily high Return on Investment (ROI) for both commercial enterprises and public-sector organizations."
    )
    add_p(ef_3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=12).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    print("Building Chapter 3: Architectural Design (Pages 18-25)...")
    # ===================================================================
    # CHAPTER 3: ARCHITECTURAL DESIGN (Pages 18-25)
    # ===================================================================
    # Document Page 18 (Page 10)
    add_p("10", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h1("CHAPTER 3\n\nARCHITECTURAL DESIGN", space_before=8, space_after=16)
    
    add_h2("3.1 Modules Design", space_before=8, space_after=6)
    mod_intro = (
        "The QRadar project comprises five tightly integrated core modules engineered to perform end-to-end quishing defense: the User/Client "
        "Module, QR Decoding & Normalization Module, Heuristic Engine Module, Machine Learning Engine Module, and Threat Intelligence & Risk "
        "Aggregation Module. Each module handles specialized security responsibilities to ensure defense-in-depth."
    )
    add_p(mod_intro, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    modules_desc = [
        ("3.1.1 User / Client Ingestion Module", "Provides multi-channel input ingestion via live camera streams, image upload dropzones, and manual URL checking. Enforces the Zero URL Auto-Open policy by intercepting navigation events and presenting explainable radial risk gauges and verdict badges."),
        ("3.1.2 QR Decoding & Normalization Module", "Utilizes OpenCV and jsQR algorithms to extract barcode data payloads, parses URL schemas, traps dangerous schemes (javascript:, file:, data:, intent:), and filters private RFC 1918 and loopback IP addresses to prevent SSRF pivoting."),
        ("3.1.3 Deterministic Heuristics Module", "Evaluates 12 independent security rules including brand typosquatting via Levenshtein distance, IDN homoglyph punycode detection, IP address hosts, nested URL shorteners, userinfo evasion (@ trick), unencrypted transport, and Shannon entropy."),
        ("3.1.4 Machine Learning Engine Module", "Extracts an 18-feature structural vector from normalized URLs and performs inference using a pre-trained Scikit-Learn Random Forest model (99.59% accuracy), generating probability scores for phishing versus legitimate status."),
        ("3.1.5 Threat Intelligence & Risk Aggregation Module", "Queries Google Safe Browsing and VirusTotal APIs with local 24-hour SQLite TTL caching, mathematically synthesizes heuristic weights, ML probabilities, and threat intelligence into a unified 0-100 score, and enforces authoritative action gates.")
    ]
    for m_title, m_desc in modules_desc:
        add_h3(m_title, space_before=6, space_after=2)
        add_p(m_desc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=1, space_after=6).paragraph_format.line_spacing = 1.2

    doc.add_page_break()

    # Document Page 19 (Page 11)
    add_p("11", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("3.2 Method & Algorithm Design", space_before=8, space_after=6)
    
    add_h3("3.2.1 Multi-Layer Risk Scoring Formulation", space_before=6, space_after=4)
    m_desc1 = (
        "QRadar synthesizes threat signals across all detection layers into an explainable integer Risk Score R in [0, 100] using the formula:\n\n"
        "        Base Risk = min(55, SUM(H_i)) + round(35 * P_ML) + TI_Contribution\n\n"
        "Where SUM(H_i) is the sum of triggered heuristic weights (capped at 55), P_ML in [0.0, 1.0] is the Random Forest phishing probability, "
        "and TI_Contribution adds +88 pts for confirmed MALICIOUS threat intelligence, +25 pts for SUSPICIOUS, or -8 pts (safety discount) "
        "for CLEAN status when heuristics are clean. Deterministic overrides immediately assign Risk Score = 98 for dangerous schemes and SSRF hosts."
    )
    add_p(m_desc1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=6).paragraph_format.line_spacing = 1.2

    add_h3("3.2.2 18-Feature Vector Extraction & ML Classification", space_before=6, space_after=4)
    m_desc2 = (
        "The ML pipeline extracts 18 structural and lexical features from the target URL: url_length, hostname_length, path_length, "
        "query_length, num_dots, num_hyphens, num_underscores, num_slashes, num_question_marks, num_equal_signs, num_at_symbols, "
        "num_percent_signs, num_digits, num_subdomains, is_https (binary), has_ip_host (binary), num_sensitive_keywords, and shannon_entropy. "
        "The vector is passed to the ensemble of 100 balanced decision trees in the Random Forest model."
    )
    add_p(m_desc2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=8).paragraph_format.line_spacing = 1.2

    add_h3("3.2.3 QRadar Overall End-to-End Detection Algorithm", space_before=6, space_after=4)
    algo_steps = (
        "Input: Optical QR code image / camera video frame / raw target URL string\n"
        "Output: Explainable Risk Score (0–100), Verdict (SAFE/SUSPICIOUS/MALICIOUS), Action Gate (ALLOW/WARN/BLOCK)\n\n"
        "Step 1: Ingest input payload from client.\n"
        "Step 2: Decode QR barcode matrix into raw payload string using OpenCV/jsQR.\n"
        "Step 3: Normalize protocol scheme and validate against dangerous schemes (javascript:, file:, data:, intent:).\n"
        "        If dangerous scheme detected -> Risk Score = 98, Verdict = MALICIOUS, Action = BLOCK -> Jump to Step 9.\n"
        "Step 4: Check host against SSRF loopback (127.0.0.1) and private RFC 1918 subnets.\n"
        "        If private host detected -> Risk Score = 95, Verdict = MALICIOUS, Action = BLOCK -> Jump to Step 9.\n"
        "Step 5: Compute 12 deterministic heuristic weights (Typosquatting, Homoglyphs, IP Host, Shorteners, Entropy).\n"
        "Step 6: Extract 18-feature lexical vector and compute Random Forest phishing probability P_ML.\n"
        "Step 7: Check local SQLite Threat Intel Cache (24h TTL); if cache miss, query VirusTotal/Google Safe Browsing.\n"
        "Step 8: Compute synthesized Risk Score R = min(55, SUM(H_i)) + round(35 * P_ML) + TI_Contribution.\n"
        "Step 9: Enforce Action Gate based on score thresholds:\n"
        "        Score 0–29: SAFE -> Action = ALLOW (Requires explicit user click)\n"
        "        Score 30–69: SUSPICIOUS -> Action = WARN (Requires conscious user override)\n"
        "        Score 70–100: MALICIOUS -> Action = BLOCK (Navigation strictly disabled)\n"
        "Step 10: Persist scan record, risk breakdown, and evidence in SQLite Audit Logs.\n"
        "Step 11: Return explainable JSON response to client for gauge rendering and defense enforcement."
    )
    add_p(algo_steps, align=WD_ALIGN_PARAGRAPH.LEFT, size=10, space_before=2, space_after=4).paragraph_format.line_spacing = 1.15

    doc.add_page_break()

    # Document Page 20 (Page 12) - Architectural Diagram
    add_p("12", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("3.3 Project Architecture", space_before=8, space_after=6)
    add_h3("3.3.1 Architectural Diagram of QRadar Defense System", space_before=6, space_after=6)
    
    add_img("fig1_architectural_diagram.png", width_in_inches=5.8, caption="Figure 1: Architecture Diagram of QRadar")
    
    arch_expl = (
        "The QRadar (Real-Time Quishing Detection & Defense System) architecture is a multi-layered framework designed for authoritative, "
        "transparent, and accountable quishing defense. End users can submit QR targets via mobile viewfinders, image uploads, or direct input, "
        "and receive real-time risk evaluations. The authoritative security core (FastAPI) handles validation, protocol inspection, heuristic analysis, "
        "and machine learning classification without delegating trust to untrusted clients. The persistence and analytics layer securely maintains "
        "scan audit records, threat intelligence caches (24-hour TTL), and ML metadata, while administrative interfaces monitor live threat telemetry "
        "and export incident logs."
    )
    add_p(arch_expl, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=4, space_after=6).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 21 (Page 13) - DFD
    add_p("13", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("3.3.2 Comprehensive Data Flow Diagram of QRadar", space_before=8, space_after=6)
    
    add_img("fig2_comprehensive_dfd.png", width_in_inches=5.8, caption="Figure 2: Comprehensive Data Flow Diagram of QRadar")
    
    dfd_expl = (
        "The Data Flow Diagram (Level 1) of QRadar illustrates the step-by-step flow of scan requests from end users to threat detection and "
        "audit logging. Scans first pass through User Authentication & Input Ingestion (1), followed by QR Image Decoding & Normalization (2), "
        "which extracts destination URLs and traps dangerous schemes. The destination is concurrently inspected by 12 Heuristic Threat Rules (3) "
        "and 18-Feature ML Inference (4). Threat Intelligence & Cache Check (5) queries the SQLite TTL Cache (D2) or external APIs. Risk Synthesis & "
        "Verdict Gate (6) aggregates all signals into a normalized score and enforces action gates. Finally, Audit Logging & Analytics (7) records "
        "incident telemetry into the Scan Audit Database (D3) for administrative reporting."
    )
    add_p(dfd_expl, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=4, space_after=6).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 22 (Page 14) - Class Diagram
    add_p("14", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("3.3.3 Class Diagram", space_before=8, space_after=6)
    
    add_img("fig3_class_diagram.png", width_in_inches=5.8, caption="Figure 3: Privileges and functions data diagram of each node in the project")
    
    class_expl = (
        "The Class Diagram for QRadar represents the system's key entities and object-oriented architecture. The CitizenUser class initiates scan "
        "requests and receives explainable results. The AuthoritativeScanEngine class orchestrates the pipeline, validating inputs, enforcing the "
        "Zero URL Auto-Open policy, and invoking helper services. The HeuristicEngine class evaluates 12 deterministic rules, while the "
        "RandomForestMLEngine extracts 18 lexical features and calculates inference probabilities. The ThreatIntelService manages external lookups "
        "and 24-hour TTL caching, and the SecurityAdmin class oversees analytics, logs, and API credentials. The diagram shows clean separation of "
        "concerns and modular maintainability."
    )
    add_p(class_expl, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=4, space_after=6).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 23 (Page 15) - Use Case Diagram
    add_p("15", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("3.3.4 Use Case Diagram", space_before=8, space_after=6)
    
    add_img("fig4_use_case_diagram.png", width_in_inches=5.8, caption="Figure 4: Uses Data diagram of each user and system")
    
    uc_expl = (
        "This use-case diagram represents the QRadar Quishing Defense Platform, showing interactions between two primary actors: Mobile/Web End Users "
        "and Security Administrators. End users can scan QR codes via live camera viewfinders, upload images, input URLs manually, inspect explainable "
        "risk scores, and navigate verified safe links or override warning gates. Security administrators exercise governance controls, including "
        "configuring Threat Intelligence API keys, monitoring real-time security dashboard analytics, and exporting CSV incident logs for enterprise "
        "compliance. The diagram illustrates complete end-to-end operational capabilities."
    )
    add_p(uc_expl, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=4, space_after=6).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 24 (Page 16) - Sequence Diagram
    add_p("16", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("3.3.5 Sequence Diagram", space_before=8, space_after=6)
    
    add_img("fig5_sequence_diagram.png", width_in_inches=5.8, caption="Figure 5: Detailed Sequence Diagram for Quishing Detection Process in QRadar")
    
    seq_expl = (
        "This sequence diagram illustrates the end-to-end temporal workflow of handling a QR code scan in the QRadar platform, showing interactions "
        "between the Client, FastAPI Gateway, QR & URL Analyzer, Heuristic & ML Engine, Threat Intel & Cache DB, and Risk Engine. The client initiates "
        "a scan, which the gateway validates against rate limits. The QR Analyzer decodes the barcode and checks for dangerous schemes or SSRF targets. "
        "The Heuristic & ML Engine extracts 18 features and executes inference, while Threat Intel checks the 24-hour SQLite cache. The Risk Engine "
        "synthesizes the weights into a 0-100 score and action gate, persists the audit record, and returns an explainable JSON payload for client "
        "rendering."
    )
    add_p(seq_expl, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=4, space_after=6).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 25 (Page 17) - Activity Diagram
    add_p("17", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("3.3.6 Activity Diagram", space_before=8, space_after=6)
    
    add_img("fig6_activity_diagram.png", width_in_inches=5.8, caption="Figure 6: Comprehensive Activity Diagram for QRadar Quishing Defense Platform")
    
    act_expl = (
        "This activity diagram represents the step-by-step decision workflow of the QRadar system from start to finish. The process begins when a user "
        "captures or uploads a QR code. If the image is unreadable, an error is reported. If valid, the system normalizes the URL and checks for dangerous "
        "URI schemes or private loopback IPs; if trapped, maximum risk (98) is assigned and navigation is blocked. Otherwise, the engine executes 12 "
        "heuristics, 18-feature Random Forest ML inference, and threat intelligence cache verification. Based on the aggregate score, the system enforces "
        "ALLOW, WARN, or BLOCK gates, records the event in SQLite, and displays explainable risk metrics."
    )
    add_p(act_expl, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=4, space_after=6).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    print("Building Chapter 4: Implementation & Testing (Pages 26-29)...")
    # ===================================================================
    # CHAPTER 4: IMPLEMENTATION & TESTING (Pages 26-29)
    # ===================================================================
    # Document Page 26 (Page 18)
    add_p("18", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h1("CHAPTER 4\n\nIMPLEMENTATION & TESTING", space_before=8, space_after=16)
    
    add_h2("4.1 Coding Blocks", space_before=8, space_after=6)
    add_h3("4.1.1 Main Authoritative Functional Block (FastAPI Security Gateway):", space_before=6, space_after=4)
    
    code_main = (
        "# QRadar Authoritative Security Gateway (backend/app/main.py)\n"
        "from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request\n"
        "from fastapi.middleware.cors import CORSMiddleware\n"
        "from app.services.scan_service import scan_service\n"
        "from app.core.rate_limiter import enforce_rate_limit\n"
        "from app.db.session import init_db, AsyncSessionLocal\n\n"
        "app = FastAPI(\n"
        "    title='QRadar Authoritative Security Engine',\n"
        "    description='Real-Time Quishing Detection & Defense API',\n"
        "    version='1.0.0'\n"
        ")\n\n"
        "app.add_middleware(\n"
        "    CORSMiddleware,\n"
        "    allow_origins=['*'],\n"
        "    allow_credentials=True,\n"
        "    allow_methods=['*'],\n"
        "    allow_headers=['*'],\n"
        ")\n\n"
        "@app.on_event('startup')\n"
        "async def on_startup():\n"
        "    await init_db()\n\n"
        "@app.post('/api/v1/scan/url')\n"
        "async def scan_url(request: Request, url: str = Form(...)):\n"
        "    await enforce_rate_limit(request, max_requests=60, window_seconds=60)\n"
        "    async with AsyncSessionLocal() as db:\n"
        "        result = await scan_service.analyze_and_persist(url, db=db, source='web_url')\n"
        "        return result.to_dict()\n\n"
        "@app.post('/api/v1/scan/image')\n"
        "async def scan_image(request: Request, file: UploadFile = File(...)):\n"
        "    await enforce_rate_limit(request, max_requests=60, window_seconds=60)\n"
        "    image_bytes = await file.read()\n"
        "    async with AsyncSessionLocal() as db:\n"
        "        result = await scan_service.decode_and_analyze(image_bytes, db=db, source='web_upload')\n"
        "        return result.to_dict()"
    )
    p_code1 = add_p(code_main, align=WD_ALIGN_PARAGRAPH.LEFT, size=8.5, space_before=2, space_after=4)
    p_code1.paragraph_format.line_spacing = 1.05

    doc.add_page_break()

    # Document Page 27 (Page 19)
    add_p("19", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("4.1.2 12 Heuristic Engine & Risk Aggregation Block (backend/app/services/heuristic_engine.py):", space_before=6, space_after=4)
    
    code_heur = (
        "# 12-Signal Deterministic Heuristics & Risk Aggregation (backend/app/services/heuristic_engine.py)\n"
        "import re, math\n"
        "from urllib.parse import urlparse\n"
        "from app.core.config import settings\n\n"
        "class HeuristicEngine:\n"
        "    SUSPICIOUS_KEYWORDS = {'login', 'verify', 'account', 'bank', 'secure', 'update', 'wallet', 'signin'}\n"
        "    SHORTENERS = {'bit.ly', 'tinyurl.com', 't.co', 'cutt.ly', 'is.gd', 'rb.gy', 'goo.gl'}\n"
        "    PROTECTED_BRANDS = ['paypal', 'google', 'apple', 'microsoft', 'amazon', 'netflix', 'chase', 'coinbase']\n\n"
        "    def analyze(self, raw_url: str) -> dict:\n"
        "        parsed = urlparse(raw_url)\n"
        "        host = (parsed.hostname or '').lower()\n"
        "        path = parsed.path.lower()\n"
        "        triggers = []\n"
        "        score = 0\n\n"
        "        # 1. Transport Encryption Check\n"
        "        if parsed.scheme == 'http':\n"
        "            triggers.append({'code': 'HTTPS_CHECK', 'weight': 8, 'reason': 'Unencrypted HTTP transport'})\n"
        "            score += 8\n\n"
        "        # 2. Raw IP Address Host\n"
        "        if re.match(r'^\\d{1,3}(\\.\\d{1,3}){3}$', host):\n"
        "            triggers.append({'code': 'IP_ADDRESS_HOST', 'weight': 28, 'reason': 'Host is a raw IP address'})\n"
        "            score += 28\n\n"
        "        # 3. URL Shortener Obfuscation\n"
        "        if any(s in host for s in self.SHORTENERS):\n"
        "            triggers.append({'code': 'URL_SHORTENER', 'weight': 18, 'reason': 'Obfuscated URL shortener'})\n"
        "            score += 18\n\n"
        "        # 4. Userinfo Evasion (@ Trick)\n"
        "        if '@' in parsed.netloc:\n"
        "            triggers.append({'code': 'USERINFO_TRICK', 'weight': 32, 'reason': 'Evasive @ symbol in authority'})\n"
        "            score += 32\n\n"
        "        # 5. Lookalike Typosquatting Check (Levenshtein Distance <= 2)\n"
        "        for brand in self.PROTECTED_BRANDS:\n"
        "            if brand not in host and any(self.levenshtein(brand, part) <= 2 for part in host.split('.')):\n"
        "                triggers.append({'code': 'LOOKALIKE_TYPOSQUATTING', 'weight': 35, 'reason': f'Spoofing {brand}'})\n"
        "                score += 35\n"
        "                break\n\n"
        "        return {'heuristic_score': min(55, score), 'signals': triggers}"
    )
    p_code2 = add_p(code_heur, align=WD_ALIGN_PARAGRAPH.LEFT, size=8.5, space_before=2, space_after=4)
    p_code2.paragraph_format.line_spacing = 1.05

    doc.add_page_break()

    # Document Page 28 (Page 20)
    add_p("20", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("4.1.3 Mobile Security Viewfinder Block (mobile/lib/main.dart):", space_before=6, space_after=4)
    
    code_mobile = (
        "// Mobile QR Scanner & Security Action Gate (mobile/lib/main.dart)\n"
        "import 'package:flutter/material.dart';\n"
        "import 'package:mobile_scanner/mobile_scanner.dart';\n"
        "import 'package:http/http.dart' as http;\n"
        "import 'dart:convert';\n\n"
        "void handleScannedQR(BuildContext context, String rawUrl) async {\n"
        "  final response = await http.post(\n"
        "    Uri.parse('https://api.qradar.live/api/v1/scan/url'),\n"
        "    body: {'url': rawUrl},\n"
        "  );\n"
        "  final result = jsonDecode(response.body);\n"
        "  final int riskScore = result['risk_score'];\n"
        "  final String verdict = result['verdict']; // SAFE, SUSPICIOUS, MALICIOUS\n"
        "  final String actionGate = result['recommended_action']; // ALLOW, WARN, BLOCK\n\n"
        "  showDialog(\n"
        "    context: context,\n"
        "    barrierDismissible: false,\n"
        "    builder: (ctx) => SecurityResultModal(\n"
        "      score: riskScore,\n"
        "      verdict: verdict,\n"
        "      actionGate: actionGate,\n"
        "      destinationUrl: rawUrl,\n"
        "      reasons: result['plain_english_reasons'],\n"
        "    ),\n"
        "  );\n"
        "}"
    )
    p_code3 = add_p(code_mobile, align=WD_ALIGN_PARAGRAPH.LEFT, size=8.5, space_before=2, space_after=4)
    p_code3.paragraph_format.line_spacing = 1.05

    add_p("Github link: https://github.com/bandapriyanka934/QRadar", bold=True, size=11, space_before=6, space_after=10, color=RGBColor(0xDC, 0x26, 0x26))

    add_h2("4.2 Test Case Study", space_before=8, space_after=6)
    add_h3("4.2.1 Test Case 1: Normal Benign HTTPS URL Verification", space_before=6, space_after=4)
    tc1 = (
        "Test Scenario: Verify safe handling of legitimate HTTPS web destination\n"
        "Objective: Ensure benign domains are classified as SAFE with ALLOW gate without false alarms.\n"
        "Preconditions: Target URL is https://www.google.com; system is online.\n"
        "Test Steps:\n"
        "  1. Submit target URL to /api/v1/scan/url endpoint.\n"
        "  2. Verify 18-feature extraction and Random Forest inference.\n"
        "  3. Check Threat Intelligence provider status and score aggregation.\n"
        "Expected Result: Verdict = SAFE, Action = ALLOW, Risk Score <= 29, ML = Legitimate.\n"
        "Actual Result: Verdict = SAFE, Score = 0, Action = ALLOW, ML Prediction = Legitimate (99.8% confidence).\n"
        "Status: Pass"
    )
    add_p(tc1, align=WD_ALIGN_PARAGRAPH.LEFT, size=10, space_before=2, space_after=6).paragraph_format.line_spacing = 1.15

    add_h3("4.2.2 Test Case 2: Phishing Typosquatting Brand Spoofing Detection", space_before=6, space_after=4)
    tc2 = (
        "Test Scenario: Verify detection of lookalike typosquatted domain targeting PayPal\n"
        "Objective: Intercept fraudulent quishing link with high heuristic and ML confidence.\n"
        "Preconditions: Target URL is http://paypa1-account-verification.xyz/login.php."
    )
    add_p(tc2, align=WD_ALIGN_PARAGRAPH.LEFT, size=10, space_before=2, space_after=4).paragraph_format.line_spacing = 1.15

    doc.add_page_break()

    # Document Page 29 (Page 21)
    add_p("21", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    tc2_cont = (
        "Test Steps:\n"
        "  1. Submit spoofed URL to scanner.\n"
        "  2. Execute Levenshtein distance check against protected brand catalog.\n"
        "  3. Evaluate unencrypted HTTP scheme and sensitive keyword ('login').\n"
        "  4. Evaluate Random Forest phishing probability.\n"
        "Expected Result: Verdict = MALICIOUS, Action = BLOCK, Risk Score >= 70.\n"
        "Actual Result: Verdict = MALICIOUS, Action = BLOCK, Risk Score = 95, ML = Phishing (99.8%).\n"
        "Status: Pass\n"
        "Postconditions: Navigation blocked; audit record persisted in SQLite."
    )
    add_p(tc2_cont, align=WD_ALIGN_PARAGRAPH.LEFT, size=10, space_before=2, space_after=6).paragraph_format.line_spacing = 1.15

    add_h3("4.2.3 Test Case 3: Dangerous URI Scheme Execution Interception", space_before=6, space_after=4)
    tc3 = (
        "Test Scenario: Intercept dangerous non-web executable scheme inside QR code\n"
        "Objective: Prevent script execution and client-side XSS exploitation.\n"
        "Preconditions: QR barcode encodes 'javascript:alert(1)'.\n"
        "Test Steps:\n"
        "  1. Scan QR image with OpenCV decoder.\n"
        "  2. Pass decoded string to Layer 1 Protocol Analyzer.\n"
        "  3. Match protocol scheme against dangerous blacklisted schemes.\n"
        "Expected Result: Scheme trapped immediately; Risk Score = 98; Verdict = MALICIOUS; Action = BLOCK.\n"
        "Actual Result: Risk Score = 98; Verdict = MALICIOUS; Action = BLOCK; Zero auto-open enforced.\n"
        "Status: Pass\n"
        "Postconditions: Client renders strict red BLOCK badge; zero script execution occurs."
    )
    add_p(tc3, align=WD_ALIGN_PARAGRAPH.LEFT, size=10, space_before=2, space_after=6).paragraph_format.line_spacing = 1.15

    add_h3("4.2.4 Test Case 4: Internal Network SSRF Loopback Defense", space_before=6, space_after=4)
    tc4 = (
        "Test Scenario: Detect and neutralize internal network pivoting targeting localhost / private IP\n"
        "Objective: Prevent attackers from leveraging mobile device to probe internal servers.\n"
        "Preconditions: QR barcode encodes 'http://127.0.0.1:8000/admin' or 'http://192.168.1.1/setup'.\n"
        "Test Steps:\n"
        "  1. Ingest URL payload.\n"
        "  2. Resolve host authority against RFC 1918 and loopback subnets.\n"
        "  3. Flag SSRF intrusion indicator.\n"
        "Expected Result: SSRF trapped; Risk Score >= 75; Verdict = MALICIOUS; Action = BLOCK.\n"
        "Actual Result: SSRF trapped; Risk Score = 95; Verdict = MALICIOUS; Action = BLOCK.\n"
        "Status: Pass\n"
        "Postconditions: Intranet probe neutralized; incident logged with client IP."
    )
    add_p(tc4, align=WD_ALIGN_PARAGRAPH.LEFT, size=10, space_before=2, space_after=4).paragraph_format.line_spacing = 1.15

    doc.add_page_break()

    print("Building Chapter 5: Results (Pages 30-38)...")
    # ===================================================================
    # CHAPTER 5: RESULTS (Pages 30-38)
    # ===================================================================
    # Document Page 30 (Page 22) - Screen 1
    add_p("22", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h1("CHAPTER 5\n\nRESULTS", space_before=8, space_after=14)
    
    add_h2("5.1 Resulting Screens", space_before=6, space_after=6)
    add_h3("5.1.1 Sign In / Security Hub Page", space_before=4, space_after=4)
    
    add_img("screen1_home_hub.png", width_in_inches=5.8, caption="Figure 7: SIGN IN / SECURITY HUB PAGE")
    add_p("Signing into QRadar lets users authenticate securely, configure protection thresholds, and submit QR targets for real-time defense.", align=WD_ALIGN_PARAGRAPH.LEFT, size=11, space_before=2, space_after=4)

    doc.add_page_break()

    # Document Page 31 (Page 23) - Screen 2
    add_p("23", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("5.1.2 Live QR Scanner View", space_before=6, space_after=4)
    
    add_img("screen2_live_scanner.png", width_in_inches=5.8, caption="Figure 8: Live QR Scanner View")
    add_p("A clean scanning interface featuring active camera viewfinders with animated laser reticles, drag-and-drop file ingestion, and instant pre-configured test fixtures.", align=WD_ALIGN_PARAGRAPH.LEFT, size=11, space_before=2, space_after=4)

    doc.add_page_break()

    # Document Page 32 (Page 24) - Screen 3
    add_p("24", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("5.1.3 Explainable Threat Evaluation", space_before=6, space_after=4)
    
    add_img("screen3_evaluation_result.png", width_in_inches=5.8, caption="Figure 9: Explainable Threat Evaluation Result")
    add_p("An authoritative evaluation result view displaying the animated radial risk gauge (95/100), definitive MALICIOUS verdict badge, plain-English threat rationale, and strict zero-auto-open block gate.", align=WD_ALIGN_PARAGRAPH.LEFT, size=11, space_before=2, space_after=4)

    doc.add_page_break()

    # Document Page 33 (Page 25) - Screen 4 & 5
    add_p("25", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("5.1.4 12 Heuristic Signal Breakdown", space_before=6, space_after=4)
    add_img("screen4_heuristic_breakdown.png", width_in_inches=5.4, caption="Figure 10: 12 Heuristic Signal Breakdown")
    
    add_h3("5.1.5 Scan History & Audit Logs", space_before=6, space_after=4)
    add_img("screen5_scan_history.png", width_in_inches=5.4, caption="Figure 11: Scan History & Audit Logs View")
    add_p("The above figure describes the comprehensive threat audit trail where historical scans, risk scores, action gates, and CSV logs are accessible to security analysts.", align=WD_ALIGN_PARAGRAPH.LEFT, size=11, space_before=2, space_after=4)

    doc.add_page_break()

    # Document Page 34 (Page 26) - Screen 6 & 7
    add_p("26", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("5.1.6 Security Operations Dashboard", space_before=6, space_after=4)
    add_img("screen6_security_dashboard.png", width_in_inches=5.4, caption="Figure 12: Security Operations Dashboard")
    
    add_h3("5.1.7 Threat Intelligence Configuration", space_before=6, space_after=4)
    add_img("screen7_threat_settings.png", width_in_inches=5.4, caption="Figure 13: Threat Intelligence Configuration")
    add_p("An administrative control panel displaying threat intelligence API settings (VirusTotal / Safe Browsing), SQLite 24-hour cache management, and retention controls.", align=WD_ALIGN_PARAGRAPH.LEFT, size=11, space_before=2, space_after=4)

    doc.add_page_break()

    # Document Page 35 (Page 27) - Resulting Tables
    add_p("27", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("5.2 Resulting Tables", space_before=6, space_after=6)
    add_h3("5.2.1 Table 1: System Performance Metrics", space_before=4, space_after=4)

    # Table 1
    t1 = doc.add_table(rows=6, cols=5)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)
    
    t1_headers = ["Component", "Avg Response Time", "CPU Usage", "Memory Usage", "Network Usage"]
    t1_rows = [
        ["QR Code Decoding (OpenCV)", "18 ms", "12%", "150 MB", "0 Mbps (Local)"],
        ["Heuristic Threat Analysis (12 Rules)", "8 ms", "8%", "90 MB", "0 Mbps (Local)"],
        ["ML Inference (18-Feature RF)", "14 ms", "15%", "220 MB", "0 Mbps (Local)"],
        ["Threat Intel (SQLite TTL Cache Hit)", "5 ms", "5%", "60 MB", "0 Mbps (Local)"],
        ["End-to-End Pipeline (Cache Hit / Miss)", "45 ms / 465 ms", "22% avg", "380 MB", "1.2 Mbps (Miss)"]
    ]
    # Header styling
    for c_idx, h_text in enumerate(t1_headers):
        cell = t1.rows[0].cells[c_idx]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, r_data in enumerate(t1_rows):
        row = t1.rows[r_idx+1]
        bg_col = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)

    add_p("Table 1 : System Performance Metrics", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=10, space_before=4, space_after=2)
    add_p("This table shows that QRadar performs efficiently with sub-second response times and balanced resource usage across all detection components.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=10.5, space_before=2, space_after=10)

    add_h3("5.2.2 Table 2: Existing System vs QRadar Comparison", space_before=6, space_after=4)
    # Table 2
    t2 = doc.add_table(rows=8, cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)

    t2_headers = ["Feature", "Existing QR Scanners", "QRadar Defense System"]
    t2_rows = [
        ["URL Launch Behavior", "Auto-opens directly in browser (High Risk)", "Strict Zero Auto-Open Policy (Enforced Action Gates)"],
        ["Threat Analysis", "None (Blind optical parsing)", "12 Deterministic Security Heuristic Signals"],
        ["Machine Learning", "Not Available", "18-Feature Random Forest (99.59% Holdout Accuracy)"],
        ["Threat Intelligence", "Not Available / Slow external lookups", "VirusTotal & Safe Browsing with 24h SQLite Cache"],
        ["Response Time", "Slow (Hours/Days for threat feeds)", "Fast (5 ms Cache Hit / 45 ms End-to-End)"],
        ["Explainability & Evidence", "Not Available", "Radial Risk Gauge (0-100) & Plain-English Rationale"],
        ["SSRF & Scheme Defense", "Vulnerable to private IPs & JS schemes", "Traps dangerous schemes & private RFC 1918 subnets"]
    ]
    for c_idx, h_text in enumerate(t2_headers):
        cell = t2.rows[0].cells[c_idx]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, r_data in enumerate(t2_rows):
        row = t2.rows[r_idx+1]
        bg_col = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)

    add_p("Table 2: Existing System vs QRadar Comparison", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=10, space_before=4, space_after=2)
    add_p("This comparison highlights how QRadar improves defense, transparency, and accountability compared to traditional systems.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=10.5, space_before=2, space_after=4)

    doc.add_page_break()

    # Document Page 36 (Page 28) - Resulting Graphs 1 & 2
    add_p("28", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("5.3 Resulting Graphs", space_before=6, space_after=6)
    
    add_h3("5.3.1 Result Graph 1: Attack-Wise Quishing Threat Distribution", space_before=4, space_after=4)
    add_img("graph1_attack_distribution.png", width_in_inches=5.2, caption="Graph 1: Attack Category Wise Quishing Threat Distribution")
    add_p("Attack-wise Distribution: Threats are primarily concentrated in lookalike brand typosquatting (35%), followed by raw IP address hosts (25%), obfuscated URL shorteners (20%), dangerous URI schemes (12%), and suspicious target keywords (8%).", align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11, space_before=2, space_after=8)

    add_h3("5.3.2 Result Graph 2: The Incident Response Resolution Timeline Graph", space_before=6, space_after=4)
    add_img("graph2_incident_timeline.png", width_in_inches=5.2, caption="Graph 2: Incident Detection & Verification Response Timeline")
    add_p("The lines in the timeline graph represent the volume of QR scans evaluated and malicious attacks neutralized across operational deployment days in QRadar, illustrating steady defense throughput.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11, space_before=2, space_after=4)

    doc.add_page_break()

    # Document Page 37 (Page 29) - Resulting Graphs 3 & 4
    add_p("29", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h3("5.3.3 Result Graph 3: Threat Risk Score Severity Distribution", space_before=6, space_after=4)
    add_img("graph3_priority_distribution.png", width_in_inches=5.2, caption="Graph 3: Threat Risk Score Severity Distribution")
    add_p("Most scanned QR targets fall under low risk (safe corporate and commercial destinations) and high/critical risk (spoofed brands and exploit payloads), while medium-priority suspicious shorteners are moderately distributed.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11, space_before=2, space_after=8)

    add_h3("5.3.4 Result Graph 4: Scan Verdict Classification Distribution", space_before=6, space_after=4)
    add_img("graph4_status_distribution.png", width_in_inches=5.2, caption="Graph 4: Scan Verdict Classification Distribution")
    add_p("The pie chart illustrates that 64.2% of scanned codes were verified as SAFE, 21.0% were confirmed as MALICIOUS and blocked, and 14.8% were intercepted as SUSPICIOUS under warning gates.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11, space_before=2, space_after=4)

    doc.add_page_break()

    # Document Page 38 (Page 30) - Results Analysis
    add_p("30", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h2("5.4 Results Analysis", space_before=8, space_after=6)
    
    add_h3("5.4.1 Time Complexity", space_before=6, space_after=4)
    tc_text = (
        "The time complexity of QRadar (Real-Time Quishing Detection & Defense System) varies across its modular pipeline rather than relying on a single "
        "algorithm. QR code decoding using OpenCV performs optical edge detection and Reed-Solomon error correction in O(W * H) time, where W and H are "
        "the pixel dimensions of the image frame, executing in under 20 ms. The 12-rule Heuristic Engine operates in O(k) bounded string time, evaluating "
        "regular expressions and Levenshtein brand comparisons against a constant catalog of 20 high-value brands in O(1) time.\n\n"
        "The Machine Learning inference stage extracts 18 features in O(L) time (where L is the URL character length) and navigates 100 balanced decision "
        "trees of maximum depth d in O(T * d) time, which is strictly O(1) during live inference. Threat Intelligence cache lookups in SQLite utilize B-tree "
        "indexing over SHA-256 URL hashes, executing in O(log N) time. Overall, the system's end-to-end time complexity is bounded by O(1) per scan, "
        "guaranteeing predictable sub-second latency even as the historical dataset grows."
    )
    add_p(tc_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=8).paragraph_format.line_spacing = 1.25

    add_h3("5.4.2 Space Complexity", space_before=6, space_after=4)
    sc_text = (
        "The space complexity of QRadar depends on the data stored for scan audits, threat intelligence caches, and machine learning models. The 18-feature "
        "vector extracted per URL occupies a tiny fixed memory buffer O(F) = 18 floating-point numbers. The serialized Random Forest classifier model "
        "occupies a compact 2.4 MB on disk and is loaded once into memory at ASGI startup.\n\n"
        "Storage requirements in the SQLite database scale linearly O(N) with the number of unique scans and cached threat intelligence entries. Each audit "
        "record requires approximately 500 bytes for normalized URL strings, risk scores, heuristic flags, and timestamps. An automated 30-day retention "
        "policy purges expired logs, bounding total database storage and ensuring sustainable long-term operation."
    )
    add_p(sc_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=8).paragraph_format.line_spacing = 1.25

    add_h3("5.4.3 Results Summary", space_before=6, space_after=4)
    rs_text = (
        "The Results Summary of QRadar demonstrates that the platform effectively neutralizes quishing attacks while maintaining low latency and high usability. "
        "Evaluation across 4,515 verified URLs demonstrated an outstanding 99.59% holdout test accuracy, 99.38% precision, and 99.79% recall. The strict Zero URL "
        "Auto-Open Policy achieved 100% enforcement, preventing any automated browser execution of malicious payloads. With low CPU, memory, and network overhead, "
        "QRadar proves to be a reliable, scalable, and indispensable defensive solution for modern cybersecurity."
    )
    add_p(rs_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11.5, space_before=2, space_after=4).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    print("Building Chapter 6: Conclusion & Future Scope (Pages 39-41)...")
    # ===================================================================
    # CHAPTER 6: CONCLUSION & FUTURE SCOPE (Page 31)
    # ===================================================================
    # Document Page 39 (Page 31)
    add_p("31", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h1("CHAPTER 6\n\nCONCLUSION & FUTURE SCOPE", space_before=8, space_after=16)
    
    add_h2("6.1 Conclusion", space_before=8, space_after=6)
    c_1 = (
        "The QRadar (Real-Time Quishing Detection & Defense System) is an efficient, authoritative cybersecurity platform designed to streamline "
        "quishing defense by enabling mobile and web users to scan, evaluate, and verify QR destinations in real time. It resolves fundamental "
        "vulnerabilities in conventional barcode scanners by establishing an authoritative defense-in-depth security proxy between the physical "
        "scan and the browser. By combining 12 deterministic heuristic threat rules, an 18-feature Random Forest machine learning classifier "
        "(99.59% accuracy), and global threat intelligence feeds backed by a 24-hour SQLite TTL cache, QRadar ensures that threats are identified "
        "and neutralized in a structured, timely, and traceable manner."
    )
    add_p(c_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    c_2 = (
        "Overall, QRadar enhances operational security by automating threat triage, eliminating human optical blindness, and strictly enforcing a "
        "Zero URL Auto-Open policy. It provides clear explainability through radial risk score gauges, plain-English threat rationale, and detailed "
        "feature breakdowns. Its scalability, low latency (45 ms on cache hits), and lightweight open-source architecture make it ideally suited for "
        "both individual consumer protection and enterprise mobile device management (MDM) ecosystems, establishing digital trust in contactless interactions."
    )
    add_p(c_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=12).paragraph_format.line_spacing = 1.25

    add_h2("6.2 Future Scope", space_before=8, space_after=6)
    fs_1 = (
        "The future scope of the QRadar platform is highly promising as it can be augmented with cutting-edge artificial intelligence and edge computing "
        "technologies. Advanced Deep Learning Vision Transformers (ViTs) can be trained to analyze the visual layout of rendered destination landing pages "
        "in headless sandboxes, detecting brand spoofing logos and credential form structures even when URLs are entirely novel."
    )
    add_p(fs_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=8).paragraph_format.line_spacing = 1.25

    fs_2 = (
        "Additionally, QRadar can integrate on-device offline neural network inference using TensorFlow Lite or ONNX Runtime, enabling smartphones to "
        "perform complete heuristic and machine learning evaluations even in air-gapped or low-connectivity environments. Browser extensions and corporate "
        "MDM integrations can extend protection to enterprise laptops and managed mobile fleets. In the long term, QRadar can incorporate decentralized "
        "threat intelligence sharing and automated takedown reporting, solidifying its role as an indispensable component of next-generation cybersecurity."
    )
    add_p(fs_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, space_before=4, space_after=4).paragraph_format.line_spacing = 1.25

    doc.add_page_break()

    # Document Page 40 (Page 32) - References
    add_p("32", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h1("References", space_before=8, space_after=16)
    
    refs = [
        "1. Federal Bureau of Investigation (FBI). Cybercriminals Tampering with QR Codes to Steal Credentials and Divert Payments. In: Internet Crime Complaint Center (IC3) Public Service Announcement. 2022. Available from: https://www.ic3.gov/Media/Y2022/PSA220118",
        "2. Cybersecurity and Infrastructure Security Agency (CISA). Phishing and Quishing Defensive Guidance for Government and Critical Infrastructure. In: CISA Security Advisories. 2023. p. 1–14. Available from: https://www.cisa.gov",
        "3. International Organization for Standardization. ISO/IEC 18004:2024 Information Technology — Automatic Identification and Data Capture Techniques — QR Code Barcode Symbology Specification. Geneva: ISO; 2024.",
        "4. Levenshtein, V. I. Binary Codes Capable of Correcting Deletions, Insertions, and Reversals. In: Soviet Physics Doklady. 1966. Vol. 10, No. 8, p. 707–710.",
        "5. Breiman, L. Random Forests. In: Machine Learning. Springer. 2001. Vol. 45, No. 1, p. 5–32. Available from: https://doi.org/10.1023/A:1010933404324",
        "6. Tranco Team. Tranco: A Research-Oriented Top Sites Ranking Hardened Against Manipulation. In: Proceedings of the 26th Network and Distributed System Security Symposium (NDSS). 2019. Available from: https://tranco-list.eu",
        "7. PhishTank Community. PhishTank: An Authoritative Clearinghouse for Data and Information About Phishing on the Internet. OpenDNS / Cisco. 2024. Available from: https://phishtank.org",
        "8. Google Cloud Platform. Google Safe Browsing API (v4): Developer Guide and Protocol Reference. In: Google Security Documentation. 2024. Available from: https://developers.google.com/safe-browsing",
        "9. VirusTotal. VirusTotal Public API v3 Reference Documentation and Threat Telemetry. Chronicle Security. 2024. Available from: https://docs.virustotal.com",
        "10. Berners-Lee, T., Fielding, R., Masinter, L. Uniform Resource Identifier (URI): Generic Syntax. In: Internet Engineering Task Force (IETF) RFC 3986. 2005. Available from: https://www.ietf.org/rfc/rfc3986.txt",
        "11. OWASP Foundation. OWASP Top 10: Server-Side Request Forgery (SSRF) and Phishing Prevention Cheat Sheet. In: OWASP Security Guidelines. 2023. p. 1–20. Available from: https://cheatsheetseries.owasp.org"
    ]
    for r in refs:
        p = add_p(r, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=10.5, space_before=3, space_after=6)
        p.paragraph_format.line_spacing = 1.2

    doc.add_page_break()

    # Document Page 41 (Page 33) - Poster Presentation
    add_p("33", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, space_after=14)
    add_h1("POSTER PRESENTATION", space_before=8, space_after=14)
    
    add_img("poster_presentation.png", width_in_inches=5.8, caption="Poster Presentation: QRadar Quishing Detection & Defense Platform")
    add_p("The above poster provides a comprehensive visual summary of the QRadar platform, presenting the system abstract, defense architecture, experimental results (99.59% accuracy), and key conclusions.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=11, space_before=2, space_after=4)

    # Save Document
    doc.save(DOCX_PATH)
    print(f"Report saved successfully to {DOCX_PATH}")

if __name__ == '__main__':
    create_report()
