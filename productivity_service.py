import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

class ProductivityService:
    def __init__(self):
        self.todo_patterns = [
            r'(?:need to|should|must|have to|remember to|don\'t forget to)\s+(.+)',
            r'(?:todo|task|action item):\s*(.+)',
            r'(?:i need to|i should|i must)\s+(.+)',
            r'(?:let\'s|we should|we need to)\s+(.+)',
            r'(?:schedule|plan|book|arrange)\s+(.+)',
        ]
        
        self.calendar_patterns = [
            r'(?:schedule|book|arrange|set up|plan)\s+(?:a\s+)?(?:meeting|call|appointment|session)\s+(.+)',
            r'(?:meet|call|talk)\s+(?:with\s+)?(.+?)\s+(?:on|at|tomorrow|next week|this week)',
            r'(?:meeting|appointment|call)\s+(?:with\s+)?(.+?)\s+(?:at|on)\s+(.+)',
        ]

    def extract_todos_from_conversation(self, user_message: str, ai_response: str) -> List[Dict[str, Any]]:
        """Extract actionable todos from conversation"""
        todos = []
        
        # Check user message
        for pattern in self.todo_patterns:
            matches = re.findall(pattern, user_message, re.IGNORECASE)
            for match in matches:
                todos.append({
                    'id': f"todo_{len(todos)}_{int(datetime.now().timestamp())}",
                    'title': match.strip(),
                    'source': 'user_message',
                    'priority': 'medium',
                    'status': 'pending',
                    'created_at': datetime.now().isoformat(),
                    'due_date': None
                })
        
        # Check AI response for suggested actions
        ai_actions = re.findall(r'(?:you should|consider|recommend|suggest)\s+(.+?)(?:\.|$)', ai_response, re.IGNORECASE)
        for action in ai_actions:
            if len(action.strip()) > 10:  # Filter out short matches
                todos.append({
                    'id': f"todo_{len(todos)}_{int(datetime.now().timestamp())}",
                    'title': f"Consider: {action.strip()}",
                    'source': 'ai_suggestion',
                    'priority': 'low',
                    'status': 'pending',
                    'created_at': datetime.now().isoformat(),
                    'due_date': None
                })
        
        return todos

    def extract_calendar_events_from_conversation(self, user_message: str, ai_response: str) -> List[Dict[str, Any]]:
        """Extract calendar events from conversation"""
        events = []
        
        for pattern in self.calendar_patterns:
            matches = re.findall(pattern, user_message, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    title = match[0].strip()
                    time_info = match[1].strip() if len(match) > 1 else "TBD"
                else:
                    title = match.strip()
                    time_info = "TBD"
                
                events.append({
                    'id': f"event_{len(events)}_{int(datetime.now().timestamp())}",
                    'title': title,
                    'description': f"Extracted from conversation",
                    'start_time': time_info,
                    'duration': '1 hour',
                    'type': 'meeting',
                    'status': 'suggested',
                    'created_at': datetime.now().isoformat()
                })
        
        return events

    def create_note_from_response(self, user_message: str, ai_response: str, category: str = 'general') -> Dict[str, Any]:
        """Create a note from AI response"""
        # Extract key points from AI response
        key_points = []
        
        # Look for bullet points or numbered lists
        bullet_points = re.findall(r'[•\-\*]\s*(.+)', ai_response)
        numbered_points = re.findall(r'\d+\.\s*(.+)', ai_response)
        
        key_points.extend(bullet_points)
        key_points.extend(numbered_points)
        
        # If no structured points, take first few sentences
        if not key_points:
            sentences = re.split(r'[.!?]+', ai_response)
            key_points = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        return {
            'id': f"note_{int(datetime.now().timestamp())}",
            'title': user_message[:50] + "..." if len(user_message) > 50 else user_message,
            'content': ai_response,
            'key_points': key_points[:5],  # Max 5 key points
            'category': category,
            'tags': self._extract_tags(user_message + " " + ai_response),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'is_favorite': False
        }

    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        # Common tech/business keywords
        tag_keywords = [
            'api', 'database', 'frontend', 'backend', 'react', 'python', 'javascript',
            'meeting', 'project', 'task', 'deadline', 'client', 'team', 'code',
            'bug', 'feature', 'deployment', 'testing', 'design', 'ui', 'ux'
        ]
        
        text_lower = text.lower()
        found_tags = []
        
        for keyword in tag_keywords:
            if keyword in text_lower:
                found_tags.append(keyword)
        
        return found_tags[:5]  # Max 5 tags

    def analyze_productivity_insights(self, todos: List[Dict], events: List[Dict], notes: List[Dict]) -> Dict[str, Any]:
        """Generate productivity insights"""
        return {
            'total_todos': len(todos),
            'pending_todos': len([t for t in todos if t['status'] == 'pending']),
            'completed_todos': len([t for t in todos if t['status'] == 'completed']),
            'total_events': len(events),
            'upcoming_events': len([e for e in events if e['status'] == 'confirmed']),
            'total_notes': len(notes),
            'recent_notes': len([n for n in notes if datetime.fromisoformat(n['created_at']) > datetime.now() - timedelta(days=7)]),
            'productivity_score': min(100, (len([t for t in todos if t['status'] == 'completed']) * 10) + (len(notes) * 5)),
            'suggestions': [
                "Review pending tasks daily",
                "Set specific deadlines for todos",
                "Organize notes by categories"
            ]
        }
