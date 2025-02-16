import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import scipy.stats as stats
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, PageBreak

# Dil Seçimi
lang = st.sidebar.radio("🌐 Select Language / Dil Seçin", ["English", "Türkçe"])

# Metinler
texts = {
    "title": {"English": "🧬 Gene Expression Analysis Application", "Türkçe": "🧬 Gen Ekspresyon Analizi Uygulaması"},
    "developer": {"English": "Developed by B. Yalçınkaya", "Türkçe": "B. Yalçınkaya tarafından geliştirildi"},
    "enter_data": {"English": "📊 Enter Patient and Control Group Data", "Türkçe": "📊 Hasta ve Kontrol Grubu Verisi Girin"},
    "target_gene_count": {"English": "🔹 Enter Target Gene Count", "Türkçe": "🔹 Hedef Gen Sayısını Girin"},
    "patient_group_count": {"English": "🔹 Enter Patient Group Count", "Türkçe": "🔹 Hasta Grubu Sayısını Girin"},
}

# Başlık
st.title(texts["title"][lang])
st.markdown(f"### {texts['developer'][lang]}")

# Kullanıcıdan giriş al
st.header(texts["enter_data"][lang])

# Hedef Gen ve Hasta Grubu Sayısı
num_target_genes = st.number_input(texts["target_gene_count"][lang], min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(texts["patient_group_count"][lang], min_value=1, step=1, key="patient_count")

# Veri listeleri
input_values_table = []
data = []
stats_data = []

def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])
for i in range(num_target_genes):
    st.subheader(f"🧬 Target Gene {i+1}" if lang == "English" else f"🧬 Hedef Gen {i+1}")
    
    # Kontrol Grubu Verileri
    control_target_ct = st.text_area(f"🟦 Control Group Target Gene {i+1} Ct Values" if lang == "English" else f"🟦 Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"🟦 Control Group Reference Gene {i+1} Ct Values" if lang == "English" else f"🟦 Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error("⚠️ Please enter valid control group data!" if lang == "English" else "⚠️ Lütfen geçerli kontrol grubu verilerini girin!")
        continue
    
    control_delta_ct = control_target_ct_values - control_reference_ct_values
    avg_control_delta_ct = np.mean(control_delta_ct)

    # Hasta Grubu Verileri
    for j in range(num_patient_groups):
        st.subheader(f"🩸 Patient Group {j+1} - Target Gene {i+1}" if lang == "English" else f"🩸 Hasta Grubu {j+1} - Hedef Gen {i+1}")

        sample_target_ct = st.text_area(f"🟥 Patient Group {j+1} Target Gene {i+1} Ct Values" if lang == "English" else f"🟥 Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"🟥 Patient Group {j+1} Reference Gene {i+1} Ct Values" if lang == "English" else f"🟥 Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}_{j}")

        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)

        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error("⚠️ Please enter valid patient group data!" if lang == "English" else "⚠️ Lütfen geçerli hasta grubu verilerini girin!")
            continue

        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        avg_sample_delta_ct = np.mean(sample_delta_ct)

        delta_delta_ct = avg_sample_delta_ct - avg_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)

        regulation_status = (
            "No Change" if expression_change == 1 else
            ("Upregulated" if expression_change > 1 else "Downregulated")
        ) if lang == "English" else (
            "Değişim Yok" if expression_change == 1 else
            ("Upregüle" if expression_change > 1 else "Downregüle")
        )
        # İstatistiksel Testler
        shapiro_control = stats.shapiro(control_delta_ct)
        shapiro_sample = stats.shapiro(sample_delta_ct)
        levene_test = stats.levene(control_delta_ct, sample_delta_ct)

        test_type = "Parametric" if lang == "English" else "Parametrik"
        test_method = "t-test" if lang == "English" else "t-testi"

        if shapiro_control.pvalue < 0.05 or shapiro_sample.pvalue < 0.05:
            test_type = "Nonparametric" if lang == "English" else "Nonparametrik"
            test_method = "Mann-Whitney U Test" if lang == "English" else "Mann-Whitney U Testi"

        test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue if test_type == "Parametric" else stats.mannwhitneyu(control_delta_ct, sample_delta_ct).pvalue

        significance = "Significant" if test_pvalue < 0.05 else "Not Significant"
        significance = "Anlamlı" if lang == "Türkçe" else significance

        stats_data.append({
            "Target Gene": f"Target Gene {i+1}" if lang == "English" else f"Hedef Gen {i+1}",
            "Patient Group": f"Patient Group {j+1}" if lang == "English" else f"Hasta Grubu {j+1}",
            "Test Type": test_type,
            "Used Test": test_method,
            "Test P-value": test_pvalue,
            "Significance": significance
        })
if stats_data:
    st.subheader("📈 Statistical Results" if lang == "English" else "📈 İstatistik Sonuçları")
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
