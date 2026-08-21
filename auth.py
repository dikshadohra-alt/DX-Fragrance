from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from app.services.auth_service import AuthService


auth_bp = Blueprint("auth", __name__)


# =========================================================
# CUSTOMER / ADMIN LOGIN
# =========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # -------------------------------------------------
        # CHECK FIELDS
        # -------------------------------------------------

        if not email or not password:

            flash(
                "Please enter email and password.",
                "error"
            )

            return render_template(
                "customer/login.html"
            )

        # -------------------------------------------------
        # AUTHENTICATE USER
        # -------------------------------------------------

        user = AuthService.login(
            email,
            password
        )

        # -------------------------------------------------
        # INVALID LOGIN
        # -------------------------------------------------

        if not user:

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "customer/login.html"
            )

        # -------------------------------------------------
        # CLEAR OLD SESSION
        # -------------------------------------------------

        session.clear()

        # -------------------------------------------------
        # CUSTOMER / ADMIN SESSION
        # -------------------------------------------------

        session["user_id"] = user["id"]

        session["username"] = user["username"]

        session["email"] = user["email"]

        session["is_admin"] = int(
            user["is_admin"]
        )

        # -------------------------------------------------
        # ADMIN
        # -------------------------------------------------

        if int(user["is_admin"]) == 1:

            session["admin_id"] = user["id"]

            session["admin_name"] = user["username"]

            flash(
                "Welcome back, Admin!",
                "success"
            )

            return redirect(
                url_for("admin.dashboard")
            )

        # -------------------------------------------------
        # CUSTOMER
        # -------------------------------------------------

        flash(
            "Login successful! Welcome back!",
            "success"
        )

        return redirect(
            url_for("main.home")
        )

    # -----------------------------------------------------
    # GET REQUEST
    # -----------------------------------------------------

    return render_template(
        "customer/login.html"
    )


# =========================================================
# CUSTOMER REGISTRATION
# =========================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        # Accept username
        username = request.form.get(
            "username",
            ""
        ).strip()

        # Accept full_name if register.html uses it
        if not username:

            username = request.form.get(
                "full_name",
                ""
            ).strip()

        # Accept name if register.html uses it
        if not username:

            username = request.form.get(
                "name",
                ""
            ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        print("--------------------------------")
        print("REGISTER FORM RECEIVED")
        print("Username:", username)
        print("Email:", email)
        print("Password received:", bool(password))
        print("--------------------------------")

        # -------------------------------------------------
        # CHECK REQUIRED FIELDS
        # -------------------------------------------------

        if not username or not email or not password:

            flash(
                "Please fill all fields.",
                "error"
            )

            return render_template(
                "customer/register.html"
            )

        # -------------------------------------------------
        # PASSWORD VALIDATION
        # -------------------------------------------------

        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return render_template(
                "customer/register.html"
            )

        # -------------------------------------------------
        # CREATE ACCOUNT
        # -------------------------------------------------

        try:

            user = AuthService.register(
                username,
                email,
                password
            )

            # -------------------------------------------------
            # REGISTRATION FAILED / EMAIL EXISTS
            # -------------------------------------------------

            if not user:

                flash(
                    "Email already registered.",
                    "error"
                )

                return render_template(
                    "customer/register.html"
                )

            # -------------------------------------------------
            # AUTOMATIC LOGIN
            # -------------------------------------------------

            session.clear()

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            session["email"] = user["email"]

            session["is_admin"] = 0

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            flash(
                "Account created successfully! Welcome to DX Fragrance!",
                "success"
            )

            # -------------------------------------------------
            # GO TO HOME PAGE
            # -------------------------------------------------

            return redirect(
                url_for("main.home")
            )

        except Exception as error:

            print(
                "REGISTER ERROR:",
                error
            )

            flash(
                "Something went wrong during registration.",
                "error"
            )

            return render_template(
                "customer/register.html"
            )

    # =====================================================
    # GET REQUEST
    # =====================================================

    return render_template(
        "customer/register.html"
    )


# =========================================================
# CUSTOMER ACCOUNT / PROFILE
# =========================================================

@auth_bp.route("/account")
def account():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("auth.login")
        )

    connection = None

    try:

        # -------------------------------------------------
        # GET DATABASE CONNECTION
        # -------------------------------------------------

        connection = AuthService.get_db_connection()

        # -------------------------------------------------
        # GET CURRENT LOGGED-IN USER
        # -------------------------------------------------

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (
                session["user_id"],
            )
        ).fetchone()

        # -------------------------------------------------
        # USER NOT FOUND
        # -------------------------------------------------

        if not user:

            session.clear()

            flash(
                "Your account could not be found.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        # -------------------------------------------------
        # UPDATE SESSION FROM DATABASE
        # -------------------------------------------------

        session["username"] = user["username"]

        session["email"] = user["email"]

        # -------------------------------------------------
        # ACCOUNT PAGE
        # -------------------------------------------------

        return render_template(
            "customer/account.html",
            user=user
        )

    except Exception as error:

        print(
            "ACCOUNT ERROR:",
            error
        )

        flash(
            "Unable to load your profile.",
            "error"
        )

        return redirect(
            url_for("main.home")
        )

    finally:

        if connection:

            connection.close()


# =========================================================
# EDIT PROFILE
# =========================================================

@auth_bp.route(
    "/edit-profile",
    methods=["GET", "POST"]
)
def edit_profile():

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("auth.login")
        )

    connection = None

    try:

        connection = AuthService.get_db_connection()

        # -------------------------------------------------
        # GET CURRENT USER
        # -------------------------------------------------

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (
                session["user_id"],
            )
        ).fetchone()

        # -------------------------------------------------
        # USER NOT FOUND
        # -------------------------------------------------

        if not user:

            session.clear()

            return redirect(
                url_for("auth.login")
            )

        # =================================================
        # UPDATE PROFILE
        # =================================================

        if request.method == "POST":

            username = request.form.get(
                "username",
                ""
            ).strip()

            # Support full_name/name too
            if not username:

                username = request.form.get(
                    "full_name",
                    ""
                ).strip()

            if not username:

                username = request.form.get(
                    "name",
                    ""
                ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            # -------------------------------------------------
            # VALIDATION
            # -------------------------------------------------

            if not username or not email:

                flash(
                    "Please fill all fields.",
                    "error"
                )

                return render_template(
                    "customer/edit_profile.html",
                    user=user
                )

            # -------------------------------------------------
            # CHECK DUPLICATE EMAIL
            # -------------------------------------------------

            existing_user = connection.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                AND id != ?
                """,
                (
                    email,
                    session["user_id"]
                )
            ).fetchone()

            if existing_user:

                flash(
                    "This email is already registered.",
                    "error"
                )

                return render_template(
                    "customer/edit_profile.html",
                    user=user
                )

            # -------------------------------------------------
            # UPDATE USER
            # -------------------------------------------------

            connection.execute(
                """
                UPDATE users
                SET username = ?,
                    email = ?
                WHERE id = ?
                """,
                (
                    username,
                    email,
                    session["user_id"]
                )
            )

            connection.commit()

            # -------------------------------------------------
            # UPDATE SESSION
            # -------------------------------------------------

            session["username"] = username

            session["email"] = email

            session.modified = True

            flash(
                "Profile updated successfully!",
                "success"
            )

            return redirect(
                url_for("auth.account")
            )

        # -----------------------------------------------------
        # GET EDIT PROFILE
        # -----------------------------------------------------

        return render_template(
            "customer/edit_profile.html",
            user=user
        )

    except Exception as error:

        print(
            "EDIT PROFILE ERROR:",
            error
        )

        flash(
            "Unable to update your profile.",
            "error"
        )

        return redirect(
            url_for("auth.account")
        )

    finally:

        if connection:

            connection.close()


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
def logout():

    # -----------------------------------------------------
    # CLEAR SESSION
    # -----------------------------------------------------

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    # -----------------------------------------------------
    # RETURN HOME
    # -----------------------------------------------------

    return redirect(
        url_for("main.home")
    )