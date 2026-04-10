# 💡 أمثلة عملية - AI Software Company

## 🎯 نظرة عامة

هذا الملف يحتوي على أمثلة عملية لاستخدام النظام في سيناريوهات مختلفة.

---

## 📝 مثال 1: Task Management App

### User Prompt

```
Build a task management web application with the following features:
- User authentication and authorization
- Create, read, update, delete tasks
- Task prioritization using AI based on deadlines and importance
- Real-time notifications
- Team collaboration (assign tasks to team members)
- Dashboard with analytics
- Mobile-responsive design
```

### Expected Output

```
✓ Project Generated Successfully!

Project Name: TaskMaster AI
Location: ./output/taskmaster_ai/
GitHub: https://github.com/user/taskmaster-ai

Structure:
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   └── users.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── task.py
│   │   ├── services/
│   │   │   ├── ai_prioritization.py
│   │   │   └── notifications.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── ai/
│   ├── models/
│   │   └── priority_predictor.py
│   ├── training/
│   └── requirements.txt
│
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── README.md

Tech Stack:
- Backend: FastAPI + PostgreSQL + Redis
- Frontend: React + TypeScript + Tailwind CSS
- AI: Python + scikit-learn
- Deployment: Docker + GitHub Actions

Tests: 67 tests, 89% coverage
Time: 18 minutes
```

---

## 🛒 مثال 2: E-commerce Platform

### User Prompt

```
Create a full-featured e-commerce platform with:
- Product catalog with categories and search
- Shopping cart and wishlist
- Payment integration (Stripe)
- Order management and tracking
- User reviews and ratings
- Admin dashboard for inventory management
- Email notifications
- Responsive design
```

### Generated Architecture

```json
{
  "tech_stack": {
    "backend": {
      "framework": "Django",
      "language": "Python 3.11",
      "orm": "Django ORM",
      "authentication": "JWT + OAuth2"
    },
    "frontend": {
      "framework": "Next.js",
      "language": "TypeScript",
      "state_management": "Redux Toolkit",
      "styling": "Tailwind CSS"
    },
    "database": {
      "primary": "PostgreSQL",
      "cache": "Redis",
      "search": "Elasticsearch"
    }
  },
  "modules": [
    {
      "name": "auth_module",
      "type": "backend",
      "files": ["models.py", "views.py", "serializers.py"]
    },
    {
      "name": "products_module",
      "type": "backend",
      "files": ["models.py", "views.py", "search.py"]
    },
    {
      "name": "orders_module",
      "type": "backend",
      "files": ["models.py", "views.py", "payment.py"]
    },
    {
      "name": "admin_dashboard",
      "type": "frontend",
      "files": ["Dashboard.tsx", "Inventory.tsx", "Orders.tsx"]
    }
  ]
}
```

### Database Schema

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    category_id UUID REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Orders
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payment_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Order Items
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

---

## 🏥 مثال 3: Healthcare Appointment System

### User Prompt

```
Build a healthcare appointment booking system with:
- Patient registration and profiles
- Doctor profiles with specializations
- Appointment scheduling with calendar view
- Video consultation integration
- Medical records management
- Prescription management
- Payment processing
- SMS and email reminders
- HIPAA compliance features
```

### Key Features Generated

#### 1. Authentication & Authorization

```python
# backend/app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.services.auth import AuthService
from app.schemas.user import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register")
async def register(user: UserCreate):
    """
    تسجيل مستخدم جديد (مريض أو طبيب)
    """
    return await AuthService.register_user(user)

@router.post("/login")
async def login(credentials: UserLogin):
    """
    تسجيل الدخول
    """
    return await AuthService.authenticate(credentials)

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    الحصول على بيانات المستخدم الحالي
    """
    return await AuthService.get_user_from_token(token)
```

#### 2. Appointment Booking

```python
# backend/app/api/appointments.py

from fastapi import APIRouter, Depends
from app.services.appointments import AppointmentService
from app.schemas.appointment import AppointmentCreate

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/")
async def create_appointment(
    appointment: AppointmentCreate,
    current_user = Depends(get_current_user)
):
    """
    حجز موعد جديد
    """
    # التحقق من توفر الموعد
    if not await AppointmentService.is_slot_available(
        appointment.doctor_id,
        appointment.datetime
    ):
        raise HTTPException(400, "Time slot not available")
    
    # إنشاء الموعد
    new_appointment = await AppointmentService.create(
        patient_id=current_user.id,
        appointment_data=appointment
    )
    
    # إرسال تأكيد
    await NotificationService.send_appointment_confirmation(
        new_appointment
    )
    
    return new_appointment

@router.get("/available-slots")
async def get_available_slots(
    doctor_id: str,
    date: str
):
    """
    الحصول على المواعيد المتاحة
    """
    return await AppointmentService.get_available_slots(
        doctor_id,
        date
    )
```

#### 3. Video Consultation

```typescript
// frontend/src/components/VideoConsultation.tsx

import React, { useEffect, useRef } from 'react';
import { useVideoCall } from '../hooks/useVideoCall';

interface VideoConsultationProps {
  appointmentId: string;
  isDoctor: boolean;
}

export const VideoConsultation: React.FC<VideoConsultationProps> = ({
  appointmentId,
  isDoctor
}) => {
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  
  const {
    startCall,
    endCall,
    toggleMute,
    toggleVideo,
    isMuted,
    isVideoOff
  } = useVideoCall(appointmentId);
  
  useEffect(() => {
    startCall(localVideoRef.current, remoteVideoRef.current);
    
    return () => {
      endCall();
    };
  }, []);
  
  return (
    <div className="video-consultation">
      <div className="video-grid">
        <video ref={remoteVideoRef} autoPlay className="remote-video" />
        <video ref={localVideoRef} autoPlay muted className="local-video" />
      </div>
      
      <div className="controls">
        <button onClick={toggleMute}>
          {isMuted ? 'Unmute' : 'Mute'}
        </button>
        <button onClick={toggleVideo}>
          {isVideoOff ? 'Start Video' : 'Stop Video'}
        </button>
        <button onClick={endCall} className="end-call">
          End Call
        </button>
      </div>
    </div>
  );
};
```

---

## 🍕 مثال 4: Food Delivery Platform

### User Prompt

```
Build a food delivery platform similar to Uber Eats with:
- Restaurant listings with menus
- Real-time order tracking with GPS
- AI-powered restaurant recommendations
- Multiple payment methods
- Rating and review system
- Driver management
- Push notifications
- Promo codes and discounts
```

### AI Recommendation Engine

```python
# ai/models/recommendation_engine.py

import numpy as np
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict

class RestaurantRecommender:
    """
    نظام توصيات المطاعم باستخدام Collaborative Filtering
    """
    
    def __init__(self):
        self.model = NearestNeighbors(
            n_neighbors=10,
            algorithm='ball_tree',
            metric='cosine'
        )
        self.user_item_matrix = None
        self.restaurant_ids = []
    
    def train(self, orders_data: List[Dict]):
        """
        تدريب النموذج على بيانات الطلبات
        """
        # بناء User-Item Matrix
        self.user_item_matrix = self._build_matrix(orders_data)
        
        # تدريب النموذج
        self.model.fit(self.user_item_matrix)
    
    def recommend(
        self,
        user_id: str,
        n_recommendations: int = 5
    ) -> List[str]:
        """
        توصية مطاعم للمستخدم
        """
        # الحصول على تفضيلات المستخدم
        user_vector = self._get_user_vector(user_id)
        
        # إيجاد المطاعم المشابهة
        distances, indices = self.model.kneighbors(
            user_vector.reshape(1, -1),
            n_neighbors=n_recommendations
        )
        
        # إرجاع IDs المطاعم
        recommended_ids = [
            self.restaurant_ids[idx]
            for idx in indices[0]
        ]
        
        return recommended_ids
    
    def _build_matrix(self, orders_data: List[Dict]) -> np.ndarray:
        """
        بناء User-Item Matrix
        """
        # Implementation...
        pass
    
    def _get_user_vector(self, user_id: str) -> np.ndarray:
        """
        الحصول على vector المستخدم
        """
        # Implementation...
        pass
```

### Real-time Order Tracking

```python
# backend/app/services/tracking.py

from fastapi import WebSocket
from typing import Dict
import asyncio

class OrderTrackingService:
    """
    خدمة تتبع الطلبات في الوقت الفعلي
    """
    
    active_connections: Dict[str, WebSocket] = {}
    
    @classmethod
    async def connect(cls, order_id: str, websocket: WebSocket):
        """
        اتصال WebSocket جديد
        """
        await websocket.accept()
        cls.active_connections[order_id] = websocket
    
    @classmethod
    async def disconnect(cls, order_id: str):
        """
        قطع الاتصال
        """
        if order_id in cls.active_connections:
            del cls.active_connections[order_id]
    
    @classmethod
    async def send_location_update(
        cls,
        order_id: str,
        location: Dict[str, float]
    ):
        """
        إرسال تحديث الموقع
        """
        if order_id in cls.active_connections:
            websocket = cls.active_connections[order_id]
            await websocket.send_json({
                "type": "location_update",
                "order_id": order_id,
                "location": location,
                "timestamp": datetime.now().isoformat()
            })
    
    @classmethod
    async def send_status_update(
        cls,
        order_id: str,
        status: str
    ):
        """
        إرسال تحديث الحالة
        """
        if order_id in cls.active_connections:
            websocket = cls.active_connections[order_id]
            await websocket.send_json({
                "type": "status_update",
                "order_id": order_id,
                "status": status,
                "timestamp": datetime.now().isoformat()
            })

# WebSocket Endpoint
@app.websocket("/ws/orders/{order_id}/track")
async def track_order(websocket: WebSocket, order_id: str):
    await OrderTrackingService.connect(order_id, websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        await OrderTrackingService.disconnect(order_id)
```

---

## 📱 مثال 5: Social Media App

### User Prompt

```
Create a social media application with:
- User profiles with bio and photos
- Post creation (text, images, videos)
- Like, comment, and share functionality
- Follow/unfollow users
- News feed with algorithmic sorting
- Direct messaging
- Stories feature (24-hour posts)
- Content moderation using AI
- Hashtags and trending topics
```

### Content Moderation AI

```python
# ai/models/content_moderator.py

from transformers import pipeline
from typing import Dict, List

class ContentModerator:
    """
    نظام فحص المحتوى باستخدام AI
    """
    
    def __init__(self):
        # تحميل نموذج التصنيف
        self.classifier = pipeline(
            "text-classification",
            model="unitary/toxic-bert"
        )
        
        # تحميل نموذج فحص الصور
        self.image_classifier = pipeline(
            "image-classification",
            model="Falconsai/nsfw_image_detection"
        )
    
    def moderate_text(self, text: str) -> Dict:
        """
        فحص النص
        """
        result = self.classifier(text)[0]
        
        is_safe = result['label'] == 'non-toxic'
        confidence = result['score']
        
        return {
            "is_safe": is_safe,
            "confidence": confidence,
            "label": result['label'],
            "action": "approve" if is_safe else "review"
        }
    
    def moderate_image(self, image_path: str) -> Dict:
        """
        فحص الصورة
        """
        result = self.image_classifier(image_path)[0]
        
        is_safe = result['label'] == 'normal'
        confidence = result['score']
        
        return {
            "is_safe": is_safe,
            "confidence": confidence,
            "label": result['label'],
            "action": "approve" if is_safe else "block"
        }
    
    def moderate_post(
        self,
        text: str = None,
        images: List[str] = None
    ) -> Dict:
        """
        فحص منشور كامل
        """
        results = {
            "text": None,
            "images": [],
            "overall_safe": True
        }
        
        # فحص النص
        if text:
            results["text"] = self.moderate_text(text)
            if not results["text"]["is_safe"]:
                results["overall_safe"] = False
        
        # فحص الصور
        if images:
            for image in images:
                image_result = self.moderate_image(image)
                results["images"].append(image_result)
                if not image_result["is_safe"]:
                    results["overall_safe"] = False
        
        return results
```

### News Feed Algorithm

```python
# backend/app/services/feed.py

from typing import List, Dict
import numpy as np

class FeedAlgorithm:
    """
    خوارزمية ترتيب المنشورات في الـ Feed
    """
    
    def __init__(self):
        self.weights = {
            "recency": 0.3,
            "engagement": 0.4,
            "relevance": 0.3
        }
    
    def rank_posts(
        self,
        posts: List[Dict],
        user_id: str
    ) -> List[Dict]:
        """
        ترتيب المنشورات
        """
        scored_posts = []
        
        for post in posts:
            score = self._calculate_score(post, user_id)
            scored_posts.append({
                "post": post,
                "score": score
            })
        
        # ترتيب حسب النتيجة
        scored_posts.sort(key=lambda x: x["score"], reverse=True)
        
        return [item["post"] for item in scored_posts]
    
    def _calculate_score(self, post: Dict, user_id: str) -> float:
        """
        حساب نتيجة المنشور
        """
        # Recency Score
        recency_score = self._calculate_recency(post["created_at"])
        
        # Engagement Score
        engagement_score = self._calculate_engagement(post)
        
        # Relevance Score
        relevance_score = self._calculate_relevance(post, user_id)
        
        # النتيجة النهائية
        total_score = (
            self.weights["recency"] * recency_score +
            self.weights["engagement"] * engagement_score +
            self.weights["relevance"] * relevance_score
        )
        
        return total_score
    
    def _calculate_recency(self, created_at: datetime) -> float:
        """
        حساب نتيجة الحداثة
        """
        hours_ago = (datetime.now() - created_at).total_seconds() / 3600
        return 1 / (1 + hours_ago)  # Decay function
    
    def _calculate_engagement(self, post: Dict) -> float:
        """
        حساب نتيجة التفاعل
        """
        likes = post.get("likes_count", 0)
        comments = post.get("comments_count", 0)
        shares = post.get("shares_count", 0)
        
        # وزن مختلف لكل نوع تفاعل
        engagement = (likes * 1) + (comments * 2) + (shares * 3)
        
        # Normalize
        return min(engagement / 100, 1.0)
    
    def _calculate_relevance(self, post: Dict, user_id: str) -> float:
        """
        حساب نتيجة الصلة بالمستخدم
        """
        # هل المستخدم يتابع الناشر؟
        is_following = self._check_following(user_id, post["author_id"])
        
        # هل للمستخدم اهتمامات مشتركة؟
        common_interests = self._get_common_interests(
            user_id,
            post["hashtags"]
        )
        
        relevance = 0.0
        if is_following:
            relevance += 0.5
        relevance += min(len(common_interests) * 0.1, 0.5)
        
        return relevance
```

---

## 🎓 مثال 6: Learning Management System (LMS)

### User Prompt

```
Build an online learning platform with:
- Course creation and management
- Video lessons with progress tracking
- Quizzes and assignments
- Discussion forums
- Live classes with video conferencing
- Certificate generation
- Payment integration for paid courses
- Student analytics dashboard
```

### Generated Features

#### Course Progress Tracking

```python
# backend/app/services/progress.py

class ProgressTracker:
    """
    تتبع تقدم الطالب
    """
    
    @staticmethod
    async def update_progress(
        user_id: str,
        course_id: str,
        lesson_id: str,
        completed: bool = True
    ):
        """
        تحديث التقدم
        """
        progress = await Progress.get_or_create(
            user_id=user_id,
            course_id=course_id
        )
        
        if completed:
            progress.completed_lessons.append(lesson_id)
        
        # حساب النسبة المئوية
        total_lessons = await Lesson.count(course_id=course_id)
        progress.percentage = (
            len(progress.completed_lessons) / total_lessons * 100
        )
        
        await progress.save()
        
        # التحقق من إكمال الدورة
        if progress.percentage == 100:
            await CertificateService.generate(user_id, course_id)
        
        return progress
```

---

## 🎮 الخلاصة

هذه الأمثلة توضح قدرة النظام على توليد مشاريع متنوعة ومعقدة. كل مثال يشمل:

- ✅ بنية معمارية كاملة
- ✅ كود جاهز للتشغيل
- ✅ اختبارات شاملة
- ✅ توثيق كامل
- ✅ إعدادات النشر

**الإصدار**: 1.0.0  
**آخر تحديث**: 2026-04-09
