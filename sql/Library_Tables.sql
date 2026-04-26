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