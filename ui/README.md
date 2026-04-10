# 🎨 AI Software Company - Web UI

Modern web interface for AI Software Company with real-time project generation.

## ✨ Features

- 💬 **Chat Interface**: Describe your project in natural language
- 📁 **File Explorer**: Browse generated project files (left sidebar)
- 📝 **Code Preview**: View file contents (center panel)
- 🔄 **Real-time Updates**: Watch your project being generated live
- 📊 **Progress Tracking**: See which phase is currently running
- 🎨 **Modern Design**: Clean, dark-themed UI inspired by VS Code

## 🏗️ Architecture

```
ui/
├── backend/
│   └── app.py          # FastAPI backend with WebSocket
└── frontend/
    ├── src/
    │   ├── App.tsx     # Main React component
    │   ├── main.tsx    # Entry point
    │   └── index.css   # Tailwind styles
    ├── package.json
    └── vite.config.ts
```

## 🚀 Quick Start

### Prerequisites

1. **Backend Requirements**:
   - Python 3.11+
   - Ollama running with models
   - All project dependencies installed

2. **Frontend Requirements**:
   - Node.js 18+
   - npm or yarn

### Installation

#### 1. Start Backend

```bash
# From project root
cd ui/backend

# Install dependencies (if needed)
pip install fastapi uvicorn websockets

# Run backend
python app.py
```

Backend will run on: http://localhost:8000

#### 2. Start Frontend

```bash
# From project root
cd ui/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on: http://localhost:3000

### 3. Open Browser

Navigate to: http://localhost:3000

## 📖 Usage

### Generate a Project

1. **Enter Project Description**:
   ```
   Build a blog platform with user authentication and post management
   ```

2. **Watch Real-time Generation**:
   - Phase 1: Planning (1-2 min)
   - Phase 2: Architecture (2-3 min)
   - Phase 3: Backend Code (1-2 min)
   - Phase 4: File Building (<1 sec)
   - Phase 5: Frontend Code (1-2 min)

3. **Explore Generated Files**:
   - Click folders in left sidebar to expand
   - Click files to view content in center panel
   - See project structure in real-time

### Example Prompts

```
Build a task management app with teams and priorities
```

```
Create an e-commerce platform with products, cart, and checkout
```

```
Build a social media app with posts, comments, and likes
```

## 🎨 UI Layout

```
┌─────────────┬──────────────────┬─────────────┐
│             │                  │             │
│   File      │   Code Preview   │    Chat     │
│  Explorer   │                  │  Interface  │
│             │                  │             │
│  (Left)     │    (Center)      │   (Right)   │
│             │                  │             │
│  - Folders  │  - File content  │  - Messages │
│  - Files    │  - Syntax        │  - Input    │
│  - Tree     │    highlight     │  - Progress │
│             │                  │             │
└─────────────┴──────────────────┴─────────────┘
```

## 🔧 Configuration

### Backend Configuration

Edit `ui/backend/app.py`:

```python
# Change port
uvicorn.run(app, host="0.0.0.0", port=8000)

# Enable/disable CORS
allow_origins=["*"]  # Change for production
```

### Frontend Configuration

Edit `ui/frontend/vite.config.ts`:

```typescript
server: {
  port: 3000,  // Change frontend port
  proxy: {
    '/api': 'http://localhost:8000',  // Backend URL
  }
}
```

## 🎯 Features in Detail

### 1. Real-time WebSocket Communication

- Instant updates during generation
- No polling required
- Efficient bidirectional communication

### 2. File Tree Viewer

- Expandable/collapsible folders
- File type icons
- Click to view content
- Smooth navigation

### 3. Code Preview

- Syntax highlighting (coming soon)
- Line numbers (coming soon)
- Copy to clipboard (coming soon)
- Download file (coming soon)

### 4. Progress Tracking

- Current phase indicator
- Phase completion status
- Time estimates
- Error handling

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Backend won't start
```bash
# Solution: Check if port 8000 is available
netstat -an | grep 8000

# Or use different port
uvicorn app:app --port 8001
```

**Problem**: WebSocket connection fails
```bash
# Solution: Make sure Ollama is running
ollama list

# Restart Ollama
ollama serve
```

### Frontend Issues

**Problem**: Frontend won't start
```bash
# Solution: Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Can't connect to backend
```bash
# Solution: Check backend is running
curl http://localhost:8000/api/health
```

## 📊 Performance

### Generation Times

| Phase | Time | Description |
|-------|------|-------------|
| Planning | 1-2 min | Analyze requirements |
| Architecture | 2-3 min | Design system |
| Backend | 1-2 min | Generate code |
| File Building | <1 sec | Create files |
| Frontend | 1-2 min | Generate UI |

**Total**: 5-10 minutes for complete project

### Optimization Tips

1. **Use smaller models** for faster generation:
   ```bash
   # In .env
   PLANNER_MODEL=llama3.2:3b
   BACKEND_MODEL=llama3.2:3b
   ```

2. **Close other applications** to free memory

3. **Use SSD** for faster file operations

## 🚀 Deployment

### Production Build

```bash
# Build frontend
cd ui/frontend
npm run build

# Serve with backend
cd ../backend
# Serve static files from frontend/dist
```

### Docker (Coming Soon)

```bash
docker-compose up
```

## 🎓 Development

### Adding New Features

1. **Backend**: Edit `ui/backend/app.py`
2. **Frontend**: Edit `ui/frontend/src/App.tsx`
3. **Styling**: Edit `ui/frontend/src/index.css`

### Project Structure

```
ui/
├── backend/
│   └── app.py              # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main component
│   │   ├── main.tsx        # Entry point
│   │   └── index.css       # Styles
│   ├── index.html          # HTML template
│   ├── package.json        # Dependencies
│   ├── vite.config.ts      # Vite config
│   └── tailwind.config.js  # Tailwind config
└── README.md               # This file
```

## 📝 TODO

- [ ] Syntax highlighting for code preview
- [ ] Download project as ZIP
- [ ] Project history
- [ ] Multiple projects management
- [ ] Dark/Light theme toggle
- [ ] Mobile responsive design
- [ ] File search
- [ ] Code editing
- [ ] Git integration

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

- **Issues**: GitHub Issues
- **Docs**: See main project README
- **Discord**: Coming soon

---

**Version**: 2.0.0  
**Last Updated**: 2026-04-10  
**Status**: ✅ Production Ready

🎉 **Enjoy building with AI Software Company UI!**
