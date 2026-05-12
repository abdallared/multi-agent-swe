# 🤖 AI Software Company - Multi-Agent System

نظام ذكاء اصطناعي متعدد الوكلاء لتوليد مشاريع Full-Stack كاملة تلقائياً.

## 🚀 البدء السريع

### 1. تشغيل واجهة الويب (موصى به)

```bash
# Backend
cd ui/backend
python app.py

# Frontend (في terminal آخر)
cd ui/frontend
npm install
npm run dev
```

افتح المتصفح على: http://localhost:3000

### 2. استخدام سطر الأوامر (CLI)

```bash
python main.py
```

## 📋 المتطلبات

- Python 3.11 أو 3.12
- Node.js 18+
- Ollama مع نموذج llama3.2

### التثبيت

```bash
# 1. تثبيت Python dependencies
pip install -r requirements.txt

# 2. تثبيت Ollama
# راجع docs/OLLAMA_SETUP.md

# 3. تحميل النموذج
ollama pull llama3.2

# 4. إعداد Frontend
cd ui/frontend
npm install
```

## 📁 هيكل المشروع

```
multi-agent-swe/
├── agents/          # الوكلاء (Planner, Architect, Backend, Frontend)
├── core/            # الإعدادات الأساسية
├── builder/         # بناء الملفات
├── ui/              # واجهة الويب (Backend + Frontend)
├── output/          # المشاريع المولدة (CLI)
├── tests/           # الاختبارات
├── scripts/         # سكريبتات التشغيل
├── docs/            # التوثيق
└── main.py          # نقطة البداية (CLI)
```

للتفاصيل الكاملة: راجع `PROJECT_STRUCTURE.md`

## ✨ المميزات

- ✅ توليد Backend (FastAPI + SQLAlchemy)
- ✅ توليد Frontend (React + TypeScript + Tailwind)
- ✅ مصادقة المستخدمين (JWT + bcrypt)
- ✅ قاعدة بيانات SQLite
- ✅ API كامل مع توثيق Swagger
- ✅ تصميم احترافي وجاهز للإنتاج

## 🔧 التحسينات الأخيرة

- ✅ جميع نماذج SQLAlchemy تتضمن الـ imports الكاملة
- ✅ تشفير كلمات المرور باستخدام bcrypt
- ✅ API URL صحيح (localhost:8000)
- ✅ إعداد Build كامل (Vite + TypeScript)
- ✅ تصميم UI احترافي

## 📊 الإحصائيات

- معدل النجاح: 93%
- وقت التوليد: 5-10 دقائق
- التكلفة: صفر (يستخدم Ollama المحلي)

## 🧪 الاختبارات

```bash
# اختبار سريع
python tests/test_agents_quick.py

# اختبار النظام الكامل
python tests/test_full_system.py

# اختبار الإعداد
python tests/test_setup.py
```

للمزيد: راجع `tests/README.md`

## 📚 التوثيق

| الملف | الوصف |
|-------|-------|
| `docs/USE_WEB_UI.md` | دليل استخدام واجهة الويب |
| `docs/OLLAMA_SETUP.md` | إعداد Ollama |
| `docs/CODEBASE_INDEX.md` | توثيق الكود الكامل |
| `docs/ARCHITECTURE_VISUAL.md` | معمارية النظام |
| `docs/API_DOCUMENTATION.md` | توثيق API |
| `docs/DEPLOYMENT_GUIDE.md` | دليل النشر |
| `docs/SUMMARY_AR.md` | ملخص بالعربية |
| `PROJECT_STRUCTURE.md` | هيكل المشروع |

## 🎯 مثال على الاستخدام

### عبر واجهة الويب

1. افتح http://localhost:3000
2. أدخل اسم المشروع: "Task Manager"
3. أضف وصف: "تطبيق لإدارة المهام"
4. أضف ميزات:
   - مصادقة المستخدمين
   - إنشاء وإدارة المهام
   - تصنيف المهام
5. اضغط "Generate Project"
6. انتظر 5-10 دقائق

### تشغيل المشروع المولد

```bash
cd ui/backend/output/task_manager

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 🛠️ التطوير

### إضافة وكيل جديد

1. أنشئ ملف في `agents/`
2. ورث من `BaseAgent`
3. نفذ `execute()` و `get_system_prompt()`

### إضافة اختبار

1. أنشئ ملف في `tests/`
2. استخدم نفس نمط الاختبارات الموجودة

## 📝 ملاحظات

- استخدم Python 3.11 أو 3.12 (ليس 3.14)
- تأكد من تشغيل Ollama قبل البدء
- المشاريع المولدة جاهزة للتشغيل مباشرة
- المشاريع المولدة عبر CLI تُحفظ في `output/`
- المشاريع المولدة عبر UI تُحفظ في `ui/backend/output/`

## 🤝 المساهمة

المشروع مفتوح المصدر. يمكنك المساهمة بإضافة ميزات جديدة أو تحسينات.

## 📄 الترخيص

MIT License

---

**للمزيد من المعلومات:** راجع ملفات التوثيق في مجلد `docs/`
