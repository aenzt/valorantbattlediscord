from pymongo import MongoClient
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('auth', 'discordtoken')
mongosrv = config.get('auth', 'mongosrv')

cluster = MongoClient(mongosrv, tls=True, tlsAllowInvalidCertificates=True)
db = cluster['ValorantBot']
collection = db['agent']
user_coll = db['user']
user_weapon = user_coll['weapons']
weapons = db['weapons']
ranks = ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Immortal', 'Radiant']