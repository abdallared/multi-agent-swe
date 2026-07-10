# Pipeline Flow Diagrams

This document contains Mermaid diagrams illustrating exactly how the project's pipelines and agents work.

### 1. The Whole Pipeline (Overall System Flow)
This diagram shows the complete journey from the moment a user enters a prompt to the moment the final application is built.

```mermaid
flowchart TD
    %% Styling
    classDef user fill:#3b82f6,stroke:#fff,stroke-width:2px,color:#fff
    classDef agent fill:#8b5cf6,stroke:#fff,stroke-width:2px,color:#fff
    classDef parallel fill:#10b981,stroke:#fff,stroke-width:2px,color:#fff
    classDef artifact fill:#f59e0b,stroke:#fff,stroke-width:2px,color:#fff
    classDef loop fill:#ef4444,stroke:#fff,stroke-width:2px,color:#fff

    User(("User Input:<br/>Project Description")):::user

    subgraph "Phase 1: Planning & Design (Sequential)"
        Planner["Planner Agent"]:::agent
        PlanDoc[/"Project Plan JSON"/]:::artifact
        Architect["Architect Agent"]:::agent
        ArchDoc[/"Architecture JSON"/]:::artifact
    end

    subgraph "Phase 2: Development (Parallel)"
        Backend["Backend Agent"]:::parallel
        Frontend["Frontend Agent"]:::parallel
        CodeDicts[/"Generated Code Dictionaries"/]:::artifact
    end

    subgraph "Phase 3: The Self-Correction Loop"
        Reviewer["Reviewer Agent"]:::loop
        ReviewIssues[/"Review Report"/]:::artifact
        BugCheck{"Are there<br/>Critical Bugs?"}:::loop
        Fixer["Agents Fix Code"]:::loop
    end

    subgraph "Phase 4: Build & Finalize (Parallel)"
        Builder["File Builder"]:::agent
        Testing["Testing Agent"]:::parallel
        Docker["Docker Agent"]:::parallel
    end

    FinalFolder[("Final Project Folder")]:::user

    %% Connections
    User --> Planner
    Planner -->|Produces| PlanDoc
    PlanDoc --> Architect
    Architect -->|Produces| ArchDoc

    PlanDoc & ArchDoc --> Backend
    PlanDoc & ArchDoc --> Frontend
    Backend & Frontend -->|Produce| CodeDicts

    CodeDicts --> Reviewer
    Reviewer --> ReviewIssues
    ReviewIssues --> BugCheck
    BugCheck -- Yes (Bug Found) --> Fixer
    Fixer --> Reviewer
    BugCheck -- No (Looks Good) --> Builder

    Builder --> Testing & Docker
    Testing & Docker --> FinalFolder
```

### 2. The Custom Pipeline (From `core/pipeline.py`)
This shows exactly how the Python code in `pipeline.py` orchestrates the agents using `asyncio` for parallel processing.

```mermaid
sequenceDiagram
    participant CLI as main.py
    participant Pipe as Pipeline Orchestrator
    participant P_A as Planner & Architect
    participant Dev as Backend & Frontend
    participant Rev as Reviewer
    participant BTD as Builder, Test, Docker

    CLI->>Pipe: run(user_prompt)
    activate Pipe
    
    %% Planning
    Pipe->>P_A: Await Planner.execute()
    P_A-->>Pipe: Return Plan
    Pipe->>P_A: Await Architect.execute(Plan)
    P_A-->>Pipe: Return Architecture
    
    %% Parallel Dev
    note over Pipe,Dev: ASYNC PARALLEL EXECUTION
    Pipe->>Dev: asyncio.gather(Backend, Frontend)
    Dev-->>Pipe: Return Backend Files & Frontend Files
    
    %% Review Loop
    loop Max 2 Iterations
        Pipe->>Rev: Await Reviewer.execute()
        Rev-->>Pipe: Return Pass/Fail Status
        opt If Failed
            Pipe->>Dev: Re-run affected Developer Agent to fix
            Dev-->>Pipe: Return fixed code
        end
    end
    
    %% Build and Finalize
    Pipe->>BTD: Await FileBuilder (Write base files)
    note over Pipe,BTD: ASYNC PARALLEL EXECUTION
    Pipe->>BTD: asyncio.gather(Testing, Docker)
    BTD-->>Pipe: Add Test/Docker files to disk
    
    Pipe-->>CLI: return final_project_path
    deactivate Pipe
```

### 3. The CrewAI Pipeline (From `core/crew_pipeline.py`)
This shows how the alternative CrewAI mode works. It is sequential and task-based.

```mermaid
flowchart LR
    classDef crew fill:#f97316,stroke:#fff,stroke-width:2px,color:#fff
    classDef task fill:#0ea5e9,stroke:#fff,stroke-width:2px,color:#fff

    Start(["Start crew_main.py"])
    
    subgraph "CrewAI Assembly"
        direction TB
        CrewObj["Assemble Crew"]:::crew
        Task1["Planning Task"]:::task
        Task2["Architecture Task"]:::task
        Task3["Coding Task"]:::task
        Task4["Review Task"]:::task
        
        CrewObj --> Task1 --> Task2 --> Task3 --> Task4
    end

    subgraph "Agent Tool Execution"
        direction TB
        AgentTools(("Agents can use tools:<br/>- Web Search<br/>- File Reader"))
    end

    Task1 -.-> AgentTools
    Task4 -.-> AgentTools

    Finish(["Project Complete"])

    Start --> CrewObj
    Task4 --> Finish
```

### 4. The Internal Processing Loop for EVERY Agent
Because all agents inherit from `BaseAgent`, they all share this identical internal "thinking" loop when processing their specific tasks.

```mermaid
flowchart TD
    classDef agent_step fill:#4b5563,stroke:#fff,stroke-width:2px,color:#fff
    classDef llm fill:#059669,stroke:#fff,stroke-width:2px,color:#fff

    Input(("Input Context"))
    
    Step1["1. Get System Prompt<br/>(Specific to Agent Role)"]:::agent_step
    Step2["2. Check Memory System<br/>(Find similar past projects)"]:::agent_step
    Step3["3. Inject Few-Shot Examples<br/>into Prompt"]:::agent_step
    Step4["4. Token Manager<br/>(Calculate required tokens)"]:::agent_step
    
    Step5{"5. Check Cache"}:::agent_step
    
    CallLLM["6. Call Ollama HTTP API<br/>(generate code/json)"]:::llm
    ReturnCache["Return Cached Response"]:::agent_step
    
    Step7["7. Parse JSON Response"]:::agent_step
    
    Validate{"8. Is Output Valid?"}:::agent_step
    Retry["Retry LLM Call<br/>(Max 3 times)"]:::agent_step
    
    Output(("Return Dict Output"))

    Input --> Step1 --> Step2 --> Step3 --> Step4 --> Step5
    Step5 -- Cache Miss --> CallLLM
    Step5 -- Cache Hit --> ReturnCache
    
    CallLLM --> Step7
    ReturnCache --> Step7
    
    Step7 --> Validate
    Validate -- Invalid JSON --> Retry
    Retry --> CallLLM
    Validate -- Valid JSON --> Output
```

---

### 5. Specific Input/Output Flows for Each Agent Role
This section breaks down exactly what data each specific agent takes in and what it produces.

#### Planner & Architect (Phase 1)
```mermaid
flowchart LR
    classDef input fill:#3b82f6,stroke:#fff,color:#fff
    classDef agent fill:#8b5cf6,stroke:#fff,color:#fff
    classDef output fill:#f59e0b,stroke:#fff,color:#fff

    UserPrompt[/"User Prompt<br/>(1 Sentence)"/]:::input
    
    Planner["Planner Agent"]:::agent
    PlanJSON[/"Plan JSON<br/>(Features, User Stories)"/]:::output
    
    Architect["Architect Agent"]:::agent
    ArchJSON[/"Architecture JSON<br/>(DB Schema, Endpoints)"/]:::output
    
    UserPrompt --> Planner --> PlanJSON
    PlanJSON --> Architect --> ArchJSON
```

#### Code Generators (Phase 2)
```mermaid
flowchart LR
    classDef input fill:#3b82f6,stroke:#fff,color:#fff
    classDef agent fill:#10b981,stroke:#fff,color:#fff
    classDef output fill:#f59e0b,stroke:#fff,color:#fff

    Plan[/"Project Plan"/]:::input
    Arch[/"Architecture"/]:::input
    
    BackAgent["Backend Agent"]:::agent
    FrontAgent["Frontend Agent"]:::agent
    
    BackCode[/"Backend Files<br/>(FastAPI, SQLAlchemy)"/]:::output
    FrontCode[/"Frontend Files<br/>(React, Tailwind)"/]:::output

    Plan & Arch --> BackAgent
    Plan & Arch --> FrontAgent
    
    BackAgent --> BackCode
    FrontAgent --> FrontCode
```

#### Reviewer (Phase 3)
```mermaid
flowchart LR
    classDef input fill:#3b82f6,stroke:#fff,color:#fff
    classDef agent fill:#ef4444,stroke:#fff,color:#fff
    classDef output fill:#f59e0b,stroke:#fff,color:#fff

    Plan[/"Project Plan"/]:::input
    Arch[/"Architecture"/]:::input
    Code[/"Generated Code"/]:::input
    
    Reviewer["Reviewer Agent"]:::agent
    
    Static["1. Static Analysis<br/>(Syntax, Imports)"]:::agent
    LLM["2. LLM Semantic Review<br/>(Logic, Security)"]:::agent
    
    Result[/"Review Result<br/>(Pass/Fail + Issues)"/]:::output

    Plan & Arch & Code --> Reviewer
    Reviewer --> Static --> LLM --> Result
```

#### DevOps & Finalization (Phase 4)
```mermaid
flowchart LR
    classDef input fill:#3b82f6,stroke:#fff,color:#fff
    classDef agent fill:#6366f1,stroke:#fff,color:#fff
    classDef output fill:#f59e0b,stroke:#fff,color:#fff

    PlanArch[/"Plan & Architecture"/]:::input
    Code[/"Generated Code"/]:::input
    
    TestAgent["Testing Agent"]:::agent
    DockerAgent["Docker Agent"]:::agent
    
    TestFiles[/"Pytest Suite"/]:::output
    DockerFiles[/"Dockerfiles &<br/>docker-compose.yml"/]:::output

    PlanArch & Code --> TestAgent --> TestFiles
    PlanArch --> DockerAgent --> DockerFiles
```
