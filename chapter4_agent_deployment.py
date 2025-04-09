import os
import time
import json

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from google.adk.agents import SequentialAgent

from agent_maths.agent import agent_math
from agent_grammar.agent import agent_grammar
from agent_summary.agent import agent_summary

from google.cloud import storage
from google.cloud import exceptions
from typing import Optional, Tuple # Import Tuple

from dotenv import load_dotenv
load_dotenv()

# Get the model ID from the environment variable
MODEL = os.getenv("MODEL", "gemini-2.0-flash-001") # The model ID for the agent

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

AGENT_ENGINE_BUCKET = f"ae-{GOOGLE_CLOUD_PROJECT}-{GOOGLE_CLOUD_LOCATION}-bucket"

IS_REMOTE_DEPLOYMENT = 0

def check_or_create_gcs_bucket_with_url(bucket_name: str, location: str, project_id: str = None) -> Optional[Tuple[str, storage.Bucket]]:
    """
    Checks if a Google Cloud Storage bucket exists. Creates it if it doesn't,
    otherwise retrieves it. Returns the bucket's gs:// URL and the Bucket object.

    Args:
        bucket_name: The globally unique name for the bucket.
                     (Must follow GCS naming rules).
        location: The location (region or multi-region) to create the bucket in
                  if it doesn't exist (e.g., 'US-EAST1', 'EUROPE-WEST2', 'US').
        project_id: Your Google Cloud project ID. If None, the client library
                    tries to infer it from the environment credentials.

    Returns:
        A tuple containing (bucket_url, bucket_object) where:
          - bucket_url (str): The GCS URL (e.g., "gs://your-bucket-name").
          - bucket_object (storage.Bucket): The Bucket object.
        Returns None if a fatal error occurred preventing retrieval or creation.

    Raises:
        google.cloud.exceptions.Forbidden: If permissions are insufficient.
        Other google.cloud.exceptions: For various GCS API errors.
    """
    try:
        storage_client = storage.Client(project=project_id)
        print(f"Using project: {storage_client.project}")

        try:
            # Check if bucket exists
            bucket = storage_client.get_bucket(bucket_name)
            bucket_url = f"gs://{bucket.name}" # Construct the URL
            print(f"\nBucket '{bucket_name}' already exists.")
            print(f"  Bucket URL: {bucket_url}")
            return bucket_url, bucket # Return URL and object

        except exceptions.NotFound:
            print(f"\nBucket '{bucket_name}' not found. Attempting to create...")
            print(f"Creating bucket '{bucket_name}' in location '{location}'...")
            try:
                # Create the bucket
                new_bucket = storage_client.create_bucket(bucket_name, location=location)
                bucket_url = f"gs://{new_bucket.name}" # Construct the URL
                print(f"Bucket '{new_bucket.name}' created successfully.")
                print(f"  Bucket URL: {bucket_url}")

                return bucket_url, new_bucket # Return URL and object

            except exceptions.Conflict as e:
                print(f"Error: Conflict during creation of bucket '{bucket_name}'. Checking if it exists now...")
                try:
                    # Attempt to get the bucket again in case of race condition
                    existing_bucket = storage_client.get_bucket(bucket_name)
                    bucket_url = f"gs://{existing_bucket.name}"
                    print(f"Bucket '{existing_bucket.name}' found after conflict.")
                    print(f"  Bucket URL: {bucket_url}")
                    # You might want to print metadata here too if needed
                    return bucket_url, existing_bucket # Return existing bucket info
                except exceptions.NotFound:
                     print(f"Bucket '{bucket_name}' still not found after conflict. Creation failed.")
                     return None
                except Exception as get_e:
                     print(f"Error trying to get bucket after conflict: {get_e}")
                     return None
            except exceptions.Forbidden as e:
                 print(f"Error: Permission denied to create bucket '{bucket_name}'. Details: {e}")
                 raise
            except Exception as create_e:
                 print(f"An unexpected error occurred during bucket creation: {create_e}")
                 return None

    except exceptions.Forbidden as e:
        print(f"Error: Permission denied. Details: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def parse_event_content(event: dict) -> list:
    """
    Parses the 'content' section of an event dictionary to extract text,
    function calls, or function responses from the 'parts' list.

    Args:
        event: The event dictionary to parse.

    Returns:
        A list of tuples. Each tuple contains (events type, content)
        Returns an empty list if the structure is invalid or no 
        relevant parts are found.
    """
    results = []
    
    # Use .get() for safer access in case keys are missing
    content = event.get('content')
    if not isinstance(content, dict):
        # print("Warning: 'content' key missing or not a dictionary in event.")
        return results # Return empty list if content is missing/wrong type

    parts = content.get('parts')
    if not isinstance(parts, list):
        # print("Warning: 'parts' key missing or not a list in event['content'].")
        return results # Return empty list if parts is missing/wrong type

    # Iterate through each dictionary in the 'parts' list
    for part in parts:
        if not isinstance(part, dict):
            # print(f"Warning: Item in 'parts' is not a dictionary: {part}")
            results.append(('unknown', part)) # Handle non-dict items if necessary
            continue # Skip to the next item

        if 'text' in part:
            print("-----------------------------")
            print('>>> Inside final response <<<')
            print("-----------------------------")
            print(part['text'])
            results.append(('text', part['text']))
        elif 'function_call' in part:
            print("-----------------------------")
            print('+++ Inside function call +++')
            print("-----------------------------")
            print(f"Call Function: {part['function_call']['name']}")
            print(f"Argument: {part['function_call']['args']}")
            # Found a function call part
            results.append(('function_call', part['function_call']))
        elif 'function_response' in part:
            print("------------------------------")
            print('-- Inside function response --')
            print("------------------------------")
            print(f"Function Response: {part['function_response']['name']}")
            print(f"Response: {part['function_response']['response']}")
            results.append(('function_response', part['function_response']))
        else:
            # The part dictionary doesn't contain any of the expected keys
            # print(f"Warning: Unknown structure in part: {part}")
            print(f'Unknown part: {part}')
            results.append(('unknown', part))

    return results


if __name__ == '__main__':

    result = check_or_create_gcs_bucket_with_url(bucket_name=AGENT_ENGINE_BUCKET,
                                                 location=GOOGLE_CLOUD_LOCATION,
                                                 project_id=GOOGLE_CLOUD_PROJECT)

    if result:
        bucket_url, bucket_object = result # Unpack the tuple
        print(f"\nBucket is ready available to AgentEngine")
        print(f"  Returned URL: {bucket_url}")
        print(f"  Bucket Object Name: {bucket_object.name}")
    else:
        print(f"\nFailed to process AgentEngine bucket '{AGENT_ENGINE_BUCKET}'. Check logs and permissions.")
        exit()

    vertexai.init( project=GOOGLE_CLOUD_PROJECT, 
                  location=GOOGLE_CLOUD_LOCATION,
                  staging_bucket=bucket_url,)
    
    agent_teaching_assistant = SequentialAgent(
        name="agent_teaching_assistant",
        description="This agent acts as a friendly teaching assistant, checking the grammar of kids' questions, performing math calculations using corrected or original text (if grammatically correct), and providing results or grammar feedback in a friendly tone.",
        sub_agents=[agent_grammar, agent_math, agent_summary],
    )

    if(IS_REMOTE_DEPLOYMENT == 0):
        deployed_agent = AdkApp(agent=agent_teaching_assistant,enable_tracing=True,)
    else:
        deployed_agent = agent_engines.create(agent_teaching_assistant, requirements=["google-cloud-aiplatform[adk,agent_engines]"])

    session = deployed_agent.create_session(user_id="user")
    print("-----------------------------")
    print('>>>  New session details  <<<')
    print("-----------------------------")
    print(session)

    print("-----------------------------")
    print('>>>>>>  List sessions  <<<<<<')
    print("-----------------------------")
    print(deployed_agent.list_sessions(user_id="user"))

    print("-----------------------------")
    print('>>>>>>  Get sessions  <<<<<<')
    print("-----------------------------")
    session = deployed_agent.get_session(user_id="user", session_id=session.id)
    print(session)

    print("-----------------------------")
    print('>>>> Interact with Agent <<<<')
    print("-----------------------------")
    start_time = time.time()
    
    events = deployed_agent.stream_query(user_id="user", session_id=session.id,message="Hi teacher. Could she help me to multiply all the numbers between 1 and 10?",)
    
    end_time = time.time()
    elapsed_time_ms = round((end_time - start_time) * 1000, 3)

    for event in events:
        parse_event_content(event)

    if(IS_REMOTE_DEPLOYMENT == 1):
        print("-----------------------------")
        print('>>> Deleting Remote Agent <<<')
        print("-----------------------------")
        deployed_agent.delete(force=True)