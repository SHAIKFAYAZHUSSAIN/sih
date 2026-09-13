# LMPC SmartInspector: Legal Metrology Compliance Checking System

> **Smart India Hackathon (SIH) — Problem Statement ID: 26034**  
> **Problem:** Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/Ministry-Department%20of%20Consumer%20Affairs-amber.svg)](https://consumeraffairs.gov.in/)

---

## Overview

**LMPC SmartInspector** is an AI-powered regulatory compliance inspection platform designed for enforcement officials under the **Ministry of Consumer Affairs, Food & Public Distribution (Government of India)**. 

Packaged commodities sold across offline retail stores, supermarkets, and rapid/e-commerce platforms must strictly comply with mandatory statutory declarations. Manual verification is time-consuming, prone to human oversight, and difficult to scale across millions of SKUs.

This system automates the detection, extraction, and statutory cross-verification of package declarations directly from product images, identifying infringements and generating legally admissible inspection memorandums under **Section 36 of the Legal Metrology Act, 2009**.

---

## Statutory Legal Framework Codified

The deterministic rule engine directly codifies the official Gazette notifications from the Department of Consumer Affairs:

1. **G.S.R. 202(E) (March 7, 2011)** — *Legal Metrology (Packaged Commodities) Rules, 2011* (Principal Rules)
   * **Rule 6**: Core mandatory declarations (Manufacturer/Packer Name & Complete Address with PIN code, Common/Generic Name, Net Quantity, MRP, Month & Year of Mfg/Packing, Consumer Care Cell).
   * **Rule 7 & Schedule II**: Strict minimum font height requirements ($1\,\text{mm}, 2\,\text{mm}, 4\,\text{mm}, 6\,\text{mm}$) based on package weight/volume and Principal Display Panel (PDP) surface area.
   * **Rule 8**: Mandatory surrounding clear space around net quantity declarations.
   * **Rule 9 & 10**: Prominence, contrasting background, and language requirements.
   * **Rule 13(5)**: Mandatory SI units (`g`, `kg`, `ml`, `l`, `m`, `cm`, `N`, `U`). Prohibits non-standard symbols such as `gms`, `gm`, `ltrs`.
   * **Rule 12(6)**: Prohibits deceptive/approximating expressions like *"minimum"*, *"not less than"*, *"approximate"*, or *"when packed"*.
2. **G.S.R. 779(E) (November 2, 2021)** — *Packaged Commodities Amendment Rules, 2021*
   * **Rule 6(11)**: **Mandatory Unit Sale Price (USP)** declaration (e.g., `Rs. __ per g`, `Rs. __ per kg`, `Rs. __ per ml`, `Rs. __ per litre`).
   * **Mathematical Consistency**: Cross-verifies that $\text{Declared USP} \equiv \frac{\text{MRP}}{\text{Net Quantity}}$.
   * **Rule 4(2)**: Promotional multi-packs and combo packs must bear full declarations on every individual unit.
3. **G.S.R. 577(E) (July 14, 2022)** — *Second Amendment Rules, 2022 (QR Codes for Electronics)*
   * Allows electronic commodities to provide manufacturer address and dimensions via a scannable QR code, while strictly mandating that the **consumer helpline phone number and email address remain printed on the physical package itself**.

---

## Key Features

* **Real-Time Bounding Box Inspection Studio**: Side-by-side visualization of product packaging with color-coded bounding boxes (Green = Valid statutory declaration, Red = Infringement, Blue = QR / Electronic).
* **Statutory Compliance Scorecard**: Calculates a real-time compliance score (0–100%) and categorizes the inspection status.
* **1-Click Live Demonstration Scenarios**: Pre-configured test packages covering:
  1. *100% Compliant Snack Pack* (NutriBite Biscuits)
  2. *Illegal 'gms' Unit & Undersized Font* (Desi Swad Namkeen)
  3. *Missing Unit Sale Price (USP) & Consumer Care Phone* (AquaPure Water 1L)
  4. *Post-Dated Future Mfg Date Fraud Detection* (FarmFresh Cow Ghee)
  5. *Smart Electronics with QR Code Verification* (SoundMax Earbuds)
* **Automated PDF Legal Memo Generation**: One-click export of official **Seventh Schedule (Rule 19) Inspection Memorandums** complete with penal citations under **Section 36(1) of the Legal Metrology Act, 2009**.
* **Audit Trail & Inspection Repository**: Embedded SQLite database logging all scans, timestamps, scores, and infraction histories.

---

## System Architecture

```
                      [ Package Image / Camera Upload ]
                                     │
                                     ▼
                    [ Computer Vision & KIE Pipeline ]
                     • OpenCV Label Preprocessing
                     • Text & Bounding Box Localization
                                     │
                                     ▼
                [ Deterministic LMPC 2011 Rule Engine ]
                     • Rule 6 Declaration Completeness
                     • Rule 13 SI Unit Checker (flags 'gms')
                     • Rule 6(11) Unit Sale Price Math Verifier
                     • Rule 7 & Schedule II Font Height Scaler
                     • Rule 6(1)(d) Date Chronology & Fraud Filter
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
      [ Real-Time Web Dashboard ]         [ PDF Notice Generator ]
       • Side-by-Side Visuals              • Seventh Schedule Form
       • Compliance Scorecard              • Section 36(1) Citation
```

---

## Getting Started

### Prerequisites
* Python 3.10 or higher
* Pip package manager

### Installation

1. Clone this repository:
```bash
git clone https://github.com/SHAIKFAYAZHUSSAIN/sih.git
cd sih
```

2. Install dependencies:
```bash
pip install fastapi uvicorn opencv-python pillow reportlab pydantic python-multipart
```

3. Generate sample demo assets (if not already present):
```bash
python generate_demo_assets.py
```

4. Launch the application:
```bash
python app.py
```
*(Or double-click `run_demo.bat` on Windows)*

5. Open your browser at:
```text
http://127.0.0.1:8000
```

---

## Project Structure

```
├── app.py                      # FastAPI web server and routing API
├── lmpc_rule_engine.py         # Codified statutory Legal Metrology rule engine
├── lmpc_rules_config.json      # Structured rulebook parameters & font tables
├── lmpc_extractor.py           # Computer vision & key-information extraction (KIE)
├── report_generator.py         # Official PDF inspection report generator (ReportLab)
├── database.py                 # SQLite persistent audit repository
├── generate_demo_assets.py     # Generates mock product packaging labels for demo
├── verify_system.py            # Automated end-to-end integration test suite
├── run_demo.bat                # Windows single-click launcher
├── templates/
│   └── index.html              # Responsive inspector web dashboard
├── static/
│   ├── images/                 # Sample demonstration product images
│   └── uploads/                # User-uploaded package photos
├── sample_data/                # Pre-configured scenario metadata profiles
└── reports/                    # Generated statutory inspection memos (PDF)
```

---

## Verification & Testing

Run the automated test suite to verify all rules, endpoints, and PDF generation:
```bash
python verify_system.py
```

Expected output:
```text
=== STARTING LMPC SYSTEM VERIFICATION TESTS ===
[PASS] GET / (Dashboard UI serves HTTP 200)
[PASS] Sample 01 (Compliant): Score 100.0% | Violations: 0
[PASS] Sample 02 (Illegal 'gms' & Font): Violations detected -> ['RULE_13_5_NON_STANDARD_UNIT', 'RULE_7_NUMERAL_HEIGHT']
[PASS] Sample 03 (Missing USP): Violations detected -> ['RULE_6_11_USP_MISSING', 'RULE_6_2_INCOMPLETE_CARE']
[PASS] Sample 04 (Future Date): Violations detected -> ['RULE_6_1_D_FUTURE_DATE']
[PASS] Sample 05 (QR Code Electronics): Score 100.0% under G.S.R. 577(E)
[PASS] Metrics Endpoint: Total Scans = 10 | Pass Rate = 40.0%
[PASS] PDF Generation: Generated Seventh Schedule Inspection Report
*** ALL 8 STATUTORY VERIFICATION TESTS PASSED SUCCESSFULLY! ***
```

---

## Government of India Reference Notifications
* [Department of Consumer Affairs — Legal Metrology Division](https://consumeraffairs.gov.in/pages/legal-metrology-act)
* The Legal Metrology Act, 2009 (No. 1 of 2010)
* G.S.R. 202(E) (March 2011) — The Legal Metrology (Packaged Commodities) Rules, 2011
* G.S.R. 779(E) (November 2021) — The Legal Metrology (Packaged Commodities) Amendment Rules, 2021
* G.S.R. 577(E) (July 2022) — The Legal Metrology (Packaged Commodities) (Second Amendment) Rules, 2022
