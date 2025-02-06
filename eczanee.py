import streamlit as st
import requests

def get_pharmacies(city, district):
    url = f"https://api.nobetcieczaneler.com/{city}/{district}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

st.title("Nöbetçi Eczane Bulucu")

city = st.text_input("Şehir giriniz:")
district = st.text_input("İlçe giriniz:")

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
            st.error("Eczane bilgileri alınamadı, lütfen tekrar deneyin.")
    else:
        st.warning("Lütfen bir şehir ve ilçe adı giriniz.")
