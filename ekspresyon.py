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
from reportlab.lib.units import inch

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

translations = {
    "tr": {
        "title": "🧬 Gen Ekspresyon Analizi Uygulaması",
        "subtitle": "B. Yalçınkaya tarafından geliştirildi",
        "patient_data_header": "📊 Hasta ve Kontrol Grubu Verisi Girin",
        "num_target_genes": "🔹 Hedef Gen Sayısını Girin",
        "num_patient_groups": "🔹 Hasta Grubu Sayısını Girin",
        "sample_number": "Örnek Numarası",
        "Grup": "Grup",
        "x_axis_title": "Grup Adı",
        "ct_value": "Ct Değeri",
        "reference_ct": "Referans Ct",
        "delta_ct_control": "ΔCt (Kontrol)",
        "delta_ct_patient": "ΔCt (Hasta)",
        "warning_empty_input": "⚠️ Dikkat: Verileri alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.",
        "statistical_results": "📈 İstatistik Sonuçları",
        "download_csv": "📥 CSV İndir",
        "generate_pdf": "📥 PDF Raporu Hazırla",
        "pdf_report": "Gen Ekspresyon Analizi Raporu",
        "statistics": "istatistiksel Sonuçlar",
        "nil_mine": "📊 Sonuçlar",
        "gr_tbl": "📋 Giriş Verileri Tablosu",
        "control_group": "🧬 Kontrol Grubu",
        "patient_group": "🩸 Hasta Grubu",
        "ctrl_trgt_ct": "🟦 Kontrol Grubu Hedef Gen {i} Ct Değerleri",
        "ctrl_ref_ct": "🟦 Kontrol Grubu Referans Gen {i} Ct Değerleri",
        "hst_trgt_ct": "🩸 Hasta Grubu Hedef Gen {j} Ct Değerleri",
        "hst_ref_ct": "🩸 Hasta Grubu Referans Gen {j} Ct Değerleri",
        "warning_control_ct": "⚠️ Dikkat: Kontrol Grubu {i} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde Excel'den kopyalayıp yapıştırın.",
        "warning_patient_ct": "⚠️ Dikkat: Hasta grubu Ct verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde Excel'den kopyalayıp yapıştırın.",
        "statistical_results": "📈 İstatistik Sonuçları",
        "target_gene": "Hedef Gen",
        "reference_gene": "Referans Gen",
        "target_ct": "Hedef Gen Ct",
        "distribution_graph": "Dağılım Grafiği",
        "error_missing_control_data": "⚠️ Hata: Kontrol Grubu için Hedef Gen {i} verileri eksik!",
        "control_group_avg": "Kontrol Grubu Ortalama",
        "avg": "Ortalama",
        "control": "Kontrol",
        "sample": "Örnek",
        "patient": "Hasta",
        "delta_ct_distribution": "ΔCt Dağılımı",
        "delta_ct_value": "ΔCt Değeri",
        "parametric": "Parametrik",
        "non_parametric": "Nonparametrik",
        "t_test": "t-test",
        "mann_whitney_u_test": "Mann-Whitney U testi",
        "significant": "Anlamlı",
        "insignificant": "Anlamsız",
        "test_type": "Test Türü",
        "test_method": "Kullanılan Test",
        "test_pvalue": "Test P-değeri",
        "significance": "Anlamlılık",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "Gen Ekspresyon Değişimi (2^(-ΔΔCt))",
        "regulation_status": "Regülasyon Durumu",
        "no_change": "Değişim Yok",
        "upregulated": "Yukarı Regüle",
        "downregulated": "Aşağı Regüle",
        "report_title": "Gen Ekspresyon Analizi Raporu",
        "input_data_table": "Giriş Verileri Tablosu",
        "results": "Sonuçlar",
        "statistical_results": "İstatistiksel Sonuçlar",
        "statistical_evaluation": "İstatistiksel Değerlendirme",
        "significance": "Anlamlılık",
        "target_gene": "Hedef Gen",
        "patient_group": "Hasta Grubu",
        "expression_change": "Gen Ekspresyon Değişimi",
        "regulation_status": "Regülasyon Durumu",
        "generate_pdf": "PDF Oluştur",
        "pdf_report": "Gen Ekspresyon Raporu",
        "error_no_data": "Veri bulunamadı, PDF oluşturulamadı.",
        "statistical_explanation": (
            "İstatistiksel değerlendirme sürecinde veri dagilimi Shapiro-Wilk testi ile analiz edilmiştir. "
            "Normallik sağlanırsa, gruplar arasındaki varyans eşitliği Levene testi ile kontrol edilmiştir. "
            "Varyans eşitliği varsa bağımsız örneklem t-testi, yoksa Welch t-testi uygulanmiştir. "
            "Normal daglim saglanmazsa, parametrik olmayan Mann-Whitney U testi kullanılmiştir. "
            "Sonuçlarin anlamliligi p < 0.05 kriterine göre belirlenmiştir."
        )
    },

    "en": {
        "title": "🧬 Gene Expression Analysis Application",
        "subtitle": "Developed by B. Yalçınkaya",
        "patient_data_header": "📊 Enter Patient and Control Group Data",
        "num_target_genes": "🔹 Enter the Number of Target Genes",
        "num_patient_groups": "🔹 Enter the Number of Patient Groups",
        "sample_number": "Sample Number",
        "Grup": "Group",
        "x_axis_title": "Grup Name",
        "ct_value": "Ct Value",
        "reference_ct": "Reference Ct",
        "delta_ct_control": "ΔCt (Control)",
        "delta_ct_patient": "ΔCt (Patient)",
        "warning_empty_input": "⚠️ Warning: Write data one below the other or copy-paste without empty cells from Excel.",
        "statistical_results": "📈 Statistical Results",
        "download_csv": "📥 Download CSV",
        "generate_pdf": "📥 Prepare PDF Report",
        "pdf_report": "Gene Expression Analysis Report",
        "statistics": "Statistical Results",
        "nil_mine": "📊 Results",
        "gr_tbl": "📋 Input Data Table",
        "control_group": "🧬 Control Group",
        "patient_group": "🩸 Patient Group",
        "ctrl_trgt_ct": "🟦 Control Group Target Gene {i} Ct Values",
        "ctrl_ref_ct": "🟦 Control Group Reference Gene {i} Ct Values",
        "hst_trgt_ct": "🩸 Patient Group Target Gene {j} Ct Values",
        "hst_ref_ct": "🩸 Patient Group Reference Gene {j} Ct Values",
        "warning_control_ct": "⚠️ Warning: Control Group {i} data should be entered line by line or copied from Excel without empty cells.",
        "warning_patient_ct": "⚠️ Warning: Enter patient group Ct values line by line or copy-paste from Excel without empty cells.",
        "statistical_results": "📈 Statistical Results",
        "target_gene": "Target Gene",
        "reference_gene": "Reference Gen",
        "target_ct": "Target Gene Ct", 
        "distribution_graph": "Distribution Graph",
        "error_missing_control_data": "⚠️ Error: Missing data for Target Gene {i} in the Control Group!",
        "control_group_avg": "Control Group Average",
        "avg": "Average",
        "control": "Control",
        "sample": "Sample",
        "patient": "Patient",
        "delta_ct_distribution": "ΔCt Distribution",
        "delta_ct_value": "ΔCt Value",
        "parametric": "Parametric",
        "non_parametric": "Nonparametric",
        "t_test": "t-test",
        "mann_whitney_u_test": "Mann-Whitney U test",
        "significant": "Significant",
        "insignificant": "Insignificant",
        "test_type": "Test Type",
        "test_method": "Test Method",
        "test_pvalue": "Test P-value",
        "significance": "Significance",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "Gene Expression Change (2^(-ΔΔCt))",
        "regulation_status": "Regulation Status",
        "no_change": "No Change",
        "upregulated": "Upregulated",
        "downregulated": "Downregulated",
        "report_title": "Gene Expression Analysis Report",
        "input_data_table": "Input Data Table",
        "results": "Results",
        "statistical_results": "Statistical Results",
        "statistical_evaluation": "Statistical Evaluation",
        "significance": "Significance",
        "target_gene": "Target Gene",
        "patient_group": "Patient Group",
        "expression_change": "Gene Expression Change",
        "regulation_status": "Regulation Status",
        "generate_pdf": "Generate PDF",
        "pdf_report": "Gene Expression Report",
        "error_no_data": "No data found, PDF could not be generated.",
        "statistical_explanation": (
            "During the statistical evaluation process, data distribution was analyzed using the Shapiro-Wilk test. "
            "If normality was met, variance homogeneity between groups was checked with Levene’s test. "
            "If variance was equal, an independent sample t-test was applied; otherwise, a Welch t-test was used. "
            "If normal distribution was not achieved, the non-parametric Mann-Whitney U test was applied. "
            "Significance was determined using the p < 0.05 criterion."
        )
    },

    "de": {
        "title": "🧬 Genexpression-Analyseanwendung",
        "subtitle": "Entwickelt von B. Yalçınkaya",
        "patient_data_header": "📊 Geben Sie Patientendaten und Kontrollgruppen ein",
        "num_target_genes": "🔹 Geben Sie die Anzahl der Zielgene ein",
        "num_patient_groups": "🔹 Geben Sie die Anzahl der Patientengruppen ein",
        "sample_number": "Beispielnummer",
        "Grup": "Gruppe",
        "x_axis_title": "Gruppenname",
        "ct_value": "Ct-Wert",
        "reference_ct": "Referenz Ct",
        "delta_ct_control": "ΔCt (Kontrolle)",
        "delta_ct_patient": "ΔCt (Patientendaten)",
        "warning_empty_input": "⚠️ Warnung: Geben Sie die Daten untereinander ein oder kopieren Sie sie ohne leere Zellen aus Excel.",
        "statistical_results": "📈 Statistische Ergebnisse",
        "download_csv": "📥 CSV herunterladen",
        "generate_pdf": "📥 PDF-Bericht erstellen",
        "pdf_report": "Genexpression-Analysebericht",
        "statistics": "Statistische Ergebnisse",
        "nil_mine": "📊 Ergebnisse",
        "gr_tbl": "📋 Eingabedaten Tabelle",
        "control_group": "🧬 Kontroll gruppe",
        "patient_group": "🩸 Patientendaten Gruppe",
        "ctrl_trgt_ct": "🟦 Kontrollgruppe Zielgen {i} Ct-Werte",
        "ctrl_ref_ct": "🟦 Kontrollgruppe Referenz {i} Ct-Werte",
        "hst_trgt_ct": "🩸 Patientendaten gruppe Zielgen {j} Ct-Werte",
        "hst_ref_ct": "🩸 Patientendaten gruppe Referenz {j} Ct-Werte",
        "warning_control_ct": "⚠️ Achtung: Kontrollgruppe {i} Daten sollten untereinander eingegeben oder aus Excel ohne leere Zellen eingefügt werden.",
        "warning_patient_ct": "⚠️ Achtung: Geben Sie die Ct-Werte der Patientendaten gruppe untereinander ein oder kopieren Sie sie aus Excel ohne leere Zellen.",
        "statistical_results": "📈 Statistische Ergebnisse",
        "target_gene": "Zielgen",
        "reference_gene": "Referenzgen",
        "target_ct": "Zielgen Ct",
        "distribution_graph": "Verteilungsdiagramm",
        "error_missing_control_data": "⚠️ Fehler: Fehlende Daten für Zielgen {i} in der Kontrollgruppe!",
        "control_group_avg": "Durchschnitt der Kontrollgruppe",
        "avg": "Durchschnitt",
        "control": "Kontrolle",
        "sample": "Probe",
        "patient": "Patient",
        "delta_ct_distribution": "ΔCt-Verteilung",
        "delta_ct_value": "ΔCt-Wert",
        "parametric": "Parametrisch",
        "non_parametric": "Nicht parametrisch",
        "t_test": "t-Test",
        "mann_whitney_u_test": "Mann-Whitney U-Test",
        "significant": "Signifikant",
        "insignificant": "Nicht signifikant",
        "test_type": "Testtyp",
        "test_method": "Verwendeter Test",
        "test_pvalue": "P-Wert",
        "significance": "Bedeutung",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "Genexpression Veränderung (2^(-ΔΔCt))",
        "regulation_status": "Regulierungsstatus",
        "no_change": "Keine Veränderung",
        "upregulated": "Hochreguliert",
        "downregulated": "Herunterreguliert",
        "report_title": "Genexpressionsanalysebericht",
        "input_data_table": "Eingabedatentabelle",
        "results": "Ergebnisse",
        "statistical_results": "Statistische Ergebnisse",
        "statistical_evaluation": "Statistische Auswertung",
        "significance": "Signifikanz",
        "target_gene": "Zielgen",
        "patient_group": "Patientengruppe",
        "expression_change": "Genexpressionsänderung",
        "regulation_status": "Regulierungsstatus",
        "generate_pdf": "PDF Erstellen",
        "pdf_report": "Genexpressionsbericht",
        "error_no_data": "Keine Daten gefunden, PDF konnte nicht erstellt werden.",
        "statistical_explanation": (
            "Während des statistischen Bewertungsprozesses wurde die Datenverteilung mit dem Shapiro-Wilk-Test analysiert. "
            "Wenn die Normalität erfüllt war, wurde die Varianzhomogenität zwischen den Gruppen mit dem Levene-Test überprüft. "
            "War die Varianz gleich, wurde ein unabhängiger Stichprobent-Test angewendet; andernfalls wurde ein Welch-T-Test verwendet. "
            "Wenn keine normale Verteilung vorlag, wurde der nicht-parametrische Mann-Whitney-U-Test angewendet. "
            "Die Signifikanz wurde anhand des Kriteriums p < 0,05 bestimmt."
        )
    }
}

# Translate text using the selected language
st.title(translations[language_code]["title"])

# Kullanıcıdan giriş alın
st.header(translations[language_code]["patient_data_header"])
num_target_genes = st.number_input(translations[language_code]["num_target_genes"], min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(translations[language_code]["num_patient_groups"], min_value=1, step=1, key="patient_count")

# Veri işleme fonksiyonu
def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# Veri listeleri
input_values_table = []
data = []
stats_data = []

# Grafik için son işlenen Hedef Genın kontrol verilerini saklamak amacıyla değişkenler
last_control_delta_ct = None
last_gene_index = None

control_group = translations[language_code]["control_group"]
target_gene = translations[language_code]["target_gene"]
reference_gene = translations[language_code]["reference_gene"]
ct_value = translations[language_code]["ct_value"]
patient_group = translations[language_code]["patient_group"]

    # Kontrol Grubu Verileri
for i in range(num_target_genes):
    st.subheader(f"{translations[language_code]['control_group']} {i+1} - {translations[language_code]['target_gene']} {i+1}")
    control_target_ct = st.text_area(f"{translations[language_code]['control_group']} {i+1} - {translations[language_code]['target_gene']} {i+1} - {translations[language_code]['ct_value']}", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"{translations[language_code]['control_group']} {i+1} - {translations[language_code]['reference_gene']} {i+1} - {translations[language_code]['ct_value']}", key=f"control_reference_ct_{i}")
   
    control_target_ct_values = np.array(parse_input_data(control_target_ct))
    control_reference_ct_values = np.array(parse_input_data(control_reference_ct))

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(translations[language_code]["warning_control_ct"].format(i=i+1))
        continue
    
    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_target_ct_values = control_target_ct_values[:min_control_len]
    control_reference_ct_values = control_reference_ct_values[:min_control_len]
    control_delta_ct = control_target_ct_values - control_reference_ct_values

    average_control_delta_ct = np.mean(control_delta_ct) if len(control_delta_ct) > 0 else None
    sample_counter = 1  # Kontrol grubu örnek sayacı
    
    for idx in range(min_control_len):
        input_values_table.append({
            translations[language_code]["sample_number"]: sample_counter,
            translations[language_code]["target_gene"]: f"{target_gene} {i+1}",
            "Grup": translations[language_code]["control_group"],
            translations[language_code]["target_ct"]: control_target_ct_values[idx],
            translations[language_code]["reference_ct"]: control_reference_ct_values[idx],  
            translations[language_code]["delta_ct_control"]: control_delta_ct[idx]
        })
        sample_counter += 1
    
    
    for j in range(num_patient_groups):
        st.subheader(f"{translations[language_code]['patient_group']} {j+1} - {translations[language_code]['target_gene']} {i+1}")        
        
        sample_target_ct = st.text_area(f"{translations[language_code]['patient_group']} {j+1} - {translations[language_code]['target_gene']} {i+1} - {translations[language_code]['ct_value']}", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"{translations[language_code]['patient_group']} {j+1} - {translations[language_code]['reference_gene']} {i+1} - {translations[language_code]['ct_value']}", key=f"sample_reference_ct_{i}_{j}")
        
        sample_target_ct_values = np.array(parse_input_data(sample_target_ct))
        sample_reference_ct_values = np.array(parse_input_data(sample_reference_ct))
         
        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(translations[language_code]["warning_patient_ct"].format(j=j+1))
            continue
        
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
        average_sample_delta_ct = np.mean(sample_delta_ct) if len(sample_delta_ct) > 0 else None
        
        sample_counter = 1  
        for idx in range(min_sample_len):
            input_values_table.append({
                translations[language_code]["sample_number"]: sample_counter,
                translations[language_code]["target_gene"]: f"{translations[language_code]['target_gene']} {i+1}",
                "Grup": f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["target_ct"]: sample_target_ct_values[idx],
                translations[language_code]["reference_ct"]: sample_reference_ct_values[idx],
                translations[language_code]["delta_ct_patient"]: sample_delta_ct[idx]
            })
            sample_counter += 1
        
        # ΔΔCt ve Gen Ekspresyon Değişimi Hesaplama
        if average_control_delta_ct is not None and average_sample_delta_ct is not None:
            delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
            expression_change = 2 ** (-delta_delta_ct)
            
            if expression_change == 1:
                regulation_status = translations[language_code]["no_change"]
            elif expression_change > 1:
                regulation_status = translations[language_code]["upregulated"]
            else:
                regulation_status = translations[language_code]["downregulated"]
       
        # İstatistiksel Testler
            shapiro_control = stats.shapiro(control_delta_ct)
            shapiro_sample = stats.shapiro(sample_delta_ct)
            levene_test = stats.levene(control_delta_ct, sample_delta_ct)
            
            control_normal = shapiro_control.pvalue > 0.05
            sample_normal = shapiro_sample.pvalue > 0.05
            equal_variance = levene_test.pvalue > 0.05
            
            if control_normal and sample_normal:
               if equal_variance:
                   test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue
                   test_method = translations[language_code]["t_test"]
               else:
                   test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct, equal_var=False).pvalue
                   test_method = translations[language_code]["welch_t_test"]
               test_type = translations[language_code]["parametric"]
            else:
                test_pvalue = stats.mannwhitneyu(control_delta_ct, sample_delta_ct).pvalue
                test_method = translations[language_code]["mann_whitney_u_test"]
                test_type = translations[language_code]["non_parametric"]
               
            significance = translations[language_code]["significant"] if test_pvalue < 0.05 else translations[language_code]["insignificant"]
            
            stats_data.append({
                translations[language_code]["target_gene"]: f"{translations[language_code]['target_gene']} {i+1}",
                translations[language_code]["patient_group"]: f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["test_type"]: test_type,
                translations[language_code]["test_method"]: test_method,
                translations[language_code]["test_pvalue"]: test_pvalue,
                translations[language_code]["significance"]: significance
            })
            
            data.append({
                translations[language_code]["target_gene"]: f"{translations[language_code]['target_gene']} {i+1}",
                translations[language_code]["patient_group"]: f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["delta_delta_ct"]: delta_delta_ct,
                translations[language_code]["gene_expression_change"]: expression_change,
                translations[language_code]["regulation_status"]: regulation_status,
                translations[language_code]["delta_ct_control"]: average_control_delta_ct,
                translations[language_code]["delta_ct_patient"]: average_sample_delta_ct
            })

# Giriş Verileri Tablosunu Göster
if input_values_table: 
    st.subheader(f"📋 {translations[language_code]['gr_tbl']}")
    input_df = pd.DataFrame(input_values_table) 
    st.write(input_df) 

    csv = input_df.to_csv(index=False).encode("utf-8")  
    st.download_button(
        label=translations[language_code]['download_csv'],  # Dil koduna göre etiket
        data=csv, file_name="giris_verileri.csv", mime="text/csv") 



# Sonuçlar Tablosunu Göster
if data:
    st.subheader(f"📊 {translations[language_code]['nil_mine']}")

    df = pd.DataFrame(data)
    st.write(df)

# İstatistik Sonuçları
if stats_data:
    st.subheader(f"📈 {translations[language_code]['statistical_results']}")
    
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
    
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=translations[language_code]['download_csv'],  # Dil koduna göre etiket
        data=csv_stats,
        file_name="istatistik_sonuclari.csv",
        mime="text/csv")


# Grafik oluşturma (her hedef gen için bir grafik oluşturulacak)
for i in range(num_target_genes):
    st.subheader(f"{translations[language_code]['target_gene']} {i+1} - {translations[language_code]['distribution_graph']}")

    # Kontrol Grubu Verileri
    control_target_ct_values = [
        d[translations[language_code]["target_ct"]] 
        for d in input_values_table
        if d["Grup"] == translations[language_code]["control_group"] and
           d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}"
    ]

    control_reference_ct_values = [
        d[translations[language_code]["reference_ct"]] 
        for d in input_values_table
        if d["Grup"] == translations[language_code]["control_group"] and
           d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}"
    ]

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f"⚠️ {translations[language_code]['error_missing_control_data'].format(i=i+1)}")
        continue

    control_delta_ct = np.array(control_target_ct_values) - np.array(control_reference_ct_values)
    average_control_delta_ct = np.mean(control_delta_ct)

    # Grafik başlatma
    fig = go.Figure()

    # Kontrol Grubu Ortalama Çizgisi
    fig.add_trace(go.Scatter(
        x=[0.8, 1.2],  
        y=[average_control_delta_ct, average_control_delta_ct],  
        mode='lines',
        line=dict(color='black', width=4),
        name=translations[language_code]["control_group_avg"]
    ))

    # Hasta Gruplarının Ortalama Çizgileri
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d[translations[language_code]["delta_ct_patient"]] 
            for d in input_values_table 
            if d["Grup"] == f"{translations[language_code]['patient_group']} {j+1}" and 
               d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}"
        ]

        if not sample_delta_ct_values:
            continue  

        average_sample_delta_ct = np.mean(sample_delta_ct_values)
        fig.add_trace(go.Scatter(
            x=[(j + 1.8), (j + 2.2)],  
            y=[average_sample_delta_ct, average_sample_delta_ct],  
            mode='lines',
            line=dict(color='black', width=4),
            name=f"{translations[language_code]['patient_group']} {j+1} {translations[language_code]['avg']}"
        ))

    # Veri Noktaları (Kontrol Grubu)
    fig.add_trace(go.Scatter(
        x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
        y=control_delta_ct,
        mode='markers',  
        name=translations[language_code]["control_group"],
        marker=dict(color='blue'),
        text=[f"{translations[language_code]['control']} {value:.2f}, {translations[language_code]['sample']} {idx+1}" for idx, value in enumerate(control_delta_ct)],
        hoverinfo='text'
    ))

    # Veri Noktaları (Hasta Grupları)
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d[translations[language_code]["delta_ct_patient"]] 
            for d in input_values_table 
            if d["Grup"] == f"{translations[language_code]['patient_group']} {j+1}" and 
               d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}"
        ]

        if not sample_delta_ct_values:
            continue  

        fig.add_trace(go.Scatter(
            x=np.ones(len(sample_delta_ct_values)) * (j + 2) + np.random.uniform(-0.05, 0.05, len(sample_delta_ct_values)),
            y=sample_delta_ct_values,
            mode='markers',  
            name=f"{translations[language_code]['patient_group']} {j+1}",
            marker=dict(color='red'),
            text=[f"{translations[language_code]['patient']} {value:.2f}, {translations[language_code]['sample']} {idx+1}" for idx, value in enumerate(sample_delta_ct_values)],
            hoverinfo='text'
        ))

    # Grafik ayarları
    fig.update_layout(
        title=f"{translations[language_code]['target_gene']} {i+1} - {translations[language_code]['delta_ct_distribution']}",
        xaxis=dict(
            tickvals=[1] + [j + 2 for j in range(num_patient_groups)],
            ticktext=[translations[language_code]['control_group']] + [f"{translations[language_code]['patient_group']} {j+1}" for j in range(num_patient_groups)],
            title=translations[language_code]['x_axis_title']
        ),
        yaxis=dict(title=translations[language_code]['delta_ct_value']),
        showlegend=True
    )
    st.plotly_chart(fig)
# PDF rapor oluşturma kısmı
def create_pdf(results, stats, input_df, language_code):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Başlık
    elements.append(Paragraph(translations[language_code]["report_title"], styles['Title']))
    elements.append(Spacer(1, 12))

    # Giriş Verileri Tablosu Başlığı
    elements.append(Paragraph(translations[language_code]["input_data_table"], styles['Heading2']))
    
    # Tablo Verisi
    table_data = [input_df.columns.tolist()] + input_df.values.tolist()
    col_width = (letter[0] - 80) / len(input_df.columns)
    table = Table(table_data, colWidths=[col_width] * len(input_df.columns))
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    # Sonuçlar Başlığı
    elements.append(Paragraph(translations[language_code]["results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for result in results:
        text = (f"{result[translations[language_code]['target_gene']]} - {result[translations[language_code]['patient_group']]} | "
                f"ΔΔCt: {result['ΔΔCt']:.2f} | 2^(-ΔΔCt): {result[translations[language_code]['gene_expression_change']]:.2f} | "
                f"{result[translations[language_code]['regulation_status']]}")
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # İstatistiksel Sonuçlar
    elements.append(Paragraph(translations[language_code]["statistical_results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for stat in stats:
        text = (f"{stat[translations[language_code]['target_gene']]} - {stat[translations[language_code]['patient_group']]} | "
                f"{translations[language_code]['test_method']}: {stat[translations[language_code]['test_method']]} | "
                f"p: {stat[translations[language_code]['test_pvalue']]:.4f} | {stat[translations[language_code]['significance']]}")
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # İstatistiksel Değerlendirme
    elements.append(Paragraph(translations[language_code]["statistical_evaluation"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    explanation = translations[language_code]["statistical_explanation"]
    
    for line in explanation.split(". "):
        elements.append(Paragraph(line.strip() + '.', styles['Normal']))
        elements.append(Spacer(1, 6))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button(f"📥 {translations[language_code]['generate_pdf']}"):
    if input_values_table:
        pdf_buffer = create_pdf(data, stats_data, pd.DataFrame(input_values_table), language_code)
        st.download_button(label=f"{translations[language_code]['pdf_report']}", data=pdf_buffer, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
    else:
        st.error(translations[language_code]["error_no_data"])


st.markdown(f"### {translations[language_code]['subtitle']}")
