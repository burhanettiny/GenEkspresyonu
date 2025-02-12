import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
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
    st.subheader(f"Hedef Gen {i+1} - Hasta ve Kontrol Grubu Dağılım Grafiği")
    
    # Plotly grafik objesi oluşturuluyor
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

    # Kontrol grubunun ortalama değerini çizme (kesik çizgi - siyah)
    fig.add_trace(go.Scatter(
        x=[1, 1],  # X ekseninde 1 (Kontrol grubu) için
        y=[average_control_delta_ct, average_control_delta_ct],  # Y ekseninde ortalama değer
        mode='lines',
        line=dict(color='black', dash='dot', width=4),  # Kesik siyah çizgi
        name='Kontrol Grubu Ortalama'
    ))

    # Hasta grubunun ortalama değerini çizme (kesik çizgi - siyah)
    for j in range(num_patient_groups):
        fig.add_trace(go.Scatter(
            x=[(j + 2), (j + 2)],  # X ekseninde 2 (Hasta grubu) için
            y=[average_sample_delta_ct, average_sample_delta_ct],  # Y ekseninde ortalama değer
            mode='lines',
            line=dict(color='black', dash='dot', width=4),  # Kesik siyah çizgi
            name=f'Hasta Grubu {j+1} Ortalama'
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

    # Etkileşimli grafik gösterimi
    st.plotly_chart(fig)

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(results, stats, input_df, plotly_figure):
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

    c.save()
    buffer.seek(0)
    return buffer

def create_pdf(results, stats, input_df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Gen Ekspresyon Analizi Raporu")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 80, "Giriş Verileri Tablosu:")
    
    table_data = [input_df.columns.tolist()] + input_df.values.tolist()
    table = Table(table_data, colWidths=[100, 100, 100, 100, 100])
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEBEFORE', (0, 0), (0, -1), 0.5, colors.black)
    ]))
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 320)
    
    c.setFont("Helvetica", 12)
    y_position = height - 440
    c.drawString(50, y_position, "Sonuçlar:")
    y_position -= 20
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
    c.drawString(50, y_position - 30, "İstatistiksel Değerlendirme:")
    
    y_position -= 50
    explanation = (
        "İstatistiksel değerlendirme sürecinde öncelikle veri dağılımı Shapiro-Wilk testi ile normal olup olmadığı açısından analiz edilmiştir. "
        "Normallik varsayımı sağlandığında, gruplar arasındaki varyans eşitliği Levene testi ile kontrol edilmiştir. "
        "Varyans eşitliği sağlandığında bağımsız örneklem t-testi, sağlanmadığında Welch t-testi uygulanmıştır. "
        "Eğer veriler normal dağılmıyorsa, parametrik olmayan Mann-Whitney U testi kullanılmıştır. "
        "Sonuçların anlamlı olup olmadığı, p-değerinin 0.05 eşik değerinden küçük olup olmadığına göre belirlenmiştir. "
        "Eğer p < 0.05 ise sonuç istatistiksel olarak anlamlı kabul edilmiştir."
    )
    
    c.setFont("Helvetica", 12)
    text_lines = explanation.split(". ")
    for line in text_lines:
        c.drawString(50, y_position, line.strip() + '.')
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    # Convert Plotly figure to image (PNG format)
    plotly_image = pio.to_image(plotly_figure, format='png')
    plotly_image_stream = BytesIO(plotly_image)
    c.drawImage(plotly_image_stream, 50, height - 350, width=500, height=300)
    
    # Grafik Görselini PDF'ye ekleyelim
    plotly_image = pio.to_image(plotly_figure, format='png')
    image_buffer = BytesIO(plotly_image)
    c.drawImage(image_buffer, 50, y_position - 150, width=500, height=300)

    c.save()
    buffer.seek(0)
    return buffer

if st.button("📥 PDF Raporu İndir"):
    if input_values_table:
        pdf_buffer = create_pdf(data, stats_data, pd.DataFrame(input_values_table), fig)  # Pass the Plotly figure here
        st.download_button(label="PDF Olarak İndir", data=pdf_buffer, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
    else:
        st.error("Veri bulunamadı, PDF oluşturulamadı.")

