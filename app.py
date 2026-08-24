import streamlit as st
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

from core.parser import extract_text
from core.analyzer import analyze_resume, score_ats, tailor_resume
from core.ats_scorer import keyword_overlap_score
from utils.helpers import count_tokens, truncate_text

# Page Config
st.set_page_config(
    page_title="AlignCV - AI Resume Analyzer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --accent:        #7c6df0;
        --accent-light:  #a78bfa;
        --accent-glow:   rgba(124,109,240,0.35);
        --surface:       rgba(255,255,255,0.04);
        --surface-hover: rgba(255,255,255,0.08);
        --border:        rgba(255,255,255,0.08);
        --border-accent: rgba(124,109,240,0.4);
        --text-primary:  #f0eeff;
        --text-muted:    rgba(240,238,255,0.55);
        --green:   #22d3a0;
        --red:     #f87171;
        --yellow:  #fbbf24;
        --blue:    #60a5fa;
        --orange:  #fb923c;
        --radius:  14px;
    }

    html, body, .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background: #0d0b1a !important;
        color: var(--text-primary) !important;
    }

    .stApp {
        background:
            radial-gradient(ellipse 80% 50% at 20% 0%, rgba(124,109,240,0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(167,139,250,0.08) 0%, transparent 55%),
            #0d0b1a !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(13,11,26,0.97) !important;
        border-right: 1px solid var(--border) !important;
        backdrop-filter: blur(20px);
    }
    [data-testid="stSidebar"] * {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebarContent"] { padding: 1.5rem 1rem !important; }

    .sidebar-brand {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 1.5rem;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid var(--border);
    }
    .sidebar-brand-icon {
        width: 38px; height: 38px;
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 0 16px var(--accent-glow);
    }
    .sidebar-brand-name {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em;
    }
    .sidebar-brand-tag {
        font-size: 0.65rem; color: var(--accent-light) !important;
        font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase;
    }
    .sidebar-section-title {
        font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.12em; color: var(--text-muted) !important;
        margin: 1.4rem 0 0.6rem 0;
    }

    .score-guide {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius); overflow: hidden; margin-top: 0.5rem;
    }
    .score-guide-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.55rem 1rem; border-bottom: 1px solid var(--border); font-size: 0.82rem;
    }
    .score-guide-row:last-child { border-bottom: none; }
    .score-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem; font-weight: 500; padding: 0.15rem 0.5rem; border-radius: 6px;
    }
    .badge-green  { background: rgba(34,211,160,0.15);  color: var(--green); }
    .badge-yellow { background: rgba(251,191,36,0.15);  color: var(--yellow); }
    .badge-orange { background: rgba(251,146,60,0.15);  color: var(--orange); }
    .badge-red    { background: rgba(248,113,113,0.15); color: var(--red); }

    .privacy-badge {
        background: rgba(34,211,160,0.07); border: 1px solid rgba(34,211,160,0.2);
        border-radius: 10px; padding: 0.65rem 1rem; font-size: 0.78rem;
        color: var(--green) !important; text-align: center; margin-top: 1.5rem;
    }

    .main-header {
        position: relative; overflow: hidden;
        background: linear-gradient(135deg, #1a1535 0%, #231a45 50%, #1a1535 100%);
        border: 1px solid var(--border-accent); border-radius: 20px;
        padding: 3rem 2.5rem 2.5rem; margin-bottom: 2.5rem; text-align: center;
        box-shadow: 0 0 60px rgba(124,109,240,0.15), 0 1px 0 rgba(255,255,255,0.05) inset;
    }
    .main-header::before {
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: conic-gradient(from 0deg at 50% 50%, transparent 0deg, rgba(124,109,240,0.06) 60deg, transparent 120deg);
        animation: spin 20s linear infinite; pointer-events: none;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    .header-eyebrow {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.18em;
        text-transform: uppercase; color: var(--accent-light); margin-bottom: 0.8rem;
    }
    .header-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem,4vw,2.9rem); font-weight: 700;
        letter-spacing: -0.03em; line-height: 1.15; color: #ffffff; margin: 0 0 0.75rem 0;
    }
    .header-title span {
        background: linear-gradient(135deg, #a78bfa, #7c6df0, #c4b5fd);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .header-subtitle {
        font-size: 1rem; color: var(--text-muted); font-weight: 400;
        max-width: 520px; margin: 0 auto; line-height: 1.6;
    }
    .header-pills {
        display: flex; justify-content: center; gap: 0.6rem; margin-top: 1.5rem; flex-wrap: wrap;
    }
    .header-pill {
        background: rgba(124,109,240,0.12); border: 1px solid rgba(124,109,240,0.25);
        border-radius: 20px; padding: 0.3rem 0.85rem;
        font-size: 0.78rem; font-weight: 500; color: var(--accent-light);
    }

    .upload-zone-label {
        font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 600;
        color: var(--text-primary); margin-bottom: 0.6rem;
    }

    [data-testid="stFileUploader"] {
        background: var(--surface) !important;
        border: 1.5px dashed var(--border-accent) !important;
        border-radius: var(--radius) !important;
        transition: border-color 0.2s, background 0.2s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-light) !important;
        background: var(--surface-hover) !important;
    }

    .stTextArea textarea {
        background: var(--surface) !important; border: 1.5px solid var(--border) !important;
        border-radius: var(--radius) !important; color: var(--text-primary) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 0.9rem !important;
        transition: border-color 0.2s; resize: vertical;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(124,109,240,0.15) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c6df0, #9b8af4) !important;
        border: none !important; border-radius: 12px !important; color: #fff !important;
        font-family: 'Space Grotesk', sans-serif !important; font-size: 1rem !important;
        font-weight: 600 !important; letter-spacing: 0.01em !important;
        padding: 0.75rem 2rem !important;
        box-shadow: 0 4px 20px rgba(124,109,240,0.35) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(124,109,240,0.5) !important;
        filter: brightness(1.08) !important;
    }

    .stDownloadButton > button {
        background: var(--surface) !important; border: 1px solid var(--border-accent) !important;
        border-radius: 12px !important; color: var(--accent-light) !important;
        font-family: 'Space Grotesk', sans-serif !important; font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(124,109,240,0.12) !important; transform: translateY(-1px) !important;
    }

    .score-card {
        background: linear-gradient(145deg, rgba(124,109,240,0.1), rgba(167,139,250,0.06));
        border: 1px solid var(--border-accent); border-radius: 18px;
        padding: 2rem 1.5rem; text-align: center; backdrop-filter: blur(20px);
        box-shadow: 0 0 40px rgba(124,109,240,0.1), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .score-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 60px rgba(124,109,240,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .score-value {
        font-family: 'Space Grotesk', sans-serif; font-size: 4rem; font-weight: 700;
        background: linear-gradient(135deg, #c4b5fd, #a78bfa, #7c6df0);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        line-height: 1; letter-spacing: -0.04em;
    }
    .score-label {
        font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.14em; color: var(--text-muted); margin-top: 0.5rem;
    }
    .score-status { margin-top: 0.75rem; font-size: 0.92rem; font-weight: 600; }

    .section-header {
        font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700;
        letter-spacing: -0.01em; color: var(--text-primary);
        margin: 2rem 0 1.2rem 0; padding-bottom: 0.75rem; border-bottom: 1px solid var(--border);
    }

    .pill-green  { display:inline-block; background:rgba(34,211,160,0.12);  color:#22d3a0; border:1px solid rgba(34,211,160,0.25);  padding:.38rem .85rem; border-radius:20px; margin:.2rem; font-size:.82rem; font-weight:500; }
    .pill-red    { display:inline-block; background:rgba(248,113,113,0.12); color:#f87171; border:1px solid rgba(248,113,113,0.25); padding:.38rem .85rem; border-radius:20px; margin:.2rem; font-size:.82rem; font-weight:500; }
    .pill-blue   { display:inline-block; background:rgba(96,165,250,0.12);  color:#60a5fa; border:1px solid rgba(96,165,250,0.25);  padding:.38rem .85rem; border-radius:20px; margin:.2rem; font-size:.82rem; font-weight:500; }
    .pill-orange { display:inline-block; background:rgba(251,146,60,0.12);  color:#fb923c; border:1px solid rgba(251,146,60,0.25);  padding:.38rem .85rem; border-radius:20px; margin:.2rem; font-size:.82rem; font-weight:500; }
    .pill-purple { display:inline-block; background:rgba(124,109,240,0.12); color:#a78bfa; border:1px solid rgba(124,109,240,0.25); padding:.38rem .85rem; border-radius:20px; margin:.2rem; font-size:.82rem; font-weight:500; }

    .keyword-matched { display:inline-block; background:rgba(34,211,160,0.12);  color:#22d3a0; padding:.28rem .65rem; border-radius:7px; margin:.18rem; font-size:.78rem; font-weight:600; }
    .keyword-missing { display:inline-block; background:rgba(248,113,113,0.12); color:#f87171; padding:.28rem .65rem; border-radius:7px; margin:.18rem; font-size:.78rem; font-weight:600; }

    .improvement-card {
        position: relative; background: var(--surface); border: 1px solid var(--border);
        border-left: 3px solid var(--accent); border-radius: 0 var(--radius) var(--radius) 0;
        padding: 1.1rem 1.4rem; margin: 0.7rem 0; font-size: 0.9rem; line-height: 1.6;
        transition: background 0.2s;
    }
    .improvement-card:hover { background: var(--surface-hover); }
    .improvement-card strong {
        font-family: 'Space Grotesk', sans-serif; color: var(--accent-light);
        font-size: 0.82rem; letter-spacing: 0.05em; text-transform: uppercase;
    }

    .tip-box {
        background: rgba(96,165,250,0.07); border: 1px solid rgba(96,165,250,0.2);
        border-radius: var(--radius); padding: 1.1rem 1.3rem;
        font-size: 0.88rem; color: #60a5fa; line-height: 1.6;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #7c6df0, #a78bfa, #c4b5fd); border-radius: 10px;
    }
    .stProgress > div > div > div { background: rgba(255,255,255,0.06); border-radius: 10px; }

    .section-col-label {
        font-family: 'Space Grotesk', sans-serif; font-size: 0.82rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.1em; color: rgba(240,238,255,0.55);
        margin-bottom: 0.5rem;
    }

    [data-testid="stExpander"] {
        background: var(--surface) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }

    hr { border: none; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

    .stCaption, [data-testid="stCaptionContainer"] { color: rgba(240,238,255,0.55) !important; font-size: 0.8rem !important; }

    [data-testid="stRadio"] label { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 0.9rem !important; font-weight: 500 !important; }

    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(124,109,240,0.4); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(124,109,240,0.7); }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="header-eyebrow">✦ Powered by Gemini AI</div>
    <h1 class="header-title">Resume<span>IQ</span></h1>
    <p class="header-subtitle">
        Upload your resume and get actionable AI insights, ATS compatibility scores,
        and a tailored version matched to any job description.
    </p>
    <div class="header-pills">
        <span class="header-pill">📊 Deep Analysis</span>
        <span class="header-pill">🎯 ATS Scoring</span>
        <span class="header-pill">✍️ Smart Rewriting</span>
        <span class="header-pill">🔒 Privacy-First</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">✦</div>
        <div>
            <div class="sidebar-brand-name">ResumeIQ</div>
            <div class="sidebar-brand-tag">AI-Powered</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">⚙ Analysis Mode</div>', unsafe_allow_html=True)
    mode = st.radio(
        "Analysis Mode",
        ["📊 Analyze Only", "🎯 ATS Score + Tailor"],
        help="Choose 'Analyze Only' for general feedback, or 'ATS Score + Tailor' to optimize for a specific job.",
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section-title">📈 Score Reference</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="score-guide">
        <div class="score-guide-row">
            <span>85 – 100</span>
            <span class="score-badge badge-green">✓ Excellent</span>
        </div>
        <div class="score-guide-row">
            <span>70 – 84</span>
            <span class="score-badge badge-yellow">◎ Good</span>
        </div>
        <div class="score-guide-row">
            <span>50 – 69</span>
            <span class="score-badge badge-orange">◑ Fair</span>
        </div>
        <div class="score-guide-row">
            <span>0 – 49</span>
            <span class="score-badge badge-red">✕ Needs Work</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="privacy-badge">
        🔒 Processed in-memory · Never stored
    </div>
    """, unsafe_allow_html=True)

# Upload Section
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="upload-zone-label">📎  Upload Resume</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader(
        "Drag and drop or click to upload (PDF or DOCX)",
        type=["pdf", "docx"],
        label_visibility="collapsed",
    )
    if resume_file:
        st.success(f"✓ **{resume_file.name}**  ·  {resume_file.size / 1024:.1f} KB")

with col2:
    jd_text = ""
    if "ATS" in mode:
        st.markdown('<div class="upload-zone-label">📋  Job Description</div>', unsafe_allow_html=True)
        jd_text = st.text_area(
            "Job Description",
            height=180,
            placeholder="Paste the full job description here — we'll score your resume against it and rewrite it to fit…",
            label_visibility="collapsed",
        )
    else:
        st.markdown('<div class="upload-zone-label">💡  Pro Tip</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="tip-box">
            Switch to <strong>🎯 ATS Score + Tailor</strong> mode in the sidebar to score your
            resume against a specific job posting and receive an AI-rewritten version optimised
            for that role.
        </div>
        """, unsafe_allow_html=True)

# Analyze Button
st.markdown("<br>", unsafe_allow_html=True)

if resume_file:
    analyze_btn = st.button("✦  Analyze My Resume", type="primary", use_container_width=True)
else:
    analyze_btn = False
    st.markdown(
        "<p style='text-align:center; color:rgba(240,238,255,0.3); font-size:0.88rem; margin-top:0.5rem;'>"
        "⬆ Upload a resume above to get started</p>",
        unsafe_allow_html=True,
    )

# Analysis Pipeline
if resume_file and analyze_btn:
    suffix = ".pdf" if resume_file.name.lower().endswith(".pdf") else ".docx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name

    try:
        with st.spinner("Parsing resume…"):
            resume_text = extract_text(tmp_path)

        if not resume_text.strip():
            st.error("❌ Could not extract text. The file may be image-based and require OCR.")
            st.stop()

        token_count = count_tokens(resume_text)
        st.caption(f"📝 {len(resume_text):,} characters · {token_count:,} tokens extracted")

        if token_count > 4000:
            resume_text = truncate_text(resume_text, max_tokens=4000)
            st.warning("⚠️ Resume truncated to 4,000 tokens to stay within AI context limits.")

        st.divider()

        with st.spinner("Analysing with AI — this may take a moment…"):
            analysis = analyze_resume(resume_text)

        st.markdown('<div class="section-header">📊  Overall Analysis</div>', unsafe_allow_html=True)

        score   = analysis.get("overall_score", 0)
        summary = analysis.get("summary", "")

        if score >= 85:
            emoji, label, badge_cls = "🟢", "Excellent",  "badge-green"
        elif score >= 70:
            emoji, label, badge_cls = "🟡", "Good",       "badge-yellow"
        elif score >= 50:
            emoji, label, badge_cls = "🟠", "Fair",       "badge-orange"
        else:
            emoji, label, badge_cls = "🔴", "Needs Work", "badge-red"

        score_col, summary_col = st.columns([1, 2.2])

        with score_col:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{score}</div>
                <div class="score-label">Resume Score</div>
                <div class="score-status">
                    <span class="score-badge {badge_cls}">{emoji} {label}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with summary_col:
            st.markdown(f"<p style='font-size:.95rem; line-height:1.7; color:rgba(240,238,255,0.7);'>{summary}</p>", unsafe_allow_html=True)
            st.progress(score / 100)

            skills      = analysis.get("skills_identified", {})
            tech_skills = skills.get("technical", [])
            soft_skills = skills.get("soft", [])

            if tech_skills:
                st.markdown("<div class='section-col-label'>Technical Skills</div>", unsafe_allow_html=True)
                pills = " ".join(f'<span class="pill-blue">{s}</span>' for s in tech_skills[:15])
                st.markdown(pills, unsafe_allow_html=True)

            if soft_skills:
                st.markdown("<div class='section-col-label' style='margin-top:.8rem'>Soft Skills</div>", unsafe_allow_html=True)
                pills = " ".join(f'<span class="pill-purple">{s}</span>' for s in soft_skills[:10])
                st.markdown(pills, unsafe_allow_html=True)

        st.markdown("")
        str_col, weak_col = st.columns(2)

        with str_col:
            st.markdown('<div class="section-col-label" style="color:#22d3a0;">✅ Strengths</div>', unsafe_allow_html=True)
            for s in analysis.get("strengths", []):
                st.markdown(f'<span class="pill-green">✓ {s}</span>', unsafe_allow_html=True)

        with weak_col:
            st.markdown('<div class="section-col-label" style="color:#f87171;">⚠️ Weaknesses</div>', unsafe_allow_html=True)
            for w in analysis.get("weaknesses", []):
                st.markdown(f'<span class="pill-red">✗ {w}</span>', unsafe_allow_html=True)

        missing = analysis.get("missing_sections", [])
        if missing:
            st.markdown("<div class='section-col-label' style='margin-top:1rem'>📋 Missing Sections</div>", unsafe_allow_html=True)
            pills = " ".join(f'<span class="pill-orange">+ {m}</span>' for m in missing)
            st.markdown(pills, unsafe_allow_html=True)

        st.markdown('<div class="section-header">🔝  High-Impact Improvements</div>', unsafe_allow_html=True)
        for i, tip in enumerate(analysis.get("top_3_improvements", []), 1):
            st.markdown(f"""
            <div class="improvement-card">
                <strong>#{i}  Action Item</strong>
                <p style="margin:0.4rem 0 0 0; color:var(--text-primary);">{tip}</p>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("🛠 Detailed Issues & Suggestions", expanded=False):
            quant_gaps  = analysis.get("quantification_gaps", [])
            verb_issues = analysis.get("action_verb_issues", [])
            fmt_issues  = analysis.get("formatting_issues", [])

            if quant_gaps:
                st.markdown("**📏 Bullets Missing Metrics:**")
                for g in quant_gaps: st.markdown(f"- _{g}_")
            if verb_issues:
                st.markdown("**💪 Weak Action Verbs:**")
                for v in verb_issues: st.markdown(f"- _{v}_")
            if fmt_issues:
                st.markdown("**🎨 Formatting Issues:**")
                for f in fmt_issues: st.markdown(f"- _{f}_")
            if not (quant_gaps or verb_issues or fmt_issues):
                st.success("No major issues detected — great job! 🎉")

        if "ATS" in mode and jd_text.strip():
            st.divider()
            st.markdown('<div class="section-header">🤖  ATS Compatibility</div>', unsafe_allow_html=True)

            with st.spinner("Running ATS analysis…"):
                ats     = score_ats(resume_text, jd_text)
                kw_data = keyword_overlap_score(resume_text, jd_text)

            llm_ats   = ats.get("ats_score", 0)
            kw_ats    = kw_data["keyword_score"]
            ats_score = round((llm_ats + kw_ats) / 2)

            ats_col1, ats_col2, ats_col3 = st.columns(3)

            with ats_col1:
                st.markdown(f"""
                <div class="score-card">
                    <div class="score-value">{ats_score}</div>
                    <div class="score-label">Combined ATS Score</div>
                </div>
                """, unsafe_allow_html=True)

            with ats_col2:
                st.markdown(f"""
                <div class="score-card">
                    <div class="score-value" style="font-size:3rem">{llm_ats}</div>
                    <div class="score-label">AI Analysis</div>
                </div>
                """, unsafe_allow_html=True)

            with ats_col3:
                st.markdown(f"""
                <div class="score-card">
                    <div class="score-value" style="font-size:3rem">{kw_ats}</div>
                    <div class="score-label">Keyword Match</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.progress(ats_score / 100)

            kw_col1, kw_col2 = st.columns(2)

            with kw_col1:
                st.markdown('<div class="section-col-label" style="color:#22d3a0">✅ Matched Keywords</div>', unsafe_allow_html=True)
                if kw_data["matched"]:
                    tags = " ".join(f'<span class="keyword-matched">{k}</span>' for k in kw_data["matched"][:25])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.caption("No keyword matches found")

            with kw_col2:
                st.markdown('<div class="section-col-label" style="color:#f87171">❌ Missing Keywords</div>', unsafe_allow_html=True)
                if kw_data["missing"]:
                    tags = " ".join(f'<span class="keyword-missing">{k}</span>' for k in kw_data["missing"][:25])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.success("All important keywords are covered! 🎉")

            recs = ats.get("recommendations", [])
            if recs:
                st.markdown('<div class="section-col-label" style="margin-top:1.2rem">💡 ATS Recommendations</div>', unsafe_allow_html=True)
                for rec in recs:
                    st.markdown(f'<div class="improvement-card">{rec}</div>', unsafe_allow_html=True)

            risks = ats.get("formatting_ats_risks", [])
            if risks:
                with st.expander("⚠️ ATS Formatting Risks"):
                    for r in risks: st.warning(r)

            st.divider()
            st.markdown('<div class="section-header">✍️  Tailored Resume</div>', unsafe_allow_html=True)
            st.caption("Rewritten to match the job description — no fabricated experience added")

            with st.spinner("Rewriting your resume for this role — please wait…"):
                tailored = tailor_resume(resume_text, jd_text)

            st.text_area("Tailored Resume", tailored, height=400, label_visibility="visible")

            st.download_button(
                "⬇  Download Tailored Resume (.txt)",
                data=tailored,
                file_name="tailored_resume.txt",
                mime="text/plain",
                use_container_width=True,
            )

        elif "ATS" in mode and not jd_text.strip():
            st.divider()
            st.warning("📋 Paste a job description in the panel above to unlock ATS scoring and resume tailoring.")

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.caption("Please check your API key in .env and try again.")

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
