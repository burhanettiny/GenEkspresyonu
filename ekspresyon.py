import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
from scipy import stats
import numpy as np

# PDF oluşturma fonksiyonu
def create_pdf(data, stats_data, input_df, num_patient_groups, num_target_genes):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Başlık
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "🧬 Gen Ekspresyon Analizi Sonuçları")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "B. Yalçınkaya tarafından geliştirildi")
    
    y_position = height - 100
    
    # Giriş Verileri
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📋 Giriş Verileri")
    y_position -= 20
    c.setFont("Helvetica", 8)
    for index, row in input_df.iterrows():
        text_line = (
            f"Örnek {row['Örnek Numarası']} - {row['Grup']} - {row['Hedef Gen']} - "
            f"Hedef Gen Ct: {row['Hedef Gen Ct Değeri']} - Referans Ct: {row['Referans Ct']}"
        )
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    y_position -= 20
    
    # Sonuçlar
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📊 Sonuçlar")
    y_position -= 20
    c.setFont("Helvetica", 8)
    for result in data:
        text_line = (
            f"{result['Hedef Gen']} - {result['Hasta Grubu']} - ΔΔCt: {result['ΔΔCt']} - "
            f"Ekspresyon: {result['Gen Ekspresyon Değişimi (2^(-ΔΔCt))']} - {result['Regülasyon Durumu']}"
        )
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    y_position -= 20
    
    # İstatistik Sonuçları
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "📈 İstatistik Sonuçları")
    y_position -= 20
    c.setFont("Helvetica", 8)
    for stat in stats_data:
        text_line = (
            f"{stat['Hedef Gen']} - {stat['Hasta Grubu']} - {stat['Test Türü']} ({stat['Kullanılan Test']}) - "
            f"P-değeri: {stat['Test P-değeri']:.4f} - {stat['Anlamlılık']}"
        )
        c.drawString(50, y_position, text_line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    
    # Hesaplamaların ve istatistiksel değerlendirmenin açıklamaları
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "📝 Hesaplama Yöntemi ve İstatistiksel Değerlendirme")
    c.setFont("Helvetica", 10)
    explanation_text = """
    Bu çalışmada, gen ekspresyonunun karşılaştırılması için ΔCt (delta Ct) yöntemi kullanılmıştır. 
    Bu yöntem, hedef genin ve referans genin Ct (threshold cycle) değerleri arasındaki farkı hesaplayarak, gen ekspresyonunu değerlendirir.
    
    ΔCt hesaplaması şu şekilde yapılır:
    
    ΔCt = Ct_Hedef Gen - Ct_Referans Gen
    
    Bu değer, kontrol ve hasta grupları arasında karşılaştırma yapabilmek için kullanılır. 
    Kontrol grubu ile hasta grubu arasında ΔΔCt (delta-delta Ct) hesaplanır:
    
    ΔΔCt = ΔCt_Hasta Grubu - ΔCt_Kontrol Grubu
    
    Son olarak, gen ekspresyonundaki değişim şu formül ile hesaplanır:
    
    Gen Ekspresyon Değişimi = 2^(-ΔΔCt)
    
    **📊 Veri Yapısı:**
    
    - **Kontrol Grubu:** Her bir hedef gen için kontrol grubunda örnek sayısı ve her örneğe ait Ct değerleri verilmiştir.
    - **Hasta Grupları:** Her hedef gen için, hasta gruplarında farklı sayıda örnekler bulunmaktadır. Bu gruptaki örnekler ve her örneğe ait Ct değerleri belirtilmiştir.
    
    **🧑‍🔬 İstatistiksel Değerlendirme:**
    
    Verilerin parametrik ya da non-parametrik olup olmadığını belirlemek için önce normal dağılım testi yapılmıştır. 
    Kontrol ve hasta grupları arasındaki farkları test etmek için şu adımlar takip edilmiştir:
    
    1. **Normal Dağılım Testi:** 
       - Kontrol grubu ve hasta grubunun ΔCt değerleri için Shapiro-Wilk testi uygulanarak normal dağılım testi yapılmıştır.
       - P-değeri 0.05'ten büyükse, veri normal dağıldığı kabul edilmiştir.
    
    2. **Varyans Homojenliği Testi:** 
       - Levene testi kullanılarak her iki grup için varyans homojenliği test edilmiştir. 
       - Eğer p-değeri 0.05'ten büyükse, iki grup arasındaki varyansların eşit olduğu kabul edilmiştir.
    
    3. **Parametrik ve Non-Parametrik Test Seçimi:**
       - Eğer veriler normal dağılıma uyuyorsa ve varyanslar homojense, bağımsız örnekler için **t-test** kullanılmıştır.
       - Eğer veriler normal dağılıma uymuyorsa veya varyanslar homojen değilse, **Mann-Whitney U testi** gibi non-parametrik testler kullanılmıştır.
    
    **📑 Test Sonuçları:**
    
    - **Anlamlılık Değerlendirmesi:** 
       - İstatistiksel testin p-değeri, 0.05'ten küçükse, fark anlamlı kabul edilmiştir (p < 0.05).
       - Eğer p-değeri 0.05'ten büyükse, fark anlamsız kabul edilmiştir (p ≥ 0.05).
       - Bu sonuçlar, gen ekspresyonundaki değişimlerin gerçekten anlamlı olup olmadığını belirlemeye yardımcı olur.
    
    **📉 Test Türleri:**
    
    - Parametrik testler, normal dağılım ve eşit varyans koşulları altında kullanılmıştır. Eğer bu koşullar sağlanmadıysa, non-parametrik testler tercih edilmiştir.
    - Testin seçimi ve sonuçların anlamlılığı, çalışmada kullanılan gruplar ve verilerin özelliklerine göre belirlenmiştir.
    """
    
    text_object = c.beginText(50, y_position - 30)
    text_object.setFont("Helvetica", 9)
    text_object.textLines(explanation_text)
    c.drawText(text_object)
    
    c.save()
    buffer.seek(0)
    return buffer

# İstatistiksel hesaplamalar ve PDF raporu için örnek veri
num_target_genes = 2
num_patient_groups = 2

input_values_table = [
    {'Örnek Numarası': 1, 'Grup': 'Kontrol', 'Hedef Gen': 'GenA', 'Hedef Gen Ct Değeri': 22.5, 'Referans Ct': 24.5},
    {'Örnek Numarası': 2, 'Grup': 'Hasta', 'Hedef Gen': 'GenA', 'Hedef Gen Ct Değeri': 19.2, 'Referans Ct': 21.4},
    {'Örnek Numarası': 3, 'Grup': 'Kontrol', 'Hedef Gen': 'GenB', 'Hedef Gen Ct Değeri': 23.2, 'Referans Ct': 25.1},
    {'Örnek Numarası': 4, 'Grup': 'Hasta', 'Hedef Gen': 'GenB', 'Hedef Gen Ct Değeri': 20.3, 'Referans Ct': 22.8}
]

# Örnek gen ekspresyon hesaplamaları
data = [
    {'Hedef Gen': 'GenA', 'Hasta Grubu': 'Hasta', 'ΔΔCt': 3.3, 'Gen Ekspresyon Değişimi (2^(-ΔΔCt))': 0.097, 'Regülasyon Durumu': 'Azalma'},
    {'Hedef Gen': 'GenB', 'Hasta Grubu': 'Hasta', 'ΔΔCt': 2.1, 'Gen Ekspresyon Değişimi (2^(-ΔΔCt))': 0.221, 'Regülasyon Durumu': 'Azalma'}
]

# İstatistiksel test sonuçları (örnek)
stats_data = [
    {'Hedef Gen': 'GenA', 'Hasta Grubu': 'Hasta', 'Test Türü': 'Parametrik', 'Kullanılan Test': 't-test', 'Test P-değeri': 0.02, 'Anlamlılık': 'Anlamlı'},
    {'Hedef Gen': 'GenB', 'Hasta Grubu': 'Hasta', 'Test Türü': 'Non-Parametrik', 'Kullanılan Test': 'Mann-Whitney U', 'Test P-değeri': 0.03, 'Anlamlılık': 'Anlamlı'}
]

# PDF raporu oluşturma
input_df = pd.DataFrame(input_values_table)
pdf_buffer = create_pdf(data, stats_data, input_df, num_patient_groups, num_target_genes)
st.download_button(
    label="📥 PDF Raporu İndir",
    data=pdf_buffer,
    file_name="gen_ekspresyon_raporu.pdf",
    mime="application/pdf"
)
