#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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


# In[ ]:


def clean_timestamp(timestamp):
    months = {
        "janvier":"01",
        "février":"02",
        "mars":"03",
        "avril":"04",
        "mai":"05",
        "juin":"06",
        "juillet":"07",
        "août":"08",
        "septembre":"09",
        "octobre":"10",
        "novembre":"11",
        "décembre":"12"}
    day_regex  = "(\d{2})\s[^à]" #first group only
    year_regex = "\d{4}"
    time_regex = "\d{2}:\d{2}:\d{2}"
    day_regex  = re.compile(day_regex)
    year_regex = re.compile(year_regex)
    time_regex = re.compile(time_regex)
    day = day_regex.search(timestamp).group(1)
    year = year_regex.search(timestamp).group(0)
    time = time_regex.search(timestamp).group(0).replace(":","")
    final_timestamp = f"{day}-{month}-{year}-{time}"
    return final_timestamp
    
def clean_post_text(post_text):
    #Parsing html
    clean_text = ""
    soup = BeautifulSoup(post_text,"html.parser")
    for tag in soup("blockquote.blockquote-jv"):
        tag.clear()
        
    #Boucler sur la liste d'élements à l'envers est le meilleur moment 
    for elem in list(soup)[::-1]:
        if elem.name == "p":
            clean_text += elem.get_text()
        else:
            break
    
    return clean_text


# In[ ]:


in_path  = "/usr/src/app/project-boucle/src/boucled_scrapers/spiders/out/posts"
out_path = "/usr/src/app/project-boucle/src/boucled_scrapers/spiders/out/posts/processed" 
posts_df = sqlsc.read.json(in_path)
timestamp_regex = "(\d{2})\s(\D{3,9})\s(\d{4})\s[à]\s(\d{2}:\d{2}:\d{2})"
#g1:day|g2:month|g3:year|g4:time
months = {
        "janvier":"01",
        "février":"02",
        "mars":"03",
        "avril":"04",
        "mai":"05",
        "juin":"06",
        "juillet":"07",
        "août":"08",
        "septembre":"09",
        "octobre":"10",
        "novembre":"11",
        "décembre":"12"}
months_udf = udf(lambda x : months[x],StringType())
posts_df = posts_df.withColumn("day", regexp_extract(col("timestamp"),timestamp_regex,1))
posts_df = posts_df.withColumn("month", regexp_extract(col("timestamp"),timestamp_regex,2))
posts_df = posts_df.withColumn("month",months_udf(col("month")))
posts_df = posts_df.withColumn("year", regexp_extract(col("timestamp"),timestamp_regex,3))
posts_df = posts_df.withColumn("time", regexp_extract(col("timestamp"),timestamp_regex,4))

udf_clean_text = udf(lambda x : clean_post_text(x),StringType())
posts_df = posts_df.withColumn("post_text",udf_clean_text(col("post_text")))


# In[ ]:


final_df = posts_df.select("author", "page", "post_id", 
                "post_text", "topic_id", "day",
                "month", "year","time")
final_df = final_df.withColumn("post_id",final_df["post_id"].cast(IntegerType()))
final_df = final_df.withColumn("topic_id",final_df["topic_id"].cast(IntegerType()))
final_df = final_df.withColumn("day",final_df["day"].cast(IntegerType()))
final_df = final_df.withColumn("month",final_df["month"].cast(IntegerType()))
final_df = final_df.withColumn("year",final_df["year"].cast(IntegerType()))
#output_df = df_cust.withColumn("zip",df_cust["zip"].cast(StringType()))
final_df.write.format('jdbc').options(
  url='jdbc:postgresql://localhost:5432/boucled',
  driver='org.postgresql.Driver',
  dbtable='posts',
  user='postgres',
  password='password').mode('append').save()

conn = psycopg2.connect(dbname="boucled", user="postgres",
                        password="password", host="localhost")
conn.autocommit = True 
cur = conn.cursor()
cur.execute("""
DELETE FROM posts
WHERE pk_id IN
    (SELECT pk_id
    FROM
        (SELECT pk_id,
        ROW_NUMBER() OVER(PARTITION BY post_text 
        ORDER BY pk_id) AS row_num
        FROM posts) temp_table
        WHERE temp_table.row_num > 1);
""")
cur.close()
conn.close()


# In[ ]:


out_dir = os.listdir(in_path)
for file_name in out_dir:
    shutil.move(os.path.join(in_path, file_name), out_path)


# In[ ]:




