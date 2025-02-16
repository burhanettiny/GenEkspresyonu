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
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, PageBreak

# Dil Seçimi
lang = st.sidebar.radio("🌐 Select Language / Dil Seçin", ["English", "Türkçe"])

# Metinler
texts = {
    "title": {"English": "🧬 Gene Expression Analysis Application", "Türkçe": "🧬 Gen Ekspresyon Analizi Uygulaması"},
    "developer": {"English": "Developed by B. Yalçınkaya", "Türkçe": "B. Yalçınkaya tarafından geliştirildi"},
    "enter_data": {"English": "📊 Enter Patient and Control Group Data", "Türkçe": "📊 Hasta ve Kontrol Grubu Verisi Girin"},
    "target_gene_count": {"English": "🔹 Enter Target Gene Count", "Türkçe": "🔹 Hedef Gen Sayısını Girin"},
    "patient_group_count": {"English": "🔹 Enter Patient Group Count", "Türkçe": "🔹 Hasta Grubu Sayısını Girin"},
}

# Başlık
st.title(texts["title"][lang])
st.markdown(f"### {texts['developer'][lang]}")

# Kullanıcıdan giriş al
st.header(texts["enter_data"][lang])

# Hedef Gen ve Hasta Grubu Sayısı
num_target_genes = st.number_input(texts["target_gene_count"][lang], min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(texts["patient_group_count"][lang], min_value=1, step=1, key="patient_count")

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
    st.subheader(f"🧬 Target Gene {i+1}" if lang == "English" else f"🧬 Hedef Gen {i+1}")
    
    # Kontrol Grubu Verileri
    control_target_ct = st.text_area(f"🟦 Control Group Target Gene {i+1} Ct Values" if lang == "English" else f"🟦 Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"🟦 Control Group Reference Gene {i+1} Ct Values" if lang == "English" else f"🟦 Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error("⚠️ Please enter valid control group data!" if lang == "English" else "⚠️ Lütfen geçerli kontrol grubu verilerini girin!")
        continue
    
        sample_counter = 1  # Kontrol grubu örnek sayacı
    for idx in range(min_control_len):
        input_values_table.append({
            "Örnek Numarası": sample_counter,
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Grup": "Kontrol",
            "Hedef Gen Ct Değeri": control_target_ct_values[idx],
            "Referans Ct": control_reference_ct_values[idx],  
            "ΔCt (Kontrol)": control_delta_ct[idx]
        })
        sample_counter += 1
    
    # Hasta Grubu Verileri
    for j in range(num_patient_groups):
        st.subheader(f"🩸 Patient Group {j+1} - Target Gene {i+1}" if lang == "English" else f"🩸 Hasta Grubu {j+1} - Hedef Gen {i+1}")

        sample_target_ct = st.text_area(f"🟥 Patient Group {j+1} Target Gene {i+1} Ct Values" if lang == "English" else f"🟥 Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"🟥 Patient Group {j+1} Reference Gene {i+1} Ct Values" if lang == "English" else f"🟥 Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}_{j}")

        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)

        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error("⚠️ Please enter valid patient group data!" if lang == "English" else "⚠️ Lütfen geçerli hasta grubu verilerini girin!")
            continue

          min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
          sample_target_ct_values = sample_target_ct_values[:min_sample_len]
          sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
          sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
          if len(sample_delta_ct) > 0:
            average_sample_delta_ct = np.mean(sample_delta_ct)
          else:
            st.warning(f"⚠️ Dikkat: Hasta grubu {j+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.")
            continue
        
          sample_counter = 1  # Her Hasta Grubu için örnek sayacı sıfırlanıyor
          for idx in range(min_sample_len):
            input_values_table.append({
                "Örnek Numarası": sample_counter,
                "Hedef Gen": f"Hedef Gen {i+1}",
                "Grup": f"Hasta Grubu {j+1}",
                "Hedef Gen Ct Değeri": sample_target_ct_values[idx],
                "Referans Ct": sample_reference_ct_values[idx],
                "ΔCt (Hasta)": sample_delta_ct[idx]
            })
            sample_counter += 1
        
        # ΔΔCt ve Gen Ekspresyon Değişimi Hesaplama
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        avg_sample_delta_ct = np.mean(sample_delta_ct)

        delta_delta_ct = avg_sample_delta_ct - avg_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)

        regulation_status = (
            "No Change" if expression_change == 1 else
            ("Upregulated" if expression_change > 1 else "Downregulated")
        ) if lang == "English" else (
            "Değişim Yok" if expression_change == 1 else
            ("Upregüle" if expression_change > 1 else "Downregüle")
        )
        # İstatistiksel Testler
        shapiro_control = stats.shapiro(control_delta_ct)
        shapiro_sample = stats.shapiro(sample_delta_ct)
        levene_test = stats.levene(control_delta_ct, sample_delta_ct)

        test_type = "Parametric" if lang == "English" else "Parametrik"
        test_method = "t-test" if lang == "English" else "t-testi"

        if shapiro_control.pvalue < 0.05 or shapiro_sample.pvalue < 0.05:
            test_type = "Nonparametric" if lang == "English" else "Nonparametrik"
            test_method = "Mann-Whitney U Test" if lang == "English" else "Mann-Whitney U Testi"

        test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue if test_type == "Parametric" else stats.mannwhitneyu(control_delta_ct, sample_delta_ct).pvalue

        significance = "Significant" if test_pvalue < 0.05 else "Not Significant"
        significance = "Anlamlı" if lang == "Türkçe" else significance

        stats_data.append({
            "Target Gene": f"Target Gene {i+1}" if lang == "English" else f"Hedef Gen {i+1}",
            "Patient Group": f"Patient Group {j+1}" if lang == "English" else f"Hasta Grubu {j+1}",
            "Test Type": test_type,
            "Used Test": test_method,
            "Test P-value": test_pvalue,
            "Significance": significance
        })
        data.append({
            "Target Gene" if lang == "English" else "Hedef Gen": f"Target Gene {i+1}" if lang == "English" else f"Hedef Gen {i+1}",
            "Patient Group" if lang == "English" else "Hasta Grubu": f"Patient Group {j+1}" if lang == "English" else f"Hasta Grubu {j+1}",
            "ΔΔCt": delta_delta_ct,
            "Gene Expression Change (2^(-ΔΔCt))" if lang == "English" else "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
            "Regulation Status" if lang == "English" else "Regülasyon Durumu": regulation_status,
            "ΔCt (Control)" if lang == "English" else "ΔCt (Kontrol)": avg_control_delta_ct,
            "ΔCt (Patient)" if lang == "English" else "ΔCt (Hasta)": avg_sample_delta_ct
        })

# Giriş Verileri Tablosunu Göster
if input_values_table: 
    st.subheader("📋 Input Data Table" if lang == "English" else "📋 Giriş Verileri Tablosu") 
    input_df = pd.DataFrame(input_values_table) 
    st.write(input_df) 

    csv = input_df.to_csv(index=False).encode("utf-8") 
    st.download_button(
        label="📥 Download CSV" if lang == "English" else "📥 CSV İndir", 
        data=csv, 
        file_name="input_data.csv" if lang == "English" else "giris_verileri.csv", 
        mime="text/csv"
    ) 

# Sonuçlar Tablosunu Göster
if data:
    st.subheader("📊 Results" if lang == "English" else "📊 Sonuçlar")
    df = pd.DataFrame(data)
    st.write(df)

# İstatistik Sonuçları
if stats_data:
    st.subheader("📈 Statistical Results" if lang == "English" else "📈 İstatistik Sonuçları")
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
    
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Statistical Results as CSV" if lang == "English" else "📥 İstatistik Sonuçlarını CSV Olarak İndir", 
        data=csv_stats, 
        file_name="statistical_results.csv" if lang == "English" else "istatistik_sonuclari.csv", 
        mime="text/csv"
    )

# Grafik oluşturma (her hedef gen için bir grafik oluşturulacak)
for i in range(num_target_genes):
    st.subheader(f"Target Gene {i+1} - Patient and Control Group Distribution Graph" if lang == "English" else f"Hedef Gen {i+1} - Hasta ve Kontrol Grubu Dağılım Grafiği")
    
    # Kontrol Grubu Verileri
    control_target_ct_values = [
        d["Target Gene Ct Value"] if lang == "English" else d["Hedef Gen Ct Değeri"] for d in input_values_table
        if d["Group"] == "Control" if lang == "English" else d["Grup"] == "Kontrol" and d["Target Gene"] if lang == "English" else d["Hedef Gen"] == f"Target Gene {i+1}" if lang == "English" else f"Hedef Gen {i+1}"
    ]
    
    control_reference_ct_values = [
        d["Reference Ct"] if lang == "English" else d["Referans Ct"] for d in input_values_table
        if d["Group"] == "Control" if lang == "English" else d["Grup"] == "Kontrol" and d["Target Gene"] if lang == "English" else d["Hedef Gen"] == f"Target Gene {i+1}" if lang == "English" else f"Hedef Gen {i+1}"
    ]
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f"⚠️ Error: Missing data for Target Gene {i+1} in Control Group!" if lang == "English" else f"⚠️ Hata: Kontrol Grubu için Hedef Gen {i+1} verileri eksik!")
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
        name="Control Group Average" if lang == "English" else "Kontrol Grubu Ortalama"
    ))

    # Hasta Gruplarının Ortalama Çizgileri
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d["ΔCt (Patient)"] if lang == "English" else d["ΔCt (Hasta)"] for d in input_values_table 
            if d["Group"] == f"Patient Group {j+1}" if lang == "English" else d["Grup"] == f"Hasta Grubu {j+1}" and d["Target Gene"] if lang == "English" else d["Hedef Gen"] == f"Target Gene {i+1}" if lang == "English" else f"Hedef Gen {i+1}"
        ]
    
        if not sample_delta_ct_values:
            continue  # Eğer hasta grubuna ait veri yoksa, bu hasta grubunu atla
        
        average_sample_delta_ct = np.mean(sample_delta_ct_values)
        fig.add_trace(go.Scatter(
            x=[(j + 1.8), (j + 2.2)],  
            y=[average_sample_delta_ct, average_sample_delta_ct],  
            mode='lines',
            line=dict(color='black', width=4),
            name=f"Patient Group {j+1} Average" if lang == "English" else f"Hasta Grubu {j+1} Ortalama"
        ))

    # Veri Noktaları (Kontrol Grubu)
    fig.add_trace(go.Scatter(
        x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
        y=control_delta_ct,
        mode='markers',  
        name="Control Group" if lang == "English" else "Kontrol Grubu",
        marker=dict(color='blue'),
        text=[f"Control {value:.2f}, Sample {idx+1}" if lang == "English" else f"Kontrol {value:.2f}, Örnek {idx+1}" for idx, value in enumerate(control_delta_ct)],
        hoverinfo='text'
    ))

    # Veri Noktaları (Hasta Grupları)
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d["ΔCt (Patient)"] if lang == "English" else d["ΔCt (Hasta)"] for d in input_values_table 
            if d["Group"] == f"Patient Group {j+1}" if lang == "English" else d["Grup"] == f"Hasta Grubu {j+1}" and d["Target Gene"] if lang == "English" else d["Hedef Gen"] == f"Target Gene {i+1}" if lang == "English" else f"Hedef Gen {i+1}"
        ]
    
        if not sample_delta_ct_values:
            continue  # Eğer hasta grubuna ait veri yoksa, bu hasta grubunu atla
        
        fig.add_trace(go.Scatter(
            x=np.ones(len(sample_delta_ct_values)) * (j + 2) + np.random.uniform(-0.05, 0.05, len(sample_delta_ct_values)),
            y=sample_delta_ct_values,
            mode='markers',  
            name=f"Patient Group {j+1}" if lang == "English" else f"Hasta Grubu {j+1}",
            marker=dict(color='red'),
            text=[f"Patient {value:.2f}, Sample {idx+1}" if lang == "English" else f"Hasta {value:.2f}, Örnek {idx+1}" for idx, value in enumerate(sample_delta_ct_values)],
            hoverinfo='text'
        ))

    # Grafik ayarları
    fig.update_layout(
        title=f"Target Gene {i+1} - ΔCt Distribution" if lang == "English" else f"Hedef Gen {i+1} - ΔCt Dağılımı",
        xaxis=dict(
            tickvals=[1] + [i + 2 for i in range(num_patient_groups)],
            ticktext=["Control Group" if lang == "English" else "Kontrol Grubu"] + [f"Patient Group {i+1}" if lang == "English" else f"Hasta Grubu {i+1}" for i in range(num_patient_groups)],
            title="Group" if lang == "English" else "Grup"
        ),
        yaxis=dict(title="ΔCt Value" if lang == "English" else "ΔCt Değeri"),
        showlegend=True
    )

    st.plotly_chart(fig)

else:
    st.info("At least one valid dataset is required to generate the graph." if lang == "English" else "Grafik oluşturulabilmesi için en az bir geçerli veri seti gereklidir.")

# PDF rapor oluşturma
def create_pdf(results, stats, input_df, lang="Turkish"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()

    # Başlık
    title = "Gene Expression Analysis Report" if lang == "English" else "Gen Ekspresyon Analizi Raporu"
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    # Giriş Verileri Tablosu Başlığı
    input_data_title = "Input Data Table:" if lang == "English" else "Giriş Verileri Tablosu:"
    elements.append(Paragraph(input_data_title, styles['Heading2']))
    
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
    results_title = "Results:" if lang == "English" else "Sonuçlar:"
    elements.append(Paragraph(results_title, styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for result in results:
        text = (
            f"{result['Target Gene'] if lang == 'English' else result['Hedef Gen']} - "
            f"{result['Patient Group'] if lang == 'English' else result['Hasta Grubu']} | "
            f"ΔΔCt: {result['ΔΔCt']:.2f} | 2^(-ΔΔCt): {result['Gene Expression Change (2^(-ΔΔCt))'] if lang == 'English' else result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']:.2f} | "
            f"{result['Regulation Status'] if lang == 'English' else result['Regülasyon Durumu']}"
        )
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # İstatistiksel Sonuçlar
    stats_title = "Statistical Results:" if lang == "English" else "İstatistiksel Sonuçlar:"
    elements.append(Paragraph(stats_title, styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for stat in stats:
        text = (
            f"{stat['Target Gene'] if lang == 'English' else stat['Hedef Gen']} - "
            f"{stat['Patient Group'] if lang == 'English' else stat['Hasta Grubu']} | "
            f"Test: {stat['Used Test'] if lang == 'English' else stat['Kullanılan Test']} | "
            f"p-value: {stat['Test P-value'] if lang == 'English' else stat['Test P-değeri']:.4f} | "
            f"{stat['Significance'] if lang == 'English' else stat['Anlamlılık']}"
        )
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # İstatistiksel Değerlendirme
    eval_title = "Statistical Evaluation:" if lang == "English" else "İstatistiksel Değerlendirme:"
    elements.append(Paragraph(eval_title, styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    explanation = (
        "During statistical evaluation, data distribution was analyzed using the Shapiro-Wilk test. "
        "If normality was met, equality of variances was checked with the Levene test. "
        "If variance equality was present, an independent sample t-test was applied; otherwise, Welch's t-test was used. "
        "If normal distribution was not met, the non-parametric Mann-Whitney U test was applied. "
        "Significance was determined based on p < 0.05 criteria."
    ) if lang == "English" else (
        "İstatistiksel değerlendirme sürecinde veri dağılımı Shapiro-Wilk testi ile analiz edilmiştir. "
        "Normallik sağlanırsa, gruplar arasındaki varyans eşitliği Levene testi ile kontrol edilmiştir. "
        "Varyans eşitliği varsa bağımsız örneklem t-testi, yoksa Welch t-testi uygulanmıştır. "
        "Eğer normal dağılım sağlanmazsa, parametrik olmayan Mann-Whitney U testi kullanılmıştır. "
        "Sonuçların anlamlılığı p < 0.05 kriterine göre belirlenmiştir."
    )
    
    for line in explanation.split(". "):
        elements.append(Paragraph(line.strip() + '.', styles['Normal']))
        elements.append(Spacer(1, 6))
    
    doc.build(elements)
    buffer.see
