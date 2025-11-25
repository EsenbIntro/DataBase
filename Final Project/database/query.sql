DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS members CASCADE;
DROP TABLE IF EXISTS books CASCADE;

CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    stock_quantity INT DEFAULT 1,
    CONSTRAINT check_stock_positive CHECK (stock_quantity >= 0)
);

CREATE TABLE members (
    member_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    join_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    book_id INT REFERENCES books(book_id) ON DELETE CASCADE,
    member_id INT REFERENCES members(member_id) ON DELETE CASCADE,
    loan_date DATE DEFAULT CURRENT_DATE,
    return_date DATE
);

CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_members_email ON members(email);

INSERT INTO books (title, author, isbn, stock_quantity) VALUES 
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 4),
('1984', 'George Orwell', '9780451524935', 2),
('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 3),
('Pride and Prejudice', 'Jane Austen', '9781503290563', 5),
('The Catcher in the Rye', 'J.D. Salinger', '9780316769488', 2),
('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 6),
('Fahrenheit 451', 'Ray Bradbury', '9781451673319', 4),
('Dune', 'Frank Herbert', '9780441013593', 3),
('The Hitchhiker''s Guide to the Galaxy', 'Douglas Adams', '9780345391803', 5),
('Neuromancer', 'William Gibson', '9780441569595', 2),
('Clean Code', 'Robert C. Martin', '9780132350884', 8),
('The Pragmatic Programmer', 'Andrew Hunt', '9780201616224', 4),
('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 2),
('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', '9780062316097', 5),
('Educated', 'Tara Westover', '9780399590504', 3);

INSERT INTO members (name, email, phone) VALUES 
('Usongazy Esenbaev', 'eu12855@auca.kg', '550-0303'),
('Carl Johnson', 'carl.j@auca.kg', '555-0101'),
('Joker Smith', 'joker.s@auca.kg', '555-0102'),
('Charlie Cake', 'charlie.c@auca.kg', '555-0103'),
('Diana Prince', 'diana.p@auca.kg', '555-0104'),
('Evan Wright', 'evan.w@auca.kg', '555-0105'),
('Fiona Shrek', 'fiona.s@auca.kg', '555-0106'),
('George Martin', 'george.m@auca.kg', '555-0107'),
('Hannah Montana', 'hannah.m@auca.kg', '555-0108');

INSERT INTO loans (book_id, member_id, loan_date, return_date) VALUES 
(1, 1, CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '25 days'),
(2, 2, CURRENT_DATE - INTERVAL '28 days', CURRENT_DATE - INTERVAL '20 days'),
(5, 3, CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE - INTERVAL '10 days'),
(11, 5, CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '10 days'),
(8, 4, CURRENT_DATE - INTERVAL '40 days', CURRENT_DATE - INTERVAL '35 days');

INSERT INTO loans (book_id, member_id, loan_date, return_date) VALUES 
(3, 1, CURRENT_DATE - INTERVAL '5 days', NULL),
(11, 2, CURRENT_DATE - INTERVAL '2 days', NULL),
(9, 6, CURRENT_DATE - INTERVAL '1 day', NULL),
(1, 7, CURRENT_DATE, NULL);