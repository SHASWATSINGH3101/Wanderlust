---

```markdown
# 🌍 Wanderlust - AI-Powered Travel Itinerary Generator
<img src='https://github.com/SHASWATSINGH3101/Wanderlust/blob/main/asset/logo.png' alt="wanderlust" width="350">

Wanderlust is an AI-powered travel itinerary generator that helps users plan their trips effortlessly by asking a series of questions and generating personalized travel recommendations. It uses **LangChain**, **Groq's Llama3-8B-8192 model**, and **TavilySearch** to create highly customized itineraries based on user preferences.

---

## 🎯 Live Demo
Check out the live version on Hugging Face Spaces:
👉 [Wanderlust - AI-Powered Travel Itinerary Generator](https://huggingface.co/spaces/SHASWATSINGH3101/Wanderlust)

---

## 🚀 Features

- ✅ **Interactive Chat Interface**: Guided conversation to gather user preferences.
- 🔍 **Smart Search Integration**: Fetches top recommendations for destinations using TavilySearch.
- 🤖 **AI-Powered Itinerary Generation**: Generates a detailed multi-day itinerary based on preferences and search results.
- 🔄 **Restart Option**: Easily start over and plan a new trip.
- 🛠️ **Seamless Gradio Interface**: User-friendly chatbot interface built using Gradio.

---

## 🖥️ Demo Preview
![Demo GIF](https://github.com/SHASWATSINGH3101/Wanderlust/blob/main/asset/demo.gif)

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/SHASWATSINGH3101/Wanderlust.git
cd wanderlust
```

### 2. Create a Virtual Environment
```bash
# Create a virtual environment
python -m venv wanderlust-env

# Activate the virtual environment
# For Windows
wanderlust-env\Scripts\activate

# For macOS/Linux
source wanderlust-env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory and add the following:
```
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
```

👉 **API Key Setup:**
- Get your [Tavily API Key](https://tavily.com/)
- Get your [Groq API Key](https://groq.com/)

---

## ▶️ Usage

### 1. Run the Application
```bash
python wanderlust.py
```

### 2. Open the Gradio Interface
Visit the link provided in your terminal, usually:
```
http://127.0.0.1:7860
```

### 3. Example Interaction
```
Bot: Hello! Ready to plan your next trip? Type 'START' to begin.
User: START
Bot: Great! Where would you like to go?
User: Paris, France
...
```

---

## ⚡ Key Components

### 1. **ChatGroq Model**
- Utilizes `llama3-8b-8192` from Groq to generate the final itinerary.
- Processes user preferences and search results to craft detailed recommendations.

### 2. **TavilySearch**
- Searches for top-rated activities and recommendations.
- Helps provide relevant suggestions for the itinerary.

### 3. **State Management**
- Stores user responses and progress in a Python dictionary.
- Tracks the conversation flow and resets after completion.

---

## 🛠️ File Structure
```
📁 wanderlust
├── 📄 wanderlust.py          # Main script with Gradio interface and logic
├── 📄 requirements.txt       # Dependencies
├── 📄 .env                   # API keys for Groq and Tavily (ignored in Git)
└── 📂 asset
    └── 📄 logo.png           # Logo image
```

---

## 📚 Dependencies
- `gradio`
- `langchain_groq`
- `langchain_tavily`
- `python-dotenv`

Install them using:
```bash
pip install gradio langchain_groq langchain_tavily python-dotenv
```

---

## 🧠 AI Models Used
- **LLM:** Llama3-8B-8192 (Groq API)
- **Search API:** Tavily API for fetching relevant travel data

---

## ❗ Troubleshooting
- Make sure to correctly set API keys in the `.env` file.
- Check the console for any errors while running the application.

---

## 💻 System Requirements
- Python 3.8+
- Compatible with Windows, macOS, and Linux

---

## 📝 Virtual Environment Deactivation
```bash
# Deactivate the virtual environment after usage
# For Windows/macOS/Linux
deactivate
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing
Pull requests are welcome! Please check out the [CONTRIBUTING.md](CONTRIBUTING.md) before making any changes.

---

## 📧 Contact
For any inquiries, reach out to:

- **GitHub:** [SHASWATSINGH3101](https://github.com/SHASWATSINGH3101)
