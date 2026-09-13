"""
Demo Assets Generator
Generates realistic product label mockup images and matching extracted metadata profiles
for 5 distinct Legal Metrology test scenarios.
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

SAMPLE_DIR = "c:/Users/sfaya/Documents/SIH/sample_data"
STATIC_IMAGES_DIR = "c:/Users/sfaya/Documents/SIH/static/images"
os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)

# Helper to draw a product label
def create_label_image(filename: str, bg_color: tuple, border_color: tuple, title: str, details: list, stamp_box: dict):
    width, height = 700, 900
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.draw(img) if hasattr(ImageDraw, "draw") else ImageDraw.Draw(img)

    # Outer border
    draw.rectangle([(15, 15), (width - 15, height - 15)], outline=border_color, width=4)
    # Header banner
    draw.rectangle([(20, 20), (width - 20, 110)], fill=border_color)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 30)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_body = ImageFont.truetype("arial.ttf", 16)
        font_stamp = ImageFont.truetype("arial.ttf", 15)
        font_bold = ImageFont.truetype("arialbd.ttf", 18)
    except Exception:
        font_title = font_sub = font_body = font_stamp = font_bold = ImageFont.load_default()

    # Product Title in Banner
    draw.text((width // 2, 45), title, fill="white", font=font_title, anchor="mm")
    draw.text((width // 2, 85), "PRE-PACKAGED COMMODITY • STATUTORY DECLARATION PANEL", fill="#f3f4f6", font=font_sub, anchor="mm")

    # Draw Declarations
    y = 140
    for label, val, is_highlight in details:
        draw.text((40, y), label, fill="#111827", font=font_bold)
        y += 24
        draw.text((40, y), val, fill="#374151" if not is_highlight else "#b91c1c", font=font_body)
        y += 36
        draw.line([(40, y - 10), (width - 40, y - 10)], fill="#e5e7eb", width=1)

    # Inkjet MRP / Batch Stamp Box
    sx1, sy1, sx2, sy2 = stamp_box["coords"]
    draw.rectangle([(sx1, sy1), (sx2, sy2)], outline="#1e3a8a", fill="#eff6ff", width=2)
    draw.text((sx1 + 15, sy1 + 15), "INKJET BATCH / MRP PRINT PANEL", fill="#1e3a8a", font=font_bold)
    
    sy = sy1 + 45
    for s_line in stamp_box["lines"]:
        draw.text((sx1 + 15, sy), s_line, fill="#0f172a", font=font_stamp)
        sy += 24

    # QR Code placeholder if requested
    if stamp_box.get("draw_qr"):
        qx1, qy1, qx2, qy2 = width - 180, height - 190, width - 40, height - 50
        draw.rectangle([(qx1, qy1), (qx2, qy2)], fill="white", outline="#000000", width=3)
        # draw QR matrix simulation
        for i in range(qx1 + 10, qx2 - 10, 15):
            for j in range(qy1 + 10, qy2 - 10, 15):
                if (i + j) % 30 == 0 or (i * j) % 45 == 0:
                    draw.rectangle([(i, j), (i + 10, j + 10)], fill="black")
        draw.text((qx1 + 70, qy2 + 10), "[SCANNABLE QR CODE]", fill="#111827", font=font_stamp, anchor="mt")

    img_path = os.path.join(STATIC_IMAGES_DIR, filename)
    img.save(img_path, "JPEG", quality=95)
    return img_path


def generate_all_samples():
    samples_meta = [
        {
            "id": "sample_01",
            "title": "NutriBite Whole Wheat Biscuits",
            "category": "Biscuits & Bakery",
            "filename": "sample_01_compliant_snack.jpg",
            "bg_color": (254, 252, 246),
            "border_color": (16, 185, 129), # Green
            "details": [
                ("Generic Name / Commodity:", "Crispy Whole Wheat Biscuits (Combination pack of 2)", False),
                ("Manufactured & Packed By:", "Sunbeam Confectioneries Pvt Ltd, Plot 14, Sector 18, Gurugram, Haryana 122015", False),
                ("Country of Origin:", "India", False),
                ("Consumer Care / Grievance Redressal:", "Manager - Consumer Care, Tel: 1800-208-9999, Email: feedback@sunbeamfoods.com", False),
                ("Dimensions of Package:", "Length: 18 cm, Width: 8 cm, Height: 5 cm", False)
            ],
            "stamp": {
                "coords": (40, 520, 660, 710),
                "lines": [
                    "BATCH NO: SB-2026/089",
                    "NET WEIGHT: 250 g",
                    "MFG DATE: 08/2026  •  USE BY: 02/2027",
                    "MAX. RETAIL PRICE: Rs. 50.00 (inclusive of all taxes)",
                    "UNIT SALE PRICE: Rs. 0.20 per g"
                ],
                "draw_qr": False
            },
            "extracted_data": {
                "commodity_name": "NutriBite Whole Wheat Biscuits",
                "generic_name": "Crispy Whole Wheat Biscuits",
                "category": "Biscuits & Bakery",
                "manufacturer_name": "Sunbeam Confectioneries Pvt Ltd",
                "manufacturer_address": "Plot 14, Sector 18, Gurugram, Haryana 122015",
                "country_of_origin": "India",
                "net_quantity_raw": "250 g",
                "net_quantity_value": 250.0,
                "net_quantity_unit": "g",
                "mrp_raw": "Rs. 50.00 (inclusive of all taxes)",
                "mrp_value": 50.0,
                "unit_sale_price_raw": "Rs. 0.20 per g",
                "unit_sale_price_value": 0.20,
                "mfg_date": "08/2026",
                "consumer_care_phone": "1800-208-9999",
                "consumer_care_email": "feedback@sunbeamfoods.com",
                "measured_numeral_height_mm": 2.2,
                "measured_letter_height_mm": 1.4,
                "has_qr_code": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "box": [40, 140, 600, 185], "color": "#10b981"},
                {"label": "Manufacturer Details", "box": [40, 200, 650, 255], "color": "#10b981"},
                {"label": "Country of Origin", "box": [40, 270, 250, 315], "color": "#10b981"},
                {"label": "Consumer Care", "box": [40, 330, 650, 385], "color": "#10b981"},
                {"label": "MRP & USP Stamp Box", "box": [40, 520, 660, 710], "color": "#10b981"}
            ]
        },
        {
            "id": "sample_02",
            "title": "Desi Swad Roasted Namkeen",
            "category": "Savory Snacks",
            "filename": "sample_02_illegal_unit_snack.jpg",
            "bg_color": (255, 247, 237),
            "border_color": (239, 68, 68), # Red
            "details": [
                ("Generic Name / Commodity:", "Spicy Roasted Mixture", False),
                ("Manufactured & Packed By:", "Desi Swad Foods Ltd, GIDC Estate, Vatva, Ahmedabad, Gujarat 382445", False),
                ("Country of Origin:", "India", False),
                ("Consumer Care / Complaints:", "Phone: 079-22334455, Email: care@desiswad.in", False),
                ("Notice:", "Stored in dry hygienic condition", False)
            ],
            "stamp": {
                "coords": (40, 520, 660, 710),
                "lines": [
                    "LOT: DS-N771",
                    "NET WT.: 400 gms  <-- ILLEGAL UNIT 'gms'!",
                    "MFG: 07/2026",
                    "MRP: Rs. 120.00 (incl. of all taxes)",
                    "USP: Rs. 0.30 per g  [Printed Numeral Height: 1.1mm - UNDERSIZED!]"
                ],
                "draw_qr": False
            },
            "extracted_data": {
                "commodity_name": "Desi Swad Roasted Namkeen",
                "generic_name": "Spicy Roasted Mixture",
                "category": "Savory Snacks",
                "manufacturer_name": "Desi Swad Foods Ltd",
                "manufacturer_address": "GIDC Estate, Vatva, Ahmedabad, Gujarat 382445",
                "country_of_origin": "India",
                "net_quantity_raw": "400 gms",
                "net_quantity_value": 400.0,
                "net_quantity_unit": "gms",
                "mrp_raw": "Rs. 120.00 (incl. of all taxes)",
                "mrp_value": 120.0,
                "unit_sale_price_raw": "Rs. 0.30 per g",
                "unit_sale_price_value": 0.30,
                "mfg_date": "07/2026",
                "consumer_care_phone": "079-22334455",
                "consumer_care_email": "care@desiswad.in",
                "measured_numeral_height_mm": 1.1, # Below statutory 2.0mm for 400g!
                "measured_letter_height_mm": 1.0,
                "has_qr_code": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "box": [40, 140, 600, 185], "color": "#10b981"},
                {"label": "Manufacturer Details", "box": [40, 200, 650, 255], "color": "#10b981"},
                {"label": "VIOLATION: Illegal Unit 'gms'", "box": [40, 560, 450, 600], "color": "#ef4444"},
                {"label": "VIOLATION: Font Height < 2.0mm", "box": [40, 650, 650, 700], "color": "#ef4444"}
            ]
        },
        {
            "id": "sample_03",
            "title": "AquaPure Natural Spring Water",
            "category": "Beverages",
            "filename": "sample_03_missing_usp_beverage.jpg",
            "bg_color": (240, 249, 255),
            "border_color": (239, 68, 68), # Red
            "details": [
                ("Generic Name / Commodity:", "Natural Mineral Water", False),
                ("Packer & Bottler:", "Himalayan Spring Bottlers Ltd, Solan, Himachal Pradesh 173212", False),
                ("Country of Origin:", "India", False),
                ("Consumer Care:", "Email: contact@aquapure.co.in (NO PHONE NUMBER PROVIDED!)", True),
                ("Recycling Info:", "100% Recyclable PET Container", False)
            ],
            "stamp": {
                "coords": (40, 520, 660, 690),
                "lines": [
                    "BATCH NO: AQ-091",
                    "NET VOLUME: 1 L",
                    "DATE OF PACKING: 08/2026",
                    "MRP: Rs. 30.00 (inclusive of all taxes)",
                    "*** UNIT SALE PRICE NOT DECLARED ***"
                ],
                "draw_qr": False
            },
            "extracted_data": {
                "commodity_name": "AquaPure Natural Spring Water",
                "generic_name": "Natural Mineral Water",
                "category": "Beverages",
                "manufacturer_name": "Himalayan Spring Bottlers Ltd",
                "manufacturer_address": "Solan, Himachal Pradesh 173212",
                "country_of_origin": "India",
                "net_quantity_raw": "1 L",
                "net_quantity_value": 1.0,
                "net_quantity_unit": "L",
                "mrp_raw": "Rs. 30.00 (inclusive of all taxes)",
                "mrp_value": 30.0,
                "unit_sale_price_raw": "", # Missing!
                "unit_sale_price_value": None,
                "mfg_date": "08/2026",
                "consumer_care_phone": "", # Missing!
                "consumer_care_email": "contact@aquapure.co.in",
                "measured_numeral_height_mm": 4.5,
                "measured_letter_height_mm": 1.5,
                "has_qr_code": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "box": [40, 140, 600, 185], "color": "#10b981"},
                {"label": "VIOLATION: Incomplete Consumer Care", "box": [40, 330, 650, 385], "color": "#ef4444"},
                {"label": "VIOLATION: Missing Unit Sale Price", "box": [40, 520, 660, 690], "color": "#ef4444"}
            ]
        },
        {
            "id": "sample_04",
            "title": "FarmFresh Organic Cow Ghee",
            "category": "Dairy Products",
            "filename": "sample_04_future_date_dairy.jpg",
            "bg_color": (254, 252, 232),
            "border_color": (220, 38, 38), # Red
            "details": [
                ("Generic Name / Commodity:", "Pure Organic Desi Cow Ghee", False),
                ("Manufactured By:", "Purity Dairy Farms, GT Road, Karnal, Haryana 132001", False),
                ("Country of Origin:", "India", False),
                ("Consumer Care:", "Customer Grievance Cell, Phone: 1800-440-2200, Email: support@puritydairy.in", False),
                ("Storage Condition:", "Store in a cool, dry place away from sunlight", False)
            ],
            "stamp": {
                "coords": (40, 520, 660, 710),
                "lines": [
                    "BATCH NO: GH-902",
                    "NET QUANTITY: 500 ml",
                    "MFG DATE: 12/2026  <-- POST-DATED FUTURE PACKING FRAUD!",
                    "MRP: Rs. 350.00 (inclusive of all taxes)",
                    "UNIT SALE PRICE: Rs. 0.70 per ml"
                ],
                "draw_qr": False
            },
            "extracted_data": {
                "commodity_name": "FarmFresh Organic Cow Ghee",
                "generic_name": "Pure Organic Desi Cow Ghee",
                "category": "Dairy Products",
                "manufacturer_name": "Purity Dairy Farms",
                "manufacturer_address": "GT Road, Karnal, Haryana 132001",
                "country_of_origin": "India",
                "net_quantity_raw": "500 ml",
                "net_quantity_value": 500.0,
                "net_quantity_unit": "ml",
                "mrp_raw": "Rs. 350.00 (inclusive of all taxes)",
                "mrp_value": 350.0,
                "unit_sale_price_raw": "Rs. 0.70 per ml",
                "unit_sale_price_value": 0.70,
                "mfg_date": "12/2026", # Post-dated!
                "consumer_care_phone": "1800-440-2200",
                "consumer_care_email": "support@puritydairy.in",
                "measured_numeral_height_mm": 2.5,
                "measured_letter_height_mm": 1.2,
                "has_qr_code": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "box": [40, 140, 600, 185], "color": "#10b981"},
                {"label": "Manufacturer Address", "box": [40, 200, 650, 255], "color": "#10b981"},
                {"label": "CRITICAL VIOLATION: Future Mfg Date", "box": [40, 570, 650, 615], "color": "#ef4444"}
            ]
        },
        {
            "id": "sample_05",
            "title": "SoundMax True Wireless Earbuds",
            "category": "Consumer Electronics",
            "filename": "sample_05_qr_code_electronics.jpg",
            "bg_color": (248, 250, 252),
            "border_color": (59, 130, 246), # Blue
            "details": [
                ("Manufacturer Name (Physical):", "Apex Audio Technologies Pvt Ltd", False),
                ("Statutory QR Code Declaration:", "Scan QR code for complete factory address, technical specifications and size.", False),
                ("Consumer Helpline (Physical as per G.S.R. 577(E)):", "Toll Free: 1800-112-9900, Email: support@apexaudio.in", False),
                ("Package Contents:", "Earbuds (1 Pair), Charging Case (1 U), USB-C Cable (1 U)", False)
            ],
            "stamp": {
                "coords": (40, 480, 500, 680),
                "lines": [
                    "MODEL NO: SM-ANC20",
                    "NET QUANTITY: 1 U",
                    "MFG DATE: 08/2026",
                    "MRP: Rs. 1499.00 (inclusive of all taxes)",
                    "UNIT SALE PRICE: Rs. 1499.00 per number"
                ],
                "draw_qr": True
            },
            "extracted_data": {
                "commodity_name": "SoundMax True Wireless Earbuds",
                "generic_name": "True Wireless Earbuds",
                "category": "Consumer Electronics",
                "manufacturer_name": "Apex Audio Technologies Pvt Ltd",
                "manufacturer_address": "", # Allowed via QR under G.S.R. 577(E)
                "country_of_origin": "India",
                "net_quantity_raw": "1 U",
                "net_quantity_value": 1.0,
                "net_quantity_unit": "U",
                "mrp_raw": "Rs. 1499.00 (inclusive of all taxes)",
                "mrp_value": 1499.0,
                "unit_sale_price_raw": "Rs. 1499.00 per number",
                "unit_sale_price_value": 1499.0,
                "mfg_date": "08/2026",
                "consumer_care_phone": "1800-112-9900",
                "consumer_care_email": "support@apexaudio.in",
                "measured_numeral_height_mm": 2.0,
                "measured_letter_height_mm": 1.2,
                "has_qr_code": True,
                "qr_scan_instruction": "Scan QR code for complete factory address and specifications."
            },
            "bounding_boxes": [
                {"label": "Manufacturer Name", "box": [40, 140, 500, 185], "color": "#3b82f6"},
                {"label": "Mandatory Physical Contact", "box": [40, 270, 650, 320], "color": "#10b981"},
                {"label": "Scannable QR Code", "box": [520, 710, 660, 850], "color": "#3b82f6"}
            ]
        }
    ]

    for s in samples_meta:
        img_path = create_label_image(
            filename=s["filename"],
            bg_color=s["bg_color"],
            border_color=s["border_color"],
            title=s["title"],
            details=s["details"],
            stamp_box=s["stamp"]
        )
        s["image_rel_path"] = f"/static/images/{s['filename']}"
        json_path = os.path.join(SAMPLE_DIR, f"{s['id']}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
        print(f"Generated sample: {s['id']} -> {img_path}")

    print("All 5 test scenario mockups generated successfully!")

if __name__ == "__main__":
    generate_all_samples()
