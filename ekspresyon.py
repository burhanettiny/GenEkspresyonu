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

# Dil Seçimi
language = st.selectbox("Dil Seçin", ["Türkçe", "English"])

# Başlık ve açıklamalar dil seçimine göre ayarlandı
if language == "Türkçe":
    st.title("🧬 Gen Ekspresyon Analizi Uygulaması")
    st.markdown("### B. Yalçınkaya tarafından geliştirildi")
    st.header("📊 Hasta ve Kontrol Grubu Verisi Girin")
    target_genes_label = "🔹 Hedef Gen Sayısını Girin"
    patient_groups_label = "🔹 Hasta Grubu Sayısını Girin"
else:
    st.title("🧬 Gene Expression Analysis Application")
    st.markdown("### Developed by B. Yalçınkaya")
    st.header("📊 Enter Patient and Control Group Data")
    target_genes_label = "🔹 Enter the Number of Target Genes"
    patient_groups_label = "🔹 Enter the Number of Patient Groups"

# Kullanıcıdan giriş al
num_target_genes = st.number_input(target_genes_label, min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(patient_groups_label, min_value=1, step=1, key="patient_count")

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
    st.subheader(f"🧬 Hedef Gen {i+1}" if language == "Türkçe" else f"🧬 Target Gene {i+1}")
    
    # Kontrol Grubu Verileri
    control_target_ct = st.text_area(f"🟦 Kontrol Grubu Hedef Gen {i+1} Ct Değerleri" if language == "Türkçe" else f"🟦 Control Group Target Gene {i+1} Ct Values", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"🟦 Kontrol Grubu Referans Gen {i+1} Ct Değerleri" if language == "Türkçe" else f"🟦 Control Group Reference Gene {i+1} Ct Values", key=f"control_reference_ct_{i}")
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f"⚠️ Dikkat: Kontrol Grubu {i+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın." if language == "Türkçe" else f"⚠️ Warning: Enter Control Group {i+1} data row by row or copy-paste without blank cells from Excel.")
        continue
    
    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_target_ct_values = control_target_ct_values[:min_control_len]
    control_reference_ct_values = control_reference_ct_values[:min_control_len]
    control_delta_ct = control_target_ct_values - control_reference_ct_values
    
    if len(control_delta_ct) > 0:
        average_control_delta_ct = np.mean(control_delta_ct)
        # Grafik kısmında kullanabilmek için bu genin kontrol verilerini saklıyoruz.
        last_control_delta_ct = control_delta_ct  
        last_gene_index = i
    else:
        st.warning(f"⚠️ Dikkat: Kontrol grubu Ct verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın" if language == "Türkçe" else f"⚠️ Warning: Enter Control Group Ct values row by row or copy-paste without blank cells from Excel.")
        continue
    
    sample_counter = 1  # Kontrol grubu örnek sayacı
    for idx in range(min_control_len):
        input_values_table.append({
            "Örnek Numarası": sample_counter,
            "Hedef Gen": f"Hedef Gen {i+1}" if language == "Türkçe" else f"Target Gene {i+1}",
            "Grup": "Kontrol" if language == "Türkçe" else "Control",
            "Hedef Gen Ct Değeri": control_target_ct_values[idx],
            "Referans Ct": control_reference_ct_values[idx],  
            "ΔCt (Kontrol)": control_delta_ct[idx]
        })
        sample_counter += 1
    
    # Hasta Grubu Verileri
    for j in range(num_patient_groups):
        st.subheader(f"🩸 Hasta Grubu {j+1} - Hedef Gen {i+1}" if language == "Türkçe" else f"🩸 Patient Group {j+1} - Target Gene {i+1}")
        
        sample_target_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri" if language == "Türkçe" else f"🟥 Patient Group {j+1} Target Gene {i+1} Ct Values", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri" if language == "Türkçe" else f"🟥 Patient Group {j+1} Reference Gene {i+1} Ct Values", key=f"sample_reference_ct_{i}_{j}")
        
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)
        
        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(f"⚠️ Dikkat: Hasta Grubu {j+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın." if language == "Türkçe" else f"⚠️ Warning: Enter Patient Group {j+1} data row by row or copy-paste without blank cells from Excel.")
            continue
        
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
        if len(sample_delta_ct) > 0:
            average_sample_delta_ct = np.mean(sample_delta_ct)
        else:
            st.warning(f"⚠️ Dikkat: Hasta grubu {j+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın." if language == "Türkçe" else f"⚠️ Warning: Enter Patient Group {j+1} data row by row or copy-paste without blank cells from Excel.")
            continue
        
        sample_counter = 1  # Her Hasta Grubu için örnek sayacı sıfırlanıyor
        for idx in range(min_sample_len):
            input_values_table.append({
                "Örnek Numarası": sample_counter,
                "Hedef Gen": f"Hedef Gen {i+1}" if language == "Türkçe" else f"Target Gene {i+1}",
                "Grup": f"Hasta Grubu {j+1}" if language == "Türkçe" else f"Patient Group {j+1}",
                "Hedef Gen Ct Değeri": sample_target_ct_values[idx],
                "Referans Ct": sample_reference_ct_values[idx],
                "ΔCt (Hasta)": sample_delta_ct[idx]
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
        
        test_type = "Parametrik" if control_normal and sample_normal and equal_variance else "Nonparametrik" if language == "Türkçe" else "Parametric" if control_normal and sample_normal and equal_variance else "Nonparametric"
        
        if test_type == "Parametrik" if language == "Türkçe" else "Parametric":
            test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue
            test_method = "t-test" if language == "Türkçe" else "t-test"
        else:
            test_pvalue = stats.mannwhitneyu(control_delta_ct, sample_delta_ct).pvalue
            test_method = "Mann-Whitney U testi" if language == "Türkçe" else "Mann-Whitney U test"
        
        significance = "Anlamlı" if test_pvalue < 0.05 else "Anlamsız" if language == "Türkçe" else "Significant" if test_pvalue < 0.05 else "Not Significant"
        
        stats_data.append({
            "Hedef Gen": f"Hedef Gen {i+1}" if language == "Türkçe" else f"Target Gene {i+1}",
            "Hasta Grubu": f"Hasta Grubu {j+1}" if language == "Türkçe" else f"Patient Group {j+1}",
            "Test Türü": test_type,
            "Kullanılan Test": test_method,  
            "Test P-değeri": test_pvalue,
            "Anlamlılık": significance
        })
        
        data.append({
            "Hedef Gen": f"Hedef Gen {i+1}" if language == "Türkçe" else f"Target Gene {i+1}",
            "Hasta Grubu": f"Hasta Grubu {j+1}" if language == "Türkçe" else f"Patient Group {j+1}",
            "ΔΔCt": delta_delta_ct,
            "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
            "Regülasyon Durumu": regulation_status,
          


  "ΔCt (Kontrol)": average_control_delta_ct,
            "ΔCt (Hasta)": average_sample_delta_ct
        })

# Giriş Verileri Tablosunu Göster
if input_values_table:
    st.subheader(translations["input_table_header"][language])
    input_df = pd.DataFrame(input_values_table)
    st.write(input_df)

    csv = input_df.to_csv(index=False).encode("utf-8")
    st.download_button(label=translations["download_button_label"][language], data=csv, file_name="input_data.csv", mime="text/csv")

# Sonuçlar Tablosunu Göster
if data:
    st.subheader(translations["results_header"][language])
    df = pd.DataFrame(data)
    st.write(df)

# İstatistik Sonuçları
if stats_data:
    st.subheader(translations["statistics_header"][language])
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)

    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(label=translations["statistics_download_button_label"][language], data=csv_stats, file_name="statistical_results.csv", mime="text/csv")

# Grafik oluşturma (her hedef gen için bir grafik oluşturulacak)
for i in range(num_target_genes):
    st.subheader(translations["graph_title"][language].format(i=i))

    # Kontrol Grubu Verileri
    control_target_ct_values = [
        d["Hedef Gen Ct Değeri"] for d in input_values_table
        if d["Grup"] == "Kontrol" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]

    control_reference_ct_values = [
        d["Referans Ct"] for d in input_values_table
        if d["Grup"] == "Kontrol" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(translations["error_message"][language].format(i=i))
        continue

    control_delta_ct = np.array(control_target_ct_values) - np.array(control_reference_ct_values)
    average_control_delta_ct = np.mean(control_delta_ct)

    # Hasta Grubu Verileri
    fig = go.Figure()

    # Kontrol Grubu Ortalama Çizgisi
    fig.add_trace(go.Scatter(
        x=[0.8, 1.2],  
        y=[average_control_delta_ct, average_control_delta_ct],  
        mode='lines',
        line=dict(color='black', width=4),
        name='Kontrol Grubu Ortalama'
    ))

    # Hasta Gruplarının Ortalama Çizgileri
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d["ΔCt (Hasta)"] for d in input_values_table 
            if d["Grup"] == f"Hasta Grubu {j+1}" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
        ]

        if not sample_delta_ct_values:
            continue  # Eğer hasta grubuna ait veri yoksa, bu hasta grubunu atla
        
        average_sample_delta_ct = np.mean(sample_delta_ct_values)
        fig.add_trace(go.Scatter(
            x=[(j + 1.8), (j + 2.2)],  
            y=[average_sample_delta_ct, average_sample_delta_ct],  
            mode='lines',
            line=dict(color='black', width=4),
            name=f'Hasta Grubu {j+1} Ortalama'
        ))

    # Veri Noktaları (Kontrol Grubu)
    fig.add_trace(go.Scatter(
        x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
        y=control_delta_ct,
        mode='markers',  
        name='Kontrol Grubu',
        marker=dict(color='blue'),
        text=[f'Kontrol {value:.2f}, Örnek {idx+1}' for idx, value in enumerate(control_delta_ct)],
        hoverinfo='text'
    ))

    # Veri Noktaları (Hasta Grupları)
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d["ΔCt (Hasta)"] for d in input_values_table 
            if d["Grup"] == f"Hasta Grubu {j+1}" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
        ]

        if not sample_delta_ct_values:
            continue  # Eğer hasta grubuna ait veri yoksa, bu hasta grubunu atla
        
        fig.add_trace(go.Scatter(
            x=np.ones(len(sample_delta_ct_values)) * (j + 2) + np.random.uniform(-0.05, 0.05, len(sample_delta_ct_values)),
            y=sample_delta_ct_values,
            mode='markers',  
            name=f'Hasta Grubu {j+1}',
            marker=dict(color='red'),
            text=[f'Hasta {value:.2f}, Örnek {idx+1}' for idx, value in enumerate(sample_delta_ct_values)],
            hoverinfo='text'
        ))

    # Grafik ayarları
    fig.update_layout(
        title=f"Hedef Gen {i+1} - ΔCt Dağılımı",
        xaxis=dict(
            tickvals=[1] + [i + 2 for i in range(num_patient_groups)],
            ticktext=['Kontrol Grubu'] + [f'Hasta Grubu {i+1}' for i in range(num_patient_groups)],
            title='Grup'
        ),
        yaxis=dict(title='ΔCt Değeri'),
        showlegend=True
    )

    st.plotly_chart(fig)

else:
    st.info(translations["info_message"][language])

# PDF rapor oluşturma kısmı
# Dil Desteği
def translate_to_selected_language():
    if language == "Türkçe":
        return {
            "title": "Gen Ekspresyon Analizi Raporu",
            "input_data_table": "Giriş Verileri Tablosu:",
            "results": "Sonuçlar:",
            "statistical_results": "İstatistiksel Sonuçlar:",
            "statistical_assessment": "İstatistiksel Değerlendirme:",
            "statistical_explanation": (
                "İstatistiksel değerlendirme sürecinde veri dağılımı Shapiro-Wilk testi ile analiz edilmiştir. "
                "Normallik sağlanırsa, gruplar arasındaki varyans eşitliği Levene testi ile kontrol edilmiştir. "
                "Varyans eşitliği varsa bağımsız örneklem t-testi, yoksa Welch t-testi uygulanmıştır. "
                "Eğer normal dağılım sağlanmazsa, parametrik olmayan Mann-Whitney U testi kullanılmıştır. "
                "Sonuçların anlamlılığı p < 0.05 kriterine göre belirlenmiştir. "
                "Görüş ve önerileriniz için; <a href='mailto:mailtoburhanettin@gmail.com'>mailtoburhanettin@gmail.com</a>"
            ),
        }
    else:  # English
        return {
            "title": "Gene Expression Analysis Report",
            "input_data_table": "Input Data Table:",
            "results": "Results:",
            "statistical_results": "Statistical Results:",
            "statistical_assessment": "Statistical Assessment:",
            "statistical_explanation": (
                "In the statistical evaluation process, the distribution of data was analyzed using the Shapiro-Wilk test. "
                "If normality is achieved, Levene's test was used to check the equality of variances between groups. "
                "If variances are equal, independent t-test was applied, otherwise Welch t-test was used. "
                "If normal distribution is not achieved, non-parametric Mann-Whitney U test was used. "
                "The significance of the results was determined based on p < 0.05 criteria. "
                "For your views and suggestions; <a href='mailto:mailtoburhanettin@gmail.com'>mailtoburhanettin@gmail.com</a>"
            ),
        }

# PDF rapor oluşturma kısmı
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(results, stats, input_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    translation = translate_to_selected_language()

    # Başlık
    elements.append(Paragraph(translation["title"], styles['Title']))
    elements.append(Spacer(1, 12))

    # Giriş Verileri Tablosu Başlığı
    elements.append(Paragraph(translation["input_data_table"], styles['Heading2']))
    
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
    elements.append(Paragraph(translation["results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for result in results:
        text = f"{result['Hedef Gen']} - {result['Hasta Grubu']} | ΔΔCt: {result['ΔΔCt']:.2f} | 2^(-ΔΔCt): {result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']:.2f} | {result['Regülasyon Durumu']}"
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # İstatistiksel Sonuçlar
    elements.append(Paragraph(translation["statistical_results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for stat in stats:
        text = f"{stat['Hedef Gen']} - {stat['Hasta Grubu']} | Test: {stat['Kullanılan Test']} | p-değeri: {stat['Test P-değeri']:.4f} | {stat['Anlamlılık']}"
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # İstatistiksel Değerlendirme
    elements.append(Paragraph(translation["statistical_assessment"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for line in translation["statistical_explanation"].split(". "):
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
