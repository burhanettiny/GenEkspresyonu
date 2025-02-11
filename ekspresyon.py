import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import scipy.stats as stats
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Uygulama Başlığı
st.title("🧬 Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

# Kullanıcıdan Giriş Al
st.header("📊 Hasta ve Kontrol Grubu Verisi Girin")

# Hedef Gen ve Hasta Grubu Sayısı (Varsayılan olarak 1 değeri gelir)
num_target_genes = st.number_input("🔹 Hedef Gen Sayısını Girin", min_value=1, step=1)
num_patient_groups = st.number_input("🔹 Hasta Grubu Sayısını Girin", min_value=1, step=1)

# Global veri listeleri ve örnek numaralandırması
input_values_table = []
data = []
stats_data = []
sample_counter = 1

# PDF oluşturma fonksiyonu (global rapor)
def create_pdf(data, stats_data, input_df):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Başlık
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "🧬 Gen Ekspresyon Analizi Sonuçları")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "B. Yalçınkaya tarafından geliştirildi")
    
    y_position = height - 100
    
    # Giriş Verileri
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📋 Giriş Verileri")
    y_position -= 20
    c.setFont("Helvetica", 8)
    for index, row in input_df.iterrows():
        text_line = (
            f"Örnek {row['Örnek Numarası']} - {row['Grup']} - {row['Hedef Gen']} - "
            f"Hedef Gen Ct: {row['Hedef Gen Ct Değeri']} - Referans Ct: {row['Referans Ct']}"
        )
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    y_position -= 20
    
    # Sonuçlar
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📊 Sonuçlar")
    y_position -= 20
    c.setFont("Helvetica", 8)
    for result in data:
        text_line = (
            f"{result['Hedef Gen']} - {result['Hasta Grubu']} - ΔΔCt: {result['ΔΔCt']} - "
            f"Ekspresyon: {result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']} - {result['Regülasyon Durumu']}"
        )
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    y_position -= 20
    
    # İstatistik Sonuçları
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📈 İstatistik Sonuçları")
    y_position -= 20
    c.setFont("Helvetica", 8)
    for stat in stats_data:
        text_line = (
            f"{stat['Hedef Gen']} - {stat['Hasta Grubu']} - {stat['Test Türü']} ({stat['Kullanılan Test']}) - "
            f"P-değeri: {stat['Test P-değeri']:.4f} - {stat['Anlamlılık']}"
        )
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    
    c.save()
    buffer.seek(0)
    return buffer

# Girdi verisini sayısal değerlere çeviren fonksiyon
def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# Her hedef gen için verileri alıp hesaplamaları yapıyoruz
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
    
    # Ortak uzunlukta veriyi almak için:
    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_target_ct_values = control_target_ct_values[:min_control_len]
    control_reference_ct_values = control_reference_ct_values[:min_control_len]
    
    # ΔCt hesaplama
    control_delta_ct = control_target_ct_values - control_reference_ct_values
    average_control_delta_ct = np.mean(control_delta_ct)

    # Kontrol grubuna ait verileri tabloya ekle
    for idx in range(min_control_len):
        input_values_table.append({
            "Örnek Numarası": sample_counter,
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Grup": "Kontrol",
            "Hedef Gen Ct Değeri": control_target_ct_values[idx],
            "Referans Ct": control_reference_ct_values[idx]
        })
        sample_counter += 1
    
    # Hasta Grubu Verileri ve İşlemleri
    for j in range(num_patient_groups):
        st.subheader(f"🩸 Hasta Grubu {j+1} (Hedef Gen {i+1})")
        
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

        # Hasta grubuna ait verileri tabloya ekle
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
        st.subheader(f"Hedef Gen {i+1} - Hasta Grubu {j+1} Dağılım Grafiği")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
            y=control_delta_ct,
            mode='markers',
            name='Kontrol Grubu',
            marker=dict(color='blue'),
            text=[f'Kontrol: {val:.2f}' for val in control_delta_ct],
            hoverinfo='text'
        ))
        fig.add_trace(go.Scatter(
            x=np.ones(len(sample_delta_ct)) * 2 + np.random.uniform(-0.05, 0.05, len(sample_delta_ct)),
            y=sample_delta_ct,
            mode='markers',
            name=f'Hasta Grubu {j+1}',
            marker=dict(color='red'),
            text=[f'Hasta: {val:.2f}' for val in sample_delta_ct],
            hoverinfo='text'
        ))
        fig.add_trace(go.Scatter(
            x=[1, 1],
            y=[average_control_delta_ct, average_control_delta_ct],
            mode='lines',
            line=dict(color='black', dash='dot', width=4),
            name='Kontrol Ortalama'
        ))
        fig.add_trace(go.Scatter(
            x=[2, 2],
            y=[average_sample_delta_ct, average_sample_delta_ct],
            mode='lines',
            line=dict(color='black', dash='dot', width=4),
            name='Hasta Ortalama'
        ))
        fig.update_layout(
            title=f"Hedef Gen {i+1} - ΔCt Dağılımı",
            xaxis=dict(
                tickvals=[1, 2],
                ticktext=['Kontrol', f'Hasta Grubu {j+1}'],
                title='Grup'
            ),
            yaxis=dict(title='ΔCt Değeri'),
            showlegend=True
        )
        st.plotly_chart(fig)

        # PDF raporunu her grup için indirilebilir yapalım
        st.markdown("---")
        input_df = pd.DataFrame(input_values_table)
        pdf_buffer = create_pdf(data, stats_data, input_df)
        st.download_button(
            label="📥 PDF Raporu İndir",
            data=pdf_buffer,
            file_name=f"gen_ekspresyon_raporu_{i+1}_{j+1}.pdf",
            mime="application/pdf"
        )

# Giriş Verileri, Sonuçlar ve İstatistik Sonuçları tablolarını (ve CSV indirme butonlarını) sayfanın sonuna ekleyelim.
if input_values_table:
    st.subheader("📋 Giriş Verileri Tablosu")
    input_df = pd.DataFrame(input_values_table)
    st.write(input_df)
    csv = input_df.to_csv(index=False).encode("utf-8")
    st.download_button(label="📥 CSV İndir", data=csv, file_name="giris_verileri.csv", mime="text/csv")

if data:
    st.subheader("📊 Sonuçlar")
    results_df = pd.DataFrame(data)
    st.write(results_df)
    csv_results = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(label="📥 Sonuçları CSV İndir", data=csv_results, file_name="sonuclar.csv", mime="text/csv")

if stats_data:
    st.subheader("📈 İstatistiksel Sonuçlar")
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(label="📥 İstatistiksel Sonuçları CSV İndir", data=csv_stats, file_name="istatistikler.csv", mime="text/csv")
