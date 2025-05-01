"""Quiz Platform - Main Streamlit Application."""
import streamlit as st
import time
from datetime import datetime, timedelta

from database.db_manager import DatabaseManager
from services.auth_service import AuthService
from services.quiz_service import QuizService
from utils.helpers import (
    initialize_session_state, navigate_to, format_time, 
    display_time_remaining, set_quiz_timer, clear_quiz_session,
    show_success, show_error, show_info, is_quiz_ended
)

# Initialize services
db_manager = DatabaseManager()
auth_service = AuthService()
quiz_service = QuizService()

# App configuration
st.set_page_config(
    page_title="Quiz Platform",
    page_icon="🧠",  # Updated icon for better representation
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        border-radius: 5px;
        font-weight: 500;
    }
    .quiz-header {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .correct-answer {
        color: #0f5132;
        background-color: #d1e7dd;
        padding: 0.5rem;
        border-radius: 4px;
    }
    .incorrect-answer {
        color: #842029;
        background-color: #f8d7da;
        padding: 0.5rem;
        border-radius: 4px;
    }
    .progress-text {
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .question-text {
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    .difficulty-easy {
        color: #0d6efd;
    }
    .difficulty-medium {
        color: #fd7e14;
    }
    .difficulty-hard {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# App branding in title
def render_app_header():
    """Render the app header with logo and title."""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("# 🧠")
    with col2:
        st.markdown("# Quiz Platform")
    st.markdown("---")

# Sidebar navigation (only shown when logged in)
def render_sidebar():
    """Render sidebar navigation."""
    if st.session_state.is_authenticated:
        st.sidebar.title(f"Welcome, {st.session_state.user_info['first_name']}!")
        st.sidebar.markdown("---")
        
        # Navigation buttons with icons
        if st.sidebar.button("🏠 Home", key="sidebar_home"):
            navigate_to("home")
            clear_quiz_session()
        
        if st.sidebar.button("➕ Create Topic", key="sidebar_create_topic"):
            navigate_to("create_topic")
            clear_quiz_session()
        
        if st.sidebar.button("📝 Create Quiz", key="sidebar_create_quiz"):
            navigate_to("create_quiz")
            clear_quiz_session()
        
        if st.sidebar.button("📊 My Quiz History", key="sidebar_quiz_history"):
            navigate_to("quiz_history")
            clear_quiz_session()
        
        st.sidebar.markdown("---")
        # Logout button
        if st.sidebar.button("🚪 Logout", key="sidebar_logout"):
            st.session_state.is_authenticated = False
            st.session_state.user_info = None
            navigate_to("login")
            st.experimental_rerun()

# Registration Page
def render_registration_page():
    """Render registration page."""
    render_app_header()
    st.header("Create Your Account")
    
    with st.container():
        st.markdown("##### Please fill in your details to get started")
        
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", key="reg_first_name")
        
        with col2:
            last_name = st.text_input("Last Name", key="reg_last_name")
        
        username = st.text_input("Username", key="reg_username")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Register", key="register_button"):
                if not first_name or not last_name or not username:
                    show_error("Please fill all fields.")
                else:
                    success, result = auth_service.register_user(
                        first_name=first_name,
                        last_name=last_name,
                        username=username
                    )
                    
                    if success:
                        st.success(f"""
                        Registration successful!
                        
                        Your password is: {result['password']}
                        
                        Please note this down and use it to login.
                        """)
                        time.sleep(10)
                        navigate_to("login")
                        st.experimental_rerun()
                    else:
                        show_error(result)
        
        with col2:
            if st.button("◀️ Back to Login", key="back_to_login_button"):
                navigate_to("login")
                st.experimental_rerun()

# Login Page
def render_login_page():
    """Render login page with improved layout."""
    render_app_header()

    # Centralizing the login form with two columns
    col1, col2 = st.columns([1, 3])  # Smaller left column, larger right column
    with col1:
        st.empty()  # Empty column to help center the content horizontally

    with col2:
        # Centered login container
        with st.container():
            st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
            
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🔑 Login", key="login_button"):
                    if not username or not password:
                        show_error("Please enter both username and password.")
                    else:
                        success, result = auth_service.login(username, password)
                        if success:
                            st.session_state.is_authenticated = True
                            st.session_state.user_info = result
                            show_success(f"Welcome back, {result['first_name']}!")
                            navigate_to("home")
                            st.experimental_rerun()
                        else:
                            show_error(result)
            
            with col2:
                if st.button("📝 Register New Account", key="login_to_register_button"):
                    navigate_to("register")
                    st.experimental_rerun()

    # Right side: information and features
    col1, col2 = st.columns([1, 3])  # Keeping the right side more spacious
    with col2:
        st.markdown("""
        ### Welcome to Quiz Platform!

        Test your knowledge, create custom quizzes, and track your progress.

        #### Features:
        - Create custom topics and quizzes
        - Take timed assessments
        - Review your answers
        - Track your progress over time

        Get started by logging in or creating a new account.
        """)
        
        # Optional: Add a background color or some borders for style
        st.markdown("""
        <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
            border: 2px solid #ddd;
        }
        .stTextInput>div>div>input:focus {
            border-color: #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True)

# Home Page
def render_home_page():
    """Render home page with available quizzes by topic."""
    render_app_header()
    st.header("Available Topics")
    
    topics = quiz_service.get_all_topics()
    
    if not topics:
        st.info("No topics available. Create a new topic to get started!")
        
        if st.button("➕ Create Your First Topic", key="create_first_topic"):
            navigate_to("create_topic")
            st.experimental_rerun()
    else:
        # Search functionality
        search_term = st.text_input("🔍 Search topics or quizzes", "")
        
        # Display topics in a grid
        cols = st.columns(3)
        
        topic_found = False
        
        for i, topic in enumerate(topics):
            # Filter by search term if provided
            if search_term and search_term.lower() not in topic.name.lower():
                # Check if any quiz title matches the search term
                quizzes = db_manager.get_quizzes_by_topic(topic.id)
                if not any(search_term.lower() in quiz.title.lower() for quiz in quizzes):
                    continue
            
            topic_found = True
            
            with cols[i % 3]:
                st.markdown(f"### {topic.name}")
                st.write(topic.description or "No description")
                
                # Get quizzes for this topic
                quizzes = db_manager.get_quizzes_by_topic(topic.id)
                
                if quizzes:
                    for quiz in quizzes:
                        # Skip if search term is provided and doesn't match quiz title
                        if search_term and search_term.lower() not in quiz.title.lower():
                            continue
                        
                        # Display quiz with stats
                        stats = db_manager.get_quiz_stats(quiz.id)
                        
                        difficulty_class = f"difficulty-{quiz.difficulty}"
                        
                        with st.expander(f"📝 {quiz.title}"):
                            st.markdown(f"<span class='{difficulty_class}'>Difficulty: {quiz.difficulty.title()}</span>", unsafe_allow_html=True)
                            st.write(f"⏱️ Time limit: {format_time(quiz.time_limit)}")
                            st.write(f"👥 Total attempts: {stats['total_attempts']}")
                            st.write(f"📊 Average score: {stats['avg_score']:.1f}%")
                            
                            # User's best score
                            user_stats = db_manager.get_user_quiz_stats(quiz.id, st.session_state.user_info["user_id"])
                            if user_stats['attempts'] > 0:
                                st.write(f"🏆 Your best score: {user_stats['best_score']:.1f}%")
                            
                            if st.button(f"Take Quiz", key=f"take_quiz_{quiz.id}"):
                                st.session_state.current_quiz = quiz.id
                                navigate_to("take_quiz")
                                st.experimental_rerun()
                else:
                    st.info("No quizzes available for this topic yet.")
        
        if not topic_found and search_term:
            st.warning(f"No topics or quizzes found matching '{search_term}'")

# Create Topic Page
def render_create_topic_page():
    """Render create topic page."""
    render_app_header()
    st.header("Create New Topic")
    
    with st.container():
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Description (optional)")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("✅ Create Topic", key="create_topic_button"):
                if not topic_name:
                    show_error("Please enter a topic name.")
                else:
                    success, result = quiz_service.create_topic(
                        name=topic_name,
                        description=topic_description,
                        user_id=st.session_state.user_info["user_id"]
                    )
                    
                    if success:
                        show_success("Topic created successfully!")
                        navigate_to("home")
                        st.experimental_rerun()
                    else:
                        show_error(result)

# Create Quiz Page
def render_create_quiz_page():
    """Render create quiz page."""
    render_app_header()
    st.header("Create New Quiz")
    
    topics = quiz_service.get_all_topics()
    
    if not topics:
        st.info("No topics available. Create a topic first.")
        
        if st.button("➕ Create Topic First", key="create_topic_from_quiz_page"):
            navigate_to("create_topic")
            st.experimental_rerun()
    else:
        # Topic selection
        topic_options = {topic.name: topic.id for topic in topics}
        selected_topic = st.selectbox("Select Topic", list(topic_options.keys()))
        
        # Quiz details
        quiz_title = st.text_input("Quiz Title")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
        
        with col2:
            num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
        
        with col3:
            time_limit_minutes = st.number_input("Time Limit (minutes)", min_value=1, max_value=60, value=10)
            time_limit_seconds = time_limit_minutes * 60
        
        if st.button("🧙‍♂️ Generate Quiz", key="create_quiz_button"):
            if not quiz_title:
                show_error("Please enter a quiz title.")
            else:
                topic_id = topic_options[selected_topic]
                
                # Show progress
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                progress_text.text("🔮 Generating quiz questions...")
                progress_bar.progress(10)
                
                # Simulate steps for better UX
                time.sleep(0.5)
                progress_bar.progress(30)
                progress_text.text("🧩 Creating question options...")
                time.sleep(0.5)
                progress_bar.progress(60)
                progress_text.text("📊 Finalizing quiz structure...")
                
                success, result = quiz_service.create_quiz(
                    topic_id=topic_id,
                    user_id=st.session_state.user_info["user_id"],
                    title=quiz_title,
                    num_questions=int(num_questions),
                    difficulty=difficulty,
                    time_limit=time_limit_seconds
                )
                
                progress_bar.progress(100)
                
                if success:
                    progress_text.empty()
                    progress_bar.empty()
                    show_success("Quiz created successfully!")
                    navigate_to("home")
                    st.experimental_rerun()
                else:
                    progress_text.empty()
                    progress_bar.empty()
                    show_error(result)

# Take Quiz Page
def render_take_quiz_page():
    """Render quiz taking page."""
    if not st.session_state.current_quiz:
        show_error("No quiz selected.")
        navigate_to("home")
        st.experimental_rerun()
    
    quiz = quiz_service.get_quiz_by_id(st.session_state.current_quiz)
    
    if not quiz:
        show_error("Quiz not found.")
        navigate_to("home")
        st.experimental_rerun()
    
    # Start quiz if not started
    if not st.session_state.quiz_attempt_id:
        st.session_state.quiz_attempt_id = quiz_service.start_quiz_attempt(
            quiz_id=quiz.id,
            user_id=st.session_state.user_info["user_id"]
        )
        
        # Set timer
        set_quiz_timer(quiz.time_limit)
        
        # Get questions
        questions = quiz_service.get_quiz_questions(quiz.id)
        st.session_state.quiz_questions = questions
    
    # Display quiz header
    render_app_header()
    
    # # Create a container with background for the quiz header
    # with st.container():
    #     st.markdown(f"""
    #     <div class="quiz-header">
    #         <h2>{quiz.title}</h2>
    #         <p>Difficulty: <span class="difficulty-{quiz.difficulty}">{quiz.difficulty.title()}</span></p>
    #     </div>
    #     """, unsafe_allow_html=True)
    # Create a container with background for the quiz header
    with st.container():
        difficulty_color = {
            'easy': '#4CAF50',  # Green for easy
            'medium': '#FF9800',  # Orange for medium
            'hard': '#F44336'  # Red for hard
        }

        # Set difficulty color dynamically
        difficulty_bg_color = difficulty_color.get(quiz.difficulty.lower(), '#FFFFFF')

        # Customize the quiz title color (for example, using blue for the title)
    title_color = "#2196F3"  # Blue color for title

    st.markdown(f"""
    <div class="quiz-header">
        <h2 style="color: {title_color};">{quiz.title}</h2>
        <p style="background-color: {difficulty_bg_color}; padding: 5px; border-radius: 5px;">
            Difficulty: <span class="difficulty-{quiz.difficulty}" style="color: white;">{quiz.difficulty.title()}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display timer in top right
    timer_col1, timer_col2 = st.columns([3, 1])
    with timer_col2:
        timer_placeholder = st.empty()
        remaining_time = display_time_remaining()
        
        # Change color based on time remaining
        if ":" in remaining_time:
            minutes = int(remaining_time.split(":")[0])
            timer_color = "green" if minutes > 2 else "red"
        else:
            timer_color = "red"
        
        timer_placeholder.markdown(f"""
        <div style="text-align: center; padding: 10px; border-radius: 5px; border: 1px solid {timer_color};">
            <h5 style="margin: 0; color: {timer_color};">⏱️ {remaining_time}</h5>
        </div>
        """, unsafe_allow_html=True)
    
    # Check if time's up
    if is_quiz_ended():
        handle_quiz_completion()
        return
    
    questions = st.session_state.quiz_questions
    current_idx = st.session_state.current_question_idx
    
    if questions and 0 <= current_idx < len(questions):
        current_question = questions[current_idx]
        
        # Progress indicator
        progress_text = f"Question {current_idx + 1} of {len(questions)}"
        progress_value = (current_idx + 1) / len(questions)
        st.progress(progress_value)
        st.markdown(f'<p class="progress-text">{progress_text}</p>', unsafe_allow_html=True)
        
        # Display question
        st.markdown(f'<div class="question-text">📝 {current_question["text"]}</div>', unsafe_allow_html=True)
        
        # Display options
        selected_option = st.radio(
            "Select your answer:",
            options=[option["text"] for option in current_question["options"]],
            key=f"question_{current_question['id']}"
        )
        
        # Store answer when selected
        selected_idx = [option["text"] for option in current_question["options"]].index(selected_option)
        selected_option_id = current_question["options"][selected_idx]["id"]
        st.session_state.quiz_answers[current_question["id"]] = selected_option_id
        
        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if current_idx > 0:
                if st.button("◀️ Previous", key=f"prev_question_{current_idx}"):
                    st.session_state.current_question_idx -= 1
                    st.experimental_rerun()
        
        with col3:
            if current_idx < len(questions) - 1:
                next_button_text = "Next ▶️"
            else:
                next_button_text = "Finish Quiz ✅"
            
            if st.button(next_button_text, key=f"next_question_{current_idx}"):
                if current_idx < len(questions) - 1:
                    st.session_state.current_question_idx += 1
                    st.experimental_rerun()
                else:
                    handle_quiz_completion()
        
        # Question navigation (jump to any question)
        st.markdown("---")
        st.markdown("##### Quick Navigation")
        
        # Display numbered buttons for each question
        question_cols = st.columns(min(10, len(questions)))
        for i in range(len(questions)):
            with question_cols[i % 10]:
                # Check if this question has been answered
                q_id = questions[i]["id"]
                has_answer = q_id in st.session_state.quiz_answers
                
                button_style = "primary" if i == current_idx else "secondary"
                if has_answer and i != current_idx:
                    button_text = f"{i+1} ✓"
                else:
                    button_text = f"{i+1}"
                
                if st.button(button_text, key=f"jump_to_q_{i}"):
                    st.session_state.current_question_idx = i
                    st.experimental_rerun()
    else:
        show_error("No questions available for this quiz.")

def handle_quiz_completion():
    """Handle quiz completion and score calculation."""
    if not st.session_state.quiz_attempt_id:
        navigate_to("home")
        st.experimental_rerun()
        return
    
    # Calculate score
    total_questions = len(st.session_state.quiz_questions)
    correct_answers = 0
    
    for question in st.session_state.quiz_questions:
        question_id = question["id"]
        selected_option_id = st.session_state.quiz_answers.get(question_id)
        
        if selected_option_id:
            # Get correct option
            options = db_manager.get_options_for_question(question_id)
            correct_option = next((opt for opt in options if opt.is_correct), None)
            
            # Check if answer is correct
            is_correct = correct_option and selected_option_id == correct_option.id
            
            # Record response
            db_manager.record_user_response(
                attempt_id=st.session_state.quiz_attempt_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                is_correct=is_correct
            )
            
            if is_correct:
                correct_answers += 1
    
    # Calculate percentage score
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Complete the attempt
    db_manager.complete_quiz_attempt(
        attempt_id=st.session_state.quiz_attempt_id,
        score=score_percentage
    )
    
    # Show results page
    navigate_to("quiz_results")
    st.experimental_rerun()

# Quiz Results Page
def render_quiz_results_page():
    """Render quiz results page."""
    render_app_header()
    st.header("Quiz Results")
    
    if not st.session_state.quiz_attempt_id:
        show_error("No quiz attempt found.")
        navigate_to("home")
        st.experimental_rerun()
        return
    
    # Get attempt details
    attempt_details = db_manager.get_attempt_details(st.session_state.quiz_attempt_id)
    
    if not attempt_details or not attempt_details['attempt']:
        show_error("Quiz attempt not found.")
        navigate_to("home")
        st.experimental_rerun()
        return
    
    attempt = attempt_details['attempt']
    responses = attempt_details['responses']
    
    # Get quiz details
    quiz = db_manager.get_quiz_by_id(attempt.quiz_id)
    
    # Display results header
    st.subheader(f"Quiz: {quiz.title}")
    
    # Create a container for the results summary
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"Completed: {attempt.completed_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Calculate duration
            if attempt.started_at and attempt.completed_at:
                duration = attempt.completed_at - attempt.started_at
                duration_mins = duration.total_seconds() // 60
                duration_secs = duration.total_seconds() % 60
                st.write(f"Time taken: {int(duration_mins)} min {int(duration_secs)} sec")
            
            # Display score
            score = attempt.score or 0
            
            # Progress bar for visual score with conditional coloring
            if score >= 70:
                st.markdown(f"""
                <div style="margin-top: 10px;">
                    <div style="height: 20px; background-color: #e9ecef; border-radius: 10px;">
                        <div style="height: 100%; width: {score}%; background-color: #198754; border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif score >= 40:
                st.markdown(f"""
                <div style="margin-top: 10px;">
                    <div style="height: 20px; background-color: #e9ecef; border-radius: 10px;">
                        <div style="height: 100%; width: {score}%; background-color: #fd7e14; border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin-top: 10px;">
                    <div style="height: 20px; background-color: #e9ecef; border-radius: 10px;">
                        <div style="height: 100%; width: {score}%; background-color: #dc3545; border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.metric("Your Score", f"{score:.1f}%")
            
            # Calculate correct answers
            correct_count = sum(1 for response in responses if response.UserResponse.is_correct)
            st.metric("Correct Answers", f"{correct_count}/{len(responses)}")
        
        with col3:
            # Display feedback based on score
            if score >= 90:
                st.success("Excellent! You've mastered this topic! 🏆")
            elif score >= 70:
                st.success("Great job! You have a good understanding of this topic. 👍")
            elif score >= 50:
                st.warning("You're on the right track, but there's room for improvement. 📚")
            else:
                st.warning("You might want to study this topic more and try again. 📖")
    
    # Display questions and answers
    st.markdown("---")
    st.subheader("Questions and Answers")
    
    # Create tabs for all questions and incorrect questions only
    tab1, tab2 = st.tabs(["All Questions", "Incorrect Answers Only"])
    
    with tab1:
        display_questions_and_answers(responses, all_questions=True)
    
    with tab2:
        incorrect_responses = [r for r in responses if not r.UserResponse.is_correct]
        if incorrect_responses:
            display_questions_and_answers(incorrect_responses, all_questions=False)
        else:
            st.success("Perfect score! You answered all questions correctly.")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retry This Quiz", key="retry_quiz"):
            clear_quiz_session()
            st.session_state.current_quiz = quiz.id
            navigate_to("take_quiz")
            st.experimental_rerun()
    
    with col2:
        if st.button("📚 Take Another Quiz", key="take_another_quiz"):
            clear_quiz_session()
            navigate_to("home")
            st.experimental_rerun()
    
    with col3:
        if st.button("📊 View Quiz History", key="view_quiz_history_from_results"):
            clear_quiz_session()
            navigate_to("quiz_history")
            st.experimental_rerun()

def display_questions_and_answers(responses, all_questions=True):
    """Helper function to display questions and answers."""
    for i, response in enumerate(responses):
        question_text = response.question_text
        selected_text = response.selected_option_text
        is_correct = response.UserResponse.is_correct
        
        # Create expander with appropriate icon based on correctness
        icon = "✅" if is_correct else "❌"
        expander_label = f"Question {i+1} {icon}"
        
        with st.expander(expander_label):
            st.markdown(f"**{question_text}**")
            
            # Display user's answer with appropriate styling
            if is_correct:
                st.markdown(f"""
                <div class="correct-answer">
                    <strong>Your answer:</strong> {selected_text} ✓
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="incorrect-answer">
                    <strong>Your answer:</strong> {selected_text} ✗
                </div>
                """, unsafe_allow_html=True)
                
                # Show correct answer
                options = db_manager.get_options_for_question(response.UserResponse.question_id)
                correct_option = next((opt for opt in options if opt.is_correct), None)
                
                if correct_option:
                    st.markdown(f"""
                    <div class="correct-answer">
                        <strong>Correct answer:</strong> {correct_option.text}
                    </div>
                    """, unsafe_allow_html=True)

# Quiz History Page
def render_quiz_history_page():
    """Render quiz history page."""
    render_app_header()
    st.header("My Quiz History")
    
    # Get user's quiz history
    attempts = db_manager.get_user_quiz_history(st.session_state.user_info["user_id"])
    
    if not attempts:
        st.info("You haven't taken any quizzes yet.")
        
        if st.button("🏠 Go to Home Page", key="go_home_from_history"):
            navigate_to("home")
            st.experimental_rerun()
    else:
        # Stats summary
        total_attempts = len(attempts)
        completed_attempts = sum(1 for attempt, _, _ in attempts if attempt.completed_at)
        
        # Calculate average score for completed attempts
        scores = [attempt.score for attempt, _, _ in attempts if attempt.completed_at and attempt.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Display stats in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Attempts", total_attempts)
        
        with col2:
            st.metric("Completed Quizzes", completed_attempts)
        
        with col3:
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        st.markdown("---")
        
        # Display attempts in a table
        data = []
        for attempt, quiz_title, topic_name in attempts:
            status = "Completed" if attempt.completed_at else "In progress"
            
            # Format score for display
            score_display = f"{attempt.score:.1f}%" if attempt.score is not None else "In progress"
            
            # Format the date
            date_display = attempt.started_at.strftime("%Y-%m-%d %H:%M")
            
            data.append({
                "Date": date_display,
                "Topic": topic_name,
                "Quiz": quiz_title,
                "Score": score_display,
                "Status": status
            })
        
        # Add sorting functionality
        sort_col, _ = st.columns([1, 3])
        with sort_col:
            sort_by = st.selectbox("Sort by:", ["Date", "Topic", "Quiz", "Score"], index=0)
        
        # Sort the data
        if sort_by == "Score":
            # Handle "In progress" special case for sorting
            sorted_data = sorted(
                data,
                key=lambda x: float(x["Score"].replace("%", "")) if x["Score"] != "In progress" else -1,
                reverse=True
            )
        else:
            sorted_data = sorted(data, key=lambda x: x[sort_by], reverse=(sort_by == "Date"))
        
        # Display as a styled dataframe with hover effect
        st.markdown("""
        <style>
        .dataframe-container {
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            overflow: hidden;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        st.dataframe(sorted_data, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add button to return to home
        if st.button("🏠 Return to Home", key="return_home_from_history"):
            navigate_to("home")
            st.experimental_rerun()

# Main app logic
def main():
    """Main application entry point."""
    # Render sidebar
    render_sidebar()
    
    # Render current page
    current_page = st.session_state.current_page
    
    if current_page == "login":
        render_login_page()
    elif current_page == "register":
        render_registration_page()
    elif st.session_state.is_authenticated:
        # Authenticated pages
        if current_page == "home":
            render_home_page()
        elif current_page == "create_topic":
            render_create_topic_page()
        elif current_page == "create_quiz":
            render_create_quiz_page()
        elif current_page == "take_quiz":
            render_take_quiz_page()
        elif current_page == "quiz_results":
            render_quiz_results_page()
        elif current_page == "quiz_history":
            render_quiz_history_page()
        else:
            # Default to home if page not found
            navigate_to("home")
            st.experimental_rerun()
    else:
        # Redirect to login if not authenticated
        navigate_to("login")
        st.experimental_rerun()

if __name__ == "__main__":
    main()