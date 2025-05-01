"""Service for quiz management and operations."""
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from services.llm_service import LLMService

class QuizService:
    """Service for managing quizzes."""
    
    def __init__(self):
        """Initialize quiz service."""
        self.db_manager = DatabaseManager()
        self.llm_service = LLMService()
    
    def create_topic(self, name, description, user_id):
        """Create a new topic."""
        try:
            # Check if topic already exists
            topics = self.db_manager.get_all_topics()
            if any(topic.name.lower() == name.lower() for topic in topics):
                return False, "Topic already exists."
            
            topic_id = self.db_manager.create_topic(name, description, user_id)
            return True, topic_id
        except Exception as e:
            return False, str(e)
    
    def get_all_topics(self):
        """Get all available topics."""
        return self.db_manager.get_all_topics()
    
    def create_quiz(self, topic_id, user_id, title, num_questions=5, difficulty="medium", time_limit=600):
        """Create a new quiz with auto-generated questions."""
        try:
            # Get topic name
            topic = self.db_manager.get_topic_by_id(topic_id)
            if not topic:
                return False, "Topic not found."
            
            # Create quiz
            quiz_id = self.db_manager.create_quiz(
                topic_id=topic_id,
                user_id=user_id,
                title=title,
                difficulty=difficulty,
                time_limit=time_limit
            )
            
            # Generate questions using LLM
            questions = self.llm_service.generate_questions(
                topic=topic.name,
                num_questions=num_questions,
                difficulty=difficulty
            )
            
            if not questions:
                return False, "Failed to generate questions."
            
            # Add questions and options to database
            for question_data in questions:
                question_id = self.db_manager.create_question(
                    quiz_id=quiz_id,
                    text=question_data["text"],
                    difficulty=difficulty
                )
                
                for option in question_data["options"]:
                    self.db_manager.create_option(
                        question_id=question_id,
                        text=option["text"],
                        is_correct=option["is_correct"]
                    )
            
            return True, quiz_id
        except Exception as e:
            return False, str(e)
    
    def get_quiz_by_id(self, quiz_id):
        """Get quiz by ID."""
        return self.db_manager.get_quiz_by_id(quiz_id)
    
    def get_quiz_questions(self, quiz_id):
        """Get all questions for a quiz."""
        questions = self.db_manager.get_questions_for_quiz(quiz_id)
        question_data = []
        
        for question in questions:
            options = self.db_manager.get_options_for_question(question.id)
            question_data.append({
                "id": question.id,
                "text": question.text,
                "options": [{"id": option.id, "text": option.text} for option in options]
            })
        
        return question_data
    
    def start_quiz_attempt(self, quiz_id, user_id):
        """Start a new quiz attempt."""
        try:
            attempt_id = self.db_manager.create_quiz_attempt(quiz_id, user_id)
            return attempt_id
        except Exception:
            return None
    
    def submit_quiz_attempt(self, attempt_id, answers):
        """Submit a quiz attempt with answers."""
        try:
            # Process each answer
            correct_count = 0
            total_count = 0
            
            for question_id, selected_option_id in answers.items():
                # Get the correct option
                options = self.db_manager.get_options_for_question(question_id)
                correct_option = next((option for option in options if option.is_correct), None)
                
                # Check if answer is correct
                is_correct = correct_option is not None and selected_option_id == correct_option.id
                
                # Record the response
                self.db_manager.record_user_response(
                    attempt_id=attempt_id,
                    question_id=question_id,
                    selected_option_id=selected_option_id,
                    is_correct=is_correct
                )
                
                # Update counts
                if is_correct:
                    correct_count += 1
                total_count += 1
            
            # Calculate score
            score = (correct_count / total_count) * 100 if total_count > 0 else 0
            
            # Complete the attempt
            self.db_manager.complete_quiz_attempt(attempt_id, score)
            
            return True, {
                "score": score,
                "correct": correct_count,
                "total": total_count
            }
        except Exception as e:
            return False, str(e)
    
    def get_user_quiz_history(self, user_id):
        """Get quiz history for a user."""
        return self.db_manager.get_user_quiz_history(user_id)
    
    def get_quiz_stats(self, quiz_id):
        """Get statistics for a quiz."""
        return self.db_manager.get_quiz_stats(quiz_id)
    
    def get_quiz_attempt_details(self, attempt_id):
        """Get details of a quiz attempt."""
        return self.db_manager.get_attempt_details(attempt_id)
    
    def get_quizzes_by_topic(self, topic_id):
        """Get all quizzes for a topic."""
        return self.db_manager.get_quizzes_by_topic(topic_id)
    
    def generate_practice_questions(self, topic, num_questions=3, difficulty="medium"):
        """Generate practice questions without creating a quiz."""
        try:
            questions = self.llm_service.generate_questions(
                topic=topic,
                num_questions=num_questions,
                difficulty=difficulty
            )
            return True, questions
        except Exception as e:
            return False, str(e)