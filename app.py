import streamlit as st
import requests

# Sahifa sozlamalari
st.set_page_config(page_title="909 RA | Recruitment Portal", page_icon="🚛", layout="centered")

# CSS Dizayn
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; padding: 10px; background-color: #0b1f3f; color: white;}
</style>
""", unsafe_allow_html=True)

st.title("🚛 909 Recruiting Agency — Driver Entry Portal")

# Maxfiy kalitlar
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
MAIN_DATABASE_ID = st.secrets["DATABASE_ID"]
TEAM_DATABASE_ID = st.secrets.get("TEAM_DATABASE_ID", "")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Notion'dan Recruiter'larni tortish
@st.cache_data(ttl=60)
def get_active_recruiters():
    if not TEAM_DATABASE_ID: return {"Adam": "", "Jason": "", "Martin": "", "Lucas": ""}
    url = f"https://api.notion.com/v1/databases/{TEAM_DATABASE_ID}/query"
    payload = {"filter": {"property": "Status", "status": {"equals": "Active"}}}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            results = response.json().get("results", [])
            recruiters = {page["properties"]["Name"]["title"][0]["plain_text"]: page["id"] 
                          for page in results if page["properties"]["Role"]["select"]["name"] == "Recruiter"}
            return recruiters
        return {"Adam": "", "Jason": "", "Lucas": ""}
    except: return {"Adam": "", "Jason": "", "Lucas": ""}

recruiter_dict = get_active_recruiters()
recruiter_options = sorted(list(recruiter_dict.keys())) + ["Other (Type manually)"]

# Forma
with st.form("driver_form", clear_on_submit=True):
    st.subheader("👤 Driver Details")
    driver_name = st.text_input("Driver's Full Name *")
    phone = st.text_input("Phone Number *")
    
    col1, col2 = st.columns(2)
    with col1:
        driver_type = st.selectbox("Driver Type", ["Solo ($500-$600)", "Team ($1100-$1200)", "Owner-Operator ($1100-$1200)"])
    with col2:
        recruiter = st.selectbox("Selling Agent / Recruiter *", recruiter_options)
        
    experience = st.number_input("Experience (Years)", min_value=0, max_value=50, value=2)
    miles = st.text_input("Weekly Miles", value="3000+ miles")
    
    col3, col4 = st.columns(2)
    with col3:
        eld = st.selectbox("ELD Experience", ["Yes (ELD Friendly)", "Negotiable", "No (Paper logs)"])
        work_time = st.text_input("Work Time (OTR)", value="3 weeks out")
    with col4:
        home_time = st.text_input("Home Time", value="3-4 days")
        pay = st.text_input("Pay Structure", placeholder="e.g. 65 CPM or 30%")
        
    escrow = st.selectbox("Escrow", ["Agreed", "Needs Negotiation", "Refused"])
    location = st.text_input("Location (State)")
    ready = st.text_input("Ready Date", value="ASAP")
    notes = st.text_area("Additional Notes")

    st.subheader("📎 Document Uploads")
    cdl_front = st.file_uploader("CDL Front *", type=["png", "jpg", "jpeg", "pdf"])
    cdl_back = st.file_uploader("CDL Back (Optional)", type=["png", "jpg", "jpeg", "pdf"])
    med_card = st.file_uploader("Medical Card (Optional)", type=["png", "jpg", "jpeg", "pdf"])
    extra = st.file_uploader("Extra Docs (Optional - Multiple)", accept_multiple_files=True)

    submitted = st.form_submit_button("🚀 PROCESS DRIVER")

if submitted:
    if not driver_name or not phone or not cdl_front:
        st.error("❌ Driver Name, Phone, and CDL Front are mandatory!")
    else:
        # Notionga yozish
        notion_payload = {
            "parent": {"database_id": MAIN_DATABASE_ID},
            "properties": {
                "Driver Name": {"title": [{"text": {"content": driver_name}}]},
                "Phone Number": {"phone_number": phone},
                "Driver Type": {"select": {"name": driver_type}},
                "Status": {"status": {"name": "Lead"}}
            }
        }
        if recruiter in recruiter_dict:
            notion_payload["properties"]["Recruiter"] = {"relation": [{"id": recruiter_dict[recruiter]}]}
        requests.post("https://api.notion.com/v1/pages", headers=headers, json=notion_payload)
        
        # n8n'ga yuborish
        webhook_url = "https://recruiting909.app.n8n.cloud/webhook/b2efcc0b-1001-4936-8847-9a626d3dfe70"
        files = {"cdl_file": (cdl_front.name, cdl_front.getvalue(), cdl_front.type)}
        if cdl_back: files["cdl_back"] = (cdl_back.name, cdl_back.getvalue(), cdl_back.type)
        if med_card: files["med_card"] = (med_card.name, med_card.getvalue(), med_card.type)
        if extra:
            for idx, f in enumerate(extra):
                files[f"extra_{idx}"] = (f.name, f.getvalue(), f.type)
        
        requests.post(webhook_url, data={"driver_name": driver_name, "recruiter_name": recruiter}, files=files)
        st.success("✅ Driver processed successfully!")
