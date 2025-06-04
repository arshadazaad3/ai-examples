import streamlit as st
import webvtt
import openai
from io import StringIO
import tiktoken

# Page config with modern theme
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 5px;
    }
    .stCheckbox>div {
        padding: 0.5rem 0;
    }
    h1 {
        color: #1E88E5;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
    }
    h2 {
        color: #424242;
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
    }
    .stMarkdown {
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title with modern styling
st.markdown("<h1>📝 Teams Meeting Summarizer</h1>", unsafe_allow_html=True)

# Set the API key for the openai package
openai.api_key = st.secrets['OPENAI_API_KEY']

def num_tokens(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding_name = 'cl100k_base'
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def summarize(context: str, model:str, convo: str) -> str:
    """Returns the summary of a text string."""
    context = context
    completion = openai.chat.completions.create(
        model = model,
        messages=[
            {'role': 'system','content': context},
            {'role': 'user', 'content': convo}
        ]
    )
    return completion.choices[0].message.content

# Create two columns for better layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Configuration")
    context = st.text_input('Context', 'summarize the following conversation, with detailed bullet points')
    
    model = 'gpt-4o-mini'
    maxtokens = 128000
    st.info(f"Using {model} with {maxtokens:,} token limit")
    
    st.markdown("### Options")
    part = st.checkbox('Include participants', value=False)
    time = st.checkbox('Include timestamps', value=False)

with col2:
    st.markdown("### Upload VTT File")
    file = st.file_uploader('Upload Teams VTT transcript', type='vtt', help="Upload your Teams meeting transcript in VTT format")

if file is not None:
    data = StringIO(file.getvalue().decode('utf-8'))
    chat = webvtt.read_buffer(data)
    
    str = []
    for caption in chat:
        if part & time:
            str.append(f'{caption.start} --> {caption.end}')
            str.append(caption.raw_text)
        elif time:
            str.append(f'{caption.start} --> {caption.end}')
            str.append(caption.text)
        elif part:
            str.append(caption.raw_text)
        else:
            str.append(caption.text)
    
    sep = '\n'
    convo = sep.join(str)
    
    # Display transcript in an expander
    with st.expander("View Transcript", expanded=False):
        st.text_area('Transcript', convo, height=300)
    
    toknum = num_tokens(convo)
    st.metric("Token Count", f"{toknum:,}")
    
    if (toknum > maxtokens):
        st.error(f'Text too long. Please prune to fit under {maxtokens:,} tokens')
    else:
        if st.button('Generate Summary', type="primary"):
            with st.spinner('Generating summary...'):
                st.markdown("### Summary")
                st.markdown(summarize(context, model, convo))

else:
    st.info("👆 Please upload a VTT file to begin")
    with open('vtt/sample.vtt') as f:
        st.download_button(
            label="Download Sample VTT File",
            data=f,
            file_name="sample.vtt",
            mime="text/vtt",
            help="Download a sample VTT file to test the summarizer"
        )