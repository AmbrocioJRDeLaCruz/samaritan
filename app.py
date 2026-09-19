import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_db, init_db, login_required

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "samaritan-cs50-secret-dev-key")


@app.after_request
def after_request(response):
    """
    Asegura que las respuestas del servidor no sean cacheadas por el navegador.
    Estándar en las aplicaciones de CS50.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """
    Panel Principal (Dashboard).
    Muestra métricas generales y el listado de casos de ayuda comunitarios.
    """
    with get_db() as conn:
        # Métricas de resumen
        total_beneficiaries = conn.execute("SELECT COUNT(*) FROM beneficiaries;").fetchone()[0]
        pending_cases = conn.execute("SELECT COUNT(*) FROM help_cases WHERE status = 'Pendiente';").fetchone()[0]
        in_progress_cases = conn.execute("SELECT COUNT(*) FROM help_cases WHERE status = 'En progreso';").fetchone()[0]
        completed_cases = conn.execute("SELECT COUNT(*) FROM help_cases WHERE status = 'Completado';").fetchone()[0]

        # Listado de casos con información de beneficiario y voluntario
        cases = conn.execute("""
            SELECT 
                c.id, c.title, c.description, c.category, c.status, c.created_at,
                b.name AS beneficiary_name,
                u.name AS volunteer_name
            FROM help_cases c
            JOIN beneficiaries b ON c.beneficiary_id = b.id
            LEFT JOIN users u ON c.volunteer_id = u.id
            ORDER BY c.created_at DESC;
        """).fetchall()

    return render_template(
        "index.html",
        total_beneficiaries=total_beneficiaries,
        pending_cases=pending_cases,
        in_progress_cases=in_progress_cases,
        completed_cases=completed_cases,
        cases=cases
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registro de nuevos voluntarios en la plataforma.
    """
    # Si el usuario ya está autenticado, redirigir al panel
    if session.get("user_id"):
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validaciones de servidor
        if not name:
            flash("Debes ingresar tu nombre completo.", "warning")
            return render_template("register.html")

        if not email:
            flash("Debes ingresar un correo electrónico válido.", "warning")
            return render_template("register.html")

        if not password or not confirmation:
            flash("Debes ingresar y confirmar tu contraseña.", "warning")
            return render_template("register.html")

        if password != confirmation:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("register.html")

        # Generar hash seguro mediante Werkzeug
        password_hash = generate_password_hash(password)

        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (name, email, hash, role) VALUES (?, ?, ?, 'volunteer');",
                    (name, email, password_hash)
                )
                user_id = cursor.lastrowid

            # Iniciar sesión automáticamente
            session["user_id"] = user_id
            session["user_name"] = name
            flash("¡Bienvenido a Samaritan! Tu cuenta de voluntario ha sido creada.", "success")
            return redirect("/")

        except Exception:
            flash("Este correo electrónico ya se encuentra registrado.", "danger")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Inicio de sesión para usuarios y voluntarios.
    """
    # Limpiar cualquier sesión previa
    if request.method == "POST":
        session.clear()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")

        if not email or not password:
            flash("Debes ingresar tu correo y contraseña.", "warning")
            return render_template("login.html")

        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?;", (email,)).fetchone()

        if user is None or not check_password_hash(user["hash"], password):
            flash("Correo electrónico o contraseña inválidos.", "danger")
            return render_template("login.html")

        # Guardar datos en la sesión de Flask
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        flash(f"¡Hola de nuevo, {user['name']}!", "info")
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Cierre de sesión seguro.
    """
    session.clear()
    flash("Has cerrado sesión exitosamente.", "info")
    return redirect("/login")


@app.route("/beneficiaries", methods=["GET", "POST"])
@login_required
def beneficiaries():
    """
    Directorio y registro de beneficiarios / familias con necesidades.
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        household_size = request.form.get("household_size", "1").strip()
        notes = request.form.get("notes", "").strip()

        if not name:
            flash("El nombre o familia del beneficiario es obligatorio.", "warning")
            return redirect("/beneficiaries")

        try:
            size_int = int(household_size) if household_size else 1
        except ValueError:
            size_int = 1

        with get_db() as conn:
            conn.execute(
                "INSERT INTO beneficiaries (name, phone, location, household_size, notes) VALUES (?, ?, ?, ?, ?);",
                (name, phone if phone else None, location if location else None, size_int, notes if notes else None)
            )

        flash(f"Beneficiario '{name}' registrado con éxito.", "success")
        return redirect("/beneficiaries")

    # Listado en GET
    with get_db() as conn:
        all_beneficiaries = conn.execute("SELECT * FROM beneficiaries ORDER BY name ASC;").fetchall()

    return render_template("beneficiaries.html", beneficiaries=all_beneficiaries)


@app.route("/cases/new", methods=["GET", "POST"])
@login_required
def new_case():
    """
    Registro de una nueva necesidad o caso de ayuda.
    """
    with get_db() as conn:
        if request.method == "POST":
            beneficiary_id = request.form.get("beneficiary_id")
            title = request.form.get("title", "").strip()
            category = request.form.get("category", "Otro")
            description = request.form.get("description", "").strip()

            if not beneficiary_id or not title:
                flash("Debes seleccionar un beneficiario y proveer un título para la necesidad.", "warning")
                return redirect("/cases/new")

            conn.execute(
                "INSERT INTO help_cases (beneficiary_id, title, category, description, status) VALUES (?, ?, ?, ?, 'Pendiente');",
                (int(beneficiary_id), title, category, description if description else None)
            )
            flash("Caso de ayuda registrado exitosamente.", "success")
            return redirect("/")

        # GET: Cargar beneficiarios para el select
        selected_id = request.args.get("beneficiary_id")
        beneficiaries_list = conn.execute("SELECT id, name, location FROM beneficiaries ORDER BY name ASC;").fetchall()

    return render_template("new_case.html", beneficiaries=beneficiaries_list, selected_beneficiary_id=selected_id)


@app.route("/cases/<int:case_id>")
@login_required
def case_detail(case_id):
    """
    Ficha de detalle de un caso específico.
    """
    with get_db() as conn:
        case = conn.execute("""
            SELECT 
                c.id, c.title, c.description, c.category, c.status, c.created_at,
                b.id AS beneficiary_id, b.name AS beneficiary_name, b.phone AS beneficiary_phone,
                b.location AS beneficiary_location, b.household_size,
                u.id AS volunteer_id, u.name AS volunteer_name, u.email AS volunteer_email
            FROM help_cases c
            JOIN beneficiaries b ON c.beneficiary_id = b.id
            LEFT JOIN users u ON c.volunteer_id = u.id
            WHERE c.id = ?;
        """, (case_id,)).fetchone()

    if not case:
        flash("El caso solicitado no existe.", "warning")
        return redirect("/")

    return render_template("case_detail.html", case=case)


@app.route("/cases/<int:case_id>/claim", methods=["POST"])
@login_required
def claim_case(case_id):
    """
    Permite al voluntario autenticado asignarse a un caso pendiente.
    """
    user_id = session.get("user_id")
    with get_db() as conn:
        conn.execute(
            "UPDATE help_cases SET volunteer_id = ?, status = 'En progreso' WHERE id = ?;",
            (user_id, case_id)
        )
    flash("Te has asignado como voluntario para coordinar este caso.", "success")
    return redirect(f"/cases/{case_id}")


@app.route("/cases/<int:case_id>/status", methods=["POST"])
@login_required
def update_case_status(case_id):
    """
    Actualiza el estado de atención de un caso (Pendiente, En progreso, Completado).
    """
    new_status = request.form.get("status")
    if new_status in ["Pendiente", "En progreso", "Completado"]:
        with get_db() as conn:
            conn.execute("UPDATE help_cases SET status = ? WHERE id = ?;", (new_status, case_id))
        flash("Estado del caso actualizado correctamente.", "success")
    else:
        flash("Estado no válido.", "warning")

    return redirect(f"/cases/{case_id}")


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
