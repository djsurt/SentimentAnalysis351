import sys
import json
from pymongo import MongoClient
import certifi
# Parse the command-line argument (the filename of the JSON file)
if len(sys.argv) < 2:
    print("Usage: python insert_doc.py <json_file>")
    sys.exit(1)
json_file = sys.argv[1]

# Load the JSON data from the file
try:
    with open(json_file, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"File '{json_file}' not found.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"File '{json_file}' contains invalid JSON.")
    sys.exit(1)

# Connect to the MongoDB server hosted on MongoDB Atlas
client = MongoClient('mongodb+srv://dms310:**@cluster0.5jbvjg8.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=certifi.where())

# Select the database and collection
db = client['Sentiment_Analysis_db']
collection = db['sentiments']

# Insert the JSON document into the MongoDB collection
result = collection.insert_one(data)

# Print the ID of the newly inserted document
print(f"Inserted document with ID: {result.inserted_id}")

# Retrieve all documents from the collection
documents = collection.find()

# Loop through the documents and print them
for document in documents:
    print(document)

# Close the connection to the MongoDB server
client.close()

