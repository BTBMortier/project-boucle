from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client["boucled"]

topics_coll = db["topics"]
dummy_topic = {"test":"test"}
if int(db.topics.find({"test":"test"}).count()) == 0:
    db.topics.insert(dummy_topic)

posts_coll  = db["posts"]
dummy_post = {"test":"test"}
if int(db.posts.find({"test":"test"}).count()) == 0:
    db.posts.insert(dummy_post)

user_info  = db["users"]
dummy_user = {"test":"test"}
if int(db.user_info.find({"test":"test"}).count()) == 0:
    db.users.insert(dummy_user)

