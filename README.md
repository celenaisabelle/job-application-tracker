# Job Application Tracker

A web application to help track job applications during the job search process.

## Features
- Track companies and job listings
- Record application submissions
- Manage interview schedules
- Store contact information
- Dashboard with summary statistics
- Job Match feature based on user skills

## Technologies
- MySQL Database
- Python with Flask
- HTML/CSS for the web interface

## Setup Instructions

1. Clone the repository:
- git clone <your-repo-url>
- cd job-application-tracker

2. Install dependencies (if needed):
- pip install -r requirements.txt

3. Set up the database:
- Open MySQL Workbench (or MySQL terminal)
- Run:
  SOURCE schema.sql;

4. Configure database connection:
- Open `database.py`
- Update your MySQL username and password

5. Run the application:
- python app.py

6. Open in browser:
- http://127.0.0.1:5002/