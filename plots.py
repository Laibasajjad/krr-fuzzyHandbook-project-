"""
plots.py - all figures used by the GUI and by the report.
"""
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import handbook_data as H
import systems as S

TERM_COLOURS = ["#4C78A8", "#F58518", "#54A24B", "#E45756", "#B279A2", "#72B7B2"]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 10, "figure.dpi": 110})


ACCENT = "#FF8A75"          # coral accent used by the GUI
DARK_RC = {"figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
           "text.color": "#EDE7E3", "axes.labelcolor": "#EDE7E3", "axes.edgecolor": "#8D8590", "axes.titlecolor": "#FFFFFF",
           "xtick.color": "#CFC6C2", "ytick.color": "#CFC6C2", "grid.color": "#FFFFFF22",
           "legend.facecolor": "#1B1820", "legend.edgecolor": "#55505A", "legend.labelcolor": "#EDE7E3",
           "axes3d.xaxis.panecolor": (1, 1, 1, 0.04), "axes3d.yaxis.panecolor": (1, 1, 1, 0.04), "axes3d.zaxis.panecolor": (1, 1, 1, 0.04)}


def _ink():
    """Foreground colour of the current style (black normally, light in the dark GUI style)."""
    return plt.rcParams["text.color"]


def _term_colour(var, term):
    return TERM_COLOURS[list(var.terms).index(term) % len(TERM_COLOURS)]


# ---------------------------------------------------------------------------
# 1. Membership-function plots
# ---------------------------------------------------------------------------
def _draw_var(ax, var, xlim=None, marker=None, helper_skip=("Meets", "Not-Reduced"), direct=True):
    lo_x, hi_x = (xlim if xlim else (var.lo, var.hi))
    for t in var.terms:
        if t in helper_skip:
            ax.plot(var.universe, var.mf(t), ls=":", lw=1.2, color="#888888", label=f"{t} (helper)")
            continue
        c = _term_colour(var, t)
        y = var.mf(t)
        ax.fill_between(var.universe, y, alpha=0.15, color=c)
        ax.plot(var.universe, y, lw=2, color=c, label=t)
        if direct:                                   # write the term name above its plateau
            top = var.universe[y >= y.max() - 1e-9]
            top = top[(top >= lo_x) & (top <= hi_x)]
            if len(top):
                k = list(var.terms).index(t)
                ax.text(float(np.mean(top)), 1.05 + 0.10 * (k % 2), t, ha="center", fontsize=7.6, color=c, fontweight="bold")
    if marker is not None:
        ax.axvline(marker, color=_ink(), ls="--", lw=1.2)
    ax.set_ylim(-0.03, 1.27 if direct else 1.12)
    if any(t in helper_skip for t in var.terms) and direct:
        ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(0.0, 0.5), frameon=True)
    if xlim:
        ax.set_xlim(*xlim)
    else:
        ax.set_xlim(var.lo, var.hi)
    ax.set_ylabel("membership")
    ax.grid(alpha=0.25)


def mf_figure(module):
    """Membership functions of one module: input 1 (full + zoom), input 2, output."""
    sysm = S.SYSTEMS[module]
    ins = list(sysm.inputs.values())
    out = sysm.output
    fig = plt.figure(figsize=(9.2, 8.6))
    gs = fig.add_gridspec(3, 2, hspace=0.55, wspace=0.18)
    zoom = {"M1": (-0.3, 1.0), "M2": (3.25, 4.0), "M3": (-0.2, 0.9)}[module]
    # input 1
    ax = fig.add_subplot(gs[0, 0]); _draw_var(ax, ins[0], direct=False)
    ax.set_title(f"Input 1: {ins[0].name}  (full universe)", pad=10); ax.set_xlabel(ins[0].unit)
    ax.legend(fontsize=7, loc="center left", ncol=1)
    ax = fig.add_subplot(gs[0, 1]); _draw_var(ax, ins[0], xlim=zoom)
    ax.set_title("zoom near the handbook limits", pad=10); ax.set_xlabel(ins[0].unit); ax.set_ylabel("")
    if module in ("M1", "M3"):
        ax.axvline(0, color=_ink(), ls="--", lw=1); ax.text(0.015, 0.55, "handbook\nlimit (0)", fontsize=7, transform=ax.get_xaxis_transform())
    # input 2
    ax = fig.add_subplot(gs[1, :]); _draw_var(ax, ins[1])
    ax.set_title(f"Input 2: {ins[1].name}", pad=10); ax.set_xlabel(ins[1].unit)
    # output
    ax = fig.add_subplot(gs[2, :]); _draw_var(ax, out)
    ax.set_title(f"Output: {out.name}", pad=10); ax.set_xlabel(out.unit)
    fig.suptitle(S.SYSTEMS[module].name + " - membership functions", fontweight="bold", y=0.995)
    return fig


# ---------------------------------------------------------------------------
# 2. The result panel (what the GUI shows after "Evaluate")
# ---------------------------------------------------------------------------
def _wrap(text, w):
    return "\n".join(textwrap.wrap(text, w)) if text else ""


def result_panel(res, title=None):
    sysm = res["system"]
    out = sysm.output
    raw = res["raw"]
    fig = plt.figure(figsize=(11.4, 7.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], width_ratios=[1.1, 1], hspace=0.42, wspace=0.50,
                          left=0.045, right=0.985, top=0.885, bottom=0.09)

    # ---- (1) crisp output -------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    for t in out.terms:
        ax.plot(out.universe, out.mf(t), color="#B0B0B0", lw=1, ls="--")
        peak = out.universe[int(np.argmax(out.mf(t)))] if t != list(out.terms)[0] else out.universe[0] + 4
        if t == list(out.terms)[-1]:
            peak = 93
        ax.text(peak, 1.04, t, ha="center", fontsize=7.2, color="#555555")
    for (r, s), shape in zip(raw["fired"], raw["clipped"]):
        if s > 1e-9:
            ax.fill_between(out.universe, shape, color=H.rule_hex(r.rid), alpha=0.75, lw=0)
    ax.plot(out.universe, raw["aggregated"], color="black", lw=1.4)
    ax.axvline(res["crisp"], color="#C00000", lw=2.2)
    ax.text(res["crisp"], 0.5, f" crisp = {res['crisp']:.1f}", color="#C00000", fontsize=10, fontweight="bold",
            va="center", ha="left" if res["crisp"] < 70 else "right",
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
    ax.set_ylim(0, 1.16); ax.set_xlim(0, 100); ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel(out.unit); ax.set_ylabel("membership")
    ax.set_title("1  Crisp output (centroid of the combined rule shapes)", loc="left")

    # ---- (2) rules fired ----------------------------------------------------
    ax = fig.add_subplot(gs[0, 1]); ax.axis("off")
    ax.set_title("2  Rules fired (chip colour = colour of the handbook highlight)", loc="left")
    fired = res["fired"][:6]
    n = max(len(fired), 1)
    rowh = min(0.19, 0.94 / n)
    for i, f in enumerate(fired):
        y = 0.96 - (i + 1) * rowh
        ax.add_patch(FancyBboxPatch((0, y + 0.02), 0.095, rowh - 0.04, boxstyle="round,pad=0.005,rounding_size=0.015",
                                    fc=H.rule_hex(f["rid"]), ec="#444444", lw=0.8, transform=ax.transAxes))
        ax.text(0.047, y + rowh / 2 - 0.005, f["rid"], ha="center", va="center", fontsize=8.5, fontweight="bold", transform=ax.transAxes)
        ax.text(0.11, y + rowh / 2, _wrap(f["text"].split("   (")[0], 46), va="center", fontsize=7.4, transform=ax.transAxes)
        ax.add_patch(Rectangle((0.83, y + rowh * 0.32), 0.15, rowh * 0.26, fc="#EEEEEE", ec="#999999", lw=0.6, transform=ax.transAxes))
        ax.add_patch(Rectangle((0.83, y + rowh * 0.32), 0.15 * f["strength"], rowh * 0.26, fc=H.rule_hex(f["rid"]), ec="none", transform=ax.transAxes))
        ax.text(0.905, y + rowh * 0.72, f"strength {f['strength']:.2f}", ha="center", fontsize=7.2, transform=ax.transAxes)

    # ---- (3) text card -------------------------------------------------------
    ax = fig.add_subplot(gs[1, 0]); ax.axis("off")
    ax.set_title("3  Linguistic interpretation, decision and advice", loc="left")
    box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.0,rounding_size=0.02", fc="#F5F5F5", ec="#999999", transform=ax.transAxes)
    ax.add_patch(box)
    lines = [(f"Result:  {res['label']}", 12, "bold", "#C00000"),
             (_wrap(res["interpretation"], 78), 8.6, "normal", "black"),
             (f"Decision code: {res['decision']}", 8.6, "bold", "#000000")]
    y = 0.95
    for txt, fs, fw, col in lines:
        ax.text(0.025, y, txt, va="top", fontsize=fs, fontweight=fw, color=col, transform=ax.transAxes)
        y -= 0.062 * (txt.count("\n") + 1) * (fs / 8.6) + 0.035
    ax.text(0.025, y, "What the handbook says / advice:", va="top", fontsize=8.6, fontweight="bold", transform=ax.transAxes)
    y -= 0.075
    for a in res["advice"]:
        t = "- " + _wrap(a, 80).replace("\n", "\n  ")
        ax.text(0.025, y, t, va="top", fontsize=7.9, transform=ax.transAxes)
        y -= 0.058 * (t.count("\n") + 1) + 0.012

    # ---- (4) fuzzification of inputs -----------------------------------------
    ax = fig.add_subplot(gs[1, 1])
    ax.set_title("4  Fuzzification: how much each term applies", loc="left")
    labels, vals, cols = [], [], []
    for vname, var in sysm.inputs.items():
        for t in var.terms:
            if t in ("Meets", "Not-Reduced"):
                continue
            labels.append(f"{vname}: {t}"); vals.append(res["fuzzified"][vname][t]); cols.append(_term_colour(var, t))
    yy = np.arange(len(labels))[::-1]
    ax.barh(yy, vals, color=cols, height=0.62)
    for yv, v in zip(yy, vals):
        ax.text(min(v, 0.92) + 0.02, yv, f"{v:.2f}", va="center", fontsize=7.5)
    ax.set_yticks(yy); ax.set_yticklabels(labels, fontsize=7.5); ax.set_xlim(0, 1.15); ax.set_xlabel("membership degree")

    fig.suptitle(title or sysm.name, x=0.045, ha="left", fontsize=13, fontweight="bold", y=0.975)
    return fig


# ---------------------------------------------------------------------------
# 3. Boundary and surface plots
# ---------------------------------------------------------------------------
def boundary_figure():
    fig, axes = plt.subplots(3, 1, figsize=(8.6, 9.4))
    # module 1 : BS student, no earlier probation
    x = np.round(np.arange(1.70, 2.60, 0.01), 2)
    y = [S.evaluate_standing("BBA / BEE / BS", v, 0)["crisp"] for v in x]
    ax = axes[0]; ax.plot(x, y, lw=2, color="#1F77B4")
    ax.axvline(2.0, color="black", ls="--"); ax.text(2.005, 8, "handbook limit 2.00\n(2.00 is NOT probation)", fontsize=8)
    ax.axvspan(1.70, 1.995, color="#E45756", alpha=0.10); ax.axvspan(2.0, 2.35, color="#F58518", alpha=0.12); ax.axvspan(2.35, 2.6, color="#54A24B", alpha=0.10)
    ax.text(1.72, 80, "First-Probation zone (crisp edge)", fontsize=8); ax.text(2.04, 62, "Watch zone (fuzzy early-warning)", fontsize=8); ax.text(2.38, 8, "Safe", fontsize=8)
    ax.set_title("Module 1 - BS student, no earlier probation"); ax.set_xlabel("CGPA"); ax.set_ylabel("risk score"); ax.set_ylim(0, 100)
    # module 2 : honours, clean record
    x = np.round(np.arange(3.20, 4.001, 0.01), 2)
    y = [S.evaluate_honours(v)["crisp"] for v in x]
    ax = axes[1]; ax.plot(x, y, lw=2, color="#1F77B4")
    for lim, name in [(3.60, "Cum Laude\n3.60"), (3.80, "Magna\n3.80"), (3.90, "Summa\n3.90")]:
        ax.axvline(lim, color="black", ls="--"); ax.text(lim + 0.004, 4, name, fontsize=8)
    ax.axvspan(3.30, 3.6, color="#F58518", alpha=0.10); ax.text(3.32, 80, "Near-miss zone\n(NOT eligible)", fontsize=8)
    ax.set_title("Module 2 - honours level, all baseline conditions met"); ax.set_xlabel("CGPA"); ax.set_ylabel("honour score"); ax.set_ylim(0, 100)
    # module 3 : advance merit scholarship (min 3.50), full load
    cat = "Advance Merit (Board Topper / Top Ranker / A-Levels)"
    x = np.round(np.arange(3.30, 4.001, 0.01), 2)
    y = [S.evaluate_scholarship(cat, v, 100)["crisp"] for v in x]
    ax = axes[2]; ax.plot(x, y, lw=2, color="#1F77B4")
    ax.axvline(3.50, color="black", ls="--"); ax.text(3.505, 60, "handbook minimum 3.50\n(3.50 itself is accepted)", fontsize=8)
    ax.axvspan(3.30, 3.495, color="#E45756", alpha=0.10); ax.text(3.32, 80, "Suspended", fontsize=8)
    ax.set_title("Module 3 - Advance Merit scholarship, regular course load"); ax.set_xlabel("GPA / CGPA"); ax.set_ylabel("safety score"); ax.set_ylim(0, 100)
    for a in axes: a.grid(alpha=0.25)
    fig.tight_layout()
    return fig


def surface_figure(module):
    sysm = S.SYSTEMS[module]
    fig = plt.figure(figsize=(7.4, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    if module == "M1":
        xs = np.linspace(-1.0, 1.5, 36); ys = np.array([0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2.0]); xl, yl = "CGPA margin above minimum", "earlier probations"
        f = lambda a, b: sysm.infer({"margin": a, "probations": b})["crisp"]
    elif module == "M2":
        xs = np.linspace(3.2, 4.0, 36); ys = np.linspace(0, 2, 9); xl, yl = "CGPA", "baseline violations"
        f = lambda a, b: sysm.infer({"cgpa": a, "violations": b})["crisp"]
    else:
        xs = np.linspace(-0.5, 1.0, 36); ys = np.linspace(50, 110, 13); xl, yl = "CGPA margin above minimum", "course load (%)"
        f = lambda a, b: sysm.infer({"margin": a, "load": b})["crisp"]
    X, Y = np.meshgrid(xs, ys)
    Z = np.array([[f(a, b) for a in xs] for b in ys])
    surf = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none", alpha=0.95)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_zlabel(sysm.output.name + " score"); ax.view_init(28, -125)
    fig.colorbar(surf, shrink=0.55, pad=0.08)
    ax.set_title(sysm.name + " - output surface")
    return fig


def wireframe_figure():
    """A drawing of the GUI layout (used in the report's GUI chapter)."""
    fig, ax = plt.subplots(figsize=(9.4, 5.6)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 60)
    def box(x, y, w, h, txt, fc="#FFFFFF", fs=8, bold=False, ec="#555555", ha="left"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.8", fc=fc, ec=ec, lw=1))
        ax.text(x + (1 if ha == "left" else w / 2), y + h / 2, txt, va="center", ha=ha, fontsize=fs, fontweight="bold" if bold else "normal")
    box(0, 54, 100, 6, "  BU Handbook Fuzzy Advisor  -  Chapters 4 & 5", "#000000", 11, True); ax.texts[-1].set_color("white")
    box(0, 0, 26, 53, "", "#EFEFEF")
    ax.text(2, 50, "SIDEBAR  (inputs)", fontsize=8, fontweight="bold")
    box(2, 43, 22, 5, "(A) Module selector\n1 Probation  2 Honours  3 Scholarship", "#FFFFFF", 6.6)
    box(2, 33, 22, 8, "(B) Input widgets\nprogramme / category list\nCGPA box + slider\nradio / checkboxes", "#FFFFFF", 6.8)
    box(2, 25, 22, 5, "(C) Course load slider\n(merit scholarships only)", "#FFFFFF", 6.8)
    box(2, 17, 22, 6, "(D) EVALUATE button", "#CFCFCF", 8, True, ha="center")
    box(2, 9, 22, 6, "(E) Example cases\n(one click fills inputs)", "#FFFFFF", 6.8)
    ax.text(29, 50, "MAIN AREA  (answer)", fontsize=8, fontweight="bold")
    box(28, 38, 22, 10, "(1) CRISP OUTPUT\nscore 0-100 + gauge", "#E4E4E4", 8, True)
    box(52, 38, 46, 10, "(2) LINGUISTIC ANSWER\nlabel, decision, handbook-based advice", "#F4F4F4", 8, True)
    box(28, 20, 34, 16, "(3) RULES FIRED\ncolour chip = handbook highlight colour\nIF-THEN text + firing strength bar", "#E9E9E9", 8, True)
    box(64, 20, 34, 16, "(4) FUZZIFICATION\nmembership of each input term", "#DADADA", 8, True)
    box(28, 2, 70, 16, "(5) TABS:  Output shape (centroid)  |  Membership functions  |  Output surface  |  Rule base & sources", "#F0F0F0", 8, True, ha="center")
    fig.tight_layout()
    return fig


def output_shape_figure(res):
    """Stand-alone chart for the GUI: combined rule shapes + centroid (works on light or dark style)."""
    out = res["system"].output; raw = res["raw"]
    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    names = list(out.terms)
    for k, t in enumerate(names):
        ax.plot(out.universe, out.mf(t), color=_ink(), alpha=0.28, lw=1, ls="--")
        xs = out.universe[out.mf(t) >= out.mf(t).max() - 1e-9]
        ax.text(float(np.mean(xs)), 1.07 + 0.09 * (k % 2), t, ha="center", fontsize=7.4, color=_ink(), alpha=0.85)
    for (r, s_), shape in zip(raw["fired"], raw["clipped"]):
        if s_ > 1e-9:
            ax.fill_between(out.universe, shape, color=H.rule_hex(r.rid), alpha=0.85, lw=0, label=r.rid)
    ax.plot(out.universe, raw["aggregated"], color=_ink(), lw=1.3)
    ax.axvline(res["crisp"], color=ACCENT, lw=2.4)
    right = res["crisp"] < 70
    ax.text(res["crisp"] + (1.8 if right else -1.8), 0.55, f"crisp = {res['crisp']:.1f}", ha="left" if right else "right", va="center",
            color=ACCENT, fontsize=10, fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="#1B1820", ec=ACCENT, alpha=0.9))
    ax.set_ylim(0, 1.30); ax.set_xlim(0, 100); ax.set_yticks([0, 0.5, 1]); ax.grid(alpha=0.25)
    ax.set_xlabel(out.unit); ax.set_ylabel("membership")
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.93, bottom=0.20)
    return fig
