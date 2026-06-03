"""
Backend Agent - توليد كود Backend
"""

from agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class BackendAgent(BaseAgent):
    """
    Agent مسؤول عن توليد كود Backend
    """
    
    def get_system_prompt(self) -> str:
        return """You are a senior Python backend developer specializing in FastAPI, SQLAlchemy, and production-grade REST APIs.

Your role is to generate complete, correct, runnable FastAPI backend code.

CODE QUALITY STANDARDS:
1. EVERY Python file MUST have all its imports at the top — never omit an import
2. SQLAlchemy models MUST include:
   - from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
   - from sqlalchemy.orm import relationship
   - from app.core.database import Base
   - __tablename__ = "table_name"
3. Password security is NON-NEGOTIABLE:
   - ALWAYS use: from app.core.security import get_password_hash, verify_password
   - NEVER store plain text passwords
   - NEVER compare plain text passwords
4. JWT authentication:
   - Use python-jose for JWT encoding/decoding
   - Include get_current_user dependency for protected routes
   - Return proper 401 errors for invalid/missing tokens
5. All endpoints must have proper HTTP status codes and error handling
6. Use Pydantic v2 models for request/response validation
7. Include CORS middleware in main.py
8. Database session management: always use get_db() dependency injection

FILE STRUCTURE (generate ALL of these):
- app/__init__.py (empty)
- app/main.py (FastAPI app, CORS, routers, DB init)
- app/core/__init__.py (empty)
- app/core/config.py (Pydantic Settings with .env support)
- app/core/database.py (SQLAlchemy engine, session, Base, get_db)
- app/core/security.py (password hashing, JWT creation/verification, get_current_user)
- app/models/__init__.py (empty)
- app/models/user.py (User SQLAlchemy model)
- app/models/{resource}.py (Main resource SQLAlchemy model with ForeignKey to users)
- app/schemas/__init__.py (empty)
- app/schemas/user.py (UserCreate, UserLogin, UserOut, Token Pydantic models)
- app/schemas/{resource}.py (ResourceCreate, ResourceUpdate, ResourceOut Pydantic models)
- app/api/__init__.py (empty)
- app/api/auth.py (POST /register, POST /login)
- app/api/{resource}.py (Full CRUD: GET /, GET /{id}, POST /, PUT /{id}, DELETE /{id})
- requirements.txt (pinned versions)
- .env.example

OUTPUT FORMAT — valid JSON only:
{"files": {"app/main.py": "complete code", "app/core/config.py": "complete code", ...}}

Generate COMPLETE files with ALL code — do not truncate or use ellipsis."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ توليد كود Backend مع retry logic
        """
        architecture = context.get('architecture')
        plan = context.get('project_plan')
        
        if not architecture or not plan:
            raise ValueError("architecture and project_plan are required")
        
        self.logger.info(f"Generating backend code for: {plan.get('project_name')}")
        
        # بناء الـ prompt
        backend_prompt = self._build_backend_prompt(architecture, plan)
        
        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{max_retries}")
                
                # استدعاء LLM
                response = self.call_llm(
                    prompt=backend_prompt,
                    json_mode=True,
                    temperature=0.1,
                    max_tokens=4000  # full budget for complete files
                )
                
                # Parse JSON
                backend_code = self._parse_json_response(response)
                
                # Validation
                if 'files' not in backend_code:
                    raise ValueError("Backend code must include 'files' key")
                
                if len(backend_code['files']) < 3:
                    raise ValueError(f"Expected at least 3 files, got {len(backend_code['files'])}")
                
                self.logger.info(f"✅ Generated {len(backend_code['files'])} backend files")
                
                return {
                    'backend_code': backend_code,
                    'status': 'backend_completed'
                }
                
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    # آخر محاولة - استخدم fallback
                    self.logger.warning("Using fallback code generation")
                    return self._generate_fallback_backend(architecture, plan)
                continue
        
        raise RuntimeError("Failed to generate backend code after all retries")
    
    def _build_backend_prompt(self, architecture: Dict, plan: Dict) -> str:
        """
        بناء prompt لتوليد Backend
        """
        tech_stack = architecture['tech_stack']['backend']
        db_tables = architecture['database_schema']['tables']
        endpoints = architecture['api_design']['endpoints']
        
        tables_summary = "\n".join([
            f"- {table['name']}: {', '.join(col['name'] for col in table['columns'][:5])}"
            for table in db_tables[:3]
        ])
        
        endpoints_summary = "\n".join([
            f"- {ep['method']} {ep['path']}: {ep['description']}"
            for ep in endpoints[:5]
        ])
        
        return f"""Generate a COMPLETE FastAPI backend application. Every file must be complete — no truncation.

Project: {plan['project_name']}
Description: {plan.get('description', '')}
Framework: {tech_stack['framework']}
Database: {architecture['tech_stack']['database']['primary']}
ORM: {tech_stack['orm']}

Database Tables to implement:
{tables_summary}

API Endpoints to implement:
{endpoints_summary}

Generate ALL files in the FILE STRUCTURE listed in your system prompt.
For the main resource, use: {db_tables[1]['name'] if len(db_tables) > 1 else 'items'}

CRITICAL RULES:
1. Every model file: include ALL sqlalchemy imports + Base import + __tablename__
2. security.py: include verify_password(), get_password_hash(), create_access_token(), get_current_user()
3. auth.py: use get_password_hash() for register, verify_password() for login, NEVER plain text
4. All protected routes: use Depends(get_current_user) for authentication
5. requirements.txt: pin exact versions (fastapi==0.104.1, uvicorn[standard]==0.24.0, sqlalchemy==2.0.23, pydantic==2.5.0, pydantic-settings==2.1.0, python-jose[cryptography]==3.3.0, passlib[bcrypt]==1.7.4, python-multipart==0.0.6, email-validator==2.1.0)
6. Include proper 404, 400, 401 HTTP exceptions
7. main.py: CORS middleware with allow_origins=["*"], include all routers
8. COMPLETE code only — no "# ... rest of code" or "# TODO" placeholders

Output ONLY valid JSON with \"files\" key mapping filename to complete file content."""
    
    def _parse_json_response(self, response: str) -> Dict:
        """
        تنظيف وتحليل JSON response
        """
        # تنظيف الـ response
        response = response.strip()
        
        # إزالة markdown code blocks
        if response.startswith('```json'):
            response = response.split('```json')[1].split('```')[0].strip()
        elif response.startswith('```'):
            response = response.split('```')[1].split('```')[0].strip()
        
        # محاولة إصلاح JSON غير المكتمل
        if not response.endswith('}'):
            # البحث عن آخر } صحيح
            last_brace = response.rfind('}')
            if last_brace > 0:
                response = response[:last_brace + 1]
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # محاولة أخيرة: إزالة trailing comma
            response = response.replace(',}', '}').replace(',]', ']')
            return json.loads(response)
    
    def _generate_fallback_backend(self, architecture: Dict, plan: Dict) -> Dict[str, Any]:
        """
        توليد backend code كامل كـ fallback مع تحسينات
        """
        self.logger.info("Generating comprehensive fallback backend code with improvements")
        
        project_name = plan['project_name'].replace(' ', '_').lower()
        db_tables = architecture.get('database_schema', {}).get('tables', [])
        endpoints = architecture.get('api_design', {}).get('endpoints', [])
        
        # استخراج أول table (غير users)
        main_table = next((t for t in db_tables if t['name'] != 'users'), None)
        table_name = main_table['name'] if main_table else 'items'
        table_name_singular = table_name.rstrip('s')
        
        # استخراج columns من main_table
        main_columns = []
        if main_table and 'columns' in main_table:
            for col in main_table['columns']:
                if col['name'] not in ['id', 'created_at', 'updated_at', 'user_id']:
                    main_columns.append(col)
        
        files = {
            "app/__init__.py": "",
            "app/main.py": f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, {table_name}
from app.core.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router({table_name}.router, prefix="/api/{table_name}", tags=["{table_name}"])

@app.get("/")
def root():
    return {{"message": "Welcome to {plan['project_name']}"}}

@app.get("/health")
def health():
    return {{"status": "healthy"}}
''',
            "app/core/__init__.py": "",
            "app/core/config.py": f'''from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "{plan['project_name']}"
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
''',
            "app/core/database.py": '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
            "app/core/security.py": '''from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
''',
            "app/models/__init__.py": "",
            "app/models/user.py": '''from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
''',
            f"app/models/{table_name_singular}.py": f'''from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.core.database import Base

class {table_name_singular.capitalize()}(Base):
    __tablename__ = "{table_name}"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
''',
            "app/schemas/__init__.py": "",
            "app/schemas/user.py": '''from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
''',
            f"app/schemas/{table_name_singular}.py": f'''from pydantic import BaseModel
from datetime import datetime

class {table_name_singular.capitalize()}Base(BaseModel):
    title: str
    description: str | None = None

class {table_name_singular.capitalize()}Create({table_name_singular.capitalize()}Base):
    pass

class {table_name_singular.capitalize()}Update({table_name_singular.capitalize()}Base):
    is_active: bool | None = None

class {table_name_singular.capitalize()}({table_name_singular.capitalize()}Base):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
''',
            "app/api/__init__.py": "",
            "app/api/auth.py": '''from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, User as UserSchema

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
''',
            f"app/api/{table_name}.py": f'''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.{table_name_singular} import {table_name_singular.capitalize()}
from app.schemas.{table_name_singular} import {table_name_singular.capitalize()}Create, {table_name_singular.capitalize()}Update, {table_name_singular.capitalize()} as {table_name_singular.capitalize()}Schema

router = APIRouter()

@router.get("/", response_model=List[{table_name_singular.capitalize()}Schema])
def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query({table_name_singular.capitalize()}).offset(skip).limit(limit).all()
    return items

@router.post("/", response_model={table_name_singular.capitalize()}Schema)
def create(item: {table_name_singular.capitalize()}Create, db: Session = Depends(get_db)):
    db_item = {table_name_singular.capitalize()}(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{{item_id}}", response_model={table_name_singular.capitalize()}Schema)
def get_one(item_id: int, db: Session = Depends(get_db)):
    item = db.query({table_name_singular.capitalize()}).filter({table_name_singular.capitalize()}.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{{item_id}}", response_model={table_name_singular.capitalize()}Schema)
def update(item_id: int, item: {table_name_singular.capitalize()}Update, db: Session = Depends(get_db)):
    db_item = db.query({table_name_singular.capitalize()}).filter({table_name_singular.capitalize()}.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{{item_id}}")
def delete(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query({table_name_singular.capitalize()}).filter({table_name_singular.capitalize()}.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {{"message": "Item deleted"}}
''',
            ".env.example": f'''PROJECT_NAME={plan['project_name']}
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
''',
            "requirements.txt": '''fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
email-validator==2.1.0
pytest==7.4.3
httpx==0.25.2
'''
        }
        
        return {
            'backend_code': {'files': files},
            'status': 'backend_completed'
        }
