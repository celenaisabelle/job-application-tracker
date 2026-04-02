from flask import Flask, render_template, request, redirect
from database import get_connection

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/companies")
def companies():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("companies.html", companies=companies)

@app.route("/add_company", methods=["GET", "POST"])
def add_company():
    if request.method == "POST":
        name = request.form["name"]
        industry = request.form["industry"]
        city = request.form["city"]
        state = request.form["state"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO companies (company_name, industry, city, state) VALUES (%s, %s, %s, %s)",
            (name, industry, city, state)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/companies")

    return render_template("add_company.html")

@app.route("/delete_company/<int:id>")
def delete_company(id):
    conn = get_connection()
    cursor = conn.cursor()

    # find jobs for this company
    cursor.execute("SELECT job_id FROM jobs WHERE company_id = %s", (id,))
    jobs = cursor.fetchall()

    # delete applications tied to those jobs
    for job in jobs:
        cursor.execute("DELETE FROM applications WHERE job_id = %s", (job[0],))

    # delete contacts tied to company
    cursor.execute("DELETE FROM contacts WHERE company_id = %s", (id,))

    # delete jobs tied to company
    cursor.execute("DELETE FROM jobs WHERE company_id = %s", (id,))

    # delete company
    cursor.execute("DELETE FROM companies WHERE company_id = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/companies")

@app.route("/edit_company/<int:id>", methods=["GET", "POST"])
def edit_company(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        industry = request.form["industry"]
        city = request.form["city"]
        state = request.form["state"]

        cursor.execute("""
            UPDATE companies
            SET company_name = %s,
                industry = %s,
                city = %s,
                state = %s
            WHERE company_id = %s
        """, (name, industry, city, state, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/companies")

    cursor.execute("SELECT * FROM companies WHERE company_id = %s", (id,))
    company = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_company.html", company=company)

@app.route("/jobs")
def jobs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.job_id, j.job_title, c.company_name, j.job_type,
               j.salary_min, j.salary_max, j.date_posted
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
        job_type = request.form["job_type"]
        salary_min = request.form["salary_min"] or None
        salary_max = request.form["salary_max"] or None
        date_posted = request.form["date_posted"] or None

        cursor.execute("""
            INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, date_posted)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (company_id, job_title, job_type, salary_min, salary_max, date_posted))

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
        job_type = request.form["job_type"]
        salary_min = request.form["salary_min"] or None
        salary_max = request.form["salary_max"] or None
        date_posted = request.form["date_posted"] or None

        cursor.execute("""
            UPDATE jobs
            SET company_id = %s,
                job_title = %s,
                job_type = %s,
                salary_min = %s,
                salary_max = %s,
                date_posted = %s
            WHERE job_id = %s
        """, (company_id, job_title, job_type, salary_min, salary_max, date_posted, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/jobs")

    cursor.execute("SELECT * FROM jobs WHERE job_id = %s", (id,))
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

@app.route("/applications")
def applications():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.application_id,
               j.job_title,
               a.application_date,
               a.status,
               a.resume_version,
               a.cover_letter_sent
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
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

        cursor.execute("""
            INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent)
            VALUES (%s, %s, %s, %s, %s)
        """, (job_id, application_date, status, resume_version, cover_letter_sent))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/applications")

    cursor.execute("SELECT job_id, job_title FROM jobs ORDER BY job_title")
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

        cursor.execute("""
            UPDATE applications
            SET job_id = %s,
                application_date = %s,
                status = %s,
                resume_version = %s,
                cover_letter_sent = %s
            WHERE application_id = %s
        """, (job_id, application_date, status, resume_version, cover_letter_sent, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/applications")

    cursor.execute("SELECT * FROM applications WHERE application_id = %s", (id,))
    application = cursor.fetchone()

    cursor.execute("SELECT job_id, job_title FROM jobs ORDER BY job_title")
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

@app.route("/contacts")
def contacts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ct.contact_id,
               ct.contact_name,
               ct.email,
               ct.phone,
               cp.company_name
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
        contact_name = request.form["contact_name"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor.execute("""
            INSERT INTO contacts (company_id, contact_name, email, phone)
            VALUES (%s, %s, %s, %s)
        """, (company_id, contact_name, email, phone))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/contacts")

    cursor.execute("""
        SELECT company_id, company_name
        FROM companies
        ORDER BY company_name
    """)
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
        contact_name = request.form["contact_name"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor.execute("""
            UPDATE contacts
            SET company_id = %s,
                contact_name = %s,
                email = %s,
                phone = %s
            WHERE contact_id = %s
        """, (company_id, contact_name, email, phone, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/contacts")

    cursor.execute("""
        SELECT *
        FROM contacts
        WHERE contact_id = %s
    """, (id,))
    contact = cursor.fetchone()

    cursor.execute("""
        SELECT company_id, company_name
        FROM companies
        ORDER BY company_name
    """)
    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("edit_contact.html", contact=contact, companies=companies)


@app.route("/delete_contact/<int:id>")
def delete_contact(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM contacts
        WHERE contact_id = %s
    """, (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/contacts")

@app.route("/dashboard")
def dashboard():
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
        "dashboard.html",
        companies_count=companies_count,
        jobs_count=jobs_count,
        applications_count=applications_count,
        contacts_count=contacts_count
    )

@app.route("/job_match", methods=["GET", "POST"])
def job_match():
    results = []

    if request.method == "POST":
        keyword = request.form["keyword"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT job_title, job_type
            FROM jobs
            WHERE job_title LIKE %s
               OR job_type LIKE %s
        """, (f"%{keyword}%", f"%{keyword}%"))

        results = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template("job_match.html", results=results)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)