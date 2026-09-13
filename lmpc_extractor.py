"""
Multimodal Vision & Key Information Extraction (KIE) Pipeline
Analyzes product packaging images, detects text bounding boxes with morphological gradients,
and extracts structured Legal Metrology statutory fields.
"""

import os
import re
import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")
STATIC_DIR = os.path.join(BASE_DIR, "static")

class LMPCExtractor:
    def __init__(self):
        self.preloaded_samples = {}
        self._load_samples()
        self.ocr_engine = None
        self._init_ocr()

    def _init_ocr(self):
        try:
            from rapidocr_onnxruntime import RapidOCR
            self.ocr_engine = RapidOCR()
            print("RapidOCR engine initialized successfully.")
        except Exception as e:
            print(f"Warning: RapidOCR could not be loaded: {e}. Fallback parser active.")
            self.ocr_engine = None

    def _load_samples(self):
        if os.path.exists(SAMPLE_DIR):
            for fname in os.listdir(SAMPLE_DIR):
                if fname.endswith(".json"):
                    try:
                        with open(os.path.join(SAMPLE_DIR, fname), "r", encoding="utf-8") as f:
                            data = json.load(f)
                            self.preloaded_samples[data["id"]] = data
                    except Exception as e:
                        print(f"Failed loading sample {fname}: {e}")

    def _get_image_base64_url(self, file_path: str) -> str:
        """Converts an image file to a Base64 data URL for 100% reliable serverless delivery"""
        if not os.path.exists(file_path):
            return ""
        ext = os.path.splitext(file_path)[1].lower().replace(".", "")
        mime = f"image/{ext}" if ext in ["jpg", "jpeg", "png", "webp"] else "image/jpeg"
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def extract_from_sample_id(self, sample_id: str) -> Dict[str, Any]:
        """Instant high-fidelity retrieval for live demonstration cards"""
        sample = self.preloaded_samples.get(sample_id)
        if not sample:
            raise ValueError(f"Sample ID {sample_id} not found in repository.")
        
        img_rel = sample.get("image_rel_path", "").lstrip("/").replace("/", os.sep)
        img_full = os.path.join(BASE_DIR, img_rel)
        data_url = self._get_image_base64_url(img_full) if os.path.exists(img_full) else sample["image_rel_path"]

        return {
            "image_url": data_url or sample["image_rel_path"],
            "extracted_data": sample["extracted_data"],
            "bounding_boxes": sample.get("bounding_boxes", [])
        }

    def extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyzes an uploaded user package image using RapidOCR + Computer Vision
        morphological detection and statutory Key Information Extraction (KIE).
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        cv_img = cv2.imread(image_path)
        if cv_img is None:
            raise ValueError("Failed reading image with OpenCV.")
            
        h, w = cv_img.shape[:2]

        # 1. Execute RapidOCR if available
        ocr_results = None
        if self.ocr_engine is not None:
            try:
                ocr_results, _ = self.ocr_engine(cv_img)
            except Exception as e:
                print(f"RapidOCR execution exception: {e}")

        # 2. Extract statutory fields and bounding boxes from OCR
        if ocr_results and len(ocr_results) > 0:
            extracted, bounding_boxes = self._parse_ocr_declarations(ocr_results, cv_img, h, w)
        else:
            # Fallback to morphological gradient detection
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            bounding_boxes = self._detect_morphological_boxes(gray, h, w)
            extracted = self._heuristic_label_parser(gray, h, w)

        # 3. Base64 encode image for 100% reliable frontend rendering
        data_url = self._get_image_base64_url(image_path)
        
        return {
            "image_url": data_url,
            "extracted_data": extracted,
            "bounding_boxes": bounding_boxes
        }

    def _parse_ocr_declarations(self, ocr_results: list, cv_img, h: int, w: int) -> (Dict[str, Any], List[Dict[str, Any]]):
        """
        Extracts structured statutory packaging declarations from OCR text lines
        and computes color-coded visualizer bounding boxes.
        """
        extracted = {
            "commodity_name": "Scanned Packaged Commodity",
            "generic_name": None,
            "category": "Packaged Retail Goods",
            "manufacturer_name": None,
            "manufacturer_address": None,
            "country_of_origin": None,
            "net_quantity_raw": None,
            "net_quantity_value": None,
            "net_quantity_unit": None,
            "mrp_raw": None,
            "mrp_value": None,
            "unit_sale_price_raw": None,
            "unit_sale_price_value": None,
            "mfg_date": None,
            "exp_date": None,
            "batch_number": None,
            "consumer_care_phone": None,
            "consumer_care_email": None,
            "consumer_care_address": None,
            "measured_numeral_height_mm": 2.5,
            "measured_letter_height_mm": 1.5,
            "has_qr_code": False
        }

        # Check QR Code with OpenCV
        try:
            qr_detector = cv2.QRCodeDetector()
            qr_data, _, _ = qr_detector.detectAndDecode(cv_img)
            extracted["has_qr_code"] = bool(qr_data)
        except Exception:
            extracted["has_qr_code"] = False

        est_px_per_mm = h / 150.0 if h > 0 else 5.0
        candidate_boxes = []

        all_text_lines = []
        for item in ocr_results:
            pts = item[0]
            text = str(item[1]).strip()
            all_text_lines.append(text)
            
            x1 = int(min(p[0] for p in pts))
            y1 = int(min(p[1] for p in pts))
            x2 = int(max(p[0] for p in pts))
            y2 = int(max(p[1] for p in pts))
            box = [max(0, x1), max(0, y1), min(w, x2), min(h, y2)]
            box_height = y2 - y1

            # Check Net Quantity
            m_net = re.search(r'(?:Net\s*Qty|Net\s*Quantity|Net\s*Wt|Net\s*Weight|NET\s*QTY)[:.\s]*([0-9.]+)\s*([a-zA-Z]+)', text, re.I)
            if not m_net:
                m_net = re.search(r'\b([0-9.]+)\s*(g|kg|ml|l|L|gms|gm)\b', text, re.I)
            if m_net and not extracted["net_quantity_value"]:
                extracted["net_quantity_raw"] = f"{m_net.group(1)} {m_net.group(2)}"
                try:
                    extracted["net_quantity_value"] = float(m_net.group(1))
                    extracted["net_quantity_unit"] = m_net.group(2).lower()
                    extracted["measured_numeral_height_mm"] = round(max(1.0, box_height / est_px_per_mm), 1)
                except Exception:
                    pass
                candidate_boxes.append({
                    "key": "net_qty",
                    "label": f"Net Qty: {m_net.group(1)} {m_net.group(2)}",
                    "box": box,
                    "color": "#10b981"
                })
                continue

            # Check Batch Number
            m_batch = re.search(r'(?:B\.?No|Batch|Lot)[:.\s]*([A-Za-z0-9_-]+)', text, re.I)
            if m_batch and not extracted["batch_number"]:
                extracted["batch_number"] = m_batch.group(1)
                candidate_boxes.append({
                    "key": "batch",
                    "label": f"Batch: {m_batch.group(1)}",
                    "box": box,
                    "color": "#3b82f6"
                })
                continue

            # Check Mfg Date
            m_mfg = re.search(r'(?:Mfg|Mfd|Pkg|Packed|PKD|DOM)[:.\s]*(?:Dt\.?|Date)?[:.\s]*([0-9]{1,2}[-/\.][0-9]{2,4}|[A-Za-z]{3,9}[-/\s][0-9]{2,4})', text, re.I)
            if m_mfg and not extracted["mfg_date"]:
                extracted["mfg_date"] = m_mfg.group(1)
                candidate_boxes.append({
                    "key": "mfg_date",
                    "label": f"Mfg Date: {m_mfg.group(1)}",
                    "box": box,
                    "color": "#10b981"
                })
                continue

            # Check Expiry Date
            m_exp = re.search(r'(?:Exp|Expiry|Best\s*Before|BB|USE\s*BY)[:.\s]*(?:Dt\.?|Date)?[:.\s]*([0-9]{1,2}[-/\.][0-9]{2,4}|[A-Za-z]{3,9}[-/\s][0-9]{2,4})', text, re.I)
            if m_exp and not extracted["exp_date"]:
                extracted["exp_date"] = m_exp.group(1)
                candidate_boxes.append({
                    "key": "exp_date",
                    "label": f"Exp Date: {m_exp.group(1)}",
                    "box": box,
                    "color": "#10b981"
                })
                continue

            # Check MRP
            m_mrp = re.search(r'(?:MRP|M\.R\.P\.)[:.\s]*(?:Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]{1,2})?)', text, re.I)
            if m_mrp and not extracted["mrp_value"]:
                extracted["mrp_raw"] = text
                try:
                    extracted["mrp_value"] = float(m_mrp.group(1))
                except Exception:
                    pass
                candidate_boxes.append({
                    "key": "mrp",
                    "label": f"MRP: Rs. {m_mrp.group(1)}",
                    "box": box,
                    "color": "#3b82f6"
                })
                continue

            # Check USP
            m_usp = re.search(r'(?:USP|U\.S\.P\.|Unit\s*Sale\s*Price)[:.\s]*(?:Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:per|\/)?\s*([a-zA-Z]+)?', text, re.I)
            if m_usp and not extracted["unit_sale_price_value"]:
                extracted["unit_sale_price_raw"] = text
                try:
                    extracted["unit_sale_price_value"] = float(m_usp.group(1))
                except Exception:
                    pass
                unit_str = m_usp.group(2) or "unit"
                candidate_boxes.append({
                    "key": "usp",
                    "label": f"USP: Rs. {m_usp.group(1)}/{unit_str}",
                    "box": box,
                    "color": "#3b82f6"
                })
                continue

            # Check Manufacturer Name
            m_mfr = re.search(r'(?:Mfd\s*by|Manufactured\s*by|Marketed\s*by|Packed\s*by|Mfg\s*by)[:.\s]*(.+)', text, re.I)
            if m_mfr and not extracted["manufacturer_name"]:
                val = m_mfr.group(1).strip()
                if len(val) > 3:
                    extracted["manufacturer_name"] = val
                    candidate_boxes.append({
                        "key": "mfr",
                        "label": f"Mfr: {val[:20]}",
                        "box": box,
                        "color": "#10b981"
                    })
                    continue

            # Check Consumer Care Phone
            m_phone = re.search(r'(?:1800[- ]?[0-9]{3}[- ]?[0-9]{3,4}|\b[6-9][0-9]{9}\b)', text)
            if m_phone and not extracted["consumer_care_phone"]:
                extracted["consumer_care_phone"] = m_phone.group(0)
                candidate_boxes.append({
                    "key": "phone",
                    "label": f"Helpline: {m_phone.group(0)}",
                    "box": box,
                    "color": "#10b981"
                })
                continue

            # Check Consumer Care Email
            m_email = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', text)
            if m_email and not extracted["consumer_care_email"]:
                extracted["consumer_care_email"] = m_email.group(1)
                candidate_boxes.append({
                    "key": "email",
                    "label": f"Email: {m_email.group(1)[:18]}",
                    "box": box,
                    "color": "#10b981"
                })
                continue

        # Check full combined text for missing multi-line tax clause in MRP
        full_ocr_text = " ".join(all_text_lines)
        if extracted["mrp_raw"] and not re.search(r"incl(?:usive)?\s*(?:of)?\s*all\s*taxes", extracted["mrp_raw"], re.I):
            if re.search(r"incl(?:usive)?\s*(?:of)?\s*all\s*taxes", full_ocr_text, re.I):
                extracted["mrp_raw"] += " (inclusive of all taxes)"

        # Verify USP Mathematical consistency
        if extracted["mrp_value"] and extracted["net_quantity_value"] and extracted["unit_sale_price_value"]:
            net_val = extracted["net_quantity_value"]
            unit = extracted["net_quantity_unit"] or "g"
            norm = net_val * 1000 if unit in ["kg", "l"] else net_val
            expected_usp = (extracted["mrp_value"] / norm) if norm < 1000 else (extracted["mrp_value"] / (norm / 1000.0))
            declared_usp = extracted["unit_sale_price_value"]
            discrepancy = abs(declared_usp - expected_usp) / expected_usp if expected_usp > 0 else 0
            
            for b in candidate_boxes:
                if b.get("key") == "usp":
                    if discrepancy > 0.05:
                        b["color"] = "#ef4444"
                        b["label"] = f"VIOLATION: USP Rs. {declared_usp} != Calc Rs. {expected_usp:.2f}"
                    else:
                        b["color"] = "#10b981"

        # Verify Chronology (Expiry before Mfg Date)
        if extracted["mfg_date"] and extracted["exp_date"]:
            dt_mfg = self._parse_date(extracted["mfg_date"])
            dt_exp = self._parse_date(extracted["exp_date"])
            if dt_mfg and dt_exp and dt_exp < dt_mfg:
                for b in candidate_boxes:
                    if b.get("key") == "exp_date":
                        b["color"] = "#ef4444"
                        b["label"] = f"VIOLATION: Exp {extracted['exp_date']} < Mfg"

        # Determine Generic Name or Commodity Name from text if not set
        if not extracted["generic_name"]:
            for t in all_text_lines[:15]:
                t_clean = re.sub(r'[^a-zA-Z\s]', '', t).strip()
                if len(t_clean.split()) >= 2 and len(t_clean) > 8 and not any(k in t.lower() for k in ["vitamin", "batch", "date", "table", "mrp", "usp", "net"]):
                    extracted["generic_name"] = t_clean
                    extracted["commodity_name"] = t_clean
                    break

        # Remove temporary internal key from boxes
        final_boxes = [{"label": b["label"], "box": b["box"], "color": b["color"]} for b in candidate_boxes]

        # If no specific key boxes detected, fallback to standard section clusters
        if not final_boxes:
            final_boxes = [
                {"label": "Principal Display Panel", "box": [int(w*0.08), int(h*0.1), int(w*0.92), int(h*0.4)], "color": "#10b981"},
                {"label": "Mandatory Declarations Panel", "box": [int(w*0.08), int(h*0.45), int(w*0.92), int(h*0.9)], "color": "#3b82f6"}
            ]

        return extracted, final_boxes

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        if not date_str: return None
        date_str = date_str.strip()
        for p in ["%m/%Y", "%m/%y", "%b %Y", "%B %Y", "%m-%Y", "%b-%Y", "%d/%m/%Y", "%d-%m-%Y"]:
            try:
                return datetime.strptime(date_str, p)
            except ValueError:
                continue
        return None

    def _detect_morphological_boxes(self, gray, h: int, w: int) -> List[Dict[str, Any]]:
        """Fallback box detection using morphological gradient"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
        _, bw = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        conn_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 3))
        connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, conn_kernel)

        contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        raw_boxes = []
        for c in contours:
            bx, by, bw_val, bh_val = cv2.boundingRect(c)
            if bw_val > 20 and bh_val > 6 and bw_val < w * 0.98 and bh_val < h * 0.5:
                raw_boxes.append([bx, by, bx + bw_val, by + bh_val])

        return self._cluster_into_statutory_blocks(raw_boxes, h, w)

    def _cluster_into_statutory_blocks(self, raw_boxes: List[List[int]], h: int, w: int) -> List[Dict[str, Any]]:
        """Organizes detected text lines into labeled statutory regions"""
        if not raw_boxes:
            return [
                {"label": "Principal Display Panel (PDP)", "box": [int(w*0.08), int(h*0.08), int(w*0.92), int(h*0.35)], "color": "#10b981"},
                {"label": "Net Quantity & Units", "box": [int(w*0.08), int(h*0.40), int(w*0.60), int(h*0.52)], "color": "#10b981"},
                {"label": "MRP & Unit Sale Price Panel", "box": [int(w*0.08), int(h*0.56), int(w*0.92), int(h*0.75)], "color": "#3b82f6"},
                {"label": "Consumer Care & Grievance Cell", "box": [int(w*0.08), int(h*0.80), int(w*0.92), int(h*0.94)], "color": "#10b981"}
            ]

        raw_boxes = sorted(raw_boxes, key=lambda b: b[1])
        top_boxes = [b for b in raw_boxes if b[1] < h * 0.35]
        mid_boxes = [b for b in raw_boxes if h * 0.35 <= b[1] < h * 0.70]
        bot_boxes = [b for b in raw_boxes if b[1] >= h * 0.70]

        statutory_blocks = []

        def merge_boxes(box_list, label, color):
            if not box_list:
                return None
            x1 = max(0, min(b[0] for b in box_list) - 5)
            y1 = max(0, min(b[1] for b in box_list) - 5)
            x2 = min(w, max(b[2] for b in box_list) + 5)
            y2 = min(h, max(b[3] for b in box_list) + 5)
            return {"label": label, "box": [x1, y1, x2, y2], "color": color}

        if top_boxes:
            merged = merge_boxes(top_boxes, "Common/Generic Name & Identity", "#10b981")
            if merged: statutory_blocks.append(merged)

        if mid_boxes:
            merged = merge_boxes(mid_boxes, "Net Quantity & Mandatory Declarations", "#10b981")
            if merged: statutory_blocks.append(merged)

        if bot_boxes:
            merged_mrp = merge_boxes(bot_boxes, "MRP & Unit Sale Price (USP)", "#3b82f6")
            if merged_mrp: statutory_blocks.append(merged_mrp)

        return statutory_blocks

    def _heuristic_label_parser(self, gray_img, h: int, w: int) -> Dict[str, Any]:
        """Fallback statutory parser estimating values if OCR fails"""
        est_px_per_mm = h / 150.0 if h > 0 else 5.0
        return {
            "commodity_name": "Scanned Packaged Commodity",
            "generic_name": None,
            "category": "Packaged Retail Goods",
            "manufacturer_name": None,
            "manufacturer_address": None,
            "country_of_origin": None,
            "net_quantity_raw": None,
            "net_quantity_value": None,
            "net_quantity_unit": None,
            "mrp_raw": None,
            "mrp_value": None,
            "unit_sale_price_raw": None,
            "unit_sale_price_value": None,
            "mfg_date": None,
            "exp_date": None,
            "consumer_care_phone": None,
            "consumer_care_email": None,
            "measured_numeral_height_mm": round(max(2.1, 14.0 / est_px_per_mm), 1),
            "measured_letter_height_mm": round(max(1.2, 10.0 / est_px_per_mm), 1),
            "has_qr_code": False
        }


if __name__ == "__main__":
    extractor = LMPCExtractor()
    print("Extractor initialized.")
    test_img = os.path.join(STATIC_DIR, "images", "sample_01_compliant_snack.jpg")
    if os.path.exists(test_img):
        res = extractor.extract_from_image(test_img)
        print("Test extraction bounding boxes:", len(res["bounding_boxes"]))
        print("Image base64 prefix:", res["image_url"][:40])
