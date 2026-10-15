import anthropic
import streamlit as st

from agent import chat

st.set_page_config(page_title="AI Trip Planner", page_icon="🧭")
st.title("AI Trip Planner")

if "messages" not in st.session_state:
    st.session_state.messages = []  # full conversation sent to the model
    st.session_state.shown = []  # (role, text) pairs to display


def send(text: str):
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.shown.append(("user", text))
    try:
        with st.spinner("Checking weather and places..."):
            reply = chat(st.session_state.messages)
    except anthropic.APIError as e:
        reply = f"Something went wrong calling the model: {e}"
    st.session_state.shown.append(("assistant", reply))


with st.sidebar:
    st.header("Trip details")
    destination = st.text_input("Destination", "Lisbon")
    days = st.slider("Days", 1, 10, 3)
    budget = st.selectbox("Budget", ["budget", "mid-range", "luxury"], index=1)
    interests = st.multiselect(
        "Interests",
        ["food", "history", "nature", "nightlife", "art", "beaches"],
        default=["food", "history"],
    )
    if st.button("Plan my trip", type="primary"):
        st.session_state.messages, st.session_state.shown = [], []
        send(
            f"Plan a {days}-day trip to {destination}. Budget: {budget}. "
            f"Interests: {', '.join(interests) or 'anything'}."
        )
    if st.button("Start over"):
        st.session_state.messages, st.session_state.shown = [], []

for role, text in st.session_state.shown:
    with st.chat_message(role):
        st.markdown(text)

# Feedback loop: whatever the user types goes back to the agent, which revises the plan.
if st.session_state.shown:
    feedback = st.chat_input("Give feedback, e.g. 'cheaper', 'more outdoors', 'swap day 2'")
    if feedback:
        send(feedback)
        st.rerun()
