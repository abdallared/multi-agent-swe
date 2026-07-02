import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

interface LoginPageProps {
  onLogin: (token: string, user: { email: string; full_name?: string }) => void;
}

import { User, Mail, Lock, Eye, EyeOff, Zap, Brain, Activity, Globe, GitBranch, Sparkles } from 'lucide-react';
import { NeuralCanvas } from './components/NeuralCanvas';

// ── Status dot ────────────────────────────────────────────────────
const StatusDot: React.FC<{ label: string }> = ({ label }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: '#8b9dc7' }}>
    <span style={{
      width: 6, height: 6, borderRadius: '50%', background: '#10b981',
      boxShadow: '0 0 6px #10b981',
      display: 'inline-block',
    }} />
    {label}
  </div>
);

// ── Input ──────────────────────────────────────────────────────────
const AuthInput: React.FC<React.InputHTMLAttributes<HTMLInputElement> & { label: string; icon: React.ReactNode }> = ({
  label, icon, ...props
}) => {
  const [focused, setFocused] = useState(false);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={{ fontSize: 13, fontWeight: 500, color: '#c7c4d7' }}>{label}</label>
      <div style={{ position: 'relative' }}>
        <span style={{
          position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)',
          display: 'flex', alignItems: 'center', pointerEvents: 'none', opacity: 0.6,
          color: '#dee1f7',
        }}>{icon}</span>
        <input
          {...props}
          onFocus={(e) => { setFocused(true); props.onFocus?.(e); }}
          onBlur={(e) => { setFocused(false); props.onBlur?.(e); }}
          style={{
            width: '100%',
            background: '#161b22',
            border: `1px solid ${focused ? '#6366f1' : 'rgba(255,255,255,0.1)'}`,
            boxShadow: focused ? '0 0 0 3px rgba(99,102,241,0.2)' : 'none',
            borderRadius: 8,
            color: '#dee1f7',
            fontSize: 14,
            padding: '11px 14px 11px 40px',
            outline: 'none',
            transition: 'border-color 0.2s, box-shadow 0.2s',
            boxSizing: 'border-box',
          }}
        />
      </div>
    </div>
  );
};

// ── Main ──────────────────────────────────────────────────────────
const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendOk, setBackendOk] = useState(false);

  // Ping backend health
  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((r) => { if (r.ok) setBackendOk(true); })
      .catch(() => setBackendOk(false));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (mode === 'register' && password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const body: Record<string, string> = { email, password };
      if (mode === 'register' && fullName) body.full_name = fullName;

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(data.user));
      onLogin(data.access_token, data.user);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex', height: '100vh', width: '100vw',
      fontFamily: "'Inter', -apple-system, sans-serif",
      background: '#0a0f1e',
      overflow: 'hidden',
    }}>
      {/* ── Left Panel ── */}
      <div style={{
        flex: 1,
        position: 'relative',
        background: 'linear-gradient(135deg, #0a0f1e 0%, #1a1040 50%, #0d0a2e 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}>
        <NeuralCanvas />

        {/* Brand content */}
        <div style={{ position: 'relative', zIndex: 1, textAlign: 'center', padding: '0 48px' }}>
          {/* Logo icon */}
          <div style={{
            width: 72, height: 72, borderRadius: 18,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 24px',
            boxShadow: '0 0 40px rgba(99,102,241,0.5)',
            color: '#ffffff',
          }}><Sparkles size={36} /></div>

          <h1 style={{
            fontSize: 32, fontWeight: 700, color: '#dee1f7',
            margin: '0 0 12px',
            letterSpacing: '-0.02em',
            lineHeight: 1.2,
          }}>AI Software Company</h1>

          <p style={{
            fontSize: 14, fontWeight: 500, color: '#8b5cf6',
            letterSpacing: '0.15em', textTransform: 'uppercase',
            margin: '0 0 40px',
          }}>Multi-Agent SWE Platform</p>

          {/* Feature bullets */}
          {[
            { icon: <Zap size={18} />, text: 'Parallel multi-agent code generation' },
            { icon: <Brain size={18} />, text: 'Local LLM via Ollama — fully private' },
            { icon: <Activity size={18} />, text: 'Real-time WebSocket pipeline updates' },
          ].map((f) => (
            <div key={f.text} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '10px 20px',
              background: 'rgba(99,102,241,0.08)',
              border: '1px solid rgba(99,102,241,0.15)',
              borderRadius: 10,
              marginBottom: 10,
              textAlign: 'left',
            }}>
              <span style={{ color: '#8b5cf6', display: 'flex' }}>{f.icon}</span>
              <span style={{ fontSize: 13, color: '#c7c4d7' }}>{f.text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Right Panel ── */}
      <div style={{
        width: 480,
        minWidth: 420,
        background: '#0d1117',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 40px',
        position: 'relative',
        borderLeft: '1px solid rgba(255,255,255,0.05)',
      }}>

        {/* Status indicators — top-right */}
        <div style={{
          position: 'absolute', top: 20, right: 20,
          display: 'flex', gap: 12,
        }}>
          <StatusDot label={`Backend :8000${backendOk ? '' : ' ✗'}`} />
          <StatusDot label="Ollama" />
        </div>

        {/* Glassmorphism card */}
        <div style={{
          width: '100%',
          background: 'rgba(13,17,23,0.8)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(99,102,241,0.2)',
          borderRadius: 16,
          padding: '40px 36px',
          boxShadow: '0 0 60px rgba(99,102,241,0.08)',
        }}>
          {/* Header */}
          <div style={{ marginBottom: 32 }}>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: '#dee1f7', margin: '0 0 6px' }}>
              {mode === 'login' ? 'Welcome back' : 'Create account'}
            </h2>
            <p style={{ fontSize: 14, color: '#8b9dc7', margin: 0 }}>
              {mode === 'login' ? 'Sign in to your account' : 'Join the platform today'}
            </p>
          </div>

          {/* Error banner */}
          {error && (
            <div style={{
              background: 'rgba(244,63,94,0.1)',
              border: '1px solid rgba(244,63,94,0.3)',
              borderRadius: 8,
              padding: '10px 14px',
              fontSize: 13,
              color: '#f87171',
              marginBottom: 20,
            }}>
              ⚠ {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
            {mode === 'register' && (
              <AuthInput
                label="Full Name"
                icon={<User size={16} />}
                type="text"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            )}

            <AuthInput
              label="Email address"
              icon={<Mail size={16} />}
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            {/* Password with toggle */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <label style={{ fontSize: 13, fontWeight: 500, color: '#c7c4d7' }}>Password</label>
              <div style={{ position: 'relative' }}>
                <span style={{
                  position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)',
                  display: 'flex', pointerEvents: 'none', opacity: 0.6, color: '#dee1f7',
                }}><Lock size={16} /></span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Min. 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    background: '#161b22',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: 8,
                    color: '#dee1f7',
                    fontSize: 14,
                    padding: '11px 44px 11px 40px',
                    outline: 'none',
                    boxSizing: 'border-box',
                    transition: 'border-color 0.2s, box-shadow 0.2s',
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#6366f1';
                    e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.2)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = 'rgba(255,255,255,0.1)';
                    e.target.style.boxShadow = 'none';
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer',
                    display: 'flex', opacity: 0.6, color: '#dee1f7', padding: 4,
                  }}
                >{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button>
              </div>
            </div>

            {mode === 'register' && (
              <AuthInput
                label="Confirm Password"
                icon={<Lock size={16} />}
                type={showPassword ? 'text' : 'password'}
                placeholder="Repeat your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            )}

            {/* Remember + Forgot row (login only) */}
            {mode === 'login' && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#8b9dc7', cursor: 'pointer' }}>
                  <input type="checkbox" style={{ accentColor: '#6366f1', width: 14, height: 14 }} />
                  Remember me
                </label>
                <button type="button" style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  fontSize: 13, color: '#6366f1', padding: 0,
                  textDecoration: 'underline',
                }}>Forgot password?</button>
              </div>
            )}

            {/* Primary CTA */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                background: loading ? 'rgba(99,102,241,0.5)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                border: 'none',
                borderRadius: 8,
                color: '#fff',
                fontSize: 15,
                fontWeight: 600,
                padding: '13px',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                boxShadow: loading ? 'none' : '0 4px 20px rgba(99,102,241,0.35)',
                marginTop: 4,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
              }}
              onMouseEnter={(e) => {
                if (!loading) {
                  (e.target as HTMLButtonElement).style.boxShadow = '0 4px 30px rgba(99,102,241,0.55)';
                  (e.target as HTMLButtonElement).style.transform = 'translateY(-1px)';
                }
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLButtonElement).style.boxShadow = '0 4px 20px rgba(99,102,241,0.35)';
                (e.target as HTMLButtonElement).style.transform = 'translateY(0)';
              }}
            >
              {loading && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ animation: 'spin 0.8s linear infinite' }}>
                  <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3" />
                  <path d="M12 2a10 10 0 0 1 10 10" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
                </svg>
              )}
              {loading ? 'Please wait…' : mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          {/* Divider */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 12,
            margin: '24px 0',
          }}>
            <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.07)' }} />
            <span style={{ fontSize: 12, color: '#4a5a7a' }}>or continue with</span>
            <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.07)' }} />
          </div>

          {/* Social buttons */}
          <div style={{ display: 'flex', gap: 12 }}>
            {[
              { icon: <Globe size={18} />, label: 'Google' },
              { icon: <GitBranch size={18} />, label: 'GitHub' },
            ].map((s) => (
              <button
                key={s.label}
                type="button"
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 8,
                  color: '#c7c4d7',
                  fontSize: 13,
                  fontWeight: 500,
                  padding: '10px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  transition: 'border-color 0.2s, background 0.2s',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(99,102,241,0.4)';
                  (e.currentTarget as HTMLButtonElement).style.background = 'rgba(99,102,241,0.06)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.1)';
                  (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                }}
              >
                {s.icon} {s.label}
              </button>
            ))}
          </div>

          {/* Toggle mode */}
          <p style={{
            textAlign: 'center', fontSize: 13, color: '#8b9dc7',
            marginTop: 24, marginBottom: 0,
          }}>
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button
              type="button"
              onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                color: '#6366f1', fontWeight: 600, fontSize: 13, padding: 0,
              }}
            >
              {mode === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        * { box-sizing: border-box; }
      `}</style>
    </div>
  );
};

export default LoginPage;
