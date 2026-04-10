# 🚀 دليل النشر والتشغيل - AI Software Company

## 📋 نظرة عامة

هذا الدليل يشرح كيفية نشر وتشغيل النظام في بيئات مختلفة.

---

## 🏠 التشغيل المحلي (Local Development)

### 1. الإعداد الأولي

```bash
# Clone المشروع
git clone https://github.com/yourusername/ai-software-company.git
cd ai-software-company

# إنشاء البيئة الافتراضية
python -m venv venv

# تفعيل البيئة
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# تثبيت Dependencies
pip install -r requirements.txt
```

### 2. إعداد قواعد البيانات

```bash
# PostgreSQL
# إنشاء قاعدة بيانات
createdb ai_software_company

# تشغيل Migrations
alembic upgrade head

# Redis (باستخدام Docker)
docker run -d -p 6379:6379 redis:latest

# ChromaDB (يعمل تلقائياً)
# سيتم إنشاء المجلد ./data/chroma تلقائياً
```

### 3. إعداد Environment Variables

```bash
# نسخ .env.example
cp .env.example .env

# تعديل .env
nano .env
```

```env
# .env
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GITHUB_TOKEN=ghp_your-token-here
GITHUB_USERNAME=yourusername

DATABASE_URL=postgresql://user:password@localhost:5432/ai_software_company
REDIS_URL=redis://localhost:6379/0
CHROMA_PERSIST_DIR=./data/chroma

DEFAULT_LLM=openai
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_TOKENS=4000
MAX_ITERATIONS=50

LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
OUTPUT_DIR=./output
```

### 4. تشغيل النظام

```bash
# تشغيل مباشر
python main.py

# أو باستخدام CLI
python -m ai_software_company.cli generate "Build a todo app"
```

---

## 🐳 النشر باستخدام Docker

### 1. Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/chroma output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port (if needed for API)
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    container_name: ai_software_company
    env_file:
      - .env
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - postgres
      - redis
    networks:
      - ai_network

  postgres:
    image: postgres:15-alpine
    container_name: ai_postgres
    environment:
      POSTGRES_DB: ai_software_company
      POSTGRES_USER: aiuser
      POSTGRES_PASSWORD: aipassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - ai_network

  redis:
    image: redis:7-alpine
    container_name: ai_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ai_network

  # Optional: Web Dashboard
  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    container_name: ai_dashboard
    ports:
      - "3000:3000"
    depends_on:
      - app
    networks:
      - ai_network

volumes:
  postgres_data:
  redis_data:

networks:
  ai_network:
    driver: bridge
```

### 3. تشغيل Docker

```bash
# Build الصور
docker-compose build

# تشغيل الخدمات
docker-compose up -d

# مشاهدة الـ logs
docker-compose logs -f app

# إيقاف الخدمات
docker-compose down

# إيقاف مع حذف البيانات
docker-compose down -v
```

---

## ☁️ النشر على السحابة

### 1. AWS Deployment

#### A. استخدام EC2

```bash
# 1. إنشاء EC2 Instance
# - AMI: Ubuntu 22.04
# - Instance Type: t3.medium (2 vCPU, 4GB RAM)
# - Storage: 30GB

# 2. الاتصال بالـ Instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 5. Clone المشروع
git clone https://github.com/yourusername/ai-software-company.git
cd ai-software-company

# 6. إعداد .env
nano .env

# 7. تشغيل
docker-compose up -d
```

#### B. استخدام ECS (Elastic Container Service)

```yaml
# ecs-task-definition.json
{
  "family": "ai-software-company",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "your-ecr-repo/ai-software-company:latest",
      "essential": true,
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-software-company",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

```bash
# Deploy إلى ECS
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
aws ecs create-service --cluster your-cluster --service-name ai-software-company --task-definition ai-software-company --desired-count 1
```

### 2. Google Cloud Platform (GCP)

#### استخدام Cloud Run

```bash
# 1. تثبيت gcloud CLI
curl https://sdk.cloud.google.com | bash

# 2. تسجيل الدخول
gcloud auth login

# 3. إعداد المشروع
gcloud config set project your-project-id

# 4. Build الصورة
gcloud builds submit --tag gcr.io/your-project-id/ai-software-company

# 5. Deploy إلى Cloud Run
gcloud run deploy ai-software-company \
  --image gcr.io/your-project-id/ai-software-company \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key \
  --memory 2Gi \
  --cpu 2
```

### 3. Azure Deployment

#### استخدام Azure Container Instances

```bash
# 1. تسجيل الدخول
az login

# 2. إنشاء Resource Group
az group create --name ai-software-company-rg --location eastus

# 3. إنشاء Container Registry
az acr create --resource-group ai-software-company-rg --name aicompanyregistry --sku Basic

# 4. Build ورفع الصورة
az acr build --registry aicompanyregistry --image ai-software-company:latest .

# 5. Deploy Container
az container create \
  --resource-group ai-software-company-rg \
  --name ai-software-company \
  --image aicompanyregistry.azurecr.io/ai-software-company:latest \
  --cpu 2 \
  --memory 4 \
  --environment-variables \
    OPENAI_API_KEY=your-key \
    DATABASE_URL=postgresql://...
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          yourusername/ai-software-company:latest
          yourusername/ai-software-company:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /app/ai-software-company
          docker-compose pull
          docker-compose up -d
          docker-compose logs -f
```

---

## 📊 Monitoring & Logging

### 1. Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - ai_network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - ai_network

volumes:
  prometheus_data:
  grafana_data:
```

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-software-company'
    static_configs:
      - targets: ['app:8000']
```

### 2. ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# docker-compose.elk.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - ai_network

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: logstash
    volumes:
      - ./monitoring/logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch
    networks:
      - ai_network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - ai_network

volumes:
  elasticsearch_data:
```

### 3. Application Metrics

```python
# utils/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
agent_executions = Counter(
    'agent_executions_total',
    'Total number of agent executions',
    ['agent_name', 'status']
)

agent_duration = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration',
    ['agent_name']
)

active_projects = Gauge(
    'active_projects',
    'Number of active projects'
)

llm_api_calls = Counter(
    'llm_api_calls_total',
    'Total LLM API calls',
    ['provider', 'model']
)

class MetricsCollector:
    @staticmethod
    def track_agent_execution(agent_name: str):
        """
        Decorator لتتبع تنفيذ Agent
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    agent_executions.labels(
                        agent_name=agent_name,
                        status='success'
                    ).inc()
                    return result
                except Exception as e:
                    agent_executions.labels(
                        agent_name=agent_name,
                        status='failed'
                    ).inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    agent_duration.labels(agent_name=agent_name).observe(duration)
            
            return wrapper
        return decorator

# استخدام
class PlannerAgent(BaseAgent):
    @MetricsCollector.track_agent_execution('planner')
    def execute(self, context):
        # ... implementation
        pass
```

---

## 🔒 Security Best Practices

### 1. Secrets Management

```bash
# استخدام AWS Secrets Manager
aws secretsmanager create-secret \
  --name ai-software-company/openai-key \
  --secret-string "sk-your-key-here"

# استخدام HashiCorp Vault
vault kv put secret/ai-software-company \
  openai_key="sk-your-key-here" \
  github_token="ghp-your-token-here"
```

```python
# utils/secrets.py

import boto3
from botocore.exceptions import ClientError

class SecretsManager:
    def __init__(self, region_name='us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region_name)
    
    def get_secret(self, secret_name: str) -> dict:
        """
        استرجاع Secret من AWS Secrets Manager
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except ClientError as e:
            raise Exception(f"Failed to retrieve secret: {e}")

# استخدام
secrets = SecretsManager()
openai_key = secrets.get_secret('ai-software-company/openai-key')
```

### 2. Network Security

```yaml
# docker-compose.secure.yml
version: '3.8'

services:
  app:
    # ... other config
    networks:
      - internal
      - external
    # لا تعرض ports مباشرة

  nginx:
    image: nginx:alpine
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - external

networks:
  internal:
    driver: bridge
    internal: true
  external:
    driver: bridge
```

### 3. Rate Limiting

```python
# utils/rate_limiter.py

from redis import Redis
import time

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def check_rate_limit(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 3600
    ) -> bool:
        """
        التحقق من Rate Limit
        """
        current = self.redis.get(key)
        
        if current is None:
            self.redis.setex(key, window_seconds, 1)
            return True
        
        if int(current) >= max_requests:
            return False
        
        self.redis.incr(key)
        return True

# استخدام
rate_limiter = RateLimiter(redis_client)

if not rate_limiter.check_rate_limit(f"user:{user_id}:api_calls"):
    raise Exception("Rate limit exceeded")
```

---

## 🔧 Troubleshooting

### مشاكل شائعة وحلولها

#### 1. Out of Memory

```yaml
# زيادة Memory في Docker
services:
  app:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

#### 2. Slow LLM Responses

```python
# استخدام Caching
from functools import lru_cache
import hashlib

class CachedLLM:
    def __init__(self, llm):
        self.llm = llm
        self.cache = {}
    
    def generate(self, prompt: str, **kwargs):
        cache_key = hashlib.md5(
            f"{prompt}{kwargs}".encode()
        ).hexdigest()
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        response = self.llm.generate(prompt, **kwargs)
        self.cache[cache_key] = response
        return response
```

#### 3. Database Connection Issues

```python
# Connection Pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # التحقق من الاتصال قبل الاستخدام
    pool_recycle=3600    # إعادة تدوير الاتصالات كل ساعة
)
```

---

## 📈 Scaling Strategies

### 1. Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  app:
    # ... config
    deploy:
      replicas: 3
      
  nginx:
    # Load balancer config
    volumes:
      - ./nginx/load-balancer.conf:/etc/nginx/nginx.conf
```

```nginx
# nginx/load-balancer.conf
upstream app_servers {
    least_conn;
    server app_1:8000;
    server app_2:8000;
    server app_3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Queue-based Processing

```python
# utils/task_queue.py

from celery import Celery
from kombu import Queue

app = Celery('ai_software_company')

app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_queues=(
        Queue('high_priority', routing_key='high'),
        Queue('normal', routing_key='normal'),
        Queue('low_priority', routing_key='low'),
    )
)

@app.task(queue='high_priority')
def generate_project(user_prompt: str):
    """
    مهمة توليد مشروع (async)
    """
    cto = AICTO(llm, memory)
    result = cto.execute_workflow(user_prompt)
    return result
```

---

## 🎯 Performance Optimization

### 1. Caching Strategy

```python
# Multi-level caching
class CacheManager:
    def __init__(self):
        self.memory_cache = {}  # L1: In-memory
        self.redis_cache = Redis()  # L2: Redis
    
    def get(self, key: str):
        # L1 Cache
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # L2 Cache
        value = self.redis_cache.get(key)
        if value:
            self.memory_cache[key] = value
            return value
        
        return None
    
    def set(self, key: str, value, ttl: int = 3600):
        self.memory_cache[key] = value
        self.redis_cache.setex(key, ttl, value)
```

### 2. Database Optimization

```python
# Batch operations
class BatchProcessor:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.batch = []
    
    def add(self, item):
        self.batch.append(item)
        
        if len(self.batch) >= self.batch_size:
            self.flush()
    
    def flush(self):
        if self.batch:
            db.bulk_insert(self.batch)
            self.batch = []
```

---

**الإصدار**: 1.0.0  
**آخر تحديث**: 2026-04-09
