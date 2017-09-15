#!/usr/bin/python
#
# Joey Lee


import psycopg2
DBNAME = "newsdata"


def get_mostviewed():
    """Gets the row with the article and number of views it got."""
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()

    # Gets (title, total views) of the most viewed article
    c.execute("select title, count(path) as views \
               from log left join articles \
               on log.path LIKE '%' || articles.slug \
               where log.path LIKE '/article/%' \
               group by title \
               order by views desc \
               limit 1;")
    posts = c.fetchone()
    db.close()
    return posts


def get_popular_author():
    """Gets the row with an author and number of views."""
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    # Join articles and authors to include the author's name
    # then count the number of views each author gets.
    c.execute("select name, count(name) as views \
               from (select slug, name \
               from articles join authors \
               on articles.author = authors.id) as most_viewed \
               join log \
               on log.path LIKE '%' || most_viewed.slug \
               where log.path LIKE '/article/%' \
               group by most_viewed.name \
               order by views desc \
               limit 1;")
    posts = c.fetchone()
    db.close()
    return posts


def get_percent_error():
    """Gets the row with a date and a fraction of errors over total."""
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    # Creates a view of date and total requests that day.
    c.execute("create view total_views as \
                   select date(time), count(date(time)) as total_count \
                   from log \
                   group by date(time);")
    # Creates a view of date and requests resulting in errors that day.
    c.execute("create view error_views as \
                   select date(time), count(date(time)) as error_count \
                   from log \
                   where status != '200 OK' \
                   group by date(time);")
    # Joins the two views and gets the percent of error requests.
    c.execute("select total_views.date, \
               round(error_count/total_count::numeric, 3) as percent_error \
               from total_views join error_views \
               on total_views.date = error_views.date \
               where round(error_count/total_count::numeric, 3) > 0.01;")
    posts = c.fetchone()
    db.close()
    return posts
