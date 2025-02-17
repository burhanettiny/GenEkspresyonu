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

# Dil Seçenekleri için Sözlük
language_dict = {
    "tr": {
        "control_group": "Kontrol Grubu",
        "patient_group": "Hasta Grubu",
        "mean_line": "Ortalama",
        "target_gene": "Hedef Gen",
        "no_data": "Grafik oluşturulabilmesi için en az bir geçerli veri seti gereklidir.",
        "group": "Grup",
        "delta_ct_value": "ΔCt Değeri",
        "input_data_table": "📋 Girdi Verisi Tablosu",
        "results": "📊 Sonuçlar",
        "statistical_results": "📈 İstatistiksel Sonuçlar",
        "download_csv": "📥 CSV Olarak İndir",
        "download_stats_csv": "📥 İstatistiksel Sonuçları CSV Olarak İndir"
    },
    "en": {
        "control_group": "Control Group",
        "patient_group": "Patient Group",
        "mean_line": "Average",
        "target_gene": "Target Gene",
        "no_data": "At least one valid dataset is required to create the graph.",
        "group": "Group",
        "delta_ct_value": "ΔCt Value",
        "input_data_table": "📋 Input Data Table",
        "results": "📊 Results",
        "statistical_results": "📈 Statistical Results",
        "download_csv": "📥 Download CSV",
        "download_stats_csv": "📥 Download Statistical Results as CSV"
    }
}

# Kullanıcının dil tercihini al
selected_language = st.selectbox("🔄 Choose Language", options=["tr", "en"])

# Kullanıcı diline göre etiketleri al
language = language_dict[selected_language]

# Title
st.title(f"🧬 Gene Expression Analysis Application - {language['target_gene']} Analysis")
st.markdown("### Developed by B. Yalçınkaya")

# User Input
st.header(f"📊 {language['input_data_table']}")

# Target Gene and Patient Group Count
num_target_genes = st.number_input(f"🔹 Enter the Number of {language['target_gene']}s", min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(f"🔹 Enter the Number of {language['patient_group']}s", min_value=1, step=1, key="patient_count")

# Data Lists
input_values_table = []
data = []
stats_data = []

def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# Variables to store the last processed control gene data for graphing
last_control_delta_ct = None
last_gene_index = None

for i in range(num_target_genes):
    st.subheader(f"🧬 {language['target_gene']} {i+1}")
    
    # Control Group Data
    control_target_ct = st.text_area(f"🟦 {language['control_group']} {language['target_gene']} {i+1} Ct Values", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"🟦 {language['control_group']} Reference Gene {i+1} Ct Values", key=f"control_reference_ct_{i}")
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f"⚠️ Warning: Enter {language['control_group']} {i+1} data in separate lines or paste from Excel without empty cells.")
        continue
    
    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_target_ct_values = control_target_ct_values[:min_control_len]
    control_reference_ct_values = control_reference_ct_values[:min_control_len]
    control_delta_ct = control_target_ct_values - control_reference_ct_values
    
    if len(control_delta_ct) > 0:
        average_control_delta_ct = np.mean(control_delta_ct)
        last_control_delta_ct = control_delta_ct  # Store for graphing
        last_gene_index = i
    else:
        st.warning(f"⚠️ Warning: Enter {language['control_group']} Ct data in separate lines or paste from Excel without empty cells.")
        continue
    
    sample_counter = 1  # Control group sample counter
    for idx in range(min_control_len):
        input_values_table.append({
            "Sample Number": sample_counter,
            "Target Gene": f"{language['target_gene']} {i+1}",
            "Group": language['control_group'],
            "Target Gene Ct Value": control_target_ct_values[idx],
            "Reference Ct": control_reference_ct_values[idx],  
            "ΔCt (Control)": control_delta_ct[idx]
        })
        sample_counter += 1
    
    # Patient Group Data
    for j in range(num_patient_groups):
        st.subheader(f"🩸 {language['patient_group']} {j+1} - {language['target_gene']} {i+1}")
        
        sample_target_ct = st.text_area(f"🟥 {language['patient_group']} {j+1} {language['target_gene']} {i+1} Ct Values", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"🟥 {language['patient_group']} {j+1} Reference Gene {i+1} Ct Values", key=f"sample_reference_ct_{i}_{j}")
        
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)
        
        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(f"⚠️ Warning: Enter {language['patient_group']} {j+1} data in separate lines or paste from Excel without empty cells.")
            continue
        
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
        if len(sample_delta_ct) > 0:
            average_sample_delta_ct = np.mean(sample_delta_ct)
        else:
            st.warning(f"⚠️ Warning: Enter {language['patient_group']} {j+1} data in separate lines or paste from Excel without empty cells.")
            continue
        
        sample_counter = 1  # Reset sample counter for each patient group
        for idx in range(min_sample_len):
            input_values_table.append({
                "Sample Number": sample_counter,
                "Target Gene": f"{language['target_gene']} {i+1}",
                "Group": f"{language['patient_group']} {j+1}",
                "Target Gene Ct Value": sample_target_ct_values[idx],
                "Reference Ct": sample_reference_ct_values[idx],
                "ΔCt (Patient)": sample_delta_ct[idx]
            })
            sample_counter += 1
        
        # Calculate ΔΔCt and Gene Expression Change
        delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)
        
        regulation_status = "No Change" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")
       
        # Statistical Tests
        shapiro_control = stats.shapiro(control_delta_ct)
        shapiro_sample = stats.shapiro(sample_delta_ct)
        levene_test = stats.levene(control_delta_ct, sample_delta_ct)

        control_normal = shapiro_control.pvalue > 0.05
        sample_normal = shapiro_sample.pvalue > 0.05
        equal_variance = levene_test.pvalue > 0.05

        test_type = "Parametric" if control_normal and sample_normal and equal_variance else "Nonparametric"

        if test_type == "Parametric":
            test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue
            test_method = "t-test"
        else:
            test_pvalue = stats.mannwhitneyu(control_delta_ct, sample_delta_ct).pvalue
            test_method = "Mann-Whitney U test"

        significance = "Significant" if test_pvalue < 0.05 else "Not Significant"

        stats_data.append({
            "Target Gene": f"{language['target_gene']} {i+1}",
            "Patient Group": f"{language['patient_group']} {j+1}",
            "Test Type": test_type,
            "Test Used": test_method,  
            "Test P-value": test_pvalue,
            "Significance": significance
        })

        data.append({
            "Target Gene": f"{language['target_gene']} {i+1}",
            "Patient Group": f"{language['patient_group']} {j+1}",
            "ΔΔCt": delta_delta_ct,
            "Gene Expression Change (2^(-ΔΔCt))": expression_change,
            "Regulation Status": regulation_status,
            "ΔCt (Control)": average_control_delta_ct,
            "ΔCt (Patient)": average_sample_delta_ct
        })

# Display Input Data Table
if input_values_table: 
    st.subheader(language['input_data_table']) 
    input_df = pd.DataFrame(input_values_table) 
    st.write(input_df) 

    csv = input_df.to_csv(index=False).encode("utf-8") 
    st.download_button(label=language['download_csv'], data=csv, file_name="input_data.csv", mime="text/csv") 

# Display Results Table
if data:
    st.subheader(language['results'])
    df = pd.DataFrame(data)
    st.write(df)

# Display Statistical Results
if stats_data:
    st.subheader(language['statistical_results'])
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
    
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(label=language['download_stats_csv'], data=csv_stats, file_name="statistical_results.csv", mime="text/csv")

# Generate Graphs (one per target gene)
for i in range(num_target_genes):
    st.subheader(f"{language['target_gene']} {i+1} - ΔCt Distribution")
    
    # Graph Control and Patient Groups ΔCt distribution
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=last_control_delta_ct,
        name=language['control_group'],
        marker_color='blue'
    ))

    for j in range(num_patient_groups):
        fig.add_trace(go.Box(
            y=data[i]['ΔCt (Patient)'],
            name=f"{language['patient_group']} {j+1}",
            marker_color='red'
        ))
        
    fig.update_layout(
        title=f"{language['target_gene']} {i+1} - ΔCt Distribution",
        xaxis=dict(
            title=language['group'],
            tickvals=[1] + [i+2 for i in range(num_patient_groups)],
            ticktext=[language['control_group']] + [f"{language['patient_group']} {i+1}" for i in range(num_patient_groups)]
        ),
        yaxis=dict(title=language['delta_ct_value'])
    )

    st.plotly_chart(fig)

else:
    st.info("Grafik oluşturulabilmesi için en az bir geçerli veri seti gereklidir.")

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
