"""
app.py - Graphical user interface (Streamlit)  -  glass / coral theme
=====================================================================
Run with:   streamlit run app.py
(keep the folder  .streamlit/config.toml  next to this file - it switches Streamlit to the dark base theme)

Layout = a stack of full-width "glass cards".  Each card shows ONE complete piece of information:
   Card 1  RESULT          crisp output | linguistic answer | decision code | interpretation | advice
   Card 2  RULES FIRED     rule chip (handbook colour) | IF-THEN text | firing strength
   Card 3  CALCULATION     output shape + centroid  |  fuzzification of the inputs
   Tabs    membership functions, output surface, rule base, handbook source pages
"""
import base64, html, io, os
import matplotlib.pyplot as plt
import streamlit as st
import handbook_data as H
import systems as S
import plots as P

st.set_page_config(page_title="BU Handbook Fuzzy Advisor", page_icon="🎓", layout="wide")
BASE = os.path.dirname(os.path.abspath(__file__))

MODULE_NAMES = {"M1": "Probation & Drop", "M2": "Honours & Awards", "M3": "Scholarship Continuation"}
MODULE_MENU = {"M1": "1 · Probation & Drop (Ch. 5.5)", "M2": "2 · Honours & Awards (Ch. 5.6-5.9)", "M3": "3 · Scholarship Continuation (Ch. 4)"}
MODULE_INFO = {
    "M1": ("Chapter 5, §5.5 · pages 71-72", "CGPA margin above the programme minimum + probations already served", "Safe · Watch · 1st Probation · 2nd Probation · Dropped"),
    "M2": ("Chapter 5, §5.6-5.9 · pages 72-73", "CGPA + the six baseline conditions", "Not eligible · Near-miss · Cum Laude · Magna · Summa"),
    "M3": ("Chapter 4 · pages 50-55", "GPA/CGPA margin above the scholarship minimum + course load", "Suspended · At-risk · Continue · Secure"),
}
HB_PAGES = {"M1": [71, 72], "M2": [72, 73], "M3": [50, 51, 52, 53, 55]}
GOOD, MID, WARN, BAD = "#7BE0A4", "#FFCBA4", "#FFC857", "#FF6B6B"
LABEL_COLOURS = {"Safe": GOOD, "Watch": WARN, "First-Probation": BAD, "Second-Probation": BAD, "Dropped": BAD,
                 "Not-Eligible": BAD, "Near-Miss": WARN, "Cum-Laude": MID, "Magna-Cum-Laude": MID, "Summa-Cum-Laude": GOOD,
                 "Suspended": BAD, "At-Risk": WARN, "Continue": MID, "Secure": GOOD}

EXAMPLES = {
    "M1": {"BS student, CGPA 1.85, no earlier probation": dict(programme="BBA / BEE / BS", cgpa="1.85", prob=0),
           "BS student exactly at 2.00": dict(programme="BBA / BEE / BS", cgpa="2.00", prob=0),
           "BS student 1.70 after one probation": dict(programme="BBA / BEE / BS", cgpa="1.70", prob=1),
           "MS student 2.40": dict(programme="MBA / MS / MPhil", cgpa="2.40", prob=0)},
    "M2": {"CGPA 3.85, clean record": dict(cgpa="3.85", broken=[]),
           "CGPA 3.95 but a disciplinary penalty": dict(cgpa="3.95", broken=["5.6.6"]),
           "CGPA 3.59 (one hundredth short)": dict(cgpa="3.59", broken=[])},
    "M3": {"FAS holder with CGPA 2.55": dict(cat="Financial Assistance Scholarship (FAS)", cgpa="2.55", load="100"),
           "Merit scholar 3.90 but only 60% load": dict(cat="Merit - Batch Topper (non-engineering)", cgpa="3.90", load="60"),
           "Advance Merit exactly 3.50": dict(cat="Advance Merit (Board Topper / Top Ranker / A-Levels)", cgpa="3.50", load="100")},
}

# ----------------------------------------------------------------------------- style
CSS = """
<style>
:root{--accent:#FF8A75;--accent2:#E8638F;--glass:rgba(255,255,255,.055);--glass-b:rgba(255,255,255,.13);--ink:#F3EDEA;--mute:#B9AEB0;}
.stApp{background:radial-gradient(1100px 520px at 88% -8%,rgba(255,122,89,.24),transparent 60%),
 radial-gradient(900px 520px at -8% 108%,rgba(190,70,130,.20),transparent 60%),linear-gradient(180deg,#14111a,#0c0b10);color:var(--ink);}
header[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1180px;padding-top:2.4rem;padding-bottom:4rem;}
[data-testid="stSidebar"]{background:rgba(255,255,255,.04);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-right:1px solid var(--glass-b);}
[data-testid="stSidebar"] .block-container{padding-top:1.4rem;}
[data-baseweb="input"],[data-baseweb="select"]>div{background:rgba(255,255,255,.06)!important;border:1px solid var(--glass-b)!important;border-radius:12px!important;}
.stButton>button{width:100%;border-radius:12px;border:1px solid var(--glass-b);background:rgba(255,255,255,.06);color:var(--ink);}
.stButton>button:hover{border-color:var(--accent);color:var(--accent);}
.stButton>button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:linear-gradient(135deg,#FF8A75,#E8638F);border:none;color:#1a0f12;font-weight:700;}
.stTabs [data-baseweb="tab-list"]{gap:8px;border-bottom:none;}
.stTabs [data-baseweb="tab"]{background:rgba(255,255,255,.05);border:1px solid var(--glass-b);border-radius:12px;padding:8px 18px;height:auto;}
.stTabs [aria-selected="true"]{background:rgba(255,138,117,.18);border-color:var(--accent);color:var(--accent);}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}
.card{background:var(--glass);border:1px solid var(--glass-b);border-radius:20px;padding:22px 26px;margin:0 0 20px;
 backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 10px 40px rgba(0,0,0,.35);}
.card.err{border-color:rgba(255,107,107,.6);background:rgba(255,107,107,.09);}
.card h3{margin:0 0 14px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);font-weight:700;}
.hero h1{margin:0;font-size:2.1rem;font-weight:800;letter-spacing:-.01em;}
.hero p{margin:6px 0 0;color:var(--mute);}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;}
.pill{padding:5px 12px;border-radius:999px;background:rgba(255,255,255,.07);border:1px solid var(--glass-b);font-size:.78rem;color:var(--ink);}
.pill b{color:var(--accent);}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;}
.stat{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:16px;padding:16px 18px;min-height:132px;display:flex;flex-direction:column;justify-content:space-between;}
.stat .k{font-size:.7rem;color:var(--mute);text-transform:uppercase;letter-spacing:.12em;}
.stat .v{font-size:2.5rem;font-weight:800;line-height:1.15;}
.stat .v.code{font-size:1.35rem;font-family:ui-monospace,Consolas,monospace;letter-spacing:.02em;}
.gauge{height:8px;border-radius:6px;background:rgba(255,255,255,.1);overflow:hidden;}
.gauge i{display:block;height:100%;background:linear-gradient(90deg,#FFB199,#FF8A75,#E8638F);}
.interp{margin:18px 0 6px;font-size:1rem;}
.sub{margin:14px 0 6px;font-size:.72rem;color:var(--mute);text-transform:uppercase;letter-spacing:.12em;}
.adv{list-style:none;padding:0;margin:8px 0 0;}
.adv li{padding:10px 14px 10px 38px;position:relative;margin-bottom:8px;border-radius:12px;background:rgba(255,138,117,.08);border:1px solid rgba(255,138,117,.22);}
.adv li:before{content:"\\2726";position:absolute;left:14px;color:var(--accent);}
.rule{display:grid;grid-template-columns:70px 1fr 220px;gap:18px;align-items:center;padding:13px 2px;border-bottom:1px solid rgba(255,255,255,.08);}
.rule.nostr{grid-template-columns:70px 1fr;}
.rule:last-child{border-bottom:none;}
.chip{text-align:center;font-weight:800;border-radius:10px;padding:7px 0;color:#15121a;}
.rule .t{font-size:.95rem;} .rule .s{font-size:.76rem;color:var(--mute);margin-top:3px;}
.bar{height:10px;border-radius:6px;background:rgba(255,255,255,.1);overflow:hidden;}
.bar i{display:block;height:100%;border-radius:6px;}
.rule .n{font-size:.76rem;color:var(--mute);margin-top:5px;text-align:right;}
.grid2{display:grid;grid-template-columns:1.3fr 1fr;gap:24px;align-items:stretch;}
.grid2 img{width:100%;display:block;}
.fzh{font-size:.72rem;color:var(--accent);text-transform:uppercase;letter-spacing:.12em;margin:10px 0 4px;}
.fz{display:grid;grid-template-columns:128px 1fr 40px;gap:10px;align-items:center;margin:7px 0;}
.fz .l{font-size:.82rem;color:var(--mute);} .fz .v{font-size:.8rem;text-align:right;}
.fz .bar i{background:linear-gradient(90deg,#FFB199,#FF8A75);}
.mod{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:16px;padding:16px 18px;}
.mod b{font-size:1.05rem;} .mod div{font-size:.82rem;color:var(--mute);margin-top:6px;}
.imgcard img{width:100%;display:block;}
@media (max-width:900px){.grid3,.grid2{grid-template-columns:1fr;} .rule{grid-template-columns:60px 1fr;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def flat(s):
    """Collapse an HTML string to one line (markdown would treat blank lines / indents as code)."""
    return " ".join(line.strip() for line in s.strip().splitlines())


def show(s):
    st.markdown(flat(s), unsafe_allow_html=True)


def fig_b64(fig, dpi=140):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


@st.cache_data(show_spinner=False)
def mf_png(module):
    with plt.rc_context(P.DARK_RC):
        return fig_b64(P.mf_figure(module))


@st.cache_data(show_spinner=False)
def surface_png(module):
    with plt.rc_context(P.DARK_RC):
        return fig_b64(P.surface_figure(module))


def esc(x):
    return html.escape(str(x), quote=True)


def rule_rows(items, strength=False, original=False):
    """items = list of dicts(rid, text, strength?) -> aligned grid rows."""
    out = []
    for f in items:
        r = H.RULE_BY_ID[f["rid"]]
        col = H.rule_hex(f["rid"])
        text = " ".join(f["text"].split())
        sub = f"handbook §{esc(r['section'])} · page {', '.join(map(str, r['pages']))} · {esc(r['kind'])}"
        if original:
            sub = f"<i>“{esc(r['text'])}”</i><br/>" + sub
        right = ""
        if strength:
            right = (f"<div><div class='bar'><i style='width:{f['strength']*100:.0f}%;background:{col}'></i></div>"
                     f"<div class='n'>firing strength {f['strength']:.2f}</div></div>")
        out.append(f"<div class='rule {'' if strength else 'nostr'}'><div class='chip' style='background:{col}'>{f['rid']}</div>"
                   f"<div><div class='t'>{esc(text)}</div><div class='s'>{sub}</div></div>{right}</div>")
    return "".join(out)


# ----------------------------------------------------------------------------- sidebar
st.sidebar.markdown("## 🎓 BU Handbook<br/>Fuzzy Advisor", unsafe_allow_html=True)
st.sidebar.caption("Knowledge Representation & Reasoning · Assignment 2")
module = st.sidebar.radio("Choose a service", list(MODULE_MENU), format_func=MODULE_MENU.get)
st.sidebar.divider()
ss = st.session_state
ss.setdefault("M1_programme", "BBA / BEE / BS"); ss.setdefault("M1_cgpa", "2.50"); ss.setdefault("M1_prob", 0)
ss.setdefault("M2_cgpa", "3.70"); ss.setdefault("M3_cat", list(H.SCHOLARSHIPS)[0]); ss.setdefault("M3_cgpa", "3.20"); ss.setdefault("M3_load", "100")
for _c, _t in H.BASELINE_CONDITIONS:
    ss.setdefault(f"M2_chk_{_c}", True)


def load_example(m):
    ex = EXAMPLES[m][ss[f"ex_{m}"]]
    for k, v in ex.items():
        if k == "broken":
            for clause, _ in H.BASELINE_CONDITIONS:
                ss[f"M2_chk_{clause}"] = clause not in v
        else:
            ss[f"{m}_{k}"] = v


if module == "M1":
    prog = st.sidebar.selectbox("Programme", list(H.PROGRAMMES), key="M1_programme")
    st.sidebar.caption(f"Minimum CGPA for this programme: **{H.PROGRAMMES[prog]:.1f}** (handbook 5.5.1)")
    cgpa = st.sidebar.text_input("Your CGPA (GPA if first semester)", key="M1_cgpa", help="0.00 - 4.00, use a dot")
    prob = st.sidebar.radio("Consecutive probations already served", [0, 1, 2], horizontal=True, key="M1_prob",
                            help="0 = none (or cleared); 1 = you were on probation last time; 2 = two in a row")
    args, run = dict(programme=prog, cgpa=cgpa, probations=prob), S.evaluate_standing
elif module == "M2":
    cgpa = st.sidebar.text_input("Your CGPA", key="M2_cgpa", help="Final CGPA for honours; semester CGPA for the Rector's list")
    st.sidebar.markdown("**Tick every statement that is TRUE for you** (handbook 5.6):")
    broken = [c for c, t in H.BASELINE_CONDITIONS if not st.sidebar.checkbox(f"{c}: {t}", key=f"M2_chk_{c}")]
    args, run = dict(cgpa=cgpa, broken_conditions=broken), S.evaluate_honours
else:
    cat = st.sidebar.selectbox("Scholarship type", list(H.SCHOLARSHIPS), key="M3_cat")
    info = H.SCHOLARSHIPS[cat]
    st.sidebar.caption(f"Minimum GPA/CGPA to keep it: **{info['min_cgpa']:.2f}** (handbook {info['clause']})")
    cgpa = st.sidebar.text_input("Your GPA / CGPA", key="M3_cgpa")
    if info["merit"]:
        load = st.sidebar.text_input("Course load (% of the regular load)", key="M3_load", help="100 = the regular load of your academic road map")
    else:
        load = "100"
        st.sidebar.caption("Course load is not checked for need-based scholarships.")
    args, run = dict(category=cat, cgpa=cgpa, load_pct=load), S.evaluate_scholarship

st.sidebar.divider()
st.sidebar.selectbox("Example cases", list(EXAMPLES[module]), key=f"ex_{module}")
st.sidebar.button("Load example", on_click=load_example, args=(module,))
go = st.sidebar.button("▶  EVALUATE", type="primary")

# ----------------------------------------------------------------------------- main
if go:
    try:
        ss["last"], ss["err"] = run(**args), None
    except ValueError as e:
        ss["last"], ss["err"] = None, str(e)
    ss["last_module"] = module

show(f"""<div class='card hero'><h1>{MODULE_NAMES[module]}</h1>
<p>Fuzzy answers from the Bahria University Student Handbook · {MODULE_INFO[module][0]}</p>
<div class='pills'><span class='pill'><b>Method</b> Mamdani</span><span class='pill'><b>Defuzzification</b> centroid</span>
<span class='pill'><b>Rules</b> {len([r for r in H.RULES if r['module']==module])} in this module</span></div></div>""")

has_result = ss.get("last_module") == module and (ss.get("last") or ss.get("err"))
if not has_result:
    mods = "".join(f"<div class='mod'><b>{MODULE_NAMES[m]}</b><div>{MODULE_INFO[m][0]}</div><div><b style='font-size:.8rem;color:#FF8A75'>IN</b> {MODULE_INFO[m][1]}</div>"
                   f"<div><b style='font-size:.8rem;color:#FF8A75'>OUT</b> {MODULE_INFO[m][2]}</div></div>" for m in MODULE_NAMES)
    show(f"""<div class='card'><h3>How to use</h3>
<div class='interp'>1 · Pick a service on the left &nbsp; 2 · Enter your values &nbsp; 3 · Press <b>EVALUATE</b></div>
<div class='grid3' style='margin-top:16px'>{mods}</div>
<div class='sub'>Study project - always confirm important decisions with your HOD or the Examinations office.</div></div>""")
elif ss.get("err"):
    show(f"<div class='card err'><h3 style='color:#FF6B6B'>Please check your input</h3><div class='interp'>⚠️ {esc(ss['err'])}</div></div>")
else:
    res = ss["last"]
    colour = LABEL_COLOURS.get(res["label"], "#F3EDEA")
    i, d = res["inputs"], res["derived"]
    pills = []
    if res["module"] == "M1":
        pills = [("Programme", i["programme"]), ("CGPA", f"{i['cgpa']:.2f}"), ("Earlier probations", i["probations"]), ("Limit", f"{d['minimum']:.1f}"), ("Margin", f"{d['margin']:+.2f}")]
    elif res["module"] == "M2":
        pills = [("CGPA", f"{i['cgpa']:.2f}"), ("Broken conditions", ", ".join(i["broken"]) or "none")]
    else:
        pills = [("Scholarship", i["category"]), ("GPA/CGPA", f"{i['cgpa']:.2f}"), ("Limit", f"{d['minimum']:.2f}"), ("Margin", f"{d['margin']:+.2f}")]
        if i["load"] is not None:
            pills.append(("Load", f"{i['load']:.0f}%"))
    pills_html = "".join(f"<span class='pill'><b>{esc(k)}</b> {esc(v)}</span>" for k, v in pills)
    adv = "".join(f"<li>{esc(a)}</li>" for a in res["advice"])
    extra = "<li>🏅 Rector's Honours List (5.9) - applies if this is your semester CGPA.</li>" if res["module"] == "M2" and res.get("rector_yes") else ""

    # ---- Card 1 : result
    show(f"""<div class='card'><h3>1 · Result</h3>
<div class='pills' style='margin:0 0 16px'>{pills_html}</div>
<div class='grid3'>
 <div class='stat'><div class='k'>Crisp output (0-100)</div><div class='v'>{res['crisp']:.1f}</div><div class='gauge'><i style='width:{min(max(res['crisp'],0),100):.0f}%'></i></div></div>
 <div class='stat'><div class='k'>Linguistic answer</div><div class='v' style='color:{colour};font-size:1.9rem'>{esc(res['label'])}</div><div class='k' style='text-transform:none;letter-spacing:0'>highest membership at the crisp score</div></div>
 <div class='stat'><div class='k'>Decision code</div><div class='v code'>{esc(res['decision'])}</div><div class='k' style='text-transform:none;letter-spacing:0'>used by the test-suite</div></div>
</div>
<div class='interp'>{esc(res['interpretation'])}</div>
<div class='sub'>What the handbook says</div><ul class='adv'>{adv}{extra}</ul></div>""")

    # ---- Card 2 : rules fired
    show(f"<div class='card'><h3>2 · Rules fired ({len(res['fired'])})</h3>{rule_rows(res['fired'], strength=True)}</div>")

    # ---- Card 3 : calculation
    with plt.rc_context(P.DARK_RC):
        shape = fig_b64(P.output_shape_figure(res), 130)
    fz = ""
    for vname, var in res["system"].inputs.items():
        fz += f"<div class='fzh'>{esc(vname)}</div>"
        for t in var.terms:
            if t in ("Meets", "Not-Reduced"):
                continue
            v = res["fuzzified"][vname][t]
            fz += f"<div class='fz'><div class='l'>{esc(t)}</div><div class='bar'><i style='width:{v*100:.0f}%'></i></div><div class='v'>{v:.2f}</div></div>"
    show(f"""<div class='card'><h3>3 · How the answer was calculated</h3><div class='grid2'>
<div><div class='sub' style='margin-top:0'>Combined rule shapes and centroid</div><img src='data:image/png;base64,{shape}'/></div>
<div><div class='sub' style='margin-top:0'>Fuzzification - how much each term applies</div>{fz}</div></div></div>""")

    # ---- Tabs
    t1, t2, t3, t4 = st.tabs(["Membership functions", "Output surface", "Rule base", "Handbook source"])
    with t1:
        show(f"<div class='card imgcard'><h3>Membership functions</h3><img src='data:image/png;base64,{mf_png(res['module'])}'/></div>")
    with t2:
        show(f"<div class='card imgcard'><h3>Output surface</h3><img src='data:image/png;base64,{surface_png(res['module'])}' style='max-width:760px;margin:auto'/></div>")
    with t3:
        rows = [dict(rid=r["id"], text=r["rule"]) for r in H.RULES if r["module"] == res["module"]]
        show(f"<div class='card'><h3>Rule base of this module</h3>{rule_rows(rows, original=True)}</div>")
    with t4:
        st.caption("Handbook pages with the colour-coded highlights (same colours as the rule chips).")
        for pg in HB_PAGES[res["module"]]:
            p = os.path.join(BASE, "outputs", "handbook_pages", f"page_{pg}.png")
            if os.path.exists(p):
                st.image(p, caption=f"Handbook page {pg}")
            else:
                st.info(f"Run  python annotate_handbook.py BU_handbook.pdf  to create page {pg}.")
