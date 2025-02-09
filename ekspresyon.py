import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Başlık
st.title("Delta-Delta Ct Hesaplama Uygulaması")

# Kullanıcıdan giriş al
st.header("Hasta ve Kontrol Grubu Verisi Girin")

# Hedef Gen Sayısı
num_target_genes = st.number_input("Hedef Gen Sayısını Girin", min_value=1, step=1)

# Listeyi oluştur
data = []

# Formu oluştur ve her hedef gen için Ct değerlerini al
for i in range(num_target_genes):
    st.subheader(f"Hedef Gen {i+1}")
    
    # Kullanıcıdan birden fazla Ct değeri yapıştırmasını al
    control_target_ct = st.text_area(f"Kontrol Grubu Hedef Gen Ct Değerleri {i+1} (Virgülle Ayırın)", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"Kontrol Grubu Referans Gen Ct Değerleri {i+1} (Virgülle Ayırın)", key=f"control_reference_ct_{i}")
    sample_target_ct = st.text_area(f"Hasta Grubu Hedef Gen Ct Değerleri {i+1} (Virgülle Ayırın)", key=f"sample_target_ct_{i}")
    sample_reference_ct = st.text_area(f"Hasta Grubu Referans Gen Ct Değerleri {i+1} (Virgülle Ayırın)", key=f"sample_reference_ct_{i}")
    
    # Ct değerlerini virgülle ayırıp listeye çevir
    control_target_ct_values = np.array([float(x) for x in control_target_ct.split(',') if x.strip()])
    control_reference_ct_values = np.array([float(x) for x in control_reference_ct.split(',') if x.strip()])
    sample_target_ct_values = np.array([float(x) for x in sample_target_ct.split(',') if x.strip()])
    sample_reference_ct_values = np.array([float(x) for x in sample_reference_ct.split(',') if x.strip()])
    
    # ΔCt hesaplama
    control_delta_ct = control_target_ct_values - control_reference_ct_values
    sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
    
    # Ortalama ΔCt hesaplama
    average_control_delta_ct = np.mean(control_delta_ct)
    average_sample_delta_ct = np.mean(sample_delta_ct)
    
    # ΔΔCt hesaplama
    delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
    
    # 2^(-ΔΔCt) hesaplama (Gen Ekspresyonu)
    expression_change = 2 ** (-delta_delta_ct)
    
    # Upregulate veya Downregulate kararını verme
    if expression_change == 1:
        regulation_status = "Değişim Yok"
    elif expression_change > 1:
        regulation_status = "Upregulated"
    else:
        regulation_status = "Downregulated"
    
    # Data'ya ekleme
    data.append({
        "Hedef Gen": f"Hedef Gen {i+1}",
        "Kontrol ΔCt (Ortalama)": average_control_delta_ct,
        "Hasta ΔCt (Ortalama)": average_sample_delta_ct,
        "ΔΔCt": delta_delta_ct,
        "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
        "Regülasyon Durumu": regulation_status
    })

# DataFrame'e dönüştür
df = pd.DataFrame(data)

# Sonuçları göster
st.subheader("Sonuçlar Tablosu")
st.write(df)

# Hata Çubuklu Grafik: ΔCt ortalamaları
control_means = df["Kontrol ΔCt (Ortalama)"].values
sample_means = df["Hasta ΔCt (Ortalama)"].values
control_std = np.std([control_target_ct_values - control_reference_ct_values for control_target_ct_values, control_reference_ct_values in zip(df["Kontrol ΔCt (Ortalama)"], df["Hasta ΔCt (Ortalama)"])], axis=0)
sample_std = np.std([sample_target_ct_values - sample_reference_ct_values for sample_target_ct_values, sample_reference_ct_values in zip(df["Kontrol ΔCt (Ortalama)"], df["Hasta ΔCt (Ortalama)"])], axis=0)

# Grafik Çizme
fig, ax = plt.subplots()
bar_width = 0.35
index = np.arange(len(df))

bar1 = ax.bar(index - bar_width/2, control_means, bar_width, yerr=control_std, label="Kontrol Grubu", color='lightblue', capsize=5)
bar2 = ax.bar(index + bar_width/2, sample_means, bar_width, yerr=sample_std, label="Hasta Grubu", color='lightcoral', capsize=5)

ax.set_xlabel('Hedef Genler')
ax.set_ylabel('Ortalama ΔCt')
ax.set_title('Kontrol ve Hasta Grubu ΔCt Ortalamaları ve Hata Çubukları')
ax.set_xticks(index)
ax.set_xticklabels([f"Hedef Gen {i+1}" for i in range(len(df))])
ax.legend()

st.pyplot(fig)
