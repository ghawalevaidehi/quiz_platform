"""Database models for the Quiz Platform."""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Float, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_URL

Base = declarative_base()

class User(Base):
    """User model representing registered users."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quizzes = relationship("Quiz", back_populates="user")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    
class Topic(Base):
    """Topic model for quiz categorization."""
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    quizzes = relationship("Quiz", back_populates="topic")
    
class Quiz(Base):
    """Quiz model containing questions on a specific topic."""
    __tablename__ = 'quizzes'
    
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(200), nullable=False)
    difficulty = Column(String(20), default='medium')  # easy, medium, hard
    time_limit = Column(Integer, default=600)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="quizzes")
    user = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz")
    
class Question(Base):
    """Question model representing individual quiz questions."""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    text = Column(Text, nullable=False)
    difficulty = Column(String(20), default='medium')
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("Option", back_populates="question")
    responses = relationship("UserResponse", back_populates="question")
    
class Option(Base):
    """Option model representing multiple choice options for questions."""
    __tablename__ = 'options'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    
    # Relationships
    question = relationship("Question", back_populates="options")
    
class QuizAttempt(Base):
    """QuizAttempt model representing a user's attempt at a quiz."""
    __tablename__ = 'quiz_attempts'
    
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")
    responses = relationship("UserResponse", back_populates="attempt")
    
class UserResponse(Base):
    """UserResponse model tracking user answers to quiz questions."""
    __tablename__ = 'user_responses'
    
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey('quiz_attempts.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    selected_option_id = Column(Integer, ForeignKey('options.id'), nullable=True)
    is_correct = Column(Boolean, default=False)
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("Question", back_populates="responses")

def init_db():
    """Initialize the database with tables."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get a database session."""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()