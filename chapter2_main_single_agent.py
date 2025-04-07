import os
import time

from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent_maths.agent import agent_math

from dotenv import load_dotenv
load_dotenv()

# Get the model ID from the environment variable
MODEL = os.getenv("MODEL", "gemini-2.0-flash-001") # The model ID for the agent
AGENT_APP_NAME = 'single_agent'

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

def send_query_to_agent(agent, query):
    """Sends a query to the specified agent and prints the response.

        Args:
            agent: The agent to send the query to.
            query: The query to send to the agent.

        Returns:
            A tuple containing the elapsed time (in milliseconds) and the final response from the agent.
    """

    # Create a new session - if you want to keep the history of interruction you need to move the 
    # creation of the session outside of this function. Here we create a new session per query
    session = session_service.create_session(app_name=AGENT_APP_NAME,
                                             user_id='user',)
    
    # Create a content object representing the user's query
    print('\nUser Query: ', query)
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # Start a timer to measure the response time
    start_time = time.time()

    # Create a runner object to manage the interaction with the agent
    runner = Runner(app_name=AGENT_APP_NAME, agent=agent, artifact_service=artifact_service, session_service=session_service)

    # Run the interaction with the agent and get a stream of events
    events = runner.run(user_id='user', session_id=session.id, new_message=content)

    final_response = None
    elapsed_time_ms = 0.0

    # Loop through the events returned by the runner
    for _, event in enumerate(events):

        is_final_response = event.is_final_response()
        function_calls = event.get_function_calls()
        function_responses = event.get_function_responses()

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
        elif function_calls:
            print("-----------------------------")
            print('+++ Inside function call +++')
            print("-----------------------------")
        
            print(f'Agent: {event.author}')
            for function_call in function_calls:
                print(f'Call Function: {function_call.name}')
                print(f'Argument: {function_call.args}')
        elif function_responses:
            print("------------------------------")
            print('-- Inside function response --')
            print("------------------------------")

            print(f'Agent: {event.author}')
            for function_response in function_responses:
                    print(f'Function Name: {function_response.name}')
                    print(f'Function Results: {function_response.response}')

    return elapsed_time_ms, final_response

if __name__ == '__main__':

    # Send a single query to the agent
    send_query_to_agent(agent_math, "First multiply numbers 1 to 3 and then add 4")
    #send_query_to_agent(agent_math, "How much is 1 and 2 and 3?")

    # Send multiple queries against the basic agent
    # queries = [
    #     "Multiply 1 and 10",
    #     "Add 123 and 3 and 4",
    #     "Multiply the numbers between 1 and 10",
    # ]

    # for query in queries:
    #     send_query_to_agent(agent_math, query)
