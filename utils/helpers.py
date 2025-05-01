"""Helper functions for the Quiz Platform."""
import streamlit as st
import time
from datetime import datetime, timedelta

def initialize_session_state():
    """Initialize session state variables."""
    # Authentication related
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # Navigation related
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "login"
    
    # Quiz related
    if 'current_quiz' not in st.session_state:
        st.session_state.current_quiz = None
    if 'quiz_attempt_id' not in st.session_state:
        st.session_state.quiz_attempt_id = None
    if 'current_question_idx' not in st.session_state:
        st.session_state.current_question_idx = 0
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    if 'quiz_end_time' not in st.session_state:
        st.session_state.quiz_end_time = None

def navigate_to(page):
    """Navigate to a different page in the app."""
    st.session_state.current_page = page

def format_time(seconds):
    """Format seconds into MM:SS format."""
    return str(timedelta(seconds=seconds))[2:7]  # Extract MM:SS from HH:MM:SS

def display_time_remaining():
    """Display and track time remaining for quiz."""
    if st.session_state.quiz_end_time:
        now = datetime.now()
        end_time = st.session_state.quiz_end_time
        
        if now >= end_time:
            # Time's up
            return "Time's up!"
        else:
            # Calculate remaining time
            remaining = (end_time - now).total_seconds()
            return format_time(int(remaining))
    return ""

def set_quiz_timer(seconds):
    """Set the quiz timer."""
    st.session_state.quiz_end_time = datetime.now() + timedelta(seconds=seconds)

def clear_quiz_session():
    """Clear quiz-related session data."""
    st.session_state.current_quiz = None
    st.session_state.quiz_attempt_id = None
    st.session_state.current_question_idx = 0
    st.session_state.quiz_answers = {}
    st.session_state.quiz_end_time = None

def show_success(message, duration=3):
    """Show success message with auto-dismissal."""
    with st.empty():
        st.success(message)
        time.sleep(duration)

def show_error(message, duration=3):
    """Show error message with auto-dismissal."""
    with st.empty():
        st.error(message)
        time.sleep(duration)

def show_info(message, duration=3):
    """Show info message with auto-dismissal."""
    with st.empty():
        st.info(message)
        time.sleep(duration)

def is_quiz_ended():
    """Check if quiz time has ended."""
    if not st.session_state.quiz_end_time:
        return False
    return datetime.now() >= st.session_state.quiz_end_time