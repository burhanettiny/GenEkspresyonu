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

# Listeyi oluştur
data = []

# Formu oluştur ve her hedef gen için Ct değerlerini al
for i in range(num_target_genes):
    st.subheader(f"Hedef Gen {i+1}")
    
    # Kullanıcıdan birden fazla Ct değeri yapıştırmasını al
    control_target_ct = st.text_area(f"Kontrol Grubu Hedef Gen {i+1} Ct Değerleri (Virgülle/Noktalarla Ayrılmış)", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"Kontrol Grubu Referans Gen {i+1} Ct Değerleri (Virgülle/Noktalarla Ayrılmış)", key=f"control_reference_ct_{i}")
    sample_target_ct = st.text_area(f"Hasta Grubu Hedef Gen {i+1} Ct Değerleri (Virgülle/Noktalarla Ayrılmış)", key=f"sample_target_ct_{i}")
    sample_reference_ct = st.text_area(f"Hasta Grubu Referans Gen {i+1} Ct Değerleri (Virgülle/Noktalarla Ayrılmış)", key=f"sample_reference_ct_{i}")
    
    # Ct değerlerini virgülle ayırıp listeye çevir
    def parse_input_data(input_data):
        return np.array([float(x.replace(",", ".").strip()) for x in input_data.split() if x.strip()])
    
    if control_target_ct and control_reference_ct and sample_target_ct and sample_reference_ct:
        control_target_ct_values = parse_input_data(control_target_ct)
        control_reference_ct_values = parse_input_data(control_reference_ct)
        sample_target_ct_values = parse_input_data(sample_target_ct)
        sample_reference_ct_values = parse_input_data(sample_reference_ct)

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
        
        # Data'ya ekleme (Kontrol ΔCt verisi artık tabloda gösterilecek)
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
st.subheader("Sonuçlar")
st.write(df)

# Grafik: Her hedef gen için ayrı bir grafik oluşturulacak
for i, row in df.iterrows():
    # Yeni grafik oluştur
    fig, ax = plt.subplots()
    
    # Hasta ve Kontrol Grubu için X eksenini oluştur
    x_positions_control = [1] * len(control_delta_ct)
    x_positions_sample = [2] * len(sample_delta_ct)
    
    # Aynı Y değerlerine sahip noktaları biraz kaydırarak gösterme (dağılım)
    jittered_control = control_delta_ct + np.random.uniform(-0.05, 0.05, size=len(control_delta_ct))
    jittered_sample = sample_delta_ct + np.random.uniform(-0.05, 0.05, size=len(sample_delta_ct))
    
    # Delta Ct değerlerini nokta olarak çiz
    ax.scatter(x_positions_control, jittered_control, color='lightblue', label='Kontrol Grubu', alpha=0.7)
    ax.scatter(x_positions_sample, jittered_sample, color='lightcoral', label='Hasta Grubu', alpha=0.7)

    # Ortalama değerleri kısa çizgilerle göster
    ax.plot([1], [row["Kontrol ΔCt (Ortalama)"]], label='Kontrol Ortalama', color='blue', linestyle='-', marker='o', markersize=8)
    ax.plot([2], [row["Hasta ΔCt (Ortalama)"]], label='Hasta Ortalama', color='red', linestyle='-', marker='o', markersize=8)

    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Kontrol Grubu', 'Hasta Grubu'])
    ax.set_xlabel('Grup')
    ax.set_ylabel('ΔCt Değerleri')
    ax.set_title(f'Hedef Gen {i+1} - ΔCt Değerleri')
    ax.legend()

    st.pyplot(fig)
