# --- Imports ---
import gradio as gr
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults # Updated import
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import os
from dotenv import load_dotenv
from typing import TypedDict, List, Optional, Dict, Sequence
from langgraph.graph import StateGraph, END

# --- Environment Setup ---
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TAVILY_API_KEY or not GROQ_API_KEY:
    raise ValueError("API keys for Tavily and Groq must be set in .env file")

# --- Constants ---
ORDERED_FIELDS = [
    "destination",
    "budget",
    "activities",
    "duration",
    "accommodation",
]

QUESTIONS_MAP = {
    "destination": "🌍 Where would you like to travel?",
    "budget": "💰 What is your budget for this trip?",
    "activities": "🤸 What kind of activities do you prefer? (e.g., adventure, relaxation, sightseeing)",
    "duration": "⏳ How many days do you plan to stay?",
    "accommodation": "🏨 Do you prefer hotels, hostels, or Airbnbs?",
}

INITIAL_MESSAGE = "👋 Welcome! Type `START` to begin planning your travel itinerary."
START_CONFIRMATION = "🚀 Great! Let's plan your trip. " + QUESTIONS_MAP[ORDERED_FIELDS[0]]
RESTART_MESSAGE = "✅ Restarted! Type `START` to begin again."
INVALID_START_MESSAGE = "❗ Please type `START` to begin the travel itinerary process."
ITINERARY_READY_MESSAGE = "✅ Your travel itinerary is ready!"

# --- LangChain / LangGraph Components ---

# Initialize models and tools
llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")
# Note: TavilySearchResults often works better when integrated as a Langchain Tool
# but for direct use like this, the previous langchain_tavily.TavilySearch is also fine.
# Let's use the more standard Tool wrapper approach for better compatibility.
search_tool = TavilySearchResults(max_results=5, tavily_api_key=TAVILY_API_KEY)


# Define the state for our graph
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]  # Conversation history
    user_info: Dict[str, str]      # Collected user preferences
    missing_fields: List[str]      # Fields still needed
    search_results: Optional[str]  # Results from Tavily search
    itinerary: Optional[str]       # Final generated itinerary

# --- Node Functions ---

def process_user_input(state: AgentState) -> Dict:
    """Processes the latest user message to update user_info."""
    last_message = state['messages'][-1]
    if not isinstance(last_message, HumanMessage):
        # Should not happen in normal flow, but good safeguard
        return {}

    user_response = last_message.content.strip()
    missing_fields = state.get('missing_fields', [])
    user_info = state.get('user_info', {})

    if not missing_fields:
        # All info gathered, nothing to process here for now
        # This node is primarily for capturing answers to questions
        return {}

    # Assume the user is answering the question related to the *first* missing field
    field_to_update = missing_fields[0]
    user_info[field_to_update] = user_response

    # Remove the field we just got
    updated_missing_fields = missing_fields[1:]

    print(f"--- Processed Input: Field '{field_to_update}' = '{user_response}' ---")
    print(f"--- Remaining Fields: {updated_missing_fields} ---")

    return {"user_info": user_info, "missing_fields": updated_missing_fields}

def ask_next_question(state: AgentState) -> Dict:
    """Adds the next question to the messages list."""
    missing_fields = state.get('missing_fields', [])
    if not missing_fields:
        # Should not be called if no fields are missing, but handle defensively
        return {"messages": state['messages'] + [AIMessage(content="Something went wrong, no more questions to ask.")]} # type: ignore

    next_field = missing_fields[0]
    question = QUESTIONS_MAP[next_field]

    print(f"--- Asking Question for: {next_field} ---")
    # Append the new question
    updated_messages = state['messages'] + [AIMessage(content=question)] # type: ignore
    return {"messages": updated_messages}


def run_search(state: AgentState) -> Dict:
    """Runs Tavily search based on collected user info, handling descriptive terms."""
    user_info = state['user_info']
    print("--- Running Search ---")

    # Construct a more descriptive query for the search engine
    query_parts = [f"Travel itinerary ideas for {user_info.get('destination', 'anywhere')}"]
    if user_info.get('duration'):
         # Try to clarify duration if it's non-numeric, otherwise use as is
         duration_desc = user_info.get('duration')
         query_parts.append(f"for about {duration_desc} days.")

    if user_info.get('budget'):
        # Frame budget as a description
        query_parts.append(f"User's budget is described as: '{user_info.get('budget')}'.")

    if user_info.get('activities'):
        # Frame activities as a description
        query_parts.append(f"User is looking for activities like: '{user_info.get('activities')}'.")

    if user_info.get('accommodation'):
        # Frame accommodation as a description
        query_parts.append(f"User's accommodation preference is: '{user_info.get('accommodation')}'.")

    search_query = " ".join(query_parts)
    print(f"--- Refined Search Query: {search_query} ---")

    try:
        results = search_tool.invoke(search_query)
        # Handle potential result formats (string, list of docs, dict)
        if isinstance(results, list):
             search_results_str = "\n\n".join([getattr(doc, 'page_content', str(doc)) for doc in results]) # Safer access
        elif isinstance(results, dict) and 'answer' in results:
             search_results_str = results['answer']
        elif isinstance(results, dict) and 'result' in results: # Another common format
             search_results_str = results['result']
        else:
             search_results_str = str(results)

        print(f"--- Search Results Found ---")
        return {"search_results": search_results_str}
    except Exception as e:
        print(f"--- Search Failed: {e} ---")
        # Provide a more informative error message if possible
        error_details = str(e)
        return {"search_results": f"Search failed or timed out. Details: {error_details}"}


def generate_itinerary(state: AgentState) -> Dict:
    """Generates the final itinerary using the LLM, interpreting flexible user inputs."""
    user_info = state['user_info']
    search_results = state.get('search_results', "No search results available.") # Provide default
    print("--- Generating Itinerary ---")

    # --- Enhanced Prompt ---
    itinerary_prompt = f"""
    You are an expert travel planner. Create a detailed and engaging travel itinerary based on the following user preferences:
    NOTE :- Do not go over the user budget.
    
    **User Preferences:**
    - Destination: {user_info.get('destination', 'Not specified')}
    - Duration: {user_info.get('duration', 'Not specified')} days
    - Budget Description: '{user_info.get('budget', 'Not specified')}'
    - Preferred Activities Description: '{user_info.get('activities', 'Not specified')}'
    - Preferred Accommodation Description: '{user_info.get('accommodation', 'Not specified')}'

    **Your Task:**
    1.  **Interpret Preferences:** Carefully interpret the user's descriptions for budget, activities, and accommodation.
        * If the budget is descriptive (e.g., 'moderate', 'budget-friendly', 'a bit flexible', 'around $X'), tailor suggestions to match that level for the specific destination. Avoid extreme high-cost or only free options unless explicitly requested. 'Moderate' usually implies a balance of value, comfort, and experiences.
        * If activities are described generally (e.g., 'mix of famous and offbeat', 'relaxing', 'cultural immersion', 'adventure'), create an itinerary that reflects this. A 'mix' should include popular landmarks and hidden gems. 'Relaxing' should include downtime.
        * Interpret accommodation descriptions (e.g., 'mid-range', 'cheap but clean', 'boutique hotel') based on typical offerings at the destination.
    2.  **Use Search Results:** Incorporate relevant and specific suggestions from the search results below, but *only* if they align with the interpreted user preferences. Do not blindly copy search results.
    3.  **Create a Coherent Plan:** Structure the itinerary logically, often day-by-day. Include suggestions for specific activities, potential dining spots (matching budget), and estimated timings where appropriate.
    4.  **Engaging Tone:** Present the itinerary in an exciting and appealing way.

    **Supporting Search Results:**
    ```
    {search_results}
    ```

    **Generate the Itinerary:**
    """
    # --- End of Enhanced Prompt ---

    try:
        response = llm.invoke(itinerary_prompt)
        # Ensure content extraction handles potential variations
        itinerary_content = getattr(response, 'content', str(response))

        print("--- Itinerary Generated ---")

        final_message = AIMessage(content=f"{ITINERARY_READY_MESSAGE}\n\n{itinerary_content}")
        # Ensure messages list exists and append correctly
        updated_messages = list(state.get('messages', [])) + [final_message]

        return {"itinerary": itinerary_content, "messages": updated_messages}
    except Exception as e:
        print(f"--- Itinerary Generation Failed: {e} ---")
        error_details = str(e)
        error_message = AIMessage(content=f"Sorry, I encountered an error while generating the itinerary. Details: {error_details}")
        # Ensure messages list exists and append correctly
        updated_messages = list(state.get('messages', [])) + [error_message]
        return {"itinerary": None, "messages": updated_messages}



def should_ask_question_or_search(state: AgentState) -> str:
    """Determines the next step based on whether all info is collected."""
    missing_fields = state.get('missing_fields', [])
    if not missing_fields:
        print("--- Condition: All info gathered, proceed to search ---")
        return "run_search"
    else:
        print("--- Condition: More info needed, ask next question ---")
        return "ask_next_question"

# --- Build the Graph ---

graph_builder = StateGraph(AgentState)

# Define nodes
graph_builder.add_node("process_user_input", process_user_input)
graph_builder.add_node("ask_next_question", ask_next_question)
graph_builder.add_node("run_search", run_search) # Uses the updated function
graph_builder.add_node("generate_itinerary", generate_itinerary)

# Define edges
graph_builder.set_entry_point("process_user_input")
graph_builder.add_conditional_edges(
    "process_user_input",
    should_ask_question_or_search,
    {"ask_next_question": "ask_next_question", "run_search": "run_search"}
)
graph_builder.add_edge("ask_next_question", END)
graph_builder.add_edge("run_search", "generate_itinerary")
graph_builder.add_edge("generate_itinerary", END)

# Compile the graph
travel_agent_app = graph_builder.compile()

# --- Gradio Interface ---

# Function to handle the conversation logic with LangGraph state
def handle_user_message(user_input: str, history: List[List[str | None]], current_state_dict: Optional[dict]) -> tuple:
    user_input_cleaned = user_input.strip().lower()

    # Initialize state if it doesn't exist (first interaction)
    if current_state_dict is None:
        current_state_dict = {
            "messages": [AIMessage(content=INITIAL_MESSAGE)],
            "user_info": {},
            "missing_fields": [], # Will be populated if user types START
            "search_results": None,
            "itinerary": None,
        }

    # Handle START command
    if user_input_cleaned == "start" and not current_state_dict.get("missing_fields"): # Only start if not already started
        print("--- Received START ---")
        current_state_dict["missing_fields"] = list(ORDERED_FIELDS) # Initialize missing fields
        current_state_dict["user_info"] = {} # Reset user info
        current_state_dict["messages"] = [AIMessage(content=START_CONFIRMATION)] # type: ignore
        # No graph execution needed yet, just update state and return the first question
        history.append([None, START_CONFIRMATION]) # Gradio format needs None for user message here

    # Handle case where user types something other than START initially
    elif not current_state_dict.get("missing_fields") and user_input_cleaned != "start":
         print("--- Waiting for START ---")
         current_state_dict["messages"] = current_state_dict["messages"] + [ # type: ignore
              HumanMessage(content=user_input),
              AIMessage(content=INVALID_START_MESSAGE)
         ]
         history.append([user_input, INVALID_START_MESSAGE])


    # Handle user responses after START
    elif current_state_dict.get("missing_fields") or current_state_dict.get("itinerary"): # Process if questions pending or itinerary just generated
        print(f"--- User Input: {user_input} ---")
         # Prevent processing if itinerary was just generated and user typed something else
        if current_state_dict.get("itinerary") and not current_state_dict.get("missing_fields"):
             print("--- Itinerary already generated, waiting for START OVER ---")
             # Optionally add a message like "Type START OVER to begin again."
             history.append([user_input, "Itinerary generated. Please click 'Start Over' to plan a new trip."])
             # Keep state as is, just update history
             return history, current_state_dict, ""


        # Add user message to state's messages list
        current_messages = current_state_dict.get("messages", [])
        current_messages.append(HumanMessage(content=user_input))
        current_state_dict["messages"] = current_messages

        # Invoke the graph
        print("--- Invoking Graph ---")
        # Ensure state keys match AgentState before invoking
        graph_input_state = AgentState(
             messages=current_state_dict.get("messages", []),
             user_info=current_state_dict.get("user_info", {}),
             missing_fields=current_state_dict.get("missing_fields", []),
             search_results=current_state_dict.get("search_results"),
             itinerary=current_state_dict.get("itinerary"),
        )
        # Use stream or invoke. Invoke is simpler for this request/response cycle.
        final_state = travel_agent_app.invoke(graph_input_state)
        print("--- Graph Execution Complete ---")

        # Update the state dictionary from the graph's final state
        current_state_dict.update(final_state)

        # Update Gradio history
        # The graph adds the AI response(s) to state['messages']
        # Get the *last* AI message added by the graph
        ai_response = final_state['messages'][-1].content if final_state['messages'] and isinstance(final_state['messages'][-1], AIMessage) else "Error: No response."
        history.append([user_input, ai_response])


    # Handle unexpected state (fallback)
    else:
        print("--- Unexpected State - Resetting ---")
        history.append([user_input, "Something went wrong. Please type START to begin."])
        current_state_dict = { # Reset state
            "messages": [AIMessage(content=INITIAL_MESSAGE)],
            "user_info": {},
            "missing_fields": [],
            "search_results": None,
            "itinerary": None,
        }


    # Return updated history, the persistent state dictionary, and clear the input box
    return history, current_state_dict, ""

# Function to reset the state (Start Over button)
def start_over() -> tuple:
    print("--- Starting Over ---")
    initial_state = {
        "messages": [AIMessage(content=RESTART_MESSAGE)],
        "user_info": {},
        "missing_fields": [],
        "search_results": None,
        "itinerary": None,
    }
    # Gradio history format: List of [user_msg, assistant_msg] pairs
    initial_history = [[None, RESTART_MESSAGE]]
    return initial_history, initial_state, "" # Return history, state, clear input


# --- Gradio UI Definition ---
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🌍 AI-Powered Travel Itinerary Generator (LangGraph Version)")
    gr.Markdown("Type `START` to begin planning your trip. Answer the questions, and I'll generate a personalized itinerary for you!")

    # Store the LangGraph state between interactions
    agent_state = gr.State(value=None) # Initialize state as None

    # Chat interface
    chatbot = gr.Chatbot(
        label="Travel Bot",
        bubble_full_width=False,
        value=[[None, INITIAL_MESSAGE]] # Initial message
        )
    user_input = gr.Textbox(label="Your Message", placeholder="Type here...", scale=3)
    submit_btn = gr.Button("Send", scale=1)
    start_over_btn = gr.Button("Start Over", scale=1)

    # Button and Textbox actions
    submit_btn.click(
        fn=handle_user_message,
        inputs=[user_input, chatbot, agent_state],
        outputs=[chatbot, agent_state, user_input] # Update chatbot, state, and clear input
    )
    user_input.submit( # Allow Enter key submission
         fn=handle_user_message,
        inputs=[user_input, chatbot, agent_state],
        outputs=[chatbot, agent_state, user_input]
    )
    start_over_btn.click(
        fn=start_over,
        inputs=[],
        outputs=[chatbot, agent_state, user_input] # Reset chatbot, state, and clear input
    )


# --- Run the App ---
if __name__ == "__main__":
    app.launch(debug=True)# Debug=True provides more logs
