# 🧪 Tests - AI Software Company

## نظرة عامة

هذا المجلد يحتوي على جميع اختبارات النظام.

## 📋 ملفات الاختبار

### اختبارات الوكلاء (Agents)
- **`test_planner.py`** - اختبار Planner Agent
- **`test_architect.py`** - اختبار Architect Agent
- **`test_backend_and_builder.py`** - اختبار Backend Agent + Builder
- **`test_frontend.py`** - اختبار Frontend Agent
- **`test_agents_quick.py`** - اختبار سريع لجميع الوكلاء

### اختبارات النظام الكامل
- **`test_full_system.py`** - اختبار النظام الكامل
- **`test_full_workflow.py`** - اختبار سير العمل الكامل

### اختبارات الإعداد
- **`test_setup.py`** - اختبار الإعداد والمتطلبات

### ملفات الإخراج
- **`test_plan_output.json`** - مخرجات اختبار Planner
- **`test_architecture_output.json`** - مخرجات اختبار Architect

## 🚀 تشغيل الاختبارات

### اختبار سريع
```bash
python tests/test_agents_quick.py
```

### اختبار وكيل معين
```bash
# Planner
python tests/test_planner.py

# Architect
python tests/test_architect.py

# Backend
python tests/test_backend_and_builder.py

# Frontend
python tests/test_frontend.py
```

### اختبار النظام الكامل
```bash
python tests/test_full_system.py
```

### اختبار سير العمل الكامل
```bash
python tests/test_full_workflow.py
```

## 📊 نتائج الاختبار

النتائج يتم حفظها في:
- `test_plan_output.json` - نتائج Planner
- `test_architecture_output.json` - نتائج Architect
- `../output/` - المشاريع المولدة

## ⚙️ المتطلبات

تأكد من:
1. تثبيت المتطلبات: `pip install -r requirements.txt`
2. تشغيل Ollama: `ollama list`
3. وجود نموذج llama3.2: `ollama pull llama3.2`

## 🔍 فحص الإعداد

```bash
python tests/test_setup.py
```

## 📝 ملاحظات

- الاختبارات تستخدم Ollama المحلي
- قد تستغرق الاختبارات الكاملة 10-15 دقيقة
- تأكد من وجود اتصال بالإنترنت لتحميل النماذج
