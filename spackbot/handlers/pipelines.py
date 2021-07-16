# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import logging
import requests
import os

from spackbot.helpers import found, gitlab_spack_project_url, spack_gitlab_url

logger = logging.getLogger(__name__)

# We can only make the request with a GITLAB TOKEN
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")


async def run_pipeline(event, gh):
    """
    Make a request to re-run a pipeline.
    """
    # Early exit if not authenticated
    if not GITLAB_TOKEN:
        return "I'm not able to re-run the pipeline now because I don't have authentication."

    # Get the pull request number
    pr_url = event.data["issue"]["pull_request"]["url"]
    number = pr_url.split("/")[-1]

    # We need the pull request branch
    response = requests.get(pr_url)
    pr = response.json()

    # Get the sender of the PR - do they have write?
    sender = event.data["sender"]["login"]
    repository = event.data["repository"]
    collaborators_url = repository["collaborators_url"]
    author = pr["user"]["login"]

    # If it's the PR author, we allow it
    if author == sender:
        logger.info(f"Author {author} is requesting a pipeline run.")

    # If they don't have write, we don't allow the command
    elif not await found(gh.getitem(collaborators_url, {"collaborator": sender})):
        logger.info(f"Not found: {sender}")
        return (
            "Sorry %s, I cannot do that for you. Only users with write can make this request!"
            % sender
        )

    # We need the branch name plus number to assemble the GitLab CI
    branch = pr["head"]["ref"]
    branch = "github/pr%s_%s" % (number, branch)

    url = "%s/pipeline?ref=%s" % (gitlab_spack_project_url, branch)
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    response = requests.post(url, headers=headers)
    result = response.json()
    if "detailed_status" in result and "details_path" in result["detailed_status"]:
        url = "%s/%s" % (spack_gitlab_url, result["detailed_status"]["details_path"])
        return "I've started that [pipeline](%s) for you!" % url
    return "I had a problem triggering the pipeline."
