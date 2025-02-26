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
from reportlab.platypus import Table, TableStyle

# Dil seçim kutusu
if 'language' not in st.session_state:
    st.session_state.language = "Türkçe"  # Varsayılan dil Türkçe olarak ayarlanıyor.

st.session_state.language = st.selectbox("Dil / Language / Sprache", ["Türkçe", "English", "Deutsch"])

# Dil kodlarını belirleyin
language_map = {
    "Türkçe": "tr",
    "English": "en",
    "Deutsch": "de"
}

# Seçilen dilin kodu
language_code = language_map[st.session_state.language]

# Çevirileri tanımlayın
translations = {
    "tr": {
        "title": "🧬 Gen Ekspresyon Analizi Uygulaması",
        "subtitle": "B. Yalçınkaya tarafından geliştirildi",
        "patient_data_header": "📊 Hasta ve Kontrol Grubu Verisi Girin",
        "num_target_genes": "🔹 Hedef Gen Sayısını Girin",
        "num_patient_groups": "🔹 Hasta Grubu Sayısını Girin",
        "sample_number": "Örnek Numarası",
        "group": "Grup",
        "gene_ct_value": "Hedef Gen Ct Değeri",
        "reference_ct": "Referans Ct",
        "delta_ct": "ΔCt (Kontrol)",
        "delta_cth": "ΔCt (Hasta)",
        "warning_empty_input": "⚠️ Dikkat: Verileri alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.",
        "statistical_results": "📈 İstatistik Sonuçları",
        "hfg": "Hedef Gen",
        "rfg": "Referans Gen",
        "ctd": "Ct Değerleri",
        "download_csv": "📥 CSV İndir",
        "results": "📊 Sonuçlar",
        "statistics": "📈 İstatistik Sonuçları",
        "group_patient": "Hasta Grubu",
        "group_control": "Kontrol Grubu",
    },
    "en": {
        "title": "🧬 Gene Expression Analysis Application",
        "subtitle": "Developed by B. Yalçınkaya",
        "patient_data_header": "📊 Enter Patient and Control Group Data",
        "num_target_genes": "🔹 Enter the Number of Target Genes",
        "num_patient_groups": "🔹 Enter the Number of Patient Groups",
        "sample_number": "Sample Number",
        "group": "Group",
        "gene_ct_value": "Target Gene Ct Value",
        "reference_ct": "Reference Ct",
        "delta_ct": "ΔCt (Control)",
        "delta_cth": "ΔCt (Patient)",
        "warning_empty_input": "⚠️ Warning: Write data one below the other or copy-paste without empty cells from Excel.",
        "statistical_results": "📈 Statistical Results",
        "hfg": "Target Gene",
        "rfg": "Reference Gen",
        "ctd": "Ct values",
        "download_csv": "📥 Download CSV",
        "results": "📊 Results",
        "statistics": "📈 Statistical Results",
        "group_patient": "Patient Group",
        "group_control": "Control Group",
    },
    "de": {
        "title": "🧬 Genexpression-Analyseanwendung",
        "subtitle": "Entwickelt von B. Yalçınkaya",
        "patient_data_header": "📊 Geben Sie Patientendaten und Kontrollgruppen ein",
        "num_target_genes": "🔹 Geben Sie die Anzahl der Zielgene ein",
        "num_patient_groups": "🔹 Geben Sie die Anzahl der Patientengruppen ein",
        "sample_number": "Beispielnummer",
        "group": "Gruppe",
        "gene_ct_value": "Zielgen Ct-Wert",
        "reference_ct": "Referenz Ct",
        "delta_ct": "ΔCt (Kontrolle)",
        "delta_cth": "ΔCt (Patientendaten)",
        "warning_empty_input": "⚠️ Warnung: Geben Sie die Daten untereinander ein oder kopieren Sie sie ohne leere Zellen aus Excel.",
        "statistical_results": "📈 Statistische Ergebnisse",
        "hfg": "Zielgen",
        "rfg": "Referenzgen",
        "ctd": "Ct Werte",
        "download_csv": "📥 CSV Herunterladen",
        "results": "📊 Ergebnisse",
        "statistics": "📈 Statistische Ergebnisse",
        "group_patient": "Patientengruppe",
        "group_control": "Kontrollgruppe",
    }
}

# Başlık
st.title(translations[language_code]["title"])
st.markdown(f"### {translations[language_code]['subtitle']}")

# Kullanıcıdan giriş al
st.header(translations[language_code]["patient_data_header"])

# Hedef Gen ve Hasta Grubu Sayısı
num_target_genes = st.number_input(translations[language_code]["num_target_genes"], min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(translations[language_code]["num_patient_groups"], min_value=1, step=1, key="patient_count")

# Veri listeleri
input_values_table = []
data = []
stats_data = []

def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# Grafik için son işlenen Hedef Genın kontrol verilerini saklamak amacıyla değişkenler
last_control_delta_ct = None
last_gene_index = None

for i in range(num_target_genes):
    st.subheader(f"🧬 {translations[language_code]['hfg']} {i+1}")

    # Kontrol Grubu Verileri
    control_target_ct = st.text_area(f"🟦 {translations[language_code]['hfg']} {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"🟦 {translations[language_code]['rfg']} {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")

    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(translations[language_code]["warning_empty_input"])
        continue

    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_target_ct_values = control_target_ct_values[:min_control_len]
    control_reference_ct_values = control_reference_ct_values[:min_control_len]
    control_delta_ct = control_target_ct_values - control_reference_ct_values

    if len(control_delta_ct) > 0:
        average_control_delta_ct = np.mean(control_delta_ct)
        last_control_delta_ct = control_delta_ct
        last_gene_index = i
    else:
        st.warning(translations[language_code]["warning_empty_input"])
        continue

    sample_counter = 1  # Kontrol grubu örnek sayacı
    for idx in range(min_control_len):
        input_values_table.append({
            "Örnek Numarası": sample_counter,
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Grup": translations[language_code]["group_control"],
            "Hedef Gen Ct Değeri": control_target_ct_values[idx],
            "Referans Ct": control_reference_ct_values[idx], 
            "ΔCt (Kontrol)": control_delta_ct[idx]
        })
        sample_counter += 1

    # Hasta Grubu Verileri
    for j in range(num_patient_groups):
        st.subheader(f"🩸 {translations[language_code]['group_patient']} {j+1} - {translations[language_code]['hfg']} {i+1}")

        sample_target_ct = st.text_area(f"🟥 {translations[language_code]['group_patient']} {j+1} {translations[language_code]['hfg']} {i+1} Ct Değerleri", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"🟥 {translations[language_code]['group_patient']} {j+1} {translations[language_code]['rfg']} {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}_{j}")

        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)

        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(translations[language_code]["warning_empty_input"])
            continue

        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values

        if len(sample_delta_ct) > 0:
            average_sample_delta_ct = np.mean(sample_delta_ct)
        else:
            st.warning(translations[language_code]["warning_empty_input"])
            continue

        sample_counter = 1  # Her Hasta Grubu için ör
        # Her Hasta Grubu için örnek sayacı
        for idx in range(min_sample_len):
            input_values_table.append({
                "Örnek Numarası": sample_counter,
                "Hedef Gen": f"Hedef Gen {i + 1}",
                "Grup": translations[language_code]["group_patient"],
                "Hedef Gen Ct Değeri": sample_target_ct_values[idx],
                "Referans Ct": sample_reference_ct_values[idx],
                "ΔCt (Hasta)": sample_delta_ct[idx]
            })
            sample_counter += 1

# Giriş verilerini tabloya dönüştür
data = pd.DataFrame(input_values_table)

# İstatistiksel analiz ve sonuçları hesaplayın
if len(data) > 0:
    # Örnek sayısını ve grup bilgilerini al
    control_data = data[data["Grup"] == translations[language_code]["group_control"]]
    patient_data = data[data["Grup"] == translations[language_code]["group_patient"]]

    # Örnekleme ve istatistiksel analiz yapılacak yer
    # Burada istatistiksel testler ve analizleri gerçekleştirin
    st.subheader(translations[language_code]["statistical_results"])

    # Örnek başına ortalamaları hesaplayın
    control_avg = control_data["ΔCt (Kontrol)"].mean()
    patient_avg = patient_data["ΔCt (Hasta)"].mean()

    st.write(f"{translations[language_code]['group_control']} Ortalama ΔCt: {control_avg:.2f}")
    st.write(f"{translations[language_code]['group_patient']} Ortalama ΔCt: {patient_avg:.2f}")

    # Sonuçları görselleştirin
    fig = plt.figure(figsize=(10, 5))
    plt.bar([translations[language_code]["group_control"], translations[language_code]["group_patient"]],
            [control_avg, patient_avg], color=['blue', 'orange'])
    plt.title(translations[language_code]["statistical_results"])
    plt.ylabel("Ortalama ΔCt Değeri")
    plt.xlabel(translations[language_code]["group"])
    st.pyplot(fig)

    # CSV indirme seçeneği
    if st.button(translations[language_code]["download_csv"]):
        csv = data.to_csv(index=False)
        st.download_button(label=translations[language_code]["download_csv"], data=csv, file_name='gen_expression_data.csv')

# Uygulama sonu
st.success("İşlemler tamamlandı!")
