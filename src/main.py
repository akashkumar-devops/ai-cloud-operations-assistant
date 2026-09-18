"""
Filename: main.py

Purpose
-------
FastAPI backend for the AI Cloud Operations Assistant.
"""

import time

from fastapi import FastAPI
from pydantic import BaseModel

from src.rag_engine import answer_question

app = FastAPI(
    title="AI Cloud Operations Assistant",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def root():

    return {
        "application": "AI Cloud Operations Assistant",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
    }


@app.post("/chat")
def chat(request: ChatRequest):

    start = time.perf_counter()

    result = answer_question(request.question)

    elapsed_ms = round(
        (time.perf_counter() - start) * 1000,
        2,
    )

    return {
        "question": result["question"],
        "answer": result["answer"],
        "sources": result["sources"],
        "retrieved_chunks": result["retrieved_chunks"],
        "processing_time_ms": elapsed_ms,
    }