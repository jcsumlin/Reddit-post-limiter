from datetime import datetime, timedelta

import praw

from praw.exceptions import RedditAPIException
from loguru import logger
import configparser
import os
config = configparser.ConfigParser()
config.read("config.ini")

reddit = praw.Reddit(client_id=config.get("reddit", "client_id", fallback=os.environ.get("CLIENT_ID")),
                     client_secret=config.get("reddit", "client_secret", fallback=os.environ.get("CLIENT_SECRET")),
                     user_agent="Post limiter",
                     username=config.get("reddit", "mod_username", fallback=os.environ.get("MOD_USERNAME")),
                     password=config.get("reddit", "mod_password", fallback=os.environ.get("MOD_PASSWORD"))
                     )

MAX_POSTS = int(config.get("rule", "max_posts", fallback=os.environ.get("MAX_POSTS", 5)))
COOLDOWN_HRS = int(config.get("rule", "cooldown_in_hours", fallback=os.environ.get("COOLDOWN_IN_HOURS", 5)))

REMOVAL_REASON_ID = config.get("rule", "removal_reason_id", fallback=os.environ.get("REMOVAL_REASON_ID"))
SUBREDDIT = config.get("rule", "subreddit", fallback=os.environ.get("SUBREDDIT"))


class Post:
    def __init__(self, author_id, post_time, post_id):
        self.author_id = author_id
        self.post_time = datetime.utcfromtimestamp(post_time)
        self.post_id = post_id


users = {}
if not SUBREDDIT:
    logger.exception("No Subreddit set, set one in the environment variables or config.ini file")
subreddit = reddit.subreddit(SUBREDDIT)
for submission in subreddit.stream.submissions():
    if submission.author.is_mod:
        logger.debug("Post is by mod, ignoring")
        continue
    # Track posts for users
    post = Post(submission.author.id, submission.created_utc, submission.id)
    if submission.author.id not in users.keys():
        users[submission.author.id] = [post]
    else:
        users[submission.author.id].append(post)

    first_post = users[submission.author.id][0]
    if len(users[submission.author.id]) > MAX_POSTS:  # 5 Post Max
        if (datetime.utcnow() - timedelta(hours=COOLDOWN_HRS)) < first_post.post_time:
            logger.info(f"Post violates frequency rule {submission.id}")
            if REMOVAL_REASON_ID:
                try:
                    reason = subreddit.mod.removal_reasons[REMOVAL_REASON_ID]
                    submission.mod.remove(reason_id=reason.id)
                except praw.exceptions.RedditAPIException as e:
                    logger.exception(f"Could not remove post properly: {e}", )
                    pass
            else:
                submission.mod.remove()

            timeleft = (first_post.post_time + timedelta(hours=COOLDOWN_HRS))
            submission.mod.remove()
            comment = submission.reply(f"Hey there {submission.author.name}, your post has been removed because you're "
                                       f"posting too frequently. Our rules request that you only post {MAX_POSTS} posts"
                                       f" every {COOLDOWN_HRS} hours.\nYou need to wait until {timeleft} UTC to post "
                                       f"again \n\nThis action was preformed automatically if you feel it was in error "
                                       f"please reply to this comment.")
            comment.mod.distinguish(sticky=True)
            logger.success("Successfully Removed and commented")
            users[submission.author.id].pop()
        else:
            users[submission.author.id].pop(0)
            logger.debug("Popped from list")
