import os
import time
import asyncio

# Import libraries from the Agent Framework
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from dotenv import load_dotenv
load_dotenv()

# Get the model ID from the environment variable
MODEL = os.getenv("MODEL", "gemini-2.0-flash") # The model ID for the agent
AGENT_APP_NAME = 'agent_basic'

# Create InMemory services for session and artifact management
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

async def send_query_to_agent(agent, query, user_id="user", session_id="user_session"):
    """Sends a query to the specified agent and prints the response.

    Args:
        agent: The agent to send the query to.
        query: The query to send to the agent.

    Returns:
        A tuple containing the elapsed time (in milliseconds) and the final response from the agent.
    """

    # Create a new session - if you want to keep the history of interruction you need to move the 
    # creation of the session outside of this function. Here we create a new session per query
    session = await session_service.create_session(app_name=AGENT_APP_NAME,
                                                   user_id=user_id,
                                                   session_id=session_id)
    # Create a content object representing the user's query
    print('\nUser Query: ', query)
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # Start a timer to measure the response time
    start_time = time.time()

    # Create a runner object to manage the interaction with the agent
    runner = Runner(app_name=AGENT_APP_NAME, agent=agent, artifact_service=artifact_service, session_service=session_service)
    # Alternatively you can use InMemoryRunner

    # Run the interaction with the agent and get a stream of events
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    final_response = None
    elapsed_time_ms = 0.0

    # Loop through the events returned by the runner
    async for event in events:

        is_final_response = event.is_final_response()

        if not event.content:
             continue

        if is_final_response:
            end_time = time.time()
            elapsed_time_ms = round((end_time - start_time) * 1000, 3)

            print("-----------------------------")
            print('>>> Inside final response <<<')
            print("-----------------------------")
            final_response = event.content.parts[0].text # Get the final response from the agent
            print(f'Agent: {event.author}')
            print(f'Response time: {elapsed_time_ms} ms\n')
            print(f'Final Response:\n{final_response}')
            print("----------------------------------------------------------\n")

    return elapsed_time_ms, final_response

if __name__ == '__main__':

    # Create a basic agent with instructions amd greeting only
    basic_agent = Agent(model=MODEL,
        name="agent_basic",
        description="This agent responds to inquiries about its creation by stating it was built using the Google Agent Development Kit.",
        instruction="If they ask you how you were created, tell them you were created with the Google Agent Development Kit.",
        generate_content_config=types.GenerateContentConfig(temperature=0.2),
    )

    # Send a single query to the agent
    asyncio.run(send_query_to_agent(basic_agent, "Hi, how are you?"))

    # Example of sending multiple queries to the agent (commented out)
    # queries = [
    #     "Hi, I am Tom",
    #     "Could you let me know what you could do for me?",
    #     "How were you built?",
    # ]

    # for query in queries:
    #     asyncio.run(send_query_to_agent(basic_agent, query))
