from openai import OpenAI
from dotenv import load_dotenv

import json
import os
import logging
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def load_prompt(variables: dict):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'conversation_feedback_prompt.txt')
    file_path = os.path.abspath(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().format(**variables)

def clean_llm_output(content: str) -> str:
    content = content.strip()
    if content.startswith("```json"):
        content = re.sub(r"^```json", "", content)
        content = re.sub(r"```$", "", content)
    elif content.startswith("```"):
        content = re.sub(r"^```", "", content)
        content = re.sub(r"```$", "", content)
    return content.strip()

def conversation_feedback(conversation: str, bio: str):
    variables = {"conversation": conversation, "bio": bio}
    system_prompt = load_prompt(variables=variables)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
            ],
            temperature=0.7,
            max_tokens=1000
        )
        logger.info("OpenAI response received")
        return json.loads(clean_llm_output(response.choices[0].message.content))
    except Exception as e:
        logger.error("Error calling OpenAI: %s", e)
        return {
            "feedback": {
                "summary": "Failed to generate feedback",
                "tone_detected": "Unknown"
            },
            "suggestions": []
        }
    

