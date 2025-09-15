import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

# -------------------------
# MCP Server Configuration
# -------------------------
MCP_SERVERS = {
    "amadeus": {
        "command": "npx",
        "args": ["@privilegemendes/amadeus-mcp-server"],
        "env": {
            "AMADEUS_CLIENT_ID": os.getenv("AMADEUS_CLIENT_ID"),
            "AMADEUS_CLIENT_SECRET": os.getenv("AMADEUS_CLIENT_SECRET"),
        },
        "transport": "stdio"
    }
}



# -------------------------
# Async setup
# -------------------------
async def setup_agent():
    client = MultiServerMCPClient(MCP_SERVERS)

   
    tools = await client.get_tools()

    

    llm = ChatOllama(model="mistral", temperature=0)
    agent = create_react_agent(llm, tools)
    return agent, client


# -------------------------
# Streamlit UI
# -------------------------
st.title("🌍 AI Travel Planner")

col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("Origin City", "Delhi")
    destination = st.text_input("Destination City", "London")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
with col2:
    preferences = st.text_area("Interests (comma separated)", "museums, food, architecture")
    budget = st.number_input("Budget (₹)", min_value=1000, max_value=1000000, value=20000)

run = st.button("Generate Itinerary")

# -------------------------
# Main logic
# -------------------------
if run:
    async def run_agent():
        agent, client = await setup_agent()

        query = f"""
        Plan a trip from {origin} to {destination}.
        Dates: {start_date} to {end_date}.
        Budget: ₹{budget}.
        Interests: {preferences}.
        
        Please include:
        1. Best airports
        2. Suggested all airline flights with approx price 
        3. Recommended hotels with approx price
        4. Popular tourist attractions at the destination
        5. Rough total cost
          also inclueds airline website link and hotel links to explore more
        """

        response = await agent.ainvoke({"messages": [("user", query)]})
        #await client.stop()
        return response

    with st.spinner("Planning your trip..."):
        result = asyncio.run(run_agent())
        st.write("## Your Personalized Itinerary")
        st.markdown(result["messages"][-1].content)
