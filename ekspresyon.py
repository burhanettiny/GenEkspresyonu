import streamlit as st
import pandas as pd
import numpy as np

# Dillerin tanımlandığı sözlük
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

# Dil seçimi (İngilizce veya Türkçe)
language = st.selectbox("Select Language", ("English", "Türkçe"))

# Çeviri fonksiyonu
def translate(key):
    return translations[language][key]

# Sayfa başlığı
st.title(translate("results"))

# Hedef gen sayısı ve hasta grubu sayısı
num_target_genes = st.number_input(translate("header_target_gen").format(i=0), min_value=1, value=3, step=1)
num_patient_groups = st.number_input(translate("header_patient_group").format(j=0), min_value=1, value=2, step=1)

# Hedef genler ve gruplar için veri girişi
data = {}
for i in range(num_target_genes):
    # Kontrol grubu için değerler
    control_group_values = st.text_area(translate("header_control_group").format(i=i), "")
    if control_group_values:
        data[f"control_group_gene_{i+1}"] = np.array([float(x) for x in control_group_values.split() if x])

    # Hasta gruplarına ait değerler
    for j in range(num_patient_groups):
        patient_group_values = st.text_area(translate("header_patient_group").format(i=i, j=j), "")
        if patient_group_values:
            data[f"patient_group_{j+1}_gene_{i+1}"] = np.array([float(x) for x in patient_group_values.split() if x])

# Veriler eğer sağlanmışsa, hesaplama ve görselleştirme işlemleri
if data:
    st.write(translate("expression_change"))

    # Örnek hesaplama: 2^(-ΔΔCt)
    expression_changes = {}
    for i in range(num_target_genes):
        control_values = data[f"control_group_gene_{i+1}"]
        for j in range(num_patient_groups):
            patient_values = data[f"patient_group_{j+1}_gene_{i+1}"]
            delta_delta_ct = np.mean(patient_values) - np.mean(control_values)
            expression_changes[f"Gene_{i+1}_Group_{j+1}"] = 2 ** (-delta_delta_ct)

    # Hesaplanan gen ekspresyon değişimlerini göster
    st.write(expression_changes)

    # CSV indirme linki
    df = pd.DataFrame(expression_changes.items(), columns=["Gene_Group", "Expression_Change"])
    st.download_button(
        label=translate("download_csv"),
        data=df.to_csv(index=False),
        file_name="gene_expression_changes.csv",
        mime="text/csv",
    )

else:
    st.warning(translate("no_graph_data"))
