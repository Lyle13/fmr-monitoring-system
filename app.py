import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime
from PIL import Image

# Configure the page layout
st.set_page_config(page_title="FMR Transparency Dashboard", layout="wide")

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def determine_project_status(target_date_str, progress, evaluation_date):
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    days_remaining = (target_date - evaluation_date).days

    if progress >= 100:
        return "Completed", [0, 255, 0, 160] 
    elif days_remaining < 0:
        return "Delayed", [255, 0, 0, 160] 
    elif days_remaining <= 30 and progress < 80:
        return "At Risk", [255, 165, 0, 160] 
    else:
        return "On Track", [0, 150, 255, 160] 

def mock_ai_prediction(image):
    """
    This is a placeholder for your future AI model (e.g., TensorFlow/PyTorch).
    For now, it just simulates analyzing the image.
    """
    import random
    score = random.randint(10, 95)
    classification = "Severe Defect (Potholes/Erosion)" if score > 50 else "Normal Unpaved Surface"
    return classification, score


# ==========================================
# MAIN APP NAVIGATION (TABS)
# ==========================================
st.title("🚜 Geospatial FMR Transparency Dashboard")

# Create 3 Navigation Tabs
tab_map, tab_ai, tab_eval = st.tabs([
    "🗺️ Project Dashboard", 
    "🤖 AI Image Validation", 
    "📋 System Assessment (SUS/TAM)"
])

# ------------------------------------------
# TAB 1: DASHBOARD & MAP (Objectives 2, 3, 4)
# ------------------------------------------
with tab_map:
    col1, col2 = st.columns([1, 3])
    with col1:
        simulated_date = st.date_input("🗓️ System Current Date", datetime.now().date())
    
    # Mock Data
    data = {
        'project_name': ['Brgy. San Jose Road Concreting', 'Sta. Cruz Repair Phase 2', 'Mandurriao-Jaro Link'],
        'lat': [10.7202, 10.7310, 10.7150],
        'lon': [122.5621, 122.5500, 122.5400],
        'target_date': ['2026-03-15', '2026-02-10', '2025-12-01'],
        'progress_pct': [60, 40, 100] 
    }
    df = pd.DataFrame(data)

    df[['status', 'color']] = df.apply(
        lambda row: pd.Series(determine_project_status(row['target_date'], row['progress_pct'], simulated_date)), axis=1
    )

    # PyDeck Map
    view_state = pdk.ViewState(latitude=10.7250, longitude=122.5550, zoom=12, pitch=45)
    layer = pdk.Layer(
        'ScatterplotLayer', data=df, get_position='[lon, lat]',
        get_color='color', get_radius=300, pickable=True,
    )
    st.pydeck_chart(pdk.Deck(map_style=None, initial_view_state=view_state, layers=[layer], tooltip={"text": "{project_name}\nStatus: {status}\nProgress: {progress_pct}%"}))

    st.subheader("Project Directory")
    st.dataframe(df[['project_name', 'status', 'progress_pct', 'target_date', 'lat', 'lon']], use_container_width=True)


# ------------------------------------------
# TAB 2: AI VISUAL VALIDATION (Objective 5 Part A)
# ------------------------------------------
with tab_ai:
    st.header("Automated Visual Validation")
    st.markdown("Upload field imagery to automatically distinguish road defects from normal unpaved surfaces using AI.")
    
    uploaded_file = st.file_uploader("Upload Road Image (Wide Shot or Close-up)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Field Image", use_container_width=True)
        
        # Run the mock AI model
        with st.spinner('AI is analyzing the image for defects...'):
            classification, severity_score = mock_ai_prediction(image)
        
        # Display Results
        st.subheader("AI Assessment Results:")
        if severity_score > 50:
            st.error(f"**Classification:** {classification}")
        else:
            st.success(f"**Classification:** {classification}")
            
        st.metric(label="Calculated Severity Score", value=f"{severity_score}/100")
        st.info("💡 Note: In the final system, this severity score will automatically feed into the Geospatial Prioritization Module (PI) for this specific road segment.")


# ------------------------------------------
# TAB 3: SYSTEM EVALUATION (Objective 5 Part B)
# ------------------------------------------
with tab_eval:
    st.header("System Usability & Acceptance Evaluation")
    st.markdown("For LGU Engineers and Citizen Testers: Please evaluate your experience using this M&E Support System.")
    
    with st.form("evaluation_form"):
        st.subheader("System Usability Scale (SUS)")
        st.slider("1. I think that I would like to use this system frequently.", 1, 5, 3)
        st.slider("2. I found the system unnecessarily complex.", 1, 5, 3)
        st.slider("3. I thought the system was easy to use.", 1, 5, 3)
        # (You would add the remaining 7 SUS questions here)
        
        st.subheader("Technology Acceptance Model (TAM)")
        st.slider("Perceived Usefulness: Using this system would improve FMR monitoring performance.", 1, 5, 3)
        st.slider("Perceived Ease of Use: My interaction with this system is clear and understandable.", 1, 5, 3)
        
        submitted = st.form_submit_button("Submit Evaluation Data")
        if submitted:
            st.success("Evaluation saved securely to the database. Thank you for your participation!")