from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client["boucled"]

topics_coll = db["topics"]
dummy_topic = {"author":"test",
               "timestamp": "test",
               "title": "test",
               "topic_hash":"test"}
if int(db.topics.find({"titre_hash":"test"}).count()) == 0:
    db.topics.insert(dummy_topic)

posts_coll  = db["posts"]
dummy_post = {"author":"test",
               "timestamp": "test",
               "post": "test",
               "post_hash":"test"}
if int(db.posts.find({"post_hash":"test"}).count()) == 0:
    db.posts.insert(dummy_post)

user_info  = db["users"]
dummy_user = {"pseudo":"test",
              "date_creation":"test",
              "date_scrape":"test",
              "num_messages":"test"}
if int(db.user_info.find({"pseudo":"test"}).count()) == 0:
    db.users.insert(dummy_user)

