import json
import logging
import requests
import globbing

from flask import Flask, request
from os import environ

logging.getLogger().addHandler(logging.StreamHandler())

app = Flask(__name__)

OAUTH_TOKEN = environ["OAUTH_TOKEN"]
AUTH_HEADER = "token {0}".format(OAUTH_TOKEN)

def template_path_for(name):
    return "templates/{0}.md".format(name)

def template_for(name):
    files = glob.glob(template_path_for('*'))
    expected_path = template_path_for(name)
    if expected_path in files:
        return open(expected_path, 'r').read()
    else:
        raise LookupError("Could not find the specified template")

def post_comments_to(url, template):
    headers = {
        'Authorization': AUTH_HEADER,
        'content-type': 'application/json',
    }
    data = {
        'body': template,
    }
    return requests.post(url, headers=headers, data=json.dumps(data))


@app.route("/pull_request", methods=['POST'])
def pull_request():
    print  request.json
    if request.json["action"] == "opened":
        comments_url = request.json["pull_request"]["comments_url"]
        template = template_for(request.args.get("comment_template", "default"))
        post_comments_to(comments_url, template)
        return "ok"
    else:
        return "Thanks, but I don't care"

if __name__ == "__main__":
    app.run(port=environ.get("PORT"), host='0.0.0.0')
