CREATE DATABASE mydb;

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email TEXT UNIQUE
);

INSERT INTO students (name, email)
VALUES 
  ('Alymbek', 'alymbek@example.com'),
  ('Timur', 'timur@example.com'),
  ('Beka', 'beka@example.com');

SELECT * FROM students;

SELECT * FROM students
WHERE name = 'Beka';

SELECT email from students
ORDER BY name;