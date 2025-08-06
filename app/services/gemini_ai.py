import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from app.core.config import get_app_settings


class QuestionData(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: int


class QuizGenerationData(BaseModel):
    title: str
    description: str
    questions: List[QuestionData]


class GeminiAIService:
    def __init__(self):
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError:
            raise ImportError("google-generativeai package is required. Install it with: poetry add google-generativeai")
        
        settings = get_app_settings()
        self.genai.configure(api_key=settings.gemini_api_key.get_secret_value())
        self.model = self.genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_quiz_from_prompt(self, prompt: str, num_questions: int = 5) -> QuizGenerationData:
        """
        Generate a quiz based on the given prompt using Gemini AI
        """
        generation_prompt = f"""
        Create a quiz about: {prompt}
        
        Generate exactly {num_questions} multiple choice questions.
        
        Return ONLY a valid JSON response in this exact format:
        {{
            "title": "Quiz Title",
            "description": "Brief quiz description",
            "questions": [
                {{
                    "question_text": "The question text",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": 0
                }}
            ]
        }}
        
        Requirements:
        - Each question must have exactly 4 options
        - correct_answer must be the index (0-3) of the correct option
        - Make questions challenging but fair
        - Ensure all JSON is properly formatted
        - Do not include any text before or after the JSON
        """
        
        try:
            response = self.model.generate_content(generation_prompt)
            response_text = response.text.strip()
            
            # Remove any markdown formatting if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse the JSON response
            quiz_data = json.loads(response_text)
            
            # Validate and return the data
            return QuizGenerationData(**quiz_data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to generate quiz: {e}")
    
    async def generate_quiz_questions_only(self, topic: str, num_questions: int = 5) -> List[QuestionData]:
        """
        Generate only questions for an existing quiz topic
        """
        quiz_data = await self.generate_quiz_from_prompt(topic, num_questions)
        return quiz_data.questions