import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import scipy.stats as stats
import plotly.io as pio
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

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

    # Kontrol Grubu Verilerini Tabloya Ekleyin
    for idx in range(min_control_len):
        input_values_table.append({
            "Örnek Numarası": sample_counter,
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Grup": "Kontrol",
            "Hedef Gen Ct Değeri": control_target_ct_values[idx],
            "Referans Ct": control_reference_ct_values[idx]
        })
        sample_counter += 1
    
    # Hasta Grubu Verileri
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

        # Hasta Grubu Verilerini Tabloya Ekleyin
        for idx in range(min_sample_len):
            input_values_table.append({
                "Örnek Numarası": sample_counter,
                "Hedef Gen": f"Hedef Gen {i+1}",
                "Grup": f"Hasta Grubu {j+1}",
                "Hedef Gen Ct Değeri": sample_target_ct_values[idx],
                "Referans Ct": sample_reference_ct_values[idx]
            })
            sample_counter += 1
        
        # ΔΔCt ve Gen Ekspresyon Değişimi Hesaplama
        delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)
        
        regulation_status = "Değişim Yok" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")
        
        # İstatistiksel Testler
        shapiro_control = stats.shapiro(control_delta_ct)
        shapiro_sample = stats.shapiro(sample_delta_ct)
        levene_test = stats.levene(control_delta_ct, sample_delta_ct)
        
        control_normal = shapiro_control.pvalue > 0.05
        sample_normal = shapiro_sample.pvalue > 0.05
        equal_variance = levene_test.pvalue > 0.05
        
        test_type = "Parametrik" if control_normal and sample_normal and equal_variance else "Nonparametrik"
        
        if test_type == "Parametrik":
            test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue
            test_method = "t-test"
        else:
            test_pvalue = stats.mannwhitneyu(control_delta_ct, sample_delta_ct).pvalue
            test_method = "Mann-Whitney U testi"
        
        significance = "Anlamlı" if test_pvalue < 0.05 else "Anlamsız"
        
        stats_data.append({
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Hasta Grubu": f"Hasta Grubu {j+1}",
            "Test Türü": test_type,
            "Kullanılan Test": test_method,  
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

# Grafik oluşturma
fig = go.Figure()

# Kontrol grubu verilerini ekleme
fig.add_trace(go.Scatter(
    x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
    y=control_delta_ct,
    mode='markers',  # Kontrol grubu için
    name='Kontrol Grubu',
    marker=dict(color='blue'),
    text=[f'Kontrol {value:.2f}, Örnek {i+1}' for i, value in enumerate(control_delta_ct)],  # Tooltip metni
    hoverinfo='text'  # Tooltip gösterimi
))

# Hasta grubu verilerini ekleme
for j in range(num_patient_groups):
    fig.add_trace(go.Scatter(
        x=np.ones(len(sample_delta_ct)) * (j + 2) + np.random.uniform(-0.05, 0.05, len(sample_delta_ct)),
        y=sample_delta_ct,
        mode='markers',  # Hasta grubu için
        name=f'Hasta Grubu {j+1}',
        marker=dict(color='red'),
        text=[f'Hasta {value:.2f}, Örnek {i+1}' for i, value in enumerate(sample_delta_ct)],  # Tooltip metni
        hoverinfo='text'  # Tooltip gösterimi
    ))

# Grafik ayarları
fig.update_layout(
    title=f"Hedef Gen {i+1} - ΔCt Dağılımı",
    xaxis=dict(
        tickvals=[1] + [i + 2 for i in range(num_patient_groups)],
        ticktext=['Kontrol Grubu'] + [f'Hasta Grubu {i+1}' for i in range(num_patient_groups)],
        title='Grup'
    ),
    yaxis=dict(
        title='ΔCt Değeri'
    ),
    showlegend=True
)

# Grafik resmi olarak kaydetme
img_buffer = BytesIO()
pio.write_image(fig, img_buffer, format='png')
img_buffer.seek(0)

# PDF oluşturma fonksiyonu
def create_pdf(results, stats, input_df, img_buffer):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Gen Ekspresyon Analizi Raporu")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "Sonuçlar:")
    
    y_position = height - 100
    for result in results:
        text = f"{result['Hedef Gen']} - {result['Hasta Grubu']} | ΔΔCt: {result['ΔΔCt']:.2f} | 2^(-ΔΔCt): {result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']:.2f}"
        c.drawString(50, y_position, text)
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    # Grafik ekleme
    c.drawImage(img_buffer, 50, y_position - 100, width=500, height=300)
    y_position -= 320

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position - 30, "İstatistiksel Sonuçlar:")

    y_position -= 50
    for stat in stats:
        text = f"{stat['Hedef Gen']} - {stat['Hasta Grubu']} | Test: {stat['Kullanılan Test']} | p-değeri: {stat['Test P-değeri']:.4f} | {stat['Anlamlılık']}"
        c.drawString(50, y_position, text)
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    c.save()
    buffer.seek(0)
    return buffer

if st.button("📥 PDF Raporu İndir"):
    if input_values_table:
        pdf_buffer = create_pdf(data, stats_data, pd.DataFrame(input_values_table), img_buffer)
        st.download_button(label="PDF Olarak İndir", data=pdf_buffer, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
    else:
        st.error("Veri bulunamadı, PDF oluşturulamadı.")
