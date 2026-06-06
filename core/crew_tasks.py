from crewai import Task

class SoftwareEngineeringCrewTasks():

    def planning_task(self, agent, user_prompt):
        return Task(
            description=f"""
                Analyze the following user request for a new software project: "{user_prompt}".
                1. Search the internet for similar applications or industry standards for this type of software.
                2. Identify the target audience and core value proposition.
                3. Define the MVP (Minimum Viable Product) features.
                4. Write detailed user stories.
            """,
            expected_output="A structured markdown document containing the Project Vision, Target Audience, Features List, and User Stories.",
            agent=agent
        )

    def architecture_task(self, agent):
        return Task(
            description="""
                Based on the project plan created by the planner, design the technical architecture.
                1. Define the Tech Stack (Backend, Frontend, Database).
                2. Design the Database Schema (Tables, Columns, Relationships).
                3. Design the API Endpoints (Paths, Methods, Request/Response payloads).
                4. If needed, ask the Planner for clarification or use the internet to check latest framework best practices.
            """,
            expected_output="A detailed Technical Architecture Document including Database Schema and API Spec.",
            agent=agent
        )

    def coding_task(self, agent):
        return Task(
            description="""
                Based on the Technical Architecture Document, write the backend code.
                Focus on the core setup, database models, and the main API endpoints.
                Produce the actual Python code (FastAPI + SQLAlchemy).
            """,
            expected_output="The Python code for the main backend files (e.g., models.py, main.py).",
            agent=agent
        )

    def review_task(self, agent):
        return Task(
            description="""
                Review the backend code produced by the developer.
                1. Check for security vulnerabilities.
                2. Check if it matches the Database Schema and API Spec.
                3. If there are issues, delegate them back to the Developer to fix.
            """,
            expected_output="A Code Review Report with a 'PASS' or 'FAIL' status and list of required fixes.",
            agent=agent
        )
