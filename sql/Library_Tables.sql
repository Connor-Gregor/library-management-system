create schema if not exists Library_Model;
use Library_Model;

create table person(
	library_id int auto_increment primary key,
    username varchar(55),
    pword varchar(55),
    email varchar(55),
    first_name varchar(55),
    last_name varchar(55),
    address varchar(55),
    city varchar(55),
    zip_code int,
    role varchar(55)
);

create table book_collection(
	book_id int auto_increment primary key,
	title varchar(255),
	author_last_name varchar(55),
	author_first_name varchar(55),
    publish_year int,
    publish_month int,
    genre varchar(55),
    is_available boolean
);

create table borrowing_history(
	borrow_id int auto_increment primary key,
    user_id int,
    book_id int,
    borrow_date date,
    due_date date,
    return_date date,
    constraint fk_user foreign key (user_id) references person(library_id),
    constraint fk_book foreign key (book_id) references book_collection(book_id)
);

-- testing login with an admin and regular user
insert into person (username, pword, email, first_name, last_name, role)
values ('admin1', 'adminpass', 'admin@test.com', 'Admin', 'User', 'admin');

insert into person (username, pword, email, first_name, last_name, role)
values ('user1', 'userpass', 'user@test.com', 'Regular', 'User', 'user');

-- testing searching for books
select * from person;
select * from book_collection;
select * from borrowing_history;

ALTER TABLE book_collection
ADD copies_available INT DEFAULT 1;

CREATE INDEX idx_book_title
ON book_collection(title);

-- Views
CREATE VIEW active_borrowed_books AS
SELECT bh.borrow_id, p.username, p.email, b.title AS book_title, bh.borrow_date, bh.due_date
FROM borrowing_history bh
JOIN person p ON bh.user_id = p.library_id
JOIN book_collection b ON bh.book_id = b.book_id
WHERE bh.return_date IS NULL;

SELECT * FROM active_borrowed_books;

-- Triggers:
DELIMITER //
CREATE TRIGGER after_book_borrow
AFTER INSERT ON borrowing_history
FOR EACH ROW
BEGIN
    UPDATE book_collection
    SET copies_available = copies_available - 1
    WHERE book_id = NEW.book_id;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER after_book_return
AFTER UPDATE ON borrowing_history
FOR EACH ROW
BEGIN
    IF OLD.return_date IS NULL AND NEW.return_date IS NOT NULL THEN
        UPDATE book_collection
        SET copies_available = copies_available + 1
        WHERE book_id = NEW.book_id;
    END IF;
END //
DELIMITER ;

-- Entering test data
INSERT INTO book_collection (title, author_first_name, author_last_name, publish_year, publish_month, genre, copies_available)
VALUES 
('The Great Gatsby', 'F. Scott', 'Fitzgerald', 1925, 4, 'Fiction', 3),
('Dune', 'Frank', 'Herbert', 1965, 8, 'Sci-Fi', 5),
('1984', 'George', 'Orwell', 1949, 6, 'Dystopian', 2),
('The Hobbit', 'J.R.R.', 'Tolkien', 1937, 9, 'Fantasy', 4),
('To Kill a Mockingbird', 'Harper', 'Lee', 1960, 7, 'Fiction', 1);

-- Stored Procedure
DELIMITER //

CREATE PROCEDURE BorrowBook(
    IN p_user_id INT,
    IN p_book_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_already_borrowed INT DEFAULT 0;
    DECLARE v_copies INT DEFAULT 0;

    SELECT COUNT(*) INTO v_already_borrowed
    FROM borrowing_history
    WHERE user_id = p_user_id AND book_id = p_book_id AND return_date IS NULL;
    IF v_already_borrowed > 0 THEN
        SET p_success = FALSE;
        SET p_message = 'You already have a copy of this book checked out!';
    ELSE
        SELECT copies_available INTO v_copies
        FROM book_collection
        WHERE book_id = p_book_id;

        IF v_copies < 1 THEN
            SET p_success = FALSE;
            SET p_message = 'Sorry, there are no copies of this book left.';
        ELSE
            INSERT INTO borrowing_history (user_id, book_id, borrow_date, due_date)
            VALUES (p_user_id, p_book_id, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY));

            SET p_success = TRUE;
            SET p_message = 'Book borrowed successfully! It is due in 30 days.';
        END IF;
    END IF;
END //

DELIMITER ;


-- Cursor:
DELIMITER //

CREATE PROCEDURE AuditOverdueBooks(OUT overdue_count INT)
BEGIN
    DECLARE v_due_date DATE;
    DECLARE v_done INT DEFAULT FALSE;
    DECLARE borrow_cursor CURSOR FOR 
        SELECT due_date 
        FROM borrowing_history 
        WHERE return_date IS NULL;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = TRUE;
    SET overdue_count = 0;
    OPEN borrow_cursor;

    audit_loop: LOOP
        FETCH borrow_cursor INTO v_due_date;
        IF v_done THEN
            LEAVE audit_loop;
        END IF;

        IF v_due_date < CURDATE() THEN
            SET overdue_count = overdue_count + 1;
        END IF;
    END LOOP;
    CLOSE borrow_cursor;

END //