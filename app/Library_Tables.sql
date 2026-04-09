create schema Library_Model;
select * from person;
select * from book_collection;
select * from borrowing_history;

create table book_collection(
	book_id int auto_increment primary key,
	title varchar(255), author_last_name varchar(55), author_first_name varchar(55),
    publish_year int, publish_month int, genre varchar(55), is_available bool);
    
create table borrowing_history(
	borrow_id int auto_increment primary key,
    user_id int, book_id int, 
    foreign key (user_id) references person(library_id), 
    foreign key (book_id) references book_collection(book_id),
    borrow_date date, due_date date, return_date date);
    
create table person(
	library_id int auto_increment primary key,
    username varchar(55), pword varchar(55), email varchar(55), first_name varchar(55),
    last_name varchar(55), address varchar(55), city varchar(55), zip_code int);