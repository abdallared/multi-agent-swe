# 🤝 المساهمة في المشروع

شكراً لاهتمامك بالمساهمة في AI Software Company!

## 🎯 كيفية المساهمة

### 1. Fork المشروع
```bash
git clone https://github.com/your-username/multi-agent-swe.git
cd multi-agent-swe
```

### 2. إنشاء Branch جديد
```bash
git checkout -b feature/amazing-feature
```

### 3. إجراء التغييرات

#### إضافة وكيل جديد
1. أنشئ ملف في `agents/`
2. ورث من `BaseAgent`
3. نفذ الدوال المطلوبة:
```python
from agents.base_agent import BaseAgent

class MyNewAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "Your system prompt here"
    
    def execute(self, context: dict) -> dict:
        # Your implementation
        return {"status": "completed"}
```

#### إضافة اختبار
1. أنشئ ملف في `tests/`
2. اتبع نفس النمط:
```python
def test_my_feature():
    # Your test code
    assert result == expected
```

#### تحديث التوثيق
1. حدّث الملفات في `docs/`
2. تأكد من تحديث `PROJECT_STRUCTURE.md` إذا لزم الأمر

### 4. اختبار التغييرات

```bash
# اختبار سريع
python tests/test_agents_quick.py

# اختبار الميزة الجديدة
python tests/test_your_feature.py

# اختبار النظام الكامل
python tests/test_full_system.py
```

### 5. Commit التغييرات

```bash
git add .
git commit -m "feat: add amazing feature"
```

#### نمط Commit Messages
- `feat:` - ميزة جديدة
- `fix:` - إصلاح bug
- `docs:` - تحديث التوثيق
- `test:` - إضافة اختبارات
- `refactor:` - إعادة هيكلة الكود
- `style:` - تنسيق الكود
- `chore:` - مهام صيانة

### 6. Push إلى GitHub

```bash
git push origin feature/amazing-feature
```

### 7. إنشاء Pull Request

1. اذهب إلى GitHub
2. اضغط "New Pull Request"
3. اختر branch الخاص بك
4. أضف وصف واضح للتغييرات

## 📋 معايير الكود

### Python
- اتبع PEP 8
- استخدم type hints
- أضف docstrings للدوال
- اكتب كود واضح وقابل للقراءة

### TypeScript/React
- استخدم TypeScript
- اتبع معايير React
- استخدم Tailwind CSS للتصميم
- اكتب مكونات قابلة لإعادة الاستخدام

## 🧪 الاختبارات

- أضف اختبارات لأي ميزة جديدة
- تأكد من نجاح جميع الاختبارات
- اختبر على Python 3.11 و 3.12

## 📚 التوثيق

- حدّث التوثيق لأي تغيير
- أضف أمثلة للاستخدام
- اكتب بوضوح وبساطة

## 🐛 الإبلاغ عن Bugs

### قبل الإبلاغ
1. تحقق من Issues الموجودة
2. تأكد من استخدام أحدث إصدار
3. جرب إعادة إنتاج المشكلة

### عند الإبلاغ
قدم:
- وصف واضح للمشكلة
- خطوات إعادة إنتاج المشكلة
- السلوك المتوقع
- السلوك الفعلي
- لقطات شاشة (إن أمكن)
- معلومات البيئة:
  - نظام التشغيل
  - إصدار Python
  - إصدار Node.js
  - إصدار Ollama

## 💡 اقتراح ميزات

### قبل الاقتراح
1. تحقق من Issues الموجودة
2. تأكد من أن الميزة تناسب المشروع

### عند الاقتراح
قدم:
- وصف واضح للميزة
- حالات الاستخدام
- أمثلة على التنفيذ
- فوائد الميزة

## 🎨 أفكار للمساهمة

### وكلاء جدد
- [ ] وكيل توليد اختبارات
- [ ] وكيل توليد Docker configs
- [ ] وكيل توليد CI/CD
- [ ] وكيل توليد توثيق

### تحسينات
- [ ] دعم قواعد بيانات إضافية (PostgreSQL, MongoDB)
- [ ] دعم أطر عمل إضافية (Django, Vue.js)
- [ ] تحسين واجهة الويب
- [ ] إضافة قوالب جاهزة

### توثيق
- [ ] فيديوهات تعليمية
- [ ] أمثلة إضافية
- [ ] ترجمة التوثيق
- [ ] دليل استكشاف الأخطاء

## 📞 التواصل

- افتح Issue للأسئلة
- استخدم Discussions للنقاشات
- راجع التوثيق أولاً

## ✅ Checklist قبل Pull Request

- [ ] الكود يعمل بدون أخطاء
- [ ] جميع الاختبارات تنجح
- [ ] التوثيق محدّث
- [ ] Commit messages واضحة
- [ ] الكود يتبع معايير المشروع
- [ ] لا توجد ملفات غير ضرورية

## 🙏 شكراً

شكراً لمساهمتك في تحسين AI Software Company!

كل مساهمة، مهما كانت صغيرة، تساعد في جعل المشروع أفضل.
