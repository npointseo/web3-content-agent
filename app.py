import streamlit as st
import json
import os
from agent import generate_blog, generate_social_assets
from renderer import generate_all_images

# Automatically install playwright chromium browsers (vital for Cloud Deployments like Streamlit Community Cloud)
os.system("playwright install chromium")

st.set_page_config(page_title="Web3 Content Agent", page_icon="🚀", layout="wide")

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = 1
if "draft_blog" not in st.session_state:
    st.session_state.draft_blog = ""
if "social_content" not in st.session_state:
    st.session_state.social_content = None
if "image_paths" not in st.session_state:
    st.session_state.image_paths = []

def load_brand():
    try:
        with open("brand.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load brand.json: {e}")
        return {}

st.title("🚀 Web3 & Crypto Content Generation Engine")
st.markdown("Automate your blog writing and perfectly branded social media asset generation.")

# Sidebar for brand settings & API keys
with st.sidebar:
    st.header("🎨 Active Brand Guide")
    brand = load_brand()
    if brand:
        st.color_picker("Primary Color", brand.get("primaryColor", "#000000"), disabled=True)
        st.color_picker("Background Color", brand.get("backgroundColor", "#ffffff"), disabled=True)
        st.write(f"**Font Family:** {brand.get('fontFamily', 'System')}")
        st.caption("Settings are currently loaded from `brand.json`.")
    
    st.divider()
    st.header("🔑 Required Settings")
    api_key = st.text_input("Gemini API Key", type="password", help="Required to generate the content.")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

# ----------------- STAGE 1: Ideation -----------------
if st.session_state.stage == 1:
    st.header("Step 1: Ideation & Generation")
    st.info("Enter a rough idea or topic. The AI will flesh this out into a full, SEO-optimized blog draft.")
    topic = st.text_input("What Web3/Crypto topic should we write about?", placeholder="e.g. Bitcoin Halving 2024 Analysis")
    
    if st.button("Generate Blog Draft", type="primary"):
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("Please enter your Gemini API Key in the sidebar.")
        elif not topic:
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Writing the draft... this usually takes 10-20 seconds."):
                try:
                    st.session_state.draft_blog = generate_blog(topic)
                    st.session_state.stage = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating text: {e}")

# ----------------- STAGE 2: Review -----------------
elif st.session_state.stage == 2:
    st.header("Step 2: Human-in-the-Loop Review")
    st.success("Blog draft generated successfully!")
    st.info("Review the content below. As the Web3 expert, make any manual tweaks or corrections directly in the text box before generating the final graphics and social copy.")
    
    edited_blog = st.text_area("Blog Draft (Markdown enabled)", value=st.session_state.draft_blog, height=500)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Approve & Generate Assets", type="primary"):
            st.session_state.draft_blog = edited_blog
            with st.spinner("Part 1/2: Synthesizing Social Media Copy..."):
                try:
                    st.session_state.social_content = generate_social_assets(st.session_state.draft_blog)
                    
                    with st.spinner("Part 2/2: Rendering Perfect Branded Graphics via Headless Browser..."):
                        st.session_state.image_paths = generate_all_images(brand, st.session_state.social_content)
                    
                    st.session_state.stage = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating assets: {e}")
    with col2:
        if st.button("Cancel & Start Over"):
            st.session_state.stage = 1
            st.rerun()

# ----------------- STAGE 3: Final Assets -----------------
elif st.session_state.stage == 3:
    st.header("Step 3: Your Ready-to-Post Assets 🎉")
    if st.button("Start New Post"):
        st.session_state.stage = 1
        st.session_state.draft_blog = ""
        st.session_state.social_content = None
        st.session_state.image_paths = []
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 The Blog", "📸 Instagram Bundle", "👔 LinkedIn Bundle", "🐦 X / Twitter Threads"])
    
    with tab1:
        st.subheader("Approved Blog Post")
        st.markdown(st.session_state.draft_blog)
        st.divider()
        st.subheader("Main Blog Header Graphic")
        header_path = next((p for p in st.session_state.image_paths if "blog_header" in p), None)
        if header_path:
            st.image(header_path)
            
    with tab2:
        st.subheader("Instagram Caption")
        st.code(st.session_state.social_content['instagram_caption'], language="text")
        st.divider()
        st.subheader("Perfectly Branded Carousel Sequence")
        cols = st.columns(3)
        carousel_imgs = [p for p in st.session_state.image_paths if "carousel" in p]
        for i, img_path in enumerate(carousel_imgs):
            cols[i % 3].image(img_path, caption=f"Slide {i+1}", use_column_width=True)

    with tab3:
        st.subheader("LinkedIn Copy")
        st.code(st.session_state.social_content['linkedin_post'], language="text")
        st.info("Pro Tip: Attach your Blog Header Graphic to this LinkedIn Post for maximum engagement.")
        
    with tab4:
        st.subheader("Engaging Tweets")
        for i, tweet in enumerate(st.session_state.social_content['twitter_posts']):
            st.code(tweet, language="text")
