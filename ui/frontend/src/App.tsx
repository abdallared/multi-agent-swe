import React, { useState, useEffect, useRef } from 'react';

interface Message {
  type: 'user' | 'system' | 'phase' | 'complete';
  content: string;
  data?: any;
}

interface FileNode {
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileNode[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [fileTree, setFileTree] = useState<FileNode | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [projectName, setProjectName] = useState<string>('');
  const [cleanProjectName, setCleanProjectName] = useState<string>(''); // اسم المشروع النظيف
  const [currentPhase, setCurrentPhase] = useState<number>(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message]);
  };

  const handleSend = () => {
    if (!input.trim() || isGenerating) return;

    const userMessage: Message = {
      type: 'user',
      content: input
    };
    addMessage(userMessage);
    setInput('');
    setIsGenerating(true);
    setCurrentPhase(0);

    // Connect WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/generate');
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ prompt: input }));
    };

    ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      
      switch (response.type) {
        case 'phase_start':
          setCurrentPhase(response.data.phase);
          addMessage({
            type: 'phase',
            content: `🔄 Phase ${response.data.phase}: ${response.data.name} - Starting...`,
            data: response.data
          });
          break;
        
        case 'phase_complete':
          addMessage({
            type: 'phase',
            content: `✅ Phase ${response.data.phase}: ${response.data.name} - Completed`,
            data: response.data
          });
          break;
        
        case 'generation_complete':
          setIsGenerating(false);
          setCurrentPhase(0);
          setFileTree(response.data.file_tree);
          setProjectName(response.data.project_name);
          setCleanProjectName(response.data.clean_project_name); // حفظ الاسم النظيف
          addMessage({
            type: 'complete',
            content: `🎉 Project "${response.data.project_name}" generated successfully!`,
            data: response.data
          });
          break;
        
        case 'error':
          setIsGenerating(false);
          setCurrentPhase(0);
          addMessage({
            type: 'system',
            content: `❌ Error: ${response.data.message}`
          });
          break;
      }
    };

    ws.onerror = () => {
      setIsGenerating(false);
      addMessage({
        type: 'system',
        content: '❌ Connection error. Make sure the backend is running.'
      });
    };

    ws.onclose = () => {
      setIsGenerating(false);
    };
  };

  const handleFileClick = async (node: FileNode) => {
    if (node.type === 'file') {
      setSelectedFile(node.path);
      try {
        const response = await fetch(`http://localhost:8000/api/file/${cleanProjectName}/${node.path}`);
        const data = await response.json();
        if (data.content) {
          setFileContent(data.content);
        } else {
          setFileContent(`Error: ${data.error || 'Could not load file'}`);
        }
      } catch (error) {
        setFileContent(`Error loading file: ${error}`);
      }
    }
  };

  const handleDownload = () => {
    if (!cleanProjectName) return;
    
    const downloadUrl = `http://localhost:8000/api/download/${cleanProjectName}`;
    
    // إنشاء link مؤقت للتحميل
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `${cleanProjectName}.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const FileTreeNode: React.FC<{ node: FileNode; level: number }> = ({ node, level }) => {
    const [isOpen, setIsOpen] = useState(true);

    if (node.type === 'file') {
      return (
        <div
          className={`flex items-center gap-2 px-2 py-1 cursor-pointer hover:bg-slate-700 rounded ${
            selectedFile === node.path ? 'bg-slate-700' : ''
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => handleFileClick(node)}
        >
          <span className="text-blue-400">📄</span>
          <span className="text-sm text-gray-300">{node.name}</span>
        </div>
      );
    }

    return (
      <div>
        <div
          className="flex items-center gap-2 px-2 py-1 cursor-pointer hover:bg-slate-700 rounded"
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => setIsOpen(!isOpen)}
        >
          <span className="text-yellow-400">{isOpen ? '📂' : '📁'}</span>
          <span className="text-sm text-gray-300 font-medium">{node.name}</span>
        </div>
        {isOpen && node.children && (
          <div>
            {node.children.map(child => (
              <FileTreeNode key={child.path} node={child} level={level + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-slate-900 text-white">
      {/* Left Sidebar - File Explorer */}
      <div className="w-80 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-4 border-b border-slate-700">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <span>📁</span>
            Project Files
          </h2>
          {projectName && (
            <div className="mt-2 flex items-center justify-between">
              <p className="text-sm text-gray-400">{projectName}</p>
              <button
                onClick={handleDownload}
                className="bg-green-600 hover:bg-green-700 text-white text-xs px-3 py-1 rounded flex items-center gap-1"
                title="Download project as ZIP"
              >
                <span>⬇️</span>
                <span>Download</span>
              </button>
            </div>
          )}
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {fileTree ? (
            <FileTreeNode node={fileTree} level={0} />
          ) : (
            <div className="text-center text-gray-500 mt-8">
              <p>No project generated yet</p>
              <p className="text-sm mt-2">Start by describing your project →</p>
            </div>
          )}
        </div>
      </div>

      {/* Middle - Code Preview */}
      <div className="flex-1 flex flex-col bg-slate-900">
        <div className="p-4 border-b border-slate-700">
          <h2 className="text-lg font-bold">
            {selectedFile || 'Code Preview'}
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {fileContent ? (
            <pre className="bg-slate-800 p-4 rounded-lg text-sm overflow-x-auto">
              <code className="text-gray-300">{fileContent}</code>
            </pre>
          ) : (
            <div className="text-center text-gray-500 mt-8">
              <p>Select a file to view its content</p>
            </div>
          )}
        </div>
      </div>

      {/* Right Sidebar - Chat */}
      <div className="w-96 bg-slate-800 border-l border-slate-700 flex flex-col">
        <div className="p-4 border-b border-slate-700">
          <h2 className="text-lg font-bold">💬 AI Assistant</h2>
          <p className="text-sm text-gray-400">Describe your project idea</p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-8">
              <p className="text-lg mb-2">👋 Welcome!</p>
              <p className="text-sm">Describe your project and I'll generate it for you.</p>
              <p className="text-xs mt-4 text-gray-600">Example: "Build a blog platform with user authentication"</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg ${
                msg.type === 'user'
                  ? 'bg-blue-600 ml-8'
                  : msg.type === 'phase'
                  ? 'bg-slate-700'
                  : msg.type === 'complete'
                  ? 'bg-green-600'
                  : 'bg-slate-700'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.data && msg.type === 'phase' && msg.data.data && (
                <div className="mt-2 text-xs text-gray-300">
                  {Object.entries(msg.data.data).map(([key, value]) => (
                    <div key={key}>
                      {key}: {String(value)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {isGenerating && (
            <div className="flex items-center gap-2 text-blue-400">
              <span className="animate-spin text-xl">⏳</span>
              <span className="text-sm">
                Generating... Phase {currentPhase}/5
              </span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-slate-700">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Describe your project..."
              disabled={isGenerating}
              className="flex-1 bg-slate-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={isGenerating || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition-colors"
            >
              <span className="text-xl">📤</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
