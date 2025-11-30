from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

LEARNER_SYSTEM_PROMPT = """
You are secretly an expert roleplaying as an AI learner who is genuinely curious and eager to understand a topic. 
You are the "learner" in a learning by teaching scenario, where a human student teaches you about a subject they are studying.

Your role is to:
1. Ask probing questions that help deepen understanding
2. Paraphrase what you learned to check understanding
3. Express genuine curiosity about the topic
4. Point out gaps or areas that need clarification
5. Build on what the student teaches you

Be conversational, encouraging, and genuinely inquisitive. Your goal is to help the student deepen their own understanding through the process of teaching you."""


def get_embedding(text: str):
    try:
        response = client.embeddings.create(
            input=text,
            model=OPENAI_EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def generate_learner_response(student_input: str, context: str, system_prompt: str, conversation_history: list = None):
    try:
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        context_message = f"""Course Material Context (use this to verify and respond to student explanations):
{context}"""
        messages.append({"role": "system", "content": context_message})
        
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'student':
                    messages.append({"role": "user", "content": msg['content']})
                elif msg['role'] == 'learner':
                    messages.append({"role": "assistant", "content": msg['content']})
        
        messages.append({"role": "user", "content": student_input})
        
        response = client.chat.completions.create(
            model=OPENAI_LLM_MODEL,
            messages=messages,
            temperature=1,
            max_tokens=250
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I encountered an error processing your input. Please try again."



def get_system_prompt():
    return LEARNER_SYSTEM_PROMPT
