# Queries and filters

[Danbooru](https://danbooru.donmai.us) and [Derpibooru](https://derpibooru.org) are very well organized image databases, where each illustration is associated with a list of tags describing its content. A query on these image databases allows to select illustrations containing tags, or more precisely which answer a boolean expression. A filter allows to refine this selection by eliminating illustrations containing one or more tags of the filter.

Note that a filter can be directly included in a query. But since Danbooru limits queries to two tags by default, my code was built to separate the queries and the filter. This allows for simple queries, while still having precise filters.


## Queries

A query is a boolean expression used to select the content to publish. It is then passed to the `request` parameter as a string.

Here are some examples of queries :
* SFW illustrations from Derpibooru : `score.gt:200 AND safe`
* SFW illustrations of Miku from Danbooru : `hatsune_miku (~rating:safe ~rating:general)`

Setting a minimum score in the query is a lazy pre-filtering, but it is very efficient on Derpibooru to get only good quality illustrations. On the other hand, it is much less effective on Danbooru, where the scores are generally low.


## Filters

A filter is a list of tags allowing to not see illustrations containing at least one of these tags. It is then passed to the `filter_tags` parameter as a list of strings.

During the years of existence of my bots, I have been able to refine my own filters for Danbooru and Derpibooru. These filters reflect in part personal values and tastes, so I recommend that you consult them before using them. Indeed, these filters are primarily used to remove content considered deviant or strange by a majority of people, but they also remove content that I don't like or that I consider to be of poor quality, and therefore that I didn't want to see shared by my bots. Note that these filters are not designed to remove NSFW content, it is the query that must select SFW or NSFW content.

These filters are stored as two lists of tags, which are respectively the [filter for Danbooru](danbooru_filter.txt) and the [one for Derpibooru](derpibooru_filter.txt). A filter must be loaded before calling the `launch()` function :
```python3
filter_tags = open( "queries_and_filters/booru_filter.txt", "r" ).read().splitlines()
```
Do not load the filter for Danbooru if you use Derpibooru, and vice versa. This is because the tags are different on these two databases, so there are two different filters.

Notes on the filter for Danbooru :
* The tags `6+boys`, `6+girls` and `everyone` are filtered because my bot using Danbooru was character-centric.
* The tags `child`, `randoseru`, and `younger` are filtered because they contain illustrations depicting children in a too suggestive way.

Important note : The filter feature on Derpibooru is not used (As if you have enabled the "[Everything](https://derpibooru.org/filters/56027)" filter on their web interface). So, to make your bot publish only SFW content, you can rebuild the "[Default](https://derpibooru.org/filters/100073)" filter and include it in the list of the `filter_tags` parameter. Alternatively, you can put the `safe` tag in your query.

Also, if you are using Derpibooru as an image bank, note that the list in the `filter_tags` parameter can contain boolean expressions (There are some in my filter). Indeed, the filter is added to the request, and sent to the Derpibooru API. Check the implementation of the [`get_on_derpibooru()`](../booru_to_twitter/function_get_on_derpibooru.py#L103) function for more details. This is not valid if you use Danbooru !
