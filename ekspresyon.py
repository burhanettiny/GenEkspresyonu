import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

# Başlık
st.title("Delta-Delta Ct Hesaplama Uygulaması")

# Kullanıcıdan giriş al
st.header("Hasta ve Kontrol Grubu Verisi Girin")

# Hedef Gen Sayısı
num_target_genes = st.number_input("Hedef Gen Sayısını Girin", min_value=1, step=1)

data = []

for i in range(num_target_genes):
    st.subheader(f"Hedef Gen {i+1}")
    
    control_target_ct = st.text_area(f"Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    sample_target_ct = st.text_area(f"Hasta Grubu Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}")
    sample_reference_ct = st.text_area(f"Hasta Grubu Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}")
    
    def parse_input_data(input_data):
        return np.array([float(x.replace(",", ".").strip()) for x in input_data.split() if x.strip()])
    
    if control_target_ct and control_reference_ct and sample_target_ct and sample_reference_ct:
        control_target_ct_values = parse_input_data(control_target_ct)
        control_reference_ct_values = parse_input_data(control_reference_ct)
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)

        # Çalışmayan örnekleri filtrele
        valid_control_mask = ~np.isnan(control_target_ct_values) & ~np.isnan(control_reference_ct_values)
        valid_sample_mask = ~np.isnan(sample_target_ct_values) & ~np.isnan(sample_reference_ct_values)

        control_target_ct_values = control_target_ct_values[valid_control_mask]
        control_reference_ct_values = control_reference_ct_values[valid_control_mask]
        sample_target_ct_values = sample_target_ct_values[valid_sample_mask]
        sample_reference_ct_values = sample_reference_ct_values[valid_sample_mask]

        control_delta_ct = control_target_ct_values - control_reference_ct_values
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
        average_control_delta_ct = np.mean(control_delta_ct) if len(control_delta_ct) > 0 else np.nan
        average_sample_delta_ct = np.mean(sample_delta_ct) if len(sample_delta_ct) > 0 else np.nan
        
        delta_delta_ct = average_sample_delta_ct - average_control_delta_ct if not np.isnan(average_control_delta_ct) and not np.isnan(average_sample_delta_ct) else np.nan
        
        expression_change = 2 ** (-delta_delta_ct) if not np.isnan(delta_delta_ct) else np.nan
        
        if np.isnan(expression_change):
            regulation_status = "Hesaplanamadı"
        elif expression_change == 1:
            regulation_status = "Değişim Yok"
        elif expression_change > 1:
            regulation_status = "Upregulated"
        else:
            regulation_status = "Downregulated"
        
        data.append({
            "Hedef Gen": f"Hedef Gen {i+1}",
            "Kontrol ΔCt (Ortalama)": average_control_delta_ct,
            "Hasta ΔCt (Ortalama)": average_sample_delta_ct,
            "ΔΔCt": delta_delta_ct,
            "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
            "Regülasyon Durumu": regulation_status,
            "Analiz Edilen Kontrol Örnek Sayısı": len(control_delta_ct),
            "Analiz Edilen Hasta Örnek Sayısı": len(sample_delta_ct)
        })

df = pd.DataFrame(data)

st.subheader("Sonuçlar")
st.write(df)

for i, row in df.iterrows():
    fig, ax = plt.subplots()
    
    x_positions_control = np.full(len(control_delta_ct), 1) + np.random.uniform(-0.05, 0.05, len(control_delta_ct))
    x_positions_sample = np.full(len(sample_delta_ct), 2) + np.random.uniform(-0.05, 0.05, len(sample_delta_ct))
    
    ax.scatter(x_positions_control, control_delta_ct, color='blue', alpha=0.6, label='Kontrol Bireyleri')
    ax.scatter(x_positions_sample, sample_delta_ct, color='red', alpha=0.6, label='Hasta Bireyleri')
    
    if not np.isnan(row["Kontrol ΔCt (Ortalama)"]):
        ax.plot([0.9, 1.1], [row["Kontrol ΔCt (Ortalama)"], row["Kontrol ΔCt (Ortalama)"]], color='blue', linewidth=2)
    if not np.isnan(row["Hasta ΔCt (Ortalama)"]):
        ax.plot([1.9, 2.1], [row["Hasta ΔCt (Ortalama)"], row["Hasta ΔCt (Ortalama)"]], color='red', linewidth=2)
    
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Kontrol Grubu", "Hasta Grubu"])
    ax.set_xlabel("Grup")
    ax.set_ylabel("ΔCt Değerleri")
    ax.set_title(f"Hedef Gen {i+1} - ΔCt Değerleri")
    ax.legend()
    
    st.pyplot(fig)
