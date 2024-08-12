''' coding: utf-8 '''
# ------------------------------------------------------------
# Content : Creating a tool for automcatically creating a meeting meniute using gpt-api
# Author : Yosuke Kawazoe
# Data Updated：
# Update Details：
# ------------------------------------------------------------

# Import
import os
import streamlit as st
import traceback
import tempfile
import logging
from dotenv import load_dotenv
# Used to securely store your API key
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# Config
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# ★★★★★★  main part ★★★★★★
# ------------------------------------------------------------
def main():

    try:
        # Streamlit app
        st.title("Travel Itinerary Suggestion App")

        # Sidebar selection
        user_type = st.sidebar.radio("Who is using this?", ("Me", "Others"))

        if user_type == "Me":
            # Load environment variables from .env file
            load_dotenv()
            GOOGLE_API_KEY = os.getenv("API_KEY")
        else:
            # set Gemini API
            GOOGLE_API_KEY = st.sidebar.text_input("Input your Google AI Studio API", type="password")

        genai.configure(api_key=GOOGLE_API_KEY)

        # Input fields
        traveling_days = st.number_input("Number of traveling days", min_value=1, max_value=99, value=3)
        destination = st.text_input("Destination")
        departure = st.date_input("Departure date")
        next_destination = st.text_input("Next destination (optional)")

        if st.button("Generate Itinerary"):
            if not destination:
                st.error("Please enter a destination.")
            else:
                try:
                    itinerary = suggest_travel_plan(traveling_days, destination, departure, next_destination)
                    st.markdown(itinerary)
                except ResourceExhausted as e:
                    st.error("Resource Exhausted: The request exceeded the available resources. Please try again later.", icon="🚨")
                    st.error(f"Details: {str(e)}")
                    logger.error(f"ResourceExhausted: {str(e)}")
                except Exception as e:
                    st.error("An unexpected error occurred.", icon="🚨")
                    st.error(f"Details: {str(e)}")
                    logger.error(f"Unexpected error: {str(e)}")
                    traceback.print_exc()
    except Exception:
        st.error("An unexpected error occurred in the main function.", icon="🚨")
        st.error(f"Details: {str(e)}")
        logger.error(f"Unexpected error in main: {str(e)}")
        traceback.print_exc()

# ------------------------------------------------------------
# ★★★★★★  functions ★★★★★★
# ------------------------------------------------------------
def suggest_travel_plan(traveling_days, destination, departure, next_destination):
    try:
        chat = model.start_chat(enable_automatic_function_calling=True)
        prompt = f"""
        ### request
        You are a professional travel planner.
        Please suggest travel plan based on my preference and duration.

        ### about me
        I am Japnese who loves travel abroad and have been to 31 countries so far. 
        What I like to do during travel is these below.
        - Exploring nature such as sea, lake and mountainds and feel the mother of earth.
        - Walking around the town and see beautiful places.
        - Meeting new people such as backpackers to change infomation about traveling tips and local people to get to know about local culture and history.
        - Eating local coffee and beer as well as food.

        ### prerequisite
        - duration : {traveling_days}days
        - destination : {destination}
        - departure : {departure}
        - next destination : {next_destination}

        """
        response = chat.send_message(prompt)
        response_text = response.text
        return response_text
    except Exception as e:
        logger.error(f"Error in summary_prompt_response: {str(e)}")
        raise


# ------------------------------------------------------------
# ★★★★★★  execution part  ★★★★★★
# ------------------------------------------------------------
if __name__ == '__main__':

    # execute
    main()