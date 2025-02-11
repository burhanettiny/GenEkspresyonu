import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import scipy.stats as stats
from fpdf import FPDF
import io

# Başlık
st.title("🧬 Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

# Kullanıcıdan giriş al
st.header("📊 Hasta ve Kontrol Grubu Verisi Yükleyin")
uploaded_file = st.file_uploader("CSV dosyanızı yükleyin", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Yüklenen Veri:")
    st.dataframe(df)
    
    if "Hasta" in df.columns and "Kontrol" in df.columns:
        # ΔCt hesapla
        df["ΔCt_Hasta"] = df["Hasta"].astype(float) - df["Referans"].astype(float)
        df["ΔCt_Kontrol"] = df["Kontrol"].astype(float) - df["Referans"].astype(float)
        df["ΔΔCt"] = df["ΔCt_Hasta"] - df["ΔCt_Kontrol"]
        df["Kat Değişimi (Fold Change)"] = 2 ** (-df["ΔΔCt"])
        
        st.subheader("📊 Hesaplanan Sonuçlar")
        st.dataframe(df)

        # İstatistiksel analiz
        t_stat, p_value = stats.ttest_ind(df["ΔCt_Hasta"], df["ΔCt_Kontrol"], equal_var=False)
        st.subheader("📈 İstatistiksel Analiz")
        st.write(f"Bağımsız örneklem t-testi sonucu: t = {t_stat:.4f}, p = {p_value:.4f}")

        # Grafik oluşturma
        fig = px.box(df.melt(id_vars=["Gen"], value_vars=["ΔCt_Hasta", "ΔCt_Kontrol"], var_name="Grup", value_name="ΔCt Değeri"), 
                     x="Grup", y="ΔCt Değeri", color="Grup", title="Hasta ve Kontrol Gruplarının ΔCt Dağılımı")
        st.plotly_chart(fig)
    
        # CSV ve PDF indirme seçenekleri
        csv_output = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Sonuçları CSV Olarak İndir", data=csv_output, file_name="gen_ekspresyon_sonuclari.csv", mime="text/csv")
        
        def create_pdf(data):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", style='B', size=16)
            pdf.cell(200, 10, "Gen Ekspresyon Analizi Raporu", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, "📋 Hesaplanan Sonuçlar", ln=True)
            pdf.ln(5)
            for _, row in data.iterrows():
                pdf.cell(0, 10, f"{row.to_string(index=False)}", ln=True)
            pdf.ln(10)
            
            pdf.cell(200, 10, f"📈 Bağımsız t-testi: t = {t_stat:.4f}, p = {p_value:.4f}", ln=True)
            pdf.ln(10)
            
            pdf_buffer = io.BytesIO()
            pdf.output(pdf_buffer)
            return pdf_buffer.getvalue()
        
        if st.button("📥 PDF Raporu İndir"):
            pdf_content = create_pdf(df)
            st.download_button(label="PDF Olarak İndir", data=pdf_content, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
