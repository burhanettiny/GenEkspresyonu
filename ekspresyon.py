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
data = []
stats_data = []

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
    
    if len(control_target_ct_values) < 2 or len(control_reference_ct_values) < 2:
        st.error(f"⚠️ Hata: Kontrol Grubu {i+1} için yeterli veri yok! Lütfen en az iki değer girin.")
        continue
    
    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_delta_ct = control_target_ct_values[:min_control_len] - control_reference_ct_values[:min_control_len]
    average_control_delta_ct = np.mean(control_delta_ct)

    for j in range(num_patient_groups):
        st.subheader(f"🩸 Hasta Grubu {j+1}")
        
        sample_target_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}_{j}")
        
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)
        
        if len(sample_target_ct_values) < 2 or len(sample_reference_ct_values) < 2:
            st.error(f"⚠️ Hata: Hasta Grubu {j+1} için yeterli veri yok! Lütfen en az iki değer girin.")
            continue
        
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_delta_ct = sample_target_ct_values[:min_sample_len] - sample_reference_ct_values[:min_sample_len]
        average_sample_delta_ct = np.mean(sample_delta_ct)

        delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)
        
        regulation_status = "Değişim Yok" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")
        
        if len(control_delta_ct) < 2 or len(sample_delta_ct) < 2:
            test_pvalue = np.nan
            significance = "Geçersiz"
        else:
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

# Sonuçları göster
if data:
    st.subheader("📊 Sonuçlar")
    df_results = pd.DataFrame(data)
    st.dataframe(df_results)
    
    # Grafik oluştur
    fig = go.Figure()
    for gene in df_results["Hedef Gen"].unique():
        gene_data = df_results[df_results["Hedef Gen"] == gene]
        fig.add_trace(go.Bar(x=gene_data["Hasta Grubu"], y=gene_data["Gen Ekspresyon Değişimi (2^(-ΔΔCt))"], name=gene))
    
    fig.update_layout(title="Gen Ekspresyon Değişimi", xaxis_title="Hasta Grubu", yaxis_title="Ekspresyon Değişimi", barmode='group')
    st.plotly_chart(fig)
    
    # PDF çıktısı
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.drawString(100, 750, "Gen Ekspresyon Analizi Sonuçları")
    y_position = 720
    for row in data:
        pdf.drawString(100, y_position, f"{row['Hedef Gen']} - {row['Hasta Grubu']}: {row['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']:.4f} ({row['Regülasyon Durumu']})")
        y_position -= 20
    pdf.save()
    pdf_buffer.seek(0)
    st.download_button("📄 Sonuçları PDF olarak indir", pdf_buffer, "gen_ekspresyon_sonuclari.pdf", "application/pdf")
