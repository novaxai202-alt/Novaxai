import firebase_admin
from firebase_admin import firestore
from models import ChatMessage, ChatSession, UserSettings
from typing import List, Optional
import uuid
import re
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
                messages = db.collection("chat_messages").where(filter=firestore.FieldFilter("chat_id", "==", chat_id)).stream()
                for message in messages:
                    message.reference.delete()
                
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
            message_list.sort(key=lambda x: x.get('timestamp', datetime.min))
            return message_list
        except Exception as e:
            print(f"Error getting chat messages: {e}")
            return []
    
    async def get_all_user_messages(self, user_id: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            messages = db.collection("chat_messages").where(filter=firestore.FieldFilter("user_id", "==", user_id)).stream()
            message_list = [message.to_dict() for message in messages]
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
            default_settings = UserSettings(user_id=user_id).dict()
            db.collection("user_settings").document(user_id).set(default_settings)
            return default_settings
    
    async def update_user_settings(self, user_id: str, settings: dict):
        db = self.get_db()
        if db:
            db.collection("user_settings").document(user_id).update(settings)
    
    # User Memory Management
    async def save_user_memory(self, user_id: str, memory_data: dict):
        db = self.get_db()
        if not db:
            return
        
        try:
            memory_doc = {
                "user_id": user_id,
                "name": memory_data.get("name", ""),
                "occupation": memory_data.get("occupation", ""),
                "background": memory_data.get("background", ""),
                "skills": memory_data.get("skills", ""),
                "goals": memory_data.get("goals", ""),
                "projects": memory_data.get("projects", ""),
                "interests": memory_data.get("interests", ""),
                "learning_path": memory_data.get("learning_path", ""),
                "response_tone": memory_data.get("response_tone", ""),
                "response_format": memory_data.get("response_format", ""),
                "language_style": memory_data.get("language_style", ""),
                "detail_level": memory_data.get("detail_level", ""),
                "use_emojis": memory_data.get("use_emojis", False),
                "code_preference": memory_data.get("code_preference", ""),
                "explanation_style": memory_data.get("explanation_style", ""),
                "context_notes": memory_data.get("context_notes", ""),
                "last_updated": datetime.now(),
                "created_at": memory_data.get("created_at", datetime.now())
            }
            
            db.collection("user_memory").document(user_id).set(memory_doc, merge=True)
            
        except Exception as e:
            print(f"Error saving user memory: {e}")
    
    # 2FA Management
    async def save_2fa_secret(self, user_id: str, secret: str):
        db = self.get_db()
        if db:
            db.collection("user_settings").document(user_id).update({
                "totp_secret": secret,
                "two_factor_enabled": False
            })
    
    async def enable_2fa(self, user_id: str):
        db = self.get_db()
        if db:
            db.collection("user_settings").document(user_id).update({
                "two_factor_enabled": True
            })
    
    async def disable_2fa(self, user_id: str):
        db = self.get_db()
        if db:
            db.collection("user_settings").document(user_id).update({
                "two_factor_enabled": False,
                "totp_secret": None
            })
    
    async def get_2fa_status(self, user_id: str) -> dict:
        db = self.get_db()
        if not db:
            return {"enabled": False, "secret": None}
        
        doc = db.collection("user_settings").document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            return {
                "enabled": data.get("two_factor_enabled", False),
                "secret": data.get("totp_secret")
            }
        return {"enabled": False, "secret": None}
    
    async def get_user_memory(self, user_id: str) -> dict:
        db = self.get_db()
        if not db:
            return {}
        
        try:
            doc = db.collection("user_memory").document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            else:
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
        try:
            message_lower = message.lower().strip()
            current_memory = await self.get_user_memory(user_id)
            
            if any(cmd in message_lower for cmd in ["remember this", "save to memory", "store this"]):
                current_memory["context_notes"] = current_memory.get("context_notes", "") + f"; {message}"
                await self.save_user_memory(user_id, current_memory)
                return
            
            if "my name is" in message_lower:
                name_match = re.search(r"my name is ([^.!?\n]+)", message_lower)
                if name_match:
                    current_memory["name"] = name_match.group(1).strip().title()
                    await self.save_user_memory(user_id, current_memory)
                
        except Exception as e:
            print(f"Error updating user memory: {e}")
    
    async def get_user_context_for_ai(self, user_id: str) -> str:
        memory = await self.get_user_memory(user_id)
        
        about_you = []
        response_style = []
        
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
    
    # Team Workspaces
    async def create_workspace(self, owner_id: str, name: str, description: str = "") -> str:
        workspace_id = str(uuid.uuid4())
        workspace_data = {
            "id": workspace_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        }
        db = self.get_db()
        if db:
            db.collection("workspaces").document(workspace_id).set(workspace_data)
            await self.add_workspace_member(workspace_id, owner_id, "admin")
        return workspace_id
    
    async def get_user_workspaces(self, user_id: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            members = db.collection("workspace_members").where(filter=firestore.FieldFilter("user_id", "==", user_id)).stream()
            workspace_ids = [member.to_dict()["workspace_id"] for member in members]
            
            workspaces = []
            for workspace_id in workspace_ids:
                workspace_doc = db.collection("workspaces").document(workspace_id).get()
                if workspace_doc.exists:
                    workspace_data = workspace_doc.to_dict()
                    member_count = len(list(db.collection("workspace_members").where(filter=firestore.FieldFilter("workspace_id", "==", workspace_id)).stream()))
                    workspace_data["member_count"] = member_count
                    workspaces.append(workspace_data)
            
            return sorted(workspaces, key=lambda x: x.get('updated_at', datetime.min), reverse=True)
        except Exception as e:
            print(f"Error getting user workspaces: {e}")
            return []
    
    async def add_workspace_member(self, workspace_id: str, user_email: str, role: str = "member") -> bool:
        db = self.get_db()
        if not db:
            return False
        try:
            member_data = {
                "workspace_id": workspace_id,
                "user_email": user_email,
                "role": role,
                "joined_at": datetime.now(),
                "is_active": True
            }
            member_id = f"{workspace_id}_{user_email}"
            db.collection("workspace_members").document(member_id).set(member_data)
            return True
        except Exception as e:
            print(f"Error adding workspace member: {e}")
            return False
    
    async def get_workspace_members(self, workspace_id: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            members = db.collection("workspace_members").where(filter=firestore.FieldFilter("workspace_id", "==", workspace_id)).stream()
            return [member.to_dict() for member in members]
        except Exception as e:
            print(f"Error getting workspace members: {e}")
            return []
    
    async def save_workspace_message(self, workspace_id: str, user_id: str, message: str, response: str) -> str:
        message_id = str(uuid.uuid4())
        message_data = {
            "id": message_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "message": message,
            "response": response,
            "timestamp": datetime.now(),
            "message_type": "collaborative"
        }
        db = self.get_db()
        if db:
            db.collection("workspace_messages").document(message_id).set(message_data)
        return message_id
    
    async def get_workspace_messages(self, workspace_id: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            messages = db.collection("workspace_messages").where(filter=firestore.FieldFilter("workspace_id", "==", workspace_id)).stream()
            message_list = [message.to_dict() for message in messages]
            return sorted(message_list, key=lambda x: x.get('timestamp', datetime.min))
        except Exception as e:
            print(f"Error getting workspace messages: {e}")
            return []
    
    # Chat Sharing
    async def create_shared_chat(self, chat_id: str, owner_id: str, share_type: str = "public", recipient_email: str = None, expires_in_days: int = 7) -> str:
        share_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=expires_in_days) if expires_in_days else None
        
        share_data = {
            "id": share_id,
            "chat_id": chat_id,
            "owner_id": owner_id,
            "share_type": share_type,
            "recipient_email": recipient_email,
            "share_url": f"/shared/{share_id}",
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "is_active": True,
            "view_count": 0
        }
        
        db = self.get_db()
        if db:
            db.collection("shared_chats").document(share_id).set(share_data)
        return share_id
    
    async def get_shared_chat(self, share_id: str) -> dict:
        db = self.get_db()
        if not db:
            return None
        try:
            doc = db.collection("shared_chats").document(share_id).get()
            if doc.exists:
                share_data = doc.to_dict()
                if share_data.get("expires_at") and share_data["expires_at"] < datetime.now():
                    return None
                db.collection("shared_chats").document(share_id).update({"view_count": firestore.Increment(1)})
                return share_data
            return None
        except Exception as e:
            print(f"Error getting shared chat: {e}")
            return None
    
    async def get_user_shared_chats(self, user_id: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            shares = db.collection("shared_chats").where(filter=firestore.FieldFilter("owner_id", "==", user_id)).stream()
            share_list = []
            for share in shares:
                share_data = share.to_dict()
                chat_doc = db.collection("chat_sessions").document(share_data["chat_id"]).get()
                if chat_doc.exists:
                    share_data["chat_title"] = chat_doc.to_dict().get("title", "Untitled Chat")
                share_list.append(share_data)
            return sorted(share_list, key=lambda x: x.get('created_at', datetime.min), reverse=True)
        except Exception as e:
            print(f"Error getting user shared chats: {e}")
            return []
    
    async def revoke_shared_chat(self, share_id: str, user_id: str) -> bool:
        db = self.get_db()
        if not db:
            return False
        try:
            doc = db.collection("shared_chats").document(share_id).get()
            if doc.exists and doc.to_dict().get("owner_id") == user_id:
                db.collection("shared_chats").document(share_id).update({"is_active": False})
                return True
            return False
        except Exception as e:
            print(f"Error revoking shared chat: {e}")
            return False
    
    async def get_private_shared_chats_for_user(self, user_email: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            shares = db.collection("shared_chats").where(filter=firestore.FieldFilter("recipient_email", "==", user_email)).where(filter=firestore.FieldFilter("share_type", "==", "private")).stream()
            share_list = []
            for share in shares:
                share_data = share.to_dict()
                if share_data.get("expires_at") and share_data["expires_at"] < datetime.now():
                    continue
                chat_doc = db.collection("chat_sessions").document(share_data["chat_id"]).get()
                if chat_doc.exists:
                    share_data["chat_title"] = chat_doc.to_dict().get("title", "Untitled Chat")
                share_list.append(share_data)
            return sorted(share_list, key=lambda x: x.get('created_at', datetime.min), reverse=True)
        except Exception as e:
            print(f"Error getting private shared chats: {e}")
            return []
    
    # Chat Export
    async def export_chat_markdown(self, chat_id: str, user_id: str) -> str:
        try:
            db = self.get_db()
            if not db:
                return "# Chat Export\n\nError: Database unavailable"
            
            chat_doc = db.collection("chat_sessions").document(chat_id).get()
            if not chat_doc.exists:
                return "# Chat Export\n\nError: Chat not found"
            
            chat_data = chat_doc.to_dict()
            messages = await self.get_chat_messages(chat_id)
            
            markdown = f"# {chat_data.get('title', 'NovaX AI Chat')}\n\n"
            markdown += f"**Created:** {chat_data.get('created_at', 'Unknown').strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            markdown += "---\n\n"
            
            for msg in messages:
                timestamp = msg.get('timestamp', datetime.now()).strftime('%H:%M:%S')
                markdown += f"## [{timestamp}] User\n\n{msg.get('message', '')}\n\n"
                markdown += f"## [{timestamp}] NovaX AI ({msg.get('agent_type', 'Assistant')})\n\n{msg.get('response', '')}\n\n---\n\n"
            
            markdown += "\n*Exported from NovaX AI Platform*"
            return markdown
        except Exception as e:
            print(f"Error exporting chat: {e}")
            return f"# Chat Export\n\nError: {str(e)}"
    
    # User Management
    async def create_user_profile(self, user_id: str, email: str, display_name: str = "") -> bool:
        db = self.get_db()
        if not db:
            return False
        try:
            user_data = {
                "user_id": user_id,
                "email": email,
                "display_name": display_name,
                "created_at": datetime.now(),
                "last_active": datetime.now(),
                "is_active": True
            }
            db.collection("user_profiles").document(user_id).set(user_data, merge=True)
            return True
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False
    
    async def check_user_exists(self, email: str) -> bool:
        db = self.get_db()
        if not db:
            return False
        try:
            users = db.collection("user_profiles").where(filter=firestore.FieldFilter("email", "==", email)).limit(1).stream()
            return len(list(users)) > 0
        except Exception as e:
            print(f"Error checking user exists: {e}")
            return False
    
    async def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        db = self.get_db()
        if not db:
            return False
        try:
            workspace_doc = db.collection("workspaces").document(workspace_id).get()
            if workspace_doc.exists and workspace_doc.to_dict().get("owner_id") == user_id:
                # Delete workspace messages
                messages = db.collection("workspace_messages").where(filter=firestore.FieldFilter("workspace_id", "==", workspace_id)).stream()
                for message in messages:
                    message.reference.delete()
                
                # Delete workspace members
                members = db.collection("workspace_members").where(filter=firestore.FieldFilter("workspace_id", "==", workspace_id)).stream()
                for member in members:
                    member.reference.delete()
                
                # Delete workspace
                db.collection("workspaces").document(workspace_id).delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting workspace: {e}")
            return False
    
    async def update_member_role(self, workspace_id: str, user_email: str, role: str) -> bool:
        db = self.get_db()
        if not db:
            return False
        try:
            member_id = f"{workspace_id}_{user_email}"
            db.collection("workspace_members").document(member_id).update({"role": role})
            return True
        except Exception as e:
            print(f"Error updating member role: {e}")
            return False
    
    async def get_workspace_with_members(self, workspace_id: str) -> dict:
        db = self.get_db()
        if not db:
            return None
        try:
            workspace_doc = db.collection("workspaces").document(workspace_id).get()
            if workspace_doc.exists:
                workspace_data = workspace_doc.to_dict()
                members = await self.get_workspace_members(workspace_id)
                workspace_data["members"] = members
                return workspace_data
            return None
        except Exception as e:
            print(f"Error getting workspace with members: {e}")
            return None
    
    async def create_public_share(self, chat_id: str, user_id: str, expires_in_days: int = 7) -> str:
        return await self.create_shared_chat(chat_id, user_id, "public", None, expires_in_days)
    
    async def get_public_shares(self, user_id: str) -> List[dict]:
        db = self.get_db()
        if not db:
            return []
        try:
            shares = db.collection("shared_chats").where(filter=firestore.FieldFilter("owner_id", "==", user_id)).where(filter=firestore.FieldFilter("share_type", "==", "public")).stream()
            share_list = []
            for share in shares:
                share_data = share.to_dict()
                chat_doc = db.collection("chat_sessions").document(share_data["chat_id"]).get()
                if chat_doc.exists:
                    share_data["chat_title"] = chat_doc.to_dict().get("title", "Untitled Chat")
                share_list.append(share_data)
            return sorted(share_list, key=lambda x: x.get('created_at', datetime.min), reverse=True)
        except Exception as e:
            print(f"Error getting public shares: {e}")
            return []
    
    async def add_share_comment(self, share_id: str, user_id: str, comment: str) -> str:
        comment_id = str(uuid.uuid4())
        comment_data = {
            "id": comment_id,
            "share_id": share_id,
            "user_id": user_id,
            "comment": comment,
            "created_at": datetime.now()
        }
        db = self.get_db()
        if db:
            db.collection("share_comments").document(comment_id).set(comment_data)
        return comment_id

# Global database instance
database = DatabaseManager()
