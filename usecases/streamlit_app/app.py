import os
import subprocess
import sys

try:
    import streamlit as st
except ImportError:
    user_agree = input("The feature you're trying to use requires an additional library(s):streamlit. Would you like to install it now? [y/N]: ")
    if user_agree.lower() == 'y':
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        import streamlit as st
    else:
        raise ImportError("The required 'streamlit' is not installed.")
from beyondllm import generator

from beyondllm.llms import GeminiModel
from beyondllm import generator
from ingest import get_retriever

st.title("Chat with files")

# Google API Key
st.text("Enter Google API Key")
google_api_key = st.text_input("Google API Key:", type="password")
os.environ['GOOGLE_API_KEY'] = google_api_key

# VectorDB and file options
vectordb_options = ['Chroma', 'Pinecone']
file_options = ['csv', 'pdf', 'doc', 'docx']

with st.sidebar:
    st.title("VectorDB Options")
    vectordb_type = st.selectbox("Select VectorDB Type", 
                                 vectordb_options, 
                                 index=0)

    if vectordb_type == 'Pinecone':
        # get the pinecone api key and index name
        pinecone_api_key = st.text_input("Pinecone API Key:", 
                                         type="password")
        pinecone_index_name = st.text_input("Pinecone Index Name:")
        
        # choose whether to use an existing index or create a new one
        st.subheader("Pinecone Options")
        pinecone_option = st.radio("Choose Option", 
                                   ('Existing', 'Create New'), 
                                   index=0)
        
        # choose whether you want to use the default embedding dimension or specify your own
        pinecone_embedding_dim = st.number_input("Embedding Dimension", 
                                                min_value=1, 
                                                max_value=2048, 
                                                value=768)
        
        # choose whether you want to use the default metric or specify your own, choose between "cosine" and "euclidean"
        pinecone_metric = st.selectbox("Metric", 
                                      ["cosine", "euclidean"], 
                                      index=0)
        
        # choose whether you want to use the default cloud or specify your own
        pinecone_cloud = st.selectbox("Cloud",
                                      ["aws", "gcp", "azure"], 
                                      index=0)
        
        # put the name of the region you want to use
        pinecone_region = st.text_input("Region:")

if google_api_key:
    st.success("Google API Key entered successfully!")
    file_type = st.selectbox("Select File Type",
                            file_options,
                            index=0)
    uploaded_file = st.file_uploader("Choose a file", type=file_options)
    if uploaded_file is not None:
        st.success("file uploaded successfully!")
    question = st.text_input("Enter your question")

    if uploaded_file is not None and question:
        # Get the retriever
        if vectordb_type == 'Pinecone':
            retriever = get_retriever(uploaded_file, 
                                      google_api_key, 
                                      vector_db=vectordb_type.lower(), 
                                      pinecone_api_key=pinecone_api_key, 
                                      pinecone_index_name=pinecone_index_name, 
                                      pinecone_option=pinecone_option,
                                      pinecone_embedding_dim=pinecone_embedding_dim,
                                      pinecone_metric=pinecone_metric,
                                      pinecone_cloud=pinecone_cloud,
                                      pinecone_region=pinecone_region,
                                      file_type=file_type)
        elif vectordb_type == 'Chroma':
            retriever = get_retriever(uploaded_file, 
                                      google_api_key, 
                                      vector_db=vectordb_type.lower(),
                                      file_type=file_type)
        # Initialize the LLM
        llm = GeminiModel(model_name="gemini-pro",
                          google_api_key = os.environ.get('GOOGLE_API_KEY'))
        # Initialize the system prompt
        system_prompt = "You are an AI assistant, who answers questions based on uploaded files. You can answer anything about the data."
        # Initialize the generator
        pipeline = generator.Generate(question=question,
                                      retriever=retriever, 
                                      llm=llm, 
                                      system_prompt=system_prompt)
        # Generate the response
        response = pipeline.call()
        # display the response
        st.write(response)

