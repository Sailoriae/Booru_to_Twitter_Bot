#!/usr/bin/python3
# coding: utf-8

import tweepy


def connect_to_twitter ( api_key, api_secret, oauth_token, oauth_token_secret ) :
    auth = tweepy.OAuthHandler( api_key, api_secret )
    auth.set_access_token( oauth_token, oauth_token_secret )
    api = tweepy.API( auth, wait_on_rate_limit = True )
    return api
