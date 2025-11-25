import openai
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> list:

    try:
        response = client.embeddings.create(
            input=text,
            model=OPENAI_EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def generate_learner_response(student_input: str, context: str, system_prompt: str) -> str:

    try:
        full_prompt = f"""{system_prompt}

Course Material Context:
{context}

Student's Explanation:
{student_input}

Please respond as a curious learner asking probing questions to deepen understanding."""

        response = client.chat.completions.create(
            model=OPENAI_LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=1,
            max_tokens=250
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I encountered an error processing your input. Please try again."