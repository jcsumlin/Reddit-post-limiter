# Reddit-post-limiter
Limit the number of posts per n hours your members can submit.

This bot can be run in docker or using the python console.
See config.ini.example for all the environment variables that you will need to set if you are using docker (uppercase ofcourse).
If you are running locally without docker here is how you run it
- Clone the repo
- Copy the `config.ini.example` files and name it `config.ini`
- Fill out all the required values (lines with a `;` at the beginning are commented out and will fall back to OS environment variables)


If you are running this with docker just make sure all the ENV variables are set and you'll be good to go!


# Links:

[Removal Reason ID](https://praw.readthedocs.io/en/latest/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.remove) 
