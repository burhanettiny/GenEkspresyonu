import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import scipy.stats as stats
from fpdf import FPDF
import io
from PIL import Image

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

def create_pdf(results, stats_results, input_table, plot_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Gen Ekspresyon Analizi Raporu", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "📋 Giriş Verileri Tablosu", ln=True)
    pdf.ln(5)
    for i, row in input_table.iterrows():
        pdf.cell(0, 10, f"{row.to_string(index=False)}", ln=True)
    pdf.ln(5)

    pdf.cell(200, 10, "📊 Sonuçlar", ln=True)
    pdf.ln(5)
    for i, row in results.iterrows():
        pdf.cell(0, 10, f"{row.to_string(index=False)}", ln=True)
    pdf.ln(5)

    pdf.cell(200, 10, "📈 İstatistik Sonuçları", ln=True)
    pdf.ln(5)
    for i, row in stats_results.iterrows():
        pdf.cell(0, 10, f"{row.to_string(index=False)}", ln=True)
    pdf.ln(10)

    pdf.cell(200, 10, "📉 Hasta ve Kontrol Grubu Dağılım Grafiği", ln=True)
    pdf.ln(5)
    pdf.image(plot_path, x=10, w=180)
    
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    return pdf_buffer.getvalue()

# Giriş Verileri Tablosunu Göster
if input_values_table: 
    input_df = pd.DataFrame(input_values_table) 
    csv = input_df.to_csv(index=False).encode("utf-8") 
    st.download_button(label="📥 CSV İndir", data=csv, file_name="giris_verileri.csv", mime="text/csv") 

# Sonuçlar Tablosunu Göster
if data:
    df = pd.DataFrame(data)
    st.subheader("📊 Sonuçlar")
    st.write(df)

# İstatistik Sonuçları
if stats_data:
    stats_df = pd.DataFrame(stats_data)
    st.subheader("📈 İstatistik Sonuçları")
    st.write(stats_df)
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(label="📥 İstatistik Sonuçlarını CSV Olarak İndir", data=csv_stats, file_name="istatistik_sonuclari.csv", mime="text/csv")

    # Grafik oluşturma
    fig = go.Figure()
    fig.update_layout(title="Hasta ve Kontrol Grubu Dağılım Grafiği", xaxis_title="Grup", yaxis_title="ΔCt Değeri")
    st.plotly_chart(fig)
    
    # Grafiği kaydet
    img_path = "graph.png"
    fig.write_image(img_path)
    
    # PDF Raporu Oluştur ve İndir
    if st.button("📥 PDF Raporu İndir"):
        pdf_content = create_pdf(df, stats_df, pd.DataFrame(input_values_table), img_path)
        st.download_button(label="PDF Olarak İndir", data=pdf_content, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
