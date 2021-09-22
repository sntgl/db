DROP SCHEMA IF EXISTS lab CASCADE ;
CREATE SCHEMA lab
CREATE TABLE lab.Owner (
    owner_id INT PRIMARY KEY,
    passport_id DECIMAL(10, 0) NOT NULL,
    last_name TEXT,
    first_name TEXT,
    middle_name TEXT,
    date_birth DATE,
    city_birth TEXT
);
CREATE TABLE lab.Camera (
    camera_id INT PRIMARY KEY,
    address TEXT,
    latitude DECIMAL(16,14),
    longitude DECIMAL(16,14),
    date_added DATE,
    department TEXT,
    system_type TEXT
);
CREATE TABLE lab.Car (
    car_id INT PRIMARY KEY,
    owner_id INT,
    model TEXT,
    color TEXT,
    plate TEXT,
    VIN TEXT,
    reg_certificate DECIMAL(10, 0),
    reg_date DATE,
    issue_year DECIMAL(4, 0)
);
CREATE TABLE lab.Fine (
    fine_id INT PRIMARY KEY,
    camera_id INT,
    car_id INT,
    article_id INT,
    is_paid BOOLEAN,
    date DATE,
    description TEXT
);
CREATE TABLE lab.Article (
    article_id INT PRIMARY KEY,
    department TEXT,
    article_number TEXT,
    description TEXT,
    amount INT
)