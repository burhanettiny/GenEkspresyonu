import streamlit as st
import pandas as pd
import numpy as np

# Başlık
st.title("Delta-Delta Ct Hesaplama Uygulaması")

# Kullanıcıdan giriş al
st.header("Birden Fazla Hasta ve Kontrol Grubu Verisi Girin")

# Kullanıcıdan birden fazla grup eklemesi yapabilmesi için bir form oluşturuyoruz
num_samples = st.number_input("Kaç Hasta/Kontrol Grubu Gireceksiniz?", min_value=1, step=1)

# DataFrame için boş liste
data = []

# Formu oluştur ve kullanıcıdan her grup için Ct değerlerini al
for i in range(num_samples):
    st.subheader(f"Grup {i+1}")
    control_target_ct = st.number_input(f"Kontrol Grubu Hedef Gen Ct Değeri {i+1}", min_value=0.0, step=0.1, key=f"control_target_ct_{i}")
    control_reference_ct = st.number_input(f"Kontrol Grubu Referans Gen Ct Değeri {i+1}", min_value=0.0, step=0.1, key=f"control_reference_ct_{i}")
    sample_target_ct = st.number_input(f"Örnek Grubu Hedef Gen Ct Değeri {i+1}", min_value=0.0, step=0.1, key=f"sample_target_ct_{i}")
    sample_reference_ct = st.number_input(f"Örnek Grubu Referans Gen Ct Değeri {i+1}", min_value=0.0, step=0.1, key=f"sample_reference_ct_{i}")
    
    # ΔCt hesaplama
    control_delta_ct = control_target_ct - control_reference_ct
    sample_delta_ct = sample_target_ct - sample_reference_ct
    
    # ΔΔCt hesaplama
    delta_delta_ct = sample_delta_ct - control_delta_ct
    
    # 2^(-ΔΔCt) hesaplama (Gen Ekspresyonu)
    expression_change = 2 ** (-delta_delta_ct)
    
    # Upregulate veya Downregulate kararını verme
    regulation_status = "Upregulated" if expression_change > 1 else "Downregulated"
    
    # Data'ya ekleme
    data.append({
        "Grup": f"Grup {i+1}",
        "Kontrol ΔCt": control_delta_ct,
        "Örnek ΔCt": sample_delta_ct,
        "ΔΔCt": delta_delta_ct,
        "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
        "Regülasyon Durumu": regulation_status
    })

# Sonuçları bir DataFrame olarak göster
df = pd.DataFrame(data)

# Sonuç tablosunu göster
st.subheader("Sonuçlar Tablosu")
st.write(df)
