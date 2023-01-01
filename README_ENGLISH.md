# Booru to Twitter Bot

There are many bots on Twitter publishing illustrations or fanarts from image databases. However, I find a big flaw in them : They credit the artists badly, if at all. That's why for a few years, I maintained my own Twitter bots. They are now stopped and deleted, but their source code is available here.

The script of this repository allows to publish regularly on Twitter illustrations coming from [Danbooru](https://danbooru.donmai.us) or [Derpibooru](https://derpibooru.org). Each Tweet contains the name of the artist, a link to the illustration on the image database, and if available a link to the source of this illustration. If this source is a Tweet, it will be retweeted. It is possible to make even more retweets by using an [Artists on Twitter Finder](https://github.com/Sailoriae/Artists_on_Twitter_Finder) (AOTF) server, which can search if the artist has already tweeted the illustration that the script is about to publish. Otherwise, AOTF also allows to put a link to the artist's Twitter account, if they have one.

To create such a Twitter bot, you must first :
1. Have "[Elevated](https://developer.twitter.com/en/portal/products/elevated)" access to the Twitter API.
2. Create an app on the "[developer portal](https://developer.twitter.com/en/portal)". This allows you to get a key pair `api_key` and `api_secret`.
3. Create a Twitter account that will be the one where the illustrations will be published. This will be the account of your bot, so it is recommended to declare it as "[automated](https://help.twitter.com/en/using-twitter/automated-account-labels)".
4. Generate the access keys to this account with the [`get_oauth_token.py`](get_oauth_token.py) script. This gives you a key pair `oauth_token` and `oauth_token`.

With these four keys you have access to your bot account through the Standard API. In order to be able to publish illustrations automatically, you need to create a Python script that calls the `booru_to_twitter.launch()` function. The parameters of this function are detailed in the table below, and an example of use is available in the [`example.py`](example.py) script. Then you can run your script automatically with a Cron task, for example once an hour. Note that if your bot tweets more than once per hour, its Tweets will no longer be indexed in the Twitter search.

| Parameter        | Type        | Default value  | Description
| ---------------- | ----------- | -------------- | -----------
| `request`        | `str`       | Mandatory      | Query to send to the image database.
| `api_key`        | `str`       | Mandatory      | Token of the app on the Twitter Standard API.
| `api_secret`     | `str`       | Mandatory      | Secret of the app's token.
| `oauth_token`    | `str`       | Mandatory      | OAuth token of the Twitter account to use.
| `oauth_secret`   | `str`       | Mandatory      | Secret of the OAuth token.
| `database`       | `str`       | `"derpibooru"` | The image database to use : `"derpibooru"` or `"danbooru"`.
| `post_new_first` | `bool`      | `False`        | Publish in priority the latest images in the database.
| `add_hashtags`   | `str`       | `""`           | Hashtags to add when creating the Tweet.
| `aotf_api_base`  | `str`       | `None`         | URL of the AOTF server API to use.
| `only_retweets`  | `bool`      | `False`        | Do not repost, only retweet.
| `sfw_bot`        | `bool`      | `False`        | Do not RT or QRT Tweets that are tagged or detected as NSFW.
| `max_relaunchs`  | `int`       | `3`            | Maximum number of relaunches after a retweet.
| `filter_tags`    | `List[str]` | `None`         | Do not tweet or retweet an image containing one of these tags.
| `lock_actions`   | `bool`      | `False`        | Do not actually tweet or retweet.

The query passed to the `request` parameter allows to select in the image database illustrations containing tags, or more precisely which answer a boolean expression. These illustrations are chosen randomly if the `post_new_first` parameter is set to `False`, or if all recent images have been published. The filter passed to the `filter_tags` parameter allows to refine this selection by eliminating illustrations containing one or more tags of the filter. Examples of queries and filters are available in the [`queries_and_filters`](queries_and_filters) directory.

Since AOTF is free software, you can use someone else's server, or install your own. Check [its repository](https://github.com/Sailoriae/Artists_on_Twitter_Finder) for more information. The API URL should look like `https://sub.domain.tld/api/` for a public AOTF server, or `http://localhost:3301/` to use your local server. Leave the `aotf_api_base` parameter at `None` to not use an AOTF server, but that's not so nice for artists who are on Twitter.

The `only_retweets` parameter forbids the script to do republications, and thus to do only retweets. It is not recommended to set it to `True` if you don't have an AOTF server, because Tweets would be found only via the source of the illustrations on the image database used, which is rarely a Tweet.

Note that if you want your bot to publish only SFW illustrations, your query must specify this to the image database. To do so, add the expression `(~rating:general ~rating:safe)` to your query for Danbooru, and the `safe` tag for Derpibooru. The `sfw_bot` parameter only prevents retweeting or quoting Tweets tagged or detected as NSFW.

Finally, I've noticed that most people don't care if a bot credits the artists properly since they just want to consume illustrations or fanarts. That's why these kind of bots are bad for artists, because they take away more visibility than they bring to them.

PS : Don't forget to install the required Python modules : `pip install -r requirements.txt`
