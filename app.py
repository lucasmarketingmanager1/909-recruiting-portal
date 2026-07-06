import streamlit as st
import requests
import json

# Sahifa sozlamalari
st.set_page_config(page_title="909 Recruiting Portal", page_icon="🚚", layout="centered")
st.title("🚚 909 Recruiting Agency — Driver Entry Portal")
st.write("Recruiterlar uchun haydovchi ma'lumotlarini avtomatlashtirilgan kiritish tizimi.")

# Streamlit Secrets ichidan maxfiy kalitlarni oqish
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
MAIN_DATABASE_ID = st.secrets["DATABASE_ID"]

# TEAM LEADS database ID raqamini aniqlash (Main database ID-dan kelib chiqib avtomat topish yoki bitta secretsga yozish mumkin)
# Bu yerda biz TEAM LEADS database ID-sini ham bitta secrets orqali olamiz
TEAM_DATABASE_ID = st.secrets.get("TEAM_DATABASE_ID", "")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 1. TEAM LEADS jadvalidan faqat "Active" xodimlarning ismlarini avtomat oqib olish funksiyasi
def get_active_recruiters():
    if not TEAM_DATABASE_ID:
        return ["Adam", "Jason", "Martin", "Tom", "Jacob", "Eric"] # Agar ID kiritilmagan bo'lsa, zaxira ro'yxat
    
    url = f"https://api.notion.com/v1/databases/{TEAM_DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Status",
            "status": {"equals": "Active"}
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            results = response.json().get("results", [])
            recruiters = {}
            for page in results:
                name_list = page["properties"]["Name"]["title"]
                if name_list:
                    name = name_list[0]["plain_text"]
                    role = page["properties"]["Role"]["select"]["name"]
                    if role == "Recruiter":
                        recruiters[name] = page["id"] # Ism va uning raqamli ID-si saqlanadi
            return recruiters
        return {"Adam": "", "Jason": "", "Martin": "", "Tom": ""}
    except:
        return {"Adam": "", "Jason": "", "Martin": "", "Tom": ""}

# Jonli xodimlar ro'yxatini yuklash
recruiter_dict = get_active_recruiters()
recruiter_options = list(recruiter_dict.keys())

# Forma yaratish
with st.form("driver_form", clear_on_submit=True):
    st.subheader("Haydovchi Ma'lumotlari")
    
    driver_name = st.text_input("Haydovchining Ismi va Familiyasi (Full Name)*")
    phone_number = st.text_input("Telefon Raqami (Phone Number)*")
    
    driver_type = st.selectbox("Haydovchi Turi (Driver Type)", 
                               ["Solo ($500-$600)", "Team ($1100-$1200)", "Owner-Operator ($1100-$1200)"])
    
    selected_recruiter = st.selectbox("Sizning Ismingiz (Recruiter Name)", recruiter_options)
    
    st.subheader("OTR / Yuk Ma'lumotlari (Kanal uchun)")
    experience = st.number_input("Tajribasi (Yil hisobida)", min_value=0, max_value=50, value=2)
    weekly_miles = st.text_input("Haftalik mili (Weekly Miles)", value="4000+ miles")
    eld_type = st.selectbox("ELD Turi", ["Friendly", "Strict", "No ELD"])
    home_time = st.text_input("Uydagi vaqti (Home Time)", value="3 weeks out / a week home time")
    
    cdl_file = st.file_uploader("CDL Nusxasini Yuklang (Rasm shaklida)*", type=["png", "jpg", "jpeg"])
    
    submit_button = st.form_submit_button(label="Notionga Yuklash 🚀")

if submit_button:
    if not driver_name or not phone_number or not cdl_file:
        st.error("Iltimos, barcha majburiy maydonlarni to'ldiring!")
    else:
        recruiter_id = recruiter_dict.get(selected_recruiter, "")
        
        # --- 1-OQIM: NOTION PIPELINE UCHUN ---
        notion_data = {
            "parent": {"database_id": MAIN_DATABASE_ID},
            "properties": {
                "Driver Name": {"title": [{"text": {"content": driver_name}}]},
                "Phone Number": {"phone_number": phone_number},
                "Driver Type": {"select": {"name": driver_type}},
                "Status": {"status": {"name": "Lead"}}
            }
        }
        
        if recruiter_id:
            notion_data["properties"]["Recruiter"] = {"relation": [{"id": recruiter_id}]}
            
        notion_response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=notion_data)
        
        if notion_response.status_code == 200 or notion_response.status_code == 201:
            # Notion-da ochilgan haqiqiy sahifa linkini sug'urib olamiz
            notion_page_url = notion_response.json().get("url", "https://notion.so")
            
            st.success(f"✅ {driver_name} ma'lumotlari Notion bazasiga muvaffaqiyatli yuklandi!")
            st.markdown(f"🔗 **[Notion-da ochilgan sahifani ko'rish uchun bu yerga bosing]({notion_page_url})**")
            
            # --- 2-OQIM: N8N WEBHOOK VA TELEGRAM UCHUN (Rasm va OTR) ---
            webhook_url = "https://recruiting909.app.n8n.cloud/webhook-test/b2efcc0b-1001-4936-8847-9a626d3dfe70"
            
            files = {
                "cdl_file": (cdl_file.name, cdl_file.getvalue(), cdl_file.type)
            }
            
            data = {
                "driver_name": driver_name,
                "driver_type": driver_type,
                "experience": experience,
                "weekly_miles": weekly_miles,
                "eld_type": eld_type,
                "home_time": home_time,
                "recruiter": selected_recruiter
            }
            
            try:
                # n8n ga eshikni ochish va ma'lumotni uzatish
                n8n_response = requests.post(webhook_url, data=data, files=files)
                if n8n_response.status_code == 200:
                    st.info("🚀 CDL Rasm va OTR ma'lumotlari n8n qopqoniga muvaffaqiyatli yetib bordi!")
                else:
                    st.warning(f"⚠️ n8n serveri qabul qilmadi: {n8n_response.text}")
            except Exception as e:
                st.error(f"❌ n8n aloqa uzildi: {e}")
                
        else:
            st.error(f"❌ Notion API yuklashni rad etdi: {notion_response.status_code} - {notion_response.text}")
