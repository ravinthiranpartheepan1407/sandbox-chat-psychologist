import streamlit as st
import urllib.request
import json
import os
import ssl

st.set_page_config(
    page_title="Chat Psychologist AI Sandbox"
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-color: 'black';
        color: 'white';
    }
    [data-testid="stHeader"] {
        display: none;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Allow self-signed HTTPS certificates
def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

# Function to get response from Azure-based LLM
def get_response(prompt, api_key):
    data = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 1,
        "stream": False
    }

    body = str.encode(json.dumps(data))

    url = 'https://Phi-3-small-8k-instruct-sotgr.eastus2.models.ai.azure.com/v1/chat/completions'
    headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        result_json = json.loads(result)
        return result_json['choices'][0]['message']['content']
    except urllib.error.HTTPError as error:
        return f"The request failed with status code: {error.code}\n{error.read().decode('utf8', 'ignore')}"

# Function to check if the prompt is psychology-related
def is_psychology_related(prompt):
    psychology_keywords = [
        'psychology', 'mental health', 'cognitive', 'behavior', 'therapy', 'therapist', 'counseling',
        'psychiatry', 'psychiatrist', 'psychotherapy', 'DSM-5', 'diagnosis', 'disorder', 'treatment',
        'depression', 'anxiety', 'stress', 'bipolar', 'schizophrenia', 'OCD', 'PTSD', 'ADHD', 'autism',
        'personality disorder', 'eating disorder', 'substance abuse', 'addiction', 'trauma', 'phobia'
    ]
    return any(keyword.lower() in prompt.lower() for keyword in psychology_keywords)

# Streamlit app layout
st.title("Chat Psychologist")
api_key = st.text_input("Enter your API key:", type="password")
prompt = st.text_area("Enter your prompt here:")
if st.button("Process"):
    if not api_key:
        st.error("Please provide an API key.")
    elif not prompt:
        st.error("Please provide a prompt.")
    elif not is_psychology_related(prompt):
        st.error("Please provide a psychology or DSM-5 related prompt.")
    else:
        with st.spinner('Processing...'):
            response = get_response(prompt, api_key)
            st.success("Done!")
            st.write("Response:")
            st.write(response)
