"""
Statutory Legal Inspection Report & Notice Generator
Produces official Seventh Schedule (Rule 19) Inspection Reports and Legal Notices under Section 36 of Legal Metrology Act, 2009.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def _get_reports_dir() -> str:
    # On serverless (Vercel, AWS Lambda), write to /tmp
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        p = "/tmp/reports"
        try:
            os.makedirs(p, exist_ok=True)
            return p
        except Exception:
            return "/tmp"
    base = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(base, "reports")
    try:
        os.makedirs(p, exist_ok=True)
        return p
    except Exception:
        p = "/tmp/reports"
        try:
            os.makedirs(p, exist_ok=True)
            return p
        except Exception:
            return "/tmp"

REPORTS_DIR = _get_reports_dir()

def generate_inspection_pdf(scan_record: Dict[str, Any], output_path: Optional[str] = None) -> str:
    scan_uid = scan_record.get("scan_uid", f"LM-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    if not output_path:
        output_path = os.path.join(REPORTS_DIR, f"Inspection_Report_{scan_uid}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=13,
        leading=16,
        alignment=1, # Center
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        alignment=1, # Center
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=6
    )
    section_head = ParagraphStyle(
        'SecHead',
        parent=styles['Heading2'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=8,
        spaceAfter=4
    )
    body_text = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1f2937")
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_text,
        fontName='Helvetica-Bold'
    )
    notice_text = ParagraphStyle(
        'NoticeText',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#b91c1c")
    )

    story = []

    # 1. Header
    story.append(Paragraph("GOVERNMENT OF INDIA", title_style))
    story.append(Paragraph("MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", subtitle_style))
    story.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS — LEGAL METROLOGY DIVISION", subtitle_style))
    story.append(Paragraph("<b>STATUTORY INSPECTION MEMORANDUM & COMPLIANCE DOSSIER</b>", ParagraphStyle('SubSub', parent=title_style, fontSize=11, textColor=colors.HexColor("#111827"))))
    story.append(Paragraph("<i>[Under Rule 19 & Seventh Schedule of Legal Metrology (Packaged Commodities) Rules, 2011]</i>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=8))

    # 2. Metadata Banner
    is_comp = scan_record.get("is_compliant", False)
    score = scan_record.get("compliance_score", 0.0)
    verdict_color = "#15803d" if is_comp else "#b91c1c"
    verdict_text = "COMPLIANT — NO ACTION REQUIRED" if is_comp else "NON-COMPLIANT — STATUTORY NOTICE ISSUED"

    meta_data = [
        [
            Paragraph("<b>Inspection ID:</b> " + str(scan_uid), body_text),
            Paragraph(f"<b>Status:</b> <font color='{verdict_color}'><b>{verdict_text}</b></font>", body_text)
        ],
        [
            Paragraph("<b>Date & Time:</b> " + str(scan_record.get("inspected_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))), body_text),
            Paragraph(f"<b>Compliance Score:</b> <b>{score}%</b>", body_text)
        ],
        [
            Paragraph("<b>Enforcement Officer ID:</b> LMO-CENTRAL-DL-402", body_text),
            Paragraph("<b>Jurisdiction:</b> District Consumer Metrology Cell", body_text)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[90 * mm, 90 * mm])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f3f4f6")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 4 * mm))

    # 3. Commodity & Manufacturer Profile
    story.append(Paragraph("<b>1. PARTICULARS OF PACKAGED COMMODITY (RULE 6)</b>", section_head))
    extracted = scan_record.get("raw_extracted", {})
    
    prod_table_data = [
        [
            Paragraph("<b>Commodity Name:</b>", body_bold),
            Paragraph(str(scan_record.get("commodity_name", "N/A")), body_text),
            Paragraph("<b>Category:</b>", body_bold),
            Paragraph(str(scan_record.get("category", "Retail Pack")), body_text)
        ],
        [
            Paragraph("<b>Manufacturer/Packer:</b>", body_bold),
            Paragraph(str(scan_record.get("manufacturer_name", "N/A")), body_text),
            Paragraph("<b>Country of Origin:</b>", body_bold),
            Paragraph(str(extracted.get("country_of_origin", "India")), body_text)
        ],
        [
            Paragraph("<b>Declared Net Quantity:</b>", body_bold),
            Paragraph(str(scan_record.get("net_quantity", "N/A")), body_text),
            Paragraph("<b>MRP (Incl. of all taxes):</b>", body_bold),
            Paragraph(str(scan_record.get("mrp", "N/A")), body_text)
        ],
        [
            Paragraph("<b>Unit Sale Price (USP):</b>", body_bold),
            Paragraph(str(scan_record.get("unit_sale_price", "N/A")), body_text),
            Paragraph("<b>Month & Year of Mfg:</b>", body_bold),
            Paragraph(str(scan_record.get("mfg_date", "N/A")), body_text)
        ],
        [
            Paragraph("<b>Manufacturer Address:</b>", body_bold),
            Paragraph(str(extracted.get("manufacturer_address", "N/A")), body_text),
            Paragraph("<b>Consumer Care:</b>", body_bold),
            Paragraph(f"{extracted.get('consumer_care_phone', '')} | {extracted.get('consumer_care_email', '')}", body_text)
        ]
    ]
    t_prod = Table(prod_table_data, colWidths=[40 * mm, 50 * mm, 40 * mm, 50 * mm])
    t_prod.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_prod)
    story.append(Spacer(1, 4 * mm))

    # 4. Violations & Infringement Audit Table
    story.append(Paragraph("<b>2. STATUTORY INFRINGEMENTS & RULE VIOLATIONS AUDIT</b>", section_head))
    violations = scan_record.get("violations", [])
    
    if not violations:
        no_viol_data = [[Paragraph("<b>COMPLIANCE VERIFIED:</b> No statutory violations detected under Legal Metrology (Packaged Commodities) Rules, 2011 and Amendments.", body_text)]]
        t_viol = Table(no_viol_data, colWidths=[180 * mm])
        t_viol.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86efac")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_viol)
    else:
        v_headers = [
            Paragraph("<b>#</b>", body_bold),
            Paragraph("<b>Rule Reference</b>", body_bold),
            Paragraph("<b>Severity</b>", body_bold),
            Paragraph("<b>Infringement Summary & Findings</b>", body_bold),
            Paragraph("<b>Statutory Penalty Section</b>", body_bold)
        ]
        v_rows = [v_headers]
        for idx, v in enumerate(violations):
            sev = v.get("severity", "MAJOR")
            sev_color = "#b91c1c" if sev == "CRITICAL" else ("#d97706" if sev == "MAJOR" else "#2563eb")
            v_rows.append([
                Paragraph(str(idx + 1), body_text),
                Paragraph(f"<b>{v.get('rule_reference', '')}</b>", body_text),
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", body_text),
                Paragraph(f"<b>{v.get('title', '')}:</b> {v.get('description', '')}", body_text),
                Paragraph(f"<b>{v.get('statutory_penalty_ref', v.get('penalty_ref', 'Sec 36(1)'))}</b>", body_text)
            ])
        t_viol = Table(v_rows, colWidths=[8 * mm, 38 * mm, 20 * mm, 80 * mm, 34 * mm])
        t_viol.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_viol)

    story.append(Spacer(1, 4 * mm))

    # 5. Legal Notice & Directives
    if violations:
        story.append(Paragraph("<b>3. STATUTORY NOTICE UNDER SECTION 36, LEGAL METROLOGY ACT, 2009</b>", section_head))
        notice_clause = (
            "<b>NOTICE IS HEREBY GIVEN</b> that the packaged commodity detailed above does not conform to the provisions "
            "of the Legal Metrology (Packaged Commodities) Rules, 2011 and amendments thereto. In accordance with Section 36(1) "
            "of the Legal Metrology Act, 2009 (1 of 2010), whoever manufactures, packs, imports, sells, distributes, or delivers "
            "any pre-packaged commodity which does not conform to the declarations on the package shall be punishable with fine "
            "which may extend to twenty-five thousand rupees, and for the second offence, to fifty thousand rupees, and for subsequent "
            "offences with fine or imprisonment. You are required to submit an explanation or apply for compounding under Section 48 "
            "within 15 days of this memorandum."
        )
        story.append(Paragraph(notice_clause, notice_text))
        story.append(Spacer(1, 4 * mm))

    # 6. Officer Endorsement & Signatures (Seventh Schedule Form A/B style)
    story.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#9ca3af"), spaceAfter=6),
        Table([
            [
                Paragraph("<b>Inspecting Legal Metrology Officer:</b>", body_bold),
                Paragraph("<b>Manufacturer / Packer / Dealer Representative:</b>", body_bold)
            ],
            [
                Paragraph("Signature: __________________________", body_text),
                Paragraph("Signature: __________________________", body_text)
            ],
            [
                Paragraph("Name: R. K. Sharma (LMO Central Cell)", body_text),
                Paragraph("Name & Stamp: ______________________", body_text)
            ],
            [
                Paragraph(f"Date & Place: {datetime.now().strftime('%d/%m/%Y')}, New Delhi", body_text),
                Paragraph("Witness Signature: __________________", body_text)
            ]
        ], colWidths=[90 * mm, 90 * mm], style=[
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ])
    ]))

    doc.build(story)
    return output_path

if __name__ == "__main__":
    test_record = {
        "scan_uid": "LM-20260913-99901",
        "commodity_name": "Crunchy Potato Chips",
        "category": "Snack Food",
        "manufacturer_name": "Evergreen Foods Pvt Ltd",
        "net_quantity": "200 gms",
        "mrp": "₹ 40.00",
        "unit_sale_price": "Not Declared",
        "mfg_date": "08/2026",
        "is_compliant": False,
        "compliance_score": 72.0,
        "inspected_at": "2026-09-13 22:30:00",
        "raw_extracted": {
            "country_of_origin": "India",
            "manufacturer_address": "Plot 45, Okhla Industrial Area, New Delhi 110020",
            "consumer_care_phone": "1800-200-1111",
            "consumer_care_email": "help@evergreenfoods.com"
        },
        "violations": [
            {
                "rule_reference": "Rule 13(5) & Second Schedule",
                "severity": "MAJOR",
                "title": "Non-Standard Unit Symbol 'gms'",
                "description": "Symbol 'gms' is prohibited under Rule 13; statutory SI symbol is 'g'.",
                "statutory_penalty_ref": "Section 36(1)"
            },
            {
                "rule_reference": "Rule 6(11) (G.S.R. 779(E))",
                "severity": "CRITICAL",
                "title": "Missing Unit Sale Price (USP)",
                "description": "Mandatory Unit Sale Price (₹/g) not declared on the package.",
                "statutory_penalty_ref": "Section 36(1)"
            }
        ]
    }
    path = generate_inspection_pdf(test_record)
    print("PDF generated successfully at:", path)
