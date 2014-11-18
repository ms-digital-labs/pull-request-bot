import json
import logging
import requests

from flask import Flask, request
from os import environ

logging.getLogger().addHandler(logging.StreamHandler())

app = Flask(__name__)

OAUTH_TOKEN = environ["OAUTH_TOKEN"]
AUTH_HEADER = "token {0}".format(OAUTH_TOKEN)

def template_for(repository):
    return open('{0}.md'.format(repository), 'r').read()

def post_comments_to(url, repository):
    headers = {
        'Authorization': AUTH_HEADER,
        'content-type': 'application/json',
    }
    data = {
        'body': template_for(repository),
    }
    return requests.post(url, headers=headers, data=json.dumps(data))


@app.route("/pull_request", methods=['POST'])
def pull_request():
    print  request.json
    if request.json["action"] == "opened":
        comments_url = request.json["pull_request"]["comments_url"]
        repository = request.json["repository"]["full_name"]
        post_comments_to(comments_url, repository)
        return "ok"
    else:
        return "Thanks, but I don't care"

if __name__ == "__main__":
    app.run(port=environ.get("PORT"), host='0.0.0.0')
