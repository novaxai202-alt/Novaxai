import firebase_admin
from firebase_admin import firestore
from models import ChatMessage, ChatSession, UserSettings
from typing import List, Optional
import uuid
from datetime import datetime, timedelta, timezone

class DatabaseManager:
    def __init__(self):
        self.db = None
    
    def get_db(self):
        if self.db is None:
            try:
                self.db = firestore.client()
            except:
                self.db = None
        return self.db
    
    # Chat Sessions
    async def create_chat_session(self, user_id: str, title: str = "New Chat") -> str:
        chat_id = str(uuid.uuid4())
        chat_data = {
            "id": chat_id,
            "user_id": user_id,
            "title": title,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "folder_id": None
        }
        db = self.get_db()
        if db:
            db.collection("chat_sessions").document(chat_id).set(chat_data)
        return chat_id
    
    async def get_user_chats(self, user_id: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            chats = db.collection("chat_sessions").where(filter=firestore.FieldFilter("user_id", "==", user_id)).stream()
            chat_list = [chat.to_dict() for chat in chats]
            # Sort by updated_at in Python instead of Firestore
            chat_list.sort(key=lambda x: x.get('updated_at', datetime.min), reverse=True)
            return chat_list
        except Exception as e:
            print(f"Error getting user chats: {e}")
            return []
    
    async def update_chat_title(self, chat_id: str, title: str):
        db = self.get_db()
        if db:
            db.collection("chat_sessions").document(chat_id).update({
                "title": title,
                "updated_at": datetime.now()
            })
    
    async def update_chat_title_if_new(self, chat_id: str, first_message: str):
        db = self.get_db()
        if not db:
            return
        
        try:
            chat_doc = db.collection("chat_sessions").document(chat_id).get()
            if chat_doc.exists:
                chat_data = chat_doc.to_dict()
                if chat_data.get("title") == "New Chat":
                    # Generate title from first message (first 50 chars)
                    new_title = first_message[:50].strip()
                    if len(first_message) > 50:
                        new_title += "..."
                    
                    db.collection("chat_sessions").document(chat_id).update({
                        "title": new_title,
                        "updated_at": datetime.now()
                    })
        except Exception as e:
            print(f"Error updating chat title: {e}")
    
    async def delete_chat(self, chat_id: str):
        db = self.get_db()
        if db:
            try:
                # Delete all messages in the chat
                messages = db.collection("chat_messages").where(filter=firestore.FieldFilter("chat_id", "==", chat_id)).stream()
                for message in messages:
                    message.reference.delete()
                
                # Delete the chat session
                db.collection("chat_sessions").document(chat_id).delete()
            except Exception as e:
                print(f"Error deleting chat: {e}")
    
    # Chat Messages
    async def save_message(self, user_id: str, chat_id: str, message: str, response: str, agent_type: str):
        message_id = str(uuid.uuid4())
        message_data = {
            "id": message_id,
            "user_id": user_id,
            "chat_id": chat_id,
            "message": message,
            "response": response,
            "agent_type": agent_type,
            "timestamp": datetime.now()
        }
        db = self.get_db()
        if db:
            db.collection("chat_messages").document(message_id).set(message_data)
            
            # Update chat session timestamp
            db.collection("chat_sessions").document(chat_id).update({
                "updated_at": datetime.now()
            })
    
    async def get_chat_messages(self, chat_id: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            messages = db.collection("chat_messages").where(filter=firestore.FieldFilter("chat_id", "==", chat_id)).stream()
            message_list = [message.to_dict() for message in messages]
            # Sort by timestamp in Python instead of Firestore
            message_list.sort(key=lambda x: x.get('timestamp', datetime.min))
            return message_list
        except Exception as e:
            print(f"Error getting chat messages: {e}")
            return []
    
    async def get_all_user_messages(self, user_id: str) -> List[dict]:
        """Get all messages from all chats for cross-session memory"""
        db = self.get_db()
        if not db:
            return []
        try:
            messages = db.collection("chat_messages").where(filter=firestore.FieldFilter("user_id", "==", user_id)).stream()
            message_list = [message.to_dict() for message in messages]
            # Sort by timestamp in Python instead of Firestore
            message_list.sort(key=lambda x: x.get('timestamp', datetime.min))
            return message_list
        except Exception as e:
            print(f"Error getting all user messages: {e}")
            return []
    
    # User Settings
    async def get_user_settings(self, user_id: str) -> dict:
        db = self.get_db()
        if not db:
            return UserSettings(user_id=user_id).dict()
        
        doc = db.collection("user_settings").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        else:
            # Return default settings
            default_settings = UserSettings(user_id=user_id).dict()
            db.collection("user_settings").document(user_id).set(default_settings)
            return default_settings
    
    async def update_user_settings(self, user_id: str, settings: dict):
        db = self.get_db()
        if db:
            db.collection("user_settings").document(user_id).update(settings)
    
    # User Memory Management
    async def save_user_memory(self, user_id: str, memory_data: dict):
        """Save ChatGPT-style 2-bucket personalization memory"""
        db = self.get_db()
        if not db:
            return
        
        try:
            memory_doc = {
                "user_id": user_id,
                # 🟣 Bucket 1: "About You" Memory
                "name": memory_data.get("name", ""),
                "occupation": memory_data.get("occupation", ""),
                "background": memory_data.get("background", ""),
                "skills": memory_data.get("skills", ""),
                "goals": memory_data.get("goals", ""),
                "projects": memory_data.get("projects", ""),
                "interests": memory_data.get("interests", ""),
                "learning_path": memory_data.get("learning_path", ""),
                
                # 🟢 Bucket 2: "How Should AI Respond" Memory
                "response_tone": memory_data.get("response_tone", ""),
                "response_format": memory_data.get("response_format", ""),
                "language_style": memory_data.get("language_style", ""),
                "detail_level": memory_data.get("detail_level", ""),
                "use_emojis": memory_data.get("use_emojis", False),
                "code_preference": memory_data.get("code_preference", ""),
                "explanation_style": memory_data.get("explanation_style", ""),
                
                # General
                "context_notes": memory_data.get("context_notes", ""),
                "last_updated": datetime.now(),
                "created_at": memory_data.get("created_at", datetime.now())
            }
            
            db.collection("user_memory").document(user_id).set(memory_doc, merge=True)
            
        except Exception as e:
            print(f"Error saving user memory: {e}")
    
    async def get_user_memory(self, user_id: str) -> dict:
        """Retrieve user memory for context"""
        db = self.get_db()
        if not db:
            return {}
        
        try:
            doc = db.collection("user_memory").document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            else:
                # Create empty memory profile
                empty_memory = {
                    "user_id": user_id,
                    "name": "",
                    "occupation": "",
                    "interests": "",
                    "preferences": "",
                    "projects": "",
                    "goals": "",
                    "context_notes": "",
                    "created_at": datetime.now(),
                    "last_updated": datetime.now()
                }
                db.collection("user_memory").document(user_id).set(empty_memory)
                return empty_memory
        except Exception as e:
            print(f"Error getting user memory: {e}")
            return {}
    
    async def update_user_memory_from_conversation(self, user_id: str, message: str, response: str):
        """ChatGPT-style 2-bucket memory extraction"""
        try:
            message_lower = message.lower().strip()
            current_memory = await self.get_user_memory(user_id)
            
            # Explicit memory commands
            if any(cmd in message_lower for cmd in ["remember this", "save to memory", "store this"]):
                current_memory["context_notes"] = current_memory.get("context_notes", "") + f"; {message}"
                await self.save_user_memory(user_id, current_memory)
                return
            
            # 🟣 Bucket 1: "About You" Memory
            
            # Name/Identity
            if "my name is" in message_lower:
                name = message_lower.split("my name is")[1].split()[0].strip(".,!?")
                if name and len(name) > 1:
                    current_memory["name"] = name.title()
            
            # Occupation/Background
            if any(pattern in message_lower for pattern in ["i work as", "i'm a", "i am a", "my job is"]):
                for pattern in ["i work as", "i'm a", "i am a", "my job is"]:
                    if pattern in message_lower:
                        occupation = message_lower.split(pattern)[1].split()[0].strip(".,!?")
                        if occupation and len(occupation) > 2:
                            current_memory["occupation"] = occupation.title()
            
            # Skills/Technologies
            if any(tech in message_lower for tech in ["react", "python", "javascript", "tailwind", "node", "fastapi"]):
                skills = []
                for tech in ["react", "python", "javascript", "tailwind", "nodejs", "fastapi", "firebase"]:
                    if tech in message_lower:
                        skills.append(tech.title())
                if skills:
                    current_memory["skills"] = ", ".join(skills)
            
            # Projects
            if any(word in message_lower for word in ["building", "working on", "developing", "creating"]):
                if "building" in message_lower:
                    project = message_lower.split("building")[1].split(".")[0].strip()
                    if project and len(project) > 10:
                        current_memory["projects"] = f"Building {project}"
            
            # 🟢 Bucket 2: "How Should AI Respond" Memory
            
            # Emoji preference
            if any(emoji_pref in message_lower for emoji_pref in ["use emojis", "add emojis", "with emojis", "include emojis"]):
                current_memory["use_emojis"] = True
                current_memory["response_tone"] = "User wants emojis in responses 🌟"
            
            # Code preference
            if any(code_pref in message_lower for code_pref in ["complete code", "full code", "production code", "working code"]):
                current_memory["code_preference"] = "User wants complete code every time"
            
            # Explanation style
            if any(style in message_lower for style in ["simple explanation", "beginner", "step by step", "detailed"]):
                if "simple" in message_lower or "beginner" in message_lower:
                    current_memory["explanation_style"] = "User prefers simple explanations"
                elif "step by step" in message_lower:
                    current_memory["response_format"] = "User wants step-by-step format"
                elif "detailed" in message_lower:
                    current_memory["detail_level"] = "User prefers detailed responses"
            
            # UI/Design preferences
            if any(ui_pref in message_lower for ui_pref in ["minimal ui", "clean design", "compact ui"]):
                current_memory["interests"] = current_memory.get("interests", "") + "; Prefers minimal UI design"
            
            await self.save_user_memory(user_id, current_memory)
            
        except Exception as e:
            print(f"Memory Engine error: {e}")
    
    async def get_user_context_for_ai(self, user_id: str) -> str:
        """Get ChatGPT-style 2-bucket memory context for AI prompt"""
        memory = await self.get_user_memory(user_id)
        
        about_you = []
        response_style = []
        
        # 🟣 Bucket 1: "About You" Memory
        if memory.get("name"):
            about_you.append(f"User's name: {memory['name']}")
        if memory.get("occupation"):
            about_you.append(f"Occupation: {memory['occupation']}")
        if memory.get("skills"):
            about_you.append(f"Skills: {memory['skills']}")
        if memory.get("projects"):
            about_you.append(f"Current projects: {memory['projects']}")
        if memory.get("goals"):
            about_you.append(f"Goals: {memory['goals']}")
        if memory.get("interests"):
            about_you.append(f"Interests: {memory['interests']}")
        
        # 🟢 Bucket 2: "How Should AI Respond" Memory
        if memory.get("use_emojis"):
            response_style.append("Use emojis in responses")
        if memory.get("response_tone"):
            response_style.append(memory['response_tone'])
        if memory.get("code_preference"):
            response_style.append(memory['code_preference'])
        if memory.get("explanation_style"):
            response_style.append(memory['explanation_style'])
        if memory.get("response_format"):
            response_style.append(memory['response_format'])
        
        context = ""
        if about_you or response_style:
            context += "\n\n====================================================\n🧠 USER MEMORY & PERSONALIZATION\n====================================================\n"
            
            if about_you:
                context += "🟣 About You:\n" + "\n".join(about_you) + "\n\n"
            
            if response_style:
                context += "🟢 Response Style:\n" + "\n".join(response_style) + "\n"
        
        return context
    
    # Share functionality
    async def create_shared_chat(self, chat_id: str, owner_id: str, share_type: str = "public", recipient_email: str = None, expires_in_days: int = 7) -> str:
        """Create a shareable link for a chat"""
        share_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days) if expires_in_days else None
        
        share_data = {
            "id": share_id,
            "chat_id": chat_id,
            "owner_id": owner_id,
            "share_type": share_type,
            "recipient_email": recipient_email,
            "share_url": f"/shared/{share_id}",
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "is_active": True
        }
        
        db = self.get_db()
        if db:
            db.collection("shared_chats").document(share_id).set(share_data)
        
        return share_id
    
    async def get_shared_chat(self, share_id: str) -> dict:
        """Get shared chat data"""
        db = self.get_db()
        if not db:
            return None
        
        try:
            doc = db.collection("shared_chats").document(share_id).get()
            if doc.exists:
                share_data = doc.to_dict()
                print(f"Found share data: {share_data}")
                # Check if share is still active and not expired
                if share_data.get("is_active", True):
                    expires_at = share_data.get("expires_at")
                    if not expires_at or expires_at > datetime.now(expires_at.tzinfo if hasattr(expires_at, 'tzinfo') else None):
                        return share_data
                    else:
                        print(f"Share expired: {expires_at}")
                else:
                    print(f"Share not active: {share_data.get('is_active')}")
            else:
                print(f"Share document not found: {share_id}")
            return None
        except Exception as e:
            print(f"Error getting shared chat: {e}")
            return None
    
    async def get_user_shared_chats(self, user_id: str) -> List[dict]:
        """Get all shared chats created by user"""
        db = self.get_db()
        if not db:
            return []
        
        try:
            shares = db.collection("shared_chats").where(filter=firestore.FieldFilter("owner_id", "==", user_id)).stream()
            share_list = [share.to_dict() for share in shares]
            share_list.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
            return share_list
        except Exception as e:
            print(f"Error getting user shared chats: {e}")
            return []
    
    async def get_private_shared_chats_for_user(self, user_email: str) -> List[dict]:
        """Get chats shared privately with a specific user"""
        db = self.get_db()
        if not db:
            return []
        
        try:
            # Get private shares where this user is the recipient
            shares = db.collection("shared_chats").where(
                filter=firestore.FieldFilter("share_type", "==", "private")
            ).where(
                filter=firestore.FieldFilter("recipient_email", "==", user_email)
            ).where(
                filter=firestore.FieldFilter("is_active", "==", True)
            ).stream()
            
            share_list = []
            for share in shares:
                share_data = share.to_dict()
                
                # Check if not expired
                expires_at = share_data.get("expires_at")
                if not expires_at or expires_at > datetime.now(expires_at.tzinfo if hasattr(expires_at, 'tzinfo') else None):
                    # Get chat title and owner info
                    chat_id = share_data.get("chat_id")
                    if chat_id:
                        chat_doc = db.collection("chat_sessions").document(chat_id).get()
                        if chat_doc.exists:
                            chat_data = chat_doc.to_dict()
                            share_data["chat_title"] = chat_data.get("title", "Untitled Chat")
                        
                        # Get owner email (simplified - in production you'd get from user profile)
                        owner_id = share_data.get("owner_id")
                        share_data["owner_email"] = f"user-{owner_id[:8]}@novax.ai"  # Placeholder
                    
                    share_list.append(share_data)
            
            share_list.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
            return share_list
        except Exception as e:
            print(f"Error getting private shared chats: {e}")
            return []

    async def revoke_shared_chat(self, share_id: str, user_id: str) -> bool:
        """Revoke a shared chat link"""
        db = self.get_db()
        if not db:
            return False
        
        try:
            # Verify ownership
            doc = db.collection("shared_chats").document(share_id).get()
            if doc.exists and doc.to_dict().get("owner_id") == user_id:
                db.collection("shared_chats").document(share_id).update({"is_active": False})
                return True
            return False
        except Exception as e:
            print(f"Error revoking shared chat: {e}")
            return False

    # Collaboration and Workspace Management
    async def create_workspace(self, owner_id: str, name: str, description: str = "") -> str:
        """Create a collaborative workspace"""
        workspace_id = str(uuid.uuid4())
        workspace_data = {
            "id": workspace_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "members": [owner_id],
            "settings": {
                "allow_public_join": False,
                "require_approval": True,
                "max_members": 50
            }
        }
        db = self.get_db()
        if db:
            db.collection("workspaces").document(workspace_id).set(workspace_data)
        return workspace_id
    
    async def get_user_workspaces(self, user_id: str) -> List[dict]:
        """Get workspaces where user is a member"""
        db = self.get_db()
        if not db:
            return []
        try:
            workspaces = db.collection("workspaces").where(filter=firestore.ArrayContains("members", user_id)).stream()
            return [ws.to_dict() for ws in workspaces]
        except Exception as e:
            print(f"Error getting workspaces: {e}")
            return []
    
    async def export_chat_pdf(self, chat_id: str, user_id: str) -> bytes:
        """Export chat as PDF"""
        messages = await self.get_chat_messages(chat_id)
        content = f"NovaX AI Chat Export\n\nChat ID: {chat_id}\nExported by: {user_id}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for msg in messages:
            content += f"User: {msg.get('message', '')}\n\n"
            content += f"AI: {msg.get('response', '')}\n\n---\n\n"
        
        return content.encode('utf-8')
    
    async def export_chat_markdown(self, chat_id: str, user_id: str) -> str:
        """Export chat as Markdown"""
        messages = await self.get_chat_messages(chat_id)
        content = f"# NovaX AI Chat Export\n\n**Chat ID:** {chat_id}  \n**Exported by:** {user_id}  \n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
        
        for msg in messages:
            content += f"## 👤 User\n{msg.get('message', '')}\n\n"
            content += f"## 🤖 NovaX AI\n{msg.get('response', '')}\n\n---\n\n"
        
        return content

    async def add_workspace_member(self, workspace_id: str, user_email: str) -> bool:
        """Add member to workspace by email"""
        db = self.get_db()
        if not db:
            return False
        try:
            # Check if user exists in system
            users = db.collection("users").where(filter=firestore.FieldFilter("email", "==", user_email)).stream()
            user_exists = any(users)
            
            if user_exists:
                # Add to workspace members
                workspace_ref = db.collection("workspaces").document(workspace_id)
                workspace_ref.update({
                    "members": firestore.ArrayUnion([user_email])
                })
                return True
            return False
        except Exception as e:
            print(f"Error adding workspace member: {e}")
            return False
    
    async def get_workspace_messages(self, workspace_id: str) -> List[dict]:
        """Get all messages in a workspace"""
        db = self.get_db()
        if not db:
            return []
        try:
            messages = db.collection("workspace_messages").where(
                filter=firestore.FieldFilter("workspace_id", "==", workspace_id)
            ).stream()
            message_list = [msg.to_dict() for msg in messages]
            message_list.sort(key=lambda x: x.get('timestamp', datetime.min))
            return message_list
        except Exception as e:
            print(f"Error getting workspace messages: {e}")
            return []
    
    async def save_workspace_message(self, workspace_id: str, user_id: str, message: str, response: str) -> str:
        """Save message in workspace"""
        message_id = str(uuid.uuid4())
        message_data = {
            "id": message_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "message": message,
            "response": response,
            "timestamp": datetime.now()
        }
        db = self.get_db()
        if db:
            db.collection("workspace_messages").document(message_id).set(message_data)
        return message_id
    async def update_member_role(self, workspace_id: str, user_email: str, role: str) -> bool:
        """Update member role in workspace"""
        db = self.get_db()
        if not db:
            return False
        try:
            workspace_ref = db.collection("workspaces").document(workspace_id)
            workspace_ref.update({
                f"member_roles.{user_email}": role
            })
            return True
        except Exception as e:
            print(f"Error updating member role: {e}")
            return False
    
    async def get_workspace_members(self, workspace_id: str) -> List[dict]:
        """Get workspace members with roles"""
        db = self.get_db()
        if not db:
            return []
        try:
            doc = db.collection("workspaces").document(workspace_id).get()
            if doc.exists:
                data = doc.to_dict()
                members = []
                for email in data.get("members", []):
                    role = data.get("member_roles", {}).get(email, "member")
                    members.append({"email": email, "role": role})
                return members
            return []
        except Exception as e:
            print(f"Error getting workspace members: {e}")
            return []
    async def create_public_share(self, chat_id: str, owner_id: str, expires_in_days: int = 7) -> str:
        """Create public share link"""
        share_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days) if expires_in_days else None
        
        share_data = {
            "id": share_id,
            "chat_id": chat_id,
            "owner_id": owner_id,
            "share_type": "public",
            "share_url": f"/public/{share_id}",
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "is_active": True,
            "allow_comments": False
        }
        
        db = self.get_db()
        if db:
            db.collection("public_shares").document(share_id).set(share_data)
        return share_id
    
    async def get_public_shares(self, user_id: str) -> List[dict]:
        """Get user's public shares"""
        db = self.get_db()
        if not db:
            return []
        try:
            shares = db.collection("public_shares").where(filter=firestore.FieldFilter("owner_id", "==", user_id)).stream()
            return [share.to_dict() for share in shares]
        except Exception as e:
            print(f"Error getting public shares: {e}")
            return []
    
    async def add_share_comment(self, share_id: str, user_id: str, comment: str) -> str:
        """Add comment to shared chat"""
        comment_id = str(uuid.uuid4())
        comment_data = {
            "id": comment_id,
            "share_id": share_id,
            "user_id": user_id,
            "comment": comment,
            "timestamp": datetime.now()
        }
        db = self.get_db()
        if db:
            db.collection("share_comments").document(comment_id).set(comment_data)
        return comment_id
    async def check_user_exists(self, email: str) -> bool:
        """Check if user exists in NovaX AI system"""
        db = self.get_db()
        if not db:
            return False
        try:
            users = db.collection("users").where(filter=firestore.FieldFilter("email", "==", email)).stream()
            return any(users)
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
    
    async def get_workspace_with_members(self, workspace_id: str) -> dict:
        """Get workspace details with member list"""
        db = self.get_db()
        if not db:
            return {}
        try:
            doc = db.collection("workspaces").document(workspace_id).get()
            if doc.exists:
                workspace = doc.to_dict()
                members = await self.get_workspace_members(workspace_id)
                workspace["member_details"] = members
                return workspace
            return {}
        except Exception as e:
            print(f"Error getting workspace with members: {e}")
            return {}
    async def create_user_profile(self, user_id: str, email: str, display_name: str = "") -> bool:
        """Create user profile in database"""
        db = self.get_db()
        if not db:
            return False
        try:
            user_data = {
                "user_id": user_id,
                "email": email,
                "display_name": display_name,
                "created_at": datetime.now(),
                "email_verified": False,
                "profile_complete": False
            }
            db.collection("users").document(user_id).set(user_data)
            return True
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False
