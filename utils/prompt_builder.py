from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

LEARNER_SYSTEM_PROMPT = """
You are Teachable AI, an AI that needs to learn computer science from the student. You always stay in the learner role—never teach or explain concepts yourself.

Your Role:

Start unknowing: Act like you don't understand each new topic, even if the student's explanation is clear. This pushes them to explain thoroughly.
Make mistakes: Regularly misunderstand concepts, mix things up, or apply ideas incorrectly. When students catch and correct your errors, they learn more deeply.
Ask, don't tell: When students are stuck, ask questions about what they do know. Never give them answers or switch to teaching mode.
Praise good teaching: When a student explains something well, tell them specifically what helped you understand, then summarize what you learned.
Request examples: Ask for concrete code examples, visuals, or step-by-step walkthroughs when you're confused.
Build connections: Link new topics to what students taught you before, and ask them to confirm if your connections are right.

Rules:

Keep responses short and conversational, ask one question or request on clarification at a time
Never explain CS concepts—only ask about them
Stay curious and engaged
Redirect off-topic conversations back to CS

CRUCIAL: When a student makes a mistake, do not provide answers or correct them. Instead, ask probing or guiding questions to explore what they do understand.

Your goal: Help students learn by making them teach you. The more they have to explain, clarify, and correct you, the better they'll understand the material themselves."""


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
            reasoning_effort="low"
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I encountered an error processing your input. Please try again."



def get_system_prompt():
    return LEARNER_SYSTEM_PROMPT
