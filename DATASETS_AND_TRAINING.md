# 📊 Datasets والتدريب - AI Software Company

## 🎯 نظرة عامة

هذا الدليل يشرح كيفية استخدام وإنشاء Datasets لتدريب وتحسين Agents في النظام.

---

## 📚 Datasets الجاهزة

### 1. The Stack

**الوصف**: أكبر مجموعة بيانات مفتوحة المصدر للكود البرمجي

**المحتوى**:
- 6+ تيرابايت من الكود
- 358M ملف
- 30+ لغة برمجة
- مشاريع GitHub مفتوحة المصدر

**الاستخدام**:
```python
from datasets import load_dataset

# تحميل The Stack
ds = load_dataset(
    "bigcode/the-stack",
    data_dir="data/python",  # للغة Python فقط
    split="train",
    streaming=True  # للملفات الكبيرة
)

# مثال على الاستخدام
for sample in ds.take(5):
    print(f"File: {sample['path']}")
    print(f"Code:\n{sample['content'][:200]}")
    print("-" * 50)
```

**التطبيق في المشروع**:
- تدريب Backend Agent على أنماط الكود
- تعلم Best Practices
- فهم هياكل المشاريع

---

### 2. CodeSearchNet

**الوصف**: كود مع documentation وتعليقات

**المحتوى**:
- 6M دالة
- 2M documentation strings
- 6 لغات: Python, Java, JavaScript, PHP, Ruby, Go

**الاستخدام**:
```python
from datasets import load_dataset

# تحميل CodeSearchNet
ds = load_dataset("code_search_net", "python")

# مثال
for item in ds['train'].select(range(3)):
    print(f"Function: {item['func_name']}")
    print(f"Documentation: {item['docstring']}")
    print(f"Code:\n{item['code']}")
    print("=" * 60)
```

**التطبيق في المشروع**:
- تعليم Agents كتابة Documentation
- فهم العلاقة بين الكود والشرح
- توليد تعليقات مفيدة

---

### 3. CodeAlpaca

**الوصف**: Instruction-following dataset للكود

**المحتوى**:
- 20K instruction-output pairs
- تعليمات برمجية متنوعة
- أكواد حل مشاكل

**الاستخدام**:
```python
from datasets import load_dataset

# تحميل CodeAlpaca
ds = load_dataset("sahil2801/CodeAlpaca-20k")

# مثال
for item in ds['train'].select(range(3)):
    print(f"Instruction: {item['instruction']}")
    print(f"Input: {item['input']}")
    print(f"Output:\n{item['output']}")
    print("=" * 60)
```

**التطبيق في المشروع**:
- تدريب Agents على فهم التعليمات
- تحسين استجابة Agents للـ prompts
- تعلم أنماط حل المشاكل

---

### 4. HumanEval

**الوصف**: اختبارات لتقييم جودة الكود المولد

**المحتوى**:
- 164 مشكلة برمجية
- Test cases شاملة
- مستويات صعوبة متنوعة

**الاستخدام**:
```python
from datasets import load_dataset

# تحميل HumanEval
ds = load_dataset("openai_humaneval")

# مثال
for item in ds['test'].select(range(2)):
    print(f"Task: {item['task_id']}")
    print(f"Prompt:\n{item['prompt']}")
    print(f"Tests:\n{item['test']}")
    print(f"Entry Point: {item['entry_point']}")
    print("=" * 60)
```

**التطبيق في المشروع**:
- تقييم جودة Code Agents
- Benchmarking للتحسينات
- اختبار قدرات حل المشاكل

---

### 5. APPS (Automated Programming Progress Standard)

**الوصف**: مشاكل برمجية تنافسية

**المحتوى**:
- 10K مشكلة برمجية
- 3 مستويات صعوبة
- حلول متعددة لكل مشكلة

**الاستخدام**:
```python
from datasets import load_dataset

# تحميل APPS
ds = load_dataset("codeparrot/apps")

# مثال
for item in ds['train'].select(range(2)):
    print(f"Problem:\n{item['question']}")
    print(f"Difficulty: {item['difficulty']}")
    print(f"Solutions: {len(item['solutions'])}")
    print("=" * 60)
```

---

## 🏗️ إنشاء Dataset مخصص

### Dataset Structure

```json
{
  "version": "1.0.0",
  "created_at": "2026-04-09",
  "description": "Multi-Agent Software Engineering Dataset",
  "samples": [
    {
      "id": "sample_001",
      "agent_type": "planner",
      "instruction": "Create a project plan for...",
      "context": {
        "user_prompt": "Build a food delivery app",
        "constraints": ["budget: $10k", "timeline: 3 months"]
      },
      "expected_output": {
        "project_name": "FoodDelivery Pro",
        "features": [...],
        "user_stories": [...]
      },
      "metadata": {
        "complexity": "medium",
        "domain": "e-commerce",
        "tech_stack": ["python", "react"]
      }
    }
  ]
}
```

### Dataset Builder Script

```python
# data/dataset_builder.py

import json
from typing import List, Dict, Any
from datetime import datetime

class DatasetBuilder:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.samples = []
        self.version = "1.0.0"
    
    def add_sample(
        self,
        agent_type: str,
        instruction: str,
        context: Dict[str, Any],
        expected_output: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ):
        """
        إضافة عينة إلى Dataset
        """
        sample = {
            "id": f"sample_{len(self.samples) + 1:04d}",
            "agent_type": agent_type,
            "instruction": instruction,
            "context": context,
            "expected_output": expected_output,
            "metadata": metadata or {}
        }
        
        self.samples.append(sample)
    
    def save(self, filepath: str):
        """
        حفظ Dataset
        """
        dataset = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "created_at": datetime.now().isoformat(),
            "total_samples": len(self.samples),
            "samples": self.samples
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"Dataset saved: {filepath}")
        print(f"Total samples: {len(self.samples)}")
    
    def load(self, filepath: str):
        """
        تحميل Dataset
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.name = data['name']
        self.version = data['version']
        self.description = data['description']
        self.samples = data['samples']
        
        print(f"Dataset loaded: {self.name}")
        print(f"Total samples: {len(self.samples)}")

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء dataset جديد
    builder = DatasetBuilder(
        name="AI Software Company Training Data",
        description="Training data for multi-agent software engineering system"
    )
    
    # إضافة عينات للـ Planner Agent
    builder.add_sample(
        agent_type="planner",
        instruction="Create a comprehensive project plan",
        context={
            "user_prompt": "Build a task management app with AI prioritization",
            "constraints": ["timeline: 2 months", "team_size: 1 developer"]
        },
        expected_output={
            "project_name": "TaskMaster AI",
            "description": "Intelligent task management with AI-powered prioritization",
            "features": [
                {
                    "name": "Task Creation",
                    "priority": "high",
                    "complexity": "simple"
                },
                {
                    "name": "AI Prioritization",
                    "priority": "high",
                    "complexity": "complex"
                }
            ],
            "user_stories": [
                {
                    "as_a": "user",
                    "i_want": "create tasks",
                    "so_that": "I can track my work"
                }
            ]
        },
        metadata={
            "complexity": "medium",
            "domain": "productivity",
            "estimated_hours": 320
        }
    )
    
    # إضافة عينات للـ Architect Agent
    builder.add_sample(
        agent_type="architect",
        instruction="Design system architecture",
        context={
            "project_plan": {
                "features": ["user_auth", "task_crud", "ai_prioritization"],
                "scale": "medium"
            }
        },
        expected_output={
            "tech_stack": {
                "backend": "FastAPI",
                "frontend": "React",
                "database": "PostgreSQL",
                "ai": "TensorFlow"
            },
            "modules": [
                {
                    "name": "auth_module",
                    "type": "backend",
                    "dependencies": ["database", "jwt"]
                }
            ]
        },
        metadata={
            "architecture_pattern": "microservices",
            "scalability": "horizontal"
        }
    )
    
    # حفظ Dataset
    builder.save("data/training_dataset.json")
```

---

## 🎓 Fine-tuning Strategy

### 1. تحضير البيانات

```python
# data/prepare_training_data.py

from datasets import Dataset
import json

def prepare_for_finetuning(dataset_path: str, agent_type: str = None):
    """
    تحضير البيانات للـ fine-tuning
    """
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    samples = data['samples']
    
    # تصفية حسب نوع Agent
    if agent_type:
        samples = [s for s in samples if s['agent_type'] == agent_type]
    
    # تحويل إلى format مناسب للتدريب
    training_data = []
    for sample in samples:
        training_data.append({
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a {sample['agent_type']} agent."
                },
                {
                    "role": "user",
                    "content": f"{sample['instruction']}\n\nContext: {json.dumps(sample['context'])}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps(sample['expected_output'])
                }
            ]
        })
    
    return training_data

# استخدام
training_data = prepare_for_finetuning(
    "data/training_dataset.json",
    agent_type="planner"
)

# حفظ بصيغة JSONL للـ OpenAI fine-tuning
with open("data/planner_training.jsonl", 'w') as f:
    for item in training_data:
        f.write(json.dumps(item) + '\n')
```

### 2. Fine-tuning مع OpenAI

```python
# training/finetune_openai.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def finetune_model(training_file_path: str, model_name: str = "gpt-3.5-turbo"):
    """
    Fine-tune نموذج OpenAI
    """
    # رفع ملف التدريب
    with open(training_file_path, 'rb') as f:
        training_file = client.files.create(
            file=f,
            purpose='fine-tune'
        )
    
    print(f"Training file uploaded: {training_file.id}")
    
    # بدء Fine-tuning
    job = client.fine_tuning.jobs.create(
        training_file=training_file.id,
        model=model_name,
        hyperparameters={
            "n_epochs": 3,
            "batch_size": 4,
            "learning_rate_multiplier": 0.1
        }
    )
    
    print(f"Fine-tuning job started: {job.id}")
    print(f"Status: {job.status}")
    
    return job.id

# استخدام
job_id = finetune_model("data/planner_training.jsonl")
```

### 3. مراقبة التدريب

```python
def monitor_finetuning(job_id: str):
    """
    مراقبة تقدم Fine-tuning
    """
    import time
    
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        
        print(f"Status: {job.status}")
        
        if job.status == "succeeded":
            print(f"Fine-tuning completed!")
            print(f"Fine-tuned model: {job.fine_tuned_model}")
            break
        elif job.status == "failed":
            print(f"Fine-tuning failed: {job.error}")
            break
        
        time.sleep(60)  # انتظر دقيقة

# استخدام
monitor_finetuning(job_id)
```

---

## 📊 Data Collection من الاستخدام

### Logging System

```python
# utils/data_logger.py

import json
from datetime import datetime
from pathlib import Path

class DataLogger:
    def __init__(self, log_dir: str = "./data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_agent_execution(
        self,
        agent_name: str,
        input_data: dict,
        output_data: dict,
        success: bool,
        execution_time: float
    ):
        """
        تسجيل تنفيذ Agent
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "input": input_data,
            "output": output_data,
            "success": success,
            "execution_time": execution_time
        }
        
        # حفظ في ملف يومي
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{agent_name}_{date_str}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def collect_training_data(self, agent_name: str, days: int = 7):
        """
        جمع بيانات التدريب من الـ logs
        """
        from datetime import timedelta
        
        training_samples = []
        
        # جمع logs من آخر X أيام
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            log_file = self.log_dir / f"{agent_name}_{date_str}.jsonl"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line)
                        if entry['success']:  # فقط التنفيذات الناجحة
                            training_samples.append({
                                "input": entry['input'],
                                "output": entry['output']
                            })
        
        return training_samples

# استخدام في Agent
logger = DataLogger()

class PlannerAgent(BaseAgent):
    def execute(self, context):
        start_time = time.time()
        
        try:
            result = self._do_planning(context)
            success = True
        except Exception as e:
            result = {"error": str(e)}
            success = False
        
        execution_time = time.time() - start_time
        
        # تسجيل التنفيذ
        logger.log_agent_execution(
            agent_name=self.name,
            input_data=context,
            output_data=result,
            success=success,
            execution_time=execution_time
        )
        
        return result
```

---

## 🔄 Continuous Learning

### Active Learning Loop

```python
# training/active_learning.py

class ActiveLearner:
    def __init__(self, model, uncertainty_threshold: float = 0.7):
        self.model = model
        self.uncertainty_threshold = uncertainty_threshold
        self.uncertain_samples = []
    
    def predict_with_uncertainty(self, input_data):
        """
        التنبؤ مع قياس عدم اليقين
        """
        # الحصول على عدة تنبؤات
        predictions = []
        for _ in range(5):
            pred = self.model.generate(input_data, temperature=0.8)
            predictions.append(pred)
        
        # حساب التنوع (كمقياس لعدم اليقين)
        uncertainty = self._calculate_diversity(predictions)
        
        if uncertainty > self.uncertainty_threshold:
            # حفظ للمراجعة البشرية
            self.uncertain_samples.append({
                "input": input_data,
                "predictions": predictions,
                "uncertainty": uncertainty
            })
        
        return predictions[0], uncertainty
    
    def _calculate_diversity(self, predictions):
        """
        حساب التنوع بين التنبؤات
        """
        # مقياس بسيط: نسبة التنبؤات المختلفة
        unique_predictions = len(set(predictions))
        return unique_predictions / len(predictions)
    
    def get_samples_for_review(self):
        """
        الحصول على العينات التي تحتاج مراجعة
        """
        return sorted(
            self.uncertain_samples,
            key=lambda x: x['uncertainty'],
            reverse=True
        )
```

---

## 📈 Evaluation Metrics

### Agent Performance Metrics

```python
# evaluation/metrics.py

from typing import List, Dict
import numpy as np

class AgentEvaluator:
    @staticmethod
    def evaluate_planner(predictions: List[Dict], ground_truth: List[Dict]):
        """
        تقييم Planner Agent
        """
        metrics = {
            "feature_coverage": 0,
            "user_story_quality": 0,
            "completeness": 0
        }
        
        for pred, truth in zip(predictions, ground_truth):
            # Feature Coverage
            pred_features = set(f['name'] for f in pred.get('features', []))
            truth_features = set(f['name'] for f in truth.get('features', []))
            
            if truth_features:
                coverage = len(pred_features & truth_features) / len(truth_features)
                metrics["feature_coverage"] += coverage
            
            # User Story Quality
            if 'user_stories' in pred and 'user_stories' in truth:
                story_score = len(pred['user_stories']) / max(len(truth['user_stories']), 1)
                metrics["user_story_quality"] += min(story_score, 1.0)
            
            # Completeness
            required_keys = ['project_name', 'features', 'user_stories']
            completeness = sum(k in pred for k in required_keys) / len(required_keys)
            metrics["completeness"] += completeness
        
        # Average
        n = len(predictions)
        return {k: v / n for k, v in metrics.items()}
    
    @staticmethod
    def evaluate_code_quality(generated_code: str):
        """
        تقييم جودة الكود المولد
        """
        import ast
        import pylint.lint
        from io import StringIO
        
        metrics = {}
        
        # Syntax Check
        try:
            ast.parse(generated_code)
            metrics['syntax_valid'] = True
        except SyntaxError:
            metrics['syntax_valid'] = False
        
        # Pylint Score
        pylint_output = StringIO()
        pylint.lint.Run(
            ['--from-stdin', 'generated'],
            reporter=pylint.reporters.text.TextReporter(pylint_output),
            exit=False
        )
        
        # استخراج النتيجة
        output = pylint_output.getvalue()
        # Parse pylint score...
        
        return metrics
```

---

## 🎯 Best Practices

### 1. Data Quality
- ✅ تنظيف البيانات من الأخطاء
- ✅ التحقق من صحة JSON
- ✅ إزالة التكرارات
- ✅ توازن الفئات (balanced dataset)

### 2. Data Diversity
- ✅ تنوع المجالات (e-commerce, social, productivity)
- ✅ تنوع التعقيد (simple, medium, complex)
- ✅ تنوع التقنيات (different tech stacks)

### 3. Versioning
- ✅ استخدام Git لتتبع التغييرات
- ✅ توثيق كل إصدار
- ✅ الاحتفاظ بالإصدارات القديمة

### 4. Privacy & Security
- ✅ إزالة البيانات الحساسة
- ✅ عدم تضمين API keys
- ✅ مراجعة البيانات قبل النشر

---

## 📦 Dataset Repository Structure

```
data/
├── raw/                    # بيانات خام
│   ├── the_stack/
│   ├── code_search_net/
│   └── code_alpaca/
│
├── processed/              # بيانات معالجة
│   ├── planner_data.json
│   ├── architect_data.json
│   └── backend_data.json
│
├── training/               # بيانات التدريب
│   ├── planner_train.jsonl
│   ├── planner_val.jsonl
│   └── planner_test.jsonl
│
├── logs/                   # سجلات الاستخدام
│   ├── planner_2026-04-09.jsonl
│   └── architect_2026-04-09.jsonl
│
└── models/                 # النماذج المدربة
    ├── planner_v1/
    └── architect_v1/
```

---

**الإصدار**: 1.0.0  
**آخر تحديث**: 2026-04-09
