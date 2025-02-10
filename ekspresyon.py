import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# Başlık
st.title("Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

# Kullanıcıdan giriş al
st.header("Hasta ve Kontrol Grubu Verisi Girin")

# Hedef Gen Sayısı
num_target_genes = st.number_input("Hedef Gen Sayısını Girin", min_value=1, step=1)

data = []
stats_data = []
input_values_table = []

def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

for i in range(num_target_genes):
    st.subheader(f"Hedef Gen {i+1}")
    
    control_target_ct = st.text_area(f"Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    sample_target_ct = st.text_area(f"Hasta Grubu Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}")
    sample_reference_ct = st.text_area(f"Hasta Grubu Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}")
    
    if control_target_ct and control_reference_ct and sample_target_ct and sample_reference_ct:
        control_target_ct_values = parse_input_data(control_target_ct)
        control_reference_ct_values = parse_input_data(control_reference_ct)
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)
        
        # Kontrol ve Hasta grubu verilerinin boyutlarını eşitleme
        control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
        sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        
        if control_len == 0 or sample_len == 0:
            st.error("Hata: Tüm gruplar için en az bir veri girilmelidir!")
            continue
        
        # Verileri aynı boyutta olacak şekilde kısaltma
        control_target_ct_values = control_target_ct_values[:control_len]
        control_reference_ct_values = control_reference_ct_values[:control_len]
        sample_target_ct_values = sample_target_ct_values[:sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:sample_len]
        
        control_delta_ct = control_target_ct_values - control_reference_ct_values
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
        average_control_delta_ct = np.mean(control_delta_ct)
        average_sample_delta_ct = np.mean(sample_delta_ct)
        
        delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
        expression_change = 2 ** (-delta_delta_ct)
        
        regulation_status = "Değişim Yok" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")
        
        shapiro_control = stats.shapiro(control_delta_ct)
        shapiro_sample = stats.shapiro(sample_delta_ct)
        
        control_normal = shapiro_control.pvalue > 0.05
        sample_normal = shapiro_sample.pvalue > 0.05
        
        levene_test = stats.levene(control_delta_ct, sample_delta_ct)
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
            "Normalite Testi Kontrol Grubu (Shapiro P-value)": shapiro_control.pvalue,
            "Normalite Testi Hasta Grubu (Shapiro P-value)": shapiro_sample.pvalue,
            "Varyans Testi (Levene P-value)": levene_test.pvalue,
            "Test Türü": test_type,
            "Kullanılan Test": test_method,  
            "Test P-değeri": test_pvalue,
            "Anlamlılık": significance
        })
        
        data.append({
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Kontrol ΔCt (Ortalama)": average_control_delta_ct,
            "Hasta ΔCt (Ortalama)": average_sample_delta_ct,
            "ΔΔCt": delta_delta_ct,
            "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
            "Regülasyon Durumu": regulation_status,
            "Kontrol Grubu Örnek Sayısı": control_len,
            "Hasta Grubu Örnek Sayısı": sample_len
        })
        
        for j in range(max(control_len, sample_len)):
            row = {"Hedef Gen": f"Hedef Gen {i+1}", "Örnek No": j+1}
            if j < control_len:
                row["Kontrol Hedef Ct"] = control_target_ct_values[j]
                row["Kontrol Referans Ct"] = control_reference_ct_values[j]
            if j < sample_len:
                row["Hasta Hedef Ct"] = sample_target_ct_values[j]
                row["Hasta Referans Ct"] = sample_reference_ct_values[j]
            input_values_table.append(row)

# Sıralamayı belirledik
if input_values_table:
    st.subheader("Giriş Verileri Tablosu")
    input_df = pd.DataFrame(input_values_table)
    st.write(input_df)

if data:
    st.subheader("Sonuçlar Tablosu")
    df = pd.DataFrame(data)
    st.write(df)

if stats_data:
    st.subheader("İstatistik Sonuçları")
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)

    # Grafik oluşturma
    st.subheader(f"Hedef Gen {i+1} - Hasta ve Kontrol Grubu Dağılım Grafiği")
    plt.figure(figsize=(8, 6))
    
    jitter = 0.05  # Değerler arasındaki küçük ofset
    # Kontrol grubu verilerini yatayda dağıtma
    control_x_positions = np.ones(len(control_delta_ct)) + np.random.uniform(-jitter, jitter, len(control_delta_ct))
    # Hasta grubu verilerini yatayda dağıtma
    sample_x_positions = np.ones(len(sample_delta_ct)) * 2 + np.random.uniform(-jitter, jitter, len(sample_delta_ct))
    
    # Verileri çizme
    plt.scatter(control_x_positions, control_delta_ct, color='blue', alpha=0.6, label="Kontrol Grubu")
    plt.scatter(sample_x_positions, sample_delta_ct, color='red', alpha=0.6, label="Hasta Grubu")
    
    # Ortalamaları X eksenine yerleştirerek yatay çizgiler ekliyoruz, çizgilerin uzunluğunu daha kısa yapıyoruz
    control_median = np.median(control_delta_ct)
    sample_median = np.median(sample_delta_ct)
    
    # Kontrol grubu ortalama çizgisi
    plt.hlines(y=control_median, xmin=0.9, xmax=1.1, color='blue', linestyle='--', linewidth=2, label=f"Kontrol Grubu Medyan: {control_median:.2f}")
    # Hasta grubu ortalama çizgisi
    plt.hlines(y=sample_median, xmin=1.9, xmax=2.1, color='red', linestyle='--', linewidth=2, label=f"Hasta Grubu Medyan: {sample_median:.2f}")
    
    # Grafik ayarları
    plt.xticks([1, 2], 
               [f"Kontrol Grubu Medyan: {control_median:.2f}", f"Hasta Grubu Medyan: {sample_median:.2f}"])
    plt.xlabel('Grup')
    plt.ylabel('ΔCt Değeri')
    plt.title(f"Hedef Gen {i+1} - ΔCt Dağılımı")
    
    # Açıklama kutusunu dışarıya yerleştiriyoruz
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Açıklamalar")
    
    st.pyplot(plt)
