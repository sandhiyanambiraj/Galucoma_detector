import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import time
import json
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Eye Pressure & Glaucoma Detector",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with Premium Design + Animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Professional medical background with eye hospital image */
    .stApp {
        background: 
            linear-gradient(rgba(10, 25, 47, 0.92), rgba(20, 40, 70, 0.92)),
            url('https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1920') center/cover fixed;
        padding: 1rem;
        min-height: 100vh;
    }
    
    /* Compact main content container */
    .block-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(40px) saturate(180%);
        border-radius: 25px;
        padding: 1.5rem !important;
        max-width: 700px !important;
        margin: 0 auto !important;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        border: 3px solid blue;
        animation: containerSlideIn 0.8s ease-out;
    }
    
    @keyframes containerSlideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Header styling - more compact */
    .header-container {
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 1.5rem 1rem;
        background: linear-gradient(135deg, rgba(13, 102, 161, 255), rgba(25, 118, 210, 0.08));
        border-radius: 18px;
        border: 1px solid rgba(13, 71, 161, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: rotate(45deg) translateX(-100%); }
        100% { transform: rotate(45deg) translateX(100%); }
    }
    
    .header-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 50%, #42a5f5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
        position: relative;
        animation: titleGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        from { text-shadow: 0 0 20px rgba(13, 71, 161, 0.3); }
        to { text-shadow: 0 0 30px rgba(13, 71, 161, 0.6), 0 0 40px rgba(13, 71, 161, 0.4); }
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #1565c0;
        font-weight: 500;
        animation: subtitleFadeIn 1s ease-out 0.5s both;
    }
    
    @keyframes subtitleFadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Compact premium card */
    .premium-card {
        background: linear-gradient(135deg,  skyblue, rgba(225, 101, 255, 0.008));
        border-radius: 10px;
        padding: 1rem;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border: 1px solid  rgba(13, 102, 161, 255);
        animation: cardSlideUp 0.6s ease-out;
    }
    
    @keyframes cardSlideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .premium-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px rgba(13, 71, 161, 0.2);
    }
    
    /* Animated warning box */
    .warning {
        background: linear-gradient(135deg, rgba(25, 118, 210, 0.12), rgba(66, 165, 245, 0.12));
        border: 1px solid rgba(25, 118, 210, 0.3);
        border-radius: 14px;
        padding: 1.2rem;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 6px 20px gba(25, 118, 210, 0.12);
        animation: pulseWarning 2s infinite;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes pulseWarning {
        0% { box-shadow: 0 6px 20px rgba(25, 118, 210, 0.12); }
        50% { box-shadow: 0 6px 30px rgba(25, 118, 210, 0.25); }
        100% { box-shadow: 0 6px 20px rgba(25, 118, 210, 0.12); }
    }
    
    .warning strong {
        color: #0d47a1;
        font-size: 1.05rem;
        font-weight: 700;
    }
    
    /* Premium button with animation */
    .stButton > button {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.9rem 2rem !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
        box-shadow: 0 8px 25px rgba(13, 71, 161, 0.25) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(13, 71, 161, 0.4) !important;
        background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%) !important;
    }
    
    /* Download button with animation */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.85rem 1.8rem !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 8px 25px rgba(46, 125, 50, 0.25) !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(46, 125, 50, 0.4) !important;
    }
    
    /* Enhanced result boxes */
    .result-box {
        border-radius: 18px;
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        border: 3px solid;
        animation: resultSlideIn 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .result-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
        animation: scanningLine 2s infinite;
    }
    
    @keyframes scanningLine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @keyframes resultSlideIn {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    .risk-normal {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.15), rgba(56, 142, 60, 0.15));
        border-color: #2e7d32;
    }
    
    .risk-high {
        background: linear-gradient(135deg, rgba(211, 47, 47, 0.15), rgba(244, 67, 54, 0.15));
        border-color: #d32f2f;
        animation: pulseHighRisk 2s infinite;
    }
    
    @keyframes pulseHighRisk {
        0% { box-shadow: 0 12px 40px rgba(211, 47, 47, 0.15); }
        50% { box-shadow: 0 12px 50px rgba(211, 47, 47, 0.3); }
        100% { box-shadow: 0 12px 40px rgba(211, 47, 47, 0.15); }
    }
    
    /* Progress bar enhancements */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0d47a1 0%, #1976d2 50%, #42a5f5 100%);
        border-radius: 10px;
        animation: progressShimmer 2s infinite;
    }
    
    @keyframes progressShimmer {
        0% { background-position: -200px 0; }
        100% { background-position: 200px 0; }
    }
    
    /* GIF container */
    .gif-container {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
        margin: 1.5rem 0;
        border: 2px solid rgba(255, 255, 255, 0.3);
        animation: gifFloat 3s ease-in-out infinite;
    }
    
    @keyframes gifFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Floating elements */
    .floating {
        animation: floating 3s ease-in-out infinite;
    }
    
    @keyframes floating {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }
    
    /* Enhanced tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.8rem;
        background: rgba(13, 71, 161, 0.05);
        padding: 0.4rem;
        border-radius: 14px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background: rgba(255, 255, 255, 0.85);
        border-radius: 10px;
        padding: 0px 25px;
        font-weight: 600;
        font-size: 1.05rem;
        color: #0d47a1;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
        color: white !important;
        box-shadow: 0 6px 20px rgba(13, 71, 161, 0.3);
        transform: translateY(-2px);
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(240, 240, 240, 0.9));
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(13, 71, 161, 0.1);
        transition: all 0.3s ease;
        animation: statCardAppear 0.6s ease-out;
    }
    
    @keyframes statCardAppear {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .stat-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Reduce top padding */
    .main > div {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class EyePressureDetector:
    def __init__(self):
        self.api_base = "http://127.0.0.1:8000"
        
        # Initialize session state
        if 'show_camera' not in st.session_state:
            st.session_state.show_camera = False
        if 'camera_photo_taken' not in st.session_state:
            st.session_state.camera_photo_taken = None
        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None
        if 'analysis_complete' not in st.session_state:
            st.session_state.analysis_complete = False
        
    def check_api_status(self):
        """Check if backend API is running"""
        try:
            response = requests.get(f"{self.api_base}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def analyze_image(self, image_file):
        """Send image to backend for analysis"""
        try:
            # Convert to bytes if needed
            if isinstance(image_file, Image.Image):
                img_byte_arr = io.BytesIO()
                image_file.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)
                file_data = img_byte_arr.getvalue()
            else:
                image_file.seek(0)
                file_data = image_file.read()
            
            files = {"file": ("image.jpg", file_data, "image/jpeg")}
            response = requests.post(
                f"{self.api_base}/api/analyze-eye",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: Status {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
            return None

    def generate_text_report(self, result):
        """Generate a detailed text report"""
        risk_level = result['analysis_result'].get('risk_level', 'Unknown')
        confidence = result['analysis_result'].get('confidence', 0)
        probabilities = result['analysis_result'].get('probabilities', [0.33, 0.33, 0.34])
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           GLAUCOMA DETECTION ANALYSIS REPORT                 ║
╚══════════════════════════════════════════════════════════════╝

Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

═══════════════════════════════════════════════════════════════
ANALYSIS RESULTS
═══════════════════════════════════════════════════════════════

Risk Level: {risk_level}
Confidence: {confidence:.1%}

───────────────────────────────────────────────────────────────
RISK PROBABILITIES
───────────────────────────────────────────────────────────────

• Normal:            {probabilities[0]:.1%}
• Early Glaucoma:    {probabilities[1]:.1%}
• Advanced Glaucoma: {probabilities[2]:.1%}

───────────────────────────────────────────────────────────────
RECOMMENDATIONS
───────────────────────────────────────────────────────────────

"""
        recommendations = result.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
───────────────────────────────────────────────────────────────
⚠️DISCLAIMER
───────────────────────────────────────────────────────────────

This  tool is designed for screening purposes only and 
should not replace professional medical advice, diagnosis, or 
treatment. Always seek the advice of qualified healthcare 
providers with any questions regarding a medical condition.

═══════════════════════════════════════════════════════════════
End of Report
═══════════════════════════════════════════════════════════════
"""
        return report

    def display_animated_header(self):
        """Display animated header with GIF-like effects"""
        st.markdown("""
        <div class="header-container">
            <div class="header-title">🔬 AI Glaucoma Detector</div>
        </div>
        """, unsafe_allow_html=True)       
    def display_ai_scanning_gif(self):
        """Display AI scanning animation"""
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #1e3c72;"> Scanning in Progress</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create an animated scanning visualization
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="gif-container">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
                    <div style="height: 4px; background: linear-gradient(90deg, transparent, white, transparent); 
                                animation: scanningLine 1.5s infinite; margin: 1rem 0;"></div>
                    <p style="color: white; font-weight: 600; margin: 0;">Analyzing Retinal Patterns</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def run(self):
        # Display animated header
        self.display_animated_header()
        
        # Warning message with animation
        st.markdown("""
        <div class="warning">
            <strong>⚠️ IMPORTANT: Upload Only Fundus Images</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Input method selection
        tab1, tab2 = st.tabs([" Camera Capture", " Upload Image"])
        
        with tab1:
            st.markdown("""
            <div class="premium-card">
                <h3 style="color: #1e3c72; text-align: center; margin-bottom: 1rem;"> Capture Eye Image</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Camera guidance with animations
            st.markdown("""
            <div class="camera-guidance">
                <h4 style="color: #1e3c72; margin-bottom: 1rem;"> Photography Guidelines:</h4>
                <ul style="color: #1e3c72; line-height: 1.8;">
                    <li> Position your eye in the center of the frame</li>
                    <li> Ensure bright, even lighting without shadows</li>
                    <li> Keep your eye fully open and relaxed</li>
                    <li> Hold the device steady and maintain focus</li>
                    <li> Capture a clear, high-quality fundus image</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to show camera
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(" Open Camera", key="open_camera_btn", use_container_width=True):
                    st.session_state.show_camera = True
                    st.rerun()
            
            # Show camera only after button click
            if st.session_state.show_camera:
                st.markdown("---")
                camera_photo = st.camera_input(" Take your photo now", key="camera")
                
                if camera_photo is not None:
                    st.session_state.camera_photo_taken = camera_photo
                    st.session_state.show_camera = False
                    st.rerun()
            
            # Display captured photo and analyze
            if st.session_state.camera_photo_taken is not None:
                self.process_analysis(st.session_state.camera_photo_taken, "camera")
        
        with tab2:
            st.markdown("""
            <div class="premium-card">
                <h3 style="color: #1e3c72; text-align: center;">📂 Upload Fundus Image</h3>
                <p style="text-align: center; color: #666; margin-top: 0.5rem;">
                    Drag and drop or browse • Limit 200MB • PNG, JPG, JPEG
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose a fundus image",
                type=['png', 'jpg', 'jpeg'],
                label_visibility="collapsed",
                key="file_uploader"
            )
            
            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file
                self.process_analysis(uploaded_file, "upload")
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; background: rgba(30, 60, 114, 0.05); border-radius: 16px; margin: 2rem 0;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;" class="floating"></div>
                    <h3 style="color: #1e3c72;">No Image Uploaded Yet</h3>
                    <p style="color: #666; font-size: 1.1rem;">
                        Upload a fundus image above to  analysis
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    def process_analysis(self, image_file, source):
        """Process the uploaded image"""
        image = Image.open(image_file)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #1e3c72;"> Image Preview & Analysis</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="image-preview">', unsafe_allow_html=True)
            st.image(image, caption="Your Fundus Image", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="premium-card">
                <h4 style="color: #1e3c72; margin-bottom: 1rem;"> Image Details</h4>
            """, unsafe_allow_html=True)
            st.write(f"**Format:** {image.format if image.format else 'JPEG'}")
            st.write(f"**Dimensions:** {image.size[0]} × {image.size[1]} px")
            st.write(f"**Mode:** {image.mode}")
            
            # Calculate file size
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            file_size = len(img_byte_arr.getvalue()) / 1024
            st.write(f"**Size:** {file_size:.2f} KB")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Check API
        if not self.check_api_status():
            st.error("""
            🔴 **Analysis Service Unavailable**
            
            The backend service is currently offline. Please:
            - Verify the backend server is running on http://127.0.0.1:8000
            - Check your network connection
            - Retry after a few moments
            """)
            return
        
        # Analyze button
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        analyze_key = f"analyze_btn_{source}"
        if st.button(" Start  Analysis", type="primary", use_container_width=True, key=analyze_key):
            with st.spinner(""):
                # Show scanning animation
                self.display_ai_scanning_gif()
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_messages = [
                    " Initializing AI model...",
                    " Analyzing retinal features...",
                    " Computing risk probabilities...",
                    " Evaluating image quality...",
                    " Generating final report..."
                ]
                
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                    status_text.markdown(f"<h4 style='text-align: center; color: #1e3c72;'>{status_messages[i // 20]}</h4>", unsafe_allow_html=True)
                
                # Convert image_file to proper format
                result = self.analyze_image(image_file)
                
                progress_bar.empty()
                status_text.empty()
                
                if result:
                    st.session_state.analysis_complete = True
                    self.display_results(result, image)
                else:
                    st.error("❌ Analysis failed. Please try again with a different image.")

    def display_results(self, result, image):
        """Display analysis results"""
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #1e3c72;"> Analysis Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if 'analysis_result' not in result:
            st.error("Invalid response format from server")
            return
            
        risk_level = result['analysis_result'].get('risk_level', 'Unknown')
        confidence = result['analysis_result'].get('confidence', 0)
        
        if risk_level.lower() in ["normal", "low"]:
            risk_class = "risk-normal"
            result_text = "✅ NORMAL - NO GLAUCOMA DETECTED"
            result_color = "#4caf50"
            message = "Your fundus image shows no signs of glaucoma"
            emoji = "😊"
            confetti_emoji = "🎉"
        else:
            risk_class = "risk-high"
            result_text = "⚠️ GLAUCOMA RISK DETECTED"
            result_color = "#f44336"
            message = "Potential glaucoma indicators found"
            emoji = "😟"
            confetti_emoji = "🚨"
        
        st.markdown(f"""
        <div class="result-box {risk_class}">
            <div style="font-size: 4rem; margin-bottom: 1rem;" class="floating">{emoji}</div>
            <h2 style="color: {result_color}; margin-bottom: 1rem; font-size: 2.2rem;">
                {result_text}
            </h2>
            <p style="font-size: 1.4rem; margin-bottom: 1rem; font-weight: 600; color: #333;">{message}</p>
            <p style="color: #666; font-size: 1.2rem;">
                Confidence Level: <strong style="color: {result_color}; font-size: 1.4rem;">{confidence:.1%}</strong>
            </p>
            <div style="font-size: 2rem; margin-top: 1rem;">{confetti_emoji}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Download Report Section
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin: 1.5rem 0;">
            <h3 style="color: #1e3c72;"> Download Your Report</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate text report
            text_report = self.generate_text_report(result)
            st.download_button(
                label=" Download Text Report",
                data=text_report,
                file_name=f"glaucoma_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_txt"
            )
        
        with col2:
            # Generate JSON report
            json_data = {
                'timestamp': datetime.now().isoformat(),
                'risk_level': risk_level,
                'confidence': float(confidence),
                'analysis_result': result['analysis_result'],
                'recommendations': result.get('recommendations', [])
            }
            st.download_button(
                label=" Download JSON Data",
                data=json.dumps(json_data, indent=2),
                file_name=f"glaucoma_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="download_json"
            )
        
        # Detailed Analysis
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        with st.expander(" View Detailed Analysis Report", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(" Risk Probabilities")
                probabilities = result['analysis_result'].get('probabilities', [0.33, 0.33, 0.34])
                
                prob_data = {
                    'Condition': ['Normal', 'Early Glaucoma', 'Advanced Glaucoma'],
                    'Probability': probabilities
                }
                prob_df = pd.DataFrame(prob_data)
                
                fig = px.bar(
                    prob_df, 
                    x='Condition', 
                    y='Probability',
                    color='Condition',
                    color_discrete_map={
                        'Normal': '#4caf50',
                        'Early Glaucoma': '#ff9800',
                        'Advanced Glaucoma': '#f44336'
                    },
                    text=prob_df['Probability'].apply(lambda x: f'{x:.1%}')
                )
                fig.update_traces(textposition='outside', textfont_size=14)
                fig.update_layout(
                    showlegend=False,
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    yaxis_title="Probability",
                    xaxis_title="",
                    font=dict(size=13, color='#1e3c72'),
                    yaxis=dict(range=[0, max(probabilities) * 1.2])
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("  Image Quality Score")
                quality_score = result.get('quality_assessment', {}).get('quality_score', 0.8)
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=quality_score * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Quality Score", 'font': {'size': 22, 'color': '#1e3c72'}},
                    delta={'reference': 80, 'increasing': {'color': "#4caf50"}},
                    number={'font': {'size': 40, 'color': '#1e3c72'}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#1e3c72"},
                        'bar': {'color': "#1e3c72", 'thickness': 0.8},
                        'bgcolor': "white",
                        'borderwidth': 3,
                        'bordercolor': "#1e3c72",
                        'steps': [
                            {'range': [0, 50], 'color': '#ffebee'},
                            {'range': [50, 80], 'color': '#fff3e0'},
                            {'range': [80, 100], 'color': '#e8f5e9'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=60, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#1e3c72", 'family': "Inter"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations section
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("  Medical Recommendations")
            
            recommendations = result.get('recommendations', [
                "Consult with an ophthalmologist for comprehensive evaluation",
                "Schedule regular eye check-ups every 6-12 months",
                "Maintain healthy lifestyle habits and eye care routine"
            ])
            
            for i, recommendation in enumerate(recommendations, 1):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(30, 60, 114, 0.05), rgba(42, 82, 152, 0.05)); 
                            padding: 1.2rem;
                            border-radius: 12px; 
                            margin: 0.8rem 0;
                            border-left: 4px solid #1e3c72;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                            animation: cardSlideUp 0.6s ease-out {i * 0.1}s both;">
                    <strong style="color: #1e3c72; font-size: 1.1rem;">{i}.</strong> 
                    <span style="color: #333; font-size: 1rem;">{recommendation}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Next Steps Section
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown(" Recommended Next Steps")
        
        if risk_level.lower() in ["normal", "low"]:
            st.success("""
               Continue Preventive Care
            
            -  Schedule annual comprehensive eye examinations
            -  Maintain a healthy diet rich in vitamins A, C, and E
            -  Stay hydrated and follow good eye hygiene
            -  Return for screening in 6-12 months
            -  Monitor for any vision changes or symptoms
            -  Regular exercise to maintain healthy intraocular pressure
            """)
        else:
            st.error("""
               Immediate Action Required
            
            -  Consult an ophthalmologist within 1-2 weeks
            -  Share these results with your healthcare provider
            -  Do not ignore any vision changes or symptoms
            -  Follow prescribed treatment plans carefully
            -  Keep this report for your medical records
            -  **Important:** This is a screening tool, not a diagnosis
            """)
        
        # Medical Disclaimer
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(211, 47, 47, 0.1));
                    border: 2px solid rgba(244, 67, 54, 0.3);
                    border-radius: 16px;
                    padding: 1.5rem;
                    text-align: center;
                    margin: 2rem 0;
                    animation: pulseWarning 2s infinite;">
            <h4 style="color: #d32f2f; margin-bottom: 0.8rem;"> Medical Disclaimer</h4>
            <p style="color: #666; font-size: 0.95rem; line-height: 1.6;">
                 ⚠️This tool is designed for screening purposes only and should not replace professional medical advice, 
                diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions regarding 
                a medical condition. Never disregard professional medical advice or delay seeking it because of information 
                provided by this tool.
            </p>
        </div>
        """, unsafe_allow_html=True)

def main():
    app = EyePressureDetector()
    app.run()

if __name__ == "__main__":
    main()