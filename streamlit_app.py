import streamlit as st
import time
from chat_ds.query_builder import build_query
from chat_ds.chart_builder import build_charts
from chat_ds.query_runner import run_query
from io import StringIO
import os
from dotenv import load_dotenv, find_dotenv
from decouple import config

DEFAULT_CHAT_MODEL = 'gpt-3.5-turbo-16k'

st.set_page_config(page_icon='📊', page_title='Data Science Assistant')
st.title('Data Science Assistant 📊')


#------------------ setup ------------------#

# check if variables are set in .env
if config("OPENAI_API_KEY", None):
    st.session_state['openai_api_key'] = config("OPENAI_API_KEY")
if config("SNOWFLAKE_ACCOUNT", None):
    st.session_state['snowflake_account'] = config("SNOWFLAKE_ACCOUNT")
if config("SNOWFLAKE_USER", None):
    st.session_state['snowflake_user'] = config("SNOWFLAKE_USER")
if config("SNOWFLAKE_PASSWORD", None):
    st.session_state['snowflake_password'] = config("SNOWFLAKE_PASSWORD")
if config("SNOWFLAKE_DATABASE", None):
    st.session_state['snowflake_database'] = config("SNOWFLAKE_DATABASE")
if config("SNOWFLAKE_SCHEMA", None):
    st.session_state['snowflake_schema'] = config("SNOWFLAKE_SCHEMA")


st.sidebar.title("API Keys 🔑")

openai_api_key = st.sidebar.text_input(
    "Enter Your **OpenAI** API Key 🗝️", 
    value=st.session_state.get('openai_api_key', ''),
    help="Get your API key from https://openai.com/",
    type='password'
)
os.environ["OPENAI_API_KEY"] = openai_api_key
st.session_state['openai_api_key'] = openai_api_key
load_dotenv(find_dotenv())

with st.sidebar.expander('Advanced Settings ⚙️', expanded=False):
    open_ai_model = st.text_input('OpenAI Chat Model', DEFAULT_CHAT_MODEL, help='See model options here: https://platform.openai.com/docs/models/overview')   

st.sidebar.title("Data Setup ⚙️")
uploaded_file = st.sidebar.file_uploader("Upload dbt yaml file describing your tables", type=["yaml", "yml"])

if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    yml_file_str = stringio.read()


st.sidebar.markdown("### Snowflake Credentials ❄️")
snowflake_account = st.sidebar.text_input("Snowflake Account", value=st.session_state.get('snowflake_account', ''), type='password')
st.session_state['snowflake_account'] = snowflake_account
snowflake_user = st.sidebar.text_input("Snowflake User", value=st.session_state.get('snowflake_user', ''), type='password')
st.session_state['snowflake_user'] = snowflake_user
snowflake_password = st.sidebar.text_input("Snowflake Password", value=st.session_state.get('snowflake_password', ''), type='password')
st.session_state['snowflake_password'] = snowflake_password
snowflake_database = st.sidebar.text_input("Snowflake Database", value=st.session_state.get('snowflake_database', ''))
st.session_state['snowflake_database'] = snowflake_database
snowflake_schema = st.sidebar.text_input("Snowflake Schema", value=st.session_state.get('snowflake_schema', ''))
st.session_state['snowflake_schema'] = snowflake_schema


# ------------------------------ the streamlit app ------------------------------
message = st.chat_message("assistant")
message.write("👋🏻 I'm your **Data Science Assistant** - Ask me a question about your data 📊")

prompt = st.chat_input(
    """How many active customers do I have?
    """
)
# prompt = st.chat_input(
#     """Create me a bar chart of the number of users I have stuck at each stage in their user journey 
# in their first 30 days after signing up for users that signed up in the last 90 days.
#     """
# )

if prompt:
    message = st.chat_message("user")
    message.write(prompt)

    with st.status("Running...", expanded=True):
        st.write("Creating the query...")
        query = build_query(prompt, yml_file_str, open_ai_model)
        st.markdown(f"""Query:
```sql
{query}
```
"""
        )
        st.write("Running the query...")
        df = run_query(query, snowflake_user, snowflake_password, snowflake_account, snowflake_database, snowflake_schema)
        st.write("Building the charts...")
        result_code = build_charts(prompt, df, open_ai_model)
    
    with st.chat_message("assistant"):
        st.write('Here are the results:')
        exec(result_code)



