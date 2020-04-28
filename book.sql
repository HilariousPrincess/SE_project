drop table if exists users;
create table if not exists users (
        user_id integer primary key autoincrement,
	user_num text unique,
	pwd text not null,
	email text
);
--邮箱和统一身份认证检测
--alter table users add constraint CK_email check(email like '%@%.%');
--alter table users add constraint CK_num check(user_num like '2[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]');
--alter table users add constraint CK_num check(user_num not null);
 
drop table if exists books;
create table if not exists books(
       book_id text primary key,
       book_name text not null,
       author text not null,
       publish_com text not null,
       publish_date text not null,
       total_num integer default 0,
       present_num integer default 0
);
--书名检测
--alter table books add constraint CK_date check(publish_date like '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]');

drop table if exists borrows;
create table  borrows(
       user_num text not null,
       book_id text not null,
       date_borrow text not null,
       date_return text not null,
       primary key (user_num, book_id)
);

drop table if exists histroys;
create table histroys(
       histroy_id integer primary key autoincrement,
       book_id text not null,
       user_num text not null,
       date_borrow text not null,
       date_return text,
       status text not null default 'not return'
);
