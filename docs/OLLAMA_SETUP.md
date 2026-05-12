# 🦙 دليل استخدام Ollama - AI Software Company

## 🎯 نظرة عامة

هذا الدليل يشرح كيفية استخدام Ollama (نماذج محلية) بدلاً من OpenAI/Anthropic APIs.

---

## ✨ المميزات

✅ **مجاني 100%** - لا تكاليف API  
✅ **سريع** - كل شيء محلي  
✅ **خصوصية** - البيانات لا تخرج من جهازك  
✅ **Offline** - يعمل بدون إنترنت  
✅ **قوي** - نماذج متخصصة لكل مهمة

---

## 📋 النماذج المتاحة

### النماذج الموصى بها

| النموذج | الحجم | الاستخدام | التحميل |
|---------|-------|-----------|----------|
| **qwen2.5:7b** | 4.7GB | Planning, General | `ollama pull qwen2.5:7b` |
| **qwen2.5-coder:7b** | 4.7GB | Code Generation | `ollama pull qwen2.5-coder:7b` |
| **gemma4:latest** | 9.6GB | Architecture Design | `ollama pull gemma4:latest` |
| **llama3.1:8b** | 4.9GB | Debugging, Analysis | `ollama pull llama3.1:8b` |
| **llama3.2:3b** | 2.0GB | Testing, DevOps | `ollama pull llama3.2:3b` |
| **nomic-embed-text** | 274MB | Embeddings | `ollama pull nomic-embed-text` |

---

## 🎯 توزيع النماذج على Agents

### التوزيع الموصى به

```
┌─────────────────────────────────────────────────┐
│              Agent → Model Mapping              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Planner Agent      →  qwen2.5:7b              │
│  ├─ Planning                                    │
│  ├─ Requirements Analysis                       │
│  └─ User Stories                                │
│                                                 │
│  Architect Agent    →  gemma4:latest (9.6GB)   │
│  ├─ System Design                               │
│  ├─ Tech Stack Selection                        │
│  └─ Database Schema                             │
│                                                 │
│  Backend Agent      →  qwen2.5-coder:7b        │
│  ├─ Python/FastAPI                              │
│  ├─ Django                                      │
│  └─ API Development                             │
│                                                 │
│  Frontend Agent     →  qwen2.5-coder:7b        │
│  ├─ React/Vue                                   │
│  ├─ TypeScript                                  │
│  └─ UI Components                               │
│                                                 │
│  AI Agent           →  qwen2.5-coder:7b        │
│  ├─ ML Models                                   │
│  ├─ Training Scripts                            │
│  └─ Inference APIs                              │
│                                                 │
│  Testing Agent      →  llama3.2:3b (Fast!)     │
│  ├─ Unit Tests                                  │
│  ├─ Integration Tests                           │
│  └─ Test Coverage                               │
│                                                 │
│  Debugger Agent     →  llama3.1:8b             │
│  ├─ Error Analysis                              │
│  ├─ Bug Fixing                                  │
│  └─ Code Review                                 │
│                                                 │
│  Refactor Agent     →  qwen2.5-coder:7b        │
│  ├─ Code Optimization                           │
│  ├─ Best Practices                              │
│  └─ Performance                                 │
│                                                 │
│  DevOps Agent       →  llama3.2:3b (Fast!)     │
│  ├─ Docker                                      │
│  ├─ CI/CD                                       │
│  └─ Deployment                                  │
│                                                 │
│  Memory System      →  nomic-embed-text        │
│  ├─ Vector Embeddings                           │
│  ├─ Semantic Search                             │
│  └─ Context Retrieval                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🚀 التثبيت والإعداد

### 1. تثبيت Ollama

#### Windows
```bash
# حمل من الموقع الرسمي
https://ollama.ai/download/windows

# أو باستخدام winget
winget install Ollama.Ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### macOS
```bash
brew install ollama
```

### 2. تشغيل Ollama

```bash
# تشغيل Ollama server
ollama serve

# في terminal آخر، تحقق من التشغيل
ollama list
```

### 3. تحميل النماذج

```bash
# النماذج الأساسية (ضرورية)
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# النماذج المتقدمة (اختيارية)
ollama pull gemma4:latest
ollama pull llama3.1:8b
```

**الحجم الإجمالي**: ~25GB للنماذج الأساسية

---

## 🛠️ التكامل مع المشروع

### 1. إنشاء Ollama Interface

```python
# utils/ollama_interface.py

import requests
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OllamaInterface:
    """
    Interface للتعامل مع Ollama Local LLMs
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        
        # تعيين النماذج لكل Agent
        self.agent_models = {
            "planner": "qwen2.5:7b",
            "architect": "gemma4:latest",
            "backend": "qwen2.5-coder:7b",
            "frontend": "qwen2.5-coder:7b",
            "ai": "qwen2.5-coder:7b",
            "testing": "llama3.2:3b",
            "debugger": "llama3.1:8b",
            "refactor": "qwen2.5-coder:7b",
            "devops": "llama3.2:3b"
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
        model = self.agent_models.get(agent_type, "llama3.1:8b")
        
        logger.info(f"Using model: {model} for agent: {agent_type}")
        
        # بناء الـ messages
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # إعداد options
        options = {
            "temperature": temperature,
            "num_predict": max_tokens
        }
        
        # JSON mode
        format_type = "json" if json_mode else None
        
        # استدعاء Ollama API
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "format": format_type,
                    "options": options
                },
                timeout=300  # 5 minutes timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def get_embeddings(self, text: str) -> list:
        """
        الحصول على embeddings من nomic-embed-text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": "nomic-embed-text:latest",
                    "prompt": text
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["embedding"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Embeddings error: {e}")
            raise
    
    def check_model_available(self, model_name: str) -> bool:
        """
        التحقق من توفر النموذج
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            available_models = [m["name"] for m in models]
            
            return model_name in available_models
            
        except Exception as e:
            logger.error(f"Error checking models: {e}")
            return False
    
    def list_models(self) -> list:
        """
        قائمة النماذج المتاحة
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            return [
                {
                    "name": m["name"],
                    "size": m["size"],
                    "modified": m["modified_at"]
                }
                for m in models
            ]
            
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def get_model_info(self, model_name: str) -> Dict:
        """
        معلومات عن نموذج معين
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {}

# Singleton instance
ollama = OllamaInterface()
```

### 2. تعديل LLM Interface

```python
# utils/llm_interface.py

from typing import Optional
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMInterface:
    def __init__(self, provider: str = None):
        self.provider = provider or settings.llm_provider
        
        if self.provider == "ollama":
            from utils.ollama_interface import ollama
            self.client = ollama
        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False,
        agent_type: str = "planner"
    ) -> str:
        """
        توليد نص من LLM
        """
        if self.provider == "ollama":
            return self.client.generate(
                prompt=prompt,
                agent_type=agent_type,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode
            )
        elif self.provider == "openai":
            # OpenAI implementation...
            pass
        elif self.provider == "anthropic":
            # Anthropic implementation...
            pass
```

### 3. تحديث Configuration

```python
# core/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM Provider
    llm_provider: str = "ollama"  # ollama, openai, anthropic
    
    # Ollama Settings
    ollama_base_url: str = "http://localhost:11434"
    
    # Agent Models (Ollama)
    planner_model: str = "qwen2.5:7b"
    architect_model: str = "gemma4:latest"
    backend_model: str = "qwen2.5-coder:7b"
    frontend_model: str = "qwen2.5-coder:7b"
    ai_model: str = "qwen2.5-coder:7b"
    testing_model: str = "llama3.2:3b"
    debugger_model: str = "llama3.1:8b"
    refactor_model: str = "qwen2.5-coder:7b"
    devops_model: str = "llama3.2:3b"
    embeddings_model: str = "nomic-embed-text:latest"
    
    # OpenAI (Optional)
    openai_api_key: Optional[str] = None
    
    # Anthropic (Optional)
    anthropic_api_key: Optional[str] = None
    
    # Other settings...
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### 4. تحديث .env

```env
# LLM Configuration
LLM_PROVIDER=ollama

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434

# Agent Models (optional - uses defaults if not specified)
PLANNER_MODEL=qwen2.5:7b
ARCHITECT_MODEL=gemma4:latest
BACKEND_MODEL=qwen2.5-coder:7b
FRONTEND_MODEL=qwen2.5-coder:7b
AI_MODEL=qwen2.5-coder:7b
TESTING_MODEL=llama3.2:3b
DEBUGGER_MODEL=llama3.1:8b
REFACTOR_MODEL=qwen2.5-coder:7b
DEVOPS_MODEL=llama3.2:3b
EMBEDDINGS_MODEL=nomic-embed-text:latest

# OpenAI (Optional - for comparison)
# OPENAI_API_KEY=sk-your-key-here

# Anthropic (Optional - for comparison)
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## 🧪 الاختبار

### اختبار شامل

```python
# test_ollama.py

from utils.ollama_interface import OllamaInterface
import json

def test_ollama():
    """
    اختبار شامل لـ Ollama
    """
    print("=" * 60)
    print("🦙 Ollama Integration Test")
    print("=" * 60)
    
    ollama = OllamaInterface()
    
    # 1. List Models
    print("\n📋 Available Models:")
    models = ollama.list_models()
    for model in models:
        size_gb = model['size'] / 1e9
        print(f"  ✓ {model['name']:<30} {size_gb:>6.1f} GB")
    
    # 2. Test Each Agent
    print("\n🧪 Testing Agent Models:\n")
    
    test_cases = [
        {
            "agent": "planner",
            "prompt": "Create a brief project plan for a todo app",
            "expected": "project plan"
        },
        {
            "agent": "backend",
            "prompt": "Write a simple FastAPI endpoint for GET /health",
            "expected": "FastAPI"
        },
        {
            "agent": "testing",
            "prompt": "Write a pytest test for a function that adds two numbers",
            "expected": "pytest"
        }
    ]
    
    for test in test_cases:
        print(f"Testing {test['agent']}...")
        try:
            response = ollama.generate(
                prompt=test['prompt'],
                agent_type=test['agent'],
                max_tokens=200
            )
            
            # Check if response contains expected keyword
            success = test['expected'].lower() in response.lower()
            status = "✅" if success else "⚠️"
            
            print(f"{status} {test['agent']}: {response[:100]}...")
            print()
            
        except Exception as e:
            print(f"❌ {test['agent']}: Error - {e}\n")
    
    # 3. Test Embeddings
    print("Testing Embeddings...")
    try:
        embeddings = ollama.get_embeddings("Test text for embeddings")
        print(f"✅ Embeddings: {len(embeddings)} dimensions")
        print(f"   Sample: {embeddings[:5]}...")
    except Exception as e:
        print(f"❌ Embeddings: {e}")
    
    # 4. Test JSON Mode
    print("\n🔍 Testing JSON Mode...")
    try:
        response = ollama.generate(
            prompt='Generate a JSON object with keys: name, age, city',
            agent_type="planner",
            json_mode=True,
            max_tokens=100
        )
        
        # Try to parse JSON
        data = json.loads(response)
        print(f"✅ JSON Mode: Valid JSON with keys: {list(data.keys())}")
        
    except json.JSONDecodeError:
        print(f"⚠️ JSON Mode: Response is not valid JSON")
    except Exception as e:
        print(f"❌ JSON Mode: {e}")
    
    print("\n" + "=" * 60)
    print("✨ Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_ollama()
```

شغل الاختبار:
```bash
python test_ollama.py
```

---

## 📊 الأداء المتوقع

### مقارنة الأداء

| Metric | Ollama (Local) | OpenAI GPT-4 | OpenAI GPT-3.5 |
|--------|----------------|--------------|----------------|
| **السرعة** | ⚡⚡⚡ (Fast) | ⚡ (Slow) | ⚡⚡ (Medium) |
| **التكلفة** | 💰 مجاني | 💰💰💰 غالي | 💰 رخيص |
| **الجودة** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **الخصوصية** | ✅ 100% | ❌ Cloud | ❌ Cloud |
| **Offline** | ✅ نعم | ❌ لا | ❌ لا |

### وقت التوليد (تقريبي)

| Agent | Model | Tokens/sec | Time for 1000 tokens |
|-------|-------|------------|---------------------|
| Planner | qwen2.5:7b | ~30 | ~33 sec |
| Architect | gemma4 | ~20 | ~50 sec |
| Backend | qwen2.5-coder | ~30 | ~33 sec |
| Testing | llama3.2:3b | ~50 | ~20 sec |
| Debugger | llama3.1:8b | ~25 | ~40 sec |

**ملاحظة**: الأرقام تعتمد على hardware (GPU/CPU)

---

## 💡 نصائح للأداء الأمثل

### 1. استخدام GPU

```bash
# تحقق من دعم GPU
ollama run llama3.2:3b --verbose

# إذا كان لديك NVIDIA GPU
# Ollama يستخدم GPU تلقائياً
```

### 2. تحسين Memory

```python
# في config.py
MAX_PARALLEL_AGENTS = 2  # لا تشغل أكثر من 2 agents معاً
```

### 3. Cache الـ Prompts

```python
# في ollama_interface.py
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generate(prompt: str, agent_type: str):
    return ollama.generate(prompt, agent_type)
```

### 4. تقليل max_tokens

```python
# للـ Agents السريعة
testing_agent_max_tokens = 2000  # بدلاً من 4000
devops_agent_max_tokens = 1500
```

---

## 🔧 Troubleshooting

### مشكلة: Ollama لا يستجيب

```bash
# تحقق من التشغيل
curl http://localhost:11434/api/tags

# إعادة تشغيل
# Windows
taskkill /F /IM ollama.exe
ollama serve

# Linux/Mac
killall ollama
ollama serve
```

### مشكلة: النموذج بطيء جداً

```bash
# استخدم نموذج أصغر
ollama pull llama3.2:1b  # 1.3GB فقط

# أو قلل max_tokens
max_tokens = 1000  # بدلاً من 4000
```

### مشكلة: Out of Memory

```bash
# استخدم نماذج أصغر
# بدلاً من gemma4:9.6GB
ollama pull gemma2:2b  # 1.6GB فقط

# أو شغل agent واحد في كل مرة
MAX_PARALLEL_AGENTS = 1
```

---

## 🎯 الخلاصة

### المميزات الرئيسية

✅ **مجاني تماماً** - لا تكاليف API  
✅ **خصوصية كاملة** - كل شيء محلي  
✅ **سريع** - لا latency للشبكة  
✅ **Offline** - يعمل بدون إنترنت  
✅ **متخصص** - نموذج لكل مهمة  

### متى تستخدم Ollama؟

- ✅ التطوير والاختبار
- ✅ المشاريع الشخصية
- ✅ عندما الخصوصية مهمة
- ✅ عندما لا يوجد ميزانية
- ✅ للتعلم والتجربة

### متى تستخدم OpenAI/Anthropic؟

- ✅ الإنتاج (Production)
- ✅ عندما الجودة أهم من التكلفة
- ✅ المشاريع التجارية الكبيرة
- ✅ عندما تحتاج أحدث النماذج

---

## 📚 موارد إضافية

- **Ollama Website**: https://ollama.ai
- **Ollama GitHub**: https://github.com/ollama/ollama
- **Model Library**: https://ollama.ai/library
- **Documentation**: https://github.com/ollama/ollama/tree/main/docs

---

**الإصدار**: 1.0.0  
**آخر تحديث**: 2026-04-10  
**الحالة**: Ready for Use ✅
