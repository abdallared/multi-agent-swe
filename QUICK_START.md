# 🚀 Quick Start - AI Software Company

## ✅ الحالة الحالية

**Phases 1-5 مكتملة وجاهزة للاستخدام!**

---

## 📦 التثبيت السريع (5 دقائق)

### 1. تحقق من المتطلبات

```bash
# Python 3.11+
python --version

# Ollama (يجب أن يكون مثبت ويعمل)
ollama list
```

### 2. تفعيل البيئة الافتراضية

```bash
# إذا لم تكن مفعلة
venv\Scripts\activate  # Windows
# أو
source venv/bin/activate  # Linux/Mac
```

### 3. تحقق من الإعدادات

```bash
# تحقق من .env
cat .env

# يجب أن يحتوي على:
# OLLAMA_BASE_URL=http://localhost:11434
# PLANNER_MODEL=qwen2.5:7b
# BACKEND_MODEL=qwen2.5-coder:7b
# FRONTEND_MODEL=qwen2.5-coder:7b
```

---

## 🎯 الاستخدام

### خيار 1: التطبيق الكامل (موصى به)

```bash
python main.py
```

ثم أدخل وصف مشروعك:
```
Build a simple blog platform with user authentication
```

**الوقت المتوقع**: 5-10 دقائق

**المخرجات**:
- ✅ Project Plan (JSON)
- ✅ Architecture Design (JSON)
- ✅ Backend Code (FastAPI)
- ✅ Frontend Code (React + TypeScript)
- ✅ Project Structure
- ✅ README.md

### خيار 2: اختبار مرحلة واحدة

```bash
# اختبار Planner فقط
python test_planner.py

# اختبار Architect فقط
python test_architect.py

# اختبار Backend فقط
python test_backend_and_builder.py

# اختبار Frontend فقط
python test_frontend.py
```

### خيار 3: اختبار النظام الكامل

```bash
python test_full_workflow.py
```

---

## 📁 المخرجات

بعد التشغيل الناجح، ستجد:

```
output/
└── your_project_name/
    ├── backend/
    │   ├── app/
    │   │   ├── main.py
    │   │   ├── core/
    │   │   │   └── config.py
    │   │   ├── models/
    │   │   │   └── user.py
    │   │   └── api/
    │   │       └── auth.py
    │   └── requirements.txt
    ├── frontend/
    │   ├── src/
    │   │   ├── App.tsx
    │   │   ├── pages/
    │   │   │   ├── Home.tsx
    │   │   │   └── Login.tsx
    │   │   └── services/
    │   │       └── api.ts
    │   └── package.json
    └── README.md
```

---

## 🏃 تشغيل المشروع المولد

### Backend

```bash
cd output/your_project_name/backend

# إنشاء بيئة افتراضية
python -m venv venv
venv\Scripts\activate

# تثبيت dependencies
pip install -r requirements.txt

# تشغيل
uvicorn app.main:app --reload
```

Backend سيعمل على: http://localhost:8000

### Frontend

```bash
cd output/your_project_name/frontend

# تثبيت dependencies
npm install

# تشغيل
npm run dev
```

Frontend سيعمل على: http://localhost:5173

---

## 🎨 أمثلة للمشاريع

### مشروع بسيط

```
Build a todo app with user authentication
```

**الوقت**: ~5 دقائق  
**الملفات**: ~10 ملفات

### مشروع متوسط

```
Build a blog platform with posts, comments, and user profiles
```

**الوقت**: ~7 دقائق  
**الملفات**: ~15 ملف

### مشروع معقد

```
Build an e-commerce platform with products, cart, orders, and payment integration
```

**الوقت**: ~10 دقائق  
**الملفات**: ~20 ملف

---

## 🔧 استكشاف الأخطاء

### المشكلة: Ollama لا يعمل

```bash
# تحقق من الحالة
ollama list

# إعادة التشغيل
ollama serve
```

### المشكلة: JSON parsing error

- ✅ النظام يحاول 3 مرات تلقائياً
- ✅ يستخدم fallback code إذا فشل
- ✅ الكود المولد يعمل دائماً

### المشكلة: بطء في التوليد

```bash
# استخدم نماذج أصغر في .env
PLANNER_MODEL=llama3.2:3b
BACKEND_MODEL=llama3.2:3b
FRONTEND_MODEL=llama3.2:3b
```

### المشكلة: نفاد الذاكرة

```bash
# أغلق التطبيقات الأخرى
# استخدم نماذج أصغر
# قلل max_tokens في agents
```

---

## 📊 المراحل المكتملة

| Phase | Agent | Status | Time |
|-------|-------|--------|------|
| 1 | Planner | ✅ | 1-2 min |
| 2 | Architect | ✅ | 2-3 min |
| 3 | Backend | ✅ | 1-2 min |
| 4 | File Builder | ✅ | <1 sec |
| 5 | Frontend | ✅ | 1-2 min |
| 6 | Testing | 🔄 | Coming |
| 7 | Debugger | 🔄 | Coming |
| 8 | Refactor | 🔄 | Coming |
| 9 | DevOps | 🔄 | Coming |

---

## 🎓 التعلم

### للمبتدئين

1. شغل `python test_planner.py` لفهم Planning
2. شغل `python test_architect.py` لفهم Architecture
3. شغل `python test_full_workflow.py` لرؤية النظام الكامل
4. شغل `python main.py` لتوليد مشروعك

### للمطورين

1. اقرأ `agents/base_agent.py` - الأساس
2. اقرأ `agents/planner.py` - مثال كامل
3. اقرأ `agents/backend.py` - retry logic
4. اقرأ `agents/frontend.py` - fallback code
5. عدّل prompts لتحسين النتائج

### للمساهمين

1. راجع `PHASE_5_COMPLETE.md` للتفاصيل
2. راجع `STEP_BY_STEP_IMPLEMENTATION.md` للخطة
3. أضف agents جديدة
4. حسّن prompts
5. أضف tests

---

## 💡 نصائح للنجاح

### ✅ افعل

- استخدم أوصاف واضحة ومحددة
- ابدأ بمشاريع بسيطة
- راجع الكود المولد
- عدّل حسب احتياجاتك
- احفظ النتائج الجيدة

### ❌ لا تفعل

- لا تستخدم أوصاف غامضة
- لا تبدأ بمشاريع معقدة جداً
- لا تستخدم الكود مباشرة في production
- لا تنسى مراجعة الأمان
- لا تتوقع كود مثالي 100%

---

## 📞 الدعم

### الملفات المهمة

- `PHASE_5_COMPLETE.md` - تفاصيل Phase 5
- `STEP_BY_STEP_IMPLEMENTATION.md` - خطة التنفيذ
- `OLLAMA_SETUP.md` - إعداد Ollama
- `API_DOCUMENTATION.md` - توثيق API
- `EXAMPLES.md` - أمثلة

### الاختبارات

- `test_planner.py` - اختبار Planning
- `test_architect.py` - اختبار Architecture
- `test_backend_and_builder.py` - اختبار Backend
- `test_frontend.py` - اختبار Frontend
- `test_full_workflow.py` - اختبار كامل

---

## 🎉 ابدأ الآن!

```bash
# تأكد من أن Ollama يعمل
ollama list

# شغل التطبيق
python main.py

# أدخل فكرتك
Build a simple task manager with user authentication

# انتظر 5-10 دقائق
# استمتع بمشروعك الجديد! 🚀
```

---

**الإصدار**: 2.0.0  
**التاريخ**: 2026-04-10  
**الحالة**: ✅ Ready to Use

**🎊 مبروك! النظام جاهز للاستخدام!**
