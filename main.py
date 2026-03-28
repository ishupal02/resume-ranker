import streamlit as st
import tempfile
import os
import time
from resume_parser import extract_text_from_pdf, extract_text_from_txt, get_candidate_name
from similarity_model import rank_resumes

# Page Configuration
st.set_page_config(
    page_title="AI Resume Ranker Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ultra Premium CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

* {
    font-family: 'Inter', sans-serif;
}

.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    min-height: 100vh;
    padding: 2rem 0;
}

.hero-section {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 30px;
    padding: 3rem;
    margin: 2rem 0;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.main-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 1rem;
    animation: glow 2s ease-in-out infinite alternate;
}

.subtitle {
    font-size: 1.3rem;
    color: #64748b;
    text-align: center;
    font-weight: 500;
    margin-bottom: 2rem;
}

.card-premium {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 25px;
    padding: 2.5rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.card-premium::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
}

.card-premium:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.2);
}

.section-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.btn-premium {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    color: white !important;
    border: none;
    border-radius: 15px;
    padding: 1rem 2.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
}

.btn-premium:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
}

.btn-premium:active {
    transform: translateY(-1px);
}

.file-upload-zone {
    border: 3px dashed #cbd5e1;
    border-radius: 20px;
    padding: 3rem;
    text-align: center;
    background: rgba(255, 255, 255, 0.7);
    transition: all 0.3s ease;
    cursor: pointer;
}

.file-upload-zone:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
}

.uploaded-file {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 15px;
    margin: 0.5rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
}

.stat-number {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 1rem;
    opacity: 0.9;
}

.results-table {
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}

.rank-badge {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 50px;
    font-weight: 700;
    font-size: 0.9rem;
}

.score-badge {
    padding: 0.5rem 1.5rem;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1rem;
}

.score-excellent { background: linear-gradient(135deg, #10b981, #059669); color: white; }
.score-good { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
.score-fair { background: linear-gradient(135deg, #f97316, #ea580c); color: white; }
.score-poor { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; }

.chart-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 25px;
    padding: 2.5rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.loading-animation {
    text-align: center;
    padding: 3rem;
}

.loading-spinner {
    border: 4px solid #f3f4f6;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes glow {
    from { filter: drop-shadow(0 0 5px #667eea); }
    to { filter: drop-shadow(0 0 20px #667eea); }
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(50px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.slide-in {
    animation: slideInUp 0.6s ease-out;
}
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="main-title">🚀 AI Resume Ranker Pro</div>
    <div class="subtitle">The Ultimate Resume Screening Tool Powered by Advanced NLP & Machine Learning</div>
    <div style="text-align: center; margin-top: 2rem;">
        <i class="fas fa-brain" style="font-size: 3rem; color: #667eea; margin: 0 1rem;"></i>
        <i class="fas fa-chart-line" style="font-size: 3rem; color: #764ba2; margin: 0 1rem;"></i>
        <i class="fas fa-rocket" style="font-size: 3rem; color: #f093fb; margin: 0 1rem;"></i>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Job Description
with st.sidebar:
    st.markdown("""
    <div class="card-premium">
        <div class="section-title">
            <i class="fas fa-file-alt"></i>
            Job Description
        </div>
    """, unsafe_allow_html=True)
    
    job_desc_input = st.text_area(
        "",
        height=400,
        placeholder="📝 Paste your job description here...\n\nInclude key skills, experience requirements, and qualifications for optimal matching.",
        label_visibility="collapsed"
    )
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 1rem; border-radius: 15px; margin-top: 1rem;">
            <i class="fas fa-lightbulb" style="color: #3b82f6;"></i>
            <strong> Pro Tip:</strong> More specific keywords = Better matching!
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main Content
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <div class="card-premium">
        <div class="section-title">
            <i class="fas fa-cloud-upload-alt"></i>
            Upload Resumes
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Drag & drop or click to upload PDF/TXT resumes"
    )
    
    if uploaded_files:
        st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div style="color: #10b981; font-size: 1.2rem; font-weight: 600;">
                    <i class="fas fa-check-circle"></i> {len(uploaded_files)} files ready!
                </div>
        """, unsafe_allow_html=True)
        
        for file in uploaded_files:
            st.markdown(f"""
                <div class="uploaded-file">
                    <span><i class="fas fa-file-pdf"></i> {file.name}</span>
                    <i class="fas fa-check" style="font-size: 1.2rem;"></i>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if uploaded_files:
        st.markdown("""
        <div class="card-premium">
            <div class="section-title">
                <i class="fas fa-chart-bar"></i>
                Quick Stats
            </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{len(uploaded_files)}</div>
                    <div class="stat-label">Resumes</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown("""
                <div class="stat-card">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Ready</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Analyze Button
st.markdown('<div style="text-align: center; margin: 3rem 0;">', unsafe_allow_html=True)
analyze_button = st.button("🚀 Analyze & Rank Resumes", key="analyze", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Results Section
if analyze_button:
    if not job_desc_input.strip():
        st.error("⚠️ Please enter a job description first!")
        st.stop()
    
    if not uploaded_files:
        st.error("⚠️ Please upload at least one resume!")
        st.stop()
    
    # Loading Animation
    st.markdown("""
    <div class="loading-animation">
        <div class="loading-spinner"></div>
        <h3>🔍 Analyzing Resumes with AI...</h3>
        <p>Processing text extraction, TF-IDF vectorization, and similarity matching</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Simulate processing time
    time.sleep(2)
    st.experimental_rerun()
    
    # Process files
    resume_texts = []
    candidate_names = []
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        if uploaded_file.name.endswith('.pdf'):
            text = extract_text_from_pdf(tmp_path)
        else:
            text = extract_text_from_txt(tmp_path)
        
        os.remove(tmp_path)
        
        if text:
            resume_texts.append(text)
            candidate_names.append(get_candidate_name(uploaded_file))
    
    if resume_texts:
        ranking_df = rank_resumes(job_desc_input, resume_texts, candidate_names)
        
        # Results Header
        st.markdown("""
        <div class="card-premium">
            <div class="section-title">
                <i class="fas fa-trophy"></i>
                Top Candidates Ranked
            </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Results Table
        for idx, row in ranking_df.iterrows():
            score_class = "score-excellent" if row['Match Score'] >= 80 else "score-good" if row['Match Score'] >= 60 else "score-fair" if row['Match Score'] >= 40 else "score-poor"
            
            st.markdown(f"""
            <div class="candidate-card" style="margin-bottom: 1rem; padding: 1.5rem; border-radius: 15px; border-left: 5px solid #667eea;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="rank-badge">#{row['Rank']}</span>
                        <h3 style="margin: 0.5rem 0 0 0; font-size: 1.3rem;">{row['Candidate']}</h3>
                    </div>
                    <div class="score-badge {score_class}" style="min-width: 80px;">
                        {row['Match Score']}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Metrics
        st.markdown("""
        <div class="card-premium">
            <div class="section-title">
                <i class="fas fa-chart-pie"></i>
                Performance Overview
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Candidates", len(ranking_df))
        with col2:
            st.metric("Best Match", f"{ranking_df['Match Score'].max():.0f}%")
        with col3:
            st.metric("Average Score", f"{ranking_df['Match Score'].mean():.0f}%")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Chart
        st.markdown("""
        <div class="card-premium chart-container">
            <div class="section-title">
                <i class="fas fa-chart-bar"></i>
                Match Score Distribution
            </div>
        """, unsafe_allow_html=True)
        
        chart_data = ranking_df.set_index("Candidate")["Match Score"]
        st.bar_chart(chart_data, height=400)
        
        # Download
        csv = ranking_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv,
            file_name="resume_ranking_pro.csv",
            mime="text/csv"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; color: rgba(255,255,255,0.8);">
    <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">
        <i class="fas fa-heart" style="color: #ef4444;"></i>
        Made with ❤️ using Streamlit + AI
    </div>
    <div style="font-size: 0.9rem;">
        TF-IDF • Cosine Similarity • NLP Processing
    </div>
</div>
""", unsafe_allow_html=True)