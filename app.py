import streamlit as st
import os
import json
import urllib.parse
from pydantic import BaseModel, Field
from groq import Groq

# ==========================================
# 1. DATA STRUCTURE REQUIREMENTS (Pydantic)
# ==========================================
class IndianMeals(BaseModel):
    breakfast: str = Field(description="Indian food item + brief energy/brain reasoning")
    lunch: str = Field(description="Indian food item + focus reasoning")
    dinner: str = Field(description="Light Indian food item + sleep-aid reasoning")
    snack: str = Field(description="Brain-boosting snack + quick reasoning")
    avoid: str = Field(description="What food/drink to avoid today + physiological reason")

class MindMateResponse(BaseModel):
    emotion: str = Field(description="One word capturing their primary state (e.g., Overwhelmed, Exhausted, Anxious)")
    empathy_validation: str = Field(description="A warm, validating open statement comforting the student, acknowledging it's normal to feel this way during this exam, and reminding them they are doing well.")
    emotion_insight: str = Field(description="1 sentence identifying the hidden root cause beneath the surface")
    academic_anxiety_pct: int = Field(description="Percentage of total stress coming from pure study load (0-100)")
    fatigue_burnout_pct: int = Field(description="Percentage of total stress coming from physical/mental exhaustion (0-100)")
    domestic_pressure_pct: int = Field(description="Percentage of total stress coming from family/peer expectations (0-100)")
    coping_plan: list[str] = Field(description="Exactly 3 sequential, actionable micro-steps to reset focus right now")
    meals: IndianMeals
    walk_prompt: str = Field(description="A creative, highly specific 15-minute evening mental-break mission")
    youtube_music_query: str = Field(description="Specific music search query for YouTube Music matching their mood (e.g., 'Calm Lo-Fi Rain Sounds for JEE Prep')")
    youtube_strategy_query: str = Field(description="Specific study/motivation search query for YouTube matching their issue (e.g., 'Organic Chemistry shortcut memory tricks')")
    parent_guardrail: str = Field(description="A pre-written, gentle, copy-pasteable 1-2 sentence message to send to parents to manage expectations")
    friend_nudge: str = Field(description="A warm, non-preachy sentence prompting quick social connection")
    burnout_score: int = Field(description="Burnout score from 1 to 10")
    dynamic_reset_exercise: str = Field(description="A highly tailored, custom 2-minute physiological breathing/grounding routine designed explicitly to tackle the detected emotion")
    motivational_nudge: str = Field(description="A deeply empathetic, tailored sentence of encouragement mentioning their exam context")

# ==========================================
# 2. PERFORMANCE CACHING (Resource Cache)
# ==========================================
@st.cache_resource
def get_groq_client(api_key: str):
    """
    Caches the Groq client object to avoid recreating it on every rerun,
    optimizing memory and connection resource utilization.
    """
    return Groq(api_key=api_key)

# ==========================================
# 3. STREAMLIT APP CONFIGURATION & STYLE
# ==========================================
st.set_page_config(
    page_title="🌿 MindMate // Your Safe Space",
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
# 4. SECURE API KEY LOGIC (Security Compliant)
# ----------------------------------------------------
api_key = None

# Retrieve API key in order of priority: st.secrets -> env variable -> manual file parse
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
elif os.getenv("GROQ_API_KEY"):
    api_key = os.getenv("GROQ_API_KEY")

# Manual file-parsing fallback for local environments (detects keys across different start CWD paths)
if not api_key:
    paths_to_try = [
        ".streamlit/secrets.toml",
        "../.streamlit/secrets.toml",
        "mindmate/.streamlit/secrets.toml"
    ]
    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    for line in f:
                        if "GROQ_API_KEY" in line and "=" in line:
                            val = line.split("=")[1].strip().strip('"').strip("'")
                            if val:
                                api_key = val
                                break
            except Exception:
                pass
            if api_key:
                break

# Invalidate template placeholders
if api_key in ["YOUR_GROQ_API_KEY_HERE", "YOUR_API_KEY_HERE", "", None]:
    api_key = None

# ----------------------------------------------------
# 5. SIDEBAR INPUTS & INTERFACE CONFIG (Accessible)
# ----------------------------------------------------
st.sidebar.markdown("### 🧬 Student Context Parameters")

# Target Examination Selection Selectbox
st.sidebar.subheader("📊 Your Exam Profile")
exam_choice = st.sidebar.selectbox(
    label="What milestone hurdle are you fighting for?",
    options=["NEET", "JEE", "UPSC", "CAT", "GATE", "CUET", "Board Exams"],
    help="Select the competitive exam you are preparing for to align the coping strategies with your syllabus structure."
)

# Days Remaining Slider
days = st.sidebar.slider(
    label="Days remaining until D-Day:",
    min_value=1,
    max_value=365,
    value=45,
    help="Drag the slider to set the number of days left before the actual examination begins."
)

# ----------------------------------------------------
# 6. CORE BACKEND GENERATION FUNCTION
# ----------------------------------------------------
def generate_sanctuary_plan(api_key, exam, days_left, journal_entry):
    try:
        if not api_key:
            st.error("🔑 Groq API Key missing! Please add GROQ_API_KEY to your Streamlit secrets configurations.")
            return None
            
        # Access cached Groq client
        client = get_groq_client(api_key)
        
        prompt = f"""
        You are MindMate, an elite, deeply empathetic AI wellness companion for Indian competitive exam students.
        
        Student Profile:
        - Exam: {exam}
        - Days Left: {days_left}
        
        Today's unstructured journal entry: "{journal_entry}"
        
        Perform a deep cognitive and structural analysis on this text.
        Make sure the percentages (academic_anxiety_pct, fatigue_burnout_pct, domestic_pressure_pct) total exactly 100.
        
        You MUST respond with a raw JSON object matching the JSON schema provided below. Do not wrap in markdown codeblocks, just output the raw JSON text directly.
        
        JSON Schema:
        {json.dumps(MindMateResponse.model_json_schema())}

        Constraints for your generation:
        1. meals: Recommend nutritious, localized Indian food items (breakfast, lunch, dinner, snack) with clear, physiological arguments detailing how they assist in study focus, energy levels, or sleep aids. Explicitly flag one item to avoid today.
        2. coping_plan: Extract EXACTLY 3 sequential, actionable micro-steps to reset focus (e.g., '1. Close your books. 2. Grab a glass of water. 3. Look out the window for 2 minutes').
        3. walk_prompt: Formulate a highly creative, specific 15-minute evening break mission.
        4. parent_guardrail: Write a pre-written, gentle, copy-pasteable 1-2 sentence text message the student can send to their parents to request space and manage expectations.
        5. dynamic_reset_exercise: Devise a highly customized 2-minute physiological grounding reset specifically targeting the detected emotion.
        6. motivational_nudge: Provide a deeply supportive, customized statement referencing {exam} and the remaining {days_left} days to instill resilient hope.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional student wellness assistant. You must output JSON matching the requested schema. Never output markdown code blocks or commentary."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.4  # Lowered temperature to optimize JSON validation reliability
        )
        
        raw_json_string = chat_completion.choices[0].message.content
        parsed_data = json.loads(raw_json_string)
        return MindMateResponse(**parsed_data)
        
    except Exception as e:
        st.error(f"Error communicating with core wellness backend: {str(e)}")
        return None

def generate_chat_response(api_key, history, user_message, context_summary):
    try:
        if not api_key:
            return "I'm here with you, but my API key configuration is missing."
            
        client = get_groq_client(api_key)
        messages = [{"role": "system", "content": f"You are MindMate, a warm, conversational AI companion helping a student with exam stress. Context about their current status: {context_summary}. Keep responses supportive, concise, and non-preachy."}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",  # Faster model for responsive interactive chat
            temperature=0.7
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"I'm here with you, but my connection stuttered slightly: {str(e)}"

# ==========================================
# 7. STREAMLIT APPLICATION INTERFACE
# ==========================================

# App Title & Header
st.markdown("""
<div>
    <h1 class="sanctuary-title" style="font-size: 2.8rem; margin-bottom: 0.2rem;">🌿 MindMate // Your Safe Space</h1>
    <p style="font-size: 1.15rem; color: #94A3B8; margin-bottom: 2rem;">Navigating competitive exam pressure with structured emotional and cognitive relief.</p>
</div>
""", unsafe_allow_html=True)

# Session State Initialization for Chat System
if "mindmate_data" not in st.session_state:
    st.session_state.mindmate_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "panic_active" not in st.session_state:
    st.session_state.panic_active = False

# Main Dashboard Entry
st.subheader("🌱 What's on your mind, friend? Let it out...")
journal_text = st.text_area(
    label=f"How is your {exam_choice} prep hitting you today? Feel free to vent about formulas, schedules, parents, or fatigue—I'm here to listen.",
    placeholder="It's completely normal to feel stressed. You are doing incredibly well just by showing up. Tell me what's going on...",
    height=140,
    help="Pour out your unstructured thoughts. Your entry remains private and is analyzed locally to calibrate your stress day-plan."
)

# Action Buttons Alignment
col_btn1, col_btn2 = st.columns([2, 1])

with col_btn1:
    generate_clicked = st.button("✨ Analyze & Build My Sanctuary Plan", use_container_width=True, help="Click here to submit your journal entry and compile your personalized daily wellness plan.")

with col_btn2:
    exercise_clicked = st.button("⚡ Quick Reset: Energy & Focus Alignment", use_container_width=True, type="secondary", help="Click here to bypass the journal report and start an immediate, customized breathing reset session.")

# ----------------------------------------------------
# 8. ROUTE DISPLAY: Mood-Responsive Grounding Or Blueprint
# ----------------------------------------------------

# Handle Quick Grounding Exercise
if exercise_clicked:
    st.session_state.panic_active = True
    st.session_state.mindmate_data = None

if st.session_state.panic_active:
    st.markdown('<div class="panic-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#10B981; margin-top:0;'>🛑 Grounding Sanctuary // Dynamic Mood Calibration</h2>", unsafe_allow_html=True)
    
    if not journal_text.strip():
        st.warning("Please quickly type a few words about your current feeling in the text box above so I can analyze and design an exercise specifically matching your current mood state!")
    else:
        with st.spinner("Analyzing your emotional state to calibrate breathing metrics..."):
            res = generate_sanctuary_plan(api_key, exam_choice, days, journal_text)
            if res:
                col_breath, col_grounding = st.columns([1, 1])
                with col_breath:
                    st.markdown("""
                    <div class="breathing-circle-container">
                        <div class="breathing-circle">BREATHE</div>
                        <div class="breathing-phase">
                            <b>Calibrated Breathing Cycle:</b><br/>
                            Follow the expanding rhythm. Inhale deeply through your nose, take a second sniff, and sigh exhale slowly.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_grounding:
                    st.write(f"#### 🧠 Detected Mood: `{res.emotion}`")
                    st.success(res.dynamic_reset_exercise)
                    
                    st.write("##### 🛡️ The Standard Grounding Method:")
                    st.write("- **5 things you see**, **4 things you touch**, **3 things you hear**, **2 things you smell**, **1 thing you taste**.")
    
    if st.button("💚 I Feel Calm / Return to Sanctuary", use_container_width=True, help="Click here to conclude the grounding session and return to the main dashboard."):
        st.session_state.panic_active = False
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# Handle Main Strategy Plan Generation
if generate_clicked:
    st.session_state.panic_active = False
    if not journal_text.strip():
        st.warning("Please type a few sentences in the journal dump area first so MindMate can hear your voice!")
    else:
        with st.spinner("Decoding stress signatures, generating specialized localized recovery blueprints..."):
            res = generate_sanctuary_plan(api_key, exam_choice, days, journal_text)
            if res:
                st.session_state.mindmate_data = res
                st.session_state.chat_history = []  # Reset conversational context for new plan

# Render Results Block if Data Exists in Session
if st.session_state.mindmate_data:
    res = st.session_state.mindmate_data
    st.markdown("---")
    
    # Empathy Validation Panel
    st.markdown(f"### ❤️ A Message for You:")
    st.info(f"**{res.empathy_validation}**")
    
    # Layout Split: Analytics Metrics & Visualization Charts
    col_metrics, col_chart = st.columns([1, 1])
    
    with col_metrics:
        st.metric("Primary Mental State Profile", res.emotion.upper(), help="The dominant emotion identified from your text journal analysis.")
        st.metric("Calculated Burnout Index", f"{res.burnout_score}/10", help="Our calculated estimate of your current cognitive burnout levels, where 10 is severe fatigue.")
        if res.burnout_score >= 8:
            st.error("⚠️ CRITICAL BURNOUT WARNING: Your indicators have crossed a critical safety point. Take an intentional academic break immediately.")
        st.markdown(f"**💡 Deep Behavioral Insight:** {res.emotion_insight}")

    with col_chart:
        # Structured progress boundaries for stress factors tracking metrics
        st.markdown('<div class="sanctuary-card">', unsafe_allow_html=True)
        st.write("#### 📊 Stress Distribution Breakdowns")
        st.write("Understanding where your stress stems from helps us address it target by target:")
        
        st.markdown("**📚 Academic Workload Fatigue**")
        st.write(f"Focus, syllabus coverage, and task pileup pressure: `{res.academic_anxiety_pct}%`")
        st.progress(res.academic_anxiety_pct / 100)
        
        st.markdown("**🔋 Physical Burnout & Exhaustion**")
        st.write(f"Physical fatigue, lack of sleep, or mental depletion: `{res.fatigue_burnout_pct}%`")
        st.progress(res.fatigue_burnout_pct / 100)
        
        st.markdown("**👥 Domestic & Peer Social Pressure**")
        st.write(f"Expectations from family, competitive comparisons, and social environments: `{res.domestic_pressure_pct}%`")
        st.progress(res.domestic_pressure_pct / 100)
        st.markdown('</div>', unsafe_allow_html=True)

    # Strategic UI Tab Delivery Separation
    tab1, tab2, tab3 = st.tabs([
        "🎯 Focus Reset & Coping Plan", 
        "🍱 Brain Fuel & Dietary Guide", 
        "🛡️ Family & Social Support Guardrails"
    ])
    
    with tab1:
        st.write("### ⚙️ Your 3-Step Micro-Action Directives:")
        for idx, step in enumerate(res.coping_plan, 1):
            st.write(f"**{idx}.** {step}")
        st.write("---")
        st.write("### 🚶‍♂️ Tonight's 15-Minute Cognitive Mind Mission:")
        st.code(res.walk_prompt, language="text")
        
    with tab2:
        st.write("### 🍛 Culturally Localized Stress-Management Foods")
        st.write("Nourish your body and brain using healthy, local Indian recommendations:")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            st.markdown(f"**🍳 Breakfast recommendation:** {res.meals.breakfast}")
            st.markdown(f"**🍛 Lunch recommendation:** {res.meals.lunch}")
        with f_col2:
            st.markdown(f"**🍲 Dinner recommendation:** {res.meals.dinner}")
            st.markdown(f"**🥜 Brain Snack recommendation:** {res.meals.snack}")
        st.error(f"**🚫 Physiological Threat to Avoid Today:** {res.meals.avoid}")
        
    with tab3:
        st.write("### 🏡 The Parent Boundary Management Guardrail")
        st.caption("Copy and paste this direct message to your parents to proactively manage expectations cleanly:")
        st.text_area("Click to copy parent boundary message:", value=res.parent_guardrail, height=70)
        
        st.write("---")
        st.write("### 🎧 Academic Efficiency & Interactive Sandbox Links")
        
        # Real Dynamic URL String Encoding for Instant Navigation Actions
        encoded_music = urllib.parse.quote(res.youtube_music_query)
        encoded_strategy = urllib.parse.quote(res.youtube_strategy_query)
        
        st.markdown(f"🎵 **Mood-Calibrated Soundscape:** [{res.youtube_music_query}](https://music.youtube.com/search?q={encoded_music})")
        st.markdown(f"📱 **High-Yield Tactical Strategy Search:** [{res.youtube_strategy_query}](https://www.youtube.com/results?search_query={encoded_strategy})")
        st.markdown(f"💬 **Social Connection Micro-Action:** {res.friend_nudge}")
        
        st.markdown("---")
        st.markdown("### 🌟 Motivational Nudge")
        st.markdown(f"""
        <div class="nudge-quote">
            "{res.motivational_nudge}"
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # 9. LIVE INTERACTIVE CHAT PLATFORM
    # ==========================================
    st.markdown("---")
    st.subheader("💬 Chat Platform // Stay & Talk with MindMate")
    st.caption("Want to adjust the steps? Need to vent more about a specific subject? Talk to me below, I am listening.")
    
    # Render interactive chat messages log
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Process Chat Input Sandbox Frame (Accessible)
    if chat_input := st.chat_input(placeholder="Talk to MindMate: Ask for custom food details, advice adjustments, or just share thoughts..."):
        # Append User Input
        st.session_state.chat_history.append({"role": "user", "content": chat_input})
        with st.chat_message("user"):
            st.write(chat_input)
            
        # Compile contextual snapshot summary for thin model mapping
        context_snap = f"Student is prepping for {exam_choice} with {days} days left. Current verified state is {res.emotion} with burnout index of {res.burnout_score}/10."
        
        # Stream response back
        with st.chat_message("assistant"):
            with st.spinner("Processing next response stream..."):
                reply = generate_chat_response(api_key, st.session_state.chat_history[:-1], chat_input, context_snap)
                st.write(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})