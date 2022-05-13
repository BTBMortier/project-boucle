import postgresql

conn = psycopg2.connect(dbname="boucled", user="postgres",
                        password="password", host="localhost")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS topics(
    pk_id serial PRIMARY KEY,
    author VARCHAR(16) NOT NULL,
    title  VARCHAR(256) NOT NULL,
    mod_title VARCHAR(256),
    day INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    time VARCHAR(10) NOT NULL )

""")

cur.execute("""CREATE TABLE IF NOT EXISTS posts(
    pk_id serial PRIMARY KEY,
    author VARCHAR(16) NOT NULL,
    page INT NOT NULL,
    post_id INT NOT NULL,
    FOREIGN KEY (topic_id)
        REFERENCES topics (topic_id),
    post_text VARCHAR(20000),
    day INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    time VARCHAR(10) NOT NULL )

""")
