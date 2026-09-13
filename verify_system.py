"""
End-to-End System Verification Test Script
Uses TestClient to test all endpoints, rule evaluations, database persistence, and PDF report generation.
"""

from starlette.testclient import TestClient
from app import app
import os

client = TestClient(app)

def run_tests():
    print("=== STARTING LMPC SYSTEM VERIFICATION TESTS ===")
    
    # 1. Test Dashboard UI endpoint
    r = client.get("/")
    assert r.status_code == 200, f"Dashboard failed with {r.status_code}"
    print("[PASS] GET / (Dashboard UI serves HTTP 200)")

    # 2. Test Demo Sample 01 (Compliant Snack Pack)
    r1 = client.post("/api/scan/demo/sample_01")
    assert r1.status_code == 200, f"Sample 01 failed: {r1.text}"
    data1 = r1.json()
    assert data1["compliance_result"]["is_compliant"] is True
    assert data1["compliance_result"]["compliance_score"] == 100.0
    print(f"[PASS] Sample 01 (Compliant): Score {data1['compliance_result']['compliance_score']}% | Violations: {len(data1['compliance_result']['violations'])}")

    # 3. Test Demo Sample 02 (Illegal 'gms' Unit & Font Height)
    r2 = client.post("/api/scan/demo/sample_02")
    assert r2.status_code == 200, f"Sample 02 failed: {r2.text}"
    data2 = r2.json()
    assert data2["compliance_result"]["is_compliant"] is False
    assert len(data2["compliance_result"]["violations"]) >= 2
    rule_ids = [v["rule_id"] for v in data2["compliance_result"]["violations"]]
    assert "RULE_13_5_NON_STANDARD_UNIT" in rule_ids
    assert "RULE_7_NUMERAL_HEIGHT" in rule_ids
    print(f"[PASS] Sample 02 (Illegal 'gms' & Font): Violations detected -> {rule_ids}")

    # 4. Test Demo Sample 03 (Missing Unit Sale Price - 2021 Amendment)
    r3 = client.post("/api/scan/demo/sample_03")
    assert r3.status_code == 200
    data3 = r3.json()
    assert data3["compliance_result"]["is_compliant"] is False
    rule_ids3 = [v["rule_id"] for v in data3["compliance_result"]["violations"]]
    assert "RULE_6_11_USP_MISSING" in rule_ids3
    print(f"[PASS] Sample 03 (Missing USP): Violations detected -> {rule_ids3}")

    # 5. Test Demo Sample 04 (Future Mfg Date Fraud)
    r4 = client.post("/api/scan/demo/sample_04")
    assert r4.status_code == 200
    data4 = r4.json()
    assert data4["compliance_result"]["is_compliant"] is False
    rule_ids4 = [v["rule_id"] for v in data4["compliance_result"]["violations"]]
    assert "RULE_6_1_D_FUTURE_DATE" in rule_ids4
    print(f"[PASS] Sample 04 (Future Date): Violations detected -> {rule_ids4}")

    # 6. Test Demo Sample 05 (Electronics QR Code - 2022 Amendment)
    r5 = client.post("/api/scan/demo/sample_05")
    assert r5.status_code == 200
    data5 = r5.json()
    assert data5["compliance_result"]["is_compliant"] is True
    print(f"[PASS] Sample 05 (QR Code Electronics): Score {data5['compliance_result']['compliance_score']}% under G.S.R. 577(E)")

    # 7. Test Metrics & History
    rm = client.get("/api/metrics")
    assert rm.status_code == 200
    metrics = rm.json()
    assert metrics["total_scanned"] >= 5
    print(f"[PASS] Metrics Endpoint: Total Scans = {metrics['total_scanned']} | Pass Rate = {metrics['compliance_rate']}%")

    # 8. Test PDF Report Generation
    scan_id = data2["scan_id"]
    r_pdf = client.get(f"/api/report/{scan_id}")
    assert r_pdf.status_code == 200
    assert r_pdf.headers.get("content-type") == "application/pdf"
    assert len(r_pdf.content) > 1000
    print(f"[PASS] PDF Generation: Generated Seventh Schedule Inspection Report ({len(r_pdf.content)} bytes)")

    print("\n========================================================")
    print("*** ALL 8 STATUTORY VERIFICATION TESTS PASSED SUCCESSFULLY! ***")
    print("========================================================")

if __name__ == "__main__":
    run_tests()
