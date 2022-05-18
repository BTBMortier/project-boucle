import psycopg2

conn = psycopg2.connect(dbname="boucled", user="postgres",
                        password="password", host="localhost")
conn.autocommit = True 
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS topics(
    pk_id serial PRIMARY KEY,
    topic_id INT NOT NULL,
    author VARCHAR(16) NOT NULL,
    title  VARCHAR(256) NOT NULL,
    mod_title VARCHAR(1),
    day INT,
    month INT,
    year INT,
    time VARCHAR(10))

""")

cur.execute("""CREATE TABLE IF NOT EXISTS posts(
    pk_id serial PRIMARY KEY,
    author VARCHAR(16) NOT NULL,
    page INT NOT NULL,
    post_id INT NOT NULL,
    topic_id INT NOT NULL,
    post_text VARCHAR(20000),
    day INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    time VARCHAR(10) NOT NULL )

""")

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    pk_id serial PRIMARY KEY,
    nickname VARCHAR(16) NOT NULL,
    signature VARCHAR(8192),
    pp_hash VARCHAR(20000) NOT NULL )

""")

cur.close()
conn.close()
