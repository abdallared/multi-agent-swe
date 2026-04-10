# 🚀 خطة التنفيذ خطوة بخطوة - AI Software Company

## 🎯 نظرة عامة

هذا الدليل يأخذك خطوة بخطوة من الصفر حتى مشروع يعمل بالكامل.

---

## ✅ المرحلة 0: الإعداد الأولي (30 دقيقة)

### الخطوة 0.1: تثبيت المتطلبات الأساسية

```bash
# تحقق من Python
python --version  # يجب أن يكون 3.11+

# تحقق من Git
git --version

# تحقق من pip
pip --version
```

### الخطوة 0.2: تثبيت Ollama

```bash
# Windows: حمل من https://ollama.ai/download/windows
# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# تشغيل Ollama
ollama serve
```

### الخطوة 0.3: تحميل النماذج

```bash
# في terminal جديد
ollama pull qwen2.5:7b          # 4.7GB - للتخطيط
ollama pull qwen2.5-coder:7b    # 4.7GB - للكود
ollama pull llama3.2:3b         # 2.0GB - للاختبار
ollama pull nomic-embed-text    # 274MB - للـ embeddings

# اختياري (للجودة الأعلى)
ollama pull gemma4:latest       # 9.6GB - للهندسة المعمارية
ollama pull llama3.1:8b         # 4.9GB - للـ debugging

# تحقق من التحميل
ollama list
```

**الوقت**: 20-30 دقيقة (حسب سرعة الإنترنت)

### الخطوة 0.4: إنشاء المشروع

```bash
# إنشاء مجلد المشروع
mkdir ai_software_company
cd ai_software_company

# إنشاء البيئة الافتراضية
python -m venv venv

# تفعيل البيئة
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### الخطوة 0.5: إنشاء الهيكل الأساسي

```bash
# إنشاء المجلدات
mkdir -p agents core memory utils builder deploy templates tests data/chroma logs output

# إنشاء ملفات __init__.py
touch agents/__init__.py
touch core/__init__.py
touch memory/__init__.py
touch utils/__init__.py
touch builder/__init__.py
touch deploy/__init__.py
```

**✅ Checkpoint**: يجب أن يكون لديك:
- Ollama يعمل
- 3-4 نماذج محملة على الأقل
- مجلد المشروع جاهز
- البيئة الافتراضية مفعلة

---

## ✅ المرحلة 1: الملفات الأساسية (15 دقيقة)

### الخطوة 1.1: إنشاء requirements.txt

انسخ المحتوى من الملف الموجود أو أنشئ ملف بسيط:

```txt
# requirements.txt - النسخة المبسطة للبداية
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
requests==2.31.0
chromadb==0.4.22
```

ثبت:
```bash
pip install -r requirements.txt
```

### الخطوة 1.2: إنشاء .env

```bash
# إنشاء .env
cat > .env << 'EOF'
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Project Settings
MAX_ITERATIONS=50
OUTPUT_DIR=./output
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Agent Models
PLANNER_MODEL=qwen2.5:7b
ARCHITECT_MODEL=qwen2.5:7b
BACKEND_MODEL=qwen2.5-coder:7b
FRONTEND_MODEL=qwen2.5-coder:7b
TESTING_MODEL=llama3.2:3b
DEBUGGER_MODEL=qwen2.5:7b
EMBEDDINGS_MODEL=nomic-embed-text:latest
EOF
```

### الخطوة 1.3: إنشاء .gitignore

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
venv/
.env
logs/
data/
output/
*.db
.pytest_cache/
EOF
```

**✅ Checkpoint**: 
```bash
# تحقق من الملفات
ls -la
# يجب أن ترى: requirements.txt, .env, .gitignore, venv/, agents/, core/, etc.
```

---

## ✅ المرحلة 2: Core Configuration (20 دقيقة)

### الخطوة 2.1: إنشاء core/config.py

```python
# core/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    إعدادات المشروع
    """
    # LLM Provider
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    
    # Agent Models
    planner_model: str = "qwen2.5:7b"
    architect_model: str = "qwen2.5:7b"
    backend_model: str = "qwen2.5-coder:7b"
    frontend_model: str = "qwen2.5-coder:7b"
    testing_model: str = "llama3.2:3b"
    debugger_model: str = "qwen2.5:7b"
    embeddings_model: str = "nomic-embed-text:latest"
    
    # Project Settings
    max_iterations: int = 50
    output_dir: str = "./output"
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton
settings = Settings()
```

### الخطوة 2.2: إنشاء core/__init__.py

```python
# core/__init__.py

from core.config import settings

__all__ = ['settings']
```

### الخطوة 2.3: اختبار Configuration

```python
# test_config.py

from core.config import settings

print("🔍 Testing Configuration...")
print(f"✅ LLM Provider: {settings.llm_provider}")
print(f"✅ Ollama URL: {settings.ollama_base_url}")
print(f"✅ Planner Model: {settings.planner_model}")
print(f"✅ Output Dir: {settings.output_dir}")
print("\n✨ Configuration loaded successfully!")
```

شغل:
```bash
python test_config.py
```

**✅ Checkpoint**: يجب أن ترى الإعدادات تطبع بنجاح

---

## ✅ المرحلة 3: Ollama Interface (30 دقيقة)

### الخطوة 3.1: إنشاء utils/ollama_interface.py

انسخ الكود من `OLLAMA_SETUP.md` أو استخدم هذه النسخة المبسطة:

```python
# utils/ollama_interface.py

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaInterface:
    """
    Interface للتعامل مع Ollama
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.agent_models = {
            "planner": "qwen2.5:7b",
            "architect": "qwen2.5:7b",
            "backend": "qwen2.5-coder:7b",
            "frontend": "qwen2.5-coder:7b",
            "testing": "llama3.2:3b",
            "debugger": "qwen2.5:7b",
        }
    
    def generate(
        self,
        prompt: str,
        agent_type: str = "planner",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False
    ) -> str:
        """
        توليد نص من Ollama
        """
        model = self.agent_models.get(agent_type, "qwen2.5:7b")
        
        logger.info(f"Using {model} for {agent_type}")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "format": "json" if json_mode else None,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=300
            )
            
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise
    
    def list_models(self) -> list:
        """
        قائمة النماذج المتاحة
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return [{"name": m["name"], "size": m["size"]} for m in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

# Singleton
ollama = OllamaInterface()
```

### الخطوة 3.2: إنشاء utils/__init__.py

```python
# utils/__init__.py

from utils.ollama_interface import ollama

__all__ = ['ollama']
```

### الخطوة 3.3: اختبار Ollama Interface

```python
# test_ollama_simple.py

from utils.ollama_interface import ollama

print("🦙 Testing Ollama Interface...\n")

# 1. List models
print("📋 Available Models:")
models = ollama.list_models()
for m in models:
    print(f"  - {m['name']}")

# 2. Simple generation
print("\n🧪 Testing Generation:")
response = ollama.generate(
    prompt="Say 'Hello from AI Software Company!' in one sentence.",
    agent_type="planner",
    max_tokens=50
)
print(f"✅ Response: {response}\n")

print("✨ Ollama is working!")
```

شغل:
```bash
python test_ollama_simple.py
```

**✅ Checkpoint**: يجب أن ترى قائمة النماذج ورد من Ollama

---

## ✅ المرحلة 4: Base Agent (45 دقيقة)

### الخطوة 4.1: إنشاء agents/base_agent.py

```python
# agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class لجميع Agents
    """
    
    def __init__(self, llm_interface):
        self.llm = llm_interface
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.name)
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ مهمة Agent
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        System prompt للـ Agent
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
        استدعاء LLM
        """
        try:
            self.logger.info(f"Calling LLM for {self.name}")
            
            # تحديد agent_type من اسم الـ class
            agent_type = self.name.lower().replace("agent", "")
            
            response = self.llm.generate(
                prompt=prompt,
                agent_type=agent_type,
                system_prompt=system_prompt or self.get_system_prompt(),
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode
            )
            
            self.logger.info(f"LLM response received")
            return response
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
```

### الخطوة 4.2: إنشاء agents/__init__.py

```python
# agents/__init__.py

from agents.base_agent import BaseAgent

__all__ = ['BaseAgent']
```

### الخطوة 4.3: اختبار Base Agent

```python
# test_base_agent.py

from agents.base_agent import BaseAgent
from utils.ollama_interface import ollama

class TestAgent(BaseAgent):
    """
    Agent بسيط للاختبار
    """
    
    def get_system_prompt(self) -> str:
        return "You are a helpful test agent."
    
    def execute(self, context: dict) -> dict:
        prompt = context.get('prompt', 'Say hello!')
        response = self.call_llm(prompt, max_tokens=100)
        return {'response': response, 'status': 'success'}

# Test
print("🧪 Testing Base Agent...\n")

agent = TestAgent(ollama)
result = agent.execute({'prompt': 'Explain what you do in one sentence.'})

print(f"✅ Status: {result['status']}")
print(f"✅ Response: {result['response']}\n")

print("✨ Base Agent is working!")
```

شغل:
```bash
python test_base_agent.py
```

**✅ Checkpoint**: يجب أن يعمل TestAgent بنجاح

---

## ✅ المرحلة 5: Planner Agent (60 دقيقة)

### الخطوة 5.1: إنشاء agents/planner.py

انسخ الكود الكامل من الملفات السابقة أو استخدم نسخة مبسطة للبداية.

### الخطوة 5.2: اختبار Planner Agent

```python
# test_planner.py

from agents.planner import PlannerAgent
from utils.ollama_interface import ollama
import json

print("🎯 Testing Planner Agent...\n")

planner = PlannerAgent(ollama, None)  # memory=None للبداية

context = {
    'user_prompt': 'Build a simple todo app with user authentication'
}

print("Generating project plan...")
result = planner.execute(context)

print(f"\n✅ Status: {result['status']}")

plan = result['project_plan']
print(f"✅ Project: {plan['project_name']}")
print(f"✅ Features: {len(plan['features'])} features")
print(f"✅ User Stories: {len(plan['user_stories'])} stories\n")

# عرض الميزات
print("Features:")
for f in plan['features'][:3]:
    print(f"  - {f['name']}: {f.get('priority', 'N/A')}")

print("\n✨ Planner Agent is working!")
```

شغل:
```bash
python test_planner.py
```

**⏱️ الوقت المتوقع**: 1-2 دقيقة للتوليد

**✅ Checkpoint**: يجب أن تحصل على خطة مشروع كاملة بصيغة JSON

---

## ✅ المرحلة 6: Main Entry Point (30 دقيقة)

### الخطوة 6.1: إنشاء main.py

```python
# main.py

import logging
import sys
from core.config import settings
from utils.ollama_interface import ollama
from agents.planner import PlannerAgent

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    نقطة البداية الرئيسية
    """
    print("=" * 60)
    print("🤖 AI Software Company - Project Generator")
    print("=" * 60)
    print()
    
    # Get user input
    user_prompt = input("📝 Describe your project: ")
    
    if not user_prompt.strip():
        print("❌ Error: Project description cannot be empty")
        return
    
    print(f"\n🚀 Starting project generation...")
    print(f"💡 Prompt: {user_prompt}")
    print()
    
    try:
        # Initialize Planner
        planner = PlannerAgent(ollama, None)
        
        # Execute planning
        print("📋 Phase 1: Planning...")
        result = planner.execute({'user_prompt': user_prompt})
        
        if result['status'] == 'planning_completed':
            plan = result['project_plan']
            print(f"\n✅ Planning completed!")
            print(f"   Project: {plan['project_name']}")
            print(f"   Features: {len(plan['features'])}")
            print(f"   User Stories: {len(plan['user_stories'])}")
            print()
            
            # TODO: Add more phases (Architecture, Code Generation, etc.)
            print("🔜 Next phases coming soon...")
        else:
            print("❌ Planning failed")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
```

### الخطوة 6.2: اختبار Main

```bash
python main.py
```

أدخل: `Build a task management app`

**✅ Checkpoint**: يجب أن يعمل البرنامج ويولد خطة

---

## 📊 ملخص ما تم إنجازه

### ✅ المكتمل

- [x] الإعداد الأولي
- [x] Ollama Integration
- [x] Configuration System
- [x] Base Agent
- [x] Planner Agent
- [x] Architect Agent
- [x] Backend Agent (مع retry logic)
- [x] Frontend Agent (مع retry logic)
- [x] File Builder
- [x] Main Entry Point (5 phases)

### 🔄 القادم

- [ ] Testing Agent
- [ ] Debugger Agent
- [ ] Refactor Agent
- [ ] DevOps Agent
- [ ] Memory System (ChromaDB)
- [ ] AI CTO Coordinator

---

## 🎯 الخطوات التالية

### المرحلة 7: Testing Agent

- إنشاء agents/testing.py
- توليد unit tests
- تشغيل الاختبارات تلقائياً

### المرحلة 8: Debugger Agent

- إنشاء agents/debugger.py
- قراءة error logs
- إصلاح الأخطاء تلقائياً

### المرحلة 9: Memory System

- إنشاء memory/vector_db.py
- تخزين واسترجاع السياق
- ChromaDB Integration

### المرحلة 10: AI CTO

- إنشاء core/ai_cto.py
- تنسيق جميع Agents
- اتخاذ القرارات

---

## 💡 نصائح

### للأداء الأفضل
- استخدم `llama3.2:3b` للمهام السريعة
- استخدم `qwen2.5-coder:7b` للكود
- فعل caching للـ prompts المتكررة

### للتطوير
- اختبر كل Agent بشكل منفصل
- استخدم logging للـ debugging
- احفظ النتائج في ملفات JSON

### للإنتاج
- أضف error handling شامل
- استخدم async للـ parallel execution
- أضف progress indicators

---

**جاهز للبدء؟** ابدأ من المرحلة 0! 🚀

**الإصدار**: 1.0.0  
**آخر تحديث**: 2026-04-10
