"""Service for generating quiz questions using Together AI SDK."""
import os
import sys
from typing import List, Dict, Any

# Import Together SDK
from together import Together

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TOGETHER_API_KEY

class LLMService:
    """Service for generating quiz content using LLM with Together SDK."""
    
    def __init__(self, model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"):
        """Initialize LLM service with Together.ai SDK."""
        self.model = model
        self.client = Together(api_key=TOGETHER_API_KEY)
        
    def generate_questions(self, topic: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate multiple-choice questions for a given topic."""
        if not self.client:
            raise ValueError("Together API client could not be initialized.")
        
        # Create prompt for question generation
        system_prompt = "You are an expert quiz creator. Create clear, accurate multiple-choice questions."
        user_prompt = self._create_question_prompt(topic, num_questions, difficulty)
        
        try:
            # Make API request using the SDK
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2048,
                temperature=0.7,
                top_p=0.9,
                stop=["===END==="]
            )
            
            # Parse response
            generated_text = response.choices[0].message.content
            return self._parse_questions(generated_text)
            
        except Exception as e:
            print(f"Failed to generate questions: {e}")
            return []
    
    def _create_question_prompt(self, topic: str, num_questions: int, difficulty: str) -> str:
        """Create prompt for question generation."""
        difficulty_descriptions = {
            "easy": "basic understanding of the topic, suitable for beginners",
            "medium": "moderate understanding of the topic, covering intermediate concepts",
            "hard": "deep understanding of the topic, including advanced concepts"
        }
        
        difficulty_desc = difficulty_descriptions.get(difficulty, difficulty_descriptions["medium"])
        
        prompt = f"""
Generate {num_questions} multiple-choice questions about {topic} with {difficulty} difficulty ({difficulty_desc}).

For each question, provide:
1. The question text
2. Four possible answers (A, B, C, D format)
3. The correct answer letter
4. A brief explanation of why that answer is correct

Format each question as follows:

Q: [Question text]
A: [Option A]
B: [Option B]
C: [Option C]
D: [Option D]
CORRECT: [Correct answer letter]
EXPLANATION: [Brief explanation]

Remember to make the incorrect options plausible to ensure the quiz is challenging.

===START===
        """
        
        return prompt
    
    def _parse_questions(self, text: str) -> List[Dict[str, Any]]:
        """Parse generated text into structured question data."""
        questions = []
        
        try:
            # Split text by question markers
            parts = text.split("Q: ")
            
            # Skip the first part if empty
            if not parts[0].strip():
                parts = parts[1:]
            else:
                parts[0] = "Q: " + parts[0]
            
            for part in parts:
                if not part.strip():
                    continue
                
                # Initialize question object
                question = {
                    "text": "",
                    "options": [],
                    "correct_answer": None,
                    "explanation": ""
                }
                
                # Extract question text
                question_parts = part.split("A: ")
                if len(question_parts) < 2:
                    continue
                
                question["text"] = question_parts[0].replace("Q: ", "").strip()
                
                # Extract options and other details
                remaining = "A: " + question_parts[1]
                
                # Option A
                option_parts = remaining.split("B: ")
                if len(option_parts) < 2:
                    continue
                option_a = option_parts[0].replace("A: ", "").strip()
                question["options"].append({"text": option_a, "is_correct": False})
                
                # Option B
                remaining = "B: " + option_parts[1]
                option_parts = remaining.split("C: ")
                if len(option_parts) < 2:
                    continue
                option_b = option_parts[0].replace("B: ", "").strip()
                question["options"].append({"text": option_b, "is_correct": False})
                
                # Option C
                remaining = "C: " + option_parts[1]
                option_parts = remaining.split("D: ")
                if len(option_parts) < 2:
                    continue
                option_c = option_parts[0].replace("C: ", "").strip()
                question["options"].append({"text": option_c, "is_correct": False})
                
                # Option D and the rest
                remaining = "D: " + option_parts[1]
                option_parts = remaining.split("CORRECT: ")
                if len(option_parts) < 2:
                    continue
                option_d = option_parts[0].replace("D: ", "").strip()
                question["options"].append({"text": option_d, "is_correct": False})
                
                # Correct answer and explanation
                remaining = "CORRECT: " + option_parts[1]
                answer_parts = remaining.split("EXPLANATION: ")
                if len(answer_parts) < 2:
                    continue
                
                correct_letter = answer_parts[0].replace("CORRECT: ", "").strip()
                question["explanation"] = answer_parts[1].strip()
                
                # Mark correct answer
                letter_to_index = {"A": 0, "B": 1, "C": 2, "D": 3}
                if correct_letter in letter_to_index:
                    correct_index = letter_to_index[correct_letter]
                    if correct_index < len(question["options"]):
                        question["options"][correct_index]["is_correct"] = True
                        question["correct_answer"] = correct_letter
                
                questions.append(question)
                
            return questions
            
        except Exception as e:
            print(f"Error parsing questions: {e}")
            return []