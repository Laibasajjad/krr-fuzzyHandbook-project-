"""make_figures.py - regenerates every figure used in the report (and the sample 'GUI panels')."""
import json
import matplotlib.pyplot as plt
import plots as P, systems as S
import run_tests

BS = "BBA / BEE / BS"
SAMPLES = [
 ("M1", "Healthy student",                      lambda: S.evaluate_standing(BS, 3.20, 0)),
 ("M1", "Just above the limit after probation", lambda: S.evaluate_standing(BS, 2.20, 1)),
 ("M1", "Second consecutive probation",         lambda: S.evaluate_standing(BS, 1.70, 1)),
 ("M1", "Dropped after two probations",         lambda: S.evaluate_standing(BS, 1.40, 2)),
 ("M2", "Summa Cum Laude",                      lambda: S.evaluate_honours(3.95)),
 ("M2", "Magna Cum Laude",                      lambda: S.evaluate_honours(3.85)),
 ("M2", "Near miss (3.55)",                     lambda: S.evaluate_honours(3.55)),
 ("M2", "High CGPA but disciplinary penalty",   lambda: S.evaluate_honours(3.95, ["5.6.6"])),
 ("M3", "FAS holder, CGPA 2.55",                lambda: S.evaluate_scholarship("Financial Assistance Scholarship (FAS)", 2.55)),
 ("M3", "Merit scholar, 60% load",              lambda: S.evaluate_scholarship("Merit - Batch Topper (non-engineering)", 3.90, 60)),
 ("M3", "Advance Merit exactly at 3.50",        lambda: S.evaluate_scholarship("Advance Merit (Board Topper / Top Ranker / A-Levels)", 3.50, 100)),
 ("M3", "FAS holder, CGPA 3.40",                lambda: S.evaluate_scholarship("Financial Assistance Scholarship (FAS)", 3.40)),
]
meta = []
for i, (m, name, fn) in enumerate(SAMPLES, 1):
    r = fn()
    P.result_panel(r, f"Example {i}: {name}").savefig(f"outputs/samples/sample_{i:02d}.png", dpi=125); plt.close("all")
    meta.append(dict(n=i, module=m, name=name, inputs={k: v for k, v in r["inputs"].items()}, derived=r["derived"],
                     crisp=r["crisp"], label=r["label"], decision=r["decision"], interpretation=r["interpretation"],
                     advice=r["advice"], fired=[(f["rid"], f["strength"]) for f in r["fired"]]))
json.dump(meta, open("outputs/samples/samples.json", "w"), indent=1, default=str)
for m in ("M1", "M2", "M3"):
    P.mf_figure(m).savefig(f"outputs/figures/mf_{m}.png", dpi=130, bbox_inches="tight")
    P.surface_figure(m).savefig(f"outputs/figures/surface_{m}.png", dpi=130, bbox_inches="tight")
P.boundary_figure().savefig("outputs/figures/boundary.png", dpi=130, bbox_inches="tight")
P.wireframe_figure().savefig("outputs/figures/gui_wireframe.png", dpi=130, bbox_inches="tight")

# test-result chart
rows = run_tests.run()
fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
for ax, key in zip(axs, ("module", "type")):
    ks = sorted({r[key] for r in rows}); ps = [sum(r["result"] == "PASS" for r in rows if r[key] == k) for k in ks]
    ts = [sum(1 for r in rows if r[key] == k) for k in ks]
    ax.bar(ks, ts, color="#E45756", label="failed"); ax.bar(ks, ps, color="#54A24B", label="passed")
    for k, p, t in zip(ks, ps, ts): ax.text(k, t + 0.4, f"{p}/{t}", ha="center", fontsize=9)
    ax.set_title(f"Results by {key}"); ax.set_ylabel("queries"); ax.legend(fontsize=8); ax.set_ylim(0, max(ts) + 5)
fig.tight_layout(); fig.savefig("outputs/figures/test_summary.png", dpi=130)
print("done")
