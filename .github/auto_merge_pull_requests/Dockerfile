# auto_merge_pull_requests/Dockerfile
FROM python:3-alpine

MAINTAINER Mikel Larreategi <larreategi@eibar.org>

LABEL "com.github.actions.name"="Auto-merge pull requests"
LABEL "com.github.actions.description"="Merge the pull request after the checks pass"
LABEL "com.github.actions.icon"="activity"
LABEL "com.github.actions.color"="green"

COPY merge_pr.py /
ENTRYPOINT ["python3", "/merge_pr.py"]