import streamlit as st
import math
import random

st.set_page_config(page_title="BMI & Health Calculators", layout="wide")

# --- Styles ---
PAGE_CSS = """
<style>
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #f7fcfb 0%, #f0fbff 100%);
}
.card {
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 6px 18px rgba(23, 162, 184, 0.08);
    background: white;
}
.small-muted { color: #6c757d; font-size: 0.9rem; }
</style>
"""

st.markdown(PAGE_CSS, unsafe_allow_html=True)

HEALTH_TIPS = [
    "Drink 8 glasses of water daily 💧",
    "Get at least 7 hours of sleep 🛌",
    "Stretch for 5 minutes every hour 🧘",
    "Aim for 150 minutes of moderate exercise per week 🏃",
    "Include vegetables and protein with every meal 🥗",
    "Walk for 30 minutes after lunch if possible 🚶",
]

# --- Utility functions ---

def cm_to_feet_inches(cm: float):
    inches = cm / 2.54
    feet = int(inches // 12)
    rem_in = inches - (feet * 12)
    return feet, rem_in


def feet_inches_to_cm(feet: int, inches: float):
    total_inches = feet * 12 + inches
    return total_inches * 2.54


# BMI

def calculate_bmi(weight_kg, height_cm):
    if height_cm <= 0:
        return None
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def bmi_category(bmi):
    if bmi is None:
        return "Invalid"
    if bmi < 18.5:
        return "Underweight"
    if 18.5 <= bmi < 25:
        return "Normal"
    if 25 <= bmi < 30:
        return "Overweight"
    return "Obese"


# BMR (Mifflin-St Jeor)

def calculate_bmr(gender, age, weight_kg, height_cm):
    if gender.lower() in ["male", "m"]:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return round(bmr, 0)

ACTIVITY_MULTIPLIERS = {
    "Sedentary (little or no exercise)": 1.2,
    "Light (1-3 days/week)": 1.375,
    "Moderate (3-5 days/week)": 1.55,
    "Active (6-7 days/week)": 1.725,
    "Very Active (hard exercise or physical job)": 1.9,
}


# Body Fat (Navy method approximation)

def body_fat_navy(gender, waist_cm, neck_cm, height_cm, hip_cm=None):
    # All inputs in cm
    try:
        if gender.lower() in ["male", "m"]:
            # % body fat = 495 / (1.0324 - 0.19077*log10(waist-neck) + 0.15456*log10(height)) - 450
            val = 1.0324 - 0.19077 * math.log10(waist_cm - neck_cm) + 0.15456 * math.log10(height_cm)
            bf = 495 / val - 450
        else:
            # % body fat = 495 / (1.29579 - 0.35004*log10(waist+hip-neck) + 0.22100*log10(height)) - 450
            val = 1.29579 - 0.35004 * math.log10(waist_cm + hip_cm - neck_cm) + 0.22100 * math.log10(height_cm)
            bf = 495 / val - 450
        return round(bf, 1)
    except Exception:
        return None


def bf_interpretation(gender, age, bf):
    # Very simple interpretation buckets (approx)
    if bf is None:
        return "Invalid data for estimation"
    if gender.lower() in ["male", "m"]:
        if bf < 6:
            return "Essential fat"
        if 6 <= bf < 14:
            return "Athlete"
        if 14 <= bf < 18:
            return "Fit"
        if 18 <= bf < 25:
            return "Average"
        return "Obese"
    else:
        if bf < 14:
            return "Essential fat"
        if 14 <= bf < 21:
            return "Athlete"
        if 21 <= bf < 25:
            return "Fit"
        if 25 <= bf < 32:
            return "Average"
        return "Obese"


# Ideal weight (Devine and Hamwi)

def ideal_weight_devine(gender, height_cm):
    # Devine formula works by inches over 5'0"
    height_in = height_cm / 2.54
    if gender.lower() in ["male", "m"]:
        base = 50.0  # kg for 152.4 cm (5 ft)
    else:
        base = 45.5
    extra_inches = max(0, height_in - 60)  # inches over 5'0"
    ideal = base + 2.3 * extra_inches
    return round(ideal, 1)


def ideal_weight_hamwi(gender, height_cm):
    height_in = height_cm / 2.54
    if gender.lower() in ["male", "m"]:
        base = 48.0
        per_inch = 2.7
    else:
        base = 45.5
        per_inch = 2.3
    extra_inches = max(0, height_in - 60)
    ideal = base + per_inch * extra_inches
    return round(ideal, 1)


# --- App UI ---

st.title("🏥 BMI & Health Calculators")
st.write("Simple, clear health calculators — no API keys, just local formulas.")

# Sidebar: random tip and theme toggle
with st.sidebar:
    st.header("Quick Actions")
    if st.button("Show a health tip 🌟"):
        st.info(random.choice(HEALTH_TIPS))
    theme_dark = st.checkbox("Dark mode (simple)")

# Small theme switch using CSS override (simple)
if theme_dark:
    st.markdown("<style> .stApp { background: linear-gradient(180deg, #0f1724 0%, #071124 100%); color: #e6eef8; } .card{ background:#0b1220; color:#e6eef8; box-shadow:none; } </style>", unsafe_allow_html=True)

# Tabs for calculators
tabs = st.tabs(["BMI 🧮", "BMR 🔥", "Body Fat % 📊", "Ideal Weight ⚖️", "Health Tips 💡"])

# ---------- BMI Tab ----------
with tabs[0]:
    st.subheader("Body Mass Index (BMI)")
    col1, col2 = st.columns([1, 1])
    with col1:
        unit_choice = st.radio("Height unit:", ("cm", "ft/in"), horizontal=True)
        if unit_choice == "cm":
            height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=300.0, value=170.0)
        else:
            feet = st.number_input("Feet", min_value=3, max_value=8, value=5)
            inches = st.number_input("Inches", min_value=0.0, max_value=11.99, value=7.0)
            height_cm = feet_inches_to_cm(int(feet), float(inches))
    with col2:
        w_unit = st.radio("Weight unit:", ("kg", "lbs"), horizontal=True)
        if w_unit == "kg":
            weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=400.0, value=70.0)
        else:
            weight_lbs = st.number_input("Weight (lbs)", min_value=44.0, max_value=900.0, value=154.0)
            weight_kg = weight_lbs * 0.45359237

    if st.button("Calculate BMI"):
        bmi = calculate_bmi(weight_kg, height_cm)
        if bmi is None:
            st.error("Please enter valid height and weight.")
        else:
            cat = bmi_category(bmi)
            st.success(f"Your BMI is {bmi} — {cat}")
            if cat == "Normal":
                st.info("Great — keep a balanced diet and regular activity! 🥦🏃")
            elif cat == "Underweight":
                st.warning("You are underweight. Consider increasing calorie intake and strength training.")
            else:
                st.warning("Work on a mix of cardio and strength training; watch portion sizes.")

# ---------- BMR Tab ----------
with tabs[1]:
    st.subheader("Basal Metabolic Rate (BMR)")
    c1, c2 = st.columns(2)
    with c1:
        sex = st.selectbox("Gender:", ("Male", "Female"))
        age = st.number_input("Age (years)", min_value=10, max_value=120, value=30)
        height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0)
    with c2:
        weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0)
        activity = st.selectbox("Activity level:", list(ACTIVITY_MULTIPLIERS.keys()))

    if st.button("Calculate BMR"):
        bmr = calculate_bmr(sex, age, weight_kg, height_cm)
        tdee = round(bmr * ACTIVITY_MULTIPLIERS[activity], 0)
        st.success(f"Estimated BMR: {int(bmr)} kcal/day")
        st.info(f"To maintain your weight with your activity level you need ≈ {int(tdee)} kcal/day.")

# ---------- Body Fat Tab ----------
with tabs[2]:
    st.subheader("Body Fat Percentage (Navy Method approximation)")
    g1, g2 = st.columns(2)
    with g1:
        sex = st.selectbox("Gender:", ("Male", "Female"), key="bf_gender")
        height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, key="bf_h")
        neck_cm = st.number_input("Neck circumference (cm)", min_value=20.0, max_value=60.0, value=37.0)
    with g2:
        waist_cm = st.number_input("Waist circumference (cm)", min_value=40.0, max_value=200.0, value=80.0)
        hip_cm = None
        if sex.lower() in ["female", "f"]:
            hip_cm = st.number_input("Hip circumference (cm)", min_value=60.0, max_value=200.0, value=95.0)

    if st.button("Estimate Body Fat %"):
        bf = body_fat_navy(sex, waist_cm, neck_cm, height_cm, hip_cm)
        if bf is None:
            st.error("Invalid measurements — please check that waist > neck and inputs are realistic.")
        else:
            interp = bf_interpretation(sex, 0, bf)
            st.success(f"Estimated Body Fat: {bf}% — {interp}")

# ---------- Ideal Weight Tab ----------
with tabs[3]:
    st.subheader("Ideal Weight (Devine & Hamwi")
    col_a, col_b = st.columns(2)
    with col_a:
        sex = st.selectbox("Gender:", ("Male", "Female"), key="ideal_gender")
        height_cm = st.number_input("Height (cm)", min_value=120.0, max_value=250.0, value=170.0, key="ideal_h")
    with col_b:
        if st.button("Calculate Ideal Weight"):
            dev = ideal_weight_devine(sex, height_cm)
            ham = ideal_weight_hamwi(sex, height_cm)
            lower = round(min(dev, ham) * 0.95, 1)
            upper = round(max(dev, ham) * 1.05, 1)
            st.success(f"Devine: {dev} kg; Hamwi: {ham} kg")
            st.info(f"A reasonable ideal weight range: {lower} – {upper} kg")

# ---------- Health Tips Tab ----------
with tabs[4]:
    st.subheader("Health Tips Carousel")
    idx = st.session_state.get("tip_idx", 0)
    colx, coly, colz = st.columns([1, 4, 1])
    with colx:
        if st.button("Prev"):
            st.session_state["tip_idx"] = max(0, st.session_state.get("tip_idx", 0) - 1)
    with coly:
        tip_to_show = HEALTH_TIPS[st.session_state.get("tip_idx", 0) % len(HEALTH_TIPS)]
        st.info(tip_to_show)
    with colz:
        if st.button("Next"):
            st.session_state["tip_idx"] = st.session_state.get("tip_idx", 0) + 1

# Footer
st.markdown("---")
st.caption("Developed By Alizay Ahmed")


