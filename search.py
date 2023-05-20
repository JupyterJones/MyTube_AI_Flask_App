from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# load the conversations JSON file
with open('static/chat/conversations.json', 'r') as f:
    conversations = json.load(f)

@app.route('/search')
def search():
    # get the search query from the request parameters
    query = request.args.get('q')

    # search the conversations for the query
    results = []
    for conversation in conversations:
        if 'messages' in conversation:
            for message in conversation['messages']:
                if 'content' in message and query.lower() in message['content'].lower():
                    results.append(message)

    # return the search results as JSON
    return jsonify(results)