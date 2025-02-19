import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Dil seçenekleri ve çeviri fonksiyonu
translations = {
    "English": {
        "header_target_gen": "Target Gene {i+1}",
        "header_control_group": "Control Group Target Gene {i+1} Ct Values",
        "header_patient_group": "Patient Group {j+1} - Target Gene {i+1}",
        "error_message": "⚠️ Attention: Paste values correctly without empty spaces in the cells.",
        "results": "Results",
        "expression_change": "Gene Expression Change (2^(-ΔΔCt))",
        "no_data_warning": "⚠️ Warning: Paste data correctly or write values without blank spaces.",
        "stats_results": "Statistical Results",
        "download_csv": "📥 Download as CSV",
        "graph_error": "⚠️ Error: Missing Control Group data for Target Gene {i+1}!",
        "no_graph_data": "Graph generation requires at least one valid data set.",
    },
    "Türkçe": {
        "header_target_gen": "Hedef Gen {i+1}",
        "header_control_group": "Kontrol Grubu Hedef Gen {i+1} Ct Değerleri",
        "header_patient_group": "Hasta Grubu {j+1} - Hedef Gen {i+1}",
        "error_message": "⚠️ Dikkat: Verileri doğru bir şekilde yapıştırın veya boşluk içermeyen hücreleri kullanın.",
        "results": "Sonuçlar",
        "expression_change": "Gen Ekspresyon Değişimi (2^(-ΔΔCt))",
        "no_data_warning": "⚠️ Dikkat: Verileri doğru şekilde yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.",
        "stats_results": "İstatistiksel Sonuçlar",
        "download_csv": "📥 CSV Olarak İndir",
        "graph_error": "⚠️ Hata: Kontrol Grubu için Hedef Gen {i+1} verileri eksik!",
        "no_graph_data": "Grafik oluşturulabilmesi için en az bir geçerli veri seti gereklidir.",
    }
}

# Dil seçimini Streamlit ile alıyoruz
language = st.selectbox("Choose Language", ["English", "Türkçe"])

def translate(key, *args):
    """Verilen anahtarı dil çevirisiyle döndürür"""
    translation = translations[language][key]
    return translation.format(*args)

# Kullanıcıdan hedef gen sayısı ve hasta grubu sayısını alma
num_target_genes = st.number_input(translate("header_target_gen", 1), min_value=1, value=3, step=1)
num_patient_groups = st.number_input(translate("header_patient_group", 1), min_value=1, value=2, step=1)

# Kullanıcıdan verileri alma (örnek olarak basit bir veri çerçevesi kullanıyoruz)
data_input = st.text_area(translate("no_data_warning"))
if data_input:
    try:
        # Veriyi işleme
        data_lines = data_input.split("\n")
        data = [list(map(float, line.split())) for line in data_lines]
        df = pd.DataFrame(data, columns=[f"Gene_{i+1}" for i in range(num_target_genes)])
        
        st.write(df)

        # Gen ekspresyonu değişimini hesaplama (2^(-ΔΔCt))
        expression_changes = {}
        for i in range(num_target_genes):
            control_group = df.iloc[:, i]  # Kontrollü veri olarak alıyoruz
            patient_group = df.iloc[:, i]  # Hasta verisi alıyoruz (gerçek veriye göre uyarlanmalı)
            
            # ΔΔCt hesaplama (örnek için basitleştirilmiş)
            delta_delta_ct = np.mean(patient_group) - np.mean(control_group)
            expression_change = 2 ** (-delta_delta_ct)
            expression_changes[f"Gene_{i+1}"] = expression_change
        
        # Sonuçları ekrana yazdırma
        st.subheader(translate("results"))
        st.write(expression_changes)

        # Grafik seçme ve çizme
        graph_type = st.selectbox("Select Graph Type", ["Boxplot", "Heatmap", "Histogram", "Scatter Plot"])
        if graph_type == "Boxplot":
            st.write("Generating Boxplot...")
            sns.boxplot(data=df)
            st.pyplot()

        elif graph_type == "Heatmap":
            st.write("Generating Heatmap...")
            sns.heatmap(df)
            st.pyplot()

        elif graph_type == "Histogram":
            st.write("Generating Histogram...")
            plt.hist(df.values.flatten(), bins=20)
            st.pyplot()

        elif graph_type == "Scatter Plot":
            st.write("Generating Scatter Plot...")
            plt.scatter(df.iloc[:, 0], df.iloc[:, 1])
            st.pyplot()

        # CSV olarak indirme
        results_df = pd.DataFrame(expression_changes.items(), columns=["Gene", "Expression Change"])
        st.download_button(
            label=translate("download_csv"),
            data=results_df.to_csv(index=False),
            file_name="gene_expression_results.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(translate("error_message"))
else:
    st.warning(translate("no_data_warning"))
