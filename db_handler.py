from pymongo import MongoClient
import configparser

class DBHandler:
    def __init__(self, config_file, section):
        # Read the config.ini file
        config = configparser.ConfigParser()
        config.read(config_file)

        # Get the MongoDB connection details from the specified section
        mongodb_url = config.get(section, "url")
        mongodb_username = config.get(section, "username")
        mongodb_password = config.get(section, "password")
        mongodb_database = config.get(section, "database")
        mongodb_collection = config.get(section, "collection")

        # Construct the connection string
        connection_string = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_url}/{mongodb_database}"
        print(connection_string)
        # Create a MongoDB client
        try:
            # Create a MongoDB client
            self.client = MongoClient(connection_string)

            # Access the specified database and collection
            self.db = self.client[mongodb_database]
            self.collection = self.db[mongodb_collection]
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")


        # Access the specified database and collection
        self.db = self.client[mongodb_database]
        self.collection = self.db[mongodb_collection]

    @staticmethod
    def flatten_dict(data):
        flattened = {}
        for key, value in data.items():
            if key == 'urls':
                flattened[key] = value
            elif key == 'payload':
                for i, payload_dict in enumerate(value, start=1):
                    for inner_key, inner_value in payload_dict.items():
                        flattened[f"payload_{inner_key}{i}"] = inner_value
        print(flattened)
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
        result = self.collection.insert_one(self.flatten_dict(data))
        return str(result.inserted_id)
