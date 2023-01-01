#!/usr/bin/python3
# coding: utf-8

"""
pip install -r requirements.txt
crontab -e
@hourly python3 /path/to/example.py
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

api_key = "api_key"
api_secret = "api_secret"
oauth_token = "oauth_token"
oauth_token_secret = "oauth_token_secret"

database = "derpibooru"
request = "score.gt:200 AND safe"
filter_tags = open( "queries_and_filters/derpibooru_filter.txt", "r" ).read().splitlines()
sfw_bot = True

post_new_first = False
aotf_api_base = None

from booru_to_twitter import launch
launch ( request,
         api_key,
         api_secret,
         oauth_token,
         oauth_token_secret,
         database = database,
         post_new_first = post_new_first,
         aotf_api_base = aotf_api_base,
         sfw_bot = sfw_bot,
         filter_tags = filter_tags )
