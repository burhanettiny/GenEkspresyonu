import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import scipy.stats as stats
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Başlık
st.title("🧬 Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

# Kullanıcıdan giriş al
st.header("📊 Hasta ve Kontrol Grubu Verisi Girin")

# Hedef Gen ve Hasta Grubu Sayısı
num_target_genes = st.number_input("🔹 Hedef Gen Sayısını Girin", min_value=1, step=1)
num_patient_groups = st.number_input("🔹 Hasta Grubu Sayısını Girin", min_value=1, step=1)

# Veri listeleri
input_values_table = []
data = []
stats_data = []
sample_counter = 1  # Örnek numaralandırması için sayaç

def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

for i in range(num_target_genes):
    st.subheader(f"🧬 Hedef Gen {i+1}")
    
    # Kontrol Grubu Verileri
    control_target_ct = st.text_area(f"🟦 Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"🟦 Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f"⚠️ Hata: Kontrol Grubu {i+1} için veriler eksik! Lütfen verileri doğru girin.")
        continue
    
    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_target_ct_values = control_target_ct_values[:min_control_len]
    control_reference_ct_values = control_reference_ct_values[:min_control_len]
    control_delta_ct = control_target_ct_values - control_reference_ct_values
    average_control_delta_ct = np.mean(control_delta_ct)

    for idx in range(min_control_len):
        input_values_table.append({
            "Örnek Numarası": sample_counter,
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Grup": "Kontrol",
            "Hedef Gen Ct Değeri": control_target_ct_values[idx],
            "Referans Ct": control_reference_ct_values[idx]
        })
        sample_counter += 1
    
    for j in range(num_patient_groups):
        st.subheader(f"🩸 Hasta Grubu {j+1}")
        
        sample_target_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}_{j}")
        
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)
        
        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(f"⚠️ Hata: Hasta Grubu {j+1} için veriler eksik! Lütfen verileri doğru girin.")
            continue
        
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        average_sample_delta_ct = np.mean(sample_delta_ct)

        for idx in range(min_sample_len):
            input_values_table.append({
                "Örnek Numarası": sample_counter,
                "Hedef Gen": f"Hedef Gen {i+1}",
                "Grup": f"Hasta Grubu {j+1}",
                "Hedef Gen Ct Değeri": sample_target_ct_values[idx],
                "Referans Ct": sample_reference_ct_values[idx]
            })
            sample_counter += 1
        
        delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)
        
        regulation_status = "Değişim Yok" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")
        
        test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue
        significance = "Anlamlı" if test_pvalue < 0.05 else "Anlamsız"
        
        stats_data.append({
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Hasta Grubu": f"Hasta Grubu {j+1}",
            "Test P-değeri": test_pvalue,
            "Anlamlılık": significance
        })
        
        data.append({
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Hasta Grubu": f"Hasta Grubu {j+1}",
            "ΔΔCt": delta_delta_ct,
            "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
            "Regülasyon Durumu": regulation_status
        })

# PDF OLUŞTURMA FONKSİYONU
def create_pdf(result_data, stats_data, input_df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "Gen Ekspresyon Analizi Raporu")
    
    y = height - 80

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "📊 Sonuçlar:")
    y -= 20

    for row in result_data:
        text = f"{row['Hedef Gen']} - {row['Hasta Grubu']} - ΔΔCt: {row['ΔΔCt']:.2f}, Ekspresyon Değişimi: {row['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']:.2f}"
        c.setFont("Helvetica", 10)
        c.drawString(100, y, text)
        y -= 15

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "📈 İstatistik Sonuçları:")
    y -= 20

    for row in stats_data:
        text = f"{row['Hedef Gen']} - {row['Hasta Grubu']} - P-Value: {row['Test P-değeri']:.4f} ({row['Anlamlılık']})"
        c.setFont("Helvetica", 10)
        c.drawString(100, y, text)
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

if st.button("📥 PDF Raporu İndir"):
    if input_values_table:
        pdf_buffer = create_pdf(data, stats_data, pd.DataFrame(input_values_table))
        st.download_button(label="PDF Olarak İndir", data=pdf_buffer, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
    else:
        st.error("PDF raporu oluşturmak için yeterli veri yok.")
