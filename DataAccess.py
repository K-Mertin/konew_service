import pymongo
import datetime
import time
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import configparser
import logging
import os
from Logger import Logger
from werkzeug.security import generate_password_hash, check_password_hash


class DataAccess:

    def __init__(self):
        self.Setting()
        self.logger = Logger('DataAccess-Flask')
        self.client = MongoClient(
            self.ipAddress, username=self.user, password=self.password, authSource=self.dbName)
        self.db = self.client['konew']
        # self.logger.info( 'Initialized')

    def Setting(self):
        self.config = configparser.ConfigParser()
        with open('Config.ini') as file:
            self.config.readfp(file)

        self.ipAddress = self.config.get('Mongo', 'ipAddress')
        self.dbName = self.config.get('Mongo', 'dbName')
        self.user = self.config.get('Mongo', 'user')
        self.password = self.config.get('Mongo', 'password')


if __name__ == "__main__":
    db = DataAccess()
