import os
from crewai import Agent, LLM
from tools.search_tools import search_internet
from tools.file_tools import read_file
from core.config import settings

class SoftwareEngineeringCrewAgents():

    def __init__(self):
        # We use CrewAI's native LLM wrapper for Ollama
        self.planner_llm = LLM(
            model=f"ollama/{settings.planner_model}",
            base_url=settings.ollama_base_url,
            temperature=0.7
        )
        
        self.coder_llm = LLM(
            model=f"ollama/{settings.backend_model}",
            base_url=settings.ollama_base_url,
            temperature=0.1
        )

    def planner_agent(self):
        return Agent(
            role='Principal Product Planner',
            goal='Analyze user requirements, search the web for industry standards, and define a comprehensive project plan with features and user stories.',
            backstory='You are a veteran product manager who specializes in translating vague ideas into concrete, buildable software plans. You frequently search the internet for competitor features and best practices to ensure the product is competitive.',
            tools=[search_internet],
            llm=self.planner_llm,
            verbose=True,
            allow_delegation=False
        )

    def architect_agent(self):
        return Agent(
            role='Lead Software Architect',
            goal='Design the technical architecture, database schema, and API endpoints based on the project plan.',
            backstory='You are a principal architect with 20+ years of experience. You design robust, scalable systems using modern tech stacks. You collaborate closely with developers to ensure the design is implementable.',
            tools=[search_internet],
            llm=self.coder_llm,
            verbose=True,
            allow_delegation=True # Architect can delegate questions to the Planner or Developers
        )

    def backend_developer_agent(self):
        return Agent(
            role='Senior Backend Developer',
            goal='Write robust backend code (FastAPI/Python) matching the architecture and database schema.',
            backstory='You are a senior backend engineer who writes clean, secure, and efficient Python code. You are meticulous about database interactions and API security.',
            tools=[read_file],
            llm=self.coder_llm,
            verbose=True,
            allow_delegation=False
        )

    def reviewer_agent(self):
        return Agent(
            role='QA & Code Reviewer',
            goal='Review the generated code for security, best practices, and exact match to the architectural requirements.',
            backstory='You are a strict code reviewer. You find bugs, security vulnerabilities, and logic flaws that others miss. You provide actionable feedback.',
            tools=[read_file],
            llm=self.planner_llm,
            verbose=True,
            allow_delegation=True # Can delegate back to the developer to fix code
        )
