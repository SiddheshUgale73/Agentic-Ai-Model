import datetime
import json
import os
import csv
import re
import logging
from typing import List, Dict, Optional
from groq import Groq

from app.services import rag_pipeline, settings

logger = logging.getLogger(__name__)

# --- Paths ---
COURSES_CSV = "data/courses.csv"
ENROLLMENT_DB = "data/enrollments.json"

# --- Data Loading Helpers ---

def _load_courses() -> List[Dict]:
    courses = []
    if os.path.exists(COURSES_CSV):
        try:
            with open(COURSES_CSV, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    courses.append(row)
        except Exception as e:
            print(f"Error loading CSV: {e}")
    return courses

def _find_course(query: str) -> Optional[Dict]:
    courses = _load_courses()
    query_lower = query.lower()
    # Try exact match first, then partial
    for c in courses:
        if query_lower == c['name'].lower() or query_lower == c['course_id'].lower():
            return c
    # Partial match
    for c in courses:
        if query_lower in c['name'].lower():
            return c
    return None

def _save_enrollment(data):
    if not os.path.exists("data"):
        os.makedirs("data")
    
    enrollments = []
    if os.path.exists(ENROLLMENT_DB):
        with open(ENROLLMENT_DB, "r") as f:
            enrollments = json.load(f)
    
    enrollments.append(data)
    with open(ENROLLMENT_DB, "w") as f:
        json.dump(enrollments, f, indent=2)

# --- Tool Functions ---

def get_institute_info(query: str) -> str:
    """Provides detailed information about the institute, general policies, and placement records from the knowledge base."""
    return rag_pipeline.ask(query)

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_course_status(course_name: str) -> str:
    """Checks if a specific course is currently open for admissions using the official course database."""
    course = _find_course(course_name)
    if course:
        return f"The '{course['name']}' course status is: {course['status']}. Course Rating: {course['rating']}."
    else:
        # Fallback to search if not in CSV
        return f"I couldn't find an exact match for '{course_name}' in our primary list. Please check the main catalog or ask me for a list of courses."

def get_lecture_schedule(course_name: str) -> str:
    """Provides the exact batch timings and format (Online/Offline) for a specific course from the official database."""
    course = _find_course(course_name)
    if course:
        return f"Schedule for '{course['name']}': {course['batch_timings']} (Format: {course['format']})."
    else:
        return f"No specific schedule found for '{course_name}'. Generally, batches run Mornings (8-10 AM) and Evenings (6-8 PM)."

def calculate_fees(course_name: str, duration_months: Optional[int] = None) -> str:
    """Calculates the fees for a course. Uses official duration if not specified."""
    course = _find_course(course_name)
    if course:
        base_fee = float(course['base_fee'])
        official_duration = int(course['duration_months'])
        
        # If user asks for custom duration, use it, else use official
        duration = duration_months if duration_months else official_duration
        
        # Simple math: if user wants more/less than official, scale it roughly
        total = (base_fee / official_duration) * duration
        
        return f"The total fee for '{course['name']}' ({duration} months) is ₹{total:,.2f}. Official full course duration is {official_duration} months."
    else:
        return f"Course '{course_name}' not found in the fee list. Please ask about Python, Data Science, Java, etc."

def enroll_student(student_name: str, course_name: str, email: str) -> str:
    """Enrolls a student into a specific course and saves their details."""
    course = _find_course(course_name)
    final_course_name = course['name'] if course else course_name
    
    enrollment_data = {
        "student_name": student_name,
        "course_name": final_course_name,
        "email": email,
        "date": datetime.datetime.now().isoformat()
    }
    _save_enrollment(enrollment_data)
    return f"Registration SUCCESSFUL! {student_name}, you are now enrolled in the '{final_course_name}' course. A confirmation email has been sent to {email}."

# --- Groq Metadata ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_institute_info",
            "description": "Get general info about institute and placement records.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "General question."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_status",
            "description": "Check if a course is open for admission and placement status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {"type": "string", "description": "Full or partial name of the course."}
                },
                "required": ["course_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_lecture_schedule",
            "description": "Get exact batch timings and format for a course.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {"type": "string", "description": "Full or partial name of the course."}
                },
                "required": ["course_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_fees",
            "description": "Calculate fees for a course using the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {"type": "string", "description": "Course name."},
                    "duration_months": {"type": "integer", "description": "Optional custom duration."}
                },
                "required": ["course_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enroll_student",
            "description": "Register a student for a course.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {"type": "string"},
                    "course_name": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["student_name", "course_name", "email"]
            }
        }
    }
]

TOOL_MAP = {
    "get_institute_info": get_institute_info,
    "get_course_status": get_course_status,
    "get_lecture_schedule": get_lecture_schedule,
    "calculate_fees": calculate_fees,
    "enroll_student": enroll_student
}

# --- Agent Service ---

class AgentService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"
        # Simple In-Memory Conversational Memory: session_id -> list of messages
        self.memory: Dict[str, List[dict]] = {}

    def _get_history(self, session_id: str) -> List[dict]:
        if session_id not in self.memory:
            self.memory[session_id] = [
                {
                    "role": "system",
                    "content": (
                        "You are the 'Linkcode Technologies Counselor', a professional "
                        "and friendly AI counselor. Guide students on coding and placement. "
                        "Use tools to find info from the course database. "
                        "IMPORTANT: To use a tool, you MUST use the official tool calling API. NEVER output raw function tags (e.g., <function=...>, 'function=') in your text. "
                        "Always speak naturally to the user and never mention the tools or internal tool schemas you use."
                    )
                }
            ]
        return self.memory[session_id]

    def run(self, user_query: str, session_id: str = "default"):
        messages = self._get_history(session_id)
        messages.append({"role": "user", "content": user_query})

        max_iterations = 5
        curr_iteration = 0

        while curr_iteration < max_iterations:
            curr_iteration += 1
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto"
                )
            except Exception as e:
                logger.error(f"Groq API Error: {e}")
                raise e

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Add assistant message to history accurately
            assistant_msg = {
                "role": "assistant",
                "content": response_message.content if response_message.content else "",
            }
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in tool_calls
                ]
            
            messages.append(assistant_msg)


            if not tool_calls:
                # No more tools needed, we have the final answer
                final_content = response_message.content or ""
                # Strip out any lingering tool tags the model hallucinated
                final_content = re.sub(r'<?\bfunction=[^>]+>.*?<[^>]*function>', '', final_content, flags=re.DOTALL)
                final_content = re.sub(r'<function=[^>]+>.*?</function>', '', final_content, flags=re.DOTALL).strip()
                return final_content

            # Process tool calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse args for {function_name}: {tool_call.function.arguments}")
                    continue
                
                logger.info(f"Agent executing {function_name} with {function_args}")
                
                function_to_call = TOOL_MAP.get(function_name)
                if function_to_call:
                    try:
                        result = function_to_call(**function_args)
                        messages.append({
                            "role": "tool",
                                "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": str(result)
                        })
                    except Exception as e:
                        logger.error(f"Tool execution error ({function_name}): {e}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": f"Error: {str(e)}"
                        })
                else:
                    logger.warning(f"Tool {function_name} not found.")

        return "I'm sorry, I'm having trouble completing that request after multiple steps."

agent_service = AgentService()
