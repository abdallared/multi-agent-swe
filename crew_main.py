import sys
import warnings
from core.crew_pipeline import CrewPipeline
from core.config import settings

# Suppress some langchain warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def main():
    print("🤖 Welcome to the AI Software Company (CrewAI Edition) 🤖")
    print("This mode uses advanced inter-agent communication and internet access.")
    print("-" * 60)
    
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        print("Enter your project idea (e.g., 'A task management app with real-time collaboration'):")
        user_prompt = input("> ")

    if not user_prompt.strip():
        print("Error: Please provide a valid prompt.")
        return

    pipeline = CrewPipeline()
    result = pipeline.run(user_prompt)

    print("\n--- FINAL RESULT ---")
    print(result)

if __name__ == "__main__":
    main()
