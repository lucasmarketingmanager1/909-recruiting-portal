import streamlit as st
import requests

# Sahifa sozlamalari
st.set_page_config(page_title="909 Recruiting Portal", page_icon="🚚", layout="centered")
st.title("🚚 909 Recruiting Agency — Driver Entry Portal")

# Maxfiy kalitlar
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
MAIN_DATABASE_ID = st.secrets["DATABASE_ID"]
TEAM_DATABASE_ID = st.secrets.get("TEAM_DATABASE_ID", "")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_active_recruiters():
    if not TEAM_DATABASE_ID:
        return ["Adam", "Jason", "Martin", "Tom", "Jacob", "Eric", "Lucas"] 
    url = f"https://api.notion.com/v1/databases/{TEAM_DATABASE_ID}/query"
    payload = {"filter": {"property": "Status", "status": {"equals": "Active"}}}
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
                        recruiters[name] = page["id"]
            return recruiters
        return {"Adam": "", "Jason": "", "Martin": "", "Lucas": ""}
    except:
        return {"Adam": "", "Jason": "", "Martin": "", "Lucas": ""}

recruiter_dict = get_active_recruiters()
recruiter_options = list(recruiter_dict.keys())

with st.form("driver_form", clear_on_submit=True):
    
    st.markdown("### 🔀 Ma'lumot qayerga yuborilsin?")
    # REJIUM TANLASH
    destination = st.radio(
        "Tizimni tanlang:",
        ("Public Channel (Ommaviy kanal - Rasm blur qilinadi)", 
         "Internal Channel (Shaxsiy kanal - Asl nusxa + Barcha hujjatlar)", 
         "Database Only (Faqat Notion CRM)")
    )
    st.divider()

    st.subheader("👤 Haydovchi Ma'lumotlari")
    driver_name = st.text_input("Haydovchining Ismi va Familiyasi*")
    phone_number = st.text_input("Telefon Raqami*")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # NOTION UCHUN TO'G'RILANGAN NARXLAR
        driver_type = st.selectbox("Haydovchi Turi", ["Solo ($500-$600)", "Team ($1100-$1200)", "Owner-Operator ($1100-$1200)"])
    with col_b:
        selected_recruiter = st.selectbox("Sizning Ismingiz (Agent)*", recruiter_options)

    st.divider()

    st.subheader("📊 Sotuv va OTR Ma'lumotlari")
    col1, col2, col3 = st.columns(3)
    with col1:
        experience = st.number_input("Tajribasi (Yil)", min_value=0, max_value=50, value=2)
    with col2:
        weekly_miles = st.text_input("Haftalik mili", value="3000+ miles")
    with col3:
        eld_type = st.selectbox("ELD Turi", ["Friendly", "Strict", "No ELD"])
        
    col4, col5 = st.columns(2)
    with col4:
        work_time = st.text_input("Ishlash vaqti (Work Time)", value="3 weeks out")
        pay_rate = st.text_input("To'lov (Pay Rate)", placeholder="Masalan: 25% yoki 65 CPM")
        location = st.text_input("Joylashuvi (Location)", placeholder="Masalan: Chicago, IL")
    with col5:
        home_time = st.text_input("Uydagi vaqti (Home Time)", value="3-4 days")
        escrow = st.selectbox("Escrow", ["Yes", "No", "Negotiable"])
        loads = st.text_input("Yuklar turi (Loads)", placeholder="Amazon, FedEx, Dry Van")
        
    ready_date = st.text_input("Tayyor bo'lish vaqti (Ready Date)", value="ASAP")
    notes = st.text_area("Qo'shimcha izoh (Note)")
    
    st.divider()

    st.subheader("📎 Hujjatlarni Yuklash")
    
    # ASOSIY RASM HAMMA REJIM UCHUN
    cdl_front = st.file_uploader("CDL Oldi (Asosiy Nusxa)*", type=["png", "jpg", "jpeg"])
    
    cdl_back = None
    medical_card = None
    
    # AGAR PUBLIC BO'LMASA, QO'SHIMCHA RASMLAR OCHILADI
    if destination != "Public Channel (Ommaviy kanal - Rasm blur qilinadi)":
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cdl_back = st.file_uploader("CDL Orqa tarafi (Ixtiyoriy)", type=["png", "jpg", "jpeg"])
        with col_f2:
            medical_card = st.file_uploader("Medical Card (Ixtiyoriy)", type=["png", "jpg", "jpeg"])

    submit_button = st.form_submit_button(label="Tizimga Yuklash 🚀")

if submit_button:
    if not driver_name or not phone_number or not cdl_front:
        st.error("❌ Iltimos, barcha majburiy (*) maydonlarni to'ldiring!")
    else:
        recruiter_id = recruiter_dict.get(selected_recruiter, "")
        
        # NOTION PIPELINE
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
        
        if notion_response.status_code in [200, 201]:
            st.success(f"✅ {driver_name} ma'lumotlari Notion bazasiga yuklandi!")
            
            # N8N WEBHOOK (PRODUCTION URL - TEST EMAS!)
            webhook_url = "https://recruiting909.app.n8n.cloud/webhook/b2efcc0b-1001-4936-8847-9a626d3dfe70"
            
            files = {}
            # N8N TUSHUNISHI UCHUN "cdl_file" NOMI BILAN YUBORAMIZ
            if cdl_front:
                files["cdl_file"] = (cdl_front.name, cdl_front.getvalue(), cdl_front.type)
            if cdl_back:
                files["cdl_back"] = (cdl_back.name, cdl_back.getvalue(), cdl_back.type)
            if medical_card:
                files["medical_card"] = (medical_card.name, medical_card.getvalue(), medical_card.type)
            
            data = {
                "routing": destination,
                "driver_name": driver_name,
                "driver_type": driver_type,
                "experience": experience,
                "weekly_miles": weekly_miles,
                "eld_type": eld_type,
                "work_time": work_time,
                "home_time": home_time,
                "pay_rate": pay_rate,
                "escrow": escrow,
                "loads": loads,
                "location": location,
                "ready_date": ready_date,
                "recruiter": selected_recruiter,
                "notes": notes
            }
            
            try:
                n8n_response = requests.post(webhook_url, data=data, files=files)
                if n8n_response.status_code == 200:
                    st.info(f"🚀 Ma'lumotlar n8n markaziga ({destination.split()[0]}) muvaffaqiyatli yetib bordi!")
                else:
                    st.warning(f"⚠️ n8n serveri xatosi: {n8n_response.text}")
            except Exception as e:
                st.error(f"❌ n8n aloqa uzildi: {e}")
        else:
            st.error(f"❌ Notion API xatosi: {notion_response.status_code}")
