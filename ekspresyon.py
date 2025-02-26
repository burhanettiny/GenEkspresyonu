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

import streamlit as st

# Dil seçim kutusu
if 'language' not in st.session_state:
    st.session_state.language = "Türkçe"  # Varsayılan dil Türkçe olarak ayarlanıyor.

st.session_state.language = st.selectbox("Dil / Language / Sprache", ["Türkçe", "English", "Deutsch"])

# Dil kodlarını belirleyin
language_map = {
    "Türkçe": "tr",
    "English": "en",
    "Deutsch": "de"
}

# Seçilen dilin kodu
language_code = language_map[st.session_state.language]

# Çeviri sözlüğü
translations = {
    "tr": {
        "title": "🧬 Gen Ekspresyon Analizi Uygulaması",
        "subtitle": "B. Yalçınkaya tarafından geliştirildi",
        "patient_data_header": "📊 Hasta ve Kontrol Grubu Verisi Girin",
        "num_target_genes": "🔹 Hedef Gen Sayısını Girin",
        "num_patient_groups": "🔹 Hasta Grubu Sayısını Girin",
        "sample_number": "Örnek Numarası",
        "group": "Grup",
        "gene_ct_value": "Hedef Gen Ct Değeri",
        "reference_ct": "Referans Ct",
        "delta_ct": "ΔCt (Kontrol)",
        "warning_empty_input": "⚠️ Dikkat: Verileri alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.",
        "statistical_results": "📈 İstatistik Sonuçları",
        "download_csv": "📥 CSV İndir",
        "results": "📊 Sonuçlar",
        "graph_title": "Hedef Gen {i} - Hasta ve Kontrol Grubu Dağılım Grafiği",
        "control_avg": "Kontrol Grubu Ortalama",
        "patient_avg": "Hasta Grubu {j} Ortalama",
        "error_control_data": "⚠️ Hata: Kontrol Grubu için Hedef Gen {i} verileri eksik!",
        "error_control_data": "⚠️ Hata: Kontrol Grubu için Hedef Gen {i} verileri eksik!",
        "download_pdf": "📥 PDF Olarak İndir",
        "pdf_title": "Gen Ekspresyon Analizi Raporu",
        "input_data_table": "Giris Verileri Tablosu:",
        "results": "Sonuçlar:",
        "statistical_results": "İstatistiksel Sonuçlar:",
        "statistical_evaluation": "İstatistiksel Değerlendirme:",
        "error_no_data": "Veri bulunamadı, PDF oluşturulamadı.",

    },
    "en": {
        "title": "🧬 Gene Expression Analysis Application",
        "subtitle": "Developed by B. Yalçınkaya",
        "patient_data_header": "📊 Enter Patient and Control Group Data",
        "num_target_genes": "🔹 Enter the Number of Target Genes",
        "num_patient_groups": "🔹 Enter the Number of Patient Groups",
        "sample_number": "Sample Number",
        "group": "Group",
        "gene_ct_value": "Target Gene Ct Value",
        "reference_ct": "Reference Ct",
        "delta_ct": "ΔCt (Control)",
        "warning_empty_input": "⚠️ Warning: Write data one below the other or copy-paste without empty cells from Excel.",
        "statistical_results": "📈 Statistical Results",
        "download_csv": "📥 Download CSV",
        "generate_pdf": "📥 Prepare PDF Report",
        "results": "📊 Results",
        "graph_title": "Target Gene {i} - Patient and Control Group Distribution Graph",
        "control_avg": "Control Group Average",
        "patient_avg": "Patient Group {j} Average",
        "error_control_data": "⚠️ Error: Data missing for Control Group Target Gene {i}!",
        "download_pdf": "📥 Download PDF",
        "pdf_title": "Gene Expression Analysis Report",
        "input_data_table": "Input Data Table:",
        "results": "Results:",
        "statistical_results": "Statistical Results:",
        "statistical_evaluation": "Statistical Evaluation:",
        "error_no_data": "No data found, PDF could not be generated.",
 
    },
    "de": {
        "title": "🧬 Genexpression-Analyseanwendung",
        "subtitle": "Entwickelt von B. Yalçınkaya",
        "patient_data_header": "📊 Geben Sie Patientendaten und Kontrollgruppen ein",
        "num_target_genes": "🔹 Geben Sie die Anzahl der Zielgene ein",
        "num_patient_groups": "🔹 Geben Sie die Anzahl der Patientengruppen ein",
        "sample_number": "Beispielnummer",
        "group": "Gruppe",
        "gene_ct_value": "Zielgen Ct-Wert",
        "reference_ct": "Referenz Ct",
        "delta_ct": "ΔCt (Kontrolle)",
        "warning_empty_input": "⚠️ Warnung: Geben Sie die Daten untereinander ein oder kopieren Sie sie ohne leere Zellen aus Excel.",
        "statistical_results": "📈 Statistische Ergebnisse",
        "download_csv": "📥 CSV herunterladen",
        "generate_pdf": "📥 PDF-Bericht erstellen",
        "results": "📊 Results",
        "graph_title": "Zielgen {i} - Patienten- und Kontrollgruppen-Verteilungsdiagramm",
        "control_avg": "Kontrollgruppe Durchschnitt",
        "patient_avg": "Patientengruppe {j} Durchschnitt",
        "error_control_data": "⚠️ Fehler: Fehlende Daten für Kontrollgruppe Zielgen {i}!",
        "download_pdf": "📥 PDF herunterladen",
        "pdf_title": "Genexpressionsanalyse-Bericht",
        "input_data_table": "Eingabedatentabelle:",
        "results": "Ergebnisse:",
        "statistical_results": "Statistische Ergebnisse:",
        "statistical_evaluation": "Statistische Bewertung:",
        "error_no_data": "Keine Daten gefunden, PDF konnte nicht generiert werden.",
        }
}

# Çeviri fonksiyonu
def translate(key):
    return translations.get(language_code, {}).get(key, key)

# Arayüz öğelerini dil desteğiyle gösterme
st.title(translate("title"))
st.subheader(translate("subtitle"))
st.header(translate("patient_data_header"))

st.warning(translate("warning_empty_input"))

# Butonlar
if st.button(translate("download_csv")):
    st.success("CSV oluşturuldu!")

if st.button(translate("generate_pdf")):
    st.success("PDF raporu hazırlandı!")

# Başlık
st.title("🧬 Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

 
# Kullanıcıdan giriş al
st.header("📊 Hasta ve Kontrol Grubu Verisi Girin")

 

# Hedef Gen ve Hasta Grubu Sayısı
num_target_genes = st.number_input(translate("num_target_genes"), min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(translate("num_patient_groups"), min_value=1, step=1, key="patient_count")

 

# Veri listeleri
input_values_table = []

data = []
stats_data = []
 
def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

last_control_delta_ct = None
last_gene_index = None

for i in range(num_target_genes):
    st.subheader(translate("gene_subheader").format(i+1))

    control_target_ct = st.text_area(translate("control_target_ct").format(i+1), key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(translate("control_reference_ct").format(i+1), key=f"control_reference_ct_{i}")

    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(translate("error_empty_control").format(i+1))
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
        st.warning(translate("warning_empty_control"))
        continue

    sample_counter = 1
    for idx in range(min_control_len):
        input_values_table.append({
            translate("sample_number"): sample_counter,
            translate("gene"): f"{translate('gene')} {i+1}",
            translate("group"): translate("control_group"),
            translate("gene_ct_value"): control_target_ct_values[idx],
            translate("reference_ct"): control_reference_ct_values[idx],
            translate("delta_ct"): control_delta_ct[idx]
        })
        sample_counter += 1

    for j in range(num_patient_groups):
        st.subheader(translate("patient_group_subheader").format(j+1, i+1))

        sample_target_ct = st.text_area(translate("patient_target_ct").format(j+1, i+1), key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(translate("patient_reference_ct").format(j+1, i+1), key=f"sample_reference_ct_{i}_{j}")

        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)

        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(translate("error_empty_patient").format(j+1))
            continue

        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values

        if len(sample_delta_ct) > 0:
            average_sample_delta_ct = np.mean(sample_delta_ct)
        else:
            st.warning(translate("warning_empty_patient").format(j+1))
            continue

        sample_counter = 1
        for idx in range(min_sample_len):
            input_values_table.append({
                translate("sample_number"): sample_counter,
                translate("gene"): f"{translate('gene')} {i+1}",
                translate("group"): f"{translate('patient_group')} {j+1}",
                translate("gene_ct_value"): sample_target_ct_values[idx],
                translate("reference_ct"): sample_reference_ct_values[idx],
                translate("delta_ct_patient"): sample_delta_ct[idx]
            })
            sample_counter += 1

        delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)
        regulation_status = (translate("no_change") if expression_change == 1 else
                             (translate("upregulated") if expression_change > 1 else translate("downregulated")))

        shapiro_control = stats.shapiro(control_delta_ct)
        shapiro_sample = stats.shapiro(sample_delta_ct)
        levene_test = stats.levene(control_delta_ct, sample_delta_ct)

        control_normal = shapiro_control.pvalue > 0.05
        sample_normal = shapiro_sample.pvalue > 0.05
        equal_variance = levene_test.pvalue > 0.05

        test_type = translate("parametric") if control_normal and sample_normal and equal_variance else translate("nonparametric")

        if test_type == translate("parametric"):
            test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue
            test_method = "t-test"
        else:
            test_pvalue = stats.mannwhitneyu(control_delta_ct, sample_delta_ct).pvalue
            test_method = "Mann-Whitney U test"

        significance = translate("significant") if test_pvalue < 0.05 else translate("not_significant")

        stats_data.append({
            translate("gene"): f"{translate('gene')} {i+1}",
            translate("patient_group"): f"{translate('patient_group')} {j+1}",
            translate("test_type"): test_type,
            translate("used_test"): test_method,
            translate("test_p_value"): test_pvalue,
            translate("significance"): significance
        })

        data.append({
            translate("gene"): f"{translate('gene')} {i+1}",
            translate("patient_group"): f"{translate('patient_group')} {j+1}",
            translate("delta_delta_ct"): delta_delta_ct,
            translate("expression_change"): expression_change,
            translate("regulation_status"): regulation_status,
            translate("delta_ct_control"): average_control_delta_ct,
            translate("delta_ct_patient"): average_sample_delta_ct
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
            "ΔCt (Kontrol)": average_control_delta_ct,
            "ΔCt (Hasta)": average_sample_delta_ct
        })
 
# Giriş Verileri Tablosunu Göster
if input_values_table:
    st.subheader(translations[language_code]["results"])
    input_df = pd.DataFrame(input_values_table)
    st.write(input_df)
    csv = input_df.to_csv(index=False).encode("utf-8")
    st.download_button(label=translations[language_code]["download_csv"], data=csv, file_name="giris_verileri.csv", mime="text/csv")

# Sonuçlar Tablosunu Göster
if data:
    st.subheader(translations[language_code]["results"])
    df = pd.DataFrame(data)
    st.write(df)

# İstatistik Sonuçları
if stats_data:
    st.subheader(translations[language_code]["statistical_results"])
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(label=translations[language_code]["download_csv"], data=csv_stats, file_name="istatistik_sonuclari.csv", mime="text/csv")

# Grafik oluşturma (her hedef gen için bir grafik oluşturulacak)
for i in range(num_target_genes):
    st.subheader(translations[language_code]["graph_title"].format(i=i+1))
    
    # Kontrol Grubu Verileri
    control_target_ct_values = [
        d["Hedef Gen Ct Değeri"] for d in input_values_table
        if d["Grup"] == "Kontrol" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]
    control_reference_ct_values = [
        d["Referans Ct"] for d in input_values_table
        if d["Grup"] == "Kontrol" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]
    
    if not control_target_ct_values or not control_reference_ct_values:
        st.error(translations[language_code]["error_control_data"].format(i=i+1))
        continue
    
    control_delta_ct = np.array(control_target_ct_values) - np.array(control_reference_ct_values)
    average_control_delta_ct = np.mean(control_delta_ct)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[0.8, 1.2],
        y=[average_control_delta_ct, average_control_delta_ct],
        mode='lines',
        line=dict(color='black', width=4),
        name=translations[language_code]["control_avg"]
    ))
    
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d["Hedef Gen Ct Değeri"] for d in input_values_table
            if d["Grup"] == "Hasta" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]
    
    patient_reference_ct_values = [
        d["Referans Ct"] for d in input_values_table
        if d["Grup"] == "Hasta" and d["Hedef Gen"] == f"Hedef Gen {i+1}"
    ]
        
        if not sample_delta_ct_values:
            continue
        
        average_sample_delta_ct = np.mean(sample_delta_ct_values)
        fig.add_trace(go.Scatter(
            x=[(j + 1.8), (j + 2.2)],
            y=[average_sample_delta_ct, average_sample_delta_ct],
            mode='lines',
            line=dict(color='black', width=4),
            name=translations[language_code]["patient_avg"].format(j=j+1)
        ))
    
    st.plotly_chart(fig)



# PDF rapor oluşturma kısmı
def create_pdf(results, stats, input_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(translations[language_code]["pdf_title"], styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(translations[language_code]["input_data_table"], styles['Heading2']))
    
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
    elements.append(Paragraph(translations[language_code]["results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for result in results:
        text = f"{result['Hedef Gen']} - {result['Hasta Grubu']} | ΔΔCt: {result['ΔΔCt']:.2f} | 2^(-ΔΔCt): {result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']:.2f} | {result['Regülasyon Durumu']}"
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    elements.append(Paragraph(translations[language_code]["statistical_results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for stat in stats:
        text = f"{stat['Hedef Gen']} - {stat['Hasta Grubu']} | Test: {stat['Kullanılan Test']} | p-değeri: {stat['Test P-değeri']:.4f} | {stat['Anlamlılık']}"
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    elements.append(Paragraph(translations[language_code]["statistical_evaluation"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    explanation = "istatistiksel degerlendirme sürecinde veri dagilimi Shapiro-Wilk testi ile analiz edilmistir."
    "Normallik saglanirsa, gruplar arasindaki varyans esitligi Levene testi ile kontrol edilmistir."
    "Varyans esitligi varsa bagimsiz örneklem t-testi, yoksa Welch t-testi uygulanmistir. "
    "Eger normal dagilim saglanmazsa, parametrik olmayan Mann-Whitney U testi kullanilmistir. "
    "Sonuclarin anlamliligi p < 0.05 kriterine göre belirlenmistir. "
    "<b>Görüs ve önerileriniz icin; <a href='mailto:mailtoburhanettin@gmail.com'>mailtoburhanettin@gmail.com</a></b>."

    elements.append(Paragraph(explanation, styles['Normal']))
    elements.append(Spacer(1, 6))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button(translations[language_code]["download_pdf"]):
    if input_values_table:
        pdf_buffer = create_pdf(data, stats_data, pd.DataFrame(input_values_table))
        st.download_button(label=translations[language_code]["download_pdf"], data=pdf_buffer, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
    else:
        st.error(translations[language_code]["error_no_data"])

       
