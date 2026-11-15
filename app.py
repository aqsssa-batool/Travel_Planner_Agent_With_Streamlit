"""PlanSpark - AI-powered travel planner dashboard."""
import os
import streamlit as st
from dotenv import load_dotenv
from agents import orchestrate_trip_planning, get_weather, convert_currency

load_dotenv()
st.set_page_config(page_title="PlanSpark | AI Travel Planner", page_icon="✈️", layout="wide")

# ------------------------------- STYLE ---------------------------------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&family=Outfit:wght@500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');
:root { --ink:#24243d; --muted:#646984; --purple:#8065ed; --purple-dark:#6549d8; --line:#deddf0; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif !important; color:var(--ink) !important; }
.stApp { background:linear-gradient(125deg,#d4d8ff 0%,#e8e9ff 24%,#f7f6ff 24%,#fbfbff 100%) !important; }
[data-testid="stHeader"] { background:transparent !important; }
.block-container { max-width:1600px; padding-top:1rem; padding-bottom:2rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#edfff1 0%,#f7f8ff 55%,#efedff 100%) !important; border-right:1px solid #d8d9eb; }
[data-testid="stSidebar"] > div { padding-top:1rem; }
.sidebar-brand { display:flex; align-items:center; gap:10px; padding:4px 10px 16px; margin-bottom:4px; }
.sidebar-plane { font-size:2.05rem; line-height:1; color:#7459e8 !important; }
.sidebar-brand-name { font-family:'Outfit',sans-serif; font-size:1.45rem; font-weight:800; letter-spacing:-.5px; color:#24243d !important; }
.page-brand { font-family:'Playfair Display',serif; font-size:2.35rem; font-weight:800; letter-spacing:-.8px; color:#252540 !important; margin:0 0 .2rem; }
.page-brand span { color:#7659e8 !important; }
.tagline { color:#646984 !important; font-size:.95rem; margin-bottom:1.25rem; }
.hero { background:#fff; border:1px solid #e5e4f2; border-radius:26px; padding:28px 30px 25px; box-shadow:0 14px 38px rgba(65,62,125,.08); min-height:260px; }
.hero-kicker { color:#33265f !important; font-size:.76rem; font-weight:800; letter-spacing:1.8px; text-transform:uppercase; }
.hero h1 { font-family:'Playfair Display',serif; font-size:2.8rem; font-weight:800; color:#22233b !important; margin:.5rem 0; letter-spacing:-1.1px; }
.hero p { color:#5e6480 !important; font-size:1.02rem; }
.pill { display:inline-block; padding:7px 13px; border-radius:30px; background:#f0edff; border:1px solid #dfd9ff; color:#292344 !important; margin:7px 5px 0 0; font-size:.78rem; }
.panel { background:#fff; border:1px solid #e6e4f2; border-radius:20px; padding:15px; margin:0 0 12px; box-shadow:0 9px 25px rgba(65,62,125,.06); }
.panel-title { color:#252640 !important; font-weight:800; font-size:1.02rem; }
.panel-sub { color:#69708a !important; font-size:.78rem; margin-top:3px; }
.destination-card { background:#fff; border:1px solid #e5e3f1; border-radius:16px; overflow:hidden; margin-bottom:10px; }
.destination-card img { width:100%; height:112px; object-fit:cover; display:block; }
.destination-card .copy { padding:9px 10px; }
.destination-card b { color:#252640 !important; font-size:.88rem; }
.destination-card small { color:#6c7189 !important; display:block; margin-top:2px; font-size:.73rem; }

/* Readable labels, inputs, dropdowns and success messages */
.stApp label, .stApp [data-testid="stWidgetLabel"], .stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stRadio"] label {
 color:#30334f !important; opacity:1 !important;
}
.stApp input, .stApp textarea, .stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea {
 background:#fff !important; color:#24243d !important; -webkit-text-fill-color:#24243d !important;
 border:1px solid #d7d6eb !important; border-radius:11px !important; caret-color:#7459e8 !important;
}
.stApp input::placeholder, .stApp textarea::placeholder { color:#898da4 !important; -webkit-text-fill-color:#898da4 !important; opacity:1 !important; }
.stApp [data-baseweb="select"] > div { background:#fff !important; color:#24243d !important; border:1px solid #d7d6eb !important; border-radius:11px !important; }
.stApp [data-baseweb="select"] * { color:#24243d !important; }
.stApp [data-baseweb="popover"], .stApp [role="listbox"], .stApp [role="option"] { background:#fff !important; color:#24243d !important; }
.stApp [data-testid="stNumberInput"] button { background:#eeeaff !important; color:#5844b2 !important; border:1px solid #dcd5ff !important; }
.stApp [data-testid="stForm"] { background:linear-gradient(135deg,#eeeaff 0%,#f7f3ff 52%,#e9f3ff 100%) !important; border:1px solid #d8cffb !important; border-radius:22px; padding:20px; box-shadow:0 10px 28px rgba(105,83,190,.10); }
.stApp [data-testid="stMetric"] { background:#f3f1ff !important; border:1px solid #e2ddff !important; border-radius:14px; padding:10px; }
.stApp [data-testid="stMetricLabel"], .stApp [data-testid="stMetricValue"] { color:#292943 !important; }
.stApp [data-testid="stAlert"],
.stApp [data-testid="stNotification"],
.stApp div[role="alert"] {
 background:#35245f !important; color:#ffffff !important;
 border:1px solid #59418e !important; border-radius:13px !important;
}
.stApp [data-testid="stAlert"] *,
.stApp [data-testid="stNotification"] *,
.stApp div[role="alert"] *,
.stApp [data-testid="stAlert"] p,
.stApp [data-testid="stNotification"] p {
 color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; opacity:1 !important;
}
.stApp [data-testid="stAlert"] svg,
.stApp [data-testid="stNotification"] svg,
.stApp div[role="alert"] svg { fill:#ffffff !important; color:#ffffff !important; }
.weather-heading { display:flex; align-items:center; gap:8px; color:#292044 !important; font-size:1.12rem; font-weight:800; margin:.25rem 0 .6rem; }
.weather-heading .weather-icon { font-size:1.45rem; filter:saturate(1.35); }
.stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
 background:linear-gradient(100deg,#927df4,#aa96ff) !important; color:#242044 !important;
 border:1px solid #9b88f3 !important; border-radius:12px !important; font-weight:800 !important; min-height:2.55rem;
}
.stButton>button *, .stFormSubmitButton>button *, .stDownloadButton>button *,
.stButton>button p, .stFormSubmitButton>button p, .stDownloadButton>button p {
 color:#242044 !important; font-weight:800 !important; -webkit-text-fill-color:#242044 !important;
}
.stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
 background:linear-gradient(100deg,#8067ed,#9c84fa) !important; color:#fff !important;
}
/* Sidebar navigation: dark option tiles with high-contrast white text. */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap:7px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
 background:#30284f !important; border:1px solid #493d70 !important;
 border-radius:11px !important; padding:8px 10px !important;
 color:#ffffff !important; opacity:1 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label p,
[data-testid="stSidebar"] [data-testid="stRadio"] label span,
[data-testid="stSidebar"] [data-testid="stRadio"] label div,
[data-testid="stSidebar"] [data-testid="stRadio"] label * {
 color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;
 font-weight:600 !important; opacity:1 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
 background:linear-gradient(100deg,#765be5,#947cf4) !important;
 border-color:#b8aaff !important;
}
hr { border-color:#e3e1f0 !important; }
h1,h2,h3 { color:#252640 !important; font-family:'Playfair Display','Outfit',serif !important; font-weight:800 !important; letter-spacing:-.35px; }
.hero h1 { font-family:'Playfair Display',serif !important; font-weight:800 !important; }
.stApp [data-testid="stForm"] label, .stApp [data-testid="stForm"] [data-testid="stWidgetLabel"] { color:#30265c !important; font-weight:700 !important; }

/* High-contrast styling for every AI-generated itinerary and Markdown table. */
.stApp [data-testid="stMarkdownContainer"] h1,
.stApp [data-testid="stMarkdownContainer"] h2,
.stApp [data-testid="stMarkdownContainer"] h3,
.stApp [data-testid="stMarkdownContainer"] h4,
.stApp [data-testid="stMarkdownContainer"] h5,
.stApp [data-testid="stMarkdownContainer"] h6 {
 color:#24183f !important; -webkit-text-fill-color:#24183f !important;
 font-family:'Playfair Display','Outfit',serif !important; font-weight:800 !important;
}
.stApp [data-testid="stMarkdownContainer"] table {
 width:100% !important; border-collapse:collapse !important;
 border:1px solid #c9bdf0 !important; border-radius:12px !important;
 overflow:hidden !important; background:#ffffff !important;
 color:#28213f !important;
}
.stApp [data-testid="stMarkdownContainer"] thead,
.stApp [data-testid="stMarkdownContainer"] table th {
 background:#493078 !important; color:#ffffff !important;
 -webkit-text-fill-color:#ffffff !important; font-weight:800 !important;
 text-align:left !important; border:1px solid #7056a6 !important;
 padding:12px 14px !important;
}
.stApp [data-testid="stMarkdownContainer"] table td {
 background:#ffffff !important; color:#29243e !important;
 -webkit-text-fill-color:#29243e !important; opacity:1 !important;
 border:1px solid #d9d1eb !important; padding:12px 14px !important;
 vertical-align:top !important; line-height:1.65 !important;
}
.stApp [data-testid="stMarkdownContainer"] table tbody tr:nth-child(even) td {
 background:#f3efff !important;
}
.stApp [data-testid="stMarkdownContainer"] table td *,
.stApp [data-testid="stMarkdownContainer"] table th *,
.stApp [data-testid="stMarkdownContainer"] table strong,
.stApp [data-testid="stMarkdownContainer"] table b {
 color:inherit !important; -webkit-text-fill-color:inherit !important; opacity:1 !important;
}
.stApp [data-testid="stMarkdownContainer"] blockquote {
 background:#f1edff !important; border-left:5px solid #765be5 !important;
 color:#29243e !important; padding:12px 16px !important; border-radius:8px !important;
}
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] strong,
.stApp [data-testid="stMarkdownContainer"] em {
 color:#29243e !important; -webkit-text-fill-color:#29243e !important; opacity:1 !important;
}
.stApp [data-testid="stMarkdownContainer"] a { color:#5535b5 !important; font-weight:700 !important; }
.stApp [data-testid="stMarkdownContainer"] code {
 background:#eee9ff !important; color:#302052 !important;
}

/* FINAL OVERRIDE: enforce readable colors on AI-generated plans, including
   Markdown tables and any inline spans returned by the model. */
.stApp table,
.stApp [data-testid="stMarkdownContainer"] table,
.stApp [data-testid="stMarkdown"] table {
  width:100% !important; border-collapse:collapse !important;
  background:#ffffff !important; color:#29243e !important;
  border:1px solid #c9bdf0 !important;
}
.stApp table thead,
.stApp table thead tr,
.stApp table th,
.stApp [data-testid="stMarkdownContainer"] table th,
.stApp [data-testid="stMarkdown"] table th {
  background:#493078 !important; background-color:#493078 !important;
  color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;
  font-weight:800 !important; text-align:left !important;
  border:1px solid #7056a6 !important; padding:12px 14px !important;
}
.stApp table tbody tr,
.stApp table td,
.stApp [data-testid="stMarkdownContainer"] table td,
.stApp [data-testid="stMarkdown"] table td {
  background:#ffffff !important; background-color:#ffffff !important;
  color:#29243e !important; -webkit-text-fill-color:#29243e !important;
  opacity:1 !important; border:1px solid #d9d1eb !important;
  padding:12px 14px !important; vertical-align:top !important;
  line-height:1.65 !important;
}
.stApp table tbody tr:nth-child(even) td,
.stApp [data-testid="stMarkdownContainer"] table tbody tr:nth-child(even) td,
.stApp [data-testid="stMarkdown"] table tbody tr:nth-child(even) td {
  background:#f3efff !important; background-color:#f3efff !important;
}
.stApp table th *, .stApp table td *,
.stApp [data-testid="stMarkdownContainer"] table th *,
.stApp [data-testid="stMarkdownContainer"] table td *,
.stApp [data-testid="stMarkdown"] table th *,
.stApp [data-testid="stMarkdown"] table td * {
  color:inherit !important; -webkit-text-fill-color:inherit !important;
  opacity:1 !important;
}
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stMarkdown"] p,
.stApp [data-testid="stMarkdown"] li {
  color:#29243e !important; -webkit-text-fill-color:#29243e !important;
  opacity:1 !important;
}

/* Strong contrast for success/status banners across Streamlit versions. */
.stApp [data-testid="stAlert"],
.stApp [data-testid="stAlert"] > div,
.stApp [data-baseweb="notification"],
.stApp [role="alert"],
.stApp [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
  background:#35245f !important;
  background-color:#35245f !important;
  color:#ffffff !important;
  border-color:#59418e !important;
}
.stApp [data-testid="stAlert"] *,
.stApp [data-baseweb="notification"] *,
.stApp [role="alert"] *,
.stApp [data-testid="stAlert"] p,
.stApp [data-testid="stAlert"] span,
.stApp [data-testid="stAlert"] div {
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  opacity:1 !important;
}

/* Keep the AI settings expander light instead of Streamlit's dark header. */
[data-testid="stSidebar"] [data-testid="stExpander"] details,
[data-testid="stSidebar"] [data-testid="stExpander"] details > summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
 background:#f1efff !important; color:#292744 !important;
 border:1px solid #ddd8f4 !important; border-radius:12px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary *,
[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
[data-testid="stSidebar"] [data-testid="stExpander"] summary span {
 color:#292744 !important; -webkit-text-fill-color:#292744 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stSidebar"] [data-testid="stExpander"] .streamlit-expanderContent {
 background:#fbfaff !important; color:#292744 !important;
 border:1px solid #e4e0f4 !important; border-top:0 !important;
 border-radius:0 0 12px 12px !important;
}
.muted { color:#69708a !important; font-size:.78rem; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- SESSION STATE ----------------------------
defaults = {
    "destination": "", "duration_days": 3, "num_people": 1, "currency": "PKR",
    "total_budget": 0.0, "travel_style": "Comfort / Mid-Range", "interests": "",
    "weather_result": None, "currency_result": None, "last_trip_result": None,
    "last_trip_destination": "", "last_trip_details": {},
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ------------------------------ SIDEBAR --------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><span class="sidebar-plane">✈️</span><span class="sidebar-brand-name">PlanSpark</span></div>', unsafe_allow_html=True)
    nav_options = ["✦  New Chat", "♧  My Trips", "⌕  Explore", "✧  Inspiration"]
    # Reset an old saved navigation value after removing Saved and Community.
    if st.session_state.get("navigation") not in nav_options:
        st.session_state["navigation"] = nav_options[0]
    nav = st.radio(
        "Navigation",
        nav_options,
        label_visibility="collapsed",
        key="navigation",
    )
    st.divider()
    with st.expander("⚙️  AI settings", expanded=False):
        api_key = st.text_input("Groq API key", value=os.getenv("GROQ_API_KEY", ""), type="password")
        model = st.selectbox("Model", ["openai/gpt-oss-120b", "openai/gpt-oss-20b"], index=0)

    st.markdown('<div class="weather-heading"><span class="weather-icon">🌤️</span><span>Live weather</span></div>', unsafe_allow_html=True)
    weather_city = st.text_input("City", placeholder="Search a city", key="weather_city")
    if st.button("Check weather", use_container_width=True, key="weather_btn"):
        if not weather_city.strip():
            st.warning("Please enter a city.")
        else:
            with st.spinner("Checking current weather..."):
                st.session_state.weather_result = get_weather(weather_city.strip())
    weather = st.session_state.weather_result
    if weather:
        if weather.get("error"):
            st.error(weather["error"])
        else:
            st.markdown(f"**{weather.get('city', weather_city)}** · {weather.get('condition','')}")
            st.metric("Temperature", f"{weather.get('current_temp_c','—')} °C")
            a, b = st.columns(2)
            a.metric("Humidity", f"{weather.get('humidity_percent','—')}%")
            b.metric("Wind", f"{weather.get('wind_speed_kmh','—')} km/h")
            st.caption(f"Today: {weather.get('forecast_low_c','—')}° to {weather.get('forecast_high_c','—')}°C")
            if weather.get("rain_chance_percent") is not None:
                st.caption(f"Rain chance: {weather.get('rain_chance_percent')}%")
            st.caption(f"Source: {weather.get('source','live data')}")

    st.divider()
    st.markdown("### 💱 Currency converter")
    fx_options = ["PKR", "USD", "EUR", "GBP", "AED", "SAR", "JPY", "CAD", "AUD", "INR", "CHF", "CNY"]
    amount = st.number_input("Amount", min_value=0.0, value=100.0, step=10.0, key="fx_amount")
    c1, c2 = st.columns(2)
    with c1:
        from_ccy = st.selectbox("From", fx_options, index=1, key="fx_from")
    with c2:
        to_ccy = st.selectbox("To", fx_options, index=0, key="fx_to")
    if st.button("Convert currency", use_container_width=True, key="fx_btn"):
        with st.spinner("Getting exchange rate..."):
            st.session_state.currency_result = convert_currency(amount, to_ccy, from_ccy)
    fx = st.session_state.currency_result
    if fx:
        if fx.get("error"):
            st.error(fx["error"])
        else:
            st.metric("Converted amount", f"{fx['to_currency']} {fx['converted_amount']:,.2f}")
            st.caption(fx.get("exchange_rate", "Rate information unavailable"))
            st.caption(f"Updated: {fx.get('timestamp','Not supplied by provider')}")

    st.divider()
    st.caption("✈️ Discover more. Travel better.")

# ------------------------------- HELPERS --------------------------------
suggestions = [
    ("Bali, Indonesia", "Island escapes · Beaches", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=700&auto=format&fit=crop&q=85"),
    ("London, UK", "Culture · City adventures", "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=700&auto=format&fit=crop&q=85"),
    ("Swiss Alps", "Mountains · Scenic escapes", "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=700&auto=format&fit=crop&q=85"),
]
experiences = [
    ("Japan adventure", "Temples, food and vibrant city life", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=700&auto=format&fit=crop&q=85"),
    ("Ocean discoveries", "Snorkeling and tropical coastlines", "https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=700&auto=format&fit=crop&q=85"),
]

def render_suggestions():
    for i, (name, desc, url) in enumerate(suggestions):
        st.markdown(f'<div class="destination-card"><img src="{url}"><div class="copy"><b>{name}</b><small>{desc}</small></div></div>', unsafe_allow_html=True)
        if st.button(f"Choose {name.split(',')[0]}", key=f"dest_{i}", use_container_width=True):
            st.session_state.destination = name.split(",")[0]
            st.session_state.navigation = "✦  New Chat"
            st.rerun()

def render_experiences():
    for i, (name, desc, url) in enumerate(experiences):
        st.markdown(f'<div class="destination-card"><img src="{url}"><div class="copy"><b>{name}</b><small>{desc}</small></div></div>', unsafe_allow_html=True)
        if st.button(f"Add {name}", key=f"exp_{i}", use_container_width=True):
            st.session_state.interests = desc
            st.session_state.navigation = "✦  New Chat"
            st.rerun()

# ------------------------------- MAIN -----------------------------------
st.markdown('<div class="page-brand"><span>✦</span> PlanSpark</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your intelligent travel companion — discover places, plan experiences, travel smarter.</div>', unsafe_allow_html=True)

if nav == "✦  New Chat":
    left, right = st.columns([1.7, .9], gap="large")
    with left:
        st.markdown('<div class="hero"><div class="hero-kicker">✦ Your next adventure starts here</div><h1>Where to next?</h1><p>Plan your perfect trip with AI. Discover places, build itineraries, and explore smarter.</p><span class="pill">✦ Smart trip planning</span><span class="pill">♡ Family escapes</span><span class="pill">⌁ Budget friendly</span></div>', unsafe_allow_html=True)
        st.markdown("### Plan your trip")
        st.caption("Add your destination and preferences. Your AI travel team will prepare the itinerary.")
        with st.form("trip_form"):
            x, y = st.columns(2)
            with x:
                destination = st.text_input("Where would you like to go?", key="destination", placeholder="City or country")
                duration = st.number_input("How many days?", min_value=1, max_value=30, step=1, key="duration_days")
                travelers = st.number_input("Travelers", min_value=1, max_value=20, step=1, key="num_people")
            with y:
                budget_currency = st.selectbox("Budget currency", fx_options, key="currency")
                budget = st.number_input("Total budget (0 = let AI suggest)", min_value=0.0, step=1000.0, key="total_budget")
                style = st.selectbox("Travel style", ["Budget / Backpacking", "Comfort / Mid-Range", "Luxury / Premium"], key="travel_style")
            interests = st.text_area("What would you love to do?", key="interests", placeholder="Beaches, food, culture, nature, shopping, adventure...")
            submitted = st.form_submit_button("✦  Plan my trip", use_container_width=True)

        if submitted:
            if not api_key.strip():
                st.error("Add your Groq API key under AI settings in the sidebar.")
            elif not destination.strip():
                st.error("Please enter a destination first.")
            else:
                budget_desc = f"total budget {budget_currency} {budget:,.2f}" if budget > 0 else f"no fixed budget; suggest a reasonable {budget_currency} budget"
                request = (f"Plan {int(duration)} days in {destination.strip()} for {int(travelers)} travelers, {budget_desc}. "
                           f"Travel style: {style}. Interests: {interests or 'Suggest a balanced range of experiences.'}")
                with st.spinner("Your travel team is creating your plan..."):
                    try:
                        result = orchestrate_trip_planning(request, api_key.strip(), model=model, status_callback=None)
                        st.session_state.last_trip_result = result
                        st.session_state.last_trip_destination = destination.strip()
                        st.session_state.last_trip_details = {"days": int(duration), "travelers": int(travelers), "budget": budget, "currency": budget_currency}
                    except Exception as exc:
                        st.error(f"Trip planning failed: {exc}")

        if st.session_state.last_trip_result:
            result = st.session_state.last_trip_result
            details = st.session_state.last_trip_details
            st.markdown("---")
            st.markdown("### ✨ Your trip plan")
            if result.get("success"):
                st.success("APPROVED — Your itinerary passed the Reviewer checks!")
            else:
                st.info("The Reviewer has requested another revision. The agents will continue until the plan is approved.")
            st.caption(f"Review process: {result.get('iterations_completed', 0)} rounds completed · Status: {result.get('approval_status', 'Pending')}")
            with st.expander("View Planner JSON blueprint"):
                st.json(result.get("final_plan", {}))
            with st.expander("View Reviewer history and revision feedback", expanded=not result.get("success", False)):
                for review in result.get("history", []):
                    status = "APPROVED" if review.get("is_approved") else "REVISE"
                    st.markdown(f"**Round {review.get('iteration', '?')}: {status}**")
                    st.write(review.get("reviewer_verdict", "No reviewer response returned."))
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Destination", st.session_state.last_trip_destination)
            m2.metric("Duration", f"{details.get('days','—')} days")
            m3.metric("Travelers", details.get("travelers","—"))
            m4.metric("Budget", f"{details.get('currency','')} {details.get('budget',0):,.0f}" if details.get("budget",0) else "Flexible")
            itinerary = result.get("final_itinerary") or "The planner did not return an itinerary. Please try again."
            st.markdown(itinerary)
            st.download_button("⬇ Download itinerary", itinerary, file_name="my_trip_itinerary.md", mime="text/markdown")
    with right:
        st.markdown('<div class="panel"><div class="panel-title">✦ Smart picks for you</div><div class="panel-sub">Popular destinations to spark your next trip</div></div>', unsafe_allow_html=True)
        render_suggestions()
        st.markdown('<div class="panel"><div class="panel-title">✈ Continue planning</div><div class="panel-sub">Ideas for your next experience</div></div>', unsafe_allow_html=True)
        render_experiences()

elif nav == "♧  My Trips":
    st.markdown("## ✈️ My Trips")
    st.caption("Your latest itinerary appears here after you create a trip.")
    if st.session_state.last_trip_result:
        st.markdown(f"### {st.session_state.last_trip_destination}")
        st.markdown(st.session_state.last_trip_result.get("final_itinerary", "No itinerary text returned."))
        st.download_button("Download this itinerary", st.session_state.last_trip_result.get("final_itinerary", ""), file_name="my_trip_itinerary.md")
    else:
        st.info("You haven't planned a trip in this session yet. Open New Chat to create one.")

elif nav == "⌕  Explore":
    st.markdown("## Explore destinations")
    st.caption("Choose a destination to start planning it.")
    cols = st.columns(3)
    for i, (name, desc, url) in enumerate(suggestions):
        with cols[i]:
            st.markdown(f'<div class="destination-card"><img src="{url}"><div class="copy"><b>{name}</b><small>{desc}</small></div></div>', unsafe_allow_html=True)
            if st.button(f"Plan {name.split(',')[0]}", key=f"explore_{i}", use_container_width=True):
                st.session_state.destination = name.split(",")[0]
                st.session_state.navigation = "✦  New Chat"
                st.rerun()

elif nav == "♡  Saved":
    st.markdown("## ♡ Saved places")
    st.info("Save a destination by choosing it from Explore. Your selected destination will be filled into the trip planner.")
    render_suggestions()

elif nav == "✧  Inspiration":
    st.markdown("## ✧ Travel inspiration")
    st.caption("Ideas to shape your next adventure.")
    cols = st.columns(2)
    for i, (name, desc, url) in enumerate(experiences):
        with cols[i]:
            st.markdown(f'<div class="destination-card"><img src="{url}"><div class="copy"><b>{name}</b><small>{desc}</small></div></div>', unsafe_allow_html=True)
            if st.button(f"Add to my preferences", key=f"inspire_{i}"):
                st.session_state.interests = desc
                st.session_state.navigation = "✦  New Chat"
                st.rerun()

elif nav == "♧  Community":
    st.markdown("## ♧ Travel community")
    st.markdown('<div class="hero"><h1>Share the journey.</h1><p>Use your trip preferences to create itineraries worth sharing. Community features can be connected to a database or social platform when you are ready.</p></div>', unsafe_allow_html=True)
    st.info("Community feed is not connected yet. Your navigation works, and this page is ready for a future community feed.")

st.markdown("<center><span class='muted'>PlanSpark · Discover places, plan experiences, travel smarter</span></center>", unsafe_allow_html=True)
