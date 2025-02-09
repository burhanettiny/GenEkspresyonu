import streamlit as st 
import pandas as pd
import numpy as np
import scipy.stats as stats

st.title("Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

st.header("Hasta ve Kontrol Grubu Verisi Girin")
num_target_genes = st.number_input("Hedef Gen Sayısını Girin", min_value=1, step=1)

data = []
input_values_table = []

def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x], dtype=np.float64)

for i in range(num_target_genes):
    st.subheader(f"Hedef Gen {i+1}")
    
    control_target_ct = st.text_area(f"Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    sample_target_ct = st.text_area(f"Hasta Grubu Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}")
    sample_reference_ct = st.text_area(f"Hasta Grubu Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}")
    
    if control_target_ct and control_reference_ct and sample_target_ct and sample_reference_ct:
        try:
            control_target_ct_values = parse_input_data(control_target_ct)
            control_reference_ct_values = parse_input_data(control_reference_ct)
            sample_target_ct_values = parse_input_data(sample_target_ct)
            sample_reference_ct_values = parse_input_data(sample_reference_ct)

            control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
            sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))

            if control_len == 0 or sample_len == 0:
                st.error("Hata: Tüm gruplar için en az bir veri girilmelidir!")
                continue

            control_delta_ct = control_target_ct_values[:control_len] - control_reference_ct_values[:control_len]
            sample_delta_ct = sample_target_ct_values[:sample_len] - sample_reference_ct_values[:sample_len]

            average_control_delta_ct = np.nanmean(control_delta_ct)
            average_sample_delta_ct = np.nanmean(sample_delta_ct)
            
            delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
            expression_change = 2 ** (-delta_delta_ct)
            regulation_status = "Değişim Yok" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")

            shapiro_control = stats.shapiro(control_delta_ct[~np.isnan(control_delta_ct)])
            shapiro_sample = stats.shapiro(sample_delta_ct[~np.isnan(sample_delta_ct)])

            control_normal = shapiro_control.pvalue > 0.05
            sample_normal = shapiro_sample.pvalue > 0.05

            levene_test = stats.levene(control_delta_ct[~np.isnan(control_delta_ct)], sample_delta_ct[~np.isnan(sample_delta_ct)])
            equal_variance = levene_test.pvalue > 0.05

            if control_normal and sample_normal and equal_variance:
                test_name = "T-Test"
                test_stat, test_pvalue = stats.ttest_ind(control_delta_ct[~np.isnan(control_delta_ct)], 
                                                         sample_delta_ct[~np.isnan(sample_delta_ct)], nan_policy='omit')
            else:
                test_name = "Mann-Whitney U"
                test_stat, test_pvalue = stats.mannwhitneyu(control_delta_ct[~np.isnan(control_delta_ct)], 
                                                            sample_delta_ct[~np.isnan(sample_delta_ct)])

            significance = "Anlamlı" if test_pvalue < 0.05 else "Anlamsız"

            data.append({
                "Hedef Gen": f"Hedef Gen {i+1}",
                "Kontrol ΔCt (Ortalama)": average_control_delta_ct,
                "Hasta ΔCt (Ortalama)": average_sample_delta_ct,
                "ΔΔCt": delta_delta_ct,
                "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
                "Regülasyon Durumu": regulation_status,
                "Test Türü": test_name,
                "p-Değeri": test_pvalue,
                "Sonuç": significance
            })

            for j in range(max(control_len, sample_len)):
                row = {"Hedef Gen": f"Hedef Gen {i+1}", "Örnek No": j+1}
                row["Kontrol Hedef Ct"] = control_target_ct_values[j] if j < control_len else None
                row["Kontrol Referans Ct"] = control_reference_ct_values[j] if j < control_len else None
                row["Hasta Hedef Ct"] = sample_target_ct_values[j] if j < sample_len else None
                row["Hasta Referans Ct"] = sample_reference_ct_values[j] if j < sample_len else None
                input_values_table.append(row)

        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# **Debug Çıktıları:**
st.subheader("Debug Çıktıları")
st.write("Veri Listesi:", data)
st.write("Giriş Tablosu Verileri:", input_values_table)

# **Giriş verileri tablosunu göster**
st.subheader("Giriş Verileri Tablosu")
input_df = pd.DataFrame(input_values_table)
st.write("Giriş Verileri DataFrame:", input_df.head())  # İlk satırları göster
st.write("Giriş Verileri DataFrame Türleri:", input_df.dtypes)
st.write(input_df)

# **Sonuçları göster**
st.subheader("Sonuçlar")
df = pd.DataFrame(data)
st.write("Sonuçlar DataFrame:", df.head())  # İlk satırları göster
st.write("Sonuçlar DataFrame Türleri:", df.dtypes)
st.write(df)
