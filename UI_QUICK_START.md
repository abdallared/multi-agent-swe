# 🚀 UI Quick Start - AI Software Company

## ⚡ البداية السريعة (5 دقائق)

### الخطوة 1: تأكد من المتطلبات ✅

```bash
# تحقق من Ollama
ollama list

# تحقق من Python
python --version

# تحقق من Node.js
node --version
```

---

### الخطوة 2: تثبيت Frontend Dependencies 📦

```bash
cd ui/frontend
npm install
```

**الوقت**: 1-2 دقيقة

---

### الخطوة 3: تشغيل النظام 🚀

#### خيار A: استخدام Script (موصى به)

**Windows:**
```bash
cd ui
start.bat
```

**Linux/Mac:**
```bash
cd ui
chmod +x start.sh
./start.sh
```

#### خيار B: يدوياً

**Terminal 1 - Backend:**
```bash
cd ui/backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd ui/frontend
npm run dev
```

---

### الخطوة 4: افتح المتصفح 🌐

```
http://localhost:3000
```

---

## 🎨 واجهة المستخدم

```
┌─────────────┬──────────────────┬─────────────┐
│             │                  │             │
│   📁 Files  │   📝 Code        │   💬 Chat   │
│             │                  │             │
│  Explorer   │   Preview        │  Interface  │
│             │                  │             │
│  (Left)     │   (Center)       │  (Right)    │
│             │                  │             │
└─────────────┴──────────────────┴─────────────┘
```

### الأقسام:

1. **📁 Left Sidebar**: File Explorer
   - عرض ملفات المشروع
   - Folders قابلة للتوسيع
   - Click على file لعرضه

2. **📝 Center Panel**: Code Preview
   - عرض محتوى الملفات
   - Syntax highlighting
   - Copy/Download (قريباً)

3. **💬 Right Sidebar**: Chat Interface
   - وصف المشروع
   - Real-time updates
   - Progress tracking

---

## 💡 أمثلة للاستخدام

### مثال 1: Todo App

```
Build a simple todo app with user authentication
```

**النتيجة**:
- ✅ Backend (FastAPI)
- ✅ Frontend (React)
- ✅ Database schema
- ✅ ~10 files

**الوقت**: ~5 دقائق

---

### مثال 2: Blog Platform

```
Build a blog platform with posts, comments, and user profiles
```

**النتيجة**:
- ✅ Full stack application
- ✅ User management
- ✅ Post CRUD
- ✅ ~15 files

**الوقت**: ~7 دقائق

---

### مثال 3: E-commerce

```
Build an e-commerce platform with products, cart, and orders
```

**النتيجة**:
- ✅ Product catalog
- ✅ Shopping cart
- ✅ Order management
- ✅ ~20 files

**الوقت**: ~10 دقائق

---

## 🔄 سير العمل

### 1. أدخل وصف المشروع

في Chat Interface (يمين):
```
Build a task management app with teams
```

### 2. شاهد التوليد Real-time

```
🔄 Phase 1: Planning - Starting...
✅ Phase 1: Planning - Completed
   Features: 5
   User Stories: 4

🔄 Phase 2: Architecture - Starting...
✅ Phase 2: Architecture - Completed
   Backend: FastAPI
   Frontend: React
   Database: PostgreSQL

🔄 Phase 3: Backend Code - Starting...
✅ Phase 3: Backend Code - Completed
   Files: 5

🔄 Phase 4: File Building - Starting...
✅ Phase 4: File Building - Completed

🔄 Phase 5: Frontend Code - Starting...
✅ Phase 5: Frontend Code - Completed
   Files: 5

🎉 Project "Task Management App" generated successfully!
```

### 3. استكشف الملفات

في File Explorer (يسار):
- Click على folder لتوسيعه
- Click على file لعرض محتواه
- شاهد الكود في Center Panel

---

## 🎯 الميزات

### ✅ متوفر الآن

- ✅ Chat interface
- ✅ Real-time generation
- ✅ File tree viewer
- ✅ Code preview
- ✅ Progress tracking
- ✅ Error handling
- ✅ WebSocket communication

### 🔜 قريباً

- 🔜 Syntax highlighting
- 🔜 Download project as ZIP
- 🔜 Project history
- 🔜 File editing
- 🔜 Dark/Light theme
- 🔜 Mobile responsive

---

## 🐛 استكشاف الأخطاء

### المشكلة: Backend لا يعمل

```bash
# الحل 1: تحقق من Ollama
ollama list

# الحل 2: أعد تشغيل Backend
cd ui/backend
python app.py
```

### المشكلة: Frontend لا يعمل

```bash
# الحل: أعد تثبيت Dependencies
cd ui/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### المشكلة: WebSocket connection failed

```bash
# الحل: تأكد من Backend يعمل
curl http://localhost:8000/api/health

# يجب أن ترى:
# {"status":"healthy","ollama_connected":true}
```

---

## 📊 الأداء

### أوقات التوليد

| Phase | الوقت | الوصف |
|-------|-------|-------|
| Planning | 1-2 min | تحليل المتطلبات |
| Architecture | 2-3 min | تصميم النظام |
| Backend | 1-2 min | توليد الكود |
| File Building | <1 sec | إنشاء الملفات |
| Frontend | 1-2 min | توليد UI |

**الإجمالي**: 5-10 دقائق

### نصائح للأداء

1. **استخدم نماذج أصغر**:
   ```bash
   # في .env
   PLANNER_MODEL=llama3.2:3b
   ```

2. **أغلق التطبيقات الأخرى**

3. **استخدم SSD**

---

## 🎓 نصائح الاستخدام

### ✅ افعل

- استخدم أوصاف واضحة ومحددة
- ابدأ بمشاريع بسيطة
- راقب Progress في Chat
- استكشف الملفات المولدة

### ❌ لا تفعل

- لا تغلق المتصفح أثناء التوليد
- لا تبدأ مشروع جديد قبل انتهاء السابق
- لا تستخدم أوصاف غامضة

---

## 📞 الدعم

### الوثائق

- `ui/README.md` - توثيق كامل
- `COMPLETE_GUIDE.md` - دليل شامل
- `FAQ.md` - أسئلة شائعة

### المشاكل

- GitHub Issues
- Discord (قريباً)

---

## 🎉 ابدأ الآن!

```bash
# 1. تثبيت Frontend
cd ui/frontend
npm install

# 2. تشغيل النظام
cd ..
start.bat  # Windows
# أو
./start.sh  # Linux/Mac

# 3. افتح المتصفح
http://localhost:3000

# 4. ابدأ التوليد!
```

---

**Version**: 2.0.0  
**Date**: 2026-04-10  
**Status**: ✅ Ready to Use

**🚀 استمتع بالتوليد!**
