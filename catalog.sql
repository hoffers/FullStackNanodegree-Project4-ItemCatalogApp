DROP DATABASE IF EXISTS catalog;

CREATE DATABASE catalog WITH OWNER = vagrant;

\c catalog

CREATE TABLE categories ( cat_id SERIAL PRIMARY KEY,
                          name TEXT );

CREATE TABLE users ( user_id SERIAL PRIMARY KEY,
                     name TEXT NOT NULL,
                     email TEXT NOT NULL,
                     picture TEXT );

CREATE TABLE items ( item_id SERIAL PRIMARY KEY,
                     title TEXT,
                     description TEXT,
                     date_added timestamp with time zone DEFAULT now(),
                     cat_id INT REFERENCES categories,
                     user_id INT REFERENCES users );

CREATE VIEW recent_items as
    SELECT c.name, i.title, i.item_id FROM items i JOIN categories c
    ON c.cat_id = i.cat_id
    ORDER BY i.date_added DESC
    LIMIT 10;

INSERT INTO categories (name) VALUES ('Soccer');
INSERT INTO categories (name) VALUES ('Basketball');
INSERT INTO categories (name) VALUES ('Baseball');
INSERT INTO categories (name) VALUES ('Frisbee');
INSERT INTO categories (name) VALUES ('Snowboarding');
INSERT INTO categories (name) VALUES ('Rock Climbing');
INSERT INTO categories (name) VALUES ('Foosball');
INSERT INTO categories (name) VALUES ('Skating');
INSERT INTO categories (name) VALUES ('Hockey');

INSERT INTO users (name, email) VALUES ('SYSTEM', 'SYSTEM');

insert into items (title, description, cat_id, user_id) values ('Soccer Cleats','The shoes', 1, 1);
insert into items (title, description, cat_id, user_id) values ('Jersey','The shirt', 1, 1);
insert into items (title, description, cat_id, user_id) values ('Bat','The bat', 3, 1);
insert into items (title, description, cat_id, user_id) values ('Frisbee','The flying disc', 4, 1);
insert into items (title, description, cat_id, user_id) values ('Shinguards','Guard yo shins!', 1, 1);
insert into items (title, description, cat_id, user_id) values ('Two shinguards','Buy one get one half off!', 1, 1);
insert into items (title, description, cat_id, user_id) values ('Snowboard','The board on which you snow', 5, 1);
insert into items (title, description, cat_id, user_id) values ('Goggles','The goggles', 5, 1);
insert into items (title, description, cat_id, user_id) values ('Stick','The stick', 9, 1);
