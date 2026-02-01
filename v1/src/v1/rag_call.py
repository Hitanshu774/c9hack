import os
import glob

from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import gradio as gr

# import gradio as gr

load_dotenv(override=True)

#######################################
# import os
# print(os.getenv("API_KEY"))

