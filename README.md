# Google ADK Walkthrough: Your Step-by-Step Development Tutorial
Get ready to dive deep and get hands-on with the Google Agent Development Kit! This walkthrough section provides a practical, step-by-step guide to building your first agentic solutions using the ADK library and code from our companion repository.

We'll start with the Prerequisites, ensuring your development environment is correctly set up – from installing ADK in a Python virtual environment to configuring necessary access credentials. Running a simple test script will confirm everything is ready to go.
Then, we'll progress through four core chapters:

**The Basic Agent *(chapter1_main_basic.py)*:** You'll learn how to instantiate your very first agent, defining its core instructions and interacting with it. We'll explore fundamental ADK components like the Agent class, the Runner, and basic session management (InMemorySessionService).

**Single Agent with Tools *(chapter2_main_single_agent.py)*:** We'll enhance our agent by giving it abilities! You'll see how to create custom tools using simple Python functions (complete with essential docstrings) and how the agent leverages these tools to perform tasks, like mathematical calculations. We'll also cover how to handle the event stream for tool calls and responses.

**Multi-Agent Interaction *(chapter3_main_multi_agent.py)*:** This is where we bring it all together. You'll learn how to design a system where multiple specialized agents collaborate. We'll build an orchestrator agent (a "teacher's assistant") that delegates tasks to child agents (like our math agent and a new grammar agent), demonstrating the power of the sub_agents parameter and defining interaction flows.

**[Placeholder] Agent Deployment to the Cloud (chapter4_agent_deployment.py):** We'll briefly touch upon the concepts and potential next steps involved in taking your agent application from local development to a live deployment, particularly focusing on cloud environments. 

Let's get started!

## Prerequisites 

Understand Agent Development Kit and its capabilities by reading the SDK.

Clone the walkthrough repository: [Repository](https://github.com/sokart/adk-walkthrough.git)

```shell
git clone https://github.com/sokart/adk-walkthrough.git
```

Create a new Python virtual environment (note: Python 3.11 is preferred, otherwise you should use the --ignore-requires-python parameter in pip3 install): 

```shell
python -m venv .adk_venv
source .adk_venv/bin/activate
```

Install Agent Development Kit:

```shell
pip install google-adk
```

```conf
Copy “dotenv.example” file and rename it to .env. Fill the Project, Location, and Default Model details as  global parameters:
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=FILL_YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=FILL_YOUR_LOCATION
MODEL=FILL_THE_DEFAULT_MODEL
```

Example:

```conf
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=gcp-project-genai
GOOGLE_CLOUD_LOCATION=us-central1
MODEL='gemini-2.0-flash-001'
```

Run your first agent example in a terminal, chapter1_main_basic.py. This is the simplest example of how to call an agent without tools. This will prove that you have setup the above correctly:

```shell
> python3 chapter1_main_basic.py

User Query:  Hi, how are you?
-----------------------------
>>> Inside final response <<<
-----------------------------
Agent: basic_agent
Response time: 1675.186 ms

Final Response:
I am doing well, thank you for asking. How can I help you today?

----------------------------------------------------------
```

Uncomment the last seven lines in chapter1_main_basic.py to test multiple queries with the agent.

If everything works, you have achieved to set up the Agent Development Kit correctly. Let’s deep dive on the key components of the basic agent starting with Chapter 1. Then, follow the increamental implementation of Chapter 2 and 3. Have fun!!!

## Author

Dr Sokratis Kartakis