import streamlit as st
import PyPDF2
import io
import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
 
load_dotenv()
 
# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedReport AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=DM+Sans:wght@300;400;500&display=swap');
 
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Sora', sans-serif; }
 
.stApp { background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%); }
 
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141824 0%, #1e2535 100%);
    border-right: 1px solid rgba(99,179,237,0.15);
}
 
/* ── Result row card ── */
.result-row {
    display: flex;
    align-items: center;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    gap: 14px;
}
.result-row:hover { background: rgba(255,255,255,0.06); }
 
.test-name  { flex: 2; font-weight: 600; color: #e2e8f0; font-size: 15px; }
.test-value { flex: 1; font-family: 'Sora', monospace; font-size: 15px; font-weight: 700; text-align:center; }
.test-range { flex: 1.5; color: #718096; font-size: 13px; text-align:center; }
.test-meaning { flex: 3; color: #a0aec0; font-size: 13px; }
 
.badge-high   { background:#c53030; color:white; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:700; }
.badge-low    { background:#2b6cb0; color:white; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:700; }
.badge-normal { background:#276749; color:white; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:700; }
 
.row-abnormal { border-left: 3px solid #fc8181; }
.row-normal   { border-left: 3px solid #68d391; }
 
/* ── Summary card ── */
.summary-card {
    background: linear-gradient(135deg, rgba(99,179,237,0.08), rgba(99,179,237,0.02));
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 16px;
    padding: 22px 26px;
    font-size: 16px;
    line-height: 1.8;
    color: #e2e8f0;
}
 
/* ── Health banner ── */
.banner-green  { background:linear-gradient(135deg,rgba(72,187,120,0.15),rgba(72,187,120,0.05)); border:1px solid rgba(72,187,120,0.3); border-radius:14px; padding:18px 24px; }
.banner-yellow { background:linear-gradient(135deg,rgba(246,173,85,0.15),rgba(246,173,85,0.05));  border:1px solid rgba(246,173,85,0.3);  border-radius:14px; padding:18px 24px; }
.banner-red    { background:linear-gradient(135deg,rgba(252,129,129,0.15),rgba(252,129,129,0.05));border:1px solid rgba(252,129,129,0.3); border-radius:14px; padding:18px 24px; }
.banner-title  { font-family:'Sora',sans-serif; font-size:22px; font-weight:700; margin:0 0 6px 0; }
.banner-sub    { color:#a0aec0; font-size:14px; margin:0; }
 
/* ── Question card ── */
.q-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #63b3ed;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #e2e8f0;
    font-size: 15px;
}
 
/* ── Tip card ── */
.tip-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #68d391;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #e2e8f0;
    font-size: 15px;
}
 
/* ── Stat boxes ── */
.stat-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.stat-number { font-family:'Sora',sans-serif; font-size:32px; font-weight:700; }
.stat-label  { color:#718096; font-size:13px; margin-top:4px; }
 
/* ── Table header ── */
.table-header {
    display:flex; gap:14px; padding: 8px 18px;
    color:#718096; font-size:12px; font-weight:600;
    text-transform:uppercase; letter-spacing:1px;
}
.th2{flex:2;} .th1{flex:1;text-align:center;} .th15{flex:1.5;text-align:center;} .th3{flex:3;}
 
/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg,#3182ce,#63b3ed);
    color:white; border:none; border-radius:10px;
    padding:10px 28px; font-family:'Sora',sans-serif;
    font-weight:600; font-size:15px; width:100%;
}
.stButton > button:hover { background:linear-gradient(135deg,#2c5282,#3182ce); }
 
.stTabs [data-baseweb="tab-list"] { gap:8px; background:rgba(255,255,255,0.03); padding:8px; border-radius:12px; }
.stTabs [data-baseweb="tab"] { border-radius:8px; padding:8px 20px; font-size:14px; font-weight:500; }
.stTabs [aria-selected="true"] { background:rgba(99,179,237,0.2)!important; color:#63b3ed!important; }
 
.disclaimer-box {
    background:rgba(246,173,85,0.08); border:1px solid rgba(246,173,85,0.3);
    border-radius:10px; padding:12px 18px; color:#f6ad55; font-size:13px; font-weight:500;
}
.section-header {
    font-family:'Sora',sans-serif; font-size:12px; font-weight:600;
    text-transform:uppercase; letter-spacing:1.5px; color:#718096; margin-bottom:10px; margin-top:20px;
}
.info-box {
    background:rgba(99,179,237,0.07); border:1px solid rgba(99,179,237,0.2);
    border-radius:12px; padding:16px 20px; margin-bottom:16px;
}
</style>
""", unsafe_allow_html=True)
 
 
# ─── Helpers ───────────────────────────────────────────────────────────────────
def read_pdf(file):
    reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
    return "".join(page.extract_text() or "" for page in reader.pages)
 
 
LANGUAGE_PROMPTS = {
    "English":           "Respond entirely in English.",
    "Telugu (తెలుగు)":   "Respond entirely in Telugu (తెలుగు).",
    "Hindi (हिंदी)":     "Respond entirely in Hindi (हिंदी).",
    "Tamil (தமிழ்)":     "Respond entirely in Tamil.",
}
 
 
def analyze_report(text, language, age, gender, conditions):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    lang = LANGUAGE_PROMPTS.get(language, "Respond in English.")
    ctx  = f"{age}-year-old {gender}" + (f" with {conditions}" if conditions else "")
 
    prompt = f"""You are a compassionate medical assistant. {lang}
Patient: {ctx}.
 
Lab report:
{text}
 
Return ONLY valid JSON (no markdown, no extra text) with this exact structure:
{{
  "summary": "2-3 warm sentences explaining the overall report simply",
  "health_score": "ALL CLEAR" | "MILD CONCERN" | "NEEDS ATTENTION",
  "stats": {{
    "total_tests": <number>,
    "normal_count": <number>,
    "abnormal_count": <number>
  }},
  "test_results": [
    {{
      "name": "Test name",
      "value": "patient value with unit",
      "normal_range": "normal range",
      "status": "NORMAL" | "HIGH" | "LOW",
      "simple_meaning": "one simple sentence what this means for the patient"
    }}
  ],
  "questions": ["question 1", "question 2", "question 3", "question 4", "question 5"],
  "tips": [
    {{ "icon": "🥦", "tip": "actionable tip" }}
  ]
}}"""
 
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000
    )
    raw = resp.choices[0].message.content.strip()
    # strip markdown fences if present
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)
 
 
def health_banner(score):
    if score == "ALL CLEAR":
        return "banner-green",  "🟢 ALL CLEAR",  "#68d391", "All your values are within normal range — great news!"
    elif score == "MILD CONCERN":
        return "banner-yellow", "🟡 MILD CONCERN","#f6ad55", "A few values need a follow-up conversation with your doctor."
    else:
        return "banner-red",    "🔴 NEEDS ATTENTION","#fc8181","Please consult your doctor soon to discuss these results."
 
 
# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MedReport AI")
    st.markdown("---")
    st.markdown('<p class="section-header">Patient Profile</p>', unsafe_allow_html=True)
    age        = st.number_input("Your Age", 1, 120, 30)
    gender     = st.selectbox("Gender", ["Male", "Female", "Other"])
    conditions = st.text_input("Existing Conditions", placeholder="e.g. Diabetes, Hypertension")
    st.markdown('<p class="section-header">Language / భాష / भाषा</p>', unsafe_allow_html=True)
    language   = st.selectbox("Explain in:", ["English","Telugu (తెలుగు)","Hindi (हिंदी)","Tamil (தமிழ்)"])
    st.markdown("---")
    st.markdown('<div class="disclaimer-box">⚠️ <strong>Disclaimer</strong><br>AI tool for education only. NOT medical advice. Always consult your doctor.</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="color:#4a5568;font-size:12px;text-align:center;">MedReport AI · Groq + Llama 3<br>Made with ❤️ for patients</div>', unsafe_allow_html=True)
 
 
# ─── Main ──────────────────────────────────────────────────────────────────────
st.markdown("# 🏥 MedReport AI")
st.markdown("*Understand your lab report — simply, visually, in your language*")
st.markdown("")
 
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("📄 Upload your lab report PDF", type="pdf")
with col2:
    if uploaded_file:
        st.markdown('<div class="info-box">✅ <strong>File uploaded!</strong><br><span style="font-size:13px;color:#a0aec0;">Set profile in sidebar → click Analyze</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">📋 <strong>How it works</strong><br><span style="font-size:13px;color:#a0aec0;">1. Fill profile in sidebar<br>2. Upload PDF<br>3. Click Analyze</span></div>', unsafe_allow_html=True)
 
if uploaded_file:
    if st.button("🔬 Analyze My Report"):
        with st.spinner("🧠 Analyzing your report..."):
            pdf_text = read_pdf(uploaded_file)
            try:
                data = analyze_report(pdf_text, language, age, gender, conditions)
                st.session_state["data"] = data
            except Exception as e:
                st.error(f"Could not parse AI response. Try again. ({e})")
 
    if "data" in st.session_state:
        d = st.session_state["data"]
        score = d.get("health_score", "NEEDS ATTENTION")
        stats = d.get("stats", {})
 
        # ── Health Banner ──
        cls, title, color, subtitle = health_banner(score)
        st.markdown(f"""
        <div class="{cls}" style="margin:16px 0;">
            <p class="banner-title" style="color:{color};">{title}</p>
            <p class="banner-sub">{subtitle}</p>
        </div>""", unsafe_allow_html=True)
 
        # ── Stats Row ──
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#63b3ed;">{stats.get("total_tests","—")}</div><div class="stat-label">Total Tests</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#68d391;">{stats.get("normal_count","—")}</div><div class="stat-label">✅ Normal</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#fc8181;">{stats.get("abnormal_count","—")}</div><div class="stat-label">⚠️ Abnormal</div></div>', unsafe_allow_html=True)
 
        st.markdown("")
 
        # ── Tabs ──
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Summary", "🔬 All Test Results", "⚠️ Abnormal Only", "❓ Ask Your Doctor", "🥗 Tips"
        ])
 
        # ── Tab 1: Summary ──
        with tab1:
            st.markdown('<div class="summary-card">' + d.get("summary","") + '</div>', unsafe_allow_html=True)
 
        # ── Tab 2: All Results Table ──
        with tab2:
            results = d.get("test_results", [])
            if results:
                st.markdown("""
                <div class="table-header">
                    <span class="th2">Test Name</span>
                    <span class="th1">Your Value</span>
                    <span class="th1">Status</span>
                    <span class="th15">Normal Range</span>
                    <span class="th3">What It Means</span>
                </div>""", unsafe_allow_html=True)
                for r in results:
                    status = r.get("status","NORMAL").upper()
                    badge  = f'<span class="badge-{"high" if status=="HIGH" else "low" if status=="LOW" else "normal"}">{status}</span>'
                    row_cls = "row-abnormal" if status in ("HIGH","LOW") else "row-normal"
                    st.markdown(f"""
                    <div class="result-row {row_cls}">
                        <span class="test-name">{r.get("name","")}</span>
                        <span class="test-value" style="color:{'#fc8181' if status in ('HIGH','LOW') else '#68d391'};">{r.get("value","")}</span>
                        <span class="test-range">{badge}</span>
                        <span class="test-range">{r.get("normal_range","")}</span>
                        <span class="test-meaning">{r.get("simple_meaning","")}</span>
                    </div>""", unsafe_allow_html=True)
 
        # ── Tab 3: Abnormal Only ──
        with tab3:
            abnormals = [r for r in d.get("test_results",[]) if r.get("status","NORMAL").upper() in ("HIGH","LOW")]
            if not abnormals:
                st.markdown('<div class="result-row row-normal"><span class="test-name">🎉 Great news! All values are within normal range.</span></div>', unsafe_allow_html=True)
            else:
                for r in abnormals:
                    status = r.get("status","").upper()
                    icon   = "🔴" if status == "HIGH" else "🔵"
                    st.markdown(f"""
                    <div class="result-row row-abnormal" style="flex-direction:column; align-items:flex-start; gap:6px;">
                        <div style="display:flex; gap:12px; width:100%; align-items:center;">
                            <span style="font-size:18px;">{icon}</span>
                            <span class="test-name" style="flex:2;">{r.get("name","")}</span>
                            <span class="test-value" style="color:#fc8181;">{r.get("value","")}</span>
                            <span class="badge-{"high" if status=="HIGH" else "low"}">{status}</span>
                            <span style="color:#718096; font-size:13px;">Normal: {r.get("normal_range","")}</span>
                        </div>
                        <div style="color:#a0aec0; font-size:14px; padding-left:30px;">💬 {r.get("simple_meaning","")}</div>
                    </div>""", unsafe_allow_html=True)
 
        # ── Tab 4: Doctor Questions ──
        with tab4:
            questions = d.get("questions", [])
            for i, q in enumerate(questions, 1):
                st.markdown(f'<div class="q-card">🩺 <strong>Q{i}.</strong> {q}</div>', unsafe_allow_html=True)
            st.markdown('<div style="background:rgba(246,173,85,0.08);border:1px solid rgba(246,173,85,0.3);border-radius:10px;padding:14px 18px;color:#f6ad55;font-size:13px;margin-top:16px;">💡 <strong>Tip:</strong> Screenshot these questions before your appointment!</div>', unsafe_allow_html=True)
 
        # ── Tab 5: Tips ──
        with tab5:
            tips = d.get("tips", [])
            for t in tips:
                st.markdown(f'<div class="tip-card">{t.get("icon","💡")} {t.get("tip","")}</div>', unsafe_allow_html=True)
 
        # ── Download ──
        st.markdown("---")
        st.download_button(
            "⬇️ Download Full Report Explanation",
            data=json.dumps(d, ensure_ascii=False, indent=2),
            file_name="my_report_explained.json",
            mime="application/json",
            use_container_width=True
        )
        st.markdown('<div class="disclaimer-box" style="margin-top:16px;">🏥 <strong>Remember:</strong> This AI explanation is for understanding only. Please discuss ALL results with your doctor before making any health decisions.</div>', unsafe_allow_html=True)