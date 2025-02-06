{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "ead98c08-8530-46f4-aa93-de8005cdd778",
   "metadata": {},
   "outputs": [],
   "source": [
    "import streamlit as st\n",
    "import requests\n",
    "\n",
    "# API'den nöbetçi eczaneleri almak için fonksiyon\n",
    "def get_nobetci_eczane(sehir, ilce):\n",
    "    # Gerçek API URL'sini buraya yerleştirin\n",
    "    api_url = f\"https://example.com/nobetci-eczane?sehir={sehir}&ilce={ilce}\"\n",
    "    \n",
    "    try:\n",
    "        response = requests.get(api_url)\n",
    "        response.raise_for_status()\n",
    "        data = response.json()\n",
    "\n",
    "        if data:\n",
    "            return data\n",
    "        else:\n",
    "            return None\n",
    "    except requests.exceptions.RequestException as e:\n",
    "        st.error(f\"Bir hata oluştu: {e}\")\n",
    "        return None\n",
    "\n",
    "# Streamlit uygulamasının başlığı\n",
    "st.title('Nöbetçi Eczane Sorgulama')\n",
    "\n",
    "# Kullanıcıdan şehir ve ilçe bilgisi almak\n",
    "sehir = st.text_input(\"Şehir adı girin:\")\n",
    "ilce = st.text_input(\"İlçe adı girin:\")\n",
    "\n",
    "# Sorgulama butonu\n",
    "if st.button(\"Sorgula\"):\n",
    "    if sehir and ilce:\n",
    "        with st.spinner('Nöbetçi eczaneler sorgulanıyor...'):\n",
    "            eczaneler = get_nobetci_eczane(sehir, ilce)\n",
    "\n",
    "            if eczaneler:\n",
    "                st.write(f\"{ilce} ilçesindeki nöbetçi eczaneler:\")\n",
    "                for eczane in eczaneler:\n",
    "                    st.write(f\"- **{eczane['isim']}**\\n  Adres: {eczane['adres']}\\n  Telefon: {eczane['telefon']}\\n\")\n",
    "            else:\n",
    "                st.warning(f\"{ilce} ilçesinde nöbetçi eczane bulunmamaktadır.\")\n",
    "    else:\n",
    "        st.error(\"Lütfen hem şehir hem de ilçe bilgilerini girin.\")\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
