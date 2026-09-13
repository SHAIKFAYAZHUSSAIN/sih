"""
SQLite Repository for Legal Metrology Inspections
Handles persistent storage and retrieval of product scans, violations, and compliance metrics.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "c:/Users/sfaya/Documents/SIH/lmpc_inspections.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_uid TEXT UNIQUE,
        commodity_name TEXT,
        category TEXT,
        manufacturer_name TEXT,
        image_path TEXT,
        net_quantity TEXT,
        mrp TEXT,
        unit_sale_price TEXT,
        mfg_date TEXT,
        is_compliant INTEGER,
        compliance_score REAL,
        violations_count INTEGER,
        inspected_at TEXT,
        raw_extracted_json TEXT,
        raw_result_json TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        rule_id TEXT,
        rule_reference TEXT,
        severity TEXT,
        title TEXT,
        description TEXT,
        penalty_ref TEXT,
        FOREIGN KEY (scan_id) REFERENCES scans (id)
    );
    """)

    conn.commit()
    conn.close()

def save_scan(extracted: Dict[str, Any], result: Dict[str, Any], image_path: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scan_uid = f"LM-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()*1000) % 100000:05d}"
    
    name = extracted.get("generic_name") or extracted.get("commodity_name") or "Unspecified Packaged Commodity"
    category = extracted.get("category") or "FMCG Retail"
    mfg_name = extracted.get("manufacturer_name") or "Unknown Manufacturer"
    
    net_qty_str = f"{extracted.get('net_quantity_value', '')} {extracted.get('net_quantity_unit', '')}".strip()
    mrp_str = f"₹{extracted.get('mrp_value', '')}" if extracted.get('mrp_value') is not None else str(extracted.get('mrp_raw', ''))
    usp_str = f"₹{extracted.get('unit_sale_price_value', '')}" if extracted.get('unit_sale_price_value') is not None else str(extracted.get('unit_sale_price_raw', ''))
    mfg_date_str = str(extracted.get("mfg_date", ""))
    
    is_compliant = 1 if result.get("is_compliant") else 0
    score = float(result.get("compliance_score", 0.0))
    violations = result.get("violations", [])
    
    cursor.execute("""
    INSERT INTO scans (
        scan_uid, commodity_name, category, manufacturer_name, image_path,
        net_quantity, mrp, unit_sale_price, mfg_date, is_compliant,
        compliance_score, violations_count, inspected_at,
        raw_extracted_json, raw_result_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_uid, name, category, mfg_name, image_path,
        net_qty_str, mrp_str, usp_str, mfg_date_str, is_compliant,
        score, len(violations), now_str,
        json.dumps(extracted), json.dumps(result)
    ))
    
    scan_id = cursor.lastrowid
    
    for v in violations:
        cursor.execute("""
        INSERT INTO violations (
            scan_id, rule_id, rule_reference, severity, title, description, penalty_ref
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_id,
            v.get("rule_id", ""),
            v.get("rule_reference", ""),
            v.get("severity", ""),
            v.get("title", ""),
            v.get("description", ""),
            v.get("statutory_penalty_ref", "Section 36(1)")
        ))
        
    conn.commit()
    conn.close()
    return scan_id

def get_all_scans(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, scan_uid, commodity_name, category, manufacturer_name, image_path,
           net_quantity, mrp, unit_sale_price, mfg_date, is_compliant, compliance_score,
           violations_count, inspected_at
    FROM scans
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

def get_scan_by_id(scan_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    scan_row = cursor.fetchone()
    if not scan_row:
        conn.close()
        return None
    
    scan_dict = dict(scan_row)
    scan_dict["raw_extracted"] = json.loads(scan_dict.get("raw_extracted_json") or "{}")
    scan_dict["raw_result"] = json.loads(scan_dict.get("raw_result_json") or "{}")
    
    cursor.execute("SELECT * FROM violations WHERE scan_id = ?", (scan_id,))
    v_rows = cursor.fetchall()
    scan_dict["violations"] = [dict(r) for r in v_rows]
    
    conn.close()
    return scan_dict

def get_dashboard_metrics() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM scans")
    total = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as compliant FROM scans WHERE is_compliant = 1")
    compliant = cursor.fetchone()["compliant"]
    
    cursor.execute("SELECT AVG(compliance_score) as avg_score FROM scans")
    avg_score_res = cursor.fetchone()["avg_score"]
    avg_score = round(avg_score_res, 1) if avg_score_res is not None else 100.0
    
    cursor.execute("""
    SELECT rule_reference, COUNT(*) as count 
    FROM violations 
    GROUP BY rule_reference 
    ORDER BY count DESC 
    LIMIT 5
    """)
    top_violations = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return {
        "total_scanned": total,
        "compliant_count": compliant,
        "non_compliant_count": total - compliant,
        "compliance_rate": round((compliant / total * 100), 1) if total > 0 else 100.0,
        "avg_compliance_score": avg_score,
        "top_infringements": top_violations
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
