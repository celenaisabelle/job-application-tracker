from flask import Flask, render_template, request, redirect
from database import get_connection

app = Flask(__name__)

@app.route("/")
def home():
    return "Connected to database: job_tracker"

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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)