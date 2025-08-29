import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="All-in-One Engineering App",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- EXPORT HELPERS ---
def export_csv(data_dict, filename="results.csv"):
    df = pd.DataFrame([data_dict])
    return df.to_csv(index=False).encode("utf-8")

def export_pdf(data_dict, filename="results.pdf", title="Exported Results"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=title, ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    for k, v in data_dict.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- STANDARD CONVERTER ---
def render_standard_converter():
    st.header("🔢 Standard Converter")
    value = st.number_input("Enter a value", value=1.0)
    unit = st.selectbox("Choose conversion", ["Meters → Kilometers", "Kilograms → Grams"])
    
    if unit == "Meters → Kilometers":
        result = value / 1000
        st.success(f"{value} meters = {result} km")
    elif unit == "Kilograms → Grams":
        result = value * 1000
        st.success(f"{value} kg = {result} g")

# --- TEMPERATURE CONVERTER ---
def render_temperature_converter():
    st.header("🌡️ Temperature Converter")
    temp = st.number_input("Enter temperature", value=0.0)
    unit = st.selectbox("Select conversion", ["Celsius → Fahrenheit", "Fahrenheit → Celsius"])
    
    if unit == "Celsius → Fahrenheit":
        result = (temp * 9/5) + 32
        st.success(f"{temp} °C = {result:.2f} °F")
    elif unit == "Fahrenheit → Celsius":
        result = (temp - 32) * 5/9
        st.success(f"{temp} °F = {result:.2f} °C")

# --- BMI CALCULATOR ---
def render_bmi_calculator():
    st.header("⚕️ BMI Calculator")
    weight = st.number_input("Weight (kg)", value=70.0)
    height = st.number_input("Height (m)", value=1.75)
    
    if height > 0:
        bmi = weight / (height ** 2)
        st.success(f"Your BMI is {bmi:.2f}")

# --- ADVANCED PER-UNIT CALCULATOR ---
def render_enhanced_per_unit():
    st.header("⚡ Advanced Per-Unit (PU) System Calculator")
    st.info("Supports Resistance, Reactance, Susceptance per km with line length")

    base_mva = st.number_input("Base MVA", value=100.0, min_value=0.1)
    base_kv = st.number_input("Base kV (L-L)", value=13.8, min_value=0.1)
    length = st.number_input("Line Length (km)", value=10.0, min_value=0.0)

    Z_base = (base_kv ** 2) / base_mva
    Y_base = 1 / Z_base

    with st.expander("Input Parameters per km"):
        R_per = st.number_input("Resistance per km (Ω/km)", value=0.1)
        X_per = st.number_input("Reactance per km (Ω/km)", value=0.3)
        B_per = st.number_input("Susceptance per km (S/km)", value=0.0002)

    R_total, X_total, B_total = R_per*length, X_per*length, B_per*length
    R_pu, X_pu, B_pu = R_total/Z_base, X_total/Z_base, B_total/Y_base

    st.success(f"Per Unit Values → R = {R_pu:.6f} pu, X = {X_pu:.6f} pu, B = {B_pu:.6f} pu")

    # --- EXPORT OPTIONS ---
    results = {
        "Base MVA": base_mva,
        "Base kV": base_kv,
        "Length (km)": length,
        "R_total (Ω)": round(R_total, 6),
        "X_total (Ω)": round(X_total, 6),
        "B_total (S)": round(B_total, 6),
        "R_pu": round(R_pu, 6),
        "X_pu": round(X_pu, 6),
        "B_pu": round(B_pu, 6)
    }

    csv_data = export_csv(results)
    pdf_data = export_pdf(results, title="Advanced PU Results")

    st.download_button("⬇️ Download as CSV", csv_data, "pu_results.csv", "text/csv")
    st.download_button("⬇️ Download as PDF", pdf_data, "pu_results.pdf", "application/pdf")

# --- ZIP LOAD MODEL ---
def render_zip_load_model():
    st.header("🏠 ZIP Load Model Calculator")
    st.info("Models load as a combination of constant impedance (Z), current (I), and power (P)")

    P0 = st.number_input("Base Real Power P0 (MW)", value=100.0)
    Q0 = st.number_input("Base Reactive Power Q0 (MVAr)", value=50.0)
    V0 = st.number_input("Base Voltage (p.u.)", value=1.0)

    a = st.slider("a (Z proportion)", 0.0, 1.0, 0.5)
    b = st.slider("b (I proportion)", 0.0, 1.0, 0.3)
    c = 1 - a - b
    d = st.slider("d (Reactive Z proportion)", 0.0, 1.0, 0.5)
    e = st.slider("e (Reactive I proportion)", 0.0, 1.0, 0.3)
    f = 1 - d - e

    V = st.slider("Operating Voltage (p.u.)", 0.5, 1.5, 1.0, 0.01)
    P = P0 * (a*(V/V0)**2 + b*(V/V0) + c)
    Q = Q0 * (d*(V/V0)**2 + e*(V/V0) + f)

    st.success(f"At V={V:.2f} pu → P = {P:.2f} MW, Q = {Q:.2f} MVAr")

    # --- Generate Curve ---
    Vs = np.linspace(0.5, 1.5, 200)
    Pcurve = P0 * (a*(Vs/V0)**2 + b*(Vs/V0) + c)
    Qcurve = Q0 * (d*(Vs/V0)**2 + e*(Vs/V0) + f)

    fig, ax = plt.subplots()
    ax.plot(Vs, Pcurve, label="P(V)", color="blue")
    ax.plot(Vs, Qcurve, label="Q(V)", color="green")
    ax.axvline(V, color='r', linestyle='--', label="Operating V")
    ax.set_xlabel("Voltage (p.u.)")
    ax.set_ylabel("Power (MW / MVAr)")
    ax.legend()
    st.pyplot(fig)

    # --- EXPORT NUMERIC RESULTS ---
    results = {
        "P0 (MW)": P0, "Q0 (MVAr)": Q0,
        "Operating V (p.u.)": V,
        "P (MW)": round(P, 4),
        "Q (MVAr)": round(Q, 4),
        "Coeffs a,b,c": f"{a:.2f}, {b:.2f}, {c:.2f}",
        "Coeffs d,e,f": f"{d:.2f}, {e:.2f}, {f:.2f}"
    }

    csv_data = export_csv(results)
    pdf_data = export_pdf(results, title="ZIP Load Model Results")

    st.download_button("⬇️ Download Results as CSV", csv_data, "zip_results.csv", "text/csv")
    st.download_button("⬇️ Download Results as PDF", pdf_data, "zip_results.pdf", "application/pdf")

    # --- EXPORT PLOT ---
    buf_png = BytesIO()
    fig.savefig(buf_png, format="png")
    buf_png.seek(0)

    buf_pdf = BytesIO()
    fig.savefig(buf_pdf, format="pdf")
    buf_pdf.seek(0)

    st.download_button("🖼️ Download Plot as PNG", buf_png, "zip_curve.png", "image/png")
    st.download_button("📑 Download Plot as PDF", buf_pdf, "zip_curve.pdf", "application/pdf")

# --- MAIN APP NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Standard Converter",
        "Temperature Converter",
        "BMI Calculator",
        "Advanced Per-Unit Calculator",
        "ZIP Load Model"
    ]
)

if page == "Standard Converter":
    render_standard_converter()
elif page == "Temperature Converter":
    render_temperature_converter()
elif page == "BMI Calculator":
    render_bmi_calculator()
elif page == "Advanced Per-Unit Calculator":
    render_enhanced_per_unit()
elif page == "ZIP Load Model":
    render_zip_load_model()
