import React, { useState, useEffect, useRef, useCallback } from 'react';

// ─── Types ──────────────────────────────────────────────────────
interface Message {
  id: string;
  type: 'user' | 'system' | 'phase_start' | 'phase_done' | 'complete' | 'error';
  content: string;
  phase?: number;
  phaseName?: string;
  timestamp: Date;
}

interface FileNode {
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileNode[];
}

interface PhaseInfo {
  num: number;
  name: string;
  icon: string;
  status: 'pending' | 'running' | 'done';
}

interface VerboseLog {
  id: string;
  agent: string;
  agent_type: string;
  model: string;
  kind: 'system_prompt' | 'prompt' | 'response' | 'error' | 'info';
  content: string;
  ts: number;
  elapsed_s?: number;
  char_count?: number;
  json_mode?: boolean;
  temperature?: number;
}

// ─── Constants ──────────────────────────────────────────────────
const PHASES: PhaseInfo[] = [
  { num: 1, name: 'Planning',      icon: '◎', status: 'pending' },
  { num: 2, name: 'Architecture',  icon: '◎', status: 'pending' },
  { num: 3, name: 'Backend',       icon: '◎', status: 'pending' },
  { num: 4, name: 'Frontend',      icon: '◎', status: 'pending' },
  { num: 5, name: 'Testing',       icon: '◎', status: 'pending' },
  { num: 6, name: 'Docker',        icon: '◎', status: 'pending' },
  { num: 7, name: 'Building',      icon: '◎', status: 'pending' },
];

// ─── File Icon helper ────────────────────────────────────────────
function getFileIcon(name: string): string {
  const ext = name.split('.').pop()?.toLowerCase() ?? '';
  const map: Record<string, string> = {
    py: '🐍', ts: '💙', tsx: '⚛️', js: '🟨', jsx: '⚛️',
    json: '📋', md: '📝', yml: 'yaml', yaml: '⚙️',
    toml: '⚙️', env: '🔐', txt: '📄', css: '🎨', html: '🌐',
    sh: '⚡', bat: '⚡', dockerfile: '🐳',
  };
  if (name.toLowerCase() === 'dockerfile') return '🐳';
  if (name.toLowerCase() === '.env' || name.toLowerCase() === '.env.example') return '🔐';
  return map[ext] ?? '📄';
}

// ─── Spinner ─────────────────────────────────────────────────────
const Spinner: React.FC<{ size?: number }> = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className="animate-spin-custom" style={{ flexShrink: 0 }}>
    <circle cx="12" cy="12" r="10" stroke="var(--border-light)" strokeWidth="2.5"/>
    <path d="M12 2a10 10 0 0 1 10 10" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round"/>
  </svg>
);

// ─── Phase Progress Panel ─────────────────────────────────────────
const PhaseProgress: React.FC<{ phases: PhaseInfo[]; current: number; isGenerating: boolean }> = ({
  phases, current, isGenerating
}) => {
  const done = phases.filter(p => p.status === 'done').length;
  const pct = isGenerating ? Math.round((done / phases.length) * 100) : 0;

  if (!isGenerating && done === 0) return null;

  return (
    <div style={{
      padding: '12px 14px',
      borderBottom: '1px solid var(--border)',
      background: 'var(--bg-base)',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
          Generation Pipeline
        </span>
        <span style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 600 }}>
          {pct}%
        </span>
      </div>
      <div className="progress-track" style={{ marginBottom: 10 }}>
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
        {phases.map(p => (
          <div key={p.num} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div className={`dot ${p.status === 'done' ? 'dot-green' : p.status === 'running' ? 'dot-accent' : 'dot-muted'}`}
              style={{ animation: p.status === 'running' ? 'pulse-accent 1.5s infinite' : undefined }} />
            <span style={{
              fontSize: 11,
              color: p.status === 'done' ? 'var(--green)' : p.status === 'running' ? 'var(--accent)' : 'var(--text-muted)',
              fontWeight: p.status === 'running' ? 600 : 400,
            }}>
              {p.name}
            </span>
            {p.status === 'running' && <Spinner size={10} />}
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── File Tree ────────────────────────────────────────────────────
const FileTreeNode: React.FC<{
  node: FileNode;
  level: number;
  selectedFile: string | null;
  onSelect: (node: FileNode) => void;
}> = ({ node, level, selectedFile, onSelect }) => {
  const [isOpen, setIsOpen] = useState(level < 2);

  if (node.type === 'file') {
    return (
      <div
        className={`file-item ${selectedFile === node.path ? 'active' : ''}`}
        style={{ paddingLeft: `${level * 14 + 10}px` }}
        onClick={() => onSelect(node)}
      >
        <span style={{ fontSize: 13, flexShrink: 0 }}>{getFileIcon(node.name)}</span>
        <span style={{ fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {node.name}
        </span>
      </div>
    );
  }

  return (
    <div>
      <div
        className="file-item"
        style={{ paddingLeft: `${level * 14 + 10}px` }}
        onClick={() => setIsOpen(o => !o)}
      >
        <span style={{ fontSize: 11, color: 'var(--text-muted)', width: 12, textAlign: 'center', flexShrink: 0 }}>
          {isOpen ? '▾' : '▸'}
        </span>
        <span style={{ fontSize: 13, flexShrink: 0 }}>📁</span>
        <span style={{ fontSize: 12, fontWeight: 500 }}>{node.name}</span>
      </div>
      {isOpen && node.children?.map(child => (
        <FileTreeNode
          key={child.path}
          node={child}
          level={level + 1}
          selectedFile={selectedFile}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
};

// ─── Message Bubble ───────────────────────────────────────────────
const MessageBubble: React.FC<{ msg: Message }> = ({ msg }) => {
  const time = msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  if (msg.type === 'user') return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 3 }}>
      <div className="bubble-user">{msg.content}</div>
      <span style={{ fontSize: 10, color: 'var(--text-muted)', paddingRight: 4 }}>{time}</span>
    </div>
  );

  if (msg.type === 'complete') return (
    <div className="bubble-complete animate-fadeIn">
      <div style={{ fontWeight: 600, marginBottom: 2 }}>Generation Complete</div>
      <div style={{ fontSize: 12 }}>{msg.content}</div>
    </div>
  );

  if (msg.type === 'error') return (
    <div style={{
      background: 'rgba(244,63,94,0.1)',
      border: '1px solid rgba(244,63,94,0.25)',
      borderRadius: 10,
      padding: '10px 14px',
      fontSize: 12,
      color: '#f43f5e',
    }} className="animate-fadeIn">
      {msg.content}
    </div>
  );

  if (msg.type === 'phase_start') return (
    <div className="bubble-phase animate-slideIn">
      <Spinner size={13} />
      <div>
        <span style={{ color: 'var(--accent)', fontWeight: 600 }}>Phase {msg.phase} — {msg.phaseName}</span>
        <div style={{ marginTop: 1, color: 'var(--text-muted)', fontSize: 11 }}>Starting…</div>
      </div>
    </div>
  );

  if (msg.type === 'phase_done') return (
    <div className="bubble-phase animate-slideIn">
      <div style={{ width: 13, height: 13, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ color: 'var(--green)', fontSize: 13, lineHeight: 1 }}>✓</span>
      </div>
      <span style={{ color: 'var(--green)', fontWeight: 500 }}>Phase {msg.phase} — {msg.phaseName} done</span>
    </div>
  );

  return (
    <div className="bubble-system animate-fadeIn">{msg.content}</div>
  );
};

// ─── App ──────────────────────────────────────────────────────────
export default function App() {
  const [messages, setMessages]       = useState<Message[]>([]);
  const [input, setInput]             = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [fileTree, setFileTree]       = useState<FileNode | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [fileLoading, setFileLoading] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [cleanName, setCleanName]     = useState('');
  const [phases, setPhases]           = useState<PhaseInfo[]>(PHASES.map(p => ({ ...p })));
  const [currentPhase, setCurrentPhase] = useState(0);
  const [ollamaOk, setOllamaOk]       = useState<boolean | null>(null);
  
  // Verbose Agent Thinking States
  const [showVerbose, setShowVerbose] = useState(false);
  const [verboseLogs, setVerboseLogs] = useState<VerboseLog[]>([]);

  const wsRef         = useRef<WebSocket | null>(null);
  const bottomRef     = useRef<HTMLDivElement>(null);
  const verboseBottomRef = useRef<HTMLDivElement>(null);
  const textareaRef   = useRef<HTMLTextAreaElement>(null);

  // Check Ollama availability
  useEffect(() => {
    fetch('http://localhost:8000/api/health')
      .then(r => r.json())
      .then(d => setOllamaOk(d?.ollama_connected ?? true))
      .catch(() => setOllamaOk(false));
  }, []);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-scroll verbose logs
  useEffect(() => {
    if (showVerbose) {
      verboseBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [verboseLogs, showVerbose]);

  const addMsg = useCallback((msg: Omit<Message, 'id' | 'timestamp'>) => {
    setMessages(prev => [...prev, { ...msg, id: crypto.randomUUID(), timestamp: new Date() }]);
  }, []);

  const resetPhases = () => setPhases(PHASES.map(p => ({ ...p, status: 'pending' })));

  const updatePhase = (num: number, status: PhaseInfo['status']) => {
    setPhases(prev => prev.map(p => p.num === num ? { ...p, status } : p));
  };

  const handleSend = () => {
    if (!input.trim() || isGenerating) return;
    const prompt = input.trim();
    setInput('');
    setIsGenerating(true);
    setFileTree(null);
    setSelectedFile(null);
    setFileContent('');
    setCurrentPhase(0);
    resetPhases();
    setVerboseLogs([]); // Clear logs for new run
    setShowVerbose(true); // Auto-show logs

    addMsg({ type: 'user', content: prompt });

    const ws = new WebSocket('ws://localhost:8000/ws/generate');
    wsRef.current = ws;

    ws.onopen = () => ws.send(JSON.stringify({ prompt }));

    ws.onmessage = (event) => {
      const res = JSON.parse(event.data);
      switch (res.type) {
        case 'phase_start': {
          const num: number = res.data.phase;
          const name: string = res.data.name;
          setCurrentPhase(num);
          updatePhase(num, 'running');
          addMsg({ type: 'phase_start', content: '', phase: num, phaseName: name });
          break;
        }
        case 'phase_complete': {
          const num: number = res.data.phase;
          const name: string = res.data.name;
          updatePhase(num, 'done');
          addMsg({ type: 'phase_done', content: '', phase: num, phaseName: name });
          break;
        }
        case 'generation_complete': {
          setIsGenerating(false);
          setCurrentPhase(0);
          setFileTree(res.data.file_tree);
          setProjectName(res.data.project_name);
          setCleanName(res.data.clean_project_name);
          setPhases(PHASES.map(p => ({ ...p, status: 'done' })));
          addMsg({
            type: 'complete',
            content: `"${res.data.project_name}" is ready — ${res.data.total_files ?? '?'} files generated`,
          });
          break;
        }
        case 'verbose': {
          const entry = res.data;
          setVerboseLogs(prev => [...prev, { ...entry, id: crypto.randomUUID() }]);
          break;
        }
        case 'error': {
          setIsGenerating(false);
          addMsg({ type: 'error', content: res.data.message });
          break;
        }
      }
    };

    ws.onerror = () => {
      setIsGenerating(false);
      addMsg({ type: 'error', content: 'Connection failed. Is the backend running?' });
    };

    ws.onclose = () => setIsGenerating(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileClick = async (node: FileNode) => {
    if (node.type !== 'file') return;
    setSelectedFile(node.path);
    setFileContent('');
    setFileLoading(true);
    try {
      const r = await fetch(`http://localhost:8000/api/file/${cleanName}/${node.path}`);
      const d = await r.json();
      setFileContent(d.content ?? `// Error: ${d.error}`);
    } catch {
      setFileContent('// Failed to load file');
    } finally {
      setFileLoading(false);
    }
  };

  const handleDownload = () => {
    if (!cleanName) return;
    const a = document.createElement('a');
    a.href = `http://localhost:8000/api/download/${cleanName}`;
    a.download = `${cleanName}.zip`;
    a.click();
  };

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const ta = textareaRef.current;
    if (ta) { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 120) + 'px'; }
  };

  // ─── Layout ──────────────────────────────────────────────────
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>

      {/* ── Top Bar ─────────────────────────────────────────── */}
      <div style={{
        height: 44,
        background: 'var(--bg-base)',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 16px',
        gap: 12,
        flexShrink: 0,
        zIndex: 10,
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 26, height: 26,
            background: 'linear-gradient(135deg, var(--accent) 0%, var(--indigo) 100%)',
            borderRadius: 7,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 13, fontWeight: 800, color: '#000',
            flexShrink: 0,
          }}>A</div>
          <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            AI Software Company
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 400 }}>— multi-agent SWE</span>
        </div>

        <div style={{ flex: 1 }} />

        {/* Status pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: 'var(--green)' }}>
            <div className="dot dot-green" />
            Backend :8000
          </div>
          <div style={{ width: 1, height: 14, background: 'var(--border)' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11,
            color: ollamaOk === false ? 'var(--red)' : ollamaOk === true ? 'var(--green)' : 'var(--text-muted)' }}>
            <div className={`dot ${ollamaOk === false ? 'dot-amber' : ollamaOk === true ? 'dot-green' : 'dot-muted'}`} />
            Ollama
          </div>
          <div style={{ width: 1, height: 14, background: 'var(--border)' }} />
          <button 
            className={`btn-verbose ${showVerbose ? 'active' : ''}`}
            onClick={() => setShowVerbose(v => !v)}
            style={{
              background: showVerbose ? 'var(--accent-dim)' : 'transparent',
              border: `1px solid ${showVerbose ? 'var(--accent)' : 'var(--border)'}`,
              color: showVerbose ? 'var(--accent)' : 'var(--text-secondary)',
              borderRadius: 6,
              padding: '4px 8px',
              fontSize: 11,
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              transition: 'all 0.12s',
            }}
          >
            <span style={{ fontSize: 9 }}>⚡</span> Verbose
          </button>
          {projectName && (
            <>
              <div style={{ width: 1, height: 14, background: 'var(--border)' }} />
              <button className="btn-download" onClick={handleDownload}>
                ↓ Download ZIP
              </button>
            </>
          )}
        </div>
      </div>

      {/* ── Main content ────────────────────────────────────── */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* ── Left: File Explorer ───────────────────────────── */}
        <div className="panel" style={{ width: 256, flexShrink: 0 }}>
          <div className="panel-header">
            <div className="dot dot-accent" />
            Explorer
            {fileTree && (
              <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--text-muted)', textTransform: 'none', letterSpacing: 0 }}>
                {projectName}
              </span>
            )}
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: '6px 4px' }}>
            {fileTree ? (
              <div className="animate-fadeIn">
                <FileTreeNode
                  node={fileTree}
                  level={0}
                  selectedFile={selectedFile}
                  onSelect={handleFileClick}
                />
              </div>
            ) : (
              <div style={{ padding: '40px 16px', textAlign: 'center' }}>
                <div style={{ fontSize: 28, marginBottom: 12, opacity: 0.3 }}>📁</div>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  No project yet.<br />Describe your idea →
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ── Center: Code Preview ──────────────────────────── */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg-base)' }}>
          {/* Tab bar */}
          <div style={{
            height: 36,
            background: 'var(--bg-panel)',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            padding: '0 4px',
            flexShrink: 0,
            overflowX: 'auto',
          }}>
            {selectedFile ? (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '0 14px',
                height: '100%',
                borderBottom: '2px solid var(--accent)',
                fontSize: 12,
                color: 'var(--text-primary)',
                fontWeight: 500,
                flexShrink: 0,
              }}>
                <span>{getFileIcon(selectedFile.split('/').pop() ?? '')}</span>
                <span>{selectedFile.split('/').pop()}</span>
                <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                  {selectedFile.includes('/') ? selectedFile.substring(0, selectedFile.lastIndexOf('/')) : ''}
                </span>
              </div>
            ) : (
              <span style={{ padding: '0 14px', fontSize: 11, color: 'var(--text-muted)' }}>
                Code Preview
              </span>
            )}
          </div>

          {/* Content */}
          <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
            {fileLoading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: 8 }}>
                {[100, 80, 60, 90, 70, 85].map((w, i) => (
                  <div key={i} className="skeleton" style={{ height: 14, width: `${w}%` }} />
                ))}
              </div>
            ) : fileContent ? (
              <pre className="code-view mono animate-fadeIn">{fileContent}</pre>
            ) : (
              <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
                <div style={{ fontSize: 48, opacity: 0.15 }}>{'</>'}</div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.7 }}>
                  Select a file from the explorer<br/>to preview its contents
                </p>
              </div>
            )}
          </div>

          {/* Collapsible Verbose Terminal Pane */}
          {showVerbose && (
            <div style={{
              height: 250,
              background: '#040813', // True dark shell background
              borderTop: '1px solid var(--border)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              flexShrink: 0,
            }}>
              {/* Drawer Header */}
              <div style={{
                height: 32,
                background: 'var(--bg-panel)',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                alignItems: 'center',
                padding: '0 12px',
                justifyContent: 'space-between',
                flexShrink: 0,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, fontWeight: 600, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <span style={{ color: 'var(--accent)', animation: isGenerating ? 'pulse-accent 1s infinite' : 'none' }}>●</span>
                  Agent Verbose Thinking Logs
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <button 
                    onClick={() => setVerboseLogs([])}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-muted)',
                      fontSize: 10,
                      cursor: 'pointer',
                    }}
                    className="verbose-header-btn"
                  >
                    Clear Logs
                  </button>
                  <button 
                    onClick={() => setShowVerbose(false)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-muted)',
                      fontSize: 10,
                      cursor: 'pointer',
                    }}
                    className="verbose-header-btn"
                  >
                    ✕ Close
                  </button>
                </div>
              </div>

              {/* Drawer Body (Logs stream) */}
              <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '10px 14px',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: 12,
                color: '#abb2bf',
                lineHeight: 1.5,
              }}>
                {verboseLogs.length === 0 ? (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: 11 }}>
                    No execution logs yet. Describe your project and start generating to view real-time model thinking.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {verboseLogs.map((log) => {
                      const timeStr = new Date(log.ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                      
                      // Assign color based on agent_type
                      let agentColor = 'var(--text-muted)';
                      if (log.agent_type === 'planner') agentColor = '#00e5b3';
                      else if (log.agent_type === 'architect') agentColor = '#a78bfa';
                      else if (log.agent_type === 'backend') agentColor = '#38bdf8';
                      else if (log.agent_type === 'frontend') agentColor = '#22d3ee';
                      else if (log.agent_type === 'testing') agentColor = '#fbbf24';
                      else if (log.agent_type === 'docker') agentColor = '#fb7185';

                      return (
                        <div key={log.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: 6 }}>
                          {/* Log Header */}
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', marginBottom: 4 }}>
                            <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>[{timeStr}]</span>
                            <span style={{ color: agentColor, fontWeight: 600 }}>[{log.agent}]</span>
                            <span style={{ background: 'rgba(255,255,255,0.06)', borderRadius: 4, padding: '1px 5px', fontSize: 10, color: 'var(--text-muted)' }}>
                              {log.model}
                            </span>
                            <span style={{ 
                              background: log.kind === 'error' ? 'rgba(244,63,94,0.15)' : 'rgba(0,229,179,0.08)',
                              color: log.kind === 'error' ? '#f43f5e' : 'var(--accent)',
                              borderRadius: 4, padding: '1px 5px', fontSize: 10, fontWeight: 600, textTransform: 'uppercase'
                            }}>
                              {log.kind.replace('_', ' ')}
                            </span>
                            {log.elapsed_s !== undefined && (
                              <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>
                                ({log.elapsed_s}s)
                              </span>
                            )}
                          </div>
                          {/* Log Content */}
                          <pre style={{
                            margin: 0,
                            whiteSpace: 'pre-wrap',
                            background: 'rgba(0,0,0,0.2)',
                            padding: '6px 10px',
                            borderRadius: 4,
                            border: '1px solid rgba(255,255,255,0.03)',
                            fontSize: 11,
                            color: log.kind === 'error' ? '#f43f5e' : '#e0e6ed',
                            maxHeight: 180,
                            overflowY: 'auto'
                          }}>
                            {log.content}
                          </pre>
                        </div>
                      );
                    })}
                    <div ref={verboseBottomRef} />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* ── Right: AI Chat ────────────────────────────────── */}
        <div className="panel" style={{ width: 360, borderLeft: '1px solid var(--border)', borderRight: 'none' }}>
          <div className="panel-header">
            <div className="dot dot-indigo" style={{ animation: isGenerating ? 'pulse-accent 1.5s infinite' : undefined }} />
            AI Assistant
            {isGenerating && (
              <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 5,
                fontSize: 10, color: 'var(--accent)', textTransform: 'none', letterSpacing: 0 }}>
                <Spinner size={11} />
                Phase {currentPhase}/7
              </span>
            )}
          </div>

          {/* Phase progress */}
          <PhaseProgress phases={phases} current={currentPhase} isGenerating={isGenerating || phases.some(p => p.status === 'done')} />

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '12px 12px', display: 'flex', flexDirection: 'column', gap: 10 }}>
            {messages.length === 0 && (
              <div style={{ padding: '32px 8px', textAlign: 'center' }} className="animate-fadeIn">
                <div style={{
                  width: 44, height: 44,
                  background: 'linear-gradient(135deg, var(--accent-dim), var(--indigo-dim))',
                  border: '1px solid var(--border-light)',
                  borderRadius: 12,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 14px',
                  fontSize: 20,
                }}>✦</div>
                <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
                  Ready to build
                </p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: 16 }}>
                  Describe your project and the multi-agent<br/>pipeline will generate it for you.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {[
                    'Blog platform with auth & comments',
                    'Task manager with team workspaces',
                    'E-commerce API with Stripe payments',
                  ].map(example => (
                    <button
                      key={example}
                      onClick={() => { setInput(example); textareaRef.current?.focus(); }}
                      style={{
                        background: 'var(--bg-surface)',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        padding: '7px 12px',
                        fontSize: 11.5,
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 0.12s',
                      }}
                      onMouseEnter={e => (e.currentTarget.style.borderColor = 'rgba(0,229,179,0.3)')}
                      onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map(msg => (
              <MessageBubble key={msg.id} msg={msg} />
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Input area */}
          <div style={{
            padding: '12px',
            borderTop: '1px solid var(--border)',
            background: 'var(--bg-base)',
            flexShrink: 0,
          }}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
              <textarea
                ref={textareaRef}
                className="chat-input"
                style={{ flex: 1, minHeight: 38, maxHeight: 120 }}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Describe your project… (Enter to send)"
                disabled={isGenerating}
                rows={1}
              />
              <button
                className="btn-send"
                onClick={handleSend}
                disabled={isGenerating || !input.trim()}
                title="Send (Enter)"
              >
                {isGenerating ? <Spinner size={16} /> : '↑'}
              </button>
            </div>
            <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 6, textAlign: 'center' }}>
              Shift+Enter for new line · Generation takes 5–15 min
            </p>
          </div>
        </div>

      </div>

      {/* ── Status Bar ──────────────────────────────────────── */}
      <div className="statusbar">
        <div className="statusbar-item">
          <div className="dot dot-green" style={{ width: 6, height: 6 }} />
          <span>Ollama local</span>
        </div>
        <div className="statusbar-item">
          <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>▸</span>
          <span>qwen3.5 · gemma4 · qwen2.5-coder</span>
        </div>
        {projectName && (
          <div className="statusbar-item" style={{ marginLeft: 'auto' }}>
            <span style={{ color: 'var(--accent)' }}>✦</span>
            <span>{projectName}</span>
          </div>
        )}
        {!projectName && (
          <div style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--text-muted)' }}>
            multi-agent-swe v2.0
          </div>
        )}
      </div>
    </div>
  );
}
