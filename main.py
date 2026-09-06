import streamlit as st
import tempfile
import os
import pandas as pd
from resume_parser import extract_text_from_pdf, extract_text_from_txt, get_candidate_name
from similarity_model import rank_resumes
from ats_checker import analyze_resume

# Page Configuration
st.set_page_config(
    page_title="AI Resume Ranker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': "https://github.com",
        'About': "🤖 AI Resume Ranker - Professional Resume Screening Tool"
    }
)

# Custom CSS for Premium Styling
st.markdown("""
    <style>
    :root {
        --ink: #17221f;
        --muted: #66736e;
        --paper: #f5f7f2;
        --panel: #ffffff;
        --line: #dfe7df;
        --teal: #126b68;
        --coral: #e36f51;
    }
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 8% 0%, #e6f2ee 0, transparent 32%), var(--paper);
    }
    [data-testid="stHeader"] { background: transparent; }
    .main .block-container { max-width: 1180px; padding-top: 2.5rem; }
    .main-header {
        color: var(--ink);
        font-size: clamp(2.2rem, 5vw, 4.6rem);
        letter-spacing: -0.04em;
        line-height: 0.95;
        text-align: left;
        margin-bottom: 0.7rem;
    }
    .eyebrow { color: var(--coral); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.16em; margin-bottom: 0.8rem; }
    .sidebar-mark { color: var(--coral); font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; line-height: 1; margin-bottom: 0.4rem; }
    .sub-header { color: var(--muted); text-align: left; max-width: 650px; margin-bottom: 2.5rem; }
    .card, .candidate-card, .chart-container {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(23, 34, 31, 0.06);
    }
    .card { padding: 1.4rem; }
    .candidate-card { padding: 0.9rem 1rem; border-left: 4px solid var(--teal); }
    .candidate-name, .section-header { color: var(--ink); }
    .section-header { font-size: 1.25rem; font-weight: 700; }
    .metric-card { background: var(--teal); border-radius: 12px; padding: 1.2rem; box-shadow: none; }
    .stButton > button[kind="primary"] { background: var(--coral); border: 0; border-radius: 8px; }
    .stButton > button[kind="primary"]:hover { background: #c9573c; }
    .stFileUploader, [data-testid="stSidebar"] { background: rgba(255,255,255,0.72); }
    .info-box { background: var(--ink); border-left: 4px solid var(--coral); border-radius: 8px; padding: 1rem; }
    .ats-good { color: #16704f; font-weight: 700; }
    .ats-warn { color: #b15a20; font-weight: 700; }
    .keyword-chip { display: inline-block; background: #e6f2ee; color: var(--teal); border-radius: 999px; padding: 0.25rem 0.55rem; margin: 0.15rem; font-size: 0.8rem; }

    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    * { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3, .main-header { font-family: 'Space Grotesk', sans-serif; }
    .main { min-height: 100vh; }
    .main-header { animation: fadeInDown 0.7s ease-out; }
    .sub-header { font-size: 1.05rem; line-height: 1.6; animation: fadeInUp 0.7s ease-out; }
    .card { margin-bottom: 1.5rem; transition: transform 0.2s ease, box-shadow 0.2s ease; }
    .card:hover { transform: translateY(-3px); box-shadow: 0 16px 38px rgba(23, 34, 31, 0.10); }
    .section-divider { border: 0; border-top: 1px solid var(--line); margin: 2.5rem 0; }
    .stFileUploader { border: 1px dashed #9bbab0; border-radius: 12px; padding: 1rem; background: rgba(255,255,255,0.78); }
    .stButton > button { background: var(--teal); color: white; border: 0; border-radius: 8px; padding: 0.7rem 1.4rem; font-weight: 700; box-shadow: 0 8px 18px rgba(18,107,104,0.20); }
    .stButton > button:hover { background: #0e5553; transform: translateY(-1px); }
    .stButton > button[kind="primary"] { background: var(--coral); box-shadow: 0 8px 18px rgba(227,111,81,0.25); }
    .stButton > button[kind="primary"]:hover { background: #c9573c; }
    .metric-card { min-height: 96px; display: flex; flex-direction: column; justify-content: center; }
    .metric-value { font-family: 'Space Grotesk', sans-serif; }
    .stDataFrame { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
    .success-message, .error-message { border-radius: 10px; padding: 0.9rem 1rem; }
    .success-message { background: #e7f4ed; border: 1px solid #9bd0b2; color: #17613f; }
    .error-message { background: #fff0ed; border: 1px solid #e7a292; color: #9b3d2b; }
    [data-testid="stSidebar"] { border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] h3 { font-family: 'Space Grotesk', sans-serif; color: var(--ink) !important; }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-18px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
    @media (max-width: 700px) {
        .main .block-container { padding-top: 1.4rem; }
        .main-header { font-size: 2.7rem; }
        .sub-header { font-size: 0.95rem; }
        .section-divider { margin: 1.5rem 0; }
    }
    </style>
""", unsafe_allow_html=True)

# Title Section
st.markdown('<div class="eyebrow">RESUME INTELLIGENCE LAB</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header">Find the resume<br><span style="color: var(--coral);">that fits the role.</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Rank candidates, check ATS readiness, and get practical resume edits from one focused workspace.</div>', unsafe_allow_html=True)

# Sidebar for Job Description
with st.sidebar:
    st.markdown('<div class="sidebar-mark">01</div>', unsafe_allow_html=True)
    st.markdown('<h3>Role brief</h3>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    job_desc_input = st.text_area(
        "Paste the job description",
        height=350,
        placeholder="Enter the job description text here...\n\nExample:\nWe are looking for a Python Developer with 3+ years of experience in web development, Django, REST APIs, and database management...",
        label_visibility="visible"
    )

    scoring_mode = st.selectbox(
        "ATS scoring mode",
        ["Balanced", "Keyword focus", "Structure focus"],
        help="Choose whether the score should emphasize job keywords or resume structure."
    )
    show_resume_preview = st.checkbox("Show extracted resume text", value=False)
    
    st.markdown("---")
    
    st.markdown("""
        <div class="info-box">
            <strong>Better matching:</strong> Include skills, tools, seniority, and must-have requirements.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <strong>Analysis stack</strong><br>
            TF-IDF &nbsp;•&nbsp; ATS signals &nbsp;•&nbsp; NLP
        </div>
    """, unsafe_allow_html=True)

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="eyebrow">02 / CANDIDATE FILES</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Bring the resumes into focus</div>', unsafe_allow_html=True)
    st.markdown("Upload one or more PDF or TXT resumes. We will rank them against the role brief and surface specific edits.")
    
    # File Upload Section
    uploaded_files = st.file_uploader(
        "Select Resume Files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

with col2:
    st.markdown('<div class="eyebrow">LIVE QUEUE</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Ready to review</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(uploaded_files)}</div>
                <div class="metric-label">Resumes Uploaded</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("**Uploaded Files:**")
        for file in uploaded_files:
            st.markdown(f"""
                <div class="candidate-card">
                    <div class="candidate-name">📄 {file.name}</div>
                    <div class="candidate-score">Ready for analysis</div>
                </div>
            """, unsafe_allow_html=True)

# Divider
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# Analyze Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button(
        "🔍 Analyze Resumes",
        type="primary",
        use_container_width=True,
        help="Click to rank resumes based on job description"
    )

# Results Section
if analyze_button:
    # Validation
    if not job_desc_input:
        st.markdown("""
            <div class="error-message">
                <strong>❌ Error:</strong> Please enter a Job Description in the sidebar.
            </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    if not uploaded_files:
        st.markdown("""
            <div class="error-message">
                <strong>❌ Error:</strong> Please upload at least one Resume file.
            </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Processing Indicator
    with st.spinner("⏳ Analyzing resumes..."):
        resume_texts = []
        candidate_names = []
        resume_analyses = []
        
        for uploaded_file in uploaded_files:
            # Save uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Extract text based on file type
            if uploaded_file.name.endswith('.pdf'):
                text = extract_text_from_pdf(tmp_path)
            else:
                text = extract_text_from_txt(tmp_path)
            
            # Clean up temporary file
            os.remove(tmp_path)
            
            # Store data
            if text:
                resume_texts.append(text)
                candidate_names.append(get_candidate_name(uploaded_file))
                resume_analyses.append(analyze_resume(job_desc_input, text, scoring_mode))
        
        # Run the Ranking Model
        if resume_texts:
            try:
                ranking_df = rank_resumes(job_desc_input, resume_texts, candidate_names)
                
                # Success Message
                st.markdown("""
                    <div class="success-message">
                        <strong>✅ Success!</strong> Analysis completed successfully!
                    </div>
                """, unsafe_allow_html=True)
                
                # Results Header
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">📊 Ranked Results</div>', unsafe_allow_html=True)
                
                # Display Results Table
                st.dataframe(
                    ranking_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                        "Candidate": st.column_config.TextColumn("Candidate"),
                        "Match Score": st.column_config.NumberColumn(
                            "Match Score", 
                            format="%d%%",
                            help="Similarity score with job description"
                        )
                    }
                )
                
                # Summary Statistics
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">📈 Performance Metrics</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{ranking_df['Match Score'].max()}%</div>
                            <div class="metric-label">Best Match</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{ranking_df['Match Score'].mean():.1f}%</div>
                            <div class="metric-label">Average Score</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{len(ranking_df)}</div>
                            <div class="metric-label">Total Candidates</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

                # Top Candidate Highlight
                top_candidate = ranking_df.iloc[0]

                st.markdown(f"""
                    <div class="card">
                        <h3>🏆 Top Candidate</h3>
                        <p><strong>Name:</strong> {top_candidate['Candidate']}</p>
                        <p><strong>Match Score:</strong> {top_candidate['Match Score']}%</p>
                        <p>This candidate best matches the job description based on AI similarity analysis.</p>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">🧭 ATS Resume Health</div>', unsafe_allow_html=True)
                st.caption("A practical checklist based on the job description and the resume text. ATS scores are guidance, not a hiring decision.")

                candidate_tabs = st.tabs([name for name in candidate_names])
                for resume_index, (tab, candidate_name, ats) in enumerate(zip(candidate_tabs, candidate_names, resume_analyses)):
                    with tab:
                        score_class = "ats-good" if ats["ats_score"] >= 70 else "ats-warn"
                        st.markdown(f"<h3 class='{score_class}'>ATS readiness: {ats['ats_score']} / 100</h3>", unsafe_allow_html=True)
                        score_cols = st.columns(4)
                        for score_col, label, value in zip(
                            score_cols,
                            ["Keyword match", "Sections", "Contact", "Word count"],
                            [f"{ats['keyword_score']}%", f"{ats['section_score']}%", f"{ats['contact_score']}%", str(ats['word_count'])],
                        ):
                            with score_col:
                                st.metric(label, value)

                        detail_col, suggestion_col = st.columns(2)
                        with detail_col:
                            st.markdown("**Matched job terms**")
                            if ats["matched_keywords"]:
                                chips = "".join(f"<span class='keyword-chip'>{term}</span>" for term in ats["matched_keywords"][:18])
                                st.markdown(chips, unsafe_allow_html=True)
                            else:
                                st.info("No strong keyword overlap found yet.")
                            st.markdown("**Terms to consider adding**")
                            st.write(", ".join(ats["missing_keywords"][:12]) or "No major gaps detected.")
                        with suggestion_col:
                            st.markdown("**Add or remove**")
                            for suggestion in ats["suggestions"]:
                                st.markdown(f"- {suggestion}")
                            if ats["repeated_words"]:
                                st.markdown("**Repeated words**")
                                st.dataframe(
                                    pd.DataFrame(ats["repeated_words"], columns=["Word", "Frequency"]),
                                    hide_index=True,
                                    use_container_width=True,
                                )
                        if show_resume_preview:
                            with st.expander("View extracted resume text"):
                                st.text_area(
                                    "Extracted text",
                                    resume_texts[resume_index],
                                    height=240,
                                    key=f"preview_{resume_index}",
                                )

                # Score Visualization
                st.markdown('<div class="section-header">📊 Score Visualization</div>', unsafe_allow_html=True)

                import altair as alt

                chart = alt.Chart(ranking_df).mark_bar().encode(
                    x='Candidate',
                    y='Match Score',
                    tooltip=['Candidate', 'Match Score']
                ).properties(
                    height=400
                )

                st.altair_chart(chart, use_container_width=True)

                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

                # Download Results
                st.markdown('<div class="section-header">⬇️ Download Results</div>', unsafe_allow_html=True)

                csv = ranking_df.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="📥 Download Ranking Report",
                    data=csv,
                    file_name="resume_ranking_results.csv",
                    mime="text/csv"
                )

                ats_report = pd.DataFrame([
                    {
                        "Candidate": candidate_name,
                        "ATS Score": ats["ats_score"],
                        "Keyword Match": ats["keyword_score"],
                        "Section Score": ats["section_score"],
                        "Contact Score": ats["contact_score"],
                        "Word Count": ats["word_count"],
                        "Missing Keywords": ", ".join(ats["missing_keywords"]),
                        "Repeated Words": ", ".join(f"{word} ({count}x)" for word, count in ats["repeated_words"]),
                        "Suggestions": " | ".join(ats["suggestions"]),
                    }
                    for candidate_name, ats in zip(candidate_names, resume_analyses)
                ])
                st.download_button(
                    label="Download detailed ATS report",
                    data=ats_report.to_csv(index=False).encode("utf-8"),
                    file_name="resume_ats_report.csv",
                    mime="text/csv",
                )

            except Exception as e:
                st.markdown(f"""
                    <div class="error-message">
                        <strong>❌ Error during analysis:</strong> {str(e)}
                    </div>
                """, unsafe_allow_html=True)

        else:
            st.markdown("""
                <div class="error-message">
                    <strong>❌ Error:</strong> Could not extract text from uploaded resumes.
                </div>
            """, unsafe_allow_html=True)