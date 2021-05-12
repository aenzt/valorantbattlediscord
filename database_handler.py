import pymongo
from pymongo import MongoClient


cluster = MongoClient("mongodb+srv://aenzt:katasandi321@cluster0.gichf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster['ValorantBot']
collection = db['agent']

post = {
    "_id" : 1,
    "name" : "Raze",
    "ava_URL" : "https://images.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt6fef56a8182d0a81/5ebf2c2798f79d6925dbd6b4/V_AGENTS_587x900_ALL_Raze_2.png",
    "rating" : 25,
    "type" : "Agent"
}

collection.insert_one(post)