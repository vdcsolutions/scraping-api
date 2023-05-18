from pymongo import MongoClient
import configparser

class DBHandler:
    def __init__(self, config_file, section):
        # Read the config.ini file
        config = configparser.ConfigParser()
        config.read(config_file)

        # Get the MongoDB connection details from the specified section
        mongodb_url = config.get("MONGODB", "url")
        mongodb_username = config.get("MONGODB", "username")
        mongodb_password = config.get("MONGODB", "password")
        mongodb_database = config.get("MONGODB", "database")
        mongodb_collection = config.get("MONGODB", "collection")

        # Construct the connection string
        connection_string = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_url}/{mongodb_database}"

        # Create a MongoDB client
        self.client = MongoClient(connection_string)

        # Access the specified database and collection
        self.db = self.client[mongodb_database]
        self.collection = self.db[mongodb_collection]
    @staticmethod
    def flatten_dict(data, parent_key='', sep='.'):
        flattened = {}
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                flattened.update(DBHandler.flatten_dict(v, new_key, sep=sep))
            else:
                flattened[new_key] = v
        return flattened

    @staticmethod
    def expand_dict(data, sep='.'):
        expanded = {}
        for k, v in data.items():
            keys = k.split(sep)
            nested_dict = expanded
            for key in keys[:-1]:
                nested_dict.setdefault(key, {})
                nested_dict = nested_dict[key]
            nested_dict[keys[-1]] = v
        return expanded

    def insert_data(self, data):
        result = self.collection.insert_one(flatten(data))
        return str(result.inserted_id)
