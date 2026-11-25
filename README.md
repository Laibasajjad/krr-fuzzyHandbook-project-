# BU Handbook Fuzzy Advisor  (KRR Assignment #2)

A fuzzy inference system (Mamdani, centroid defuzzification) that answers student questions
using rules taken from **Chapter 4 (Scholarships)** and **Chapter 5 (Grading, Probation, Honours)** of the
Bahria University Student Handbook (Spring 2024 edition).

| Module | Handbook | Inputs | Output |
|---|---|---|---|
| 1 Probation & Drop | 5.5 (p.71-72) | CGPA margin above programme minimum, earlier probations | Standing: Safe / Watch / 1st Probation / 2nd Probation / Dropped |
| 2 Honours & Awards | 5.6 - 5.9 (p.72-73) | CGPA, number of baseline conditions broken | Not eligible / Near-miss / Cum / Magna / Summa (+ Rector's list) |
| 3 Scholarship Continuation | Ch. 4 (p.49-56) | CGPA margin above scholarship minimum, course load % | Suspended / At-Risk / Continue / Secure |

## 1. Install (Python 3.10+)
```
pip install -r requirements.txt
```

## 2. Run the graphical interface
```
streamlit run app.py
```
Your browser opens. Pick a service on the left, type your numbers, press **EVALUATE**.
You will see the crisp score, the linguistic answer, the advice, and the rules fired (with firing strengths).

## 3. Run the 60-query test-suite
```
python run_tests.py
```
Prints PASS/FAIL for every query and writes `outputs/test_results.csv`.

## 4. Other scripts
| Script | What it does |
|---|---|
| `python verify_with_skfuzzy.py` | Checks our engine against scikit-fuzzy on 900 random inputs |
| `python annotate_handbook.py BU_handbook.pdf` | Re-creates the colour-highlighted handbook pages |
| `python make_figures.py` | Re-creates all plots and the example panels |

## 5. Files
- `fuzzy_engine.py` - small Mamdani engine (membership functions, rules, centroid)
- `handbook_data.py` - handbook numbers, the 24 rules (R01-R24), their source text, pages and colours
- `systems.py` - the three fuzzy systems and the `evaluate_*` functions (validation, advice)
- `plots.py` - membership plots, result panel, boundary and surface plots
- `app.py` - the Streamlit GUI
- `run_tests.py` - the test-suite

Printed handbook page = PDF page - 10 (e.g. printed page 71 is page 81 of the PDF).
