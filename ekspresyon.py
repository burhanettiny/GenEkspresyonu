import streamlit as st
import pandas as pd
import numpy as np

# Başlık
st.title("Delta-Delta Ct Hesaplama Uygulaması")

# Kullanıcıdan giriş al
st.header("PCR Verilerini Girin")

# Kontrol ve örnek grubu için Ct değerlerini girme
control_target_ct = st.number_input("Kontrol Grubu Hedef Gen Ct Değeri", min_value=0.0, step=0.1)
control_reference_ct = st.number_input("Kontrol Grubu Referans Gen Ct Değeri", min_value=0.0, step=0.1)
sample_target_ct = st.number_input("Örnek Grubu Hedef Gen Ct Değeri", min_value=0.0, step=0.1)
sample_reference_ct = st.number_input("Örnek Grubu Referans Gen Ct Değeri", min_value=0.0, step=0.1)

# Delta Ct Hesaplama
st.subheader("ΔCt Hesaplama")
control_delta_ct = control_target_ct - control_reference_ct
sample_delta_ct = sample_target_ct - sample_reference_ct

st.write(f"Kontrol Grubu ΔCt: {control_delta_ct}")
st.write(f"Örnek Grubu ΔCt: {sample_delta_ct}")

# Delta-Delta Ct Hesaplama
st.subheader("ΔΔCt Hesaplama")
delta_delta_ct = sample_delta_ct - control_delta_ct

# 2^(-ΔΔCt) Hesaplama
expression_change = 2 ** (-delta_delta_ct)

st.write(f"ΔΔCt: {delta_delta_ct}")
st.write(f"Gen Ekspresyon Değişimi (2^(-ΔΔCt)): {expression_change}")

# Sonuçları görselleştirme
st.subheader("Sonuçlar")
result_df = pd.DataFrame({
    "Kontrol Grubu Hedef Gen Ct": [control_target_ct],
    "Kontrol Grubu Referans Gen Ct": [control_reference_ct],
    "Örnek Grubu Hedef Gen Ct": [sample_target_ct],
    "Örnek Grubu Referans Gen Ct": [sample_reference_ct],
    "Kontrol ΔCt": [control_delta_ct],
    "Örnek ΔCt": [sample_delta_ct],
    "ΔΔCt": [delta_delta_ct],
    "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": [expression_change]
})

st.write(result_df)
