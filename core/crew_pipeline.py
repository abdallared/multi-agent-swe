from crewai import Crew, Process
from agents.crew_agents import SoftwareEngineeringCrewAgents
from core.crew_tasks import SoftwareEngineeringCrewTasks

class CrewPipeline:
    def __init__(self):
        self.agents = SoftwareEngineeringCrewAgents()
        self.tasks = SoftwareEngineeringCrewTasks()

    def run(self, user_prompt: str):
        print(f"\n================================================")
        print(f"🚀 Kicking off CrewAI Pipeline")
        print(f"================================================\n")

        # Initialize Agents
        planner = self.agents.planner_agent()
        architect = self.agents.architect_agent()
        developer = self.agents.backend_developer_agent()
        reviewer = self.agents.reviewer_agent()

        # Initialize Tasks
        planning_task = self.tasks.planning_task(planner, user_prompt)
        architecture_task = self.tasks.architecture_task(architect)
        coding_task = self.tasks.coding_task(developer)
        review_task = self.tasks.review_task(reviewer)

        # Assemble the Crew
        # We use Hierarchical process or Sequential. Sequential is easier to start with.
        crew = Crew(
            agents=[planner, architect, developer, reviewer],
            tasks=[planning_task, architecture_task, coding_task, review_task],
            process=Process.sequential,
            verbose=True
        )

        # Start the execution
        result = crew.kickoff()
        
        print("\n================================================")
        print("✅ CrewAI Execution Completed")
        print("================================================\n")
        
        return result
