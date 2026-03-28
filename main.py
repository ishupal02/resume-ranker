import streamlit as st
import tempfile
import os
from resume_parser import extract_text_from_pdf, extract_text_from_txt, get_candidate_name
from similarity_model import rank_resumes

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
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Header Styles */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Card Styles */
    .card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* File Upload */
    .stFileUploader {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Divider */
    .section-divider {
        border: none;
        border-top: 2px solid #e0e0e0;
        margin: 2rem 0;
    }
    
    /* Score Badges */
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .score-high {
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        color: white;
    }
    
    .score-medium {
        background: linear-gradient(90deg, #f39c12, #e67e22);
        color: white;
    }
    
    .score-low {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        color: white;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Table Styles */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .loading-pulse {
        animation: pulse 1.5s infinite;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Success/Error Messages */
    .success-message {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border: 1px solid #4caf50;
        border-radius: 10px;
        padding: 1rem;
        color: #2e7d32;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border: 1px solid #f44336;
        border-radius: 10px;
        padding: 1rem;
        color: #c62828;
    }
    
    /* Chart Container */
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Download Button */
    .download-btn {
        background: linear-gradient(90deg, #4caf50, #45a049);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
    }
    
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(76, 175, 80, 0.6);
    }
    
    /* Candidate Card */
    .candidate-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }
    
    .candidate-name {
        font-weight: 600;
        color: #333;
    }
    
    .candidate-score {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Title Section
st.markdown('<div class="main-header">🤖 AI Resume Ranker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional Resume Screening Powered by NLP & Machine Learning</div>', unsafe_allow_html=True)

# Decorative Elements
st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <span style="font-size: 2rem;">✨</span>
        <span style="font-size: 2rem;">📊</span>
        <span style="font-size: 2rem;">🎯</span>
    </div>
""", unsafe_allow_html=True)

# Sidebar for Job Description
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 1rem;">📋</div>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #333;">Job Description</h3>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    job_desc_input = st.text_area(
        "Paste Job Description",
        height=350,
        placeholder="Enter the job description text here...\n\nExample:\nWe are looking for a Python Developer with 3+ years of experience in web development, Django, REST APIs, and database management...",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("""
        <div class="info-box">
            <strong>💡 Pro Tip:</strong> Include key skills, requirements, and qualifications for better matching!
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <strong>Powered by:</strong><br>
            TF-IDF • Cosine Similarity • NLP
        </div>
    """, unsafe_allow_html=True)

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-header">📁 Upload Resumes</div>', unsafe_allow_html=True)
    st.markdown("**Step 2:** Upload candidate resumes (PDF or TXT files)")
    
    # File Upload Section
    uploaded_files = st.file_uploader(
        "Select Resume Files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

with col2:
    st.markdown('<div class="section-header">📊 Quick Stats</div>', unsafe_allow_html=True)
    
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
                        <div class="metric