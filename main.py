# import os
# import json
# import asyncio
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

load_dotenv()

# --- 1. Define Pydantic Models ---
class Paper(BaseModel):
    title: str 
    authors: list[str] 
    year: int
    abstract: str = Field(description="The abstract of the paper")
    publication_date: str = Field(description="The publication date of the paper")
    journal: str = Field(description="The journal in which the paper was published")

class Formula(BaseModel):
    name: str
    latex: str = Field(description="The LaTeX representation of the formula")
    description: str = Field(description="A brief description of the formula")
    formula: str = Field(description="The mathematical representation of the formula")

class Trend(BaseModel):
    topic: str
    description: str = Field(description="A brief description of the trend")
    examples: list[str] = Field(description="Examples of the trend in action")

class Report(BaseModel):
    topic: str
    papers: list[Paper]
    formulas: list[Formula]
    trends: list[Trend]

class ResearchRequest(BaseModel):
    topic: str
    research_questions: str
    timeframe: str

# --- 2. Initialize FastAPI ---
app = FastAPI(title="Local Research Assistant")

# --- 3. Define Routes ---
@app.get("/", response_class=HTMLResponse)
async def serve_webpage():
    """Serves the frontend HTML file."""
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/generate", response_model=Report)
async def generate_report(request: ResearchRequest):
    """Handles the form submission and calls the LLM."""
    task = f"""Topic:{request.topic}
Research Questions:{request.research_questions}
Timeframe:{request.timeframe}

Gather 5-10 highly relevant research papers, formulas, and trends related to the topic.
Then identify the most important papers, formulas, and trends, and provide a summary of each.
Populate the report schema fully"""
    
    model = init_chat_model(
        "gemini-3.1-flash-lite", 
        model_provider="google-genai"
    ).with_structured_output(Report)

    result = await model.ainvoke([
        {'role': 'system', 'content': 'You are a research assistant that specializes in gathering and summarizing information on various topics.'},
        {'role': 'user', 'content': task}
    ])

    return result