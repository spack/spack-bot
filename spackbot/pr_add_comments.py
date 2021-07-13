# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import logging
import random
import re

from gidgethub import routing


logger = logging.getLogger(__name__)
router = routing.Router()

# Aliases for spackbot so spackbot doesn't respond to himself
aliases = ["spack-bot", "spackbot", "spack-bot-develop"]
alias_regex = "(%s)" "|".join(aliases)


def say_hello():
    """
    Respond to saying hello.
    """
    messages = [
        "Hello!",
        "Hi! How are you?",
        "👋️",
        "Hola!",
        "Hey there!",
        "Howdy!",
        "こんにちは！",
    ]
    return random.choice(messages)


commands_message = """
You can interact with me in many ways! 

- `@spackbot hello`: say hello and get a friendly response back!
- `@spackbot help` or `@spackbot commands`: see this message 

I'll also help to label your pull request and assign reviewers!
If you need help or see there might be an issue with me, open an issue [here](https://github.com/spack/spack-bot/issues)
"""


@router.register("issue_comment", action="created")
@router.register("issue_comment", action="edited")
async def add_comments(event, gh, *args, session, **kwargs):
    """Respond to messages to spackbot"""

    # We can only tell PR and issue comments apart by this field
    if "pull_request" not in event.data["issue"]:
        return

    # spackbot should not respond to himself!
    if re.search(alias_regex, event.data["comment"]["user"]["login"]):
        return

    # Respond with appropriate messages
    comment = event.data["comment"]["body"]

    # @spackbot hello
    message = None
    if re.search("@spackbot hello", comment):
        logger.info(f"Responding to hello message {comment}...")
        message = say_hello()

    # @spackbot commands OR @spackbot help
    elif re.search("@spackbot (commands|help)", comment):
        logger.debug("Responding to request for help commands.")
        message = commands_message

    if message:
        await gh.post(event.data["issue"]["comments_url"], {}, data={"body": message})
