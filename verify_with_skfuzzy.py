"""
verify_with_skfuzzy.py
----------------------
Cross-checks our own Mamdani engine against scikit-fuzzy (the library named in the
assignment).  For many random inputs it compares the crisp outputs of all 3 systems.
Run:  python verify_with_skfuzzy.py        (needs: pip install scikit-fuzzy)
"""
import random
import numpy as np
import skfuzzy as fuzz
import systems as S


def sk_infer(system, crisp):
    """Re-implements the same pipeline with scikit-fuzzy building blocks."""
    out = system.output
    clipped = []
    for r in system.rules:
        degs = []
        for name, term in r.ifs:
            var = system.inputs[name]
            kind, p = var.terms[term]
            params = p if kind == "trap" else [p[0], p[1], p[1], p[2]]
            degs.append(float(fuzz.trapmf(np.array([crisp[name]]), params)[0]))
        w = min(degs)
        kind, p = out.terms[r.then[1]]
        omf = fuzz.trapmf(out.universe, p if kind == "trap" else [p[0], p[1], p[1], p[2]])
        clipped.append(np.fmin(w, omf))
    agg = np.max(clipped, axis=0)
    return fuzz.defuzz(out.universe, agg, "centroid")


random.seed(1)
worst = 0
for _ in range(300):
    cases = [
        (S.standing_system, {"margin": random.uniform(-4, 2), "probations": random.choice([0, 1, 2])}),
        (S.honours_system, {"cgpa": random.uniform(0, 4), "violations": random.choice([0, 1, 2, 3])}),
        (S.scholarship_system, {"margin": random.uniform(-4, 1.5), "load": random.uniform(0, 120)}),
    ]
    for sysm, inp in cases:
        mine = sysm.infer(inp)["crisp"]
        theirs = sk_infer(sysm, inp)
        worst = max(worst, abs(mine - theirs))
print(f"Compared 900 random inferences. Largest difference = {worst:.2e}")
print("MATCH" if worst < 1e-3 else "MISMATCH")
