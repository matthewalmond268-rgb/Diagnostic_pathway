import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(page_title="Diagnostic Pathway Explorer", layout="wide")

st.title("Diagnostic Testing Pathway Explorer")
st.caption(
    "Interactive health economic model linking diagnostic accuracy, disease severity, "
    "treatment allocation and net monetary benefit."
)

# =========================
# DEFAULT VALUES + RESET HELPERS
# =========================

DEFAULTS = {
    "cohort_size": 10000,
    "p_cad": 0.60,
    "p_mvd_given_cad": 0.70,
    "sens_est": 0.85,
    "spec_est": 0.90,
    "Threshold": 2500,
    "cost_est": 53,
    "cost_ang": 668,
    "cost_cabg": 3527,
    "cost_mm": 157,
    "qaly_nd": 11.40112689,
    "qaly_svd_treated": 8.224409508,
    "qaly_mvd_treated": 8.025797179,
    "qaly_svd_missed": 5.943634468,
    "qaly_mvd_missed": 3.211270002,
    "qaly_svd_mm": 8.060466987,
    "qaly_mvd_mm": 4.082891737,
    "p_cabg_svd": 0.50,
    "p_cabg_mvd": 0.90,
    "p_survive_ang_mvd": 0.999,
    "p_survive_ang_svd": 0.997,
    "p_survive_ang_nd": 0.9998,
    "p_survive_cabg_mvd": 0.92,
    "p_survive_cabg_svd": 0.97,
    "p_success_cabg_mvd": 0.70,
    "p_success_cabg_svd": 0.85,
}


def reset_keys(keys):
    for key in keys:
        st.session_state[key] = DEFAULTS[key]
    st.rerun()


def reset_all():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()


# =========================
# SIDEBAR INPUTS
# =========================

st.sidebar.header("Reset")

if st.sidebar.button("Reset all inputs"):
    reset_all()

st.sidebar.markdown("---")

st.sidebar.header("Population Inputs")

if st.sidebar.button("Reset population inputs"):
    reset_keys(["cohort_size", "p_cad", "p_mvd_given_cad", "sens_est", "spec_est"])

cohort_size = st.sidebar.number_input(
    "Cohort size",
    value=DEFAULTS["cohort_size"],
    min_value=100,
    step=100,
    key="cohort_size"
)

p_cad = st.sidebar.slider(
    "CAD prevalence",
    0.0,
    1.0,
    DEFAULTS["p_cad"],
    0.01,
    key="p_cad"
)

p_mvd_given_cad = st.sidebar.slider(
    "Probability MVD given CAD",
    0.0,
    1.0,
    DEFAULTS["p_mvd_given_cad"],
    0.01,
    key="p_mvd_given_cad"
)

sens_est = st.sidebar.slider(
    "EST sensitivity",
    0.0,
    1.0,
    DEFAULTS["sens_est"],
    0.01,
    key="sens_est"
)

spec_est = st.sidebar.slider(
    "EST specificity",
    0.0,
    1.0,
    DEFAULTS["spec_est"],
    0.01,
    key="spec_est"
)

st.sidebar.header("Cost Inputs")

if st.sidebar.button("Reset cost inputs"):
    reset_keys(["Threshold", "cost_est", "cost_ang", "cost_cabg", "cost_mm"])

Threshold = st.sidebar.number_input(
    "Threshold (£/QALY)",
    value=DEFAULTS["Threshold"],
    min_value=0,
    max_value=50000,
    step=500,
    key="Threshold"
)

cost_est = st.sidebar.number_input(
    "Cost of EST (£)",
    value=DEFAULTS["cost_est"],
    min_value=0,
    max_value=5000,
    step=10,
    key="cost_est"
)

cost_ang = st.sidebar.number_input(
    "Cost of ANG (£)",
    value=DEFAULTS["cost_ang"],
    min_value=0,
    max_value=20000,
    step=50,
    key="cost_ang"
)

cost_cabg = st.sidebar.number_input(
    "Cost of CABG (£)",
    value=DEFAULTS["cost_cabg"],
    min_value=0,
    max_value=20000,
    step=100,
    key="cost_cabg"
)

cost_mm = st.sidebar.number_input(
    "Cost of medical management (£)",
    value=DEFAULTS["cost_mm"],
    min_value=0,
    max_value=5000,
    step=10,
    key="cost_mm"
)

st.sidebar.header("QALY Inputs")

if st.sidebar.button("Reset QALY inputs"):
    reset_keys([
        "qaly_nd",
        "qaly_svd_treated",
        "qaly_mvd_treated",
        "qaly_svd_missed",
        "qaly_mvd_missed",
        "qaly_svd_mm",
        "qaly_mvd_mm"
    ])

qaly_nd = st.sidebar.number_input(
    "QALYs: ND",
    value=DEFAULTS["qaly_nd"],
    step=0.5,
    key="qaly_nd"
)

qaly_svd_treated = st.sidebar.number_input(
    "QALYs: SVD treated",
    value=DEFAULTS["qaly_svd_treated"],
    step=0.5,
    key="qaly_svd_treated"
)

qaly_mvd_treated = st.sidebar.number_input(
    "QALYs: MVD treated",
    value=DEFAULTS["qaly_mvd_treated"],
    step=0.5,
    key="qaly_mvd_treated"
)

qaly_svd_missed = st.sidebar.number_input(
    "QALYs: SVD missed",
    value=DEFAULTS["qaly_svd_missed"],
    step=0.5,
    key="qaly_svd_missed"
)

qaly_mvd_missed = st.sidebar.number_input(
    "QALYs: MVD missed",
    value=DEFAULTS["qaly_mvd_missed"],
    step=0.5,
    key="qaly_mvd_missed"
)

qaly_svd_mm = st.sidebar.number_input(
    "QALYs: SVD medical management",
    value=DEFAULTS["qaly_svd_mm"],
    step=0.5,
    key="qaly_svd_mm"
)

qaly_mvd_mm = st.sidebar.number_input(
    "QALYs: MVD medical management",
    value=DEFAULTS["qaly_mvd_mm"],
    step=0.5,
    key="qaly_mvd_mm"
)

st.sidebar.header("Treatment Allocation")

if st.sidebar.button("Reset treatment inputs"):
    reset_keys(["p_cabg_svd", "p_cabg_mvd"])

p_cabg_svd = st.sidebar.slider(
    "Probability CABG if detected SVD",
    0.0,
    1.0,
    DEFAULTS["p_cabg_svd"],
    0.01,
    key="p_cabg_svd"
)

p_cabg_mvd = st.sidebar.slider(
    "Probability CABG if detected MVD",
    0.0,
    1.0,
    DEFAULTS["p_cabg_mvd"],
    0.01,
    key="p_cabg_mvd"
)

st.sidebar.header("Clinical Event Probabilities")

if st.sidebar.button("Reset clinical event inputs"):
    reset_keys([
        "p_survive_ang_mvd",
        "p_survive_ang_svd",
        "p_survive_ang_nd",
        "p_survive_cabg_mvd",
        "p_survive_cabg_svd",
        "p_success_cabg_mvd",
        "p_success_cabg_svd",
    ])

p_survive_ang_mvd = st.sidebar.slider(
    "Survive ANG if MVD",
    0.0, 1.0,
    DEFAULTS["p_survive_ang_mvd"],
    0.0001,
    key="p_survive_ang_mvd"
)

p_survive_ang_svd = st.sidebar.slider(
    "Survive ANG if SVD",
    0.0, 1.0,
    DEFAULTS["p_survive_ang_svd"],
    0.0001,
    key="p_survive_ang_svd"
)

p_survive_ang_nd = st.sidebar.slider(
    "Survive ANG if ND",
    0.0, 1.0,
    DEFAULTS["p_survive_ang_nd"],
    0.0001,
    key="p_survive_ang_nd"
)

p_survive_cabg_mvd = st.sidebar.slider(
    "Survive CABG if MVD",
    0.0, 1.0,
    DEFAULTS["p_survive_cabg_mvd"],
    0.001,
    key="p_survive_cabg_mvd"
)

p_survive_cabg_svd = st.sidebar.slider(
    "Survive CABG if SVD",
    0.0, 1.0,
    DEFAULTS["p_survive_cabg_svd"],
    0.001,
    key="p_survive_cabg_svd"
)

p_success_cabg_mvd = st.sidebar.slider(
    "Successful CABG if MVD",
    0.0, 1.0,
    DEFAULTS["p_success_cabg_mvd"],
    0.01,
    key="p_success_cabg_mvd"
)

p_success_cabg_svd = st.sidebar.slider(
    "Successful CABG if SVD",
    0.0, 1.0,
    DEFAULTS["p_success_cabg_svd"],
    0.01,
    key="p_success_cabg_svd"
)

# Complementary probabilities
p_die_ang_mvd = 1 - p_survive_ang_mvd
p_die_ang_svd = 1 - p_survive_ang_svd
p_die_ang_nd = 1 - p_survive_ang_nd

p_die_cabg_mvd = 1 - p_survive_cabg_mvd
p_die_cabg_svd = 1 - p_survive_cabg_svd

p_unsuccessful_cabg_mvd = 1 - p_success_cabg_mvd
p_unsuccessful_cabg_svd = 1 - p_success_cabg_svd

# =========================
# MODEL FUNCTION
# =========================

def run_model(
    sens_value=sens_est,
    spec_value=spec_est,
    p_cad_value=p_cad,
    p_mvd_given_cad_value=p_mvd_given_cad,
    lambda_value=Threshold,
    cabg_cost_value=cost_cabg
):
    cad = cohort_size * p_cad_value
    nd = cohort_size * (1 - p_cad_value)

    mvd = cad * p_mvd_given_cad_value
    svd = cad * (1 - p_mvd_given_cad_value)

    tp_svd = svd * sens_value
    fn_svd = svd * (1 - sens_value)

    tp_mvd = mvd * sens_value
    fn_mvd = mvd * (1 - sens_value)

    tn_nd = nd * spec_value
    fp_nd = nd * (1 - spec_value)

    true_positive = tp_svd + tp_mvd
    false_negative = fn_svd + fn_mvd
    true_negative = tn_nd
    false_positive = fp_nd

    ppv = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
    npv = true_negative / (true_negative + false_negative) if (true_negative + false_negative) > 0 else 0

    svd_cabg = tp_svd * p_cabg_svd
    svd_mm_after_detection = tp_svd * (1 - p_cabg_svd)

    mvd_cabg = tp_mvd * p_cabg_mvd
    mvd_mm_after_detection = tp_mvd * (1 - p_cabg_mvd)

    est_total_cost = (
        cohort_size * cost_est
        + (true_positive + false_positive) * cost_ang
        + (svd_cabg + mvd_cabg) * cabg_cost_value
        + (svd_mm_after_detection + mvd_mm_after_detection + false_negative) * cost_mm
    )

    est_total_qalys = (
        svd_cabg * qaly_svd_treated
        + svd_mm_after_detection * qaly_svd_mm
        + fn_svd * qaly_svd_missed
        + mvd_cabg * qaly_mvd_treated
        + mvd_mm_after_detection * qaly_mvd_mm
        + fn_mvd * qaly_mvd_missed
        + tn_nd * qaly_nd
        + fp_nd * qaly_nd
    )

    est_cost = est_total_cost / cohort_size
    est_qalys = est_total_qalys / cohort_size
    est_nmb = (lambda_value * est_qalys) - est_cost

        # ANG strategy:
    # Everyone receives angiography.
    # Disease status is assumed to be correctly identified.
    # Detected SVD/MVD patients are allocated to CABG or MM using the same treatment probabilities as EST.

    ang_svd_cabg = svd * p_cabg_svd
    ang_svd_mm = svd * (1 - p_cabg_svd)

    ang_mvd_cabg = mvd * p_cabg_mvd
    ang_mvd_mm = mvd * (1 - p_cabg_mvd)

    ang_total_cost = (
        cohort_size * cost_ang
        + (ang_svd_cabg + ang_mvd_cabg) * cabg_cost_value
        + (ang_svd_mm + ang_mvd_mm) * cost_mm
    )

    ang_total_qalys = (
        ang_svd_cabg * qaly_svd_treated
        + ang_svd_mm * qaly_svd_mm
        + ang_mvd_cabg * qaly_mvd_treated
        + ang_mvd_mm * qaly_mvd_mm
        + nd * qaly_nd
    )

    ang_cost = ang_total_cost / cohort_size
    ang_qalys = ang_total_qalys / cohort_size
    ang_nmb = (lambda_value * ang_qalys) - ang_cost

    nt_total_cost = (
        svd * cost_mm
        + mvd * cost_mm
    )

    nt_total_qalys = (
        svd * qaly_svd_mm
        + mvd * qaly_mvd_mm
        + nd * qaly_nd
    )

    nt_cost = nt_total_cost / cohort_size
    nt_qalys = nt_total_qalys / cohort_size
    nt_nmb = (lambda_value * nt_qalys) - nt_cost

    results = pd.DataFrame({
    "Strategy": ["EST", "ANG", "NT"],
    "Expected Cost (£)": [est_cost, ang_cost, nt_cost],
    "Expected QALYs": [est_qalys, ang_qalys, nt_qalys],
    "NMB (£)": [est_nmb, ang_nmb, nt_nmb]
    })

    results["Rank"] = results["NMB (£)"].rank(ascending=False, method="min").astype(int)
    results = results.sort_values("NMB (£)", ascending=False)

    return {
        "cad": cad,
        "nd": nd,
        "svd": svd,
        "mvd": mvd,
        "tp_svd": tp_svd,
        "fn_svd": fn_svd,
        "tp_mvd": tp_mvd,
        "fn_mvd": fn_mvd,
        "tn_nd": tn_nd,
        "fp_nd": fp_nd,
        "true_positive": true_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "ppv": ppv,
        "npv": npv,
        "svd_cabg": svd_cabg,
        "svd_mm_after_detection": svd_mm_after_detection,
        "mvd_cabg": mvd_cabg,
        "mvd_mm_after_detection": mvd_mm_after_detection,
        "ang_svd_cabg": ang_svd_cabg,
        "ang_svd_mm": ang_svd_mm,
        "ang_mvd_cabg": ang_mvd_cabg,
        "ang_mvd_mm": ang_mvd_mm,
        "est_nmb": est_nmb,
        "ang_nmb": ang_nmb,
        "nt_nmb": nt_nmb,
        "delta_ang_est": ang_nmb - est_nmb,
        "delta_est_ang": est_nmb - ang_nmb,
        "results": results,
        "best_strategy": results.iloc[0]["Strategy"]
    }


model = run_model()

# =========================
# FULL TREE PATHWAY ENGINE - TEST BRANCH PROTOTYPE
# =========================

def build_est_tpos_mvd_paths():

    paths = []

    # Dynamic probabilities
    p_test_pos = (
        p_cad * sens_est
        + (1 - p_cad) * (1 - spec_est)
    )

    p_mvd = p_cad * p_mvd_given_cad

    p_mvd_given_tpos = (
        sens_est * p_mvd
    ) / p_test_pos

    # Clinical probabilities now controlled by sidebar sliders

    # Utilities
    utility_mvd_cabg_success = qaly_mvd_treated
    utility_mvd_cabg_unsuccessful = qaly_mvd_mm
    utility_mvd_mm = qaly_mvd_mm
    utility_death = 0

    # Decision node: choose CABG or MM based on expected utility
    cabg_mvd_eu = (
        p_survive_cabg_mvd
        * (
            p_success_cabg_mvd * utility_mvd_cabg_success
            + p_unsuccessful_cabg_mvd * utility_mvd_cabg_unsuccessful
        )
        + p_die_cabg_mvd * utility_death
    )

    mm_mvd_eu = utility_mvd_mm

    optimal_mvd_treatment = "CABG" if cabg_mvd_eu >= mm_mvd_eu else "MM"

    # Costs
    cost_path_est_ang_cabg = cost_est + cost_ang + cost_cabg
    cost_path_est_ang_mm = cost_est + cost_ang + cost_mm
    cost_path_est_ang_death = cost_est + cost_ang

    if optimal_mvd_treatment == "CABG":

        # 1. EST -> T+ -> MVD -> survives ANG -> CABG -> survives CABG -> successful CABG
        paths.append({
            "Strategy": "EST",
            "Test Result": "T+",
            "Disease": "MVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Survives CABG",
            "Treatment Outcome": "Successful CABG",
            "Probability": (
                p_test_pos
                * p_mvd_given_tpos
                * p_survive_ang_mvd
                * p_survive_cabg_mvd
                * p_success_cabg_mvd
            ),
            "Cost (£)": cost_path_est_ang_cabg,
            "QALYs": utility_mvd_cabg_success
        })

        # 2. EST -> T+ -> MVD -> survives ANG -> CABG -> survives CABG -> unsuccessful CABG
        paths.append({
            "Strategy": "EST",
            "Test Result": "T+",
            "Disease": "MVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Survives CABG",
            "Treatment Outcome": "Unsuccessful CABG",
            "Probability": (
                p_test_pos
                * p_mvd_given_tpos
                * p_survive_ang_mvd
                * p_survive_cabg_mvd
                * p_unsuccessful_cabg_mvd
            ),
            "Cost (£)": cost_path_est_ang_cabg,
            "QALYs": utility_mvd_cabg_unsuccessful
        })

        # 3. EST -> T+ -> MVD -> survives ANG -> CABG -> dies during CABG
        paths.append({
            "Strategy": "EST",
            "Test Result": "T+",
            "Disease": "MVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Dies during CABG",
            "Treatment Outcome": "Death",
            "Probability": (
                p_test_pos
                * p_mvd_given_tpos
                * p_survive_ang_mvd
                * p_die_cabg_mvd
            ),
            "Cost (£)": cost_path_est_ang_cabg,
            "QALYs": utility_death
        })

    if optimal_mvd_treatment == "MM":

        # 4. EST -> T+ -> MVD -> survives ANG -> MM
        paths.append({
            "Strategy": "EST",
            "Test Result": "T+",
            "Disease": "MVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "MM",
            "CABG Outcome": "Not applicable",
            "Treatment Outcome": "Medical management",
            "Probability": (
                p_test_pos
                * p_mvd_given_tpos
                * p_survive_ang_mvd
            ),
            "Cost (£)": cost_path_est_ang_mm,
            "QALYs": utility_mvd_mm
        })

    # 5. EST -> T+ -> MVD -> dies during ANG
    paths.append({
        "Strategy": "EST",
        "Test Result": "T+",
        "Disease": "MVD",
        "ANG Outcome": "Dies during ANG",
        "Treatment": "None",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "Death",
        "Probability": (
            p_test_pos
            * p_mvd_given_tpos
            * p_die_ang_mvd
        ),
        "Cost (£)": cost_path_est_ang_death,
        "QALYs": utility_death
    })

    df = pd.DataFrame(paths)
    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df

def build_est_tpos_svd_paths():

    paths = []

    # Dynamic probabilities
    p_test_pos = (
        p_cad * sens_est
        + (1 - p_cad) * (1 - spec_est)
    )

    p_svd = p_cad * (1 - p_mvd_given_cad)

    p_svd_given_tpos = (
        sens_est * p_svd
    ) / p_test_pos

    # Clinical probabilities now controlled by sidebar sliders

    # Utilities
    utility_svd_cabg_success = qaly_svd_treated
    utility_svd_cabg_unsuccessful = qaly_svd_mm
    utility_svd_mm = qaly_svd_mm

    utility_death = 0

    # Decision node: choose CABG or MM based on expected utility

    cabg_svd_eu = (
        p_survive_cabg_svd
        * (
            p_success_cabg_svd * utility_svd_cabg_success
            + p_unsuccessful_cabg_svd * utility_svd_cabg_unsuccessful
        )
        + p_die_cabg_svd * utility_death
    )

    mm_svd_eu = utility_svd_mm

    optimal_svd_treatment = "CABG" if cabg_svd_eu >= mm_svd_eu else "MM"

    # Costs
    cost_path_est_ang_cabg = cost_est + cost_ang + cost_cabg
    cost_path_est_ang_mm = cost_est + cost_ang + cost_mm
    cost_path_est_ang_death = cost_est + cost_ang

    if optimal_svd_treatment == "CABG":

        # 1. Successful CABG
        paths.append({
            "Strategy": "EST",
            "Test Result": "T+",
            "Disease": "SVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Survives CABG",
            "Treatment Outcome": "Successful CABG",
            "Probability": (
                p_test_pos
                * p_svd_given_tpos
                * p_survive_ang_svd
                * p_survive_cabg_svd
                * p_success_cabg_svd
            ),
            "Cost (£)": cost_path_est_ang_cabg,
            "QALYs": utility_svd_cabg_success
        })

        # 2. Unsuccessful CABG
        paths.append({
            "Strategy": "EST",
            "Test Result": "T+",
            "Disease": "SVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Survives CABG",
            "Treatment Outcome": "Unsuccessful CABG",
            "Probability": (
                p_test_pos
                * p_svd_given_tpos
                * p_survive_ang_svd
                * p_survive_cabg_svd
                * p_unsuccessful_cabg_svd
            ),
            "Cost (£)": cost_path_est_ang_cabg,
            "QALYs": utility_svd_cabg_unsuccessful
        })

        # 3. Dies during CABG
        paths.append({
            "Strategy": "EST",
            "Test Result": "T+",
            "Disease": "SVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Dies during CABG",
            "Treatment Outcome": "Death",
            "Probability": (
                p_test_pos
                * p_svd_given_tpos
                * p_survive_ang_svd
                * p_die_cabg_svd
            ),
            "Cost (£)": cost_path_est_ang_cabg,
            "QALYs": utility_death
        })

    if optimal_svd_treatment == "MM":

        paths.append({
            "Strategy": "EST",
            "Test Result": "T+",
            "Disease": "SVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "MM",
            "CABG Outcome": "Not applicable",
            "Treatment Outcome": "Medical management",

            "Probability": (
                p_test_pos
                * p_svd_given_tpos
                * p_survive_ang_svd
            ),

            "Cost (£)": cost_path_est_ang_mm,
            "QALYs": utility_svd_mm
        })

    # 5. Dies during ANG
    paths.append({
        "Strategy": "EST",
        "Test Result": "T+",
        "Disease": "SVD",
        "ANG Outcome": "Dies during ANG",
        "Treatment": "None",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "Death",
        "Probability": (
            p_test_pos
            * p_svd_given_tpos
            * p_die_ang_svd
        ),
        "Cost (£)": cost_path_est_ang_death,
        "QALYs": utility_death
    })

    df = pd.DataFrame(paths)

    df["Weighted Cost (£)"] = (
        df["Probability"] * df["Cost (£)"]
    )

    df["Weighted QALYs"] = (
        df["Probability"] * df["QALYs"]
    )

    return df

def build_est_tpos_nd_paths():

    paths = []

    # Dynamic probabilities
    p_test_pos = (
        p_cad * sens_est
        + (1 - p_cad) * (1 - spec_est)
    )

    p_nd = 1 - p_cad

    p_nd_given_tpos = (
        (1 - spec_est) * p_nd
    ) / p_test_pos

    # Clinical probabilities now controlled by sidebar sliders

    utility_nd = qaly_nd
    utility_death = 0

    cost_path_est_ang = cost_est + cost_ang

    # 1. EST -> T+ -> ND -> survives ANG
    paths.append({
        "Strategy": "EST",
        "Test Result": "T+",
        "Disease": "ND",
        "ANG Outcome": "Survives ANG",
        "Treatment": "No treatment",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "No disease",
        "Probability": (
            p_test_pos
            * p_nd_given_tpos
            * p_survive_ang_nd
        ),
        "Cost (£)": cost_path_est_ang,
        "QALYs": utility_nd
    })

    # 2. EST -> T+ -> ND -> dies during ANG
    paths.append({
        "Strategy": "EST",
        "Test Result": "T+",
        "Disease": "ND",
        "ANG Outcome": "Dies during ANG",
        "Treatment": "None",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "Death",
        "Probability": (
            p_test_pos
            * p_nd_given_tpos
            * p_die_ang_nd
        ),
        "Cost (£)": cost_path_est_ang,
        "QALYs": utility_death
    })

    df = pd.DataFrame(paths)

    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df

def build_est_tpos_ang_paths():
    return pd.concat(
        [
            build_est_tpos_mvd_paths(),
            build_est_tpos_svd_paths(),
            build_est_tpos_nd_paths()
        ],
        ignore_index=True
    )


def build_est_tpos_paths():

    ang_df = build_est_tpos_ang_paths()
    no_ang_df = build_est_tpos_no_ang_paths()

    ang_eu = ang_df["Weighted QALYs"].sum()
    no_ang_eu = no_ang_df["Weighted QALYs"].sum()

    if ang_eu >= no_ang_eu:
        return ang_df
    else:
        return no_ang_df

def build_est_tpos_no_ang_paths():

    paths = []

    # Dynamic probabilities
    p_test_pos = (
        p_cad * sens_est
        + (1 - p_cad) * (1 - spec_est)
    )

    p_mvd = p_cad * p_mvd_given_cad
    p_svd = p_cad * (1 - p_mvd_given_cad)
    p_nd = 1 - p_cad

    p_mvd_given_tpos = (sens_est * p_mvd) / p_test_pos
    p_svd_given_tpos = (sens_est * p_svd) / p_test_pos
    p_nd_given_tpos = ((1 - spec_est) * p_nd) / p_test_pos

    # Utilities controlled by sidebar
    utility_mvd_no_ang = qaly_mvd_mm
    utility_svd_no_ang = qaly_svd_mm
    utility_nd_no_ang = qaly_nd

    cost_path_est_mm = cost_est + cost_mm
    cost_path_est_only = cost_est

    paths.append({
        "Strategy": "EST",
        "Test Result": "T+",
        "Disease": "MVD",
        "ANG Outcome": "No ANG",
        "Treatment": "MM",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T+ MVD managed without ANG",
        "Probability": p_test_pos * p_mvd_given_tpos,
        "Cost (£)": cost_path_est_mm,
        "QALYs": utility_mvd_no_ang
    })

    paths.append({
        "Strategy": "EST",
        "Test Result": "T+",
        "Disease": "SVD",
        "ANG Outcome": "No ANG",
        "Treatment": "MM",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T+ SVD managed without ANG",
        "Probability": p_test_pos * p_svd_given_tpos,
        "Cost (£)": cost_path_est_mm,
        "QALYs": utility_svd_no_ang
    })

    paths.append({
        "Strategy": "EST",
        "Test Result": "T+",
        "Disease": "ND",
        "ANG Outcome": "No ANG",
        "Treatment": "No treatment",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T+ ND no ANG",
        "Probability": p_test_pos * p_nd_given_tpos,
        "Cost (£)": cost_path_est_only,
        "QALYs": utility_nd_no_ang
    })

    df = pd.DataFrame(paths)
    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df

def build_est_tneg_mm_paths():

    paths = []

    p_test_neg = (
        p_cad * (1 - sens_est)
        + (1 - p_cad) * spec_est
    )

    p_mvd = p_cad * p_mvd_given_cad
    p_svd = p_cad * (1 - p_mvd_given_cad)
    p_nd = 1 - p_cad

    p_mvd_given_tneg = ((1 - sens_est) * p_mvd) / p_test_neg
    p_svd_given_tneg = ((1 - sens_est) * p_svd) / p_test_neg
    p_nd_given_tneg = (spec_est * p_nd) / p_test_neg

    utility_mvd_mm = qaly_mvd_mm
    utility_svd_mm = qaly_svd_mm
    utility_nd = qaly_nd

    cost_path_est_mm = cost_est + cost_mm
    cost_path_est_only = cost_est

    paths.append({
        "Strategy": "EST",
        "Test Result": "T-",
        "Disease": "MVD",
        "ANG Outcome": "Not applicable",
        "Treatment": "MM",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T- disease → MVD → MM",
        "Probability": p_test_neg * p_mvd_given_tneg,
        "Cost (£)": cost_path_est_mm,
        "QALYs": utility_mvd_mm
    })

    paths.append({
        "Strategy": "EST",
        "Test Result": "T-",
        "Disease": "SVD",
        "ANG Outcome": "Not applicable",
        "Treatment": "MM",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T- disease → SVD → MM",
        "Probability": p_test_neg * p_svd_given_tneg,
        "Cost (£)": cost_path_est_mm,
        "QALYs": utility_svd_mm
    })

    paths.append({
        "Strategy": "EST",
        "Test Result": "T-",
        "Disease": "ND",
        "ANG Outcome": "Not applicable",
        "Treatment": "No treatment",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T- no disease",
        "Probability": p_test_neg * p_nd_given_tneg,
        "Cost (£)": cost_path_est_only,
        "QALYs": utility_nd
    })

    df = pd.DataFrame(paths)
    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df


def build_est_tneg_nt_paths():

    paths = []

    p_test_neg = (
        p_cad * (1 - sens_est)
        + (1 - p_cad) * spec_est
    )

    p_mvd = p_cad * p_mvd_given_cad
    p_svd = p_cad * (1 - p_mvd_given_cad)
    p_nd = 1 - p_cad

    p_mvd_given_tneg = ((1 - sens_est) * p_mvd) / p_test_neg
    p_svd_given_tneg = ((1 - sens_est) * p_svd) / p_test_neg
    p_nd_given_tneg = (spec_est * p_nd) / p_test_neg

    utility_mvd_nt = qaly_mvd_missed
    utility_svd_nt = qaly_svd_missed
    utility_nd = qaly_nd

    cost_path_est_only = cost_est

    paths.append({
        "Strategy": "EST",
        "Test Result": "T-",
        "Disease": "MVD",
        "ANG Outcome": "Not applicable",
        "Treatment": "NT",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T- disease → MVD → NT",
        "Probability": p_test_neg * p_mvd_given_tneg,
        "Cost (£)": cost_path_est_only,
        "QALYs": utility_mvd_nt
    })

    paths.append({
        "Strategy": "EST",
        "Test Result": "T-",
        "Disease": "SVD",
        "ANG Outcome": "Not applicable",
        "Treatment": "NT",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T- disease → SVD → NT",
        "Probability": p_test_neg * p_svd_given_tneg,
        "Cost (£)": cost_path_est_only,
        "QALYs": utility_svd_nt
    })

    paths.append({
        "Strategy": "EST",
        "Test Result": "T-",
        "Disease": "ND",
        "ANG Outcome": "Not applicable",
        "Treatment": "No treatment",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "T- no disease",
        "Probability": p_test_neg * p_nd_given_tneg,
        "Cost (£)": cost_path_est_only,
        "QALYs": utility_nd
    })

    df = pd.DataFrame(paths)
    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df


def build_est_tneg_paths():

    mm_df = build_est_tneg_mm_paths()
    nt_df = build_est_tneg_nt_paths()

    mm_eu = mm_df["Weighted QALYs"].sum()
    nt_eu = nt_df["Weighted QALYs"].sum()

    if mm_eu >= nt_eu:
        return mm_df
    else:
        return nt_df


def build_est_paths():

    return pd.concat(
        [
            build_est_tpos_paths(),
            build_est_tneg_paths()
        ],
        ignore_index=True
    )


def build_ang_mvd_paths():

    paths = []

    p_mvd = p_cad * p_mvd_given_cad

    cost_path_ang_cabg = cost_ang + cost_cabg
    cost_path_ang_mm = cost_ang + cost_mm
    cost_path_ang_death = cost_ang

    utility_mvd_cabg_success = qaly_mvd_treated
    utility_mvd_cabg_unsuccessful = qaly_mvd_mm
    utility_mvd_mm = qaly_mvd_mm
    utility_death = 0

    cabg_mvd_eu = (
        p_survive_cabg_mvd
        * (
            p_success_cabg_mvd * utility_mvd_cabg_success
            + p_unsuccessful_cabg_mvd * utility_mvd_cabg_unsuccessful
        )
        + p_die_cabg_mvd * utility_death
    )

    mm_mvd_eu = utility_mvd_mm

    optimal_mvd_treatment = "CABG" if cabg_mvd_eu >= mm_mvd_eu else "MM"

    if optimal_mvd_treatment == "CABG":

        paths.append({
            "Strategy": "ANG",
            "Disease": "MVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Survives CABG",
            "Treatment Outcome": "Successful CABG",
            "Probability": (
                p_mvd
                * p_survive_ang_mvd
                * p_survive_cabg_mvd
                * p_success_cabg_mvd
            ),
            "Cost (£)": cost_path_ang_cabg,
            "QALYs": utility_mvd_cabg_success
        })

        paths.append({
            "Strategy": "ANG",
            "Disease": "MVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Survives CABG",
            "Treatment Outcome": "Unsuccessful CABG",
            "Probability": (
                p_mvd
                * p_survive_ang_mvd
                * p_survive_cabg_mvd
                * p_unsuccessful_cabg_mvd
            ),
            "Cost (£)": cost_path_ang_cabg,
            "QALYs": utility_mvd_cabg_unsuccessful
        })

        paths.append({
            "Strategy": "ANG",
            "Disease": "MVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Dies during CABG",
            "Treatment Outcome": "Death",
            "Probability": (
                p_mvd
                * p_survive_ang_mvd
                * p_die_cabg_mvd
            ),
            "Cost (£)": cost_path_ang_cabg,
            "QALYs": utility_death
        })

    if optimal_mvd_treatment == "MM":

        paths.append({
            "Strategy": "ANG",
            "Disease": "MVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "MM",
            "CABG Outcome": "Not applicable",
            "Treatment Outcome": "Medical management",
            "Probability": (
                p_mvd
                * p_survive_ang_mvd
            ),
            "Cost (£)": cost_path_ang_mm,
            "QALYs": utility_mvd_mm
        })

    paths.append({
        "Strategy": "ANG",
        "Disease": "MVD",
        "ANG Outcome": "Dies during ANG",
        "Treatment": "None",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "Death",
        "Probability": (
            p_mvd
            * p_die_ang_mvd
        ),
        "Cost (£)": cost_path_ang_death,
        "QALYs": utility_death
    })

    df = pd.DataFrame(paths)
    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df


def build_ang_svd_paths():

    paths = []

    p_svd = p_cad * (1 - p_mvd_given_cad)

    cost_path_ang_cabg = cost_ang + cost_cabg
    cost_path_ang_mm = cost_ang + cost_mm
    cost_path_ang_death = cost_ang

    utility_svd_cabg_success = qaly_svd_treated
    utility_svd_cabg_unsuccessful = qaly_svd_mm
    utility_svd_mm = qaly_svd_mm
    utility_death = 0

    cabg_svd_eu = (
        p_survive_cabg_svd
        * (
            p_success_cabg_svd * utility_svd_cabg_success
            + p_unsuccessful_cabg_svd * utility_svd_cabg_unsuccessful
        )
        + p_die_cabg_svd * utility_death
    )

    mm_svd_eu = utility_svd_mm

    optimal_svd_treatment = "CABG" if cabg_svd_eu >= mm_svd_eu else "MM"

    if optimal_svd_treatment == "CABG":

        paths.append({
            "Strategy": "ANG",
            "Disease": "SVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Survives CABG",
            "Treatment Outcome": "Successful CABG",
            "Probability": (
                p_svd
                * p_survive_ang_svd
                * p_survive_cabg_svd
                * p_success_cabg_svd
            ),
            "Cost (£)": cost_path_ang_cabg,
            "QALYs": utility_svd_cabg_success
        })

        paths.append({
            "Strategy": "ANG",
            "Disease": "SVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Survives CABG",
            "Treatment Outcome": "Unsuccessful CABG",
            "Probability": (
                p_svd
                * p_survive_ang_svd
                * p_survive_cabg_svd
                * p_unsuccessful_cabg_svd
            ),
            "Cost (£)": cost_path_ang_cabg,
            "QALYs": utility_svd_cabg_unsuccessful
        })

        paths.append({
            "Strategy": "ANG",
            "Disease": "SVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "CABG",
            "CABG Outcome": "Dies during CABG",
            "Treatment Outcome": "Death",
            "Probability": (
                p_svd
                * p_survive_ang_svd
                * p_die_cabg_svd
            ),
            "Cost (£)": cost_path_ang_cabg,
            "QALYs": utility_death
        })

    if optimal_svd_treatment == "MM":

        paths.append({
            "Strategy": "ANG",
            "Disease": "SVD",
            "ANG Outcome": "Survives ANG",
            "Treatment": "MM",
            "CABG Outcome": "Not applicable",
            "Treatment Outcome": "Medical management",
            "Probability": (
                p_svd
                * p_survive_ang_svd
            ),
            "Cost (£)": cost_path_ang_mm,
            "QALYs": utility_svd_mm
        })

    paths.append({
        "Strategy": "ANG",
        "Disease": "SVD",
        "ANG Outcome": "Dies during ANG",
        "Treatment": "None",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "Death",
        "Probability": (
            p_svd
            * p_die_ang_svd
        ),
        "Cost (£)": cost_path_ang_death,
        "QALYs": utility_death
    })

    df = pd.DataFrame(paths)
    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df


def build_ang_nd_paths():

    paths = []

    p_nd = 1 - p_cad

    cost_path_ang_only = cost_ang

    utility_nd = qaly_nd
    utility_death = 0

    paths.append({
        "Strategy": "ANG",
        "Disease": "ND",
        "ANG Outcome": "Survives ANG",
        "Treatment": "No treatment",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "No disease / no treatment",
        "Probability": (
            p_nd
            * p_survive_ang_nd
        ),
        "Cost (£)": cost_path_ang_only,
        "QALYs": utility_nd
    })

    paths.append({
        "Strategy": "ANG",
        "Disease": "ND",
        "ANG Outcome": "Dies during ANG",
        "Treatment": "None",
        "CABG Outcome": "Not applicable",
        "Treatment Outcome": "Death",
        "Probability": (
            p_nd
            * p_die_ang_nd
        ),
        "Cost (£)": cost_path_ang_only,
        "QALYs": utility_death
    })

    df = pd.DataFrame(paths)
    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df


def build_ang_paths():

    return pd.concat(
        [
            build_ang_mvd_paths(),
            build_ang_svd_paths(),
            build_ang_nd_paths()
        ],
        ignore_index=True
    )


def build_no_test_paths():

    paths = []

    p_mvd = p_cad * p_mvd_given_cad
    p_svd = p_cad * (1 - p_mvd_given_cad)
    p_nd = 1 - p_cad

    utility_mm_mvd = qaly_mvd_mm
    utility_mm_svd = qaly_svd_mm
    utility_mm_nd = qaly_nd

    utility_nt_mvd = qaly_mvd_missed
    utility_nt_svd = qaly_svd_missed
    utility_nt_nd = qaly_nd

    paths.append({
        "Strategy": "No Test",
        "Branch": "MM",
        "Disease": "MVD",
        "Probability": p_mvd,
        "Cost (£)": cost_mm,
        "QALYs": utility_mm_mvd
    })

    paths.append({
        "Strategy": "No Test",
        "Branch": "MM",
        "Disease": "SVD",
        "Probability": p_svd,
        "Cost (£)": cost_mm,
        "QALYs": utility_mm_svd
    })

    paths.append({
        "Strategy": "No Test",
        "Branch": "MM",
        "Disease": "ND",
        "Probability": p_nd,
        "Cost (£)": 0,
        "QALYs": utility_mm_nd
    })

    paths.append({
        "Strategy": "No Test",
        "Branch": "NT",
        "Disease": "MVD",
        "Probability": p_mvd,
        "Cost (£)": 0,
        "QALYs": utility_nt_mvd
    })

    paths.append({
        "Strategy": "No Test",
        "Branch": "NT",
        "Disease": "SVD",
        "Probability": p_svd,
        "Cost (£)": 0,
        "QALYs": utility_nt_svd
    })

    paths.append({
        "Strategy": "No Test",
        "Branch": "NT",
        "Disease": "ND",
        "Probability": p_nd,
        "Cost (£)": 0,
        "QALYs": utility_nt_nd
    })

    df = pd.DataFrame(paths)
    df["Weighted Cost (£)"] = df["Probability"] * df["Cost (£)"]
    df["Weighted QALYs"] = df["Probability"] * df["QALYs"]

    return df

no_test_all_df = build_no_test_paths()

no_test_branch_summary = (
    no_test_all_df
    .groupby(["Strategy", "Branch"], as_index=False)
    .agg({
        "Weighted Cost (£)": "sum",
        "Weighted QALYs": "sum"
    })
)

no_test_branch_summary["NMB (£)"] = (
    Threshold * no_test_branch_summary["Weighted QALYs"]
    - no_test_branch_summary["Weighted Cost (£)"]
)

best_no_test_branch = no_test_branch_summary.loc[
    no_test_branch_summary["NMB (£)"].idxmax(),
    "Branch"
]

no_test_optimal_df = no_test_all_df[
    no_test_all_df["Branch"] == best_no_test_branch
]

df_paths = pd.concat(
    [
        build_est_paths(),
        build_ang_paths(),
        no_test_optimal_df
    ],
    ignore_index=True
)

full_tree_summary = (
    df_paths
    .groupby("Strategy", as_index=False)
    .agg({
        "Weighted Cost (£)": "sum",
        "Weighted QALYs": "sum"
    })
)

full_tree_summary["NMB (£)"] = (
    Threshold * full_tree_summary["Weighted QALYs"]
    - full_tree_summary["Weighted Cost (£)"]
)

full_tree_summary = full_tree_summary.sort_values("NMB (£)", ascending=False)
full_tree_summary["Rank"] = range(1, len(full_tree_summary) + 1)

best_full_tree_strategy = full_tree_summary.iloc[0]["Strategy"]

no_test_df = build_no_test_paths()

no_test_summary = (
    no_test_df
    .groupby(["Strategy", "Branch"], as_index=False)
    .agg({
        "Weighted QALYs": "sum",
        "Weighted Cost (£)": "sum"
    })
)

no_test_summary["NMB (£)"] = (
    Threshold * no_test_summary["Weighted QALYs"]
    - no_test_summary["Weighted Cost (£)"]
)

optimal_no_test = no_test_summary.loc[
    no_test_summary["NMB (£)"].idxmax()
]


# =========================
# HELPER FUNCTIONS
# =========================

def safe_bar_chart(labels, values, title, ylabel, rotation=0):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel(ylabel)

    max_val = np.nanmax(values) if len(values) > 0 else 1
    ax.set_ylim(0, max_val * 1.15 if max_val > 0 else 1)

    ax.grid(axis="y", alpha=0.25)

    plt.xticks(rotation=rotation)
    plt.tight_layout()
    st.pyplot(fig)


def plot_contour_from_grid(X, Y, Z, title, xlabel, ylabel, cbar_label):
    fig, ax = plt.subplots(figsize=(10, 7), dpi=120)

    vmax = np.nanmax(np.abs(Z))
    if vmax == 0 or np.isnan(vmax):
        vmax = 1

    vmin = -vmax
    levels = np.linspace(vmin, vmax, 100)

    contour = ax.contourf(
        X,
        Y,
        Z,
        levels=levels,
        cmap="coolwarm",
        vmin=vmin,
        vmax=vmax
    )

    try:
        ax.contour(X, Y, Z, levels=[0], colors="black", linewidths=2)
    except Exception:
        pass

    cbar = fig.colorbar(contour, ax=ax)
    cbar.set_label(cbar_label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.15)

    plt.tight_layout()
    st.pyplot(fig)

    st.caption(
        "The black contour line shows the decision boundary where ΔNMB = 0. "
        "Positive values favour ANG; negative values favour EST."
    )


def plot_slices(x_vals, y_vals, Z, selected_y, xlabel, ylabel, title, label_name):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

    for y in selected_y:
        row_i = np.argmin(np.abs(y_vals - y))
        nearest_y = y_vals[row_i]
        y_values = Z[row_i, :]

        smooth_y = gaussian_filter1d(y_values, sigma=3)

        ax.plot(
            x_vals,
            smooth_y,
            linewidth=2,
            label=f"{label_name} {nearest_y:.2f}"
        )

    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend()

    plt.tight_layout()
    st.pyplot(fig)

    st.caption(
        "Each line is a one-way slice through the two-way sensitivity surface. "
        "Where a line crosses zero, the preferred strategy switches between ANG and EST."
    )


def make_incremental_table(results_df):
    ordered = results_df.sort_values("Expected Cost (£)").copy()
    ordered["Incremental Cost (£)"] = ordered["Expected Cost (£)"].diff()
    ordered["Incremental QALYs"] = ordered["Expected QALYs"].diff()
    ordered["ICER (£/QALY)"] = ordered["Incremental Cost (£)"] / ordered["Incremental QALYs"]
    ordered["Dominance Note"] = ""
    ordered.loc[ordered["Incremental QALYs"] <= 0, "Dominance Note"] = "Potentially dominated"
    return ordered


def make_tornado_data():
    base_delta = model["delta_ang_est"]

    parameters = [
        ("CAD prevalence", p_cad, 0.05, 1.00, "p_cad_value"),
        ("MVD given CAD", p_mvd_given_cad, 0.05, 1.00, "p_mvd_given_cad_value"),
        ("EST sensitivity", sens_est, 0.05, 1.00, "sens_value"),
        ("EST specificity", spec_est, 0.05, 1.00, "spec_value"),
        ("Threshold", Threshold, 1000, 5000, "lambda_value"),
        ("CABG cost", cost_cabg, 500, 6000, "cabg_cost_value"),
    ]

    rows = []

    for name, current, low, high, arg_name in parameters:
        kwargs_low = {
            "sens_value": sens_est,
            "spec_value": spec_est,
            "p_cad_value": p_cad,
            "p_mvd_given_cad_value": p_mvd_given_cad,
            "lambda_value": Threshold,
            "cabg_cost_value": cost_cabg
        }

        kwargs_high = kwargs_low.copy()

        kwargs_low[arg_name] = low
        kwargs_high[arg_name] = high

        low_delta = run_model(**kwargs_low)["delta_ang_est"]
        high_delta = run_model(**kwargs_high)["delta_ang_est"]

        rows.append({
            "Parameter": name,
            "Low Value": low,
            "High Value": high,
            "Low ΔNMB": low_delta,
            "High ΔNMB": high_delta,
            "Range": abs(high_delta - low_delta),
            "Base ΔNMB": base_delta
        })

    tornado = pd.DataFrame(rows).sort_values("Range", ascending=True)
    return tornado


# =========================
# TABS
# =========================

tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "0. Pathway Structure",
    "1. Population",
    "2. Test Accuracy",
    "3. Cost-Effectiveness",
    "4. Sensitivity Analysis",
    "5. Interpretation",
    "6. Model Assumptions"
])

# =========================
# TAB 0
# =========================

with tab0:
    st.subheader("Clinical Pathway Structure")

    st.caption(
        "Each diagram shows the available branches for that strategy. Where MM and NT or ANG and No ANG appear, "
        "the model selects the option with the higher expected value."
    )

    tree_choice = st.radio(
        "Select pathway to view",
        ["EST", "ANG", "No Test"],
        horizontal=True
    )

    if tree_choice == "EST":
        pathway_graph = """
        digraph {
            graph [rankdir=LR, bgcolor="transparent"];
            node [shape=box, style="rounded,filled", color="#4B5563", fillcolor="#111827", fontcolor="white", fontsize=11];
            edge [color="#9CA3AF", fontcolor="white", fontsize=10];

            Start [label="EST"];
            Start -> TPOS [label="Test +"];
            Start -> TNEG [label="Test -"];

            TPOS -> TPOS_DECISION [label="Decision node"];
            TPOS_DECISION -> ANG [label="ANG"];
            TPOS_DECISION -> NO_ANG [label="No ANG"];

            ANG -> MVD [label="MVD"];
            ANG -> SVD [label="SVD"];
            ANG -> ND [label="ND"];

            MVD -> MVD_CABG [label="CABG"];
            MVD -> MVD_MM [label="MM"];

            SVD -> SVD_CABG [label="CABG"];
            SVD -> SVD_MM [label="MM"];

            ND -> ND_NOTREAT [label="No treatment"];

            TNEG -> TNEG_MM [label="MM"];
            TNEG -> TNEG_NT [label="NT"];
        }
        """

    elif tree_choice == "ANG":
        pathway_graph = """
        digraph {
            graph [rankdir=LR, bgcolor="transparent"];
            node [shape=box, style="rounded,filled", color="#4B5563", fillcolor="#111827", fontcolor="white", fontsize=11];
            edge [color="#9CA3AF", fontcolor="white", fontsize=10];

            Start [label="ANG"];

            Start -> MVD [label="MVD"];
            Start -> SVD [label="SVD"];
            Start -> ND [label="ND"];

            MVD -> MVD_ANG_SURVIVE [label="Survive ANG"];
            MVD -> MVD_ANG_DIE [label="Die during ANG"];

            MVD_ANG_SURVIVE -> MVD_CABG [label="CABG"];
            MVD_ANG_SURVIVE -> MVD_MM [label="MM"];

            MVD_CABG -> MVD_CABG_SUCCESS [label="Successful CABG"];
            MVD_CABG -> MVD_CABG_UNSUCCESS [label="Unsuccessful CABG"];
            MVD_CABG -> MVD_CABG_DIE [label="Die during CABG"];

            SVD -> SVD_ANG_SURVIVE [label="Survive ANG"];
            SVD -> SVD_ANG_DIE [label="Die during ANG"];

            SVD_ANG_SURVIVE -> SVD_CABG [label="CABG"];
            SVD_ANG_SURVIVE -> SVD_MM [label="MM"];

            SVD_CABG -> SVD_CABG_SUCCESS [label="Successful CABG"];
            SVD_CABG -> SVD_CABG_UNSUCCESS [label="Unsuccessful CABG"];
            SVD_CABG -> SVD_CABG_DIE [label="Die during CABG"];

            ND -> ND_ANG_SURVIVE [label="Survive ANG"];
            ND -> ND_ANG_DIE [label="Die during ANG"];

            ND_ANG_SURVIVE -> ND_NOTREAT [label="No treatment"];
        }
        """

    else:
        pathway_graph = """
        digraph {
            graph [rankdir=LR, bgcolor="transparent"];
            node [shape=box, style="rounded,filled", color="#4B5563", fillcolor="#111827", fontcolor="white", fontsize=11];
            edge [color="#9CA3AF", fontcolor="white", fontsize=10];

            Start [label="No Test"];

            Start -> Decision [label="Decision node"];
            Decision -> MM [label="MM"];
            Decision -> NT [label="NT"];

            MM -> MM_MVD [label="MVD"];
            MM -> MM_SVD [label="SVD"];
            MM -> MM_ND [label="ND"];

            NT -> NT_MVD [label="MVD"];
            NT -> NT_SVD [label="SVD"];
            NT -> NT_ND [label="ND"];

            MM_MVD -> MM_MVD_OUT [label="QALYs / cost"];
            MM_SVD -> MM_SVD_OUT [label="QALYs / cost"];
            MM_ND -> MM_ND_OUT [label="QALYs / cost"];

            NT_MVD -> NT_MVD_OUT [label="QALYs / cost"];
            NT_SVD -> NT_SVD_OUT [label="QALYs / cost"];
            NT_ND -> NT_ND_OUT [label="QALYs / cost"];
        }
        """

    st.graphviz_chart(pathway_graph, use_container_width=True)

    with st.expander("How to read this pathway", expanded=False):
        st.write(
            """
            These diagrams show pathway structure only. All probabilities, costs, QALYs and NMB calculations are dynamically updated in the tables below.
            """
        )

    st.divider()

    st.subheader("Full Pathway Event Tables")

    st.write(
        "These tables show the full event-level pathway calculations for each strategy."
    )

    st.divider()

    st.header("EST Strategy")

    est_full_df = build_est_paths()
    display_est_full_df = est_full_df.copy()

    display_est_full_df["Probability"] = display_est_full_df["Probability"].map("{:.6f}".format)
    display_est_full_df["Cost (£)"] = display_est_full_df["Cost (£)"].map("£{:,.2f}".format)
    display_est_full_df["QALYs"] = display_est_full_df["QALYs"].map("{:.4f}".format)
    display_est_full_df["Weighted Cost (£)"] = display_est_full_df["Weighted Cost (£)"].map("£{:,.2f}".format)
    display_est_full_df["Weighted QALYs"] = display_est_full_df["Weighted QALYs"].map("{:.4f}".format)

    st.dataframe(display_est_full_df, use_container_width=True)

    est_total_cost = est_full_df["Weighted Cost (£)"].sum()
    est_total_qalys = est_full_df["Weighted QALYs"].sum()
    est_total_nmb = Threshold * est_total_qalys - est_total_cost

    c1, c2, c3 = st.columns(3)
    c1.metric("EST Expected Cost", f"£{est_total_cost:,.2f}")
    c2.metric("EST Expected QALYs", f"{est_total_qalys:.4f}")
    c3.metric("EST NMB", f"£{est_total_nmb:,.2f}")

    st.divider()

    st.header("ANG Strategy")

    ang_full_df = build_ang_paths()
    display_ang_full_df = ang_full_df.copy()

    display_ang_full_df["Probability"] = display_ang_full_df["Probability"].map("{:.6f}".format)
    display_ang_full_df["Cost (£)"] = display_ang_full_df["Cost (£)"].map("£{:,.2f}".format)
    display_ang_full_df["QALYs"] = display_ang_full_df["QALYs"].map("{:.4f}".format)
    display_ang_full_df["Weighted Cost (£)"] = display_ang_full_df["Weighted Cost (£)"].map("£{:,.2f}".format)
    display_ang_full_df["Weighted QALYs"] = display_ang_full_df["Weighted QALYs"].map("{:.4f}".format)

    st.dataframe(display_ang_full_df, use_container_width=True)

    ang_total_cost = ang_full_df["Weighted Cost (£)"].sum()
    ang_total_qalys = ang_full_df["Weighted QALYs"].sum()
    ang_total_nmb = Threshold * ang_total_qalys - ang_total_cost

    c1, c2, c3 = st.columns(3)
    c1.metric("ANG Expected Cost", f"£{ang_total_cost:,.2f}")
    c2.metric("ANG Expected QALYs", f"{ang_total_qalys:.4f}")
    c3.metric("ANG NMB", f"£{ang_total_nmb:,.2f}")

    st.divider()

    st.header("No Test Strategy")

    no_test_df = build_no_test_paths()
    display_no_test_df = no_test_df.copy()

    display_no_test_df["Probability"] = display_no_test_df["Probability"].map("{:.6f}".format)
    display_no_test_df["Cost (£)"] = display_no_test_df["Cost (£)"].map("£{:,.2f}".format)
    display_no_test_df["QALYs"] = display_no_test_df["QALYs"].map("{:.4f}".format)
    display_no_test_df["Weighted Cost (£)"] = display_no_test_df["Weighted Cost (£)"].map("£{:,.2f}".format)
    display_no_test_df["Weighted QALYs"] = display_no_test_df["Weighted QALYs"].map("{:.4f}".format)

    st.dataframe(display_no_test_df, use_container_width=True)

    no_test_summary = (
        no_test_df
        .groupby(["Strategy", "Branch"], as_index=False)
        .agg({
            "Weighted QALYs": "sum",
            "Weighted Cost (£)": "sum"
        })
    )

    no_test_summary["NMB (£)"] = (
        Threshold * no_test_summary["Weighted QALYs"]
        - no_test_summary["Weighted Cost (£)"]
    )

    optimal_no_test = no_test_summary.loc[no_test_summary["NMB (£)"].idxmax()]

    st.subheader("No Test Branch Comparison")

    display_no_test_summary = no_test_summary.copy()
    display_no_test_summary["Weighted Cost (£)"] = display_no_test_summary["Weighted Cost (£)"].map("£{:,.2f}".format)
    display_no_test_summary["Weighted QALYs"] = display_no_test_summary["Weighted QALYs"].map("{:.4f}".format)
    display_no_test_summary["NMB (£)"] = display_no_test_summary["NMB (£)"].map("£{:,.2f}".format)

    st.dataframe(display_no_test_summary, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Optimal No Test Branch", optimal_no_test["Branch"])
    c2.metric("Expected QALYs", f"{optimal_no_test['Weighted QALYs']:.4f}")
    c3.metric("NMB", f"£{optimal_no_test['NMB (£)']:,.2f}")



# =========================
# TAB 1
# =========================

with tab1:
    st.subheader("Disease-State Breakdown")

    c1, c2, c3 = st.columns(3)
    c1.metric("ND", round(model["nd"]))
    c2.metric("SVD", round(model["svd"]))
    c3.metric("MVD", round(model["mvd"]))

    disease_df = pd.DataFrame({
        "Disease State": ["ND", "SVD", "MVD"],
        "Patients": [model["nd"], model["svd"], model["mvd"]]
    })

    with st.expander("Show disease-state chart", expanded=True):
        safe_bar_chart(
            disease_df["Disease State"],
            disease_df["Patients"],
            "Disease-State Breakdown",
            "Patients"
        )
        st.caption("This chart shows how the cohort is split into ND, SVD and MVD.")


# =========================
# TAB 2
# =========================

with tab2:
    st.subheader("Diagnostic Accuracy Outcomes")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("True positives", round(model["true_positive"]))
    c2.metric("False negatives", round(model["false_negative"]))
    c3.metric("True negatives", round(model["true_negative"]))
    c4.metric("False positives", round(model["false_positive"]))

    st.divider()

    st.subheader("Predictive Values")

    c5, c6 = st.columns(2)

    c5.metric("PPV", f"{model['ppv']:.2%}")
    c6.metric("NPV", f"{model['npv']:.2%}")

    with st.expander("What do PPV and NPV mean?", expanded=False):
        st.write(
            """
            **PPV** means positive predictive value.

            It answers:

            > Among people who test positive, how many actually have disease?

            **NPV** means negative predictive value.

            It answers:

            > Among people who test negative, how many truly do not have disease?

            PPV and NPV are affected by disease prevalence.
            Higher prevalence usually increases PPV.
            """
        )

    st.divider()

    st.subheader("Diagnostic Breakdown by Disease State")

    diagnostic_breakdown = pd.DataFrame({
        "Outcome": [
            "TP SVD",
            "FN SVD",
            "TP MVD",
            "FN MVD",
            "TN ND",
            "FP ND"
        ],
        "Patients": [
            model["tp_svd"],
            model["fn_svd"],
            model["tp_mvd"],
            model["fn_mvd"],
            model["tn_nd"],
            model["fp_nd"]
        ]
    })

    diagnostic_display = diagnostic_breakdown.copy()
    diagnostic_display["Patients"] = diagnostic_display["Patients"].round(0).astype(int)

    st.dataframe(diagnostic_display, use_container_width=True)

    with st.expander("Show diagnostic outcome chart", expanded=False):
        safe_bar_chart(
            diagnostic_breakdown["Outcome"],
            diagnostic_breakdown["Patients"],
            "Diagnostic Outcomes by Disease State",
            "Patients",
            rotation=45
        )

    st.divider()

    st.subheader("Confusion Matrix")

    confusion_matrix = pd.DataFrame(
        {
            "Disease Present": [
                round(model["true_positive"]),
                round(model["false_negative"])
            ],
            "No Disease": [
                round(model["false_positive"]),
                round(model["true_negative"])
            ]
        },
        index=["Test Positive", "Test Negative"]
    )

    st.dataframe(confusion_matrix, use_container_width=True)

    with st.expander("What does the confusion matrix mean?", expanded=False):
        st.write(
            """
            The confusion matrix compares the EST test result
            against the patient's true disease status.

            - **True positive:** patient has CAD and EST correctly says positive.
            - **False positive:** patient has no CAD but EST incorrectly says positive.
            - **False negative:** patient has CAD but EST incorrectly says negative.
            - **True negative:** patient has no CAD and EST correctly says negative.

            Sensitivity is based on the disease-present group.

            Specificity is based on the no-disease group.
            """
        )


# =========================
# TAB 3
# =========================

with tab3:
    st.subheader("Cost-Effectiveness Results")

    st.success(
        f"Best strategy at £{Threshold:,.0f}/QALY: "
        f"{best_full_tree_strategy}"
    )

    display_results = full_tree_summary.copy()

    display_results["Weighted Cost (£)"] = (
        display_results["Weighted Cost (£)"]
        .map("£{:,.2f}".format)
    )

    display_results["Weighted QALYs"] = (
        display_results["Weighted QALYs"]
        .map("{:.4f}".format)
    )

    display_results["NMB (£)"] = (
        display_results["NMB (£)"]
        .map("£{:,.2f}".format)
    )

    st.dataframe(display_results, use_container_width=True)

    with st.expander("What does Net Monetary Benefit mean?", expanded=False):
        st.write(
            """
            Net monetary benefit converts QALYs and costs
            into one value.

            NMB = (Threshold × QALYs) − Cost

            A higher NMB means a strategy is more
            cost-effective at the selected threshold.

            The strategy with the highest NMB
            is treated as the preferred strategy.
            """
        )

    st.divider()

    st.subheader("Net Monetary Benefit by Strategy")

    with st.expander("Show NMB chart", expanded=False):
        nmb_df = full_tree_summary.set_index("Strategy")

        safe_bar_chart(
            nmb_df.index,
            nmb_df["NMB (£)"],
            "Net Monetary Benefit by Strategy",
            "NMB (£)"
        )

    st.divider()

    st.subheader("Treatment Allocation After Detection")

    treatment_df = pd.DataFrame({
        "Group": [
            "SVD → CABG",
            "SVD → MM",
            "MVD → CABG",
            "MVD → MM"
        ],
        "Patients": [
            model["svd_cabg"],
            model["svd_mm_after_detection"],
            model["mvd_cabg"],
            model["mvd_mm_after_detection"]
        ]
    })

    treatment_display = treatment_df.copy()
    treatment_display["Patients"] = treatment_display["Patients"].round(0).astype(int)

    st.dataframe(treatment_display, use_container_width=True)

    with st.expander("Show treatment allocation chart", expanded=False):
        safe_bar_chart(
            treatment_df["Group"],
            treatment_df["Patients"],
            "Treatment Allocation After Detection",
            "Patients",
            rotation=45
        )

    st.divider()

    show_tornado = st.checkbox("Show tornado plot", value=False)

    if show_tornado:
        st.subheader("Tornado Plot: Impact on ΔNMB: ANG vs EST")

        tornado = make_tornado_data()

        fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

        y_pos = np.arange(len(tornado))
        low = tornado["Low ΔNMB"]
        high = tornado["High ΔNMB"]
        base = tornado["Base ΔNMB"]

        ax.barh(y_pos, high - low, left=low)
        ax.axvline(base.iloc[0], linestyle="--", linewidth=1.5, label="Base ΔNMB")
        ax.axvline(0, linestyle="-", linewidth=1.5, label="Decision boundary")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(tornado["Parameter"])
        ax.set_xlabel("ΔNMB: ANG − EST (£)")
        ax.set_title("One-Way Sensitivity Analysis Tornado Plot")
        ax.grid(axis="x", alpha=0.25)
        ax.legend()

        plt.tight_layout()
        st.pyplot(fig)

        with st.expander("What does the tornado plot show?", expanded=False):
            st.write(
                """
                A tornado plot shows which parameters have the largest effect on the model result.

                Wider bars mean the conclusion is more sensitive to that parameter.

                This plot varies one parameter at a time and records the impact on:

                **ΔNMB = NMB(ANG) − NMB(EST)**

                - Positive ΔNMB favours ANG.
                - Negative ΔNMB favours EST.
                - The vertical zero line is the decision boundary.
                """
            )


# =========================
# TAB 4
# =========================

with tab4:

    st.subheader("Sensitivity Analysis")

    st.write(
        """
        These figures evaluate how model conclusions change
        when key parameters vary.

        One-way sensitivity analysis varies one parameter at a time.

        Two-way sensitivity analysis varies two parameters simultaneously.

        Positive ΔNMB values favour ANG over EST.
        Negative ΔNMB values favour EST over ANG.
        """
    )

    with st.expander(
        "How should I interpret these sensitivity analysis graphs?",
        expanded=False
    ):
        st.write(
            """
            These graphs show how the preferred strategy changes
            when assumptions vary.

            For the two-way plots:

            ΔNMB = NMB(ANG) − NMB(EST)

            - Positive values favour ANG.
            - Negative values favour EST.
            - The black contour line shows the decision boundary
              where ΔNMB = 0.
            """
        )

    # =========================
    # ONE-WAY SA
    # =========================

    st.divider()

    st.subheader("One-Way Sensitivity Analysis")

    owsa_choice = st.selectbox(
        "Choose parameter to vary",
        [
            "CAD prevalence",
            "Probability MVD given CAD",
            "EST sensitivity",
            "EST specificity",
            "Threshold",
            "Cost of EST",
            "Cost of ANG",
            "Cost of CABG",
            "Cost of medical management",
            "QALYs: ND",
            "QALYs: SVD treated",
            "QALYs: MVD treated",
            "QALYs: SVD missed",
            "QALYs: MVD missed",
            "QALYs: SVD MM",
            "QALYs: MVD MM",
        ]
    )

    owsa_ranges = {
        "CAD prevalence": np.linspace(0.01, 0.99, 100),
        "Probability MVD given CAD": np.linspace(0.01, 0.99, 100),
        "EST sensitivity": np.linspace(0.01, 0.99, 100),
        "EST specificity": np.linspace(0.01, 0.99, 100),
        "Threshold": np.linspace(0, 50000, 100),
        "Cost of EST": np.linspace(0, 1000, 100),
        "Cost of ANG": np.linspace(0, 5000, 100),
        "Cost of CABG": np.linspace(0, 10000, 100),
        "Cost of medical management": np.linspace(0, 3000, 100),
        "QALYs: ND": np.linspace(0, 15, 100),
        "QALYs: SVD treated": np.linspace(0, 15, 100),
        "QALYs: MVD treated": np.linspace(0, 15, 100),
        "QALYs: SVD missed": np.linspace(0, 15, 100),
        "QALYs: MVD missed": np.linspace(0, 15, 100),
        "QALYs: SVD MM": np.linspace(0, 15, 100),
        "QALYs: MVD MM": np.linspace(0, 15, 100),
    }

    def one_way_full_tree(param_name, param_value):

        global p_cad, p_mvd_given_cad, sens_est, spec_est
        global Threshold, cost_est, cost_ang, cost_cabg, cost_mm
        global qaly_nd, qaly_svd_treated, qaly_mvd_treated
        global qaly_svd_missed, qaly_mvd_missed
        global qaly_svd_mm, qaly_mvd_mm

        old_values = {
            "p_cad": p_cad,
            "p_mvd_given_cad": p_mvd_given_cad,
            "sens_est": sens_est,
            "spec_est": spec_est,
            "Threshold": Threshold,
            "cost_est": cost_est,
            "cost_ang": cost_ang,
            "cost_cabg": cost_cabg,
            "cost_mm": cost_mm,
            "qaly_nd": qaly_nd,
            "qaly_svd_treated": qaly_svd_treated,
            "qaly_mvd_treated": qaly_mvd_treated,
            "qaly_svd_missed": qaly_svd_missed,
            "qaly_mvd_missed": qaly_mvd_missed,
            "qaly_svd_mm": qaly_svd_mm,
            "qaly_mvd_mm": qaly_mvd_mm,
        }

        mapping = {
            "CAD prevalence": "p_cad",
            "Probability MVD given CAD": "p_mvd_given_cad",
            "EST sensitivity": "sens_est",
            "EST specificity": "spec_est",
            "Threshold": "Threshold",
            "Cost of EST": "cost_est",
            "Cost of ANG": "cost_ang",
            "Cost of CABG": "cost_cabg",
            "Cost of medical management": "cost_mm",
            "QALYs: ND": "qaly_nd",
            "QALYs: SVD treated": "qaly_svd_treated",
            "QALYs: MVD treated": "qaly_mvd_treated",
            "QALYs: SVD missed": "qaly_svd_missed",
            "QALYs: MVD missed": "qaly_mvd_missed",
            "QALYs: SVD MM": "qaly_svd_mm",
            "QALYs: MVD MM": "qaly_mvd_mm",
        }

        globals()[mapping[param_name]] = param_value

        no_test_all_df = build_no_test_paths()

        no_test_branch_summary = (
            no_test_all_df
            .groupby(["Strategy", "Branch"], as_index=False)
            .agg({
                "Weighted Cost (£)": "sum",
                "Weighted QALYs": "sum"
            })
        )

        no_test_branch_summary["NMB (£)"] = (
            Threshold * no_test_branch_summary["Weighted QALYs"]
            - no_test_branch_summary["Weighted Cost (£)"]
        )

        best_no_test_branch = no_test_branch_summary.loc[
            no_test_branch_summary["NMB (£)"].idxmax(),
            "Branch"
        ]

        no_test_optimal_df = no_test_all_df[
            no_test_all_df["Branch"] == best_no_test_branch
        ]

        temp_df = pd.concat(
            [
                build_est_paths(),
                build_ang_paths(),
                no_test_optimal_df
            ],
            ignore_index=True
        )

        temp_summary = (
            temp_df
            .groupby("Strategy", as_index=False)
            .agg({
                "Weighted Cost (£)": "sum",
                "Weighted QALYs": "sum"
            })
        )

        temp_summary["NMB (£)"] = (
            Threshold * temp_summary["Weighted QALYs"]
            - temp_summary["Weighted Cost (£)"]
        )

        for key, value in old_values.items():
            globals()[key] = value

        return temp_summary

    owsa_values = owsa_ranges[owsa_choice]

    owsa_rows = []

    for value in owsa_values:

        temp_summary = one_way_full_tree(
            owsa_choice,
            value
        )

        for _, row in temp_summary.iterrows():

            owsa_rows.append({
                "Parameter value": value,
                "Strategy": row["Strategy"],
                "NMB (£)": row["NMB (£)"]
            })

    owsa_df = pd.DataFrame(owsa_rows)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

    for strategy in owsa_df["Strategy"].unique():

        strategy_df = owsa_df[
            owsa_df["Strategy"] == strategy
        ]

        ax.plot(
            strategy_df["Parameter value"],
            strategy_df["NMB (£)"],
            linewidth=2,
            label=strategy
        )

    ax.set_xlabel(owsa_choice)
    ax.set_ylabel("Net Monetary Benefit (£)")
    ax.set_title(
        f"One-way sensitivity analysis: {owsa_choice}"
    )

    ax.grid(alpha=0.25)
    ax.legend()

    plt.tight_layout()
    st.pyplot(fig)

    st.caption(
        "This graph varies one parameter at a time while holding all other model inputs constant."
    )

    current_best = (
        owsa_df
        .sort_values(["Parameter value", "NMB (£)"], ascending=[True, False])
        .groupby("Parameter value")
        .first()
        .reset_index()
    )

    st.write("### Preferred strategy by parameter value")

    st.dataframe(
        current_best[["Parameter value", "Strategy", "NMB (£)"]],
        use_container_width=True
    )
    # =========================
    # TWO-WAY SA
    # =========================

    st.divider()

    run_sa = st.button("Run two-way sensitivity analysis")

    if run_sa:

        st.subheader("Threshold and CABG Cost")

        threshold_vals = np.linspace(0, 50000, 101)
        cabg_vals = np.linspace(500, 6000, 101)

        THRESH, CABG = np.meshgrid(
            threshold_vals,
            cabg_vals
        )

        Z_thresh_cabg = np.zeros_like(THRESH)

        for i in range(CABG.shape[0]):
            for j in range(THRESH.shape[1]):

                temp = run_model(
                    sens_value=sens_est,
                    spec_value=spec_est,
                    p_cad_value=p_cad,
                    p_mvd_given_cad_value=p_mvd_given_cad,
                    lambda_value=THRESH[i, j],
                    cabg_cost_value=CABG[i, j]
                )

                Z_thresh_cabg[i, j] = temp["delta_ang_est"]

        plot_contour_from_grid(
            THRESH,
            CABG,
            Z_thresh_cabg,
            "Two-way sensitivity analysis: Threshold and CABG cost",
            "Threshold (£/QALY)",
            "CABG cost (£)",
            "ΔNMB (£)"
        )

        plot_slices(
            threshold_vals,
            cabg_vals,
            Z_thresh_cabg,
            selected_y=[1000, 3000, 5000],
            xlabel="Threshold (£/QALY)",
            ylabel="ΔNMB (£)",
            title="Effect of threshold at selected CABG costs",
            label_name="CABG cost £"
        )

# =========================
# TAB 5
# =========================

with tab5:
    st.subheader("Plain-English Interpretation")

    st.write(
        f"""
        Out of **{cohort_size:,}** patients:

        - **{round(model["nd"]):,}** have no disease (ND).
        - **{round(model["svd"]):,}** have single-vessel disease (SVD).
        - **{round(model["mvd"]):,}** have multi-vessel disease (MVD).

        With EST sensitivity of **{sens_est:.0%}**, the model correctly identifies:

        - **{round(model["tp_svd"]):,}** SVD patients.
        - **{round(model["tp_mvd"]):,}** MVD patients.

        However, it misses:

        - **{round(model["fn_svd"]):,}** SVD patients.
        - **{round(model["fn_mvd"]):,}** MVD patients.

        With EST specificity of **{spec_est:.0%}**, the model correctly classifies 
        **{round(model["tn_nd"]):,}** no-disease patients as negative, but falsely classifies 
        **{round(model["fp_nd"]):,}** no-disease patients as positive.

        Among detected patients, the model allocates:

        - **{p_cabg_svd:.0%}** of detected SVD patients to CABG.
        - **{p_cabg_mvd:.0%}** of detected MVD patients to CABG.

        Remaining detected patients receive medical management.

        At a willingness-to-pay threshold of **£{Threshold:,.0f} per QALY**, 
        the strategy with the highest net monetary benefit is currently:

        ## {best_full_tree_strategy}

        The sensitivity analysis figures show how this conclusion changes across:
        - willingness-to-pay thresholds,
        - CABG costs,
        - disease prevalence,
        - EST sensitivity,
        - and EST specificity.

        Positive ΔNMB values favour ANG over EST, while negative values favour EST over ANG. 
        The black contour line represents the decision boundary where ΔNMB = 0.
        """
    )

    # =========================
# TAB 6
# =========================

with tab6:
    st.subheader("Model Assumptions")

    st.markdown(
        """
        ### Structural Assumptions

        - EST is an imperfect diagnostic test with user-defined sensitivity and specificity.
        - ANG is assumed to perfectly identify disease status.
        - Disease severity is divided into:
            - No disease (ND)
            - Single-vessel disease (SVD)
            - Multi-vessel disease (MVD)

        ### Treatment Assumptions

        - Detected SVD and MVD patients may receive:
            - CABG
            - Medical management (MM)

        - Treatment allocation probabilities are user-defined.
        - False-negative EST patients are assumed to remain undetected and receive lower-QALY outcomes.
        - False-positive EST patients undergo angiography but receive no disease-related QALY benefit.

        ### Economic Assumptions

        - Costs and QALYs are represented as expected average values.
        - Net monetary benefit (NMB) is calculated as:

            NMB = (Threshold × QALYs) − Cost

        - The strategy with the highest NMB is considered cost-effective.

        ### Sensitivity Analysis

        - The app currently performs deterministic sensitivity analysis only.
        - Two-way sensitivity analysis evaluates how ΔNMB changes across parameter ranges.
        - Positive ΔNMB values favour ANG over EST.
        - Negative ΔNMB values favour EST over ANG.

        ### Limitations

        - The model does not currently include:
            - Probabilistic sensitivity analysis (PSA)
            - Parameter distributions
            - Time-varying Markov transitions
            - Adverse events
            - Long-term survival modelling
            - Half-cycle correction
            - Discounting over multiple periods
        """
    )