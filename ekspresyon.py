import streamlit as st
import pandas as pd
import numpy as np

# Başlık
st.title("Delta-Delta Ct Hesaplama Uygulaması")

# Kullanıcıdan giriş al
st.header("Hasta ve Kontrol Grubu Verisi Girin")

# Kullanıcıdan Hedef Gen sayısını al
num_target_genes = st.number_input("Hedef Gen Sayısını Girin", min_value=1, step=1)

# Listeyi oluştur
data = []

# Formu oluştur ve her hedef gen için Ct değerlerini al
for i in range(num_target_genes):
    st.subheader(f"Hedef Gen {i+1}")
    # Kontrol Grubu Ct verileri
    control_target_ct = st.number_input(f"Kontrol Grubu Hedef Gen Ct Değeri {i+1}", min_value=0.0, step=0.1, key=f"control_target_ct_{i}")
    control_reference_ct = st.number_input(f"Kontrol Grubu Referans Gen Ct Değeri {i+1}", min_value=0.0, step=0.1, key=f"control_reference_ct_{i}")
    # Hasta Grubu Ct verileri
    sample_target_ct = st.number_input(f"Hasta Grubu Hedef Gen Ct Değeri {i+1}", min_value=0.0, step=0.1, key=f"sample_target_ct_{i}")
    sample_reference_ct = st.number_input(f"Hasta Grubu Referans Gen Ct Değeri {i+1}", min_value=0.0, step=0.1, key=f"sample_reference_ct_{i}")
    
    # ΔCt hesaplama
    control_delta_ct = control_target_ct - control_reference_ct
    sample_delta_ct = sample_target_ct - sample_reference_ct
    
    # Her bir hedef gen için ΔCt'lerin ortalamasını hesaplamak için
    data.append({
        "Hedef Gen": f"Hedef Gen {i+1}",
        "Kontrol ΔCt": control_delta_ct,
        "Hasta ΔCt": sample_delta_ct
    })

# DataFrame'e dönüştür
df = pd.DataFrame(data)

# Ortalamaları hesapla
average_control_delta_ct = df["Kontrol ΔCt"].mean()
average_sample_delta_ct = df["Hasta ΔCt"].mean()

# ΔΔCt hesaplama
delta_delta_ct = average_sample_delta_ct - average_control_delta_ct

# 2^(-ΔΔCt) hesaplama (Gen Ekspresyonu)
expression_change = 2 ** (-delta_delta_ct)

# Upregulate veya Downregulate kararını verme
regulation_status = "Upregulated" if expression_change > 1 else "Downregulated"

# Sonuçları göster
st.subheader("Sonuçlar Tablosu")
st.write(df)

# Ortalamalar ve Regülasyon Durumu
st.subheader("Genel Sonuçlar")
st.write(f"Kontrol Grubunun Ortalama ΔCt: {average_control_delta_ct}")
st.write(f"Hasta Grubunun Ortalama ΔCt: {average_sample_delta_ct}")
st.write(f"ΔΔCt: {delta_delta_ct}")
st.write(f"Gen Ekspresyon Değişimi (2^(-ΔΔCt)): {expression_change}")
st.write(f"Gen Ekspresyon Durumu: {regulation_status}")
