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
num_patient_groups = st.number_input("Hasta Grubu Sayısını Girin", min_value=1, step=1)

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
    
    if control_target_ct and control_reference_ct:
        control_target_ct_values = parse_input_data(control_target_ct)
        control_reference_ct_values = parse_input_data(control_reference_ct)
        
        min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
        
        if min_control_len == 0:
            st.error("Hata: Kontrol grubu için en az bir veri girilmelidir!")
            continue
        
        control_target_ct_values = control_target_ct_values[:min_control_len]
        control_reference_ct_values = control_reference_ct_values[:min_control_len]
        control_delta_ct = control_target_ct_values - control_reference_ct_values
        average_control_delta_ct = np.mean(control_delta_ct)
        
        for j in range(num_patient_groups):
            st.subheader(f"Hasta Grubu {j+1} - Hedef Gen {i+1}")
            
            sample_target_ct = st.text_area(f"Hasta Grubu {j+1} Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}_{j}")
            sample_reference_ct = st.text_area(f"Hasta Grubu {j+1} Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}_{j}")
            
            if sample_target_ct and sample_reference_ct:
                sample_target_ct_values = parse_input_data(sample_target_ct)
                sample_reference_ct_values = parse_input_data(sample_reference_ct)
                
                min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
                
                if min_sample_len == 0:
                    st.error(f"Hata: Hasta grubu {j+1} için en az bir veri girilmelidir!")
                    continue
                
                sample_target_ct_values = sample_target_ct_values[:min_sample_len]
                sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
                
                sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
                average_sample_delta_ct = np.mean(sample_delta_ct)
                
                delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
                expression_change = 2 ** (-delta_delta_ct)
                
                regulation_status = "Değişim Yok" if expression_change == 1 else ("Upregulated" if expression_change > 1 else "Downregulated")
                
                # Grafik oluşturma
                st.subheader(f"Hedef Gen {i+1} - Hasta Grubu {j+1} ve Kontrol Grubu Dağılım Grafiği")
                fig = go.Figure()
                
                fig.add_trace(go.Box(y=control_delta_ct, name='Kontrol Grubu', marker_color='blue'))
                fig.add_trace(go.Box(y=sample_delta_ct, name=f'Hasta Grubu {j+1}', marker_color='red'))
                
                fig.update_layout(
                    title=f"Hedef Gen {i+1} - ΔCt Dağılımı",
                    yaxis_title='ΔCt Değeri',
                    boxmode='group'
                )
                
                st.plotly_chart(fig)

if data:
    st.subheader("Sonuçlar Tablosu")
    df = pd.DataFrame(data)
    st.write(df)

if stats_data:
    st.subheader("İstatistik Sonuçları")
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
