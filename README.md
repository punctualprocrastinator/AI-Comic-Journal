# 📖 AI Comic Journal

Transform your daily conversations into personalized comic strips with AI! Chat about your day, and watch as AI agents craft your experiences into beautiful visual stories.

## ✨ Features

- **Interactive Chat Interface**: Share your daily experiences with an empathetic AI companion
- **Multi-Agent Story Creation**: Specialized AI agents work together to craft engaging narratives
- **Visual Comic Generation**: Transform conversations into comic strips using Fireworks AI's Flux models
- **Customizable Styles**: Choose from various art styles (cartoonish, manga, minimalist, etc.)
- **Multiple Tones**: Set the mood (funny, heartwarming, inspirational, etc.)
- **Export Functionality**: Download your comics and chat history
- **Memory Management**: Contextual conversations that remember your story

## 🚀 Live Demo

[Try it on Streamlit Cloud](https://your-app-url.streamlit.app) *(Update with your actual URL)*

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Orchestration**: CrewAI with specialized agents
- **Language Model**: Groq (Mixtral-8x7B)
- **Image Generation**: Fireworks AI (Flux-Kontext-Pro)
- **Memory**: LangChain ConversationBufferMemory

## 🏃‍♂️ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-comic-journal.git
cd ai-comic-journal
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
FIREWORKS_API_KEY=your_fireworks_api_key_here
```

### 4. Run the Application
```bash
streamlit run production_app_code.py
```

## 🔑 API Keys Setup

### Groq API Key
1. Visit [Groq Console](https://console.groq.com)
2. Create an account and generate an API key
3. Free tier available with generous limits

### Fireworks AI API Key
1. Visit [Fireworks AI](https://fireworks.ai)
2. Sign up for an account
3. Navigate to API section and create a key
4. Cost-effective image generation with high-quality results

## 🚀 Deploy to Streamlit Cloud

### 1. Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set main file path: `production_app_code.py`

### 3. Configure Secrets
In Streamlit Cloud dashboard, add these secrets:
```toml
[secrets]
GROQ_API_KEY = "your_groq_api_key_here"
FIREWORKS_API_KEY = "your_fireworks_api_key_here"
```

## 🤖 How It Works

### The AI Agent Workflow

1. **Journal Agent**: Engages in empathetic conversation, analyzing emotional context
2. **Story Agent**: Transforms conversations into structured narratives
3. **Judge Agent**: Reviews story quality and ensures appropriateness
4. **Visual Agent**: Creates detailed prompts for comic generation

### Comic Generation Process

1. **Story Extraction**: AI analyzes your conversation for key events and emotions
2. **Narrative Structuring**: Creates a coherent story with beginning, middle, and end
3. **Quality Review**: Ensures the story is engaging and appropriate
4. **Visual Design**: Generates detailed prompts for comic panel creation
5. **Image Generation**: Uses Fireworks AI to create your personalized comic strip

## 🎨 Customization Options

### Art Styles
- Cartoonish (fun and whimsical)
- Manga (expressive characters)
- New Yorker (clean line art)
- Watercolor (soft and artistic)
- Minimalist (simple and clean)
- Pixel art (retro gaming style)
- Comic book (superhero style)

### Story Tones
- Funny (comedic moments)
- Heartwarming (touching emotions)
- Slice-of-life (realistic daily life)
- Inspirational (uplifting message)
- Adventure (exciting journey)
- Dramatic (intense emotions)

### Panel Configuration
- 1-6 panels per comic strip
- Automatic layout optimization
- Consistent character design across panels

## 📁 Project Structure

```
ai-comic-journal/
├── production_app_code.py    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── assets/                 # Screenshots and demo images
    └── demo-screenshot.png
```

## 🔧 Configuration

### Streamlit Configuration
The app includes optimized settings for:
- Wide layout for better comic display
- Custom color scheme and styling
- Enhanced sidebar with session management
- Responsive design for mobile devices

### Performance Optimization
- Rate limiting to prevent API abuse
- Memory management for long conversations
- Caching for API clients
- Progress indicators for long operations

## 🐛 Troubleshooting

### Common Issues

**API Key Errors**
- Ensure your API keys are correctly set in Streamlit secrets
- Verify the keys are active and have sufficient credits

**Generation Timeouts**
- Image generation can take 30-60 seconds
- The app will show progress and retry if needed

**Memory Issues**
- Long conversations are automatically trimmed
- Clear chat history if experiencing slowdowns

### Error Logging
The app includes comprehensive error logging:
- API failures are logged with details
- User actions are tracked for debugging
- Rate limiting events are monitored

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewai) for the multi-agent framework
- [Streamlit](https://streamlit.io) for the amazing web app framework
- [Fireworks AI](https://fireworks.ai) for cost-effective, high-quality image generation
- [Groq](https://groq.com) for fast language model inference

## 📞 Support

- 🐛 [Report Issues](https://github.com/yourusername/ai-comic-journal/issues)
- 💬 [Discussions](https://github.com/yourusername/ai-comic-journal/discussions)
- 📧 Email: your.email@example.com

---

**Made with ❤️ by [Your Name](https://github.com/yourusername)**

*Turn your everyday moments into extraordinary visual stories!*
