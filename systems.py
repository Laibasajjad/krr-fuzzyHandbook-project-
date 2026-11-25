"""
systems.py
==========
The THREE fuzzy inference systems of the project, plus the "evaluate_*" functions that the GUI
and the test-suite call.  Each evaluate function:
    1. validates the inputs (raises ValueError with a friendly message for bad data),
    2. turns the handbook's crisp numbers into fuzzy inputs,
    3. runs the Mamdani engine,
    4. returns the crisp score, the linguistic label, the final decision, advice and fired rules.

Module 1  standing_system     Chapter 5.5       Probation / Drop
Module 2  honours_system      Chapter 5.6-5.9   Honours & Rector's list
Module 3  scholarship_system  Chapter 4         Keeping a scholarship
"""
import math
from fuzzy_engine import Variable, Rule, MamdaniSystem
import handbook_data as H

# ===========================================================================
# MODULE 1 : ACADEMIC STANDING  (probation / drop)           handbook 5.5
# ===========================================================================
# Input 1: margin = CGPA - programme minimum.   Input 2: how many probations in a row so far.
margin1 = Variable("margin", -4, 2, 0.01, {
    "Low":        ("trap", (-4, -4, -0.01, 0.0)),      # below the limit  (handbook: "failing to achieve")
    "Borderline": ("trap", (0.0, 0.0, 0.15, 0.35)),    # exactly at the limit, fading out 0.35 above it
    "Safe":       ("trap", (0.15, 0.50, 2, 2)),        # comfortably above the limit
}, unit="CGPA points above the programme minimum")

prob_in = Variable("probations", 0, 2, 0.01, {
    "None": ("trap", (0, 0, 0, 1)),
    "One":  ("tri",  (0, 1, 2)),
    "Two":  ("trap", (1, 2, 2, 2)),
}, unit="consecutive probations already served")

standing_out = Variable("standing", 0, 100, 0.1, {
    "Safe":             ("trap", (0, 0, 10, 25)),
    "Watch":            ("tri",  (15, 30, 45)),
    "First-Probation":  ("tri",  (35, 50, 65)),
    "Second-Probation": ("tri",  (55, 70, 85)),
    "Dropped":          ("trap", (75, 90, 100, 100)),
}, unit="risk score (0 = safest, 100 = dropped)", tie_prefer="high")


def _rule(rid, ifs, then):
    return Rule(rid, ifs, then, H.RULE_BY_ID[rid]["rule"])


standing_system = MamdaniSystem("Academic Standing", [margin1, prob_in], standing_out, [
    _rule("R02", [("margin", "Low"), ("probations", "None")], ("standing", "First-Probation")),
    _rule("R03", [("margin", "Low"), ("probations", "One")], ("standing", "Second-Probation")),
    _rule("R04", [("margin", "Low"), ("probations", "Two")], ("standing", "Dropped")),
    _rule("R05", [("margin", "Safe")], ("standing", "Safe")),
    _rule("R06", [("margin", "Borderline")], ("standing", "Watch")),
])

# ===========================================================================
# MODULE 2 : HONOURS & AWARDS                               handbook 5.6 - 5.9
# ===========================================================================
cgpa_h = Variable("cgpa", 0, 4, 0.01, {
    "Low":            ("trap", (0, 0, 3.30, 3.45)),
    "Near-Miss":      ("trap", (3.30, 3.45, 3.59, 3.60)),
    "Cum-Laude-Band": ("trap", (3.59, 3.60, 3.79, 3.80)),
    "Magna-Band":     ("trap", (3.79, 3.80, 3.89, 3.90)),
    "Summa-Band":     ("trap", (3.89, 3.90, 4, 4)),
}, unit="CGPA")

viol_in = Variable("violations", 0, 6, 0.01, {
    "None": ("trap", (0, 0, 0, 1)),
    "Some": ("trap", (0, 1, 6, 6)),
}, unit="baseline conditions that are NOT met")

honour_out = Variable("honour", 0, 100, 0.1, {
    "Not-Eligible":    ("trap", (0, 0, 10, 25)),
    "Near-Miss":       ("tri",  (15, 30, 45)),
    "Cum-Laude":       ("tri",  (35, 50, 65)),
    "Magna-Cum-Laude": ("tri",  (55, 70, 85)),
    "Summa-Cum-Laude": ("trap", (75, 90, 100, 100)),
}, unit="honour level score", tie_prefer="low")

honours_system = MamdaniSystem("Honours & Awards", [cgpa_h, viol_in], honour_out, [
    _rule("R07", [("violations", "Some")], ("honour", "Not-Eligible")),
    _rule("R08", [("cgpa", "Low")], ("honour", "Not-Eligible")),
    _rule("R09", [("cgpa", "Near-Miss"), ("violations", "None")], ("honour", "Near-Miss")),
    _rule("R10", [("cgpa", "Cum-Laude-Band"), ("violations", "None")], ("honour", "Cum-Laude")),
    _rule("R11", [("cgpa", "Magna-Band"), ("violations", "None")], ("honour", "Magna-Cum-Laude")),
    _rule("R12", [("cgpa", "Summa-Band"), ("violations", "None")], ("honour", "Summa-Cum-Laude")),
])

# ===========================================================================
# MODULE 3 : SCHOLARSHIP CONTINUATION                       handbook Chapter 4
# ===========================================================================
margin3 = Variable("margin", -4, 1.5, 0.01, {
    "Below":       ("trap", (-4, -4, -0.01, 0.0)),
    "At-Limit":    ("trap", (0.0, 0.0, 0.05, 0.15)),
    "Comfortable": ("trap", (0.05, 0.15, 0.30, 0.50)),
    "Strong":      ("trap", (0.30, 0.50, 1.5, 1.5)),
    "Meets":       ("trap", (0.0, 0.0, 1.5, 1.5)),     # helper term = "not Below"
}, unit="CGPA points above the scholarship minimum")

load_in = Variable("load", 0, 120, 0.5, {
    "Reduced":          ("trap", (0, 0, 70, 90)),
    "Slightly-Reduced": ("tri",  (70, 90, 100)),
    "Regular":          ("trap", (90, 100, 120, 120)),
    "Not-Reduced":      ("trap", (70, 90, 120, 120)),      # helper term = "not Reduced"
}, unit="% of the regular course load")

schol_out = Variable("scholarship", 0, 100, 0.1, {
    "Suspended": ("trap", (0, 0, 10, 25)),
    "At-Risk":   ("tri",  (15, 35, 55)),
    "Continue":  ("tri",  (45, 65, 85)),
    "Secure":    ("trap", (75, 90, 100, 100)),
}, unit="scholarship safety score", tie_prefer="low")

scholarship_system = MamdaniSystem("Scholarship Continuation", [margin3, load_in], schol_out, [
    _rule("R19", [("margin", "Below")], ("scholarship", "Suspended")),
    _rule("R20", [("margin", "At-Limit"), ("load", "Not-Reduced")], ("scholarship", "At-Risk")),
    _rule("R21", [("margin", "Comfortable"), ("load", "Regular")], ("scholarship", "Continue")),
    _rule("R22", [("margin", "Strong"), ("load", "Regular")], ("scholarship", "Secure")),
    _rule("R23", [("load", "Reduced")], ("scholarship", "Suspended")),
    _rule("R24", [("load", "Slightly-Reduced"), ("margin", "Meets")], ("scholarship", "At-Risk")),
])

SYSTEMS = {"M1": standing_system, "M2": honours_system, "M3": scholarship_system}


# ===========================================================================
# helpers
# ===========================================================================
def _num(value, name, lo, hi):
    """Turn `value` into a float or raise a friendly ValueError."""
    if value is None or isinstance(value, bool) or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"{name} is missing. Please enter a number.")
    try:
        x = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number (use a dot, e.g. 3.25) - you entered {value!r}.")
    if math.isnan(x) or math.isinf(x):
        raise ValueError(f"{name} must be a real number.")
    if not (lo <= x <= hi):
        raise ValueError(f"{name} must be between {lo} and {hi} - you entered {x}.")
    return x


def _fired(system, res):
    out = []
    for r, s in res["fired"]:
        if s > 1e-9:
            out.append(dict(rid=r.rid, text=r.text, strength=s))
    return sorted(out, key=lambda d: -d["strength"])


def _pack(module, system, res, inputs, derived, decision, interpretation, advice, clauses, **extra):
    d = dict(module=module, system=system, inputs=inputs, derived=derived,
             crisp=res["crisp"], label=res["label"], out_degrees=res["out_degrees"],
             fuzzified=res["fuzzified"], fired=_fired(system, res), decision=decision,
             interpretation=interpretation, advice=advice, clauses=clauses, raw=res)
    d.update(extra)
    return d


# ===========================================================================
# MODULE 1 evaluate
# ===========================================================================
def evaluate_standing(programme, cgpa, probations):
    if programme not in H.PROGRAMMES:
        raise ValueError(f"Unknown programme {programme!r}. Choose one of: {', '.join(H.PROGRAMMES)}.")
    cgpa = _num(cgpa, "CGPA", 0.0, 4.0)
    p = _num(probations, "Number of consecutive probations", 0, 2)
    if abs(p - round(p)) > 1e-9:
        raise ValueError("Number of consecutive probations must be a whole number: 0, 1 or 2.")
    p = int(round(p))

    minimum = H.PROGRAMMES[programme]
    margin = round(cgpa - minimum, 4)
    res = standing_system.infer({"margin": margin, "probations": p})
    label = res["label"]

    decision = {"Safe": "NO_ACTION", "Watch": "NO_ACTION", "First-Probation": "PROBATION_1",
                "Second-Probation": "PROBATION_2", "Dropped": "DROP"}[label]
    interp = (f"Standing = {label} (risk score {res['crisp']:.1f} / 100).  "
              f"Your CGPA {cgpa:.2f} is {abs(margin):.2f} {'above' if margin >= 0 else 'below'} the "
              f"{minimum:.1f} minimum for {programme}.")
    advice = {
        "Safe": [f"You are in good standing. Your CGPA is comfortably above the {minimum:.1f} limit.",
                 "If you were on probation before, it is cleared and your probation count is reset to zero (5.5.4)."],
        "Watch": [f"You meet the {minimum:.1f} limit, so there is NO probation (5.5.1, 5.5.4).",
                  "But the margin is very small. One weak semester could push you below the limit - work on your CGPA now."],
        "First-Probation": ["CGPA is below the minimum, so you are placed on PROBATION (5.5.1).",
                            "The HOD will issue a formal warning letter that you must acknowledge and sign (5.5.2).",
                            "Raise your CGPA to the minimum or higher (Summer session counts) to leave probation (5.5.4)."],
        "Second-Probation": ["CGPA is still below the minimum: this is your 2nd CONSECUTIVE probation (5.5.5).",
                             "You must NOT register for a new course / semester without the prior approval of the Principal, through your HOD (5.5.5).",
                             "If you fail to reach the minimum in the next semester you will be DROPPED (5.5.3)."],
        "Dropped": ["You failed to reach the minimum CGPA in the semester after two consecutive probations, so you are DROPPED from the programme (5.5.3).",
                    "You may return only as a NEW student after qualifying the entry test, on merit (5.5.6)."],
    }[label]
    return _pack("M1", standing_system, res, dict(programme=programme, cgpa=cgpa, probations=p),
                 dict(minimum=minimum, margin=margin), decision, interp, advice,
                 "5.5.1, 5.5.2, 5.5.3, 5.5.4, 5.5.5, 5.5.6")


# ===========================================================================
# MODULE 2 evaluate
# ===========================================================================
def rector_degree(cgpa):
    """Rule R13 (handbook 5.9): degree to which a semester CGPA belongs to the Rector's Honours List."""
    return cgpa_h.degree("Summa-Band", cgpa)


def evaluate_honours(cgpa, broken_conditions=()):
    """broken_conditions = iterable of clause numbers (e.g. '5.6.4') that are NOT satisfied."""
    cgpa = _num(cgpa, "CGPA", 0.0, 4.0)
    valid = [c for c, _ in H.BASELINE_CONDITIONS]
    broken = list(broken_conditions)
    for b in broken:
        if b not in valid:
            raise ValueError(f"Unknown baseline condition {b!r}. Valid: {', '.join(valid)}.")
    broken = sorted(set(broken))
    res = honours_system.infer({"cgpa": cgpa, "violations": len(broken)})
    label = res["label"]
    decision = {"Not-Eligible": "NOT_ELIGIBLE", "Near-Miss": "NOT_ELIGIBLE", "Cum-Laude": "CUM_LAUDE",
                "Magna-Cum-Laude": "MAGNA_CUM_LAUDE", "Summa-Cum-Laude": "SUMMA_CUM_LAUDE"}[label]
    rd = rector_degree(cgpa)
    interp = f"Honour level = {label} (score {res['crisp']:.1f} / 100) for CGPA {cgpa:.2f}."
    if broken:
        advice = [f"Baseline condition(s) not met: {', '.join(broken)} (clause 5.6). Under 5.6 you are not eligible for any honour or award, whatever your CGPA."]
    elif label == "Not-Eligible":
        advice = ["Your CGPA is below the 3.60 needed for any honour (5.6.3, 5.8.1)."]
    elif label == "Near-Miss":
        advice = [f"Not eligible yet: the minimum is 3.60 (5.6.3) and you are {3.60 - cgpa:.2f} short. Honours are decided on the final CGPA at graduation, so there may still be time."]
    elif label == "Cum-Laude":
        advice = ["You qualify for CUM LAUDE honours (CGPA 3.60 to below 3.80, clause 5.8.1).",
                  f"You are {3.80 - cgpa:.2f} CGPA away from Magna Cum Laude."]
    elif label == "Magna-Cum-Laude":
        advice = ["You qualify for MAGNA CUM LAUDE honours (CGPA 3.80 to below 3.90, clause 5.8.1).",
                  f"You are {3.90 - cgpa:.2f} CGPA away from Summa Cum Laude."]
    else:
        advice = ["You qualify for the top honour: SUMMA CUM LAUDE (CGPA 3.90 or above, clause 5.8.1)."]
    advice.append("Gold / Silver medals (5.7) depend on your rank in the batch, so this tool cannot decide them.")
    if rd >= 0.5:
        advice.append("If this is your SEMESTER CGPA, you are on the Rector's Honours List (5.9).")
    return _pack("M2", honours_system, res, dict(cgpa=cgpa, broken=broken), dict(violations=len(broken)),
                 decision, interp, advice, "5.6, 5.8.1, 5.9",
                 rector=rd, rector_yes=rd >= 0.5)


# ===========================================================================
# MODULE 3 evaluate
# ===========================================================================
def evaluate_scholarship(category, cgpa, load_pct=100):
    if category not in H.SCHOLARSHIPS:
        raise ValueError(f"Unknown scholarship {category!r}. Choose one of: {', '.join(H.SCHOLARSHIPS)}.")
    cgpa = _num(cgpa, "GPA/CGPA", 0.0, 4.0)
    info = H.SCHOLARSHIPS[category]
    load_used = 100.0
    if info["merit"]:                       # regular course load is demanded for MERIT scholarships only
        load_used = _num(load_pct, "Course load (%)", 0.0, 120.0)
    minimum = info["min_cgpa"]
    margin = round(cgpa - minimum, 4)
    res = scholarship_system.infer({"margin": margin, "load": load_used})
    label = res["label"]
    decision = "WITHHOLD" if label == "Suspended" else "RETAIN"
    interp = (f"Scholarship status = {label} (safety score {res['crisp']:.1f} / 100).  "
              f"GPA/CGPA {cgpa:.2f} is {abs(margin):.2f} {'above' if margin >= 0 else 'below'} the {minimum:.2f} minimum.")
    advice = {
        "Suspended": ["The scholarship is SUSPENDED / WITHHELD until your grades improve to the minimum for your category (4.11)."
                      if margin < 0 else
                      "Merit scholarships require the regular course load of the academic road map, so the scholarship cannot continue (4.4.3.5, 4.12(b)).",
                      "It can be restored once the requirement is met again (4.5.3(d), 4.9, 4.11)."],
        "At-Risk": ["You may KEEP the scholarship for now, but you are on the edge.",
                    "Scholarship holders are reviewed EVERY semester (4.11, 4.12(d)) - protect your GPA" +
                    (" and take the full regular course load (4.4.3.5)." if info["merit"] else ".")],
        "Continue": ["You meet the requirement with a healthy margin: the scholarship CONTINUES (4.5.3(d))."],
        "Secure": ["Your GPA/CGPA is well above the minimum: the scholarship is SECURE for the coming review (4.5.2)."],
    }[label]
    if not info["merit"]:
        advice.append("Course load is not checked for this need-based scholarship (only merit scholarships need it, 4.4.3.5).")
    if category.startswith("Qarz"):
        advice.append("Note: Qarz-e-Hasna was discontinued from Fall 2020; only existing awardees are served (4.8).")
    return _pack("M3", scholarship_system, res, dict(category=category, cgpa=cgpa, load=load_used if info["merit"] else None),
                 dict(minimum=minimum, margin=margin, load_used=load_used), decision, interp, advice,
                 info["clause"] + ", 4.11, 4.12")
