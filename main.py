from base64 import b64decode
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
GITHUB_REQUEST_HEADERS = {
    'Authorization': AUTH_HEADER,
    'content-type': 'application/json',
}
MERGE_CHECKLIST_API_PATH =\
    "https://api.github.com/repos/{}/contents/.merge_checklist.md"


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
    data = {
        'body': body,
    }
    headers = GITHUB_REQUEST_HEADERS
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()


def extract_template_from_repo(repository, ref="master"):
    """
    Loads the `.merge_checklist.md` file from the root of the given repo.
    :param repository: Full repository path (username/repository).
    :param ref: Git reference.
    """
    url = MERGE_CHECKLIST_API_PATH.format(repository)
    headers = GITHUB_REQUEST_HEADERS
    response = requests.get(url, headers=headers, params={"ref": ref})
    response.raise_for_status()
    return b64decode(response.json()["content"])


def template_from_request_json(json):
    """
    Uses the request JSON to get the merge checklist from the git repo
    :param json: A github pull request webhook notification JSON.
    """
    pull_request = json["pull_request"]
    pr_head_ref = pull_request["head"]["ref"]
    repo_name = pull_request["head"]["repositiory"]["full_name"]
    return extract_template_from_repo(repo_name, pr_head_ref)


@app.route("/", methods=['GET'])
def home():
    """
    A blank home page so I don't need to panic every time I visit it.
    """
    return "everything is ok"


@app.route("/pull_request", methods=['POST'])
def pull_request():
    """
    Respond to github's webhook calls. We ignore anything other than new PRs.

    The github API just cares about the HTTP status code, no response body is
    needed.
    """
    event_type = request.headers["X-GitHub-Event"]
    action = request.json["action"]
    template_name = request.args.get("comment_template", "default")

    if action == "opened" and event_type == "pull_request":
        comments_url = request.json["pull_request"]["comments_url"]
        try:
            template = template_from_request_json(request.json)
        except requests.exceptions.HTTPError:
            template = template_for(template_name)
        post_comments_to(comments_url, template)
        return "ok"
    else:
        return "Thanks, but I don't care"


if __name__ == "__main__":
    app.run(port=environ.get("PORT"), host='0.0.0.0')
