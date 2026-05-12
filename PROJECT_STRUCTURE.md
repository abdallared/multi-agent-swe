# 📁 هيكل المشروع - AI Software Company

## 🏗️ البنية العامة

```
multi-agent-swe/
├── 📂 agents/              # الوكلاء (Agents)
│   ├── base_agent.py       # الوكيل الأساسي
│   ├── planner.py          # وكيل التخطيط
│   ├── architect.py        # وكيل المعمارية
│   ├── backend.py          # وكيل Backend
│   ├── frontend.py         # وكيل Frontend
│   ├── testing.py          # وكيل الاختبارات
│   └── docker.py           # وكيل Docker
│
├── 📂 core/                # الإعدادات الأساسية
│   ├── config.py           # إعدادات النظام
│   └── __init__.py
│
├── 📂 builder/             # بناء الملفات
│   └── file_builder.py     # بناء هيكل الملفات
│
├── 📂 memory/              # الذاكرة (مستقبلي)
│   └── __init__.py
│
├── 📂 utils/               # أدوات مساعدة
│   └── (أدوات مساعدة)
│
├── 📂 ui/                  # واجهة الويب
│   ├── backend/            # FastAPI Backend
│   │   ├── app.py          # تطبيق FastAPI
│   │   ├── output/         # المشاريع المولدة
│   │   └── logs/           # سجلات النظام
│   └── frontend/           # React Frontend
│       ├── src/            # كود المصدر
│       ├── public/         # ملفات عامة
│       └── package.json    # المتطلبات
│
├── 📂 output/              # المشاريع المولدة (CLI)
│   └── [project_name]/     # مشروع مولد
│       ├── backend/        # Backend code
│       └── frontend/       # Frontend code
│
├── 📂 tests/               # الاختبارات
│   ├── test_planner.py
│   ├── test_architect.py
│   ├── test_backend_and_builder.py
│   ├── test_frontend.py
│   ├── test_agents_quick.py
│   ├── test_full_system.py
│   ├── test_full_workflow.py
│   ├── test_setup.py
│   └── README.md
│
├── 📂 scripts/             # سكريبتات التشغيل
│   ├── run_backend.bat
│   └── run_frontend.bat
│
├── 📂 docs/                # التوثيق
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE_VISUAL.md
│   ├── CODEBASE_INDEX.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── OLLAMA_SETUP.md
│   ├── PROJECT_PLAN.md
│   ├── SUMMARY_AR.md
│   └── USE_WEB_UI.md
│
├── 📄 main.py              # نقطة البداية (CLI)
├── 📄 requirements.txt     # المتطلبات
├── 📄 README.md            # دليل البدء السريع
├── 📄 .env.example         # مثال للإعدادات
└── 📄 .gitignore           # ملفات Git المستبعدة
```

## 📦 المجلدات الرئيسية

### 1. `agents/` - الوكلاء
يحتوي على جميع الوكلاء المسؤولة عن توليد الكود:
- **Planner**: تحليل المتطلبات وتحديد الميزات
- **Architect**: تصميم المعمارية والـ API
- **Backend**: توليد كود FastAPI
- **Frontend**: توليد كود React
- **Testing**: توليد اختبارات (مستقبلي)
- **Docker**: توليد Docker configs (مستقبلي)

### 2. `core/` - الإعدادات
- **config.py**: إعدادات Ollama والنظام
- يحتوي على الإعدادات المشتركة بين جميع الوكلاء

### 3. `builder/` - البناء
- **file_builder.py**: بناء هيكل الملفات والمجلدات
- يقوم بإنشاء المشروع الفعلي من الكود المولد

### 4. `ui/` - واجهة الويب
#### `ui/backend/`
- FastAPI backend لواجهة الويب
- WebSocket للتحديثات الفورية
- حفظ المشاريع في `output/`

#### `ui/frontend/`
- React + TypeScript + Tailwind
- واجهة مستخدم حديثة
- اتصال WebSocket للتحديثات

### 5. `output/` - المشاريع المولدة
- المشاريع المولدة عبر CLI تُحفظ هنا
- المشاريع المولدة عبر UI تُحفظ في `ui/backend/output/`

### 6. `tests/` - الاختبارات
- اختبارات لجميع الوكلاء
- اختبارات النظام الكامل
- اختبارات الإعداد

### 7. `scripts/` - السكريبتات
- سكريبتات تشغيل سريعة
- أدوات مساعدة

### 8. `docs/` - التوثيق
- جميع ملفات التوثيق
- دلائل الاستخدام
- توثيق API

## 🔄 سير العمل

### CLI Mode
```
main.py → Planner → Architect → Backend → Builder → Frontend → output/
```

### Web UI Mode
```
ui/frontend → ui/backend/app.py → Agents → ui/backend/output/
```

## 📊 تدفق البيانات

```
User Input
    ↓
Planner Agent (تحليل المتطلبات)
    ↓
Architect Agent (تصميم المعمارية)
    ↓
Backend Agent (توليد Backend)
    ↓
File Builder (بناء الملفات)
    ↓
Frontend Agent (توليد Frontend)
    ↓
Output (المشروع الكامل)
```

## 🎯 الملفات الرئيسية

| الملف | الوظيفة |
|-------|---------|
| `main.py` | نقطة البداية للـ CLI |
| `ui/backend/app.py` | نقطة البداية للـ Web UI |
| `agents/base_agent.py` | الوكيل الأساسي |
| `core/config.py` | إعدادات النظام |
| `builder/file_builder.py` | بناء الملفات |

## 📝 ملاحظات

- **المشاريع المولدة**: تُحفظ في `output/` (CLI) أو `ui/backend/output/` (Web UI)
- **السجلات**: تُحفظ في `ui/backend/logs/`
- **الاختبارات**: جميعها في مجلد `tests/`
- **التوثيق**: جميعه في مجلد `docs/`

## 🚀 البدء السريع

### CLI
```bash
python main.py
```

### Web UI
```bash
# Backend
cd ui/backend
python app.py

# Frontend
cd ui/frontend
npm run dev
```

## 🔧 التطوير

### إضافة وكيل جديد
1. أنشئ ملف في `agents/`
2. ورث من `BaseAgent`
3. نفذ `execute()` و `get_system_prompt()`

### إضافة اختبار
1. أنشئ ملف في `tests/`
2. استخدم نفس نمط الاختبارات الموجودة

### إضافة توثيق
1. أنشئ ملف في `docs/`
2. اتبع نفس تنسيق الملفات الموجودة

## 📚 المراجع

- **README.md** - دليل البدء السريع
- **docs/CODEBASE_INDEX.md** - توثيق الكود الكامل
- **docs/ARCHITECTURE_VISUAL.md** - معمارية النظام
- **tests/README.md** - دليل الاختبارات
