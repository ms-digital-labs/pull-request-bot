import glob
import json
import logging
from os import environ

from flask import Flask, request
import requests

logging.getLogger().addHandler(logging.StreamHandler())

app = Flask(__name__)

OAUTH_TOKEN = environ["OAUTH_TOKEN"]
AUTH_HEADER = "token {}".format(OAUTH_TOKEN)


def _template_path_for(name):
    return "templates/{}.md".format(name)


def template_for(name):
    """
    Gets the contents of the named template file.
    """
    files = glob.glob(_template_path_for('*'))
    expected_path = _template_path_for(name)
    if expected_path in files:
        with open(expected_path, 'r') as template_file:
            return template_file.read()
    else:
        raise LookupError("Could not find the specified template")


def post_comments_to(url, body):
    """
    Given a comments URL and a comment body, create a new comment.
    """
    headers = {
        'Authorization': AUTH_HEADER,
        'content-type': 'application/json',
    }
    data = {
        'body': body,
    }
    return requests.post(url, headers=headers, data=json.dumps(data))


@app.route("/pull_request", methods=['POST'])
def pull_request():
    event_type = request.headers["X-GitHub-Event"]
    action = request.json["action"]
    template_name = request.args.get("comment_template", "default")

    if action == "opened" and event_type == "pull_request":
        comments_url = request.json["pull_request"]["comments_url"]
        template = template_for(template_name)
        post_comments_to(comments_url, template)
        return "ok"
    else:
        return "Thanks, but I don't care"


if __name__ == "__main__":
    app.run(port=environ.get("PORT"), host='0.0.0.0')
