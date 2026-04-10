"""
Configuration Module
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    إعدادات المشروع
    """
    # LLM Provider
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    
    # Agent Models
    planner_model: str = "qwen2.5:7b"
    architect_model: str = "gemma4:latest"
    backend_model: str = "qwen2.5-coder:7b"
    frontend_model: str = "qwen2.5-coder:7b"
    ai_model: str = "qwen2.5-coder:7b"
    testing_model: str = "llama3.2:3b"
    debugger_model: str = "llama3.1:8b"
    refactor_model: str = "qwen2.5-coder:7b"
    devops_model: str = "llama3.2:3b"
    embeddings_model: str = "nomic-embed-text:latest"
    
    # Project Settings
    max_iterations: int = 50
    output_dir: str = "./output"
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton
settings = Settings()
