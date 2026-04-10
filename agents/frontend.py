"""
Frontend Agent - توليد كود Frontend
"""

from agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class FrontendAgent(BaseAgent):
    """
    Agent مسؤول عن توليد كود Frontend
    """
    
    def get_system_prompt(self) -> str:
        return """You are an expert frontend developer specializing in React and modern web development.

Your role is to generate production-ready frontend code.

You must output valid JSON with this structure:
{
    "files": {
        "src/App.tsx": "// React App component...",
        "src/pages/Home.tsx": "// Home page...",
        "src/services/api.ts": "// API service...",
        "package.json": "{ dependencies... }"
    }
}

Generate clean, modern, responsive code following React best practices."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ توليد كود Frontend مع retry logic
        """
        architecture = context.get('architecture')
        plan = context.get('project_plan')
        
        if not architecture or not plan:
            raise ValueError("architecture and project_plan are required")
        
        self.logger.info(f"Generating frontend code for: {plan.get('project_name')}")
        
        # بناء الـ prompt
        frontend_prompt = self._build_frontend_prompt(architecture, plan)
        
        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{max_retries}")
                
                # استدعاء LLM
                response = self.call_llm(
                    prompt=frontend_prompt,
                    json_mode=True,
                    temperature=0.1,
                    max_tokens=1800
                )
                
                # Parse JSON
                frontend_code = self._parse_json_response(response)
                
                # Validation
                if 'files' not in frontend_code:
                    raise ValueError("Frontend code must include 'files' key")
                
                if len(frontend_code['files']) < 3:
                    raise ValueError(f"Expected at least 3 files, got {len(frontend_code['files'])}")
                
                self.logger.info(f"✅ Generated {len(frontend_code['files'])} frontend files")
                
                return {
                    'frontend_code': frontend_code,
                    'status': 'frontend_completed'
                }
                
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    self.logger.warning("Using fallback code generation")
                    return self._generate_fallback_frontend(architecture, plan)
                continue
        
        raise RuntimeError("Failed to generate frontend code after all retries")
    
    def _parse_json_response(self, response: str) -> Dict:
        """
        تنظيف وتحليل JSON response
        """
        response = response.strip()
        
        if response.startswith('```json'):
            response = response.split('```json')[1].split('```')[0].strip()
        elif response.startswith('```'):
            response = response.split('```')[1].split('```')[0].strip()
        
        if not response.endswith('}'):
            last_brace = response.rfind('}')
            if last_brace > 0:
                response = response[:last_brace + 1]
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            response = response.replace(',}', '}').replace(',]', ']')
            return json.loads(response)
    
    def _build_frontend_prompt(self, architecture: Dict, plan: Dict) -> str:
        """
        بناء prompt لتوليد Frontend
        """
        tech_stack = architecture['tech_stack']['frontend']
        features = plan['features'][:3]
        
        features_summary = "\n".join([
            f"- {f['name']}: {f.get('description', 'N/A')}"
            for f in features
        ])
        
        return f"""Generate a complete React frontend application.

Project: {plan['project_name']}
Framework: {tech_stack['framework']}
Language: {tech_stack['language']}

Key Features:
{features_summary}

Generate these essential files (keep each file under 40 lines):
1. src/App.tsx - Main React component with routing
2. src/pages/Home.tsx - Home page component
3. src/pages/Login.tsx - Login page component
4. src/services/api.ts - API service for backend calls
5. package.json - NPM dependencies

Requirements:
- Use TypeScript
- Use React Router for navigation
- Use Axios for API calls
- Keep code VERY concise (max 40 lines per file)
- Modern React with hooks
- Responsive design with Tailwind CSS
- No complex state management
- Focus on core functionality only

Output ONLY valid JSON with "files" key. Keep total response under 1500 tokens."""
    
    def _generate_fallback_frontend(self, architecture: Dict, plan: Dict) -> Dict[str, Any]:
        """
        توليد frontend code كامل كـ fallback
        """
        self.logger.info("Generating comprehensive fallback frontend code")
        
        project_name = plan['project_name']
        features = plan.get('features', [])
        
        # استخراج اسم الـ resource الرئيسي من الـ features
        resource = 'items'
        resource_singular = 'item'
        for f in features:
            name = f.get('name', '').lower()
            if 'task' in name or 'todo' in name:
                resource, resource_singular = 'tasks', 'task'
                break
            elif 'post' in name or 'blog' in name:
                resource, resource_singular = 'posts', 'post'
                break
            elif 'product' in name:
                resource, resource_singular = 'products', 'product'
                break
            elif 'note' in name:
                resource, resource_singular = 'notes', 'note'
                break
        
        Resource = resource_singular.capitalize()
        
        files = {
            "src/App.tsx": f'''import React from 'react';
import {{ BrowserRouter, Routes, Route, Navigate }} from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Navbar from './components/Navbar';

function App() {{
  const isAuthenticated = !!localStorage.getItem('token');
  
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={{<Home />}} />
          <Route path="/login" element={{<Login />}} />
          <Route path="/register" element={{<Register />}} />
          <Route path="/dashboard" element={{isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}}

export default App;
''',
            "src/main.tsx": '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
''',
            "src/index.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;
''',
            "src/components/Navbar.tsx": f'''import React from 'react';
import {{ Link, useNavigate }} from 'react-router-dom';

const Navbar: React.FC = () => {{
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem('token');

  const handleLogout = () => {{
    localStorage.removeItem('token');
    navigate('/login');
  }};

  return (
    <nav className="bg-blue-600 text-white px-6 py-4 flex justify-between items-center shadow">
      <Link to="/" className="text-xl font-bold">{project_name}</Link>
      <div className="flex gap-4">
        {{isAuthenticated ? (
          <>
            <Link to="/dashboard" className="hover:underline">Dashboard</Link>
            <button onClick={{handleLogout}} className="hover:underline">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" className="hover:underline">Login</Link>
            <Link to="/register" className="hover:underline">Register</Link>
          </>
        )}}
      </div>
    </nav>
  );
}};

export default Navbar;
''',
            "src/pages/Home.tsx": f'''import React from 'react';
import {{ Link }} from 'react-router-dom';

const Home: React.FC = () => (
  <div className="container mx-auto px-4 py-16 text-center">
    <h1 className="text-5xl font-bold mb-6 text-gray-800">{project_name}</h1>
    <p className="text-xl text-gray-600 mb-8">Manage your {resource} efficiently</p>
    <div className="flex gap-4 justify-center">
      <Link to="/register" className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium">
        Get Started
      </Link>
      <Link to="/login" className="border border-blue-600 text-blue-600 px-6 py-3 rounded-lg hover:bg-blue-50 font-medium">
        Login
      </Link>
    </div>
  </div>
);

export default Home;
''',
            "src/pages/Login.tsx": '''import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const response = await api.login(username, password);
      localStorage.setItem('token', response.access_token);
      navigate('/dashboard');
    } catch {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-md">
      <h1 className="text-3xl font-bold mb-6 text-center">Login</h1>
      {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow space-y-4">
        <input type="text" placeholder="Username" value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
        <input type="password" placeholder="Password" value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium">
          Login
        </button>
        <p className="text-center text-gray-600">
          No account? <Link to="/register" className="text-blue-600 hover:underline">Register</Link>
        </p>
      </form>
    </div>
  );
};

export default Login;
''',
            "src/pages/Register.tsx": '''import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

const Register: React.FC = () => {
  const [form, setForm] = useState({ email: '', username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.register(form.email, form.username, form.password);
      navigate('/login');
    } catch {
      setError('Registration failed. Try a different username or email.');
    }
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-md">
      <h1 className="text-3xl font-bold mb-6 text-center">Register</h1>
      {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow space-y-4">
        {(['email', 'username', 'password'] as const).map((field) => (
          <input key={field} type={field === 'password' ? 'password' : 'text'}
            placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
            value={form[field]} onChange={(e) => setForm({ ...form, [field]: e.target.value })}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
        ))}
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium">
          Register
        </button>
        <p className="text-center text-gray-600">
          Have an account? <Link to="/login" className="text-blue-600 hover:underline">Login</Link>
        </p>
      </form>
    </div>
  );
};

export default Register;
''',
            f"src/pages/Dashboard.tsx": f'''import React, {{ useState, useEffect }} from 'react';
import {{ api }} from '../services/api';

interface {Resource} {{
  id: number;
  title: string;
  description?: string;
  is_active: boolean;
}}

const Dashboard: React.FC = () => {{
  const [{resource}, set{Resource}s] = useState<{Resource}[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {{
    api.get{Resource}s().then(set{Resource}s).finally(() => setLoading(false));
  }}, []);

  const handleCreate = async (e: React.FormEvent) => {{
    e.preventDefault();
    const newItem = await api.create{Resource}({{ title, description }});
    set{Resource}s(prev => [...prev, newItem]);
    setTitle('');
    setDescription('');
  }};

  const handleDelete = async (id: number) => {{
    await api.delete{Resource}(id);
    set{Resource}s(prev => prev.filter(item => item.id !== id));
  }};

  if (loading) return <div className="text-center py-12">Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">My {Resource}s</h1>
      <form onSubmit={{handleCreate}} className="bg-white p-6 rounded-lg shadow mb-6 space-y-3">
        <input type="text" placeholder="{Resource} title" value={{title}}
          onChange={{(e) => setTitle(e.target.value)}}
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required />
        <input type="text" placeholder="Description (optional)" value={{description}}
          onChange={{(e) => setDescription(e.target.value)}}
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
          Add {Resource}
        </button>
      </form>
      <div className="space-y-3">
        {{{resource}.map(item => (
          <div key={{item.id}} className="bg-white p-4 rounded-lg shadow flex justify-between items-center">
            <div>
              <h3 className="font-medium text-gray-800">{{item.title}}</h3>
              {{item.description && <p className="text-sm text-gray-500">{{item.description}}</p>}}
            </div>
            <button onClick={{() => handleDelete(item.id)}}
              className="text-red-500 hover:text-red-700 font-medium text-sm">
              Delete
            </button>
          </div>
        ))}}
        {{!{resource}.length && <p className="text-center text-gray-500 py-8">No {resource} yet. Create one above!</p>}}
      </div>
    </div>
  );
}};

export default Dashboard;
''',
            "src/services/api.ts": f'''import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const http = axios.create({{ baseURL: API_BASE_URL }});

http.interceptors.request.use((config) => {{
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${{token}}`;
  return config;
}});

export const api = {{
  login: async (username: string, password: string) =>
    (await http.post('/auth/login', {{ username, password }})).data,

  register: async (email: string, username: string, password: string) =>
    (await http.post('/auth/register', {{ email, username, password }})).data,

  get{Resource}s: async () =>
    (await http.get('/{resource}/')).data,

  create{Resource}: async (data: {{ title: string; description?: string }}) =>
    (await http.post('/{resource}/', data)).data,

  update{Resource}: async (id: number, data: object) =>
    (await http.put(`/{resource}/${{id}}`, data)).data,

  delete{Resource}: async (id: number) =>
    (await http.delete(`/{resource}/${{id}}`)).data,
}};
''',
            "src/types/index.ts": f'''export interface User {{
  id: number;
  email: string;
  username: string;
  is_active: boolean;
}}

export interface {Resource} {{
  id: number;
  title: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}}

export interface AuthToken {{
  access_token: string;
  token_type: string;
}}
''',
            "index.html": f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''',
            "package.json": f'''{{"name": "frontend", "version": "1.0.0", "private": true,
  "dependencies": {{
    "react": "^18.2.0", "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0", "axios": "^1.6.2"
  }},
  "devDependencies": {{
    "@types/react": "^18.2.42", "@types/react-dom": "^18.2.17",
    "typescript": "^5.3.3", "tailwindcss": "^3.3.6",
    "vite": "^5.0.7", "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16", "postcss": "^8.4.32"
  }},
  "scripts": {{"dev": "vite", "build": "vite build", "preview": "vite preview"}}
}}
''',
            "vite.config.ts": '''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { port: 3000 }
});
''',
            "tailwind.config.js": '''/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
''',
            "postcss.config.js": '''export default {
  plugins: { tailwindcss: {}, autoprefixer: {} }
};
''',
            "tsconfig.json": '''{"compilerOptions": {"target": "ES2020", "useDefineForClassFields": true,
  "lib": ["ES2020", "DOM", "DOM.Iterable"], "module": "ESNext",
  "skipLibCheck": true, "moduleResolution": "bundler",
  "allowImportingTsExtensions": true, "resolveJsonModule": true,
  "isolatedModules": true, "noEmit": true, "jsx": "react-jsx",
  "strict": true}, "include": ["src"]}
''',
            ".env.example": '''VITE_API_URL=http://localhost:8000/api
'''
        }
        
        return {
            'frontend_code': {'files': files},
            'status': 'frontend_completed'
        }
