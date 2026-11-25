"""
fuzzy_engine.py
===============
A small, easy-to-read Mamdani fuzzy inference engine (only needs NumPy).

Why write our own engine?
  * Every step (fuzzify -> fire rules -> clip -> combine -> defuzzify) is visible,
    so the code doubles as a study aid for the KRR course.
  * verify_with_skfuzzy.py proves that it gives the same numbers as scikit-fuzzy.

Pipeline used (classic Mamdani):
  1. Fuzzification   : crisp input  -> membership degree of every linguistic term
  2. Rule firing     : AND = min of the antecedent degrees  (firing strength)
  3. Implication     : clip the output term at the firing strength (min)
  4. Aggregation     : combine all clipped output shapes with max
  5. Defuzzification : centroid (centre of gravity) -> one crisp number
"""
from dataclasses import dataclass, field
import numpy as np


# --------------------------------------------------------------------------
# Membership functions
# --------------------------------------------------------------------------
def trapmf(x, abcd):
    """Trapezoid: 0 below a, rises a->b, 1 on b..c, falls c->d, 0 above d.
    a==b (or c==d) gives a vertical edge, which we use for crisp handbook limits."""
    a, b, c, d = abcd
    x = np.atleast_1d(np.asarray(x, dtype=float))
    y = np.zeros_like(x)
    if b > a:
        m = (x > a) & (x < b)
        y[m] = (x[m] - a) / (b - a)
    y[(x >= b) & (x <= c)] = 1.0
    if d > c:
        m = (x > c) & (x < d)
        y[m] = (d - x[m]) / (d - c)
    return y


def trimf(x, abc):
    """Triangle = trapezoid whose top is a single point."""
    a, b, c = abc
    return trapmf(x, (a, b, b, c))


# --------------------------------------------------------------------------
# Variables and rules
# --------------------------------------------------------------------------
@dataclass
class Variable:
    name: str
    lo: float
    hi: float
    step: float
    terms: dict                      # term name -> ("trap" | "tri", params)
    unit: str = ""
    tie_prefer: str = "high"         # used only for output variables
    universe: np.ndarray = field(init=False)

    def __post_init__(self):
        self.universe = np.round(np.arange(self.lo, self.hi + self.step / 2, self.step), 6)

    def mf(self, term, x=None):
        """Membership values of `term` over the universe (or at x)."""
        kind, p = self.terms[term]
        xs = self.universe if x is None else x
        return trapmf(xs, p) if kind == "trap" else trimf(xs, p)

    def degree(self, term, x):
        """Membership degree of ONE crisp value."""
        return float(self.mf(term, x)[0])

    def fuzzify(self, x):
        return {t: self.degree(t, x) for t in self.terms}


@dataclass
class Rule:
    rid: str                         # e.g. "R05"  (same IDs as the traceability table)
    ifs: list                        # [(input_name, term), ...]  joined by AND
    then: tuple                      # (output_name, term)
    text: str = ""                   # human readable IF-THEN sentence


class MamdaniSystem:
    def __init__(self, name, inputs, output, rules):
        self.name = name
        self.inputs = {v.name: v for v in inputs}
        self.output = output
        self.rules = rules

    def infer(self, crisp):
        """crisp = {input_name: value}.  Returns a dictionary with every step."""
        fuzz = {n: v.fuzzify(crisp[n]) for n, v in self.inputs.items()}

        fired, clipped = [], []
        for r in self.rules:
            strength = min(fuzz[n][t] for n, t in r.ifs)          # AND = min
            fired.append((r, strength))
            shape = np.minimum(self.output.mf(r.then[1]), strength)  # implication = clip
            clipped.append(shape)

        agg = np.max(clipped, axis=0)                             # aggregation = max
        area = np.trapezoid(agg, self.output.universe)
        if area <= 0:
            raise ValueError("No rule fired for these inputs, so no answer can be given.")
        crisp_out = float(np.trapezoid(agg * self.output.universe, self.output.universe) / area)

        degrees = {t: self.output.degree(t, crisp_out) for t in self.output.terms}
        best = max(degrees.values())
        winners = [t for t, d in degrees.items() if abs(d - best) < 1e-9]
        label = winners[-1] if self.output.tie_prefer == "high" else winners[0]

        return dict(fuzzified=fuzz, fired=fired, clipped=clipped, aggregated=agg,
                    crisp=crisp_out, out_degrees=degrees, label=label)
