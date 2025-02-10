import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
        
        # Verilerin boyutlarının eşit olduğundan emin olalım
        min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        
        if min_control_len == 0 or min_sample_len == 0:
            st.error("Hata: Tüm gruplar için en az bir veri girilmelidir!")
            continue

        # Kontrol ve hasta grubu verilerini eşitleme
        control_target_ct_values = control_target_ct_values[:min_control_len]
        control_reference_ct_values = control_reference_ct_values[:min_control_len]
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        
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
            "Kontrol Grubu Örnek Sayısı": min_control_len,
            "Hasta Grubu Örnek Sayısı": min_sample_len
        })
        
        for j in range(max(min_control_len, min_sample_len)):
            row = {"Hedef Gen": f"Hedef Gen {i+1}", "Örnek No": j+1}
            if j < min_control_len:
                row["Kontrol Hedef Ct"] = control_target_ct_values[j]
                row["Kontrol Referans Ct"] = control_reference_ct_values[j]
            if j < min_sample_len:
                row["Hasta Hedef Ct"] = sample_target_ct_values[j]
                row["Hasta Referans Ct"] = sample_reference_ct_values[j]
            input_values_table.append(row)

# Sıralamayı belirledik
if input_values_table:
    st.subheader("Giriş Verileri Tablosu")
    input_df = pd.DataFrame(input_values_table)
    
    # İlk sütunu (index sütunu) silme
    input_df = input_df.drop(columns=input_df.columns[0])  # ilk sütunu siliyoruz
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
    
    # Plotly grafik objesi oluşturuluyor
    fig = go.Figure()

    # Kontrol grubu verilerini ekleme
    fig.add_trace(go.Scatter(
        x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
        y=control_delta_ct,
        mode='markers',
        name='Kontrol Grubu',
        marker=dict(color='blue'),
        text=[f'Kontrol {value:.2f}, Örnek {i+1}' for i, value in enumerate(control_delta_ct)],  # Tooltip metni
        hoverinfo='text'  # Tooltip gösterimi
    ))

    # Hasta grubu verilerini ekleme
    fig.add_trace(go.Scatter(
        x=np.ones(len(sample_delta_ct)) * 2 + np.random.uniform(-0.05, 0.05, len(sample_delta_ct)),
        y=sample_delta_ct,
        mode='markers',
        name='Hasta Grubu',
        marker=dict(color='red'),
        text=[f'Hasta {value:.2f}, Örnek {i+1}' for i, value in enumerate(sample_delta_ct)],  # Tooltip metni
        hoverinfo='text'  # Tooltip gösterimi
    ))

    # Kontrol grubunun ortalama değerini çizme (kesik çizgi - siyah)
    fig.add_trace(go.Scatter(
        x=[1, 1],  # X ekseninde 1 (Kontrol grubu) için
        y=[average_control_delta_ct, average_control_delta_ct],  # Y ekseninde ortalama değer
        mode='lines',
        line=dict(color='black', dash='dot', width=4),  # Kesik siyah çizgi
        name='Kontrol Grubu Ortalama'
    ))

    # Hasta grubunun ortalama değerini çizme (kesik çizgi - siyah)
    fig.add_trace(go.Scatter(
        x=[2, 2],  # X ekseninde 2 (Hasta grubu) için
        y=[average_sample_delta_ct, average_sample_delta_ct],
