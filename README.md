## Item Catalog Application

### How to run it?

First, to create the database in your PostgreSQL database server, use the command `psql -f catalog.sql`.

Next, download your own `client_secrets.json` file from [Google APIs Console](https://console.developers.google.com/apis). Help on that is available in [this YouTube video](https://www.youtube.com/watch?v=8aGoty0VXgw).

Then, simply run `python application.py` and go to http://localhost:5000 to view the application running locally.

### What's it do?

The sql script will create the catalog database and then create 3 tables: categories, users, and items.

#### categories
| Column        | Type          | Description                       |
| ------------- | ------------- | --------------------------------- |
| cat_id        | integer       | auto-incrementing category id     |
| name          | text          | name of the category              |

#### users
| Column        | Type          | Description                        |
| ------------- | ------------- | ---------------------------------- |
| user_id       | integer       | auto-incrementing user id          |
| name          | text          | name of the user                   |
| email         | text          | email address of the user          |
| picture       | text          | url to profile picture of the user |


#### items
| Column      | Type                     | Description                  |
| ----------- | ------------------------ | ---------------------------- |
| item_id     | integer                  | auto-incrementing item id    |
| title       | text                     | item title                   |
| description | text                     | item description             |
| date_added  | timestamp with time zone | date and time item was added |
| cat_id      | integer                  | id of item's category        |
| user_id     | integer                  | id of user who added item    |

The python script will run the flask api on port 5000 of your local host.

To view the web app in your browser, go to http://localhost:5000.

A JSON endpoint of the catalog is available at http://localhost:5000/catalog/JSON.
