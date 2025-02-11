import streamlit as st 
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import scipy.stats as stats
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

# PDF Oluşturma Fonksiyonu
def create_pdf(results, stats, input_df):
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
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position - 30, "Giriş Verileri Tablosu:")
    
    y_position -= 50
    input_data_str = input_df.to_string(index=False)
    for line in input_data_str.split("\n"):
        c.drawString(50, y_position, line)
        y_position -= 15
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    c.save()
    buffer.seek(0)
    return buffer

# PDF Raporu İndir Butonu
if st.button("📥 PDF Raporu İndir"):
    if input_values_table:
        pdf_buffer = create_pdf(data, stats_data, pd.DataFrame(input_values_table))
        st.download_button(label="PDF Olarak İndir", data=pdf_buffer, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
    else:
        st.error("PDF raporu oluşturmak için yeterli veri yok.")
