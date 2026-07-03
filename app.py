import streamlit as st
import requests
import json

# Sahifa sarlavhasi
st.set_page_config(page_title="909 Recruiting Portal", page_icon="🚚", layout="centered")
st.title("🚚 909 Recruiting Agency — Driver Entry Portal")
st.write("Recruiterlar uchun haydovchi ma'lumotlarini kiritish tizimi.")

# Notion API Sozlamalari (Bularni Streamlit Secrets ichiga yashiramiz)
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Forma yaratish
with st.form("driver_form", clear_on_submit=True):
    st.subheader("Haydovchi Ma'lumotlari")
    
    driver_name = st.text_input("Haydovchining Ismi va Familiyasi (Full Name)*")
    phone_number = st.text_input("Telefon Raqami (Phone Number)*")
    
    driver_type = st.selectbox("Haydovchi Turi (Driver Type)", 
                               ["Solo ($500-$600)", "Team ($1100-$1200)", "Owner-Operator ($1100-$1200)"])
    
    recruiter_name = st.selectbox("Sizning Ismingiz (Recruiter Name)", 
                                  ["Jason", "Adam", "Martin", "Jacob", "Tom", "Stan"])
    
    # Qo'shimcha OTR ma'lumotlari (Telegram kanalga avtomat chiqadigan shablon uchun)
    st.subheader("OTR / Yuk Ma'lumotlari (Kanal uchun)")
    experience = st.number_input("Tajribasi (Yil hisobida)", min_value=0, max_value=50, value=2)
    weekly_miles = st.text_input("Haftalik mili (Weekly Miles)", value="4000+ miles")
    eld_type = st.selectbox("ELD Turi", ["Friendly", "Strict", "No ELD"])
    home_time = st.text_input("Uydagi vaqti (Home Time)", value="3 weeks out / a week home time")
    
    cdl_file = st.file_uploader("CDL Nusxasini Yuklang (Rasm shaklida)*", type=["png", "jpg", "jpeg"])
    
    submit_button = st.form_submit_button(label="Notionga Yuklash 🚀")

# Tugma bosilganda Notion API ga jo'natish logikasi
if submit_button:
    if not driver_name or not phone_number or not cdl_file:
        st.error("Iltimos, yulduzcha (*) qo'yilgan barcha majburiy maydonlarni to'ldiring va CDL rasmini yuklang!")
    else:
        # Notion'ga yuboriladigan JSON Ma'lumot strukturasi
        notion_data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Driver Name": {"title": [{"text": {"content": driver_name}}]},
                "Phone Number": {"phone_number": phone_number},
                "Driver Type": {"select": {"name": driver_type}},
                "Status": {"status": {"name": "Lead"}}, # Yangi kirgan driver avtomatik "Lead" bo'ladi
            }
        }
        
        # Notion API ga POST so'rovi yuborish
        response = requests.post("https://api.notion.com/v1/pages", headers=headers, data=json.dumps(notion_data))
        
        if response.status_config == 200 or response.status_code == 201:
            st.success(f"Muvaffaqiyatli bajarildi! {driver_name} ma'lumotlari markaziy bazaga yuklandi. Seller tez orada bog'lanadi.")
        else:
            st.error(f"Xatolik yuz berdi. Notionga ulanib bo'lmadi: {response.text}")
