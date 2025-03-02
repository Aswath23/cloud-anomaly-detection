from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["myDatabase"]  # Change this to your DB name

print("Connected to MongoDB!")