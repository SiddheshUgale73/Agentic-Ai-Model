import json
import logging
import re
from typing import Dict, List
from groq import Groq
from app.core.config import settings
from app.agent.tools import TOOLS, TOOL_MAP

logger = logging.getLogger(__name__)

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
                        "IMPORTANT: NEVER output raw function tags (e.g., <function=...>) in your conversation text. "
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
                # Strip out any lingering <function=...></function> tags the model hallucinated
                final_content = re.sub(r'<function=[^>]+>.*?</function>', '', final_content).strip()
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
