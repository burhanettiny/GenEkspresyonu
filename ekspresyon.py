import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import scipy.stats as stats
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import tempfile

# Plotly için PNG render ayarı
pio.renderers.default = "kaleido"

# 🧬 Uygulama Başlığı
st.title("🧬 Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

# Kullanıcıdan giriş al
num_target_genes = st.number_input("🔹 Hedef Gen Sayısını Girin", min_value=1, step=1)
num_patient_groups = st.number_input("🔹 Hasta Grubu Sayısını Girin", min_value=1, step=1)

# Global veri listeleri
input_values_table = []
data = []
stats_data = []
graphs = []
sample_counter = 1

# 📄 PDF oluşturma fonksiyonu
def create_pdf(data, stats_data, input_df, graphs):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "🧬 Gen Ekspresyon Analizi Sonuçları")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "B. Yalçınkaya tarafından geliştirildi")

    y_position = height - 100

    # 📋 Giriş Verileri
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📋 Giriş Verileri")
    y_position -= 20
    c.setFont("Helvetica", 8)
    for index, row in input_df.iterrows():
        text_line = f"Örnek {row['Örnek Numarası']} - {row['Grup']} - {row['Hedef Gen']} - Ct: {row['Hedef Gen Ct Değeri']} - Ref Ct: {row['Referans Ct']}"
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    # 📊 Sonuçlar
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📊 Sonuçlar")
    y_position -= 20
    for result in data:
        text_line = f"{result['Hedef Gen']} - {result['Hasta Grubu']} - ΔΔCt: {result['ΔΔCt']} - Exp: {result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']} - {result['Regülasyon Durumu']}"
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    # 📈 İstatistik Sonuçları
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📈 İstatistik Sonuçları")
    y_position -= 20
    for stat in stats_data:
        text_line = f"{stat['Hedef Gen']} - {stat['Hasta Grubu']} - {stat['Test Türü']} ({stat['Kullanılan Test']}) - p: {stat['Test P-değeri']:.4f} - {stat['Anlamlılık']}"
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    # 📊 Grafikleri PDF'ye ekleme
    for graph in graphs:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            tmpfile_path = tmpfile.name
        graph.write_image(tmpfile_path)  
        c.drawImage(tmpfile_path, 50, y_position - 400, width=500, height=400)
        y_position -= 450
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    c.save()
    buffer.seek(0)
    return buffer

# 📊 Verileri işleme
def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# 🔬 Gen ekspresyon analizleri
for i in range(num_target_genes):
    st.subheader(f"🧬 Hedef Gen {i+1}")

    # 📌 Kontrol Grubu Verileri
    control_target_ct = st.text_area(f"🟦 Kontrol Grubu Hedef Gen {i+1} Ct Değerleri")
    control_reference_ct = st.text_area(f"🟦 Kontrol Grubu Referans Gen {i+1} Ct Değerleri")

    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f"⚠️ Hata: Kontrol Grubu {i+1} için veriler eksik!")
        continue

    control_delta_ct = control_target_ct_values - control_reference_ct_values
    avg_control_delta_ct = np.mean(control_delta_ct)

    # 🩸 Hasta Grubu Verileri
    for j in range(num_patient_groups):
        st.subheader(f"🩸 Hasta Grubu {j+1} - Hedef Gen {i+1}")
        sample_target_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri")
        sample_reference_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri")

        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)

        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(f"⚠️ Hata: Hasta Grubu {j+1} için veriler eksik!")
            continue

        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        avg_sample_delta_ct = np.mean(sample_delta_ct)

        delta_delta_ct = avg_sample_delta_ct - avg_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)
        regulation_status = "Değişim Yok" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")

        # 📊 Grafik
        fig = go.Figure()
        fig.add_trace(go.Box(y=control_delta_ct, name="Kontrol", marker_color='blue'))
        fig.add_trace(go.Box(y=sample_delta_ct, name=f"Hasta {j+1}", marker_color='red'))
        fig.update_layout(title=f"Hedef Gen {i+1} - Hasta {j+1} ΔCt Dağılımı")

        st.plotly_chart(fig)
        graphs.append(fig)

# 📥 PDF oluşturma ve indirme butonu
if st.button("📥 Raporu İndir"):
    input_df = pd.DataFrame(input_values_table)
    pdf_buffer = create_pdf(data, stats_data, input_df, graphs)
    st.download_button(label="📄 PDF İndir", data=pdf_buffer, file_name="GenEkspresyonAnalizi.pdf", mime="application/pdf")
