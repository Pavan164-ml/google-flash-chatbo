import json
import os
import urllib.request

# --- Function to Query Gemini API ---
def query_gemini(api_key, prompt):
    """
    Sends a prompt to the Google Gemini API using urllib.
    """
    # WHY: Google Gemini provides a REST API endpoint that requires authentication via API key.
    #      The API key is passed as a query parameter in the URL as per Google's documentation.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    # WHY: The API expects a JSON payload, so we set the appropriate header.
    headers = {'Content-Type': 'application/json'}
    
    # WHY: Gemini API expects a specific nested JSON structure for the prompt.
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    # WHY: The request body must be bytes, so we encode the JSON string.
    encoded_data = json.dumps(data).encode('utf-8')
    
    # WHY: Create an HTTP request object with the URL, data, and headers.
    req = urllib.request.Request(url, data=encoded_data, headers=headers)
    
    # WHY: Use a context manager to make the request and ensure the response is properly closed.
    #      The response is parsed from JSON into a Python dictionary for further processing.
    with urllib.request.urlopen(req) as response:
        response_body = response.read().decode('utf-8')
        return json.loads(response_body)

# --- Main Lambda Handler ---
def lambda_handler(event, context):
    """
    AWS Lambda handler for Gemini.
    Receives a prompt from API Gateway, queries the Gemini model, and returns the response.
    """
    try:
        # WHY: Store sensitive API keys in environment variables for security and easy rotation.
        google_api_key = os.environ['GOOGLE_API_KEY']
        
        # WHY: Lambda receives requests from API Gateway as JSON strings in the 'body' field.
        #      Parse the body to extract the user's prompt.
        body = json.loads(event.get('body', '{}'))
        user_prompt = body.get('prompt')

        # WHY: Validate input early to avoid unnecessary API calls and provide clear client feedback.
        if not user_prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No prompt provided'})
            }

        # WHY: Query Gemini API with the user's prompt using the helper function.
        gemini_response = query_gemini(google_api_key, user_prompt)
        
        # WHY: The Gemini API nests the generated text inside several layers.
        #      Extract the actual AI-generated message for the client.
        bot_message = gemini_response['candidates'][0]['content']['parts'][0]['text']

        # WHY: Return a JSON response with CORS headers so web clients can access the API.
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Allows requests from any origin (for web apps)
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'response': bot_message})
        }

    except urllib.error.HTTPError as e:
        # WHY: Catch HTTP errors from the Gemini API (e.g., invalid key, quota exceeded)
        #      Log details for debugging and return a generic error to the client.
        error_details = e.read().decode()
        print(f"HTTP Error: {e.code} {e.reason}. Details: {error_details}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Failed to query the Gemini model.'})
        }
    except (KeyError, IndexError) as e:
        # WHY: The Gemini response structure might change or be malformed.
        #      Catch these errors to avoid Lambda crashes and log the full response for debugging.
        print(f"Error parsing Gemini response: {e}")
        print(f"Full response received: {gemini_response}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Unexpected response format from the model.'})
        }
    except Exception as e:
        # WHY: Catch any other unexpected errors to prevent Lambda from crashing,
        #      and provide a generic error message to the client.
        print(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'An internal server error occurred.'})
        }
