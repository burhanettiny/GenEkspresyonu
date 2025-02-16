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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

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

# Language selection
language = st.selectbox("Select Language", ["Türkçe", "English"])

# Titles and Descriptions
if language == "Türkçe":
    st.title("🧬 Gen Ekspresyon Analizi Uygulaması")
    st.markdown("### B. Yalçınkaya tarafından geliştirildi")
    st.header("📊 Hasta ve Kontrol Grubu Verisi Girin")
else:
    st.title("🧬 Gene Expression Analysis Application")
    st.markdown("### Developed by B. Yalçınkaya")
    st.header("📊 Enter Patient and Control Group Data")

# User input for number of genes and patient groups
if language == "Türkçe":
    num_target_genes = st.number_input("🔹 Hedef Gen Sayısını Girin", min_value=1, step=1, key="gene_count")
    num_patient_groups = st.number_input("🔹 Hasta Grubu Sayısını Girin", min_value=1, step=1, key="patient_count")
else:
    num_target_genes = st.number_input("🔹 Enter the Number of Target Genes", min_value=1, step=1, key="gene_count")
    num_patient_groups = st.number_input("🔹 Enter the Number of Patient Groups", min_value=1, step=1, key="patient_count")

# Data storage
input_values_table = []
data = []
stats_data = []

# Function to parse input data
def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# Graph for storing the control data of the last processed target gene
last_control_delta_ct = None
last_gene_index = None

for i in range(num_target_genes):
    if language == "Türkçe":
        st.subheader(f"🧬 Hedef Gen {i+1}")
    else:
        st.subheader(f"🧬 Target Gene {i+1}")
    
    # Control Group Data
    if language == "Türkçe":
        control_target_ct = st.text_area(f"🟦 Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
        control_reference_ct = st.text_area(f"🟦 Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    else:
        control_target_ct = st.text_area(f"🟦 Control Group Target Gene {i+1} Ct Values", key=f"control_target_ct_{i}")
        control_reference_ct = st.text_area(f"🟦 Control Group Reference Gene {i+1} Ct Values", key=f"control_reference_ct_{i}")
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        if language == "Türkçe":
            st.error(f"⚠️ Dikkat: Kontrol Grubu {i+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın")
        else:
            st.error(f"⚠️ Warning: Please enter the control group data for Gene {i+1} correctly without empty cells.")
        continue
    
    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_target_ct_values = control_target_ct_values[:min_control_len]
    control_reference_ct_values = control_reference_ct_values[:min_control_len]
    control_delta_ct = control_target_ct_values - control_reference_ct_values
    
    if len(control_delta_ct) > 0:
        average_control_delta_ct = np.mean(control_delta_ct)
        last_control_delta_ct = control_delta_ct  
        last_gene_index = i
    else:
        if language == "Türkçe":
            st.warning("⚠️ Dikkat: Kontrol grubu Ct verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın")
        else:
            st.warning("⚠️ Warning: Please enter the control group Ct values correctly.")
        continue
    
    sample_counter = 1
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
    
    # Patient Group Data
    for j in range(num_patient_groups):
        if language == "Türkçe":
            st.subheader(f"🩸 Hasta Grubu {j+1} - Hedef Gen {i+1}")
        else:
            st.subheader(f"🩸 Patient Group {j+1} - Target Gene {i+1}")
        
        sample_target_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"🟥 Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}_{j}")
        
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)
        
        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            if language == "Türkçe":
                st.error(f"⚠️ Dikkat: Hasta Grubu {j+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.")
            else:
                st.error(f"⚠️ Warning: Please enter the patient group data for Group {j+1} correctly without empty cells.")
            continue
        
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
        if len(sample_delta_ct) > 0:
            average_sample_delta_ct = np.mean(sample_delta_ct)
        else:
            if language == "Türkçe":
                st.warning(f"⚠️ Dikkat: Hasta grubu {j+1} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.")
            else:
                st.warning(f"⚠️ Warning: Please enter the patient group data for Group {j+1} correctly.")
            continue
    sample_counter = 1  # Reset sample counter for each patient group
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

    # ΔΔCt and Gene Expression Change Calculation
    delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
    expression_change = 2 ** (-delta_delta_ct)

    regulation_status = "Değişim Yok" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")

    # Statistical Tests
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
        "Regülasyon Durumu": regulation_status,
        "ΔCt (Kontrol)": average_control_delta_ct,
        "ΔCt (Hasta)": average_sample_delta_ct
    })

# Display Input Data Table
if input_values_table:
    if language == "Türkçe":
        st.subheader("📋 Giriş Verileri Tablosu")
    else:
        st.subheader("📋 Input Data Table")
    input_df = pd.DataFrame(input_values_table)
    st.write(input_df)

    csv = input_df.to_csv(index=False).encode("utf-8")
    if language == "Türkçe":
        st.download_button(label="📥 CSV İndir", data=csv, file_name="giris_verileri.csv", mime="text/csv")
    else:
        st.download_button(label="📥 Download CSV", data=csv, file_name="input_data.csv", mime="text/csv")

# Display Results Table
if data:
    if language == "Türkçe":
        st.subheader("📊 Sonuçlar")
    else:
        st.subheader("📊 Results")
    df = pd.DataFrame(data)
    st.write(df)

# Display Statistical Results
if stats_data:
    if language == "Türkçe":
        st.subheader("📈 İstatistik Sonuçları")
    else:
        st.subheader("📈 Statistical Results")
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)

    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    if language == "Türkçe":
        st.download_button(label="📥 İstatistik Sonuçlarını CSV Olarak İndir", data=csv_stats, file_name="istatistik_sonuclari.csv", mime="text/csv")
    else:
        st.download_button(label="📥 Download Statistical Results CSV", data=csv_stats, file_name="statistical_results.csv", mime="text/csv")

# Create Graph for each target gene
for i in range(num_target_genes):
    if language == "Türkçe":
        st.subheader(f"Hedef Gen {i+1} - Hasta ve Kontrol Grubu Dağılım Grafiği")
    else:
        st.subheader(f"Target Gene {i+1} - Patient and Control Group Distribution Graph")
    
    # Control Group Data
    control_target_ct_values = [
        d["Hedef Gen Ct Değeri"] for d in input_values_table
        if d["Grup"] == "Kontrol" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]
    
    control_reference_ct_values = [
        d["Referans Ct"] for d in input_values_table
        if d["Grup"] == "Kontrol" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        if language == "Türkçe":
            st.error(f"⚠️ Hata: Kontrol Grubu için Hedef Gen {i+1} verileri eksik!")
        else:
            st.error(f"⚠️ Error: Missing data for Control Group Target Gene {i+1}!")
        continue
control_delta_ct = np.array(control_target_ct_values) - np.array(control_reference_ct_values)
average_control_delta_ct = np.mean(control_delta_ct)

# Patient Group Data
fig = go.Figure()

# Control Group Average Line
fig.add_trace(go.Scatter(
    x=[0.8, 1.2],  
    y=[average_control_delta_ct, average_control_delta_ct],  
    mode='lines',
    line=dict(color='black', width=4),
    name='Kontrol Grubu Ortalama' if language == "Türkçe" else 'Control Group Average'
))

# Patient Groups Average Lines
for j in range(num_patient_groups):
    sample_delta_ct_values = [
        d["ΔCt (Hasta)"] for d in input_values_table 
        if d["Grup"] == f"Hasta Grubu {j+1}" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]

    if not sample_delta_ct_values:
        continue  # Skip if no data for patient group

    average_sample_delta_ct = np.mean(sample_delta_ct_values)
    fig.add_trace(go.Scatter(
        x=[(j + 1.8), (j + 2.2)],  
        y=[average_sample_delta_ct, average_sample_delta_ct],  
        mode='lines',
        line=dict(color='black', width=4),
        name=f'Hasta Grubu {j+1} Ortalama' if language == "Türkçe" else f'Patient Group {j+1} Average'
    ))

# Data Points (Control Group)
fig.add_trace(go.Scatter(
    x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
    y=control_delta_ct,
    mode='markers',  
    name='Kontrol Grubu' if language == "Türkçe" else 'Control Group',
    marker=dict(color='blue'),
    text=[f'Kontrol {value:.2f}, Örnek {idx+1}' if language == "Türkçe" else f'Control {value:.2f}, Sample {idx+1}' for idx, value in enumerate(control_delta_ct)],
    hoverinfo='text'
))

# Data Points (Patient Groups)
for j in range(num_patient_groups):
    sample_delta_ct_values = [
        d["ΔCt (Hasta)"] for d in input_values_table 
        if d["Grup"] == f"Hasta Grubu {j+1}" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]

    if not sample_delta_ct_values:
        continue  # Skip if no data for patient group

    fig.add_trace(go.Scatter(
        x=np.ones(len(sample_delta_ct_values)) * (j + 2) + np.random.uniform(-0.05, 0.05, len(sample_delta_ct_values)),
        y=sample_delta_ct_values,
        mode='markers',  
        name=f'Hasta Grubu {j+1}' if language == "Türkçe" else f'Patient Group {j+1}',
        marker=dict(color='red'),
        text=[f'Hasta {value:.2f}, Örnek {idx+1}' if language == "Türkçe" else f'Patient {value:.2f}, Sample {idx+1}' for idx, value in enumerate(sample_delta_ct_values)],
        hoverinfo='text'
    ))

# Graph settings
if some_condition:  # Replace `some_condition` with the actual condition you want to check
    fig.update_layout(
        title=f"Hedef Gen {i+1} - ΔCt Dağılımı" if language == "Türkçe" else f"Target Gene {i+1} - ΔCt Distribution",
        xaxis=dict(
            tickvals=[1] + [i + 2 for i in range(num_patient_groups)],
            ticktext=['Kontrol Grubu'] + [f'Hasta Grubu {i+1}' if language == "Türkçe" else f'Patient Group {i+1}' for i in range(num_patient_groups)],
            title='Grup' if language == "Türkçe" else 'Group'
        ),
        yaxis=dict(title='ΔCt Değeri' if language == "Türkçe" else 'ΔCt Value'),
        showlegend=True
    )

    st.plotly_chart(fig)
else:
    st.info("Grafik oluşturulabilmesi için en az bir geçerli veri seti gereklidir." if language == "Türkçe" else "At least one valid dataset is required to generate the graph.")

# PDF report creation
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(results, stats, input_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("Gen Ekspresyon Analizi Raporu", styles['Title']) if language == "Türkçe" else Paragraph("Gene Expression Analysis Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Input Data Table Title
    elements.append(Paragraph("Giris Verileri Tablosu:" if language == "Türkçe" else "Input Data Table:", styles['Heading2']))
# Table Data
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

# Results Title
elements.append(Paragraph("Sonuçlar:" if language == "Türkçe" else "Results:", styles['Heading2']))
elements.append(Spacer(1, 12))

for result in results:
    text = (
        f"{result['Hedef Gen']} - {result['Hasta Grubu']} | ΔΔCt: {result['ΔΔCt']:.2f} | "
        f"2^(-ΔΔCt): {result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']:.2f} | {result['Regülasyon Durumu']}" 
        if language == "Türkçe" 
        else f"{result['Target Gene']} - {result['Patient Group']} | ΔΔCt: {result['ΔΔCt']:.2f} | "
             f"2^(-ΔΔCt): {result['Gene Expression Change (2^(-ΔΔCt))']:.2f} | {result['Regulation Status']}"
    )
    elements.append(Paragraph(text, styles['Normal']))
    elements.append(Spacer(1, 6))

elements.append(PageBreak())

# Statistical Results
elements.append(Paragraph("İstatistiksel Sonuçlar:" if language == "Türkçe" else "Statistical Results:", styles['Heading2']))
elements.append(Spacer(1, 12))

for stat in stats:
    text = (
        f"{stat['Hedef Gen']} - {stat['Hasta Grubu']} | Test: {stat['Kullanılan Test']} | "
        f"p-değeri: {stat['Test P-değeri']:.4f} | {stat['Anlamlılık']}" 
        if language == "Türkçe" 
        else f"{stat['Target Gene']} - {stat['Patient Group']} | Test: {stat['Test Used']} | "
             f"p-value: {stat['Test P-value']:.4f} | {stat['Significance']}"
    )
    elements.append(Paragraph(text, styles['Normal']))
    elements.append(Spacer(1, 6))

elements.append(PageBreak())

# Statistical Evaluation (Ensure this is not indented under any function or loop)
elements.append(Paragraph("İstatistiksel Değerlendirme:" if language == "Türkçe" else "Statistical Evaluation:", styles['Heading2']))
elements.append(Spacer(1, 12))

explanation = (
    "İstatistiksel değerlendirme sürecinde veri dağılımı Shapiro-Wilk testi ile analiz edilmiştir. "
    "Normallik sağlanırsa, gruplar arasındaki varyans eşitliği Levene testi ile kontrol edilmiştir. "
    "Varyans eşitliği varsa bağımsız örneklem t-testi, yoksa Welch t-testi uygulanmıştır. "
    "Eğer normal dağılım sağlanmazsa, parametrik olmayan Mann-Whitney U testi kullanılmıştır. "
    "Sonuçların anlamlılığı p < 0.05 kriterine göre belirlenmiştir. "
    "<b>Görüş ve önerileriniz için; <a href='mailto:mailtoburhanettin@gmail.com'>mailtoburhanettin@gmail.com</a></b>"
    if language == "Türkçe"
    else (
        "In the statistical evaluation process, data distribution was analyzed using the Shapiro-Wilk test. "
        "If normality is achieved, variance homogeneity between groups was checked with the Levene test. "
        "If variance homogeneity holds, the independent samples t-test was applied, otherwise the Welch t-test was used. "
        "If normal distribution is not met, the non-parametric Mann-Whitney U test was utilized. "
        "The significance of the results was determined based on the criterion p < 0.05. "
        "<b>For comments and suggestions; <a href='mailto:mailtoburhanettin@gmail.com'>mailtoburhanettin@gmail.com</a></b>"
    )
)

for line in explanation.split(". "):
    elements.append(Paragraph(line.strip() + '.', styles['Normal']))
    elements.append(Spacer(1, 6))

# Now, this block should be correctly indented.
doc.build(elements)
buffer.seek(0)
return buffer
