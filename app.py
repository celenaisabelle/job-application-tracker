from flask import Flask, render_template, request, redirect
from database import get_connection

app = Flask(__name__)


@app.route("/")
def home():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM companies")
    companies_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs")
    jobs_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications")
    applications_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contacts")
    contacts_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        "home.html",
        companies_count=companies_count,
        jobs_count=jobs_count,
        applications_count=applications_count,
        contacts_count=contacts_count
    )


@app.route("/job_match", methods=["GET", "POST"])
def job_match():
    results = []
    user_skills_text = ""

    if request.method == "POST":
        user_skills_text = request.form["skills"]

        user_skills = [
            skill.strip().lower()
            for skill in user_skills_text.split(",")
            if skill.strip()
        ]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.job_title, c.company_name, j.job_description
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY j.job_id DESC
        """)
        jobs = cursor.fetchall()

        cursor.close()
        conn.close()

        for job in jobs:
            job_title = job[0]
            company_name = job[1]
            job_description = job[2] or ""

            job_skills = [
                skill.strip().lower()
                for skill in job_description.split(",")
                if skill.strip()
            ]

            matched_skills = [skill for skill in user_skills if skill in job_skills]
            missing_skills = [skill for skill in user_skills if skill not in job_skills]

            if len(user_skills) > 0:
                match_percent = round((len(matched_skills) / len(user_skills)) * 100)
            else:
                match_percent = 0

            if len(matched_skills) > 0:
                results.append({
                    "job_title": job_title,
                    "company_name": company_name,
                    "match_percent": match_percent,
                    "matched_count": len(matched_skills),
                    "total_count": len(user_skills),
                    "missing_skills": missing_skills
                })

        results.sort(key=lambda x: x["match_percent"], reverse=True)

    return render_template(
        "job_match.html",
        results=results,
        user_skills_text=user_skills_text
    )


# -------------------------
# COMPANIES
# -------------------------

@app.route("/companies")
def companies():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company_id, company_name, industry, website, city, state, notes, created_at
        FROM companies
        ORDER BY company_id DESC
    """)
    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("companies.html", companies=companies)


@app.route("/add_company", methods=["GET", "POST"])
def add_company():
    if request.method == "POST":
        company_name = request.form["company_name"]
        industry = request.form["industry"]
        website = request.form["website"]
        city = request.form["city"]
        state = request.form["state"]
        notes = request.form["notes"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO companies (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (company_name, industry, website, city, state, notes))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/companies")

    return render_template("add_company.html")


@app.route("/edit_company/<int:id>", methods=["GET", "POST"])
def edit_company(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        company_name = request.form["company_name"]
        industry = request.form["industry"]
        website = request.form["website"]
        city = request.form["city"]
        state = request.form["state"]
        notes = request.form["notes"]

        cursor.execute("""
            UPDATE companies
            SET company_name = %s,
                industry = %s,
                website = %s,
                city = %s,
                state = %s,
                notes = %s
            WHERE company_id = %s
        """, (company_name, industry, website, city, state, notes, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/companies")

    cursor.execute("""
        SELECT company_id, company_name, industry, website, city, state, notes, created_at
        FROM companies
        WHERE company_id = %s
    """, (id,))
    company = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_company.html", company=company)


@app.route("/delete_company/<int:id>")
def delete_company(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT job_id FROM jobs WHERE company_id = %s", (id,))
    jobs = cursor.fetchall()

    for job in jobs:
        cursor.execute("DELETE FROM applications WHERE job_id = %s", (job[0],))

    cursor.execute("DELETE FROM contacts WHERE company_id = %s", (id,))
    cursor.execute("DELETE FROM jobs WHERE company_id = %s", (id,))
    cursor.execute("DELETE FROM companies WHERE company_id = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/companies")


# -------------------------
# JOBS
# -------------------------

@app.route("/jobs")
def jobs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.job_id,
               c.company_name,
               j.job_title,
               j.job_description,
               j.salary_min,
               j.salary_max,
               j.job_type,
               j.posting_url,
               j.date_posted,
               j.is_active,
               j.created_at
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.job_id DESC
    """)
    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("jobs.html", jobs=jobs)


@app.route("/add_job", methods=["GET", "POST"])
def add_job():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        company_id = request.form["company_id"]
        job_title = request.form["job_title"]
        job_description = request.form["job_description"]
        salary_min = request.form["salary_min"] or None
        salary_max = request.form["salary_max"] or None
        job_type = request.form["job_type"]
        posting_url = request.form["posting_url"]
        date_posted = request.form["date_posted"] or None
        is_active = 1 if request.form.get("is_active") else 0

        cursor.execute("""
            INSERT INTO jobs (
                company_id, job_title, job_description, salary_min, salary_max,
                job_type, posting_url, date_posted, is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            company_id, job_title, job_description, salary_min, salary_max,
            job_type, posting_url, date_posted, is_active
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/jobs")

    cursor.execute("SELECT company_id, company_name FROM companies ORDER BY company_name")
    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("add_job.html", companies=companies)


@app.route("/edit_job/<int:id>", methods=["GET", "POST"])
def edit_job(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        company_id = request.form["company_id"]
        job_title = request.form["job_title"]
        job_description = request.form["job_description"]
        salary_min = request.form["salary_min"] or None
        salary_max = request.form["salary_max"] or None
        job_type = request.form["job_type"]
        posting_url = request.form["posting_url"]
        date_posted = request.form["date_posted"] or None
        is_active = 1 if request.form.get("is_active") else 0

        cursor.execute("""
            UPDATE jobs
            SET company_id = %s,
                job_title = %s,
                job_description = %s,
                salary_min = %s,
                salary_max = %s,
                job_type = %s,
                posting_url = %s,
                date_posted = %s,
                is_active = %s
            WHERE job_id = %s
        """, (
            company_id, job_title, job_description, salary_min, salary_max,
            job_type, posting_url, date_posted, is_active, id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/jobs")

    cursor.execute("""
        SELECT job_id, company_id, job_title, job_description, salary_min, salary_max,
               job_type, posting_url, date_posted, is_active, created_at
        FROM jobs
        WHERE job_id = %s
    """, (id,))
    job = cursor.fetchone()

    cursor.execute("SELECT company_id, company_name FROM companies ORDER BY company_name")
    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("edit_job.html", job=job, companies=companies)


@app.route("/delete_job/<int:id>")
def delete_job(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM applications WHERE job_id = %s", (id,))
    cursor.execute("DELETE FROM jobs WHERE job_id = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/jobs")


# -------------------------
# APPLICATIONS
# -------------------------

@app.route("/applications")
def applications():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.application_id,
               j.job_title,
               c.company_name,
               a.application_date,
               a.status,
               a.resume_version,
               a.cover_letter_sent,
               a.response_date,
               a.interview_date,
               a.notes,
               a.created_at
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_id DESC
    """)
    applications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("applications.html", applications=applications)


@app.route("/add_application", methods=["GET", "POST"])
def add_application():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        job_id = request.form["job_id"]
        application_date = request.form["application_date"]
        status = request.form["status"]
        resume_version = request.form["resume_version"]
        cover_letter_sent = 1 if request.form.get("cover_letter_sent") else 0
        response_date = request.form["response_date"] or None
        interview_date = request.form["interview_date"] or None
        notes = request.form["notes"]

        cursor.execute("""
            INSERT INTO applications (
                job_id, application_date, status, resume_version,
                cover_letter_sent, response_date, interview_date, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            job_id, application_date, status, resume_version,
            cover_letter_sent, response_date, interview_date, notes
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/applications")

    cursor.execute("""
        SELECT j.job_id, j.job_title, c.company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.job_title
    """)
    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("add_application.html", jobs=jobs)


@app.route("/edit_application/<int:id>", methods=["GET", "POST"])
def edit_application(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        job_id = request.form["job_id"]
        application_date = request.form["application_date"]
        status = request.form["status"]
        resume_version = request.form["resume_version"]
        cover_letter_sent = 1 if request.form.get("cover_letter_sent") else 0
        response_date = request.form["response_date"] or None
        interview_date = request.form["interview_date"] or None
        notes = request.form["notes"]

        cursor.execute("""
            UPDATE applications
            SET job_id = %s,
                application_date = %s,
                status = %s,
                resume_version = %s,
                cover_letter_sent = %s,
                response_date = %s,
                interview_date = %s,
                notes = %s
            WHERE application_id = %s
        """, (
            job_id, application_date, status, resume_version,
            cover_letter_sent, response_date, interview_date, notes, id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/applications")

    cursor.execute("""
        SELECT application_id, job_id, application_date, status, resume_version,
               cover_letter_sent, response_date, interview_date, notes, created_at
        FROM applications
        WHERE application_id = %s
    """, (id,))
    application = cursor.fetchone()

    cursor.execute("""
        SELECT j.job_id, j.job_title, c.company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.job_title
    """)
    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("edit_application.html", application=application, jobs=jobs)


@app.route("/delete_application/<int:id>")
def delete_application(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM applications WHERE application_id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/applications")


# -------------------------
# CONTACTS
# -------------------------

@app.route("/contacts")
def contacts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ct.contact_id,
               ct.first_name,
               ct.last_name,
               ct.email,
               ct.phone,
               ct.job_title,
               ct.linkedin_url,
               ct.notes,
               cp.company_name,
               ct.created_at
        FROM contacts ct
        JOIN companies cp ON ct.company_id = cp.company_id
        ORDER BY ct.contact_id DESC
    """)
    contacts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("contacts.html", contacts=contacts)


@app.route("/add_contact", methods=["GET", "POST"])
def add_contact():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        company_id = request.form["company_id"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        job_title = request.form["job_title"]
        linkedin_url = request.form["linkedin_url"]
        notes = request.form["notes"]

        cursor.execute("""
            INSERT INTO contacts (
                company_id, first_name, last_name, email, phone,
                job_title, linkedin_url, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            company_id, first_name, last_name, email, phone,
            job_title, linkedin_url, notes
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/contacts")

    cursor.execute("SELECT company_id, company_name FROM companies ORDER BY company_name")
    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("add_contact.html", companies=companies)


@app.route("/edit_contact/<int:id>", methods=["GET", "POST"])
def edit_contact(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        company_id = request.form["company_id"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        job_title = request.form["job_title"]
        linkedin_url = request.form["linkedin_url"]
        notes = request.form["notes"]

        cursor.execute("""
            UPDATE contacts
            SET company_id = %s,
                first_name = %s,
                last_name = %s,
                email = %s,
                phone = %s,
                job_title = %s,
                linkedin_url = %s,
                notes = %s
            WHERE contact_id = %s
        """, (
            company_id, first_name, last_name, email, phone,
            job_title, linkedin_url, notes, id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/contacts")

    cursor.execute("""
        SELECT contact_id, company_id, first_name, last_name, email,
               phone, job_title, linkedin_url, notes, created_at
        FROM contacts
        WHERE contact_id = %s
    """, (id,))
    contact = cursor.fetchone()

    cursor.execute("SELECT company_id, company_name FROM companies ORDER BY company_name")
    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("edit_contact.html", contact=contact, companies=companies)


@app.route("/delete_contact/<int:id>")
def delete_contact(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contacts WHERE contact_id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/contacts")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)