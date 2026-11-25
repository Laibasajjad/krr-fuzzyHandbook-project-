"""
handbook_data.py
================
Everything we learned from the Bahria University Student Handbook (Spring 2024 edition)
lives here, so that the report, the GUI and the tests all use ONE source of truth.

Each knowledge item has a Rule ID (R01..R24) and ONE UNIQUE COLOUR.  The same colour is used for
  * the highlight on the handbook page,
  * the row in the traceability table,
  * the rule in the rule base, and
  * the "rules fired" chip in the GUI.
"""
import colorsys

# ---------------------------------------------------------------------------
# 1. Handbook numbers (crisp facts) used by the systems
# ---------------------------------------------------------------------------
# Section 5.5.1 (page 71) - minimum CGPA below which a student goes on probation
PROGRAMMES = {
    "AD": 2.0,
    "BBA / BEE / BS": 2.0,
    "MBA / MS / MPhil": 2.5,
    "PhD": 3.0,
}

# Chapter 4 - minimum GPA/CGPA that must be kept to continue a scholarship
SCHOLARSHIPS = {
    "Advance Merit (Board Topper / Top Ranker / A-Levels)": dict(min_cgpa=3.50, merit=True,  rule="R14", clause="4.3.2.2, 4.3.3.1.2(b), 4.3.4.2"),
    "Merit - Batch Topper (non-engineering)":               dict(min_cgpa=3.75, merit=True,  rule="R15", clause="4.4.3.3"),
    "Merit - Batch Topper (engineering)":                   dict(min_cgpa=3.60, merit=True,  rule="R16", clause="4.4.3.3"),
    "Financial Assistance Scholarship (FAS)":               dict(min_cgpa=2.50, merit=False, rule="R17", clause="4.5.2, 4.5.3(d)"),
    "Qarz-e-Hasna (existing awardees only)":                dict(min_cgpa=2.75, merit=False, rule="R18", clause="4.9"),
}

# Section 5.6 (page 72) - the baseline conditions for any honour/award (5.6.3, the 3.60 CGPA rule,
# is handled separately as a fuzzy input).
BASELINE_CONDITIONS = [
    ("5.6.1", "I completed the programme within the regular programme duration"),
    ("5.6.2", "I took the full semester load every semester (no withdrawn / repeated course)"),
    ("5.6.4", "I have no incomplete credit hours"),
    ("5.6.5", "I have no migration / credit transfer / summer-semester course to my credit"),
    ("5.6.6", "I was never penalised in a disciplinary case"),
    ("5.6.7", "I submitted my final thesis / Final Year Project within the regular timeline"),
]

# ---------------------------------------------------------------------------
# 2. Colours - 24 hues, 15 degrees apart.  The assignment of hue -> rule was chosen by a
#    search that keeps rules printed on the SAME handbook page at least 45 degrees apart.
# ---------------------------------------------------------------------------
_HUES = [45, 0, 180, 225, 90, 270, 240, 15, 30, 105, 195, 300, 150, 60, 120, 165,
         135, 345, 210, 285, 315, 255, 330, 75]


def _hls(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return (r, g, b)


def rule_rgb(rid):
    """Strong colour (0..1 floats) used for highlights and chips."""
    return _hls(_HUES[int(rid[1:]) - 1], 0.66, 0.95)


def rule_hex(rid):
    r, g, b = rule_rgb(rid)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def rule_hex_light(rid, mix=0.55):
    """Same hue, lighter (for table backgrounds)."""
    r, g, b = rule_rgb(rid)
    r, g, b = [c + (1 - c) * mix for c in (r, g, b)]
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


# ---------------------------------------------------------------------------
# 3. The knowledge base: one record per rule
#    pages    = PRINTED handbook page numbers (the PDF file page = printed + 10)
#    passages = what to highlight: (printed page, first words, last words)
# ---------------------------------------------------------------------------
RULES = [
    # ------------------------- MODULE 1 : Probation & Drop (Chapter 5.5) -------------------------
    dict(id="R01", module="M1", kind="Crisp lookup", section="5.5.1", pages=[71],
         text="Program / Minimum GPA:  AD 2.0;  BBA/BEE/BS 2.0;  MBA/MS/MPhil 2.5;  PhD 3.0",
         rule="IF Programme is AD or BBA/BEE/BS THEN Required-Minimum = 2.0;  IF MBA/MS/MPhil THEN 2.5;  IF PhD THEN 3.0   (then Margin = CGPA - Required-Minimum)",
         passages=[(71, "Program Minimum GPA", "PhD 3.0")]),
    dict(id="R02", module="M1", kind="Direct fuzzy", section="5.5.1", pages=[71],
         text="5.5.1 In any semester, a student shall be placed on Probation for failing to achieve the minimum CGPA (GPA if it is the first semester) stipulated for the programme, as follows:",
         rule="IF Margin is Low AND Previous-Probations is None THEN Standing is First-Probation",
         passages=[(71, "In any semester,", "as follows")]),
    dict(id="R03", module="M1", kind="Direct fuzzy", section="5.5.5", pages=[71, 72],
         text="5.5.5 The student placed on 2nd consecutive Probation must not register for a new course/ new semester without the prior approval of the concerned Principal, through the respective HOD.",
         rule="IF Margin is Low AND Previous-Probations is One THEN Standing is Second-Probation",
         passages=[(71, "The student placed on 2nd consecutive Probation must not", "must not"),
                   (72, "register for a new course/", "respective HOD")]),
    dict(id="R04", module="M1", kind="Direct fuzzy", section="5.5.3", pages=[71],
         text="5.5.3 The student shall be Dropped from the academic programme upon failure to attain the minimum CGPA in the immediate semester after two consecutive Probations.",
         rule="IF Margin is Low AND Previous-Probations is Two THEN Standing is Dropped",
         passages=[(71, "The student shall be Dropped", "consecutive Probations")]),
    dict(id="R05", module="M1", kind="Direct fuzzy", section="5.5.4", pages=[71],
         text="5.5.4 ... shall be taken out of the Probation regime and his/ her Probation count reset to 'Zero' for the leftover semesters till the programme completion.",
         rule="IF Margin is Safe THEN Standing is Safe   (probation count is reset to zero)",
         passages=[(71, "shall be taken out of the Probation regime", "reset to Zero")]),
    dict(id="R06", module="M1", kind="Fuzzy extension", section="5.5.4", pages=[71],
         text="5.5.4 A student on probation who improves his/ her CGPA (including Summer session) equal to or higher than the minimum CGPA ... shall be taken out of the Probation regime",
         rule="IF Margin is Borderline (just at or a little above the limit) THEN Standing is Watch   (early warning)",
         passages=[(71, "equal to or higher than the minimum CGPA", "minimum CGPA")]),

    # ------------------------- MODULE 2 : Honours (Chapter 5.6 - 5.9) -------------------------
    dict(id="R07", module="M2", kind="Direct fuzzy", section="5.6, 5.6.1, 5.6.2, 5.6.4-5.6.7", pages=[72],
         text="5.6 A student shall be eligible for an Academic Honour/ Award if he/she: 5.6.1 Has completed the program within the Regular program duration ... 5.6.2 Has taken full semester load ... without having withdrawn or repeated any course ... 5.6.4 Does not have any incomplete credit hours. 5.6.5 Does not have any Migration/ Credit Transfer ... or Summer Semester Course ... 5.6.6 Has never been penalized in any disciplinary case ... 5.6.7 Has not submitted the finalized Thesis/ Final Year Project beyond the regular timeline ...",
         rule="IF Baseline-Violations is Some THEN Honour is Not-Eligible",
         passages=[(72, "A student shall be eligible", "if he/she"),
                   (72, "5.6.1 Has completed", "5.12.9"),
                   (72, "5.6.2 Has taken full semester load", "for any semester"),
                   (72, "5.6.4 Does not have any incomplete", "credit hours"),
                   (72, "5.6.5 Does not have any Migration/", "to his her credit"),
                   (72, "5.6.6 Has never been penalized", "at the University"),
                   (72, "5.6.7 Has not submitted", "5.7.1.5")]),
    dict(id="R08", module="M2", kind="Direct fuzzy", section="5.6.3", pages=[72],
         text="5.6.3 Has scored a minimum 3.60 CGPA.",
         rule="IF CGPA is Low THEN Honour is Not-Eligible",
         passages=[(72, "5.6.3 Has scored", "3.60 CGPA")]),
    dict(id="R09", module="M2", kind="Fuzzy extension", section="5.8.1", pages=[73],
         text="5.8.1 ... graduates scoring a minimum of 3.6 CGPA upon completion of respective program shall be awarded Cum Laude Honours as per following categories:",
         rule="IF CGPA is Near-Miss (just under 3.60) AND Baseline-Violations is None THEN Honour is Near-Miss   (still NOT eligible; advice only)",
         passages=[(73, "graduates scoring a minimum of 3.6 CGPA", "following categories")]),
    dict(id="R10", module="M2", kind="Direct fuzzy", section="5.8.1", pages=[73],
         text="Cum Laude: >= 3.60 to < 3.80",
         rule="IF CGPA is Cum-Laude-Band AND Baseline-Violations is None THEN Honour is Cum-Laude",
         passages=[(73, "Cum Laude ≥ 3.60", "<3.80")]),
    dict(id="R11", module="M2", kind="Direct fuzzy", section="5.8.1", pages=[73],
         text="Magna Cum Laude: >= 3.80 to < 3.90",
         rule="IF CGPA is Magna-Band AND Baseline-Violations is None THEN Honour is Magna-Cum-Laude",
         passages=[(73, "Magna Cum Laude ≥ 3.80", "<3.90")]),
    dict(id="R12", module="M2", kind="Direct fuzzy", section="5.8.1", pages=[73],
         text="Summa Cum Laude: >= 3.90",
         rule="IF CGPA is Summa-Band AND Baseline-Violations is None THEN Honour is Summa-Cum-Laude",
         passages=[(73, "Summa Cum Laude ≥ 3.90", "3.90")]),
    dict(id="R13", module="M2", kind="Direct fuzzy", section="5.9", pages=[73],
         text="5.9 In every semester, students achieving CGPA 3.90 or above will be included in the Rector's Honours List for the corresponding semester,",
         rule="IF Semester-CGPA is Summa-Band THEN Rector's-Honours-List is Yes   (degree = firing strength)",
         passages=[(73, "In every semester, students", "for the corresponding semester")]),

    # ------------------------- MODULE 3 : Scholarship continuation (Chapter 4) -------------------------
    dict(id="R14", module="M3", kind="Crisp lookup", section="4.3.2.2, 4.3.3.1.2(b), 4.3.4.2", pages=[50, 51],
         text="4.3.2.2 ... its continuation during the subsequent semesters will be subject to the condition that awardee must maintain his/her minimum GPA/CGPA of 3.50.  4.3.3.1.2(b) For continuation of the scholarship in the subsequent semesters for the above categories the students will be required to achieve a GPA/CGPA of at least 3.50.  4.3.4.2 For continuation of scholarship in the subsequent semesters the students will be required to achieve a GPA/CGPA of at least 3.50.",
         rule="IF Scholarship is Advance-Merit THEN Required-Minimum = 3.50",
         passages=[(50, "However, its continuation", "GPA/CGPA of 3.50"),
                   (50, "For continuation of the scholarship in the", "scholarship in the"),
                   (51, "subsequent semesters for the above categories", "of at least 3.50"),
                   (51, "For continuation of scholarship in the subsequent", "of at least 3.50")]),
    dict(id="R15", module="M3", kind="Crisp lookup", section="4.4.3.3", pages=[52],
         text="4.4.3.3 The students must achieve minimum GPA >= 3.75 in order to qualify for the award of Merit Scholarship for non-engineering programs ...",
         rule="IF Scholarship is Batch-Topper-Merit AND Programme is non-engineering THEN Required-Minimum = 3.75",
         passages=[(52, "4.4.3.3 The students must achieve minimum GPA", "non-engineering programs")]),
    dict(id="R16", module="M3", kind="Crisp lookup", section="4.4.3.3", pages=[52],
         text="... & in case of engineering programs, student has to achieve minimum GPA >= 3.60 as per detail mentioned above (4.4.1 & 4.4.2).",
         rule="IF Scholarship is Batch-Topper-Merit AND Programme is engineering THEN Required-Minimum = 3.60",
         passages=[(52, "& in case of engineering", "(4.4.1 & 4.4.2)")]),
    dict(id="R17", module="M3", kind="Crisp lookup", section="4.5.2", pages=[53],
         text="4.5.2 ... provided their performance shall not fall below GPA/CGPA 2.50.",
         rule="IF Scholarship is Financial-Assistance (FAS) THEN Required-Minimum = 2.50",
         passages=[(53, "provided their performance shall not", "GPA/CGPA2.50")]),
    dict(id="R18", module="M3", kind="Crisp lookup", section="4.9", pages=[55],
         text="4.9 Qarz e Hasna shall be continued as long as the beneficiary students maintain at least 2.75 GPA/CGPA, failing which it shall be withheld till the time GPA/CGPA is improved back to 2.75.",
         rule="IF Scholarship is Qarz-e-Hasna THEN Required-Minimum = 2.75",
         passages=[(55, "Qarz e Hasna shall be continued", "back to 2.75")]),
    dict(id="R19", module="M3", kind="Direct fuzzy", section="4.11", pages=[55],
         text="4.11 ... Those scholarship holders fail to maintain the required GPA/CGPA shall be suspended till the time their grades improve to minimum eligibility criteria as per their respective category.",
         rule="IF Margin is Below THEN Scholarship is Suspended",
         passages=[(55, "Those scholarship holders fail", "respective category")]),
    dict(id="R20", module="M3", kind="Fuzzy extension", section="4.11", pages=[55],
         text="4.11 The Central Scholarship Committee will formally review cases of all scholarship holders every semester for monitoring academic progress as per scholarship policy.",
         rule="IF Margin is At-Limit AND Course-Load is Not-Reduced THEN Scholarship is At-Risk   (reviewed every semester, so a tiny margin is dangerous)",
         passages=[(55, "The Central Scholarship Committee will formally review", "as per scholarship policy")]),
    dict(id="R21", module="M3", kind="Direct fuzzy", section="4.5.3(d)", pages=[53],
         text="4.5.3(d) ... and for continuation at least 2.50 GPA/CGPA has to be maintained in the subsequent semesters.",
         rule="IF Margin is Comfortable AND Course-Load is Regular THEN Scholarship is Continue",
         passages=[(53, "and for continuation at least 2.50", "subsequent semesters")]),
    dict(id="R22", module="M3", kind="Direct fuzzy", section="4.5.2", pages=[53],
         text="4.5.2 The scholarship once granted in this category remains available to the students for the entire degree program ...",
         rule="IF Margin is Strong AND Course-Load is Regular THEN Scholarship is Secure",
         passages=[(53, "The scholarship once granted", "entire degree program")]),
    dict(id="R23", module="M3", kind="Direct fuzzy", section="4.4.3.5", pages=[52],
         text="4.4.3.5 The students have to follow the academic road map with regular course load for all type of Merit Based Scholarships.",
         rule="IF Course-Load is Reduced THEN Scholarship is Suspended   (merit scholarships only)",
         passages=[(52, "4.4.3.5 The students have to follow", "Merit Based Scholarships")]),
    dict(id="R24", module="M3", kind="Fuzzy extension", section="4.12(b)", pages=[55],
         text="4.12(b) The students have to follow the academic road map with regular course load for all type of Merit Based Scholarships.",
         rule="IF Course-Load is Slightly-Reduced AND Margin Meets the limit THEN Scholarship is At-Risk   (merit scholarships only)",
         passages=[(55, "The students have to follow the academic road map", "Merit Based Scholarships")]),
]

RULE_BY_ID = {r["id"]: r for r in RULES}

MODULES = {
    "M1": "Module 1 - Probation & Drop (Chapter 5, 5.5)",
    "M2": "Module 2 - Honours & Awards (Chapter 5, 5.6 - 5.9)",
    "M3": "Module 3 - Scholarship Continuation (Chapter 4)",
}
