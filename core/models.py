import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq


def get_local_llm():
    return ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.3,
    )


def get_groq_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )