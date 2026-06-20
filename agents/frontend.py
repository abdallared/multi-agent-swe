"""
Frontend Agent - توليد كود Frontend
"""

from agents.base_agent import BaseAgent
from typing import Dict, Any
from utils.code_validator import CodeValidator
import json
import logging

logger = logging.getLogger(__name__)


class FrontendAgent(BaseAgent):
    """
    Agent مسؤول عن توليد كود Frontend
    """
    
    def get_system_prompt(self) -> str:
        return """You are a senior frontend engineer specializing in React 18, TypeScript, and modern UI/UX design.

Your role is to generate complete, beautiful, production-ready React frontend code.

UI DESIGN STANDARDS (non-negotiable — the UI must look premium and professional):
1. Color palette: Use rich, modern colors (e.g., indigo-600, violet-600, slate-800 — not plain blue)
2. Backgrounds: Use gradient backgrounds (e.g., bg-gradient-to-br from-slate-900 to-indigo-900 for dark sections)
3. Cards: White cards with shadows and hover lift (shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all)
4. Typography: Large bold headings (text-4xl font-bold tracking-tight), proper hierarchy
5. Buttons: Gradient buttons (bg-gradient-to-r from-indigo-600 to-violet-600), rounded-xl, with hover states
6. Forms: Clean inputs with focus rings (focus:ring-2 focus:ring-indigo-500), proper labels
7. Loading states: Animated spinner (animate-spin), skeleton screens
8. Empty states: Friendly illustration/emoji + descriptive text
9. Animations: Use transition-all duration-200, hover:-translate-y-1, animate-fade-in
10. Responsive: Mobile-first, container mx-auto, proper breakpoints (sm:, md:, lg:)

CODE QUALITY STANDARDS:
1. ALWAYS use: const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
2. MUST include all build config: package.json, vite.config.ts, tsconfig.json, tsconfig.node.json, index.html, main.tsx
3. Use TypeScript with explicit interfaces for ALL data types
4. Use React Router v6 (Routes, Route, Navigate, Link, useNavigate)
5. JWT stored in localStorage, sent as Bearer token in Axios interceptors
6. Use Axios with request interceptors for auth headers
7. Error states: show user-friendly error messages in colored alert boxes
8. All forms: loading state on submit button, disable while loading
9. FastAPI returns JWT token under `response.data.access_token` (not `token`). Always save it as `access_token` from the login/register response.
10. Do NOT evaluate authentication status statically in `App.tsx` component body (e.g., `const isAuthenticated = ...`). Instead, use dynamic route guards/wrappers (like `<ProtectedRoute>` and `<PublicRoute>` helper components) that dynamically retrieve `localStorage.getItem('token')` inside their render function to ensure route protection updates reactively upon login or logout without a page refresh.
11. Navbar.tsx must subscribe to route updates by calling `useLocation()` from `react-router-dom` to ensure navigation dynamically updates the displayed links. Use `useNavigate()` to perform programmatically driven logouts.
12. To prevent "state updates on unmounted components" warnings, do NOT call `setLoading(false)` inside `finally` blocks for API requests that trigger a redirect (e.g., login or registration). Only call `setLoading(false)` in the `catch` block.
13. Match all interface property names to the snake_case properties returned by the SQLAlchemy/FastAPI backend (e.g. use `workspace_id` instead of `workspaceId`).
14. Implement real CRUD logic in pages. Do not use setTimeout simulation wrappers or mock arrays for CRUD endpoints if they are specified in the backend design.

FILE STRUCTURE (generate ALL of these):
- src/main.tsx
- src/App.tsx (routing with auth guard)
- src/index.css (@tailwind directives)
- src/types/index.ts (TypeScript interfaces)
- src/services/api.ts (Axios client with interceptors + all API calls)
- src/components/Navbar.tsx (responsive navigation)
- src/components/LoadingSpinner.tsx (reusable spinner)
- src/pages/Home.tsx (hero section with features, gradient bg, CTA buttons)
- src/pages/Login.tsx (clean form, error display)
- src/pages/Register.tsx (clean form, error display)
- src/pages/Dashboard.tsx (full CRUD UI with cards)
- index.html
- package.json (with dev/build/preview scripts)
- vite.config.ts
- tsconfig.json
- tsconfig.node.json
- tailwind.config.js
- postcss.config.js
- .env.example

OUTPUT FORMAT — valid JSON only:
{"files": {"src/App.tsx": "complete code", ...}}

Generate COMPLETE files — never truncate. The UI must look beautiful and professional."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ توليد كود Frontend مع retry logic + code validation
        """
        architecture = context.get('architecture')
        plan = context.get('project_plan')
        
        if not architecture or not plan:
            raise ValueError("architecture and project_plan are required")
        
        self.logger.info(f"Generating frontend code for: {plan.get('project_name')}")
        
        # بناء الـ prompt
        frontend_prompt = self._build_frontend_prompt(architecture, plan)
        validator = CodeValidator()
        
        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{max_retries}")
                
                # استدعاء LLM
                response = self.call_llm(
                    prompt=frontend_prompt,
                    json_mode=True,
                    temperature=0.2,
                    max_tokens=4000
                )
                
                # Parse JSON
                frontend_code = self._parse_json_response(response)
                
                # Basic validation
                if 'files' not in frontend_code:
                    raise ValueError("Frontend code must include 'files' key")
                
                if len(frontend_code['files']) < 3:
                    raise ValueError(f"Expected at least 3 files, got {len(frontend_code['files'])}")
                
                # ── Frontend Code Validation ─────────────────────
                report = validator.validate_frontend_files(frontend_code['files'])
                
                if report.warning_count > 0:
                    self.logger.warning(f"Frontend validation warnings: {report.summary()}")
                
                self.logger.info(f"✅ Generated {len(frontend_code['files'])} frontend files")
                
                return {
                    'frontend_code': frontend_code,
                    'status': 'frontend_completed',
                    'validation': report.summary(),
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
        
        return f"""Generate a COMPLETE, beautiful React + TypeScript frontend application.

Project: {plan['project_name']}
Description: {plan.get('description', '')}
Framework: {tech_stack['framework']}
Language: {tech_stack['language']}
Styling: Tailwind CSS

Key Features to implement UI for:
{features_summary}

Generate ALL files in the FILE STRUCTURE listed in your system prompt.

DESIGN REQUIREMENTS (mandatory):
- Home page: Gradient hero section (from-slate-900 to-indigo-900), large white heading, subtext in gray-300, two CTA buttons (gradient primary + outline secondary), feature cards section with icons
- Navbar: Glass effect or white with shadow, project name on left, nav links on right, conditional auth buttons
- Dashboard: Clean white card layout, creation form at top, item cards with hover lift, empty state with emoji + description, status badges
- Login/Register: Centered card, clean form inputs with focus rings, gradient submit button, link to other auth page
- Colors: Use indigo/violet palette (indigo-600, violet-600) not plain blue
- Buttons: bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700

API REQUIREMENTS:
- api.ts: const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
- Axios interceptors for Bearer token auth
- Typed response interfaces
- Methods: login, register, get{features[0]['name'].replace(' ', '') if features else 'Items'}s, create, update, delete

Output ONLY valid JSON with \"files\" key mapping filename to complete file content.

IMPORTANT: Generate COMPLETE code — do not truncate or abbreviate any file."""
    
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

const ProtectedRoute = ({{ children }}: {{ children: React.ReactNode }}) => {{
  const token = localStorage.getItem('token');
  return token ? <>{{children}}</> : <Navigate to="/login" replace />;
}};

const PublicRoute = ({{ children }}: {{ children: React.ReactNode }}) => {{
  const token = localStorage.getItem('token');
  return !token ? <>{{children}}</> : <Navigate to="/dashboard" replace />;
}};

function App() {{
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={{<PublicRoute><Home /></PublicRoute>}} />
          <Route path="/login" element={{<PublicRoute><Login /></PublicRoute>}} />
          <Route path="/register" element={{<PublicRoute><Register /></PublicRoute>}} />
          <Route path="/dashboard" element={{<ProtectedRoute><Dashboard /></ProtectedRoute>}} />
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
import {{ Link, useNavigate, useLocation }} from 'react-router-dom';

const Navbar: React.FC = () => {{
  const navigate = useNavigate();
  const location = useLocation();
  const isAuthenticated = !!localStorage.getItem('token');

  const handleLogout = () => {{
    localStorage.removeItem('token');
    navigate('/login');
  }};

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-blue-600 hover:text-blue-700 transition">
          {project_name}
        </Link>
        <div className="flex gap-6 items-center">
          {{isAuthenticated ? (
            <>
              <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 font-medium transition">
                Dashboard
              </Link>
              <button onClick={{handleLogout}} 
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-blue-600 font-medium transition">
                Login
              </Link>
              <Link to="/register" 
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition shadow-sm">
                Sign Up
              </Link>
            </>
          )}}
        </div>
      </div>
    </nav>
  );
}};

export default Navbar;
''',
            "src/pages/Home.tsx": f'''import React from 'react';
import {{ Link }} from 'react-router-dom';

const Home: React.FC = () => (
  <div className="min-h-[80vh] flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div className="container mx-auto px-4 py-16 text-center">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-6xl font-bold mb-6 text-gray-900 tracking-tight">{project_name}</h1>
        <p className="text-xl text-gray-600 mb-10 leading-relaxed">
          Manage your {resource} efficiently with our modern, intuitive platform
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link to="/register" 
            className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 font-semibold text-lg shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5">
            Get Started Free
          </Link>
          <Link to="/login" 
            className="bg-white border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-lg hover:bg-blue-50 font-semibold text-lg shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5">
            Sign In
          </Link>
        </div>
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-blue-600 text-3xl mb-3">⚡</div>
            <h3 className="font-semibold text-gray-800 mb-2">Fast & Efficient</h3>
            <p className="text-gray-600 text-sm">Lightning-fast performance for all your needs</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-blue-600 text-3xl mb-3">🔒</div>
            <h3 className="font-semibold text-gray-800 mb-2">Secure & Private</h3>
            <p className="text-gray-600 text-sm">Your data is protected with industry-standard security</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-blue-600 text-3xl mb-3">📱</div>
            <h3 className="font-semibold text-gray-800 mb-2">Responsive Design</h3>
            <p className="text-gray-600 text-sm">Works seamlessly on all devices</p>
          </div>
        </div>
      </div>
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
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await api.login(username, password);
      localStorage.setItem('token', response.access_token);
      navigate('/dashboard');
    } catch {
      setError('Invalid username or password');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Welcome Back</h1>
          <p className="text-gray-600">Sign in to your account</p>
        </div>
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-lg space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Enter your username" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Enter your password" required />
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold text-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="text-center text-gray-600 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-600 hover:text-blue-700 font-semibold hover:underline">
            Create one
          </Link>
        </p>
      </div>
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
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.register(form.email, form.username, form.password);
      navigate('/login');
    } catch {
      setError('Registration failed. Username or email may already be taken.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Create Account</h1>
          <p className="text-gray-600">Join us today</p>
        </div>
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-lg space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input type="email" value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="your@email.com" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
            <input type="text" value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Choose a username" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input type="password" value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Create a strong password" required />
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold text-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="text-center text-gray-600 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 hover:text-blue-700 font-semibold hover:underline">
            Sign in
          </Link>
        </p>
      </div>
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
  const [creating, setCreating] = useState(false);

  useEffect(() => {{
    api.get{Resource}s().then(set{Resource}s).finally(() => setLoading(false));
  }}, []);

  const handleCreate = async (e: React.FormEvent) => {{
    e.preventDefault();
    setCreating(true);
    try {{
      const newItem = await api.create{Resource}({{ title, description }});
      set{Resource}s(prev => [...prev, newItem]);
      setTitle('');
      setDescription('');
    }} finally {{
      setCreating(false);
    }}
  }};

  const handleDelete = async (id: number) => {{
    if (!confirm('Are you sure you want to delete this item?')) return;
    await api.delete{Resource}(id);
    set{Resource}s(prev => prev.filter(item => item.id !== id));
  }};

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">My {Resource}s</h1>
        <p className="text-gray-600">Manage and organize your {resource}</p>
      </div>
      
      <form onSubmit={{handleCreate}} className="bg-white p-6 rounded-xl shadow-lg mb-8 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Create New {Resource}</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{Resource} Title</label>
            <input type="text" placeholder="Enter title" value={{title}}
              onChange={{(e) => setTitle(e.target.value)}}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description (optional)</label>
            <textarea placeholder="Add a description" value={{description}}
              onChange={{(e) => setDescription(e.target.value)}} rows={{3}}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none" />
          </div>
          <button type="submit" disabled={{creating}}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed">
            {{creating ? 'Creating...' : '+ Add {Resource}'}}
          </button>
        </div>
      </form>

      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Your {Resource}s ({{{resource}.length}})</h2>
        {{{resource}.length === 0 ? (
          <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl p-12 text-center">
            <div className="text-gray-400 text-5xl mb-4">📝</div>
            <p className="text-gray-600 text-lg mb-2">No {resource} yet</p>
            <p className="text-gray-500">Create your first {resource_singular} using the form above</p>
          </div>
        ) : (
          {resource}.map(item => (
            <div key={{item.id}} 
              className="bg-white p-6 rounded-xl shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-900 mb-1">{{item.title}}</h3>
                  {{item.description && (
                    <p className="text-gray-600 text-sm leading-relaxed">{{item.description}}</p>
                  )}}
                  <div className="mt-3 flex items-center gap-2">
                    <span className={{`text-xs px-2 py-1 rounded-full ${{item.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}}`}}>
                      {{item.is_active ? '✓ Active' : 'Inactive'}}
                    </span>
                  </div>
                </div>
                <button onClick={{() => handleDelete(item.id)}}
                  className="ml-4 text-red-500 hover:text-red-700 hover:bg-red-50 px-3 py-2 rounded-lg font-medium text-sm transition-colors">
                  Delete
                </button>
              </div>
            </div>
          ))
        )}}
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
