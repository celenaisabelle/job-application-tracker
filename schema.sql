DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker;
USE job_tracker;

CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    website VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    job_description TEXT,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    job_type VARCHAR(20),
    posting_url VARCHAR(500),
    date_posted DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    application_date DATE NOT NULL,
    status VARCHAR(30) DEFAULT 'Applied',
    resume_version VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    response_date DATE,
    interview_date DATETIME,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

CREATE TABLE contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    job_title VARCHAR(100),
    linkedin_url VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

INSERT INTO companies (company_name, industry, website, city, state)
VALUES
('Tech Solutions Inc', 'Technology', 'www.techsolutions.com', 'Miami', 'Florida'),
('Data Analytics Corp', 'Data Science', 'www.dataanalytics.com', 'Austin', 'Texas'),
('Cloud Systems LLC', 'Cloud Computing', 'www.cloudsystems.com', 'Seattle', 'Washington'),
('Digital Innovations', 'Software', 'www.digitalinnovations.com', 'San Francisco', 'California'),
('Smart Tech Group', 'AI/ML', 'www.smarttech.com', 'Boston', 'Massachusetts');

INSERT INTO jobs (company_id, job_title, salary_min, salary_max, job_type, date_posted)
VALUES
(1, 'Software Developer', 70000, 90000, 'Full-time', '2025-01-15'),
(1, 'Database Administrator', 75000, 95000, 'Full-time', '2025-01-10'),
(2, 'Data Analyst', 65000, 85000, 'Full-time', '2025-01-12'),
(3, 'Cloud Engineer', 80000, 100000, 'Full-time', '2025-01-08'),
(4, 'Junior Developer', 55000, 70000, 'Full-time', '2025-01-14'),
(4, 'Senior Developer', 95000, 120000, 'Full-time', '2025-01-14'),
(5, 'ML Engineer', 90000, 115000, 'Full-time', '2025-01-11');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent)
VALUES
(1, '2025-01-16', 'Applied', 'v2.1', TRUE),
(3, '2025-01-13', 'Interview Scheduled', 'v2.1', TRUE),
(4, '2025-01-09', 'Rejected', 'v2.0', FALSE),
(5, '2025-01-15', 'Applied', 'v2.1', TRUE),
(7, '2025-01-12', 'Phone Screen', 'v2.1', TRUE);

INSERT INTO contacts (company_id, first_name, last_name, email, job_title)
VALUES
(1, 'Sarah', 'Johnson', 'sjohnson@techsolutions.com', 'HR Manager'),
(2, 'Michael', 'Chen', 'mchen@dataanalytics.com', 'Technical Recruiter'),
(3, 'Emily', 'Williams', 'ewilliams@cloudsystems.com', 'Hiring Manager'),
(4, 'David', 'Brown', NULL, 'Senior Developer'),
(5, 'Lisa', 'Garcia', 'lgarcia@smarttech.com', 'Talent Acquisition');