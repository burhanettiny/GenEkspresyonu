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

# Verileri işleyen fonksiyon
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
        
        # Eksik veri kontrolü
        control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
        sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        
        if control_len == 0 or sample_len == 0:
            st.error("Hata: Tüm gruplar için en az bir veri girilmelidir!")
            continue
        
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
        
        if expression_change == 1:
            regulation_status = "Değişim Yok"
        elif expression_change > 1:
            regulation_status = "Upregulated"
        else:
            regulation_status = "Downregulated"
        
        # Normallik testleri
        shapiro_control = stats.shapiro(control_delta_ct)
        shapiro_sample = stats.shapiro(sample_delta_ct)
        
        control_normal = shapiro_control.pvalue > 0.05
        sample_normal = shapiro_sample.pvalue > 0.05
        
        # Varyans testi
        levene_test = stats.levene(control_delta_ct, sample_delta_ct)
        equal_variance = levene_test.pvalue > 0.05
        
        # İstatistiksel test seçimi
        if control_normal and sample_normal and equal_variance:
            test_name = "T-Test"
            test_stat, test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct)
        else:
            test_name = "Mann-Whitney U"
            test_stat, test_pvalue = stats.mannwhitneyu(control_delta_ct, sample_delta_ct)
        
        significance = "Anlamlı" if test_pvalue < 0.05 else "Anlamsız"
        
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
            else:
                row["Kontrol Hedef Ct"] = None
                row["Kontrol Referans Ct"] = None
            if j < sample_len:
                row["Hasta Hedef Ct"] = sample_target_ct_values[j]
                row["Hasta Referans Ct"] = sample_reference_ct_values[j]
            else:
                row["Hasta Hedef Ct"] = None
                row["Hasta Referans Ct"] = None
            input_values_table.append(row)

# Giriş verileri tablosunu göster
st.subheader("Giriş Verileri Tablosu")
input_df = pd.DataFrame(input_values_table)
st.write(input_df)

# Sonuçları göster
st.subheader("Sonuçlar")
df = pd.DataFrame(data)
st.write(df)

st.subheader("İstatistik Sonuçları")
stats_df = pd.DataFrame(stats_data)
st.write(stats_df)
