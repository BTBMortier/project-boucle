#!/usr/bin/env python
# coding: utf-8

# In[14]:


import re 
import os
import json
import shutil
import psycopg2
from bs4 import BeautifulSoup

from pyspark.sql import Row
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType,IntegerType
from pyspark.sql.functions import udf,col,regexp_extract,regexp_replace

conf = SparkConf()  # create the configuration
conf.set("spark.jars", "postgresql-42.2.6.jar")

sc = SparkSession \
    .builder \
    .config("spark.driver.extraClassPath", "./postgresql-42.2.6.jar") \
    .appName("boucled") \
    .getOrCreate()

sqlsc = SQLContext(sc)


# In[15]:


in_path  = "/usr/src/app/project-boucle/pipeline/boucled_scrapers/spiders/out/topics"
out_path = "/usr/src/app/project-boucle/pipeline/boucled_scrapers/spiders/out/topics/processed" 
topics_df = sqlsc.read.json(in_path)
#Relier date/heure du premier d'un id topic a l'entrée topic dans la postgres avec un 
#rownum
final_df = topics_df.select("author", "title", "mod_title", "topic_id")
final_df = final_df.withColumn("topic_id",final_df["topic_id"].cast(IntegerType()))
final_df.write.format('jdbc').options(
  url='jdbc:postgresql://localhost:5432/boucled',
  driver='org.postgresql.Driver',
  dbtable='topics',
  user='postgres',
  password='password').mode('append').save()

conn = psycopg2.connect(dbname="boucled", user="postgres",
                        password="password", host="localhost")
conn.autocommit = True 
cur = conn.cursor()
cur.execute("""
DELETE FROM topics
WHERE pk_id IN
    (SELECT pk_id
    FROM
        (SELECT pk_id,
        ROW_NUMBER() OVER(PARTITION BY title 
        ORDER BY pk_id) AS row_num
        FROM topics) temp_table
        WHERE temp_table.row_num > 1);
""")
cur.execute("""
UPDATE topics AS t 

SET 
year = ts.year,
month = ts.month,
day = ts.day,
time = ts.time

FROM
(SELECT * FROM 
(SELECT 
topic_id,
day,
month,
year,
time,
ROW_NUMBER() OVER (PARTITION BY topic_id ORDER BY post_id) AS row
FROM posts) AS temp_table 
WHERE temp_table.row = 1 ) AS ts 
WHERE t.topic_id = ts.topic_id 
""")
cur.close()
conn.close()


# In[ ]:


out_dir = os.listdir(in_path)
for file_name in out_dir:
    shutil.move(os.path.join(in_path, file_name), out_path)

