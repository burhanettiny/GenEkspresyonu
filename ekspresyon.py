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

 
# Başlık
st.title("🧬 Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

# Kullanıcıdan giriş al
st.header("📊 Hasta ve Kontrol Grubu Verisi Girin")

# Hedef Gen ve Hasta Grubu Sayısı
num_target_genes = st.number_input("🔹 Hedef Gen Sayısını Girin", min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input("🔹 Hasta Grubu Sayısını Girin", min_value=1, step=1, key="patient_count")

# Veri listeleri
input_values_table = []
data = []
stats_data = []

# Giriş verilerini işleyen fonksiyon
def parse_input_data(input_data):
    # Virgülleri noktaya dönüştürüp, boşlukları ve fazlalıkları temizliyoruz
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# Grafik için son işlenen Hedef Genın kontrol verilerini saklamak amacıyla değişkenler
last_control_delta_ct = None
last_gene_index = None

input_values_table = []  # Sonuçları saklamak için kullanılan liste

# Her hedef gen için işlem yapılır
for i in range(num_target_genes):
    st.subheader(f"🧬 Hedef Gen {i+1}")

    # Kontrol Grubu Verileri
    control_target_ct = st.text_area(f"🟦 Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"🟦 Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f"⚠️ Dikkat: Kontrol Grubu {i+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.")
        continue

    # Her bir satır için örnek numarasını arttıracağız
    sample_counter = 1
    for idx in range(len(control_target_ct_values)):
        # Kontrol grubundaki her bir örnek için ortalama alıyoruz
        avg_control_target_ct = np.mean(control_target_ct_values)
        avg_control_reference_ct = np.mean(control_reference_ct_values)
        avg_control_delta_ct = avg_control_target_ct - avg_control_reference_ct

        input_values_table.append({
            "Örnek Numarası": sample_counter,
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Grup": "Kontrol",
            "Hedef Gen Ct Değeri": avg_control_target_ct,
            "Referans Ct": avg_control_reference_ct,
            "ΔCt (Kontrol)": avg_control_delta_ct
        })
        sample_counter += 1  # Her satırda örnek numarasını artırıyoruz

# Aynı işlemi Hasta grubu için de yapıyoruz:
for j in range(num_patient_groups):
    st.subheader(f"🩸 Hasta Grubu {j+1} - Hedef Gen {i+1}")

    sample_target_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}_{j}")
    sample_reference_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}_{j}")

    sample_target_ct_values = parse_input_data(sample_target_ct)
    sample_reference_ct_values = parse_input_data(sample_reference_ct)

    if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
        st.error(f"⚠️ Dikkat: Hasta Grubu {j+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.")
        continue

    # Her bir satır için örnek numarasını arttıracağız
    sample_counter = 1
    for idx in range(len(sample_target_ct_values)):
        # Hasta grubundaki her bir örnek için ortalama alıyoruz
        avg_sample_target_ct = np.mean(sample_target_ct_values)
        avg_sample_reference_ct = np.mean(sample_reference_ct_values)
        avg_sample_delta_ct = avg_sample_target_ct - avg_sample_reference_ct

        input_values_table.append({
            "Örnek Numarası": sample_counter,
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Grup": f"Hasta Grubu {j+1}",
            "Hedef Gen Ct Değeri": avg_sample_target_ct,
            "Referans Ct": avg_sample_reference_ct,
            "ΔCt (Hasta)": avg_sample_delta_ct
        })
        sample_counter += 1  # Her satırda örnek numarasını artırıyoruz

# Giriş Verileri Tablosunu Göster
if input_values_table:
    st.subheader("📋 Giriş Verileri Tablosu")
    input_df = pd.DataFrame(input_values_table)
    st.write(input_df)
    csv = input_df.to_csv(index=False).encode("utf-8")
    st.download_button(label="📥 CSV İndir", data=csv, file_name="giris_verileri.csv", mime="text/csv")

# Sonuçlar Tablosunu Göster
if data:
    st.subheader("📊 Sonuçlar")
    df = pd.DataFrame(data)
    st.write(df)

# İstatistik Sonuçları
if stats_data:
    st.subheader("📈 İstatistik Sonuçları")
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(label="📥 İstatistik Sonuçlarını CSV Olarak İndir", data=csv_stats, file_name="istatistik_sonuclari.csv", mime="text/csv")

# Grafik oluşturma
for i in range(num_target_genes):
    st.subheader(f"Hedef Gen {i+1} - Hasta ve Kontrol Grubu Dağılım Grafiği")
    control_target_ct_values = [d["Hedef Gen Ct Değeri"] for d in input_values_table if d["Grup"] == "Kontrol" and d["Hedef Gen"] == f"Hedef Gen {i+1}"]
    patient_target_ct_values = [d["Hedef Gen Ct Değeri"] for d in input_values_table if d["Grup"].startswith("Hasta") and d["Hedef Gen"] == f"Hedef Gen {i+1}"]
    
    fig = go.Figure()

    fig.add_trace(go.Histogram(x=control_target_ct_values, name="Kontrol Grubu", opacity=0.7))
    fig.add_trace(go.Histogram(x=patient_target_ct_values, name="Hasta Grubu", opacity=0.7))

    fig.update_layout(
        title=f"Hedef Gen {i+1} Dağılımı",
        xaxis_title="Ct Değerleri",
        yaxis_title="Frekans",
        barmode="overlay",
        bargap=0.2
    )
    st.plotly_chart(fig)


 

# PDF rapor oluşturma kısmı

from reportlab.lib.units import inch

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

from reportlab.lib.styles import getSampleStyleSheet

 

def create_pdf(results, stats, input_df):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []

   

    styles = getSampleStyleSheet()

   

    # Başlık

    elements.append(Paragraph("Gen Ekspresyon Analizi Raporu", styles['Title']))

    elements.append(Spacer(1, 12))

 

    # Giriş Verileri Tablosu Başlığı

    elements.append(Paragraph("Giris Verileri Tablosu:", styles['Heading2']))

   

    # Tablo Verisi

    table_data = [input_df.columns.tolist()] + input_df.values.tolist()

    col_width = (letter[0] - 80) / len(input_df.columns)

    table = Table(table_data, colWidths=[col_width] * len(input_df.columns))

   

    table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),

        ('FONTSIZE', (0, 0), (-1, -1), 10),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

    ]))

   

    elements.append(table)

    elements.append(Spacer(1, 12))

   

    # Sonuçlar Başlığı

    elements.append(Paragraph("Sonuçlar:", styles['Heading2']))

    elements.append(Spacer(1, 12))

   

    for result in results:

        text = f"{result['Hedef Gen']} - {result['Hasta Grubu']} | ΔΔCt: {result['ΔΔCt']:.2f} | 2^(-ΔΔCt): {result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']:.2f} | {result['Regülasyon Durumu']}"

        elements.append(Paragraph(text, styles['Normal']))

        elements.append(Spacer(1, 6))

   

    elements.append(PageBreak())

   

    # İstatistiksel Sonuçlar

    elements.append(Paragraph("istatistiksel Sonuçlar:", styles['Heading2']))

    elements.append(Spacer(1, 12))

   

    for stat in stats:

        text = f"{stat['Hedef Gen']} - {stat['Hasta Grubu']} | Test: {stat['Kullanılan Test']} | p-değeri: {stat['Test P-değeri']:.4f} | {stat['Anlamlılık']}"

        elements.append(Paragraph(text, styles['Normal']))

        elements.append(Spacer(1, 6))

   

    elements.append(PageBreak())

   

    # İstatistiksel Değerlendirme

    elements.append(Paragraph("istatistiksel Degerlendirme:", styles['Heading2']))

    elements.append(Spacer(1, 12))

   

    explanation = (

        "istatistiksel degerlendirme sürecinde veri dagilimi Shapiro-Wilk testi ile analiz edilmistir. "

        "Normallik saglanirsa, gruplar arasindaki varyans esitligi Levene testi ile kontrol edilmistir. "

        "Varyans esitligi varsa bagimsiz örneklem t-testi, yoksa Welch t-testi uygulanmistir. "

        "Eger normal dagilim saglanmazsa, parametrik olmayan Mann-Whitney U testi kullanilmistir. "

        "Sonuclarin anlamliligi p < 0.05 kriterine göre belirlenmistir. "

        "<b>Görüs ve önerileriniz icin; <a href='mailto:mailtoburhanettin@gmail.com'>mailtoburhanettin@gmail.com</a></b>"

       

    )

   

    for line in explanation.split(". "):

        elements.append(Paragraph(line.strip() + '.', styles['Normal']))

        elements.append(Spacer(1, 6))

   

    doc.build(elements)

    buffer.seek(0)

    return buffer

 

if st.button("📥 PDF Raporu Hazırla"):

    if input_values_table:

        pdf_buffer = create_pdf(data, stats_data, pd.DataFrame(input_values_table))

        st.download_button(label="PDF Olarak İndir", data=pdf_buffer, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")

    else:

        st.error("Veri bulunamadı, PDF oluşturulamadı.")
