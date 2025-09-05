import os
import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import chromadb

import streamlit as st
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
import requests
import base64
import time
import logging

# =====================
# PAGE CONFIGURATION
# =====================
st.set_page_config(
    page_title="AI Comic Journal - Turn Your Day into Comics",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ai-comic-journal',
        'Report a bug': 'https://github.com/yourusername/ai-comic-journal/issues',
        'About': "Transform your daily conversations into personalized comic strips with AI!"
    }
)

# =====================
# CUSTOM STYLING
# =====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .chat-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =====================
# API CONFIGURATION
# =====================
@st.cache_data
def load_api_keys():
    """Load API keys from Streamlit secrets"""
    try:
        return {
            "groq": st.secrets["GROQ_API_KEY"],
            "fireworks": st.secrets["FIREWORKS_API_KEY"]
        }
    except KeyError as e:
        st.error(f"⚠️ Missing API key in secrets: {e}")
        st.info("Please configure your API keys in Streamlit Cloud settings.")
        st.stop()

# Load API keys
api_keys = load_api_keys()

# Initialize Groq client with error handling
try:
    llm = ChatGroq(
        model="openai/gpt-oss-120b", 
        api_key=api_keys["groq"], 
        temperature=0.7,
        timeout=30  # Add timeout
    )
except Exception as e:
    st.error(f"⚠️ Failed to initialize AI services: {str(e)}")
    st.stop()

# =====================
# FIREWORKS AI IMAGE GENERATION
# =====================
def generate_image_with_fireworks(prompt, max_attempts=60):
    """Generate image using Fireworks AI API with polling"""
    try:
        # Step 1: Submit the generation request
        url = "https://api.fireworks.ai/inference/v1/workflows/accounts/fireworks/models/flux-kontext-pro"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_keys['fireworks']}",
        }
        data = {
            "prompt": prompt
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        request_id = result.get("request_id")

        if not request_id:
            raise Exception("No request ID returned from Fireworks AI")

        st.info(f"🔄 Generation started (ID: {request_id[:8]}...)")

        # Step 2: Poll for the result
        result_endpoint = f"{url}/get_result"
        
        progress_container = st.empty()
        
        for attempt in range(max_attempts):
            time.sleep(1)
            
            # Update progress
            progress_container.text(f"⏳ Generating image... ({attempt + 1}/{max_attempts})")
            
            result_response = requests.post(result_endpoint, 
                headers={
                    "Content-Type": "application/json",
                    "Accept": "image/jpeg",
                    "Authorization": f"Bearer {api_keys['fireworks']}"
                },
                json={"id": request_id}
            )
            
            poll_result = result_response.json()
            status = poll_result.get("status")
            
            if status in ["Ready", "Complete", "Finished"]:
                progress_container.empty()
                image_data = poll_result.get("result", {}).get("sample")
                
                if isinstance(image_data, str) and image_data.startswith("http"):
                    # Image is available via URL
                    return image_data
                elif image_data:
                    # Base64 encoded image data
                    try:
                        # Decode base64 and create a data URL for display
                        decoded_data = base64.b64decode(image_data)
                        # Convert to base64 string for display in Streamlit
                        img_b64 = base64.b64encode(decoded_data).decode()
                        return f"data:image/jpeg;base64,{img_b64}"
                    except Exception as decode_error:
                        st.error(f"Error decoding image: {decode_error}")
                        return None
                else:
                    st.error("No image data returned")
                    return None
            
            elif status in ["Failed", "Error"]:
                progress_container.empty()
                error_details = poll_result.get('details', 'Unknown error')
                raise Exception(f"Generation failed: {error_details}")
            
            # Continue polling for other statuses (Processing, Queued, etc.)
        
        # If we've exhausted all attempts
        progress_container.empty()
        st.error(f"⏰ Generation timed out after {max_attempts} seconds")
        return None
        
    except requests.exceptions.RequestException as e:
        st.error(f"🌐 Network error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"🚨 Image generation error: {str(e)}")
        return None

# =====================
# RATE LIMITING
# =====================
def check_rate_limit():
    """Implement simple rate limiting"""
    if 'last_request_time' not in st.session_state:
        st.session_state.last_request_time = 0
    
    if time.time() - st.session_state.last_request_time < 3:  # 3 second cooldown
        st.warning("⏳ Please wait a moment between requests to avoid overwhelming our servers...")
        return False
    
    st.session_state.last_request_time = time.time()
    return True

# =====================
# MEMORY MANAGEMENT
# =====================
@st.cache_resource
def get_memory():
    """Get or create conversation memory"""
    return ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True,
        max_token_limit=1500  # Prevent memory overflow
    )

def manage_conversation_length():
    """Keep conversation history manageable"""
    if "messages" in st.session_state and len(st.session_state.messages) > 30:
        # Keep last 20 messages to maintain context but limit memory usage
        st.session_state.messages = st.session_state.messages[-20:]
        st.info("💡 Conversation history trimmed to improve performance")

# =====================
# ENHANCED AGENTS WITH ERROR HANDLING
# =====================
def create_agents():
    """Create AI agents with error handling"""
    try:
        memory = get_memory()
        
        journal_agent = Agent(
            role="Journal Buddy & Conversation Analyst",
            goal="Engage users in meaningful conversation while analyzing emotional context",
            backstory="""You are a warm, empathetic AI companion. Use step-by-step reasoning:
            1. Analyze the emotional tone and context
            2. Identify key details and events
            3. Connect to previous conversations
            4. Respond with appropriate empathy and questions
            Keep responses concise but engaging.""",
            llm=llm,
            memory=memory,
            allow_delegation=False,
            verbose=False
        )
        
        story_agent = Agent(
            role="Story Weaver",
            goal="Transform conversations into engaging narratives",
            backstory="""Master storyteller who thinks systematically:
            1. Extract main characters, setting, and events
            2. Organize chronologically with clear structure
            3. Add narrative flow while staying authentic
            4. Create engaging but concise stories""",
            llm=llm,
            allow_delegation=False,
            verbose=False
        )
        
        judge_agent = Agent(
            role="Content Quality Specialist",
            goal="Ensure story quality and appropriateness",
            backstory="""Quality control expert with systematic approach:
            1. Check clarity and engagement
            2. Review appropriateness for all audiences
            3. Assess narrative flow and pacing
            4. Provide specific improvements if needed""",
            llm=llm,
            allow_delegation=False,
            verbose=False
        )
        
        visual_agent = Agent(
            role="Visual Prompt Creator",
            goal="Create detailed comic strip prompts",
            backstory="""Visual storytelling expert who plans systematically:
            1. Break story into logical panel sequences
            2. Design consistent characters and settings
            3. Plan compelling compositions and angles
            4. Integrate requested art style and tone
            
            Focus on creating detailed, specific visual descriptions that work well with image generation AI.""",
            llm=llm,
            allow_delegation=False,
            verbose=False
        )
        
        return journal_agent, story_agent, judge_agent, visual_agent
    
    except Exception as e:
        st.error(f"⚠️ Failed to create AI agents: {str(e)}")
        return None, None, None, None

# =====================
# MAIN APPLICATION
# =====================
def main():
    # Header
    st.markdown('<h1 class="main-header">📖 AI Comic Journal</h1>', unsafe_allow_html=True)
    st.markdown("### ✨ Turn your daily conversations into personalized comic strips!")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    # Create agents
    journal_agent, story_agent, judge_agent, visual_agent = create_agents()
    if not all([journal_agent, story_agent, judge_agent, visual_agent]):
        st.error("Failed to initialize AI agents. Please refresh the page.")
        return
    
    # Manage conversation length
    manage_conversation_length()
    
    # Main chat interface
    st.subheader("💬 Chat About Your Day")
    
    # Display conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # User input
    if user_input := st.chat_input("Tell me about your day...", disabled=st.session_state.processing):
        if not check_rate_limit():
            return
            
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # AI response
        with st.chat_message("assistant"):
            try:
                st.session_state.processing = True
                
                with st.spinner("🤔 Thinking about your message..."):
                    # Create task with conversation context
                    context = "\n".join([f"{m['role']}: {m['content']}" 
                                       for m in st.session_state.messages[-5:]])  # Last 5 messages
                    
                    task = Task(
                        description=f"""
                        User's message: "{user_input}"
                        Recent context: {context}
                        
                        Respond step-by-step:
                        1. What emotion/tone do I detect?
                        2. What key details should I remember?
                        3. How does this connect to our conversation?
                        4. What's the most engaging response?
                        
                        Keep response warm, concise (2-3 sentences), and encouraging.
                        """,
                        agent=journal_agent,
                        expected_output="A warm, engaging response that encourages further conversation"
                    )
                    
                    crew = Crew(agents=[journal_agent], tasks=[task], verbose=False)
                    response = str(crew.kickoff())
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
            except Exception as e:
                st.error(f"⚠️ Sorry, I encountered an error: {str(e)}")
                logging.error(f"Chat error: {str(e)}")
            finally:
                st.session_state.processing = False
    
    # Comic generation section
    st.markdown("---")
    st.subheader("🎨 Create Your Comic Strip")
    
    # Preferences
    col1, col2, col3 = st.columns(3)
    
    with col1:
        style = st.selectbox(
            "🎭 Art Style:",
            [
                "Cartoonish (fun and whimsical)",
                "Manga (expressive characters)",
                "New Yorker (clean line art)",
                "Watercolor (soft and artistic)",
                "Minimalist (simple and clean)",
                "Pixel art (retro gaming style)",
                "Comic book (superhero style)"
            ]
        )
    
    with col2:
        tone = st.selectbox(
            "🎵 Story Tone:",
            [
                "Funny (comedic moments)",
                "Heartwarming (touching emotions)",
                "Slice-of-life (realistic daily life)",
                "Inspirational (uplifting message)",
                "Adventure (exciting journey)",
                "Dramatic (intense emotions)"
            ]
        )
    
    with col3:
        panels = st.slider("📱 Panels:", 1, 6, 3, help="More panels = more detailed story")
    
    # Generate comic button
    if len(st.session_state.messages) >= 4:  # Need some conversation
        if st.button("✨ Generate My Comic Strip", type="primary", disabled=st.session_state.processing):
            if not check_rate_limit():
                return
                
            generate_comic(story_agent, judge_agent, visual_agent, style, tone, panels)
    else:
        st.info("💬 Chat with me more to build a story for your comic!")
    
    # Sidebar with info and controls
    with st.sidebar:
        st.markdown("## 📊 Session Stats")
        st.metric("Messages", len(st.session_state.messages))
        
        st.markdown("## 🛠️ Controls")
        
        if st.button("🗑️ Clear Chat", help="Start a new conversation"):
            st.session_state.messages = []
            get_memory().clear()
            st.rerun()
        
        if st.session_state.messages:
            chat_export = "\n".join([f"{m['role'].upper()}: {m['content']}" 
                                   for m in st.session_state.messages])
            st.download_button(
                "📄 Export Chat",
                data=chat_export,
                file_name=f"comic_journal_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        st.markdown("## 💡 Tips")
        st.info("""
        - Share specific details about your day
        - Mention emotions and reactions  
        - Include interesting people or situations
        - The more you share, the better your comic!
        """)
        
        st.markdown("## 🔗 Links")
        st.markdown("- [Report Issues](https://github.com/yourusername/ai-comic-journal/issues)")
        st.markdown("- [View Source](https://github.com/yourusername/ai-comic-journal)")

def generate_comic(story_agent, judge_agent, visual_agent, style, tone, panels):
    """Generate comic strip from conversation using Fireworks AI"""
    try:
        st.session_state.processing = True
        progress_bar = st.progress(0)
        
        # Step 1: Create story (25%)
        with st.spinner("📝 Crafting your story..."):
            conversation_text = "\n".join([f"{m['role']}: {m['content']}" 
                                         for m in st.session_state.messages])
            
            story_task = Task(
                description=f"""
                Conversation: {conversation_text}
                
                Create story systematically:
                1. Extract key characters, events, emotions
                2. Organize chronologically  
                3. Add narrative structure (beginning, middle, end)
                4. Keep it concise but engaging (2-3 sentences)
                
                Focus on the most interesting or emotional moments.
                """,
                agent=story_agent,
                expected_output="A concise, engaging story capturing the conversation's essence"
            )
            
            story_crew = Crew(agents=[story_agent], tasks=[story_task], verbose=False)
            story = str(story_crew.kickoff())
            progress_bar.progress(25)
        
        # Step 2: Quality check (50%)
        with st.spinner("🔍 Polishing the narrative..."):
            judge_task = Task(
                description=f"""
                Story: {story}
                
                Quality review process:
                1. Is it clear and engaging?
                2. Appropriate for all audiences?
                3. Good narrative flow?
                4. Any improvements needed?
                
                Provide enhanced version if needed, otherwise approve as-is.
                """,
                agent=judge_agent,
                expected_output="Final polished story or approval of current version"
            )
            
            judge_crew = Crew(agents=[judge_agent], tasks=[judge_task], verbose=False)
            final_story = str(judge_crew.kickoff())
            progress_bar.progress(50)
        
        # Step 3: Create visual prompt (75%)
        with st.spinner("🎨 Designing your comic..."):
            visual_task = Task(
                description=f"""
                Story: {final_story}
                Style: {style}
                Tone: {tone}
                Panels: {panels}
                
                Visual planning for comic strip generation:
                1. Create a {panels}-panel comic strip layout
                2. Describe consistent characters throughout all panels
                3. Plan clear sequential storytelling
                4. Integrate {style} aesthetic with {tone} mood
                5. Ensure each panel shows clear action/emotion
                6. Include speech bubbles or thought bubbles where appropriate
                
                Create a detailed, specific prompt that will generate a high-quality comic strip.
                Focus on visual storytelling elements like character expressions, panel composition, and scene setting.
                """,
                agent=visual_agent,
                expected_output=f"Detailed visual prompt for {panels}-panel comic strip generation"
            )
            
            visual_crew = Crew(agents=[visual_agent], tasks=[visual_task], verbose=False)
            comic_prompt = str(visual_crew.kickoff())
            progress_bar.progress(75)
        
        # Step 4: Generate image with Fireworks AI (100%)
        with st.spinner("🖼️ Bringing your comic to life..."):
            # Enhance the prompt for better comic generation
            enhanced_prompt = f"""
            {comic_prompt}
            
            High quality comic strip illustration, {panels} panels arranged horizontally or in a grid layout, 
            clear panel borders, consistent character design throughout all panels, 
            professional comic book illustration style, vibrant colors, detailed artwork,
            speech bubbles with readable text, dynamic compositions, expressive characters.
            """
            
            img_url = generate_image_with_fireworks(enhanced_prompt)
            progress_bar.progress(100)
        
        if img_url:
            # Display results
            st.success("🎉 Your comic strip is ready!")
            
            # Show story
            with st.expander("📖 Your Story"):
                st.write(final_story)
            
            # Show the visual prompt used
            with st.expander("🎨 Visual Prompt Used"):
                st.write(comic_prompt)
            
            # Display comic
            if img_url.startswith("data:image"):
                # Base64 encoded image
                st.image(img_url, caption=f"Your {panels}-panel {style} comic strip")
            else:
                # URL to image
                st.image(img_url, caption=f"Your {panels}-panel {style} comic strip")
                st.markdown(f"[📥 Download Comic]({img_url})")
            
            # Store for potential sharing
            st.session_state.comic_url = img_url
            
            # Option to regenerate with same story
            if st.button("🔄 Generate Another Version", help="Same story, new visual interpretation"):
                # Regenerate with slightly modified prompt
                varied_prompt = f"{enhanced_prompt} Alternative visual interpretation, different camera angles and compositions."
                new_img_url = generate_image_with_fireworks(varied_prompt)
                if new_img_url:
                    st.image(new_img_url, caption="Alternative version of your comic")
        else:
            st.error("Failed to generate comic. Please try again.")
        
    except Exception as e:
        st.error(f"⚠️ Comic generation failed: {str(e)}")
        st.info("💡 Please try again in a moment or check if your conversation is detailed enough.")
        logging.error(f"Comic generation error: {str(e)}")
    
    finally:
        st.session_state.processing = False

# =====================
# RUN APP
# =====================
if __name__ == "__main__":
    main()
