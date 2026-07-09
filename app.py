import streamlit as st
import requests
import json

# ==========================================
# 1. SAHIFA SOZLAMALARI VA DIZAYN
# ==========================================
st.set_page_config(page_title="909 RA | Recruitment Portal", page_icon="🦅", layout="centered")

st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; padding: 10px; background-color: #0b1f3f; color: white;}
</style>
""", unsafe_allow_html=True)

# Tizim sarlavhasi va Sync tugmasi yonma-yon
head_col1, head_col2 = st.columns([0.8, 0.2])
with head_col1:
    st.title("🦅 909 Recruiting Agency | HR Portal")
with head_col2:
    st.write("") # Kichik bo'shliq
    if st.button("🔄 Sync Notion"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ==========================================
# 2. MAXFIY KALITLAR VA NOTION MANTIG'I
# ==========================================
NOTION_TOKEN = st.secrets.get("NOTION_TOKEN", "")
MAIN_DATABASE_ID = st.secrets.get("DATABASE_ID", "")
TEAM_DATABASE_ID = st.secrets.get("TEAM_DATABASE_ID", "")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@st.cache_data(ttl=60)
def get_active_recruiters():
    fallback = {"Adam": "", "Jason": "", "Martin": "", "Lucas": ""}
    if not TEAM_DATABASE_ID or not NOTION_TOKEN:
        return fallback
        
    url = f"https://api.notion.com/v1/databases/{TEAM_DATABASE_ID}/query"
    payload = {"filter": {"property": "Status", "status": {"equals": "Active"}}}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            results = response.json().get("results", [])
            recruiters = {}
            for page in results:
                props = page.get("properties", {})
                
                name_list = props.get("Name", {}).get("title", [])
                if not name_list: continue
                name = name_list[0].get("plain_text", "")
                
                role_obj = props.get("Role", {}).get("select")
                role = role_obj.get("name") if role_obj else ""
                
                if role == "Recruiter":
                    recruiters[name] = page["id"]
                    
            if recruiters:
                return recruiters
        return fallback
    except:
        return fallback

recruiter_dict = get_active_recruiters()
recruiter_options = list(recruiter_dict.keys())
recruiter_options.sort()
recruiter_options.append("Other (Type manually)")

US_STATES = [
    "AL - Alabama", "AR - Arkansas", "AZ - Arizona", "CA - California", "CO - Colorado", "CT - Connecticut", 
    "DE - Delaware", "FL - Florida", "GA - Georgia", "IA - Iowa", "ID - Idaho", "IL - Illinois", 
    "IN - Indiana", "KS - Kansas", "KY - Kentucky", "LA - Louisiana", "MA - Massachusetts", "MD - Maryland", 
    "ME - Maine", "MI - Michigan", "MN - Minnesota", "MO - Missouri", "MS - Mississippi", "MT - Montana", 
    "NC - North Carolina", "ND - North Dakota", "NE - Nebraska", "NH - New Hampshire", "NJ - New Jersey", 
    "NM - New Mexico", "NV - Nevada", "NY - New York", "OH - Ohio", "OK - Oklahoma", "OR - Oregon", 
    "PA - Pennsylvania", "RI - Rhode Island", "SC - South Carolina", "SD - South Dakota", "TN - Tennessee", 
    "TX - Texas", "UT - Utah", "VA - Virginia", "VT - Vermont", "WA - Washington", "WI - Wisconsin", 
    "WV - West Virginia", "WY - Wyoming"
]

st.markdown("### 🔀 Ma'lumot qayerga yuborilsin?")
routing_destination = st.radio(
    "Tizimni tanlang:",
    ("🟢 Internal Channel (Contracted Carrier Priority)", "🔵 Public Channel (Open Market)")
)
st.divider()

# ==========================================
# 3. TELEGRAM ALBOM YUBORISH FUNKSIYASI
# ==========================================
def send_album_to_telegram(driver_data, cdl_front, cdl_back, medical_card, extra_files=None):
    BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
    CHAT_ID = "-1003900612928"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"

    caption = f"""👤 Name: {driver_data.get('driver_name', 'N/A')}
📅 Experience: {driver_data.get('experience', 'N/A')}
📊 Weekly miles: {driver_data.get('weekly_miles', 'N/A')}
📝 ELD: {driver_data.get('eld_type', 'N/A')}
⏰ Work time: {driver_data.get('work_time', 'N/A')}
🏠 Home time: {driver_data.get('home_time', 'N/A')}
💰 Pay: {driver_data.get('pay_rate', 'N/A')}
💵 Escrow: {driver_data.get('escrow', 'N/A')}
🚛 Loads: {driver_data.get('loads', 'N/A')}
📍 Location: {driver_data.get('location', 'N/A')}
🚦 Ready: {driver_data.get('ready_date', 'N/A')}
📞 Agent: {driver_data.get('recruiter_name', 'N/A')}
📝 Note: {driver_data.get('notes', 'N/A')}"""

    media = []
    files = {}

    if cdl_front:
        files["cdl_front"] = (cdl_front.name, cdl_front.getvalue(), "image/jpeg")
        media.append({"type": "photo", "media": "attach://cdl_front"})
        
    if cdl_back:
        files["cdl_back"] = (cdl_back.name, cdl_back.getvalue(), "image/jpeg")
        media.append({"type": "photo", "media": "attach://cdl_back"})
        
    if medical_card:
        files["medical_card"] = (medical_card.name, medical_card.getvalue(), "image/jpeg")
        media.append({"type": "photo", "media": "attach://medical_card"})

    if extra_files:
        for idx, ext_file in enumerate(extra_files):
            file_key = f"extra_{idx}"
            media_type = "document" if ext_file.name.lower().endswith('.pdf') else "photo"
            files[file_key] = (ext_file.name, ext_file.getvalue(), ext_file.type)
            media.append({"type": media_type, "media": f"attach://{file_key}"})

    if media:
        media[0]["caption"] = caption
        # Telegram limiti 10 ta
        if len(media) > 10:
            media = media[:10]

    if media:
        data = {
            "chat_id": CHAT_ID,
            "media": json.dumps(media)
        }
        response = requests.post(url, data=data, files=files)
        return response.json()
    else:
        return {"ok": False, "description": "Hech qanday rasm topilmadi."}

# ==========================================
# 4. MUKAMMAL FORMA 
# ==========================================
with st.form("driver_onboarding_form", clear_on_submit=True):
    
    st.subheader("👤 Driver Details")
    driver_name = st.text_input("Driver's Full Name *")
    phone_number = st.text_input("Phone Number *") 
    
    col_type, col_exp = st.columns(2)
    with col_type:
        driver_type = st.selectbox("Driver Type *", ["Solo ($500-$600)", "Team ($1100-$1200)", "Owner-Operator ($1100-$1200)"]) 
    with col_exp:
        experience_yrs = st.number_input("CDL-A Experience (Years) *", min_value=0, max_value=60, value=2, step=1)
    
    pay_col1, pay_col2 = st.columns(2)
    with pay_col1:
        pay_type = st.selectbox("Pay Structure *", ["CPM", "Percentage (%)", "Flat Weekly ($)"])
    with pay_col2:
        pay_amount = st.number_input("Amount *", min_value=1, max_value=5000, value=65, step=1)
    
    location = st.selectbox("Current Location (State) *", US_STATES)
    
    ready_col1, ready_col2 = st.columns(2)
    with ready_col1:
        ready_choice = st.selectbox("Ready to Start *", ["ASAP", "Within 3 days", "Next week", "Custom"])
    with ready_col2:
        ready_custom = st.text_input("✍️ If Custom, type here:", placeholder="e.g. in 5 days")
    
    agent_col1, agent_col2 = st.columns(2)
    with agent_col1:
        agent_choice = st.selectbox("Selling Agent Name *", recruiter_options)
    with agent_col2:
        agent_custom = st.text_input("✍️ If Other, type Agent name:")

    st.markdown("---")

    st.subheader("📊 Operational & Target Setup")
    loads = st.multiselect("Equipment / Loads *", ["Reefer", "Dry Van", "Flatbed", "Step Deck", "Box Truck", "Power Only"])
    weekly_miles = st.number_input("Target Weekly Miles", min_value=1000, max_value=4000, value=2500, step=100)
    
    eld_friendly = st.selectbox("ELD Friendly? *", ["Yes (ELD Friendly)", "Negotiable", "No (Paper logs strictly)"])
    
    work_col1, work_col2 = st.columns(2)
    with work_col1:
        work_choice = st.selectbox("Work Time (OTR)", ["2 weeks out", "3 weeks out", "4+ weeks out", "Custom"])
    with work_col2:
        work_custom = st.text_input("✍️ If Custom, type work time:", placeholder="e.g. 6 weeks out")
            
    home_col1, home_col2 = st.columns(2)
    with home_col1:
        home_choice = st.selectbox("Home Time Requirements", ["2-3 Days", "4-5 Days", "1 Full Week", "Custom"])
    with home_col2:
        home_custom = st.text_input("✍️ If Custom, type home time:", placeholder="e.g. 10 days")
        
    escrow = st.selectbox("Escrow Agreement", ["Agreed (Standard deductions)", "Needs Negotiation", "Refused"])

    st.markdown("---")
    
    st.subheader("📂 Document Uploads (Dynamic)")
    
    cdl_front = st.file_uploader("Upload CDL (Front) * [Majburiy]", type=['png', 'jpg', 'jpeg', 'pdf'])
    
    doc_col1, doc_col2 = st.columns(2)
    with doc_col1:
        cdl_back = st.file_uploader("Upload CDL (Back) [Ixtiyoriy]", type=['png', 'jpg', 'jpeg', 'pdf'])
    with doc_col2:
        medical_card = st.file_uploader("Upload Medical Card [Ixtiyoriy]", type=['png', 'jpg', 'jpeg', 'pdf'])
        
    extra_files = st.file_uploader("➕ Boshqa qo'shimcha hujjatlar (MVR, SSN, h.k.) [Ixtiyoriy - Cheksiz tanlash mumkin]", type=['png', 'jpg', 'jpeg', 'pdf'], accept_multiple_files=True)
    
    notes = st.text_area("✍️ Additional Notes (MVR issues, preferred routes, etc.)")

    submitted = st.form_submit_button("🚀 PROCESS DRIVER TO SYSTEM")

# ==========================================
# 5. EGIZAK YUBORISH MANTIGI
# ==========================================
if submitted:
    if not driver_name or not phone_number or not cdl_front:
        st.error("❌ ERROR: Driver's Name, Phone Number, and CDL (Front) are mandatory!")
    else:
        with st.spinner("Encrypting and processing data to all channels..."):
            
            final_ready = ready_custom if (ready_choice == "Custom" and ready_custom.strip()) else ready_choice
            final_agent = agent_custom if (agent_choice == "Other (Type manually)" and agent_custom.strip()) else agent_choice
            final_work = work_custom if (work_choice == "Custom" and work_custom.strip()) else work_choice
            final_home = home_custom if (home_choice == "Custom" and home_custom.strip()) else home_choice
            
            if pay_type == "CPM":
                formatted_pay = f"{pay_amount} CPM"
            elif pay_type == "Percentage (%)":
                formatted_pay = f"{pay_amount}%"
            else:
                formatted_pay = f"${pay_amount} / Week"

            # ---------------------------------------------------------
            # BQ-1: TELEGRAMGA ALBOM YUBORISH
            # ---------------------------------------------------------
            driver_data = {
                "driver_name": driver_name,
                "experience": f"{experience_yrs} Years",
                "weekly_miles": weekly_miles,
                "eld_type": eld_friendly,
                "work_time": final_work,
                "home_time": final_home,
                "pay_rate": formatted_pay,
                "escrow": escrow,
                "loads": ", ".join(loads) if loads else "Any",
                "location": location,
                "ready_date": final_ready,
                "recruiter_name": final_agent,
                "notes": notes
            }
            
            tg_response = send_album_to_telegram(driver_data, cdl_front, cdl_back, medical_card, extra_files)
            if tg_response.get("ok"):
                st.success("✅ Telegram kanaliga albom muvaffaqiyatli yuborildi!")
            else:
                st.warning(f"⚠️ Telegram xatosi: {tg_response.get('description')}")

            # ---------------------------------------------------------
            # BQ-2: NOTION MASTER CRM'GA TO'G'RIDAN-TO'G'RI YOZISH
            # ---------------------------------------------------------
            recruiter_id = recruiter_dict.get(agent_choice, "") if agent_choice != "Other (Type manually)" else ""
            
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
                
            try:
                notion_res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=notion_data)
                if notion_res.status_code in [200, 201]:
                    st.success(f"✅ {driver_name} ma'lumotlari Notion CRM'ga muvaffaqiyatli saqlandi!")
                else:
                    st.warning(f"⚠️ Notion API xatosi: {notion_res.status_code} - Iltimos, sozlamalarni tekshiring.")
            except Exception as e:
                st.warning(f"⚠️ Notion bilan ulanishda xato: {e}")

            # ---------------------------------------------------------
            # BQ-3: N8N WEBHOOK
            # ---------------------------------------------------------
            WEBHOOK_URL = "https://recruiting909.app.n8n.cloud/webhook/b2efcc0b-1001-4936-8847-9a626d3dfe70"

            payload = {
                "routing": "Internal Channel" if "Internal" in routing_destination else "Public Channel",
                "driver_name": driver_name,
                "phone_number": phone_number,
                "driver_type": driver_type,
                "experience": f"{experience_yrs} Years",
                "pay_rate": formatted_pay,
                "location": location,
                "ready_date": final_ready,
                "recruiter_name": final_agent, 
                "loads": ", ".join(loads) if loads else "Any",
                "weekly_miles": weekly_miles,
                "eld_type": eld_friendly,
                "work_time": final_work,
                "home_time": final_home,
                "escrow": escrow,
                "notes": notes
            }
            
            files = {}
            files["cdl_file"] = (cdl_front.name, cdl_front.getvalue(), cdl_front.type)
            
            if cdl_back:
                files["cdl_back"] = (cdl_back.name, cdl_back.getvalue(), cdl_back.type)
            if medical_card:
                files["medical_card"] = (medical_card.name, medical_card.getvalue(), medical_card.type)
            
            if extra_files:
                for idx, extra_file in enumerate(extra_files):
                    files[f"extra_doc_{idx+1}"] = (extra_file.name, extra_file.getvalue(), extra_file.type)
            
            try:
                response = requests.post(WEBHOOK_URL, data=payload, files=files, timeout=15)
                if response.status_code == 200:
                    st.info(f"🚀 Ma'lumotlar n8n markaziga muvaffaqiyatli yetib bordi!")
                else:
                    st.error(f"⚠️ n8n tizim xatosi: {response.text}")
            except requests.exceptions.Timeout:
                st.error("⏳ TIMEOUT: n8n server javob bermadi.")
            except Exception as e:
                st.error(f"❌ n8n aloqa uzildi: {e}")
