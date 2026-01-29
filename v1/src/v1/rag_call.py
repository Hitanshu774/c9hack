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

## relaoding the vectordb without re-embedding
from langchain_huggingface import HuggingFaceEmbeddings
embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5"
)

vectordb = Chroma(
    persist_directory="./vector_db",
    embedding_function=embedding
)

retreiver = vectordb.as_retriever(search_type="similarity",search_kwargs={"k": 5})

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="tngtech/tng-r1t-chimera:free",  # example
    openai_api_key=os.getenv("API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.1,
    top_p=0.9,
    max_tokens=512,
)

SYSTEM_PROMPT_TEMPLATE = """
You are an AI Scouting Analyst for professional VALORANT esports.

Your task is to generate concise, data-grounded scouting insights about an upcoming opponent
using ONLY the provided retrieved context from official match data.

STRICT RULES:
1. You must rely exclusively on the retrieved context.
2. Do NOT use outside knowledge, assumptions, or general VALORANT meta knowledge.
3. If the context does not contain enough information to answer a question, explicitly say:
   "Insufficient data available in the provided matches."
4. Do NOT speculate, predict outcomes, or invent tendencies.
5. Do NOT generalize beyond the scope of the provided series or maps.

OUTPUT STYLE:
- Write in clear, professional analyst language.
- Prefer bullet points over paragraphs.
- Be factual, neutral, and concise.
- Avoid hype, opinions, or narrative storytelling.

ALLOWED INSIGHTS (only if supported by context):
- Map-specific tendencies
- Agent compositions and pick patterns
- Player agent usage and consistency
- Observed attack or defense preferences
- Repeated behaviors across rounds or maps

DISALLOWED CONTENT:
- Predictions or win probabilities
- Coaching advice not supported by data
- Claims like "always", "never", or "dominant"
- Long-term trends beyond the given data
- Subjective judgments (e.g., "strong", "weak")

STRUCTURE YOUR RESPONSE AS:
- Section headers (e.g., "Map Tendencies", "Player Tendencies")
- Bullet points under each section
- A short "Key Takeaways" section with 2–3 bullets max

Remember:
Accuracy and restraint are more important than completeness.

"""

def answer_question(question: str, history):
    docs = retreiver.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
    return response.content

gr.ChatInterface(answer_question).launch(share=True)