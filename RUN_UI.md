# 🚀 تشغيل الـ UI - خطوة بخطوة

## ✅ الخطوات الصحيحة

### أنت الآن في: `ui/frontend`

### الخطوة 1: ارجع للمجلد الرئيسي

```powershell
cd ../..
```

الآن أنت في: `multi-agent-swe/`

---

### الخطوة 2: شغل Backend

**Terminal 1:**
```powershell
cd ui/backend
python app.py
```

سترى:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ Backend يعمل على http://localhost:8000

**لا تغلق هذا Terminal!**

---

### الخطوة 3: شغل Frontend

**Terminal 2 (جديد):**
```powershell
cd ui/frontend
npm run dev
```

سترى:
```
  VITE v5.0.7  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

✅ Frontend يعمل على http://localhost:3000

---

### الخطوة 4: افتح المتصفح

```
http://localhost:3000
```

---

## 🎯 الأوامر الكاملة

### من مجلد `multi-agent-swe/`:

**Terminal 1 - Backend:**
```powershell
cd ui/backend
python app.py
```

**Terminal 2 - Frontend:**
```powershell
cd ui/frontend
npm run dev
```

---

## 🎨 ما ستراه

```
┌─────────────────────────────────────────────────────┐
│          AI Software Company - Web UI                │
├─────────────┬──────────────────┬────────────────────┤
│             │                  │                    │
│  📁 Files   │   📝 Code        │   💬 Chat         │
│             │                  │                    │
│  (Empty)    │   (Empty)        │   Welcome!        │
│             │                  │                    │
│             │                  │   [Input box]     │
│             │                  │   [Send button]   │
│             │                  │                    │
└─────────────┴──────────────────┴────────────────────┘
```

---

## 💡 جرب الآن!

في Chat (يمين)، اكتب:
```
Build a simple todo app
```

واضغط Enter أو Send

---

## 🐛 إذا واجهت مشاكل

### المشكلة: Backend لا يعمل

```powershell
# تحقق من Ollama
ollama list

# إذا لم يعمل، شغله:
ollama serve
```

### المشكلة: Frontend لا يعمل

```powershell
# أعد تثبيت
cd ui/frontend
rm -r node_modules
npm install
npm run dev
```

### المشكلة: Port مستخدم

```powershell
# Backend على port آخر
# في ui/backend/app.py غير:
uvicorn.run(app, host="0.0.0.0", port=8001)

# Frontend على port آخر
# في ui/frontend/vite.config.ts غير:
server: { port: 3001 }
```

---

## ✅ Checklist

- [ ] Backend يعمل على http://localhost:8000
- [ ] Frontend يعمل على http://localhost:3000
- [ ] Ollama يعمل (`ollama list`)
- [ ] المتصفح مفتوح على http://localhost:3000
- [ ] Chat interface ظاهر

---

**🎉 استمتع بالـ UI!**
