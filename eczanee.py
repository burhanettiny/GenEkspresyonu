import streamlit as st

# Sahte nöbetçi eczane verileri
def get_pharmacies(city, district):
    dummy_data = {
        "İstanbul": {
            "Kadıköy": [
                {"name": "Kadıköy Eczanesi", "address": "Kadıköy, İstanbul", "phone": "0216 123 45 67", "latitude": 40.982, "longitude": 29.025}],
            "Beşiktaş": [
                {"name": "Beşiktaş Eczanesi", "address": "Beşiktaş, İstanbul", "phone": "0212 123 45 67", "latitude": 41.041, "longitude": 29.008}]
        },
        "Ankara": {
            "Çankaya": [
                {"name": "Çankaya Eczanesi", "address": "Çankaya, Ankara", "phone": "0312 123 45 67", "latitude": 39.920, "longitude": 32.854}]
        }
    }
    return dummy_data.get(city, {}).get(district, [])

st.title("Nöbetçi Eczane Bulucu")

cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"]  # Örnek şehir listesi
city = st.selectbox("Şehir seçiniz:", cities)

districts = {
    "İstanbul": ["Kadıköy", "Beşiktaş", "Şişli"],
    "Ankara": ["Çankaya", "Keçiören", "Mamak"],
    "İzmir": ["Konak", "Bornova", "Karşıyaka"],
    "Bursa": ["Osmangazi", "Nilüfer", "Yıldırım"],
    "Antalya": ["Muratpaşa", "Kepez", "Konyaaltı"]
}

district = st.selectbox("İlçe seçiniz:", districts.get(city, []))

if st.button("Eczaneleri Listele"):
    if city and district:
        pharmacies = get_pharmacies(city, district)
        if pharmacies:
            for pharmacy in pharmacies:
                st.subheader(pharmacy['name'])
                st.write(f"Adres: {pharmacy['address']}")
                st.write(f"Telefon: {pharmacy['phone']}")
                st.map([[pharmacy['latitude'], pharmacy['longitude']]])
        else:
            st.error("Bu bölgede nöbetçi eczane bulunamadı.")
    else:
        st.warning("Lütfen bir şehir ve ilçe seçiniz.")
