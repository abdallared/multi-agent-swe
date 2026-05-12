# 📡 API Documentation - AI Software Company

## 🎯 نظرة عامة

هذا الدليل يشرح كيفية استخدام النظام كـ API Service.

---

## 🚀 Quick Start

### تشغيل API Server

```bash
# تشغيل FastAPI server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# أو باستخدام Docker
docker-compose up api
```

### Base URL

```
http://localhost:8000
```

### Authentication

```bash
# الحصول على API Key
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'

# استخدام API Key
curl -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 📋 Endpoints

### 1. Project Generation

#### POST /api/v1/projects/generate

توليد مشروع جديد من prompt

**Request:**

```json
{
  "prompt": "Build a task management app with AI prioritization",
  "options": {
    "include_tests": true,
    "include_documentation": true,
    "auto_deploy": false,
    "tech_preferences": {
      "backend": "FastAPI",
      "frontend": "React"
    }
  }
}
```

**Response:**

```json
{
  "project_id": "proj_abc123",
  "status": "processing",
  "estimated_time": "15-20 minutes",
  "webhook_url": "https://your-domain.com/webhook"
}
```

**Status Codes:**
- `202 Accepted`: Project generation started
- `400 Bad Request`: Invalid prompt or options
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

#### GET /api/v1/projects/{project_id}

الحصول على حالة المشروع

**Response:**

```json
{
  "project_id": "proj_abc123",
  "status": "completed",
  "progress": {
    "current_stage": "deployment",
    "completed_stages": [
      "planning",
      "architecture",
      "code_generation",
      "testing",
      "refactoring"
    ],
    "percentage": 100
  },
  "result": {
    "project_name": "TaskMaster AI",
    "github_url": "https://github.com/user/taskmaster-ai",
    "local_path": "/output/taskmaster_ai",
    "structure": {
      "backend": "FastAPI application",
      "frontend": "React application",
      "tests": "67 tests, 89% coverage"
    }
  },
  "metadata": {
    "created_at": "2026-04-09T10:00:00Z",
    "completed_at": "2026-04-09T10:18:32Z",
    "duration_seconds": 1112,
    "iterations": 12
  }
}
```

---

#### GET /api/v1/projects

قائمة جميع المشاريع

**Query Parameters:**
- `page` (int): رقم الصفحة (default: 1)
- `limit` (int): عدد النتائج (default: 10, max: 100)
- `status` (string): تصفية حسب الحالة (processing, completed, failed)

**Response:**

```json
{
  "projects": [
    {
      "project_id": "proj_abc123",
      "project_name": "TaskMaster AI",
      "status": "completed",
      "created_at": "2026-04-09T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "pages": 5
  }
}
```

---

#### DELETE /api/v1/projects/{project_id}

حذف مشروع

**Response:**

```json
{
  "message": "Project deleted successfully",
  "project_id": "proj_abc123"
}
```

---

### 2. Agent Operations

#### POST /api/v1/agents/planner

تشغيل Planner Agent فقط

**Request:**

```json
{
  "prompt": "Build a food delivery platform"
}
```

**Response:**

```json
{
  "project_plan": {
    "project_name": "FoodDelivery Pro",
    "features": [...],
    "user_stories": [...]
  }
}
```

---

#### POST /api/v1/agents/architect

تشغيل Architect Agent

**Request:**

```json
{
  "project_plan": {
    "project_name": "FoodDelivery Pro",
    "features": [...]
  }
}
```

**Response:**

```json
{
  "architecture": {
    "tech_stack": {...},
    "database_schema": {...},
    "modules": [...]
  }
}
```

---

### 3. Templates

#### GET /api/v1/templates

قائمة القوالب المتاحة

**Response:**

```json
{
  "templates": [
    {
      "id": "ecommerce",
      "name": "E-commerce Platform",
      "description": "Full-featured e-commerce with payments",
      "tech_stack": {
        "backend": "FastAPI",
        "frontend": "React",
        "database": "PostgreSQL"
      }
    },
    {
      "id": "saas",
      "name": "SaaS Starter",
      "description": "Multi-tenant SaaS application",
      "tech_stack": {
        "backend": "Django",
        "frontend": "Vue",
        "database": "PostgreSQL"
      }
    }
  ]
}
```

---

#### POST /api/v1/projects/from-template

إنشاء مشروع من قالب

**Request:**

```json
{
  "template_id": "ecommerce",
  "customizations": {
    "project_name": "MyShop",
    "features": ["payment_gateway", "inventory_management"]
  }
}
```

---

### 4. Webhooks

#### POST /api/v1/webhooks

تسجيل webhook للإشعارات

**Request:**

```json
{
  "url": "https://your-domain.com/webhook",
  "events": ["project.completed", "project.failed"],
  "secret": "your_webhook_secret"
}
```

**Webhook Payload:**

```json
{
  "event": "project.completed",
  "project_id": "proj_abc123",
  "timestamp": "2026-04-09T10:18:32Z",
  "data": {
    "project_name": "TaskMaster AI",
    "github_url": "https://github.com/user/taskmaster-ai"
  }
}
```

---

### 5. Analytics

#### GET /api/v1/analytics/usage

إحصائيات الاستخدام

**Response:**

```json
{
  "period": "last_30_days",
  "total_projects": 45,
  "successful_projects": 42,
  "failed_projects": 3,
  "success_rate": 93.3,
  "average_generation_time": "18 minutes",
  "most_used_tech_stacks": [
    {"name": "FastAPI + React", "count": 15},
    {"name": "Django + Vue", "count": 12}
  ]
}
```

---

## 🔐 Authentication & Authorization

### API Key Authentication

```python
# Python Example
import requests

headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8000/api/v1/projects/generate",
    headers=headers,
    json={"prompt": "Build a todo app"}
)
```

### Rate Limits

| Plan | Requests/Hour | Projects/Day |
|------|---------------|--------------|
| Free | 10 | 3 |
| Pro | 100 | 20 |
| Enterprise | Unlimited | Unlimited |

**Rate Limit Headers:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1712664000
```

---

## 📊 WebSocket API

### Real-time Project Updates

```javascript
// JavaScript Example
const ws = new WebSocket('ws://localhost:8000/ws/projects/proj_abc123');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Progress:', update.progress);
  console.log('Stage:', update.current_stage);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**Message Format:**

```json
{
  "type": "progress_update",
  "project_id": "proj_abc123",
  "progress": 45,
  "current_stage": "code_generation",
  "message": "Generating backend code...",
  "timestamp": "2026-04-09T10:15:00Z"
}
```

---

## 🛠️ SDK Examples

### Python SDK

```python
from ai_software_company import Client

# Initialize client
client = Client(api_key="YOUR_API_KEY")

# Generate project
project = client.projects.generate(
    prompt="Build a task management app",
    options={
        "include_tests": True,
        "auto_deploy": False
    }
)

# Wait for completion
project.wait_until_complete(timeout=1800)  # 30 minutes

# Get result
if project.status == "completed":
    print(f"Project URL: {project.github_url}")
    print(f"Local path: {project.local_path}")
else:
    print(f"Error: {project.error}")
```

### JavaScript SDK

```javascript
import { AICompanyClient } from '@ai-company/sdk';

// Initialize client
const client = new AICompanyClient({
  apiKey: 'YOUR_API_KEY'
});

// Generate project
const project = await client.projects.generate({
  prompt: 'Build a task management app',
  options: {
    includeTests: true,
    autoDeploy: false
  }
});

// Listen for updates
project.on('progress', (update) => {
  console.log(`Progress: ${update.progress}%`);
});

// Wait for completion
await project.waitForCompletion();

console.log('Project URL:', project.githubUrl);
```

### cURL Examples

```bash
# Generate project
curl -X POST http://localhost:8000/api/v1/projects/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Build a todo app",
    "options": {
      "include_tests": true
    }
  }'

# Check status
curl -X GET http://localhost:8000/api/v1/projects/proj_abc123 \
  -H "Authorization: Bearer YOUR_API_KEY"

# List projects
curl -X GET "http://localhost:8000/api/v1/projects?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 🔍 Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_PROMPT",
    "message": "The provided prompt is too vague",
    "details": {
      "prompt": "Build something",
      "suggestion": "Please provide more specific requirements"
    },
    "request_id": "req_xyz789"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_PROMPT` | Prompt is invalid or too vague | 400 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `PROJECT_NOT_FOUND` | Project ID doesn't exist | 404 |
| `GENERATION_FAILED` | Project generation failed | 500 |
| `AUTHENTICATION_FAILED` | Invalid API key | 401 |
| `INSUFFICIENT_CREDITS` | Not enough credits | 402 |

---

## 📈 Best Practices

### 1. Prompt Engineering

**Good Prompts:**
```
✓ "Build a task management web app with user authentication, 
   task prioritization using AI, real-time notifications, 
   and mobile-responsive design"

✓ "Create an e-commerce platform with product catalog, 
   shopping cart, payment integration (Stripe), 
   order tracking, and admin dashboard"
```

**Bad Prompts:**
```
✗ "Build something cool"
✗ "Make an app"
✗ "Website"
```

### 2. Polling vs WebSockets

**Use Polling for:**
- Simple integrations
- Infrequent status checks
- Serverless environments

**Use WebSockets for:**
- Real-time updates
- Progress monitoring
- Interactive dashboards

### 3. Error Handling

```python
import time
from ai_software_company import Client, GenerationError

client = Client(api_key="YOUR_API_KEY")

max_retries = 3
retry_delay = 5

for attempt in range(max_retries):
    try:
        project = client.projects.generate(
            prompt="Build a todo app"
        )
        break
    except GenerationError as e:
        if attempt < max_retries - 1:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(retry_delay)
        else:
            print(f"Failed after {max_retries} attempts: {e}")
            raise
```

---

## 🔒 Security

### API Key Management

```bash
# Generate new API key
curl -X POST http://localhost:8000/api/v1/auth/keys \
  -H "Authorization: Bearer YOUR_CURRENT_KEY" \
  -d '{"name": "Production Key", "expires_in": 365}'

# Revoke API key
curl -X DELETE http://localhost:8000/api/v1/auth/keys/key_abc123 \
  -H "Authorization: Bearer YOUR_CURRENT_KEY"
```

### Webhook Signature Verification

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """
    التحقق من صحة webhook
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

# Usage
@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Webhook-Signature")
    
    if not verify_webhook(payload, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook...
```

---

## 📚 Additional Resources

- [OpenAPI Specification](http://localhost:8000/docs)
- [ReDoc Documentation](http://localhost:8000/redoc)
- [Postman Collection](./postman/collection.json)
- [SDK Documentation](./docs/sdk/)

---

**الإصدار**: 1.0.0  
**آخر تحديث**: 2026-04-09
