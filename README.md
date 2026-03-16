# 🌱 PlantGuardian AI

A Streamlit-based application that helps you take care of your plants using AI-powered image analysis and chat assistance with real LLMs.

## 🚀 Features

- 📸 **Upload plant images** for health analysis with confidence scores
- 💬 **Chat with an AI plant care assistant** using real LLMs
- 🌿 **Get personalized care recommendations** based on analysis
- 🔍 **Identify plant health issues** with detailed diagnostics
- 🌐 **Supports multiple LLM providers** (OpenAI, Anthropic, Meta, etc.)
- 📱 **Mobile-friendly interface** for on-the-go plant care
- 📧 **Email notifications** for registration and subscriptions
- 💳 **Subscription packages** with one-tap payments
- 👥 **User authentication** with username/email and password
- ✨ **20 free trials** with Gemini for new users

## 🎯 Evaluation & Prediction Confidences

Our plant analysis system provides confidence scores for all predictions:

### Computer Vision Analysis
- **Health Score**: Overall plant health percentage (0-100%)
- **Color Analysis**: 
  - Healthy green: Confidence percentage
  - Yellowing: Confidence percentage
  - Browning: Confidence percentage
- **Disease Detection**: Confidence percentages for common plant diseases
- **Leaf Count**: Estimated number of leaves with accuracy indicator

### LLM-Based Recommendations
- **Care Recommendations**: Generated with confidence based on analysis
- **Chat Responses**: Context-aware responses with relevance scoring
- **Plant Identification**: Species identification confidence percentages

### Confidence Levels Explained
- **High (80-100%)**: Very confident in the prediction
- **Medium (60-79%)**: Moderately confident, consider additional factors
- **Low (40-59%)**: Low confidence, verification recommended
- **Very Low (0-39%)**: Very low confidence, manual inspection advised

## 🛠️ Prerequisites

- Python 3.8+
- API key from one of the supported LLM providers

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/saurabhhhcodes/plant-guardian-ai.git
   cd plant-guardian-ai
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys and email credentials in a `.env` file. You can use the `.env.example` file as a template.

## 🎯 Usage

## 🎯 Usage

1. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Register a new account or log in with your existing credentials

4. Select your preferred LLM provider and enter your API key in the sidebar

5. Upload a photo of your plant or use the camera feature

6. View analysis results with confidence scores

7. Chat with the AI assistant for personalized care advice

## 🤖 Supported LLM Providers

## 🤖 Supported LLM Providers

- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude models (Claude 3 Opus, Sonnet, Haiku)
- **Meta**: Llama models through Together.ai (Llama 3, Llama 2)
- **Other providers**: Additional models via Together.ai integration
- **Ollama**: Run open source LLMs locally (no API key required, requires Ollama server)
- **Hugging Face Hub**: Use models from Hugging Face with your API key
- **local-hf (TinyLlama, open source, no API key)**: Runs a small, fast open source LLM (TinyLlama) directly on your machine using Hugging Face Transformers. No API key required. Great for privacy and offline use. Requires sufficient RAM and CPU/GPU. No server needed.

---

## 🌐 Try the App Online

**[PlantGuardian AI Streamlit App](https://plantguardianai.streamlit.app/)**

---

## 📊 Analysis Features

### Computer Vision Analysis
- **Health Assessment**: Overall plant condition with confidence score
- **Color Distribution**: Green, yellow, and brown percentage analysis
- **Disease Detection**: Identification of common plant diseases
- **Growth Monitoring**: Track plant health over time

### AI Recommendations
- **Watering Schedule**: Personalized watering advice
- **Light Requirements**: Optimal lighting conditions
- **Nutrient Needs**: Fertilization recommendations
- **Problem Solutions**: Specific solutions for detected issues


## ⚠️ Note on Linux/Streamlit Cloud Warnings

If you see a warning like `OSError: [Errno 28] inotify watch limit reached` in your logs, it is safe to ignore. This is a system-level file watcher limit and does **not** affect the app's functionality. Your plant care assistant will work as expected.

---

## ☁️ Deployment

This application is designed to work with Streamlit Cloud. Users can select their preferred LLM provider and enter their API key directly in the application interface.

### Streamlit Cloud Deployment
1. Fork this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app using your forked repository
4. Set the main file path to `streamlit_app.py`
5. Deploy and share with others

## 🧪 Reproducible Testing

To verify the installation and core functionality, follow these steps:

### 1. Environment Setup
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```env
# Required for Gemini/ADK functionality
GOOGLE_API_KEY=your_gemini_api_key_here
USER_EMAIL=your_email@gmail.com
USER_PASSWORD=your_app_password  # For email notifications
```

### 3. Execution
Run the application:
```bash
streamlit run streamlit_app.py
```

### 4. Verification Steps
1. **Login:** Register a new user and login.
2. **Analysis:** Upload a plant image (e.g., `test_image.jpg`).
3. **Agent Verification:** Verify that the "AI Diagnosis" appears with a 7-Day recovery roadmap.
4. **Chat:** Send a message like "How much water does this plant need?" and verify the AI response.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- Streamlit for the excellent web framework
- LangChain for LLM integration
- Plant care experts for validation and feedback

---

**Keep your plants healthy and happy with AI-powered care! 🌱**