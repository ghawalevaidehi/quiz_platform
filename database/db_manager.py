"""Database operations for the Quiz Platform."""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_URL
from database.models import Base, User, Topic, Quiz, Question, Option, QuizAttempt, UserResponse

class DatabaseManager:
    """Manages database operations for the Quiz Platform."""
    
    def __init__(self):
        """Initialize database connection."""
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_user(self, first_name, last_name, username, password_hash):
        """Create a new user."""
        session = self.Session()
        try:
            user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password_hash=password_hash
            )
            session.add(user)
            session.commit()
            return user.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user_by_username(self, username):
        """Get user by username."""
        session = self.Session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user
        finally:
            session.close()
    
    def get_user_by_id(self, user_id):
        """Get user by ID."""
        session = self.Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            return user
        finally:
            session.close()
    
    def create_topic(self, name, description, created_by):
        """Create a new topic."""
        session = self.Session()
        try:
            topic = Topic(
                name=name,
                description=description,
                created_by=created_by
            )
            session.add(topic)
            session.commit()
            return topic.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_topics(self):
        """Get all topics."""
        session = self.Session()
        try:
            topics = session.query(Topic).all()
            return topics
        finally:
            session.close()
    
    def get_topic_by_id(self, topic_id):
        """Get topic by ID."""
        session = self.Session()
        try:
            topic = session.query(Topic).filter(Topic.id == topic_id).first()
            return topic
        finally:
            session.close()
    
    def create_quiz(self, topic_id, user_id, title, difficulty, time_limit):
        """Create a new quiz."""
        session = self.Session()
        try:
            quiz = Quiz(
                topic_id=topic_id,
                user_id=user_id,
                title=title,
                difficulty=difficulty,
                time_limit=time_limit
            )
            session.add(quiz)
            session.commit()
            return quiz.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_quiz_by_id(self, quiz_id):
        """Get quiz by ID."""
        session = self.Session()
        try:
            quiz = session.query(Quiz).filter(Quiz.id == quiz_id).first()
            return quiz
        finally:
            session.close()
    
    def create_question(self, quiz_id, text, difficulty):
        """Create a new question."""
        session = self.Session()
        try:
            question = Question(
                quiz_id=quiz_id,
                text=text,
                difficulty=difficulty
            )
            session.add(question)
            session.commit()
            return question.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_option(self, question_id, text, is_correct):
        """Create a new option for a question."""
        session = self.Session()
        try:
            option = Option(
                question_id=question_id,
                text=text,
                is_correct=is_correct
            )
            session.add(option)
            session.commit()
            return option.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_questions_for_quiz(self, quiz_id):
        """Get all questions for a quiz."""
        session = self.Session()
        try:
            questions = session.query(Question).filter(Question.quiz_id == quiz_id).all()
            return questions
        finally:
            session.close()
    
    def get_options_for_question(self, question_id):
        """Get all options for a question."""
        session = self.Session()
        try:
            options = session.query(Option).filter(Option.question_id == question_id).all()
            return options
        finally:
            session.close()
    
    def create_quiz_attempt(self, quiz_id, user_id):
        """Create a new quiz attempt."""
        session = self.Session()
        try:
            attempt = QuizAttempt(
                quiz_id=quiz_id,
                user_id=user_id
            )
            session.add(attempt)
            session.commit()
            return attempt.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def complete_quiz_attempt(self, attempt_id, score):
        """Complete a quiz attempt with score."""
        session = self.Session()
        try:
            attempt = session.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
            if attempt:
                attempt.completed_at = datetime.utcnow()
                attempt.score = score
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def record_user_response(self, attempt_id, question_id, selected_option_id, is_correct):
        """Record a user's response to a question."""
        session = self.Session()
        try:
            response = UserResponse(
                attempt_id=attempt_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                is_correct=is_correct
            )
            session.add(response)
            session.commit()
            return response.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user_quiz_history(self, user_id):
        """Get quiz history for a user."""
        session = self.Session()
        try:
            attempts = (
                session.query(
                    QuizAttempt,
                    Quiz.title,
                    Topic.name.label('topic_name')
                )
                .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
                .join(Topic, Quiz.topic_id == Topic.id)
                .filter(QuizAttempt.user_id == user_id)
                .order_by(QuizAttempt.started_at.desc())
                .all()
            )
            return attempts
        finally:
            session.close()
    
    def get_quiz_stats(self, quiz_id):
        """Get statistics for a quiz."""
        session = self.Session()
        try:
            stats = {
                'total_attempts': session.query(func.count(QuizAttempt.id))
                    .filter(QuizAttempt.quiz_id == quiz_id)
                    .scalar(),
                'avg_score': session.query(func.avg(QuizAttempt.score))
                    .filter(QuizAttempt.quiz_id == quiz_id)
                    .filter(QuizAttempt.score != None)
                    .scalar() or 0,
                'highest_score': session.query(func.max(QuizAttempt.score))
                    .filter(QuizAttempt.quiz_id == quiz_id)
                    .filter(QuizAttempt.score != None)
                    .scalar() or 0
            }
            return stats
        finally:
            session.close()

    def get_user_quiz_stats(self, quiz_id, user_id):
        """Get statistics for a specific user on a specific quiz."""
        session = self.Session()
        try:
            stats = {
                'attempts': session.query(func.count(QuizAttempt.id))
                    .filter(QuizAttempt.quiz_id == quiz_id)
                    .filter(QuizAttempt.user_id == user_id)
                    .scalar() or 0,
                'best_score': session.query(func.max(QuizAttempt.score))
                    .filter(QuizAttempt.quiz_id == quiz_id)
                    .filter(QuizAttempt.user_id == user_id)
                    .filter(QuizAttempt.score != None)
                    .scalar() or 0,
                'avg_score': session.query(func.avg(QuizAttempt.score))
                    .filter(QuizAttempt.quiz_id == quiz_id)
                    .filter(QuizAttempt.user_id == user_id)
                    .filter(QuizAttempt.score != None)
                    .scalar() or 0
            }
            return stats
        finally:
            session.close()
    
    def get_quizzes_by_topic(self, topic_id):
        """Get all quizzes for a topic."""
        session = self.Session()
        try:
            quizzes = session.query(Quiz).filter(Quiz.topic_id == topic_id).all()
            return quizzes
        finally:
            session.close()
    
    def get_attempt_details(self, attempt_id):
        """Get details of a quiz attempt."""
        session = self.Session()
        try:
            # Get the attempt
            attempt = session.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
            
            # Get responses with question text and selected option text
            responses = (
                session.query(
                    UserResponse,
                    Question.text.label('question_text'),
                    Option.text.label('selected_option_text')
                )
                .join(Question, UserResponse.question_id == Question.id)
                .outerjoin(Option, UserResponse.selected_option_id == Option.id)
                .filter(UserResponse.attempt_id == attempt_id)
                .all()
            )
            
            return {
                'attempt': attempt,
                'responses': responses
            }
        finally:
            session.close()