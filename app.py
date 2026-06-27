import streamlit as st
import os
import json
import urllib.parse
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ----------------------------------------------------
# 1. DATA STRUCTURE REQUIREMENTS (Pydantic Schema)
# ----------------------------------------------------

class IndianMeals(BaseModel):
    breakfast: str = Field(..., description="Nutritious Indian breakfast option + cognitive/energy reasoning")
    lunch: str = Field(..., description="Focus-oriented Indian lunch recommendation + physiological reasoning")
    dinner: str = Field(..., description="Light Indian dinner option + sleep-aid/relaxation reasoning")
    snack: str = Field(..., description="Brain-boosting healthy Indian snack + quick mental reasoning")
    avoid: str = Field(..., description="Specific food/drink to avoid today + physiological reason")

class MindMateResponse(BaseModel):
    emotion: str = Field(..., description="One word capturing the student's primary emotional state (e.g. Overwhelmed)")
    emotion_insight: str = Field(..., description="1 sentence identifying the hidden root cause of their current state beneath the surface")
    triggers: list[str] = Field(..., description="2-3 highly specific academic or emotional stress triggers identified in the student's journal entry")
    coping_plan: list[str] = Field(..., description="Exactly 3 sequential, actionable micro-steps to reset focus")
    meals: IndianMeals
    walk_prompt: str = Field(..., description="A creative, highly specific 15-minute evening mental-break mission")
    music_mood: str = Field(..., description="A 5-word playlist vibe description (e.g. 'Chill lo-fi study beats sunset')")
    youtube_search: str = Field(..., description="A tactical, high-value search query tailored to their target exam scenario")
    parent_guardrail: str = Field(..., description="A pre-written, gentle, copy-pasteable 1-2 sentence message the student can send to their parents to manage expectations and reduce domestic pressure safely")
    friend_nudge: str = Field(..., description="A warm, non-preachy sentence prompting quick social connection")
    burnout_score: int = Field(..., description="A value from 1 to 10 assessing current student burnout severity")
    motivational_nudge: str = Field(..., description="A deeply empathetic, tailored sentence of encouragement mentioning their specific exam context")

# ----------------------------------------------------
# 2. STREAMLIT APP CONFIGURATION & STYLE INJECTION
# ----------------------------------------------------

st.set_page_config(
    page_title="MindMate // Student Exam Sanctuary",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Calm Sanctuary CSS Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Font Override */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif;
}

/* Gradient Text for Header */
.sanctuary-title {
    background: linear-gradient(135deg, #10B981 0%, #3B82F6 50%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* Glassmorphic Panel Cards */
.sanctuary-card {
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
}

/* Macro/Item Highlights */
.guide-box {
    background: rgba(30, 41, 59, 0.4);
    border-left: 4px solid #10B981;
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.warning-box {
    background: rgba(239, 68, 68, 0.1);
    border-left: 4px solid #EF4444;
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1rem;
    color: #F87171;
}

.nudge-quote {
    font-style: italic;
    font-size: 1.25rem;
    color: #E2E8F0;
    line-height: 1.6;
    border-left: 3px solid #8B5CF6;
    padding-left: 1rem;
    margin: 1.5rem 0;
}

/* Breathing Circle Animation for Panic Button */
@keyframes breathe {
    0% { transform: scale(1); background-color: rgba(16, 185, 129, 0.2); box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
    40% { transform: scale(1.4); background-color: rgba(59, 130, 246, 0.35); box-shadow: 0 0 25px rgba(59, 130, 246, 0.6); }
    60% { transform: scale(1.4); background-color: rgba(59, 130, 246, 0.35); box-shadow: 0 0 25px rgba(59, 130, 246, 0.6); }
    100% { transform: scale(1); background-color: rgba(16, 185, 129, 0.2); box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
}

.breathing-circle-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 2.5rem 0;
}

.breathing-circle {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.15rem;
    color: #FFFFFF;
    border: 3px solid rgba(255, 255, 255, 0.15);
    animation: breathe 9s infinite ease-in-out;
}

.breathing-phase {
    text-align: center;
    margin-top: 1.25rem;
    font-size: 1.1rem;
    color: #94A3B8;
    max-width: 400px;
    line-height: 1.5;
}

.panic-card {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 12px 40px rgba(239, 68, 68, 0.15);
    backdrop-filter: blur(15px);
    margin-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. SECURE API KEY LOGIC
# ----------------------------------------------------

api_key = None

# Retrieve API key in order of priority: st.secrets -> env variable
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.getenv("GEMINI_API_KEY"):
    api_key = os.getenv("GEMINI_API_KEY")

# Invalidate template placeholder key so user is prompted to enter their real key
if api_key in ["YOUR_GEMINI_API_KEY_HERE", "YOUR_API_KEY_HERE", "", None]:
    api_key = None

# ----------------------------------------------------
# 4. SIDEBAR INPUTS
# ----------------------------------------------------

st.sidebar.markdown("### 🧬 Student Context")

# Fallback field in sidebar for manual key injection
if not api_key:
    st.sidebar.warning("🔑 Gemini API Key not detected in secrets.")
    api_key_input = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    if api_key_input:
        api_key = api_key_input

# Select target exam
exam_options = ["JEE", "NEET", "UPSC", "CAT", "GATE", "CUET", "Board Exams"]
selected_exam = st.sidebar.selectbox("Target Examination:", exam_options)

# Days left for exam
days_left = st.sidebar.slider(
    "Days Left for the Exam:",
    min_value=1,
    max_value=365,
    value=45,
    step=1
)

# Persistent session states
if "mindmate_response" not in st.session_state:
    st.session_state.mindmate_response = None
if "panic_active" not in st.session_state:
    st.session_state.panic_active = False

# ----------------------------------------------------
# 5. CORE LOGIC: SCHEMA API CALL
# ----------------------------------------------------

def generate_sanctuary_plan(api_key, exam, days_left, journal_text):
    """
    Invokes Gemini API with rigid validation constraints using google-genai Pydantic schemas.
    """
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are MindMate, a deeply compassionate, highly skilled student counselor and cognitive-behavioral therapy (CBT) expert.
    A student preparing for the intensely competitive {exam} exam (with exactly {days_left} days remaining) has shared this raw venting journal entry:
    
    "{journal_text}"
    
    Analyze their emotional state, stress triggers, and signs of burnout.
    
    Constraints for your JSON output matching the schema:
    1. meals: Recommend nutritious, localized Indian food items (breakfast, lunch, dinner, snack) with clear, physiological arguments detailing how they assist in study focus, energy levels, or sleep aids. Explicitly flag one item to avoid.
    2. coping_plan: Extract EXACTLY 3 sequential, actionable micro-steps to reset focus (e.g., '1. Close your books. 2. Grab a glass of water. 3. Look out the window for 2 minutes').
    3. walk_prompt: Formulate a highly creative, specific 15-minute evening break mission (e.g. 'Walk outside and count 5 white cars', 'Observe the tallest tree nearby and count its main branches').
    4. parent_guardrail: Write a pre-written, gentle, copy-pasteable 1-2 sentence text message the student can send to their parents to request space, manage high expectations, and reduce domestic pressure safely.
    5. motivational_nudge: Provide a deeply supportive, customized statement referencing {exam} and the remaining {days_left} days to instill resilient hope.
    """
    
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MindMateResponse,
            temperature=0.3,
        )
    )
    
    return MindMateResponse.model_validate_json(response.text)

# ----------------------------------------------------
# 6. APP DASHBOARD LAYOUT & BUTTON ROUTING
# ----------------------------------------------------

st.markdown("""
<div>
    <h1 class="sanctuary-title" style="font-size: 2.8rem; margin-bottom: 0.2rem;">🧠 MindMate</h1>
    <p style="font-size: 1.15rem; color: #94A3B8; margin-bottom: 2rem;">Your Exam Sanctuary // Navigating competitive stress with structured emotional relief.</p>
</div>
""", unsafe_allow_html=True)

# Main input text area
journal_text = st.text_area(
    "Pour your mind out today. Journal your thoughts, fears, or study schedule anxieties here...",
    placeholder="e.g. I am failing my mock tests and my parents have high expectations. Only 45 days left for JEE and I feel like running away...",
    height=120
)

# Button grid layout
col_btn_a, col_btn_b, col_empty = st.columns([2, 2, 4])

with col_btn_a:
    if st.button("✨ Analyze & Build My Sanctuary Plan", use_container_width=True):
        st.session_state.panic_active = False
        if not api_key:
            st.error("🔑 Please provide a valid Gemini API Key in the sidebar configuration.")
        elif not journal_text.strip():
            st.warning("📝 Please pour your thoughts into the text area before planning.")
        else:
            with st.spinner("🌌 Anchoring your thoughts and assembling mental relief sanctuary..."):
                try:
                    res = generate_sanctuary_plan(
                        api_key=api_key,
                        exam=selected_exam,
                        days_left=days_left,
                        journal_text=journal_text
                    )
                    st.session_state.mindmate_response = res
                    st.success("Your exam sanctuary blueprint is ready!")
                except Exception as e:
                    st.error("⚠️ Failed to reach Gemini API. Please verify configuration settings.")
                    st.exception(e)

with col_btn_b:
    if st.button("🚨 INSTANT PANIC BUTTON", use_container_width=True):
        st.session_state.panic_active = True
        st.session_state.mindmate_response = None

# ----------------------------------------------------
# 7. ROUTE DISPLAY: INSTANT PANIC OR BLUEPRINT
# ----------------------------------------------------

if st.session_state.panic_active:
    # Render timed physiological reset
    st.markdown('<div class="panic-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#EF4444; margin-top:0;'>🛑 Grounding Sanctuary // Active Reset</h2>", unsafe_allow_html=True)
    st.write(
        "You are safe. Your heart rate is just temporarily spiked. "
        "Let's bring you back with a double-inhale physiological sigh reset."
    )
    
    col_breath, col_grounding = st.columns([1, 1])
    
    with col_breath:
        st.markdown("""
        <div class="breathing-circle-container">
            <div class="breathing-circle">BREATHE</div>
            <div class="breathing-phase">
                <b>Double Inhale, Long Sigh:</b><br/>
                1. Inhale deeply through your nose.<br/>
                2. Take a second sharp sniff to inflate lungs fully.<br/>
                3. Exhale slowly through your mouth.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_grounding:
        st.write("#### 🛡️ The 5-4-3-2-1 Grounding Method")
        st.markdown(
            "- 👀 **5 things you can see**: Look around and name 5 items in your room.\n"
            "- ✋ **4 things you can touch**: Feel your desk, clothing, chair, or notebook.\n"
            "- 👂 **3 things you can hear**: Focus on the clock tick, fan hum, or distant traffic.\n"
            "- 👃 **2 things you can smell**: Smell your book pages, eraser, or tea/water.\n"
            "- 👅 **1 thing you can taste**: A sip of water or focus on your breath.\n"
        )
        
    if st.button("💚 I Feel Calm / Return to Sanctuary", use_container_width=True):
        st.session_state.panic_active = False
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# Render main AI companion response if set
elif st.session_state.mindmate_response:
    res = st.session_state.mindmate_response
    
    st.markdown('<div class="sanctuary-card">', unsafe_allow_html=True)
    st.subheader("📊 Well-being Metrics & Insights")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="Primary Emotion", value=res.emotion.capitalize())
    with col_m2:
        st.metric(label="Burnout Score (1-10)", value=f"{res.burnout_score} / 10")
        
    # High Burnout Warning Alert
    if res.burnout_score >= 8:
        st.error(
            f"⚠️ **CRITICAL BURNOUT ALERT:** Your burnout is flagged at {res.burnout_score}/10. "
            "Please prioritize sleep, step back from books today, and talk to someone close. Your health is irreplaceable."
        )
        
    st.markdown(f"**Root Insight:** {res.emotion_insight}")
    
    # Stress Triggers Tag Display
    st.markdown("**Academic Stress Triggers Identified:**")
    trigger_tags = " ".join([f"`{t}`" for t in res.triggers])
    st.markdown(trigger_tags)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ----------------------------------------------------
    # TABS FOR BLUEPRINT PRESENTATION
    # ----------------------------------------------------
    tab_reset, tab_fuel, tab_guardrail = st.tabs([
        "🎯 Mind Reset & Action Plan",
        "🍱 Brain Fuel (Dietary Guide)",
        "🛡️ Domestic & Social Guardrail"
    ])
    
    # Tab 1: Mind Reset & Action Plan
    with tab_reset:
        st.markdown("### 🎯 Your Focus Reset Action Plan")
        st.write("Complete these 3 micro-steps in sequence:")
        for idx, step in enumerate(res.coping_plan, 1):
            st.markdown(f"**Step {idx}:** {step}")
            
        st.markdown("---")
        st.markdown("### 🚶 Evening Walk Sanctuary Mission")
        st.markdown(f"""
        <div class="guide-box">
            <b>Your 15-Minute Cognitive Reset Mission:</b><br/>
            {res.walk_prompt}
        </div>
        """, unsafe_allow_html=True)
        
    # Tab 2: Brain Fuel
    with tab_fuel:
        st.markdown("### 🍱 Localized Brain Fuel recommendations")
        st.write("Optimize your gut-brain axis with healthy Indian options:")
        
        st.markdown(f"""
        <div class="guide-box">
            🍳 <b>Breakfast:</b> {res.meals.breakfast}
        </div>
        <div class="guide-box">
            🥗 <b>Lunch:</b> {res.meals.lunch}
        </div>
        <div class="guide-box">
            🍲 <b>Dinner:</b> {res.meals.dinner}
        </div>
        <div class="guide-box">
            🥜 <b>Snack:</b> {res.meals.snack}
        </div>
        <div class="warning-box">
            ⚠️ <b>Avoid Today:</b> {res.meals.avoid}
        </div>
        """, unsafe_allow_html=True)
        
    # Tab 3: Domestic & Social Guardrails
    with tab_guardrail:
        st.markdown("### 🛡️ Managing domestic pressure & social anchors")
        
        st.markdown("💬 **Parent Expectation Guardrail Message**")
        st.write("Copy and paste this message to communicate boundaries and expectations to your parents:")
        st.code(res.parent_guardrail, language="text")
        
        st.markdown("💬 **Friend Nudge**")
        st.info(res.friend_nudge)
        
        st.markdown("🎵 **Music Mood Recommendation**")
        st.write(f"Vibe Recommendation: **{res.music_mood}**")
        
        st.markdown("🔍 **Tactical Study Material/Break Search**")
        st.write(f"Search for this on YouTube for helpful support: `{res.youtube_search}`")
        
        # Clickable simulation link to search YouTube
        query_encoded = urllib.parse.quote(res.youtube_search)
        search_link = f"https://www.youtube.com/results?search_query={query_encoded}"
        st.markdown(f"[🔗 Click here to search YouTube for '{res.youtube_search}']({search_link})")
        
        st.markdown("---")
        st.markdown("### 🌟 Motivational Nudge")
        st.markdown(f"""
        <div class="nudge-quote">
            "{res.motivational_nudge}"
        </div>
        """, unsafe_allow_html=True)

    # Reset sanctuary layout
    if st.button("🔄 Clear and Restart Journal", use_container_width=True):
        st.session_state.mindmate_response = None
        st.session_state.panic_active = False
        st.rerun()
