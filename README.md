
---

# 🌍 Wanderlust - AI-Powered Travel Itinerary Generator
https://github.com/SHASWATSINGH3101/Wanderlust/blob/main/asset/logo.png
Wanderlust is an AI-powered travel itinerary generator that helps users plan their trips effortlessly by asking a series of questions and generating personalized travel recommendations. It uses **LangChain**, **Groq's Llama3-8B-8192 model**, and **TavilySearch** to create highly customized itineraries based on user preferences.

---

## 🚀 Features

- ✅ **Interactive Chat Interface**: Guided conversation to gather user preferences.
- 🔍 **Smart Search Integration**: Fetches top recommendations for destinations using TavilySearch.
- 🤖 **AI-Powered Itinerary Generation**: Generates a detailed multi-day itinerary based on preferences and search results.
- 🔄 **Restart Option**: Easily start over and plan a new trip.
- 🛠️ **Seamless Gradio Interface**: User-friendly chatbot interface built using Gradio.

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

---

## 💬 How It Works

1. **Start the Process**: Type `START` to begin.
2. **Answer the Questions**: The bot will ask you a series of questions to understand your preferences.
    - Destination
    - Budget
    - Preferred Activities
    - Duration of Stay
    - Accommodation Type
3. **Receive Your Itinerary**: Once all the questions are answered, a detailed itinerary is generated.
4. **Restart Anytime**: Use the `Start Over` button to begin again.

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
└── 📄 .env                   # API keys for Groq and Tavily (ignored in Git)
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

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to modify.

---

## 📧 Contact
For any inquiries, reach out to:

- **GitHub:** [SHASWATSINGH3101](https://github.com/SHASWATSINGH3101)

Happy Traveling! ✈️🌟

---

Let me know if you need any modifications or additions! 😊
