"""
run_tests.py - the test-suite (Task 7).
Each test has: an input, the answer the HANDBOOK gives (expected), and what the system says.
A test PASSES when the system's decision code equals the expected one.
For invalid inputs the expected answer is REJECT (a clear error message, no crash).
Run:  python run_tests.py      -> prints a table and writes outputs/test_results.csv / .json
"""
import csv, json, os
import systems as S

BS = "BBA / BEE / BS"; MS = "MBA / MS / MPhil"; PHD = "PhD"
ADV = "Advance Merit (Board Topper / Top Ranker / A-Levels)"
MNE = "Merit - Batch Topper (non-engineering)"; ME = "Merit - Batch Topper (engineering)"
FAS = "Financial Assistance Scholarship (FAS)"; QRZ = "Qarz-e-Hasna (existing awardees only)"

N, B, I, L = "Normal", "Boundary", "Invalid", "Limitation"
# (module, type, description, args, expected decision, handbook reason)
TESTS = [
 # ---- Module 1 : probation & drop (5.5) ----
 ("M1", N, "BS, CGPA 3.20, no probation", dict(programme=BS, cgpa=3.20, probations=0), "NO_ACTION", "3.20 >= 2.0 (5.5.1)"),
 ("M1", N, "BS, CGPA 2.80 after 1 probation", dict(programme=BS, cgpa=2.80, probations=1), "NO_ACTION", "CGPA back above 2.0: out of probation (5.5.4)"),
 ("M1", N, "BS, CGPA 1.80, first time", dict(programme=BS, cgpa=1.80, probations=0), "PROBATION_1", "below 2.0 (5.5.1)"),
 ("M1", N, "BS, CGPA 1.60 after 1 probation", dict(programme=BS, cgpa=1.60, probations=1), "PROBATION_2", "2nd consecutive probation (5.5.5)"),
 ("M1", N, "BS, CGPA 1.40 after 2 probations", dict(programme=BS, cgpa=1.40, probations=2), "DROP", "dropped after two probations (5.5.3)"),
 ("M1", N, "MS, CGPA 2.40, first time", dict(programme=MS, cgpa=2.40, probations=0), "PROBATION_1", "MS minimum is 2.5 (5.5.1)"),
 ("M1", N, "PhD, CGPA 2.90, first time", dict(programme=PHD, cgpa=2.90, probations=0), "PROBATION_1", "PhD minimum is 3.0 (5.5.1)"),
 ("M1", B, "BS, CGPA exactly 2.00", dict(programme=BS, cgpa=2.00, probations=0), "NO_ACTION", "2.00 meets the minimum (5.5.1)"),
 ("M1", B, "BS, CGPA 1.99", dict(programme=BS, cgpa=1.99, probations=0), "PROBATION_1", "1.99 < 2.0 (5.5.1)"),
 ("M1", B, "MS, CGPA exactly 2.50 after 1 probation", dict(programme=MS, cgpa=2.50, probations=1), "NO_ACTION", "equal to minimum clears probation (5.5.4)"),
 ("M1", B, "PhD, CGPA exactly 3.00 after 2 probations", dict(programme=PHD, cgpa=3.00, probations=2), "NO_ACTION", "equal to minimum, no drop (5.5.3, 5.5.4)"),
 ("M1", B, "BS, CGPA 2.01 after 2 probations", dict(programme=BS, cgpa=2.01, probations=2), "NO_ACTION", "above minimum, no drop (5.5.3)"),
 ("M1", B, "BS, CGPA 0.00 (lowest), first time", dict(programme=BS, cgpa=0.00, probations=0), "PROBATION_1", "far below 2.0 (5.5.1)"),
 ("M1", B, "BS, CGPA 4.00 (highest)", dict(programme=BS, cgpa=4.00, probations=0), "NO_ACTION", "above minimum"),
 ("M1", I, "CGPA -0.5", dict(programme=BS, cgpa=-0.5, probations=0), "REJECT", "CGPA cannot be negative"),
 ("M1", I, "CGPA 4.5", dict(programme=BS, cgpa=4.5, probations=0), "REJECT", "CGPA cannot exceed 4.00"),
 ("M1", I, "CGPA typed as 'abc'", dict(programme=BS, cgpa="abc", probations=0), "REJECT", "not a number"),
 ("M1", I, "3 earlier probations", dict(programme=BS, cgpa=1.5, probations=3), "REJECT", "handbook only defines 0, 1, 2 probations"),
 ("M1", I, "1.5 earlier probations", dict(programme=BS, cgpa=1.5, probations=1.5), "REJECT", "a count must be whole"),
 ("M1", I, "Programme 'MBBS' (not in 5.5.1 table)", dict(programme="MBBS", cgpa=2.5, probations=0), "REJECT", "programme not in table"),
 # ---- Module 2 : honours (5.6 - 5.9) ----
 ("M2", N, "CGPA 3.95, clean record", dict(cgpa=3.95), "SUMMA_CUM_LAUDE", "3.95 >= 3.90 (5.8.1)"),
 ("M2", N, "CGPA 3.85, clean record", dict(cgpa=3.85), "MAGNA_CUM_LAUDE", "3.80 <= 3.85 < 3.90 (5.8.1)"),
 ("M2", N, "CGPA 3.70, clean record", dict(cgpa=3.70), "CUM_LAUDE", "3.60 <= 3.70 < 3.80 (5.8.1)"),
 ("M2", N, "CGPA 3.40, clean record", dict(cgpa=3.40), "NOT_ELIGIBLE", "below 3.60 (5.6.3)"),
 ("M2", N, "CGPA 2.90, clean record", dict(cgpa=2.90), "NOT_ELIGIBLE", "below 3.60 (5.6.3)"),
 ("M2", N, "CGPA 3.95 but disciplinary penalty", dict(cgpa=3.95, broken_conditions=["5.6.6"]), "NOT_ELIGIBLE", "5.6.6 broken"),
 ("M2", N, "CGPA 3.70, repeated a course + summer course", dict(cgpa=3.70, broken_conditions=["5.6.2", "5.6.5"]), "NOT_ELIGIBLE", "5.6.2 and 5.6.5 broken"),
 ("M2", B, "CGPA exactly 3.60", dict(cgpa=3.60), "CUM_LAUDE", ">= 3.60 (5.6.3, 5.8.1)"),
 ("M2", B, "CGPA 3.59", dict(cgpa=3.59), "NOT_ELIGIBLE", "< 3.60 (5.6.3)"),
 ("M2", B, "CGPA exactly 3.80", dict(cgpa=3.80), "MAGNA_CUM_LAUDE", ">= 3.80 (5.8.1)"),
 ("M2", B, "CGPA 3.79", dict(cgpa=3.79), "CUM_LAUDE", "< 3.80 (5.8.1)"),
 ("M2", B, "CGPA exactly 3.90", dict(cgpa=3.90), "SUMMA_CUM_LAUDE", ">= 3.90 (5.8.1)"),
 ("M2", B, "CGPA 3.89", dict(cgpa=3.89), "MAGNA_CUM_LAUDE", "< 3.90 (5.8.1)"),
 ("M2", B, "CGPA 4.00", dict(cgpa=4.00), "SUMMA_CUM_LAUDE", "top of scale"),
 ("M2", I, "CGPA 4.2", dict(cgpa=4.2), "REJECT", "CGPA cannot exceed 4.00"),
 ("M2", I, "CGPA left empty", dict(cgpa=""), "REJECT", "missing input"),
 ("M2", I, "unknown condition '5.6.9'", dict(cgpa=3.8, broken_conditions=["5.6.9"]), "REJECT", "no such clause"),
 ("M2", I, "CGPA typed with a comma '3,85'", dict(cgpa="3,85"), "MAGNA_CUM_LAUDE", "a student means 3.85 -> Magna (5.8.1)"),
 ("M2", L, "Rank 1 in batch, CGPA 3.95: Gold medal?", dict(cgpa=3.95), "GOLD_MEDAL", "Gold = highest CGPA in batch (5.7.1.1)"),
 # ---- Module 3 : scholarships (Chapter 4) ----
 ("M3", N, "FAS, CGPA 3.00", dict(category=FAS, cgpa=3.00), "RETAIN", ">= 2.50 (4.5.2)"),
 ("M3", N, "Advance Merit, CGPA 3.80, full load", dict(category=ADV, cgpa=3.80, load_pct=100), "RETAIN", ">= 3.50 (4.3.2.2)"),
 ("M3", N, "Merit non-eng, 3.90, full load", dict(category=MNE, cgpa=3.90, load_pct=100), "RETAIN", ">= 3.75 (4.4.3.3)"),
 ("M3", N, "Merit non-eng, 3.90, only 60% load", dict(category=MNE, cgpa=3.90, load_pct=60), "WITHHOLD", "regular load needed (4.4.3.5)"),
 ("M3", N, "Advance Merit, CGPA 3.00", dict(category=ADV, cgpa=3.00, load_pct=100), "WITHHOLD", "< 3.50 (4.3.2.2)"),
 ("M3", B, "FAS exactly 2.50", dict(category=FAS, cgpa=2.50), "RETAIN", "'not fall below 2.50' (4.5.2)"),
 ("M3", B, "FAS 2.49", dict(category=FAS, cgpa=2.49), "WITHHOLD", "< 2.50 (4.5.3d)"),
 ("M3", B, "Qarz-e-Hasna exactly 2.75", dict(category=QRZ, cgpa=2.75), "RETAIN", "at least 2.75 (4.9)"),
 ("M3", B, "Qarz-e-Hasna 2.74", dict(category=QRZ, cgpa=2.74), "WITHHOLD", "< 2.75 (4.9)"),
 ("M3", B, "Advance Merit exactly 3.50", dict(category=ADV, cgpa=3.50, load_pct=100), "RETAIN", "at least 3.50 (4.3.2.2)"),
 ("M3", B, "Advance Merit 3.49", dict(category=ADV, cgpa=3.49, load_pct=100), "WITHHOLD", "< 3.50 (4.3.2.2)"),
 ("M3", B, "Merit non-eng exactly 3.75", dict(category=MNE, cgpa=3.75, load_pct=100), "RETAIN", ">= 3.75 (4.4.3.3)"),
 ("M3", B, "Merit non-eng 3.74", dict(category=MNE, cgpa=3.74, load_pct=100), "WITHHOLD", "< 3.75 (4.4.3.3)"),
 ("M3", B, "Merit engineering exactly 3.60", dict(category=ME, cgpa=3.60, load_pct=100), "RETAIN", ">= 3.60 (4.4.3.3)"),
 ("M3", B, "Merit engineering 3.59", dict(category=ME, cgpa=3.59, load_pct=100), "WITHHOLD", "< 3.60 (4.4.3.3)"),
 ("M3", B, "Merit eng 3.90, load 95% (almost regular)", dict(category=ME, cgpa=3.90, load_pct=95), "WITHHOLD", "strict reading: load must be regular (4.4.3.5)"),
 ("M3", I, "Course load 150%", dict(category=MNE, cgpa=3.9, load_pct=150), "REJECT", "load outside 0-120%"),
 ("M3", I, "Unknown scholarship 'Naval Shuhada'", dict(category="Naval Shuhada", cgpa=3.0), "REJECT", "not modelled"),
 ("M3", I, "CGPA 4.5", dict(category=FAS, cgpa=4.5), "REJECT", "CGPA cannot exceed 4.00"),
 ("M3", L, "Rank 4 in batch, CGPA 3.90: merit scholarship?", dict(category=MNE, cgpa=3.90, load_pct=100), "WITHHOLD", "only top 3 get it (4.4.1)"),
 ("M3", L, "NEW student asks for Qarz-e-Hasna, CGPA 3.0", dict(category=QRZ, cgpa=3.0), "WITHHOLD", "discontinued from Fall 2020 (4.8)"),
]
FUNCS = {"M1": S.evaluate_standing, "M2": S.evaluate_honours, "M3": S.evaluate_scholarship}


def run():
    rows = []
    for i, (mod, typ, desc, args, expected, why) in enumerate(TESTS, 1):
        try:
            r = FUNCS[mod](**args)
            got, out = r["decision"], f"{r['label']} ({r['crisp']:.1f})"
        except ValueError as e:
            got, out = "REJECT", "error: " + str(e)[:70]
        rows.append(dict(id=f"T{i:02d}", module=mod, type=typ, query=desc, input=json.dumps(args, ensure_ascii=False),
                         expected=expected, why=why, system=out, decision=got, result="PASS" if got == expected else "FAIL"))
    return rows


if __name__ == "__main__":
    rows = run()
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/test_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    json.dump(rows, open("outputs/test_results.json", "w"), indent=1)
    for r in rows:
        print(f"{r['id']} {r['module']} {r['type']:10s} {r['result']}  exp={r['expected']:16s} got={r['decision']:16s} {r['query']}")
    n = len(rows); p = sum(r["result"] == "PASS" for r in rows)
    print(f"\nTOTAL {n}  PASSED {p}  FAILED {n-p}  ACCURACY {100*p/n:.1f}%")
    for key in ("module", "type"):
        for k in sorted({r[key] for r in rows}):
            sub = [r for r in rows if r[key] == k]
            print(f"  {key}={k}: {sum(r['result']=='PASS' for r in sub)}/{len(sub)}")
