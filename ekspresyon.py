from fpdf import FPDF

# PDF oluşturma fonksiyonu
def create_pdf(data, stats_data, input_df):
    # PDF nesnesi oluşturuluyor
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Başlık
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="Gen Ekspresyon Analizi Raporu", ln=True, align='C')
    pdf.ln(10)

    # Giriş Verileri Tablosu
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(200, 10, txt="Giriş Verileri", ln=True)
    pdf.set_font('Arial', '', 10)
    
    # Giriş Verileri Tablosunu ekleyelim
    col_width = pdf.get_string_width("Grup") + 10  # Sütun genişliği
    for row in input_df.itertuples():
        pdf.ln(5)
        pdf.cell(col_width, 10, str(row[1]), border=1, align='C')
        pdf.cell(col_width, 10, str(row[2]), border=1, align='C')
        pdf.cell(col_width, 10, str(row[3]), border=1, align='C')
        pdf.cell(col_width, 10, str(row[4]), border=1, align='C')
        pdf.cell(col_width, 10, str(row[5]), border=1, align='C')
    pdf.ln(10)

    # Sonuçlar
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(200, 10, txt="Sonuçlar", ln=True)
    pdf.set_font('Arial', '', 10)

    for row in data:
        pdf.ln(5)
        pdf.cell(col_width, 10, str(row["Hedef Gen"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["Hasta Grubu"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["ΔΔCt"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["Gen Ekspresyon Değişimi (2^(-ΔΔCt))"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["Regülasyon Durumu"]), border=1, align='C')
    pdf.ln(10)

    # İstatistik Sonuçları
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(200, 10, txt="İstatistik Sonuçları", ln=True)
    pdf.set_font('Arial', '', 10)

    for row in stats_data:
        pdf.ln(5)
        pdf.cell(col_width, 10, str(row["Hedef Gen"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["Hasta Grubu"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["Test Türü"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["Kullanılan Test"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["Test P-değeri"]), border=1, align='C')
        pdf.cell(col_width, 10, str(row["Anlamlılık"]), border=1, align='C')

    # PDF'yi hafızada tut
    pdf_output = pdf.output(dest='S').encode('latin1')  # PDF içeriğini alıyoruz
    return pdf_output
