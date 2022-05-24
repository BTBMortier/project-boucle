from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.papermill.operators.papermill import PapermillOperator

from datetime import datetime, timedelta


with DAG("forum_etl",
        start_date=datetime(2022,5,18),
        schedule_interval=timedelta(minutes=1),
        catchup=False
        ) as dag:

    scrape_topics = BashOperator(
            task_id = "scrape_topics",
            bash_command = """
            cd /usr/src/app/project-boucle/src/boucled_scrapers/spiders;
            scrapy crawl topics -O topics.jl;
            """
            )
    scrape_posts = BashOperator(
            task_id = "scrape_posts",
            bash_command = """
            cd /usr/src/app/project-boucle/src/boucled_scrapers/spiders;
            scrapy crawl posts;
            """
            )
    transform_load_posts = BashOperator(
            task_id = "transload_posts",
            bash_command = "python3 /usr/src/app/project-boucle/src/boucled_etl/tl_posts.py"
            )
    transform_load_topics = BashOperator(
            task_id = "transload_topics",
            bash_command = "python3 /usr/src/app/project-boucle/src/boucled_etl/tl_topics.py"
            )

scrape_topics >> scrape_posts >> transform_load_posts >> transform_load_topics
