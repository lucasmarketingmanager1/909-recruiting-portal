import streamlit as st
import requests

# ==========================================
# 1. SAHIFA SOZLAMALARI VA DIZAYN (UI/UX)
# ==========================================
st.set_page_config(page_title="909 RA | Recruitment Portal", page_icon="🚛", layout="wide")

st.markdown("""
<style>
    /* Clean and Professional UI */
    .stApp { background-color: #f4f6f9; }
    .stButton>button { width: 100%; background-color: #0b1f3f; color: white; border-radius: 5px; font-weight: bold; }
    .stButton>button:hover { background-color: #1d3c6a; color: white; }
    h1, h2, h3, h4 { color: #0b1f3f; }
    .st-bx { background-color: white; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

st.title("🚛 909 Recruiting Agency | Dispatch & HR Portal")
st.markdown("---")

# ==========================================
# 2. BARCHA 48 OTR SHTATLAR RO'YXATI
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

# ==========================================
# 3. FORM ARXITEKTURASI (ZERO-LAG)
# ==========================================
with st.form("driver_onboarding_form"):
    
    col1, col2 = st.columns(2)
    
    # CHAP TOMON: Shaxsiy va To'lov ma'lumotlari
    with col1:
        st.subheader("👤 Driver Details")
        driver_name = st.text_input("Driver's Full Name *")
        experience = st.selectbox("CDL-A Experience *", ["Under 1 year", "1 Year", "2 Years", "3 Years", "4 Years", "5+ Years"])
        
        # Aqlli to'lov tizimi (Pay Structure)
        pay_col1, pay_col2 = st.columns(2)
        with pay_col1:
            pay_type = st.selectbox("Pay Structure *", ["CPM", "Percentage (%)", "Flat Weekly ($)"])
        with pay_col2:
            pay_amount = st.number_input("Amount *", min_value=1, max_value=5000, value=65, step=1)
        
        location = st.selectbox("Current Location (State) *", US_STATES, help="Type to search states.")
        ready_date = st.selectbox("Ready to Start *", ["ASAP", "Within 3 days", "Next week", "Needs 2+ weeks notice"])
        agent = st.text_input("Selling Agent / Recruiter Name *")

    # O'NG TOMON: Operatsion ma'lumotlar
    with col2:
        st.subheader("📊 Operational & Target Setup")
        loads = st.multiselect("Equipment / Loads *", ["Reefer", "Dry Van", "Flatbed", "Step Deck", "Box Truck", "Power Only"])
        weekly_miles = st.number_input("Target Weekly Miles", min_value=1000, max_value=4000, value=2500, step=100)
        eld_type = st.selectbox("ELD Experience", ["Motive (KeepTruckin)", "Samsara", "Garmin", "OmniTracs", "Other"])
        work_time = st.selectbox("Work Time (OTR)", ["2 weeks out", "3 weeks out", "4+ weeks out", "No touch freight strictly"])
        home_time = st.selectbox("Home Time Requirements", ["2-3 Days", "4-5 Days", "1 Full Week"])
        escrow = st.selectbox("Escrow Agreement", ["Agreed (Standard deductions)", "Needs Negotiation", "Refused"])

    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    # HUJJATLARNI YUKLASH
    with col3:
        st.subheader("📂 Document Uploads")
        cdl_file = st.file_uploader("Upload CDL (Front) *", type=['png', 'jpg', 'jpeg'])
        cdl_back = st.file_uploader("Upload CDL (Back) *", type=['png', 'jpg', 'jpeg'])
        medical_card = st.file_uploader("Upload Medical Card *", type=['png', 'jpg', 'jpeg'])
        
    # ROUTING VA QO'SHIMCHA MA'LUMOT
    with col4:
        st.subheader("🎯 Routing & Notes")
        routing_destination = st.radio(
            "Where should this driver be posted?",
            ["🟢 Internal Channel (Contracted Carrier Priority)", "🔵 Public Channel (Open Market)"]
        )
        notes = st.text_area("Additional Notes (MVR issues, preferred routes, etc.)")

    # YUBORISH TUGMASI
    submitted = st.form_submit_button("🚀 PROCESS DRIVER TO SYSTEM")

# ==========================================
# 4. N8N WEBHOOK'GA YUBORISH MANTIQI
# ==========================================
if submitted:
    # Majburiy maydonlarni tekshirish
    if not driver_name or not cdl_file or not cdl_back or not medical_card:
        st.error("❌ ERROR: Driver's Name and all 3 documents (CDL Front, Back, Medical Card) are mandatory!")
    else:
        with st.spinner("Encrypting and sending to 909 RA Database..."):
            
            # DIQQAT: O'zingizning n8n Webhook URL manzilingizni qo'ying
            WEBHOOK_URL = "SIZNING_N8N_WEBHOOK_URL_MANZILINGIZNI_SHU_YERGA_QO'YING"
            
            # To'lov formatini aqlli shakllantirish
            if pay_type == "CPM":
                formatted_pay = f"{pay_amount} CPM"
            elif pay_type == "Percentage (%)":
                formatted_pay = f"{pay_amount}%"
            else:
                formatted_pay = f"${pay_amount} / Week"
            
            # n8n ga ketadigan matnli ma'lumotlar
            payload = {
                "driver_name": driver_name,
                "experience": experience,
                "pay_rate": formatted_pay,
                "location": location,
                "ready_date": ready_date,
                "agent": agent,
                "loads": ", ".join(loads),
                "weekly_miles": weekly_miles,
                "eld_type": eld_type,
                "work_time": work_time,
                "home_time": home_time,
                "escrow": escrow,
                "notes": notes,
                "destination": "Internal" if "Internal" in routing_destination else "Public"
            }
            
            # n8n ga ketadigan fayllar (Binary)
            files = {
                "cdl_file": (cdl_file.name, cdl_file, cdl_file.type),
                "cdl_back": (cdl_back.name, cdl_back, cdl_back.type),
                "medical_card": (medical_card.name, medical_card, medical_card.type)
            }
            
            try:
                # timeout=10 ilovani qotib qolishdan asraydi
                response = requests.post(WEBHOOK_URL, data=payload, files=files, timeout=10)
                
                if response.status_code == 200:
                    st.success(f"✅ SUCCESS: {driver_name} has been routed to the {payload['destination']} pipeline.")
                else:
                    st.error(f"⚠️ SYSTEM ERROR: n8n responded with code {response.status_code}. Check backend.")
            except requests.exceptions.Timeout:
                st.error("⏳ TIMEOUT: n8n server took too long to respond. The system is protected from freezing. Try again.")
            except Exception as e:
                st.error(f"❌ CONNECTION ERROR: {e}")
