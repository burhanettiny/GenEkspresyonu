import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy import stats

# Language selection
lang = st.selectbox("Select Language / Dil Seçin", ["English", "Türkçe"])

# Translations
translations = {
    "English": {
        "header_target_gen": "Target Gene {i+1}",
        "header_control_group": "Control Group Target Gene {i+1} Ct Values",
        "header_patient_group": "Patient Group {j+1} - Target Gene {i+1}",
        "error_message": "⚠️ Attention: Paste values correctly without empty spaces in the cells.",
        "results": "Results",
        "expression_change": "Gene Expression Change (2^(-ΔΔCt))",
        "no_data_warning": "⚠️ Warning: Paste data correctly or write values without blank spaces.",
        "stats_results": "Statistical Results",
        "download_csv": "📥 Download as CSV",
        "graph_error": "⚠️ Error: Missing Control Group data for Target Gene {i+1}!",
        "no_graph_data": "Graph generation requires at least one valid data set.",
    },
    "Türkçe": {
        "header_target_gen": "Hedef Gen {i+1}",
        "header_control_group": "Kontrol Grubu Hedef Gen {i+1} Ct Değerleri",
        "header_patient_group": "Hasta Grubu {j+1} - Hedef Gen {i+1}",
        "error_message": "⚠️ Dikkat: Verileri doğru bir şekilde yapıştırın veya boşluk içermeyen hücreleri kullanın.",
        "results": "Sonuçlar",
        "expression_change": "Gen Ekspresyon Değişimi (2^(-ΔΔCt))",
        "no_data_warning": "⚠️ Dikkat: Verileri doğru şekilde yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.",
        "stats_results": "İstatistiksel Sonuçlar",
        "download_csv": "📥 CSV Olarak İndir",
        "graph_error": "⚠️ Hata: Kontrol Grubu için Hedef Gen {i+1} verileri eksik!",
        "no_graph_data": "Grafik oluşturulabilmesi için en az bir geçerli veri seti gereklidir.",
    }
}

# Function to translate based on selected language
def translate(key):
    return translations[language][key]

# Kullanıcıdan hedef gen sayısı ve hasta grubu sayısını alıyoruz
num_target_genes = st.number_input("Hedef Gen Sayısı", min_value=1, value=3, step=1)
num_patient_groups = st.number_input("Hasta Grubu Sayısı", min_value=1, value=2, step=1)

# Veri listeleri
input_values_table = []
data = []
stats_data = []

# Giriş verisini işleyen fonksiyon
def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# Grafik için son işlenen Hedef Genin kontrol verilerini saklamak amacıyla değişkenler
last_control_delta_ct = None
last_gene_index = None

for i in range(num_target_genes):
    st.subheader(translate("header_target_gen").format(i+1))
    
    # Kontrol Grubu Verileri
    control_target_ct = st.text_area(translate("header_control_group").format(i+1), key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(translate("header_control_group").format(i+1), key=f"control_reference_ct_{i}")
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(translate("error_message"))
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
        st.warning(translate("no_data_warning"))
        continue
    
    sample_counter = 1  # Kontrol grubu örnek sayacı
    for idx in range(min_control_len):
        input_values_table.append({
            "Sample Number": sample_counter,
            "Target Gene": f"Target Gene {i+1}",
            "Group": "Control",
            "Target Gene Ct Value": control_target_ct_values[idx],
            "Reference Ct": control_reference_ct_values[idx],  
            "ΔCt (Control)": control_delta_ct[idx]
        })
        sample_counter += 1
    
    # Hasta Grubu Verileri
    for j in range(num_patient_groups):
        st.subheader(translate("header_patient_group").format(j+1, i+1))
        
        sample_target_ct = st.text_area(translate("header_patient_group").format(j+1, i+1), key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(translate("header_patient_group").format(j+1, i+1), key=f"sample_reference_ct_{i}_{j}")
        
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)
        
        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(translate("error_message"))
            continue
        
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
        if len(sample_delta_ct) > 0:
            average_sample_delta_ct = np.mean(sample_delta_ct)
        else:
            st.warning(translate("no_data_warning"))
            continue
        
        sample_counter = 1  # Her Hasta Grubu için örnek sayacı sıfırlanıyor
        for idx in range(min_sample_len):
            input_values_table.append({
                "Sample Number": sample_counter,
                "Target Gene": f"Target Gene {i+1}",
                "Group": f"Patient Group {j+1}",
                "Target Gene Ct Value": sample_target_ct_values[idx],
                "Reference Ct": sample_reference_ct_values[idx],
                "ΔCt (Patient)": sample_delta_ct[idx]
            })
            sample_counter += 1
        
        # ΔΔCt ve Gen Ekspresyon Değişimi Hesaplama
        delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)
        
        regulation_status = "No Change" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")
        
        # İstatistiksel Testler
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
            "Target Gene": f"Target Gene {i+1}",
            "Patient Group": f"Patient Group {j+1}",
            "Test Type": test_type,
            "Test Used": test_method,  
            "Test P-value": test_pvalue,
            "Significance": significance
        })
        
        data.append({
            "Target Gene": f"Target Gene {i+1}",
            "Patient Group": f"Patient Group {j+1}",
            "ΔΔCt": delta_delta_ct,
            "Gene Expression Change (2^(-ΔΔCt))": expression_change,
            "Regulation Status": regulation_status,
            "ΔCt (Control)": average_control_delta_ct,
            "ΔCt (Patient)": average_sample_delta_ct
        })

# Giriş Verileri Tablosunu Göster
if input_values_table: 
    st.subheader(translate("results")) 
    input_df = pd.DataFrame(input_values_table) 
    st.write(input_df) 

    csv = input_df.to_csv(index=False).encode("utf-8") 
    st.download_button(label=translate("download_csv"), data=csv, file_name="input_data.csv", mime="text/csv") 

# Sonuçlar Tablosunu Göster
if data:
    st.subheader(translate("results"))
    df = pd.DataFrame(data)
    st.write(df)

# İstatistik Sonuçları
if stats_data:
    st.subheader(translate("stats_results"))
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
    
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(label=translate("download_csv"), data=csv_stats, file_name="statistical_results.csv", mime="text/csv")

# Grafik oluşturma (her hedef gen için bir grafik oluşturulacak)
for i in range(num_target_genes):
    st.subheader(translate("header_target_gen").format(i+1))
    
    # Kontrol Grubu Verileri
    control_target_ct_values = [
        d["Target Gene Ct Value"] for d in input_values_table
        if d["Group"] == "Control" and d["Target Gene"] == f"Target Gene {i+1}"
    ]
    
    control_reference_ct_values = [
        d["Reference Ct"] for d in input_values_table
        if d["Group"] == "Control" and d["Target Gene"] == f"Target Gene {i+1}"
    ]
    
    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(translate("graph_error").format(i+1))
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
        name='Control Group Mean'
    ))

    # Hasta Gruplarının Ortalama Çizgileri
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d["ΔCt (Patient)"] for d in input_values_table 
            if d["Group"] == f"Patient Group {j+1}" and d["Target Gene"] == f"Target Gene {i+1}"
        ]
    
        if not sample_delta_ct_values:
            continue  # Eğer hasta grubuna ait veri yoksa, bu hasta grubunu atla
        
        average_sample_delta_ct = np.mean(sample_delta_ct_values)
        fig.add_trace(go.Scatter(
            x=[(j + 1.8), (j + 2.2)],  
            y=[average_sample_delta_ct, average_sample_delta_ct],  
            mode='lines',
            line=dict(color='black', width=4),
            name=f'Patient Group {j+1} Mean'
        ))

    # Veri Noktaları (Kontrol Grubu)
    fig.add_trace(go.Scatter(
        x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
        y=control_delta_ct,
        mode='markers',  
        name='Control Group',
        marker=dict(color='blue'),
        text=[f'Control {value:.2f}, Sample {idx+1}' for idx, value in enumerate(control_delta_ct)],
        hoverinfo='text'
    ))

    # Veri Noktaları (Hasta Grupları)
    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            d["ΔCt (Patient)"] for d in input_values_table 
            if d["Group"] == f"Patient Group {j+1}" and d["Target Gene"] == f"Target Gene {i+1}"
        ]
    
        if not sample_delta_ct_values:
            continue  # Eğer hasta grubuna ait veri yoksa, bu hasta grubunu atla
        
        fig.add_trace(go.Scatter(
            x=np.ones(len(sample_delta_ct_values)) * (j + 2) + np.random.uniform(-0.05, 0.05, len(sample_delta_ct_values)),
            y=sample_delta_ct_values,
            mode='markers',  
            name=f'Patient Group {j+1}',
            marker=dict(color='red'),
            text=[f'Patient {value:.2f}, Sample {idx+1}' for idx, value in enumerate(sample_delta_ct_values)],
            hoverinfo='text'
        ))

    # Grafik ayarları
    fig.update_layout(
        title=f"Target Gene {i+1} - ΔCt Distribution",
        xaxis=dict(
            tickvals=[1] + [i + 2 for i in range(num_patient_groups)],
            ticktext=['Control Group'] + [f'Patient Group {i+1}' for i in range(num_patient_groups)],
            title='Group'
        ),
        yaxis=dict(title='ΔCt Value'),
        showlegend=True
    )

    st.plotly_chart(fig)

else:
    st.info(translate("no_graph_data"))
