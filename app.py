import streamlit as st
import requests

st.set_page_config(page_title="909 RA | Recruitment Portal", page_icon="🚛", layout="centered")

st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; padding: 10px; background-color: #0b1f3f; color: white;}
</style>
""", unsafe_allow_html=True)

st.title("🚛 909 Recruiting Agency | HR Portal")
st.markdown("---")

# ==========================================
# 🧠 NOTION API INTEGRATSIYASI (TEAM LEADS)
# ==========================================
@st.cache_data(ttl=300)  # Har 5 daqiqada Notion'dan yangilab turadi, app qotmaydi
def get_active_agents():
    # Streamlit Secrets'dan kalitlarni olamiz
    NOTION_TOKEN = st.secrets.get("NOTION_TOKEN", "")
    DATABASE_ID = st.secrets.get("TEAM_LEADS_DB_ID", "")
    
    if not NOTION_TOKEN or not DATABASE_ID:
        return ["⚠️ Setup Notion Secrets", "Other (Type manually)"]

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.post(url, headers=headers, json={})
        if res.status_code != 200:
            return ["⚠️ Notion API Error", "Other (Type manually)"]
        
        data = res.json()
        agents = []
        
        for row in data.get("results", []):
            props = row.get("properties", {})
            try:
                # Ismni ajratib olish (Ustun nomi Notion'da "Name" bo'lishi shart)
                name_obj = props.get("Name", {}).get("title", [])
                if not name_obj: continue
                name = name_obj[0].get("plain_text", "")

                # Statusni ajratib olish (Ustun nomi Notion'da "Status" bo'lishi shart)
                status_obj = props.get("Status", {})
                if "select" in status_obj and status_obj["select"]:
                    status = status_obj["select"].get("name", "")
                elif "status" in status_obj and status_obj["status"]:
                    status = status_obj["status"].get("name", "")
                else:
                    status = ""

                # Faqat "Active" agentlarni qo'shish
                if status.lower() == "active":
                    agents.append(name)
            except Exception:
                pass
                
        if not agents:
            return ["No Active Agents Found", "Other (Type manually)"]
            
        # Agentlarni alifbo tartibida taxlash
        agents.sort()
        agents.append("Other (Type manually)")
        return agents
    except:
        return ["⚠️ Network Error", "Other (Type manually)"]

# Avtomatik ro'yxatni yuklash
ACTIVE_AGENTS = get_active_agents()

# ==========================================
# BARCHA 48 OTR SHTATLAR RO'YXATI
# ==========================================
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

with st.form("driver_onboarding_form"):
    
    st.subheader("👤 Driver Details")
    driver_name = st.text_input("Driver's Full Name *")
    
    experience_yrs = st.number_input("CDL-A Experience (Years) *", min_value=0, max_value=60, value=2, step=1)
    
    pay_col1, pay_col2 = st.columns(2)
    with pay_col1:
        pay_type = st.selectbox("Pay Structure *", ["CPM", "Percentage (%)", "Flat Weekly ($)"])
    with pay_col2:
        pay_amount = st.number_input("Amount *", min_value=1, max_value=5000, value=65, step=1)
    
    location = st.selectbox("Current Location (State) *", US_STATES)
    
    # DINAMIK: Ready to Start
    ready_choice = st.selectbox("Ready to Start *", ["ASAP", "Within 3 days", "Next week", "Custom (Type manually)"])
    ready_custom = ""
    if ready_choice == "Custom (Type manually)":
        ready_custom = st.text_input("✍️ Type your custom ready date:")
    
    # DINAMIK: Agent (Notion'dan ulanadi)
    agent_choice = st.selectbox("Selling Agent / Recruiter Name *", ACTIVE_AGENTS)
    agent_custom = ""
    if agent_choice == "Other (Type manually)":
        agent_custom = st.text_input("✍️ Type Agent's name:")

    st.markdown("---")

    st.subheader("📊 Operational & Target Setup")
    loads = st.multiselect("Equipment / Loads *", ["Reefer", "Dry Van", "Flatbed", "Step Deck", "Box Truck", "Power Only"])
    weekly_miles = st.number_input("Target Weekly Miles", min_value=1000, max_value=4000, value=2500, step=100)
    
    eld_friendly = st.selectbox("ELD Friendly? *", ["Yes (ELD Friendly)", "Negotiable", "No (Paper logs strictly)"])
    
    op_col1, op_col2 = st.columns(2)
    with op_col1:
        # DINAMIK: Work Time
        work_choice = st.selectbox("Work Time (OTR)", ["2 weeks out", "3 weeks out", "4+ weeks out", "Custom (Type manually)"])
        work_custom = ""
        if work_choice == "Custom (Type manually)":
            work_custom = st.text_input("✍️ Type your custom work time:")
            
    with op_col2:
        # DINAMIK: Home Time
        home_choice = st.selectbox("Home Time Requirements", ["2-3 Days", "4-5 Days", "1 Full Week", "Custom (Type manually)"])
        home_custom = ""
        if home_choice == "Custom (Type manually)":
            home_custom = st.text_input("✍️ Type your custom home time:")
        
    escrow = st.selectbox("Escrow Agreement", ["Agreed (Standard deductions)", "Needs Negotiation", "Refused"])

    st.markdown("---")
    
    st.subheader("📂 Document Uploads & Routing")
    cdl_file = st.file_uploader("Upload CDL (Front) *", type=['png', 'jpg', 'jpeg'])
    cdl_back = st.file_uploader("Upload CDL (Back) *", type=['png', 'jpg', 'jpeg'])
    medical_card = st.file_uploader("Upload Medical Card *", type=['png', 'jpg', 'jpeg'])
    
    routing_destination = st.radio(
        "🎯 Where should this driver be posted?",
        ["🟢 Internal Channel (Contracted Carrier Priority)", "🔵 Public Channel (Open Market)"]
    )
    notes = st.text_area("✍️ Additional Notes (MVR issues, preferred routes, etc.)")

    submitted = st.form_submit_button("🚀 PROCESS DRIVER TO SYSTEM")

if submitted:
    if not driver_name or not cdl_file or not cdl_back or not medical_card:
        st.error("❌ ERROR: Driver's Name and all 3 documents (CDL Front, Back, Medical Card) are mandatory!")
    else:
        with st.spinner("Encrypting and sending to 909 RA Database..."):
            
            # Dinamik maydonlarni tekshirish (Agar "Custom" tanlansa, qo'lda yozilganini oladi)
            final_ready = ready_custom if ready_choice == "Custom (Type manually)" else ready_choice
            final_agent = agent_custom if agent_choice == "Other (Type manually)" else agent_choice
            final_work = work_custom if work_choice == "Custom (Type manually)" else work_choice
            final_home = home_custom if home_choice == "Custom (Type manually)" else home_choice
            
            WEBHOOK_URL = "SIZNING_N8N_WEBHOOK_URL_MANZILINGIZNI_SHU_YERGA_QO'YING"
            
            if pay_type == "CPM":
                formatted_pay = f"{pay_amount} CPM"
            elif pay_type == "Percentage (%)":
                formatted_pay = f"{pay_amount}%"
            else:
                formatted_pay = f"${pay_amount} / Week"
            
            payload = {
                "driver_name": driver_name,
                "experience": f"{experience_yrs} Years",
                "pay_rate": formatted_pay,
                "location": location,
                "ready_date": final_ready,
                "agent": final_agent,
                "loads": ", ".join(loads),
                "weekly_miles": weekly_miles,
                "eld_type": eld_friendly,
                "work_time": final_work,
                "home_time": final_home,
                "escrow": escrow,
                "notes": notes,
                "destination": "Internal" if "Internal" in routing_destination else "Public"
            }
            
            files = {
                "cdl_file": (cdl_file.name, cdl_file, cdl_file.type),
                "cdl_back": (cdl_back.name, cdl_back, cdl_back.type),
                "medical_card": (medical_card.name, medical_card, medical_card.type)
            }
            
            try:
                response = requests.post(WEBHOOK_URL, data=payload, files=files, timeout=10)
                if response.status_code == 200:
                    st.success(f"✅ SUCCESS: {driver_name} has been routed to the {payload['destination']} pipeline.")
                else:
                    st.error(f"⚠️ SYSTEM ERROR: n8n responded with code {response.status_code}.")
            except requests.exceptions.Timeout:
                st.error("⏳ TIMEOUT: n8n server took too long to respond.")
            except Exception as e:
                st.error(f"❌ CONNECTION ERROR: {e}")
