import pymongo
import json

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.5")
db = client["Courses"]
collection = db["physics"]

with open("courses.json") as file:
    courses = json.load(file)
# print(courses)
collection.create_index("name")


"""adding a new field"""
for course in courses:
    course['rating'] = {'total':0, 'count': 0}
    for chapter in course['chapters']:
        chapter['rating'] = {'total':0, 'count': 0}
    collection.insert_one(course)

client.close()

