import gradio as gr
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set API keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize models
llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")  # Correct Groq model
search_tool = TavilySearch(
    max_results=5,
    topic="general"
)

# State stored as a dictionary
state = {
    "destination": None,
    "budget": None,
    "activities": None,
    "duration": None,
    "accommodation": None,
    "step": -1  # -1 to wait for START
}

# Define questions
questions = [
    "Where would you like to travel?",
    "What is your budget for this trip?",
    "What kind of activities do you prefer? (e.g., adventure, relaxation, sightseeing)",
    "How many days do you plan to stay?",
    "Do you prefer hotels, hostels, or Airbnbs?"
]


# Function to handle user responses and ask the next question
def ask_question(user_response, chat_history):
    # Check if user wants to start the process
    if state["step"] == -1:
        if user_response.strip().lower() == "start":
            state["step"] = 0
            initial_message = {"role": "assistant", "content": questions[0]}
            chat_history.append(initial_message)
            return chat_history, ""
        else:
            chat_history.append({"role": "assistant", "content": "❗ Type `START` to begin the travel itinerary process."})
            return chat_history, ""

    # Handle user responses
    if user_response:
        if state["step"] == 0:
            state["destination"] = user_response
        elif state["step"] == 1:
            state["budget"] = user_response
        elif state["step"] == 2:
            state["activities"] = user_response
        elif state["step"] == 3:
            state["duration"] = user_response
        elif state["step"] == 4:
            state["accommodation"] = user_response

        state["step"] += 1

    # Check if all questions are answered
    if state["step"] < len(questions):
        next_question = questions[state["step"]]
        chat_history.append({"role": "assistant", "content": next_question})
        return chat_history, ""
    else:
        itinerary = generate_itinerary()
        chat_history.append({"role": "assistant", "content": itinerary})
        state["step"] = -1  # Reset for next session
        return chat_history, ""


# Generate the travel itinerary based on user inputs
def generate_itinerary():
    # Search for travel recommendations
    search_query = f"Top things to do in {state['destination']} for {state['duration']} days with a budget of {state['budget']} and preference for {state['activities']}"
    search_results = search_tool.run(search_query)

    # Generate itinerary using search data and user preferences
    itinerary_prompt = f"""
    Create a detailed {state['duration']}-day travel itinerary for {state['destination']}.
    Consider the following preferences:
    - Budget: {state['budget']}
    - Activities: {state['activities']}
    - Accommodation type: {state['accommodation']}
    
    Use the following recommendations:
    {search_results}
    """
    itinerary = llm.predict(itinerary_prompt)

    return f"✅ Your travel itinerary is ready!\n\n{itinerary}"


# Restart conversation (Start Over button)
def start_over():
    state.update({
        "destination": None,
        "budget": None,
        "activities": None,
        "duration": None,
        "accommodation": None,
        "step": -1  # Reset for next session
    })
    initial_message = {"role": "assistant", "content": "✅ Restarted! Type `START` to begin again."}
    return [initial_message], ""


# Gradio Interface
with gr.Blocks() as app:
    gr.Markdown("# 🌍 AI-Powered Travel Itinerary Generator")

    # Chat interface with updated `type="messages"`
    chatbot = gr.Chatbot(label="Travel Bot", type="messages")
    user_input = gr.Textbox(label="Your Answer", placeholder="Type `START` to begin...")
    submit_btn = gr.Button("Send")

    # Handle conversation flow
    submit_btn.click(ask_question, inputs=[user_input, chatbot], outputs=[chatbot, user_input])

    # Start over button
    start_btn = gr.Button("Start Over")
    start_btn.click(start_over, inputs=[], outputs=[chatbot, user_input])

# Run the Gradio app
app.launch()
