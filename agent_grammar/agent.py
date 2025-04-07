import os
from dotenv import load_dotenv

# Construct the path to the .env file in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')

# Load the environment variables from the .env file
load_dotenv(dotenv_path)

# Now you can access your environment variables using os.getenv()
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

from google.adk.agents import Agent

from google import genai
from google.genai.types import (
    GenerateContentConfig,
)

MODEL_AGENT = "gemini-2.0-flash-001"
MODEL_TOOL = "gemini-2.0-flash-001"

def check_grammar(text_input: str) -> dict:
    """Checks the grammar of input text and returns corrections and explanations.

    This function uses the Gemini API to analyze the provided text for 
    grammatical errors. It returns a dictionary containing the corrected 
    text, explanations of the errors, and descriptions of the errors.  The 
    Gemini API is called with a prompt requesting a JSON response in a 
    specific format.  The function handles potential errors in communicating
    with the Gemini API and parsing the JSON response.

    Args:
        text_input: The input text to be checked for grammar errors.

    Returns:
        A dictionary containing the following keys:
            "corrected_text": The text with grammatical errors corrected, or None 
                            if an error occurred.
            "explanations": A list of strings explaining each correction made, or
                            a list containing an error message if an error occurred.
            "errors": A list of strings describing each error found.  This may
                      be an empty list if no errors were found or if an error
                      occurred during processing.

        The dictionary structure is designed to conform to the following JSON schema:

        ```json
        {
          "type": "object",
          "properties": {
            "corrected_text": {
              "type": "string",
              "description": "The corrected text."
            },
            "explanations": {
              "type": "array",
              "items": {
                "type": "string",
                "description": "Explanation of a specific error."
              },
              "description": "An array of explanations for each correction."
            },
            "errors": {
              "type": "array",
              "items": {
                "type": "string",
                "description": "Description of a specific error."
              },
              "description": "An array of descriptions of each error."
            }
          },
          "required": [
            "corrected_text",
            "explanations",
            "errors"
          ],
          "description": "A JSON object containing corrected text, explanations, and error descriptions."
        }
        ```

        If an error occurs during communication with the Gemini API or parsing
        the JSON response, the "corrected_text" will be None and the "explanations"
        list will contain an error message. The "errors" list might be empty
        in such cases.
    """

    prompt = f"""
    Analyze the following text for grammar errors, correct them, and provide 
    explanations for each correction:

    Text: {text_input}

    Return the response as a JSON object with the following structure:
    {{
      "corrected_text": "The corrected text.",
      "explanations": [
        "Explanation of the first error.",
        "Explanation of the second error.",
        ...
      ],
      "errors": [
          "Description of the first error",
          "Description of the second error",
          ...
      ]
    }}
    """

    response_schema = {
      "type": "object",
      "properties": {
        "corrected_text": {
          "type": "string",
          "description": "The corrected text."
        },
        "explanations": {
          "type": "array",
          "items": {
            "type": "string",
            "description": "Explanation of a specific error."
          },
          "description": "An array of explanations for each correction."
        },
        "errors": {
          "type": "array",
          "items": {
            "type": "string",
            "description": "Description of a specific error."
          },
          "description": "An array of descriptions of each error."
        }
      },
      "required": [
        "corrected_text",
        "explanations",
        "errors"
      ],
      "description": "A JSON object containing corrected text, explanations, and error descriptions."
    }

    try:
        client = genai.Client(vertexai=True, project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

        contents = [prompt]

        response = client.models.generate_content(model=MODEL_TOOL, 
                                                  contents=contents,
                                                  config=GenerateContentConfig(
                                                  response_mime_type="application/json",
                                                  response_schema=response_schema,
                                              ))

        try:
             return response.parsed
        except Exception as e:
            return {
                    "corrected_text": None,
                    "explanations": [f"Error parsing Gemini response: {e}"],
                    "errors": []
                  }

    except Exception as e:
        return {
                  "corrected_text": None,
                  "explanations": [f"Error communicating with Gemini: {e}"],
                  "errors": []
                }  

agent_grammar = Agent(
    model=MODEL_AGENT,
    name='agent_grammar',
    description="This agent corrects grammar mistakes in text provided by children, explains the errors in simple terms, and returns both the corrected text and the explanations.",
    instruction="""
        You are a friendly grammar helper for kids.  Analyze the following text, 
        correct any grammar mistakes, and explain the errors in a way that a 
        child can easily understand.  Don't just list the errors; explain them 
        in a paragraph using simple but concise language.

        First, provide the corrected text.

        Then, leave two new lines.

        Finally, provide the explanation. If there are no errors, reply with an empty string "".
    """,
    tools=[check_grammar],
)