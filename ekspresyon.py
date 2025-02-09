import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

# Başlık
st.title("Delta-Delta Ct Hesaplama Uygulaması")

# Kullanıcıdan giriş al
st.header("Hasta ve Kontrol Grubu Verisi Girin")

# Veriyi yükle (Excel veya metin dosyası)
st.subheader("Excel Dosyasından Veri Yükleyin veya Verileri Yapıştırın")

uploaded_file = st.file_uploader("Excel veya CSV dosyasını yükleyin", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Excel veya CSV dosyasını oku
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)

    # Dosya yüklendiyse tabloyu göster
    st.write("Yüklenen Veri:")
    st.write(df)
else:
    # Kullanıcı verileri manuel girebilir
    st.warning("Lütfen verilerinizi yükleyin veya girin.")
    st.subheader("Veri Formatı: Virgülle veya Nokta ile Ayrılmış")
    
    # Kullanıcıdan birden fazla Ct değeri yapıştırmasını al
    control_target_ct = st.text_area("Kontrol Grubu Hedef Gen Ct Değerleri (Virgülle/Noktalarla Ayrılmış)", "")
    control_reference_ct = st.text_area("Kontrol Grubu Referans Gen Ct Değerleri (Virgülle/Noktalarla Ayrılmış)", "")
    sample_target_ct = st.text_area("Hasta Grubu Hedef Gen Ct Değerleri (Virgülle/Noktalarla Ayrılmış)", "")
    sample_reference_ct = st.text_area("Hasta Grubu Referans Gen Ct Değerleri (Virgülle/Noktalarla Ayrılmış)", "")
    
    # Verileri virgülle veya noktayla ayırarak listeye çevirme
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
        
        # Sonuçları gösterme
        st.subheader("Sonuçlar")
        st.write(f"Kontrol Grubunun Ortalama ΔCt: {average_control_delta_ct}")
        st.write(f"Hasta Grubunun Ortalama ΔCt: {average_sample_delta_ct}")
        st.write(f"ΔΔCt: {delta_delta_ct}")
        st.write(f"Gen Ekspresyon Değişimi (2^(-ΔΔCt)): {expression_change}")
        st.write(f"Gen Ekspresyon Durumu: {regulation_status}")
        
        # Grafik Çizme: Noktalı çizgi grafiği
        fig, ax = plt.subplots()
        ax.plot(control_target_ct_values, label="Kontrol Grubu Hedef Gen Ct Değerleri", marker='o', linestyle='-', color='lightblue')
        ax.plot(sample_target_ct_values, label="Hasta Grubu Hedef Gen Ct Değerleri", marker='x', linestyle='-', color='lightcoral')
        
        ax.set_xlabel('Veri İndeksi')
        ax.set_ylabel('Ct Değeri')
        ax.set_title('Kontrol ve Hasta Grubu Hedef Gen Ct Değerleri')
        ax.legend()

        st.pyplot(fig)
