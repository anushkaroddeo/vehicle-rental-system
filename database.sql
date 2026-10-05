CREATE DATABASE IF NOT EXISTS vehicle_rental;

USE vehicle_rental;

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100),
    address VARCHAR(255),
    license_no VARCHAR(50) UNIQUE
);

CREATE TABLE vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50),
    brand VARCHAR(50),
    model VARCHAR(50),
    price_per_day DECIMAL(10,2),
    status ENUM('Available','Rented','Maintenance')
    DEFAULT 'Available'
);

CREATE TABLE rentals (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,

    customer_id INT,

    vehicle_id INT,

    rental_date DATE NOT NULL,

    return_date DATE,

    total_days INT,

    total_amount DECIMAL(10,2),

    FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id),

    FOREIGN KEY (vehicle_id)
    REFERENCES vehicles(vehicle_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,

    rental_id INT,

    payment_date DATE,

    amount DECIMAL(10,2),

    payment_method VARCHAR(30),

    payment_status VARCHAR(30),

    FOREIGN KEY (rental_id)
    REFERENCES rentals(rental_id)
);