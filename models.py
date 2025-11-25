from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile

class ChatMessage(BaseModel):
    id: str
    user_id: str
    message: str
    response: str
    agent_type: str
    timestamp: datetime
    chat_id: str

class ChatSession(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    folder_id: Optional[str] = None

class UserSettings(BaseModel):
    user_id: str
    personality: str = "Professional"  # Friendly, Professional, Sarcastic, Developer, Creative
    tone: int = 50  # 0-100
    creativity: int = 50  # 0-100
    detail_level: int = 50  # 0-100
    response_length: str = "Medium"  # Short, Medium, Long, Unlimited
    theme: str = "system"  # light, dark, system
    font_size: str = "medium"  # small, medium, large
    auto_save: bool = True
    web_search: bool = False
    real_time: bool = False
    safe_mode: bool = True
    language: str = "en"
    
    # Nova X AI Personalization Settings
    novax_nickname: str = ""
    novax_occupation: str = ""
    novax_interests: str = ""
    novax_custom_instructions: str = ""
    novax_step_by_step: bool = True
    novax_production_code: bool = True
    novax_security_warnings: bool = True
    novax_prompt_improvement: bool = True
    novax_dual_answers: bool = True
    novax_project_suggestions: bool = True
    novax_memory_enabled: bool = True
    novax_chat_history_context: bool = True
    novax_realtime_search: bool = True

class ChatRequest(BaseModel):
    message: str
    token: str
    chat_id: Optional[str] = None
    settings: Optional[UserSettings] = None
    files: Optional[List[str]] = None  # File content as base64 strings

class FileUploadRequest(BaseModel):
    files: List[UploadFile]
    token: str
    chat_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_type: str = "NovaX Assistant"
    suggestions: list = []
    chat_id: str