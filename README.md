Running the Application
Now that we've created all the necessary files, here's how you can run the application:

Create a directory structure as shown earlier.
Copy all the code files (from the artifacts above) into their respective locations in the directory structure.
Create a .env file in the root directory with your database and Together AI credentials:

# Database configuration
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=quiz_platform

# Together AI API configuration
TOGETHER_API_KEY=your_together_api_key
TOGETHER_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1

# Application settings
SECRET_KEY=your_secret_key_for_session

Install dependencies:

bashpip install -r requirements.txt

Set up PostgreSQL database named "quiz_platform" (or whatever you specified in the .env file)
Run the application:

bashstreamlit run app.py
Features Implemented
The application now includes all the functionality you requested:

User Management

Registration with first name, last name, and username
Auto-generated password based on names
Login system


Topic Management

Create new topics with descriptions
View available topics


Quiz Management

Create quizzes on selected topics
Set difficulty levels (easy, medium, hard)
Configure number of questions and time limits
Automatic question generation using Together.ai API


Quiz Taking

Interactive quiz interface
Timer functionality
Question navigation
Answer tracking


Results and History

Score calculation and display
Detailed feedback on answers
Quiz history tracking
Performance metrics


Database Integration

Complete PostgreSQL database with models for users, topics, quizzes, questions, answers, and attempts
Comprehensive tracking of user quiz history and responses



This application is set up to run locally as requested, but can easily be deployed to a public server in the future with minimal changes.