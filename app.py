from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
app = Flask(__name__)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        ssl_ca="ca.pem",
        ssl_verify_cert=True
    )


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/")
def home():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM vehicles")
    total_vehicles = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM vehicles
        WHERE status = 'Available'
    """)
    available_vehicles = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM rentals
        WHERE return_date IS NULL
    """)
    active_rentals = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM customers
    """)
    total_customers = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT
            customers.name AS customer_name,
            vehicles.model AS vehicle_model,
            vehicles.vehicle_number,
            rentals.rental_date,
            rentals.total_days AS duration,
            rentals.total_amount AS amount,

            CASE
                WHEN rentals.return_date IS NOT NULL
                    THEN 'Completed'
                ELSE 'Active'
            END AS status

        FROM rentals

        JOIN customers
            ON rentals.customer_id = customers.customer_id

        JOIN vehicles
            ON rentals.vehicle_id = vehicles.vehicle_id

        ORDER BY rentals.rental_id DESC

        LIMIT 5
    """)

    recent_rentals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        total_vehicles=total_vehicles,
        available_vehicles=available_vehicles,
        active_rentals=active_rentals,
        total_customers=total_customers,
        recent_rentals=recent_rentals
    )


# =====================================================
# VEHICLES
# =====================================================

@app.route("/vehicles")
def vehicles():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM vehicles
        ORDER BY vehicle_id DESC
    """)

    vehicles = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM vehicles
    """)
    total_vehicles = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM vehicles
        WHERE status = 'Available'
    """)
    available_vehicles = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM vehicles
        WHERE status = 'Rented'
    """)
    rented_vehicles = cursor.fetchone()["total"]

    cursor.close()
    db.close()

    return render_template(
        "vehicles.html",
        vehicles=vehicles,
        total_vehicles=total_vehicles,
        available_vehicles=available_vehicles,
        rented_vehicles=rented_vehicles
    )
# =====================================================
# EDIT VEHICLE
# =====================================================

@app.route("/edit-vehicle/<int:vehicle_id>", methods=["POST"])
def edit_vehicle(vehicle_id):

    vehicle_number = request.form["vehicle_number"]
    brand = request.form["brand"]
    model = request.form["model"]
    vehicle_type = request.form["vehicle_type"]
    price_per_day = request.form["price_per_day"]
    status = request.form["status"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE vehicles
        SET
            vehicle_number = %s,
            brand = %s,
            model = %s,
            vehicle_type = %s,
            price_per_day = %s,
            status = %s
        WHERE vehicle_id = %s
    """, (
        vehicle_number,
        brand,
        model,
        vehicle_type,
        price_per_day,
        status,
        vehicle_id
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("vehicles"))
# =====================================================
# DELETE VEHICLE
# =====================================================

@app.route("/delete-vehicle/<int:vehicle_id>", methods=["POST"])
def delete_vehicle(vehicle_id):

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute("""
            DELETE FROM vehicles
            WHERE vehicle_id = %s
        """, (vehicle_id,))

        db.commit()

    except Exception as error:

        db.rollback()

        cursor.close()
        db.close()

        return f"""
        <h2>Delete Error</h2>
        <p>{error}</p>
        <br>
        <a href="/vehicles">Go Back</a>
        """

    cursor.close()
    db.close()

    return redirect(url_for("vehicles"))
# =====================================================
# SAVE VEHICLE
# =====================================================

@app.route("/save-vehicle", methods=["POST"])
def save_vehicle():

    vehicle_number = request.form["vehicle_number"]
    brand = request.form["brand"]
    model = request.form["model"]
    vehicle_type = request.form["vehicle_type"]
    rental_price = request.form["rental_price"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO vehicles
        (
            vehicle_number,
            vehicle_type,
            brand,
            model,
            price_per_day,
            status
        )
        VALUES (%s, %s, %s, %s, %s, 'Available')
    """, (
        vehicle_number,
        vehicle_type,
        brand,
        model,
        rental_price
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("vehicles"))




# =====================================================
# CUSTOMERS
# =====================================================

@app.route("/customers")
def customers():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_id DESC
    """)

    customers = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "customers.html",
        customers=customers
    )


@app.route("/add-customer")
def add_customer():

    return render_template("add_customer.html")


@app.route("/save-customer", methods=["POST"])
def save_customer():

    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]
    license_no = request.form["license_no"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO customers
        (
            name,
            phone,
            email,
            address,
            license_no
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        name,
        phone,
        email,
        address,
        license_no
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("customers"))
# =========================
# EDIT CUSTOMER
# =========================

@app.route('/edit-customer/<int:customer_id>')
def edit_customer(customer_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM customers WHERE customer_id = %s",
        (customer_id,)
    )

    customer = cursor.fetchone()

    cursor.close()
    db.close()

    if not customer:
        return "Customer not found", 404

    return render_template(
        "edit_customer.html",
        customer=customer
    )


# =====================================================
# UPDATE CUSTOMER
# =====================================================

@app.route("/update-customer/<int:customer_id>", methods=["POST"])
def update_customer(customer_id):

    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]
    license_no = request.form["license_no"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE customers
        SET
            name = %s,
            phone = %s,
            email = %s,
            address = %s,
            license_no = %s
        WHERE customer_id = %s
    """, (
        name,
        phone,
        email,
        address,
        license_no,
        customer_id
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("customers"))
# =====================================================
# DELETE CUSTOMER
# =====================================================

@app.route("/delete-customer/<int:customer_id>")
def delete_customer(customer_id):

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "DELETE FROM customers WHERE customer_id = %s",
            (customer_id,)
        )

        db.commit()

    except Exception as error:
        db.rollback()
        cursor.close()
        db.close()

        return f"""
        <h2>Delete Customer Error</h2>
        <p>{error}</p>
        <a href="/customers">Go Back</a>
        """

    cursor.close()
    db.close()

    return redirect(url_for("customers"))



# =====================================================
# RENTALS
# =====================================================

@app.route("/rentals")
def rentals():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            rentals.rental_id,
            customers.name AS customer_name,
            vehicles.vehicle_number,
            vehicles.model AS vehicle_model,
            rentals.rental_date,
            rentals.return_date,
            rentals.total_days,
            rentals.total_amount

        FROM rentals

        JOIN customers
            ON rentals.customer_id = customers.customer_id

        JOIN vehicles
            ON rentals.vehicle_id = vehicles.vehicle_id

        ORDER BY rentals.rental_id DESC
    """)

    rentals = cursor.fetchall()

    cursor.execute("""
        SELECT
            customer_id,
            name
        FROM customers
        ORDER BY name
    """)

    customers = cursor.fetchall()

    cursor.execute("""
        SELECT
            vehicle_id,
            vehicle_number,
            brand,
            model,
            price_per_day
        FROM vehicles
        WHERE status = 'Available'
        ORDER BY brand, model
    """)

    vehicles = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "rentals.html",
        rentals=rentals,
        customers=customers,
        vehicles=vehicles
    )


@app.route("/save-rental", methods=["POST"])
def save_rental():

    customer_id = request.form["customer_id"]
    vehicle_id = request.form["vehicle_id"]
    rental_date = request.form["rental_date"]
    return_date = request.form.get("return_date") or None
    total_days = request.form["total_days"]
    total_amount = request.form["total_amount"]

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute("""
            SELECT status
            FROM vehicles
            WHERE vehicle_id = %s
        """, (vehicle_id,))

        vehicle = cursor.fetchone()

        if vehicle is None:
            raise Exception("Vehicle not found.")

        if vehicle[0] != "Available":
            raise Exception("Vehicle is not available.")

        cursor.execute("""
            INSERT INTO rentals
            (
                customer_id,
                vehicle_id,
                rental_date,
                return_date,
                total_days,
                total_amount
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            customer_id,
            vehicle_id,
            rental_date,
            return_date,
            total_days,
            total_amount
        ))

        cursor.execute("""
            UPDATE vehicles
            SET status = 'Rented'
            WHERE vehicle_id = %s
        """, (vehicle_id,))

        db.commit()

    except Exception as error:

        db.rollback()

        cursor.close()
        db.close()

        return f"""
        <h2>Rental Error</h2>
        <p>{error}</p>
        <a href="/rentals">Go Back</a>
        """

    cursor.close()
    db.close()

    return redirect(url_for("rentals"))

# =====================================================
# RETURN VEHICLE
# =====================================================

@app.route("/return-rental/<int:rental_id>", methods=["POST"])
def return_rental(rental_id):

    db = get_db_connection()
    cursor = db.cursor()

    try:

        # Get vehicle belonging to this rental
        cursor.execute("""
            SELECT vehicle_id
            FROM rentals
            WHERE rental_id = %s
        """, (rental_id,))

        rental = cursor.fetchone()

        if rental is None:
            raise Exception("Rental not found.")

        vehicle_id = rental[0]

        # Mark rental as completed
        cursor.execute("""
            UPDATE rentals
            SET return_date = CURDATE()
            WHERE rental_id = %s
        """, (rental_id,))

        # Make vehicle available again
        cursor.execute("""
            UPDATE vehicles
            SET status = 'Available'
            WHERE vehicle_id = %s
        """, (vehicle_id,))

        db.commit()

    except Exception as error:

        db.rollback()

        cursor.close()
        db.close()

        return f"""
        <h2>Return Error</h2>
        <p>{error}</p>
        <br>
        <a href="/rentals">Go Back</a>
        """

    cursor.close()
    db.close()

    return redirect(url_for("rentals"))
# ============================================================
# PAYMENTS
# ============================================================

@app.route("/payments")
def payments():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            payments.payment_id,
            payments.rental_id,
            customers.name AS customer_name,
            payments.payment_date,
            payments.amount,
            payments.payment_method,
            payments.payment_status
        FROM payments
        JOIN rentals
            ON payments.rental_id = rentals.rental_id
        JOIN customers
            ON rentals.customer_id = customers.customer_id
        ORDER BY payments.payment_id DESC
    """)

    payments_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "payments.html",
        payments=payments_data
    )




# =====================================================
# ADD PAYMENT
# =====================================================

@app.route("/add-payment")
def add_payment():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            rentals.rental_id,
            customers.name AS customer_name,
            rentals.total_amount
        FROM rentals
        JOIN customers
            ON rentals.customer_id = customers.customer_id
        ORDER BY rentals.rental_id DESC
    """)

    rentals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "add_payment.html",
        rentals=rentals
    )


# =====================================================
# SAVE PAYMENT
# =====================================================

@app.route("/save-payment", methods=["POST"])
def save_payment():

    rental_id = request.form["rental_id"]
    amount = request.form["amount"]
    payment_date = request.form["payment_date"]
    payment_method = request.form["payment_method"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO payments
        (
            rental_id,
            amount,
            payment_date,
            payment_method,
            payment_status
        )
        VALUES (%s, %s, %s, %s, 'Paid')
    """, (
        rental_id,
        amount,
        payment_date,
        payment_method
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("payments"))
# =====================================================
# REPORTS
# =====================================================

@app.route("/reports")
def reports():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Total vehicles
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM vehicles
    """)
    total_vehicles = cursor.fetchone()["total"]

    # Total customers
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM customers
    """)
    total_customers = cursor.fetchone()["total"]

    # Total rentals
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM rentals
    """)
    total_rentals = cursor.fetchone()["total"]

    # Total revenue
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0) AS total
        FROM rentals
    """)
    total_revenue = cursor.fetchone()["total"]

    # Vehicle report
    cursor.execute("""
        SELECT
            vehicle_number,
            brand,
            model,
            vehicle_type,
            price_per_day,
            status
        FROM vehicles
        ORDER BY vehicle_id DESC
    """)
    vehicles = cursor.fetchall()

    # Rental report
    cursor.execute("""
        SELECT
            rentals.rental_id,
            customers.name AS customer_name,
            vehicles.model AS vehicle_model,
            rentals.rental_date,
            rentals.total_days,
            rentals.total_amount
        FROM rentals

        JOIN customers
            ON rentals.customer_id = customers.customer_id

        JOIN vehicles
            ON rentals.vehicle_id = vehicles.vehicle_id

        ORDER BY rentals.rental_id DESC
    """)
    rentals = cursor.fetchall()

    # Payment report
    cursor.execute("""
        SELECT
            payments.payment_id,
            payments.rental_id,
            customers.name AS customer_name,
            payments.amount,
            payments.payment_date,
            payments.payment_method,
            payments.payment_status
        FROM payments

        JOIN rentals
            ON payments.rental_id = rentals.rental_id

        JOIN customers
            ON rentals.customer_id = customers.customer_id

        ORDER BY payments.payment_id DESC
    """)
    payments = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "reports.html",
        total_vehicles=total_vehicles,
        total_customers=total_customers,
        total_rentals=total_rentals,
        total_revenue=total_revenue,
        vehicles=vehicles,
        rentals=rentals,
        payments=payments
    )


# =====================================================
# RUN APPLICATION
# =====================================================


if __name__ == "__main__":
    app.run(debug=True)