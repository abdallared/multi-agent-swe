# دليل التنفيذ العملي - AI Software Company

## 🚀 البداية السريعة

### المتطلبات الأساسية

```bash
# Python 3.11+
python --version

# Git
git --version

# Docker (اختياري للتطوير)
docker --version
```

---

## 📦 إعداد المشروع

### 1. إنشاء هيكل المشروع

```bash
# إنشاء المجلد الرئيسي
mkdir ai_software_company
cd ai_software_company

# إنشاء البيئة الافتراضية
python -m venv venv

# تفعيل البيئة
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# إنشاء الهيكل
mkdir -p agents core memory builder deploy utils templates tests data output
```

### 2. تثبيت Dependencies

```bash
# إنشاء requirements.txt
cat > requirements.txt << EOF
# Core
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# LLM
openai==1.6.0
anthropic==0.8.0
langchain==0.1.0
langchain-openai==0.0.2

# Vector DB
chromadb==0.4.22
sentence-transformers==2.2.2

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9

# Cache
redis==5.0.1
hiredis==2.3.2

# Code Analysis
ast-grep==0.15.0
black==23.12.1
pylint==3.0.3
autopep8==2.0.4

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
coverage==7.4.0

# Git & GitHub
gitpython==3.1.40
PyGithub==2.1.1

# Docker
docker==7.0.0

# Utils
jinja2==3.1.2
pyyaml==6.0.1
requests==2.31.0
aiohttp==3.9.1
tenacity==8.2.3
EOF

# تثبيت
pip install -r requirements.txt
```

### 3. إعداد Environment Variables

```bash
# إنشاء .env
cat > .env << EOF
# LLM API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# GitHub
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_username

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_company

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector DB
CHROMA_PERSIST_DIR=./data/chroma

# Project Settings
MAX_ITERATIONS=50
DEFAULT_LLM=openai
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_TOKENS=4000

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
EOF
```

---

## 💻 الكود الأساسي

### 1. Configuration (core/config.py)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM Settings
    openai_api_key: str
    anthropic_api_key: Optional[str] = None
    default_llm: str = "openai"
    default_model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4000
    
    # GitHub Settings
    github_token: str
    github_username: str
    
    # Database
    database_url: str
    redis_url: str
    chroma_persist_dir: str = "./data/chroma"
    
    # Project Settings
    max_iterations: int = 50
    output_dir: str = "./output"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### 2. LLM Interface (utils/llm_interface.py)

```python
from typing import Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
import logging

logger = logging.getLogger(__name__)

class LLMInterface:
    def __init__(self, provider: str = "openai", model: str = None):
        self.provider = provider
        self.model = model or self._get_default_model()
        self.client = self._initialize_client()
    
    def _get_default_model(self) -> str:
        models = {
            "openai": "gpt-4-turbo-preview",
            "anthropic": "claude-3-opus-20240229"
        }
        return models.get(self.provider, "gpt-4-turbo-preview")
    
    def _initialize_client(self):
        if self.provider == "openai":
            return OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            return Anthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False
    ) -> str:
        """
        توليد نص من LLM
        """
        try:
            if self.provider == "openai":
                return self._generate_openai(
                    prompt, system_prompt, temperature, max_tokens, json_mode
                )
            elif self.provider == "anthropic":
                return self._generate_anthropic(
                    prompt, system_prompt, temperature, max_tokens
                )
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    def _generate_openai(
        self, prompt: str, system_prompt: str, 
        temperature: float, max_tokens: int, json_mode: bool
    ) -> str:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def _generate_anthropic(
        self, prompt: str, system_prompt: str,
        temperature: float, max_tokens: int
    ) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

# Singleton instance
llm = LLMInterface()
```

### 3. Memory System (memory/vector_db.py)

```python
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import json
import hashlib

class VectorMemory:
    def __init__(self, persist_dir: str = "./data/chroma"):
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=persist_dir,
                anonymized_telemetry=False
            )
        )
        self.collections = {}
    
    def get_or_create_collection(self, name: str):
        """
        الحصول على أو إنشاء collection
        """
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[name]
    
    def add(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        إضافة documents إلى collection
        """
        collection = self.get_or_create_collection(collection_name)
        
        if ids is None:
            ids = [self._generate_id(doc) for doc in documents]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        البحث في collection
        """
        collection = self.get_or_create_collection(collection_name)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        return self._format_results(results)
    
    def _generate_id(self, text: str) -> str:
        """
        توليد ID فريد
        """
        return hashlib.md5(text.encode()).hexdigest()
    
    def _format_results(self, results: Dict) -> List[Dict]:
        """
        تنسيق النتائج
        """
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        return formatted

# Singleton
vector_memory = VectorMemory()
```

### 4. Base Agent (agents/base_agent.py)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, llm_interface, memory_system):
        self.llm = llm_interface
        self.memory = memory_system
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.name)
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ مهمة Agent
        يجب تنفيذها في كل Agent
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        الحصول على system prompt خاص بالـ Agent
        """
        pass
    
    def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False
    ) -> str:
        """
        استدعاء LLM مع error handling
        """
        try:
            self.logger.info(f"Calling LLM for {self.name}")
            
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt or self.get_system_prompt(),
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode
            )
            
            self.logger.info(f"LLM response received for {self.name}")
            return response
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def store_in_memory(self, data: Dict[str, Any], collection: str = None):
        """
        تخزين البيانات في الذاكرة
        """
        collection_name = collection or f"{self.name.lower()}_results"
        
        document = json.dumps(data)
        metadata = {
            "agent": self.name,
            "timestamp": self._get_timestamp()
        }
        
        self.memory.add(
            collection_name=collection_name,
            documents=[document],
            metadatas=[metadata]
        )
    
    def retrieve_from_memory(
        self,
        query: str,
        collection: str = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        استرجاع من الذاكرة
        """
        collection_name = collection or f"{self.name.lower()}_results"
        
        results = self.memory.search(
            collection_name=collection_name,
            query=query,
            n_results=n_results
        )
        
        return results
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        التحقق من صحة المخرجات
        """
        required_keys = ['status']
        return all(key in output for key in required_keys)
    
    def _get_timestamp(self) -> str:
        """
        الحصول على timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()
```

### 5. Planner Agent (agents/planner.py)

```python
from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class PlannerAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are an expert software project planner.
        
Your role is to convert user ideas into structured, actionable project requirements.

You must output valid JSON with this exact structure:
{
    "project_name": "string",
    "description": "string",
    "vision": "string",
    "target_users": ["string"],
    "features": [
        {
            "name": "string",
            "description": "string",
            "priority": "high|medium|low",
            "complexity": "simple|medium|complex",
            "estimated_hours": number
        }
    ],
    "user_stories": [
        {
            "as_a": "string",
            "i_want": "string",
            "so_that": "string",
            "acceptance_criteria": ["string"]
        }
    ],
    "non_functional_requirements": {
        "performance": "string",
        "security": "string",
        "scalability": "string",
        "availability": "string"
    },
    "constraints": ["string"],
    "assumptions": ["string"]
}

Be thorough, specific, and realistic in your planning."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ التخطيط
        """
        user_prompt = context.get('user_prompt', '')
        
        if not user_prompt:
            raise ValueError("user_prompt is required")
        
        self.logger.info(f"Planning project for: {user_prompt}")
        
        # بناء الـ prompt
        planning_prompt = self._build_planning_prompt(user_prompt)
        
        # استدعاء LLM
        response = self.call_llm(
            prompt=planning_prompt,
            json_mode=True,
            temperature=0.7
        )
        
        # Parse JSON
        try:
            plan = json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            raise
        
        # Validation
        self._validate_plan(plan)
        
        # Store in memory
        self.store_in_memory(plan, "project_plans")
        
        self.logger.info(f"Planning completed for: {plan['project_name']}")
        
        return {
            'project_plan': plan,
            'status': 'planning_completed'
        }
    
    def _build_planning_prompt(self, user_prompt: str) -> str:
        """
        بناء prompt للتخطيط
        """
        return f"""User Request: {user_prompt}

Create a comprehensive project plan following the JSON structure specified in your system prompt.

Consider:
1. Break down the project into clear, manageable features
2. Identify all types of users who will interact with the system
3. Write detailed user stories with acceptance criteria
4. Specify non-functional requirements (performance, security, etc.)
5. List any constraints or assumptions
6. Estimate complexity and time for each feature

Be specific and actionable. The plan will be used to generate actual code."""
    
    def _validate_plan(self, plan: Dict):
        """
        التحقق من صحة الخطة
        """
        required_keys = [
            'project_name',
            'description',
            'features',
            'user_stories'
        ]
        
        for key in required_keys:
            if key not in plan:
                raise ValueError(f"Missing required key in plan: {key}")
        
        if not plan['features']:
            raise ValueError("Plan must have at least one feature")
        
        if not plan['user_stories']:
            raise ValueError("Plan must have at least one user story")
        
        self.logger.info("Plan validation passed")
```

### 6. AI CTO (core/ai_cto.py)

```python
from enum import Enum
from typing import Dict, Any, Optional
import logging
from agents.planner import PlannerAgent
from agents.architect import ArchitectAgent
# Import other agents...

logger = logging.getLogger(__name__)

class ProjectState(Enum):
    INITIALIZED = "initialized"
    PLANNING = "planning"
    ARCHITECTURE_DESIGN = "architecture_design"
    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"
    FAILED = "failed"

class AICTO:
    def __init__(self, llm_interface, memory_system):
        self.state = ProjectState.INITIALIZED
        self.context = {}
        self.llm = llm_interface
        self.memory = memory_system
        self.agents = self._initialize_agents()
        self.iteration = 0
        self.max_iterations = settings.max_iterations
        
        logger.info("AI CTO initialized")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """
        تهيئة جميع Agents
        """
        return {
            'planner': PlannerAgent(self.llm, self.memory),
            'architect': ArchitectAgent(self.llm, self.memory),
            # Add other agents...
        }
    
    def execute_workflow(self, user_prompt: str) -> Dict[str, Any]:
        """
        تنفيذ سير العمل الكامل
        """
        logger.info(f"Starting workflow for: {user_prompt}")
        
        self.context['user_prompt'] = user_prompt
        self.context['start_time'] = self._get_timestamp()
        
        try:
            while (self.state not in [ProjectState.COMPLETED, ProjectState.FAILED] 
                   and self.iteration < self.max_iterations):
                
                logger.info(f"Iteration {self.iteration}, State: {self.state.value}")
                
                # اختيار Agent التالي
                agent = self._decide_next_agent()
                
                if agent is None:
                    logger.warning("No agent selected, workflow may be stuck")
                    break
                
                # تنفيذ Agent
                result = agent.execute(self.context)
                
                # تحديث السياق
                self.context.update(result)
                
                # تحديث الحالة
                self._update_state(result)
                
                self.iteration += 1
            
            self.context['end_time'] = self._get_timestamp()
            self.context['total_iterations'] = self.iteration
            
            if self.state == ProjectState.COMPLETED:
                logger.info("Workflow completed successfully")
                return self._prepare_final_output()
            else:
                logger.error(f"Workflow failed or exceeded max iterations")
                return self._prepare_error_output()
                
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            self.state = ProjectState.FAILED
            return self._prepare_error_output(str(e))
    
    def _decide_next_agent(self) -> Optional[Any]:
        """
        اختيار Agent التالي بناءً على الحالة
        """
        decision_map = {
            ProjectState.INITIALIZED: self.agents['planner'],
            ProjectState.PLANNING: self.agents['architect'],
            # Add other state transitions...
        }
        
        return decision_map.get(self.state)
    
    def _update_state(self, result: Dict[str, Any]):
        """
        تحديث حالة المشروع
        """
        status = result.get('status', '')
        
        state_transitions = {
            'planning_completed': ProjectState.ARCHITECTURE_DESIGN,
            'architecture_completed': ProjectState.CODE_GENERATION,
            # Add other transitions...
        }
        
        if status in state_transitions:
            self.state = state_transitions[status]
            logger.info(f"State updated to: {self.state.value}")
    
    def _prepare_final_output(self) -> Dict[str, Any]:
        """
        تحضير المخرجات النهائية
        """
        return {
            'status': 'success',
            'state': self.state.value,
            'project': self.context.get('final_project'),
            'metadata': {
                'iterations': self.iteration,
                'start_time': self.context.get('start_time'),
                'end_time': self.context.get('end_time')
            }
        }
    
    def _prepare_error_output(self, error: str = None) -> Dict[str, Any]:
        """
        تحضير مخرجات الخطأ
        """
        return {
            'status': 'failed',
            'state': self.state.value,
            'error': error,
            'context': self.context
        }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
```

### 7. Main Entry Point (main.py)

```python
import logging
from core.config import settings
from core.ai_cto import AICTO
from utils.llm_interface import LLMInterface
from memory.vector_db import VectorMemory
import sys

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    نقطة البداية الرئيسية
    """
    print("=" * 60)
    print("AI Software Company - Autonomous Project Generator")
    print("=" * 60)
    print()
    
    # Get user input
    user_prompt = input("Describe your project: ")
    
    if not user_prompt.strip():
        print("Error: Project description cannot be empty")
        return
    
    print(f"\nStarting project generation...")
    print(f"Prompt: {user_prompt}")
    print()
    
    try:
        # Initialize components
        llm = LLMInterface(
            provider=settings.default_llm,
            model=settings.default_model
        )
        memory = VectorMemory(persist_dir=settings.chroma_persist_dir)
        
        # Initialize AI CTO
        cto = AICTO(llm, memory)
        
        # Execute workflow
        result = cto.execute_workflow(user_prompt)
        
        # Display results
        if result['status'] == 'success':
            print("\n" + "=" * 60)
            print("✓ Project generated successfully!")
            print("=" * 60)
            print(f"\nProject: {result['project']['name']}")
            print(f"Location: {result['project']['path']}")
            print(f"Iterations: {result['metadata']['iterations']}")
            print()
        else:
            print("\n" + "=" * 60)
            print("✗ Project generation failed")
            print("=" * 60)
            print(f"\nError: {result.get('error', 'Unknown error')}")
            print()
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nFatal error: {e}")

if __name__ == "__main__":
    main()
```

---

## 🧪 Testing

### إنشاء اختبارات أساسية (tests/test_planner.py)

```python
import pytest
from agents.planner import PlannerAgent
from utils.llm_interface import LLMInterface
from memory.vector_db import VectorMemory

@pytest.fixture
def planner_agent():
    llm = LLMInterface()
    memory = VectorMemory()
    return PlannerAgent(llm, memory)

def test_planner_execution(planner_agent):
    context = {
        'user_prompt': 'Build a simple todo app'
    }
    
    result = planner_agent.execute(context)
    
    assert 'project_plan' in result
    assert 'status' in result
    assert result['status'] == 'planning_completed'
    
    plan = result['project_plan']
    assert 'project_name' in plan
    assert 'features' in plan
    assert len(plan['features']) > 0

def test_planner_validation(planner_agent):
    # Test with invalid plan
    invalid_plan = {'project_name': 'Test'}
    
    with pytest.raises(ValueError):
        planner_agent._validate_plan(invalid_plan)
```

### تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest tests/

# مع coverage
pytest --cov=. --cov-report=html tests/

# اختبار محدد
pytest tests/test_planner.py -v
```

---

## 📝 الخطوات التالية

1. **إكمال جميع Agents**: Architect, Backend, Frontend, Testing, Debugger, Refactor, DevOps
2. **تطوير File Builder**: لتوليد الملفات الفعلية
3. **إضافة GitHub Integration**: للنشر التلقائي
4. **بناء Dashboard**: واجهة ويب للمراقبة
5. **Fine-tuning**: تدريب نماذج مخصصة
6. **Optimization**: تحسين الأداء والتكلفة

---

## 🐛 Troubleshooting

### مشكلة: LLM API Error
```python
# الحل: إضافة retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_llm_with_retry(self, prompt):
    return self.llm.generate(prompt)
```

### مشكلة: Memory Overflow
```python
# الحل: تنظيف الذاكرة دورياً
def cleanup_old_data(self, days=7):
    cutoff_date = datetime.now() - timedelta(days=days)
    self.memory.delete_before(cutoff_date)
```

---

**الإصدار**: 1.0.0  
**آخر تحديث**: 2026-04-09
