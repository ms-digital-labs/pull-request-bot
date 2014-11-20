# PR Bot.
[ ![Codeship Status for ms-digital-labs/gif-bot](https://codeship.com/projects/6187b380-52c6-0132-d85e-6600710ca99c/status)](https://codeship.com/projects/48721)

Deploy it, with `OAUTH_TOKEN` set to a valid Github OAuth token, and add a
webhook that triggers on pull request creation pointing to
`/pull_request?comment_template=plusplus` on your instance, and it'll post a
message from the `plusplus.md` template in the comment section of all new pull
requests.

Remember, whatever account you wire it up to, must have access to actually make
the comment.
