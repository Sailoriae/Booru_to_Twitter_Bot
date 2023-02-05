🇫🇷 Ce script utilise l'API Twitter v1.1, qui est devenue payante en février 2023 (Tout comme l'API v2).  
🇬🇧 This script uses the Twitter API v1.1, which became paid in February 2023 (Just like the API v2).


# Booru to Twitter Bot

*If you don't speak French, you can read the [English translation of this file](README_ENGLISH.md).*

Il existe sur Twitter de nombreux robots publiant des illustrations ou des fanarts venant de banques d'images. Cependant, je leur trouve un gros défaut : Ils créditent mal les artistes, voir même pas du tout. C'est pour cela que pendant quelques années, j'ai maintenu mes propres robots Twitter. Ils sont aujourd'hui arrêtés et supprimés, mais leur code source est disponible ici.

Le script de ce dépôt permet de publier régulièrement sur Twitter des illustrations venant de [Danbooru](https://danbooru.donmai.us) ou [Derpibooru](https://derpibooru.org). Chaque Tweet contient le nom de l'artiste, un lien vers l'illustrations dans la banque d'images, et si disponible un lien vers la source de cette illustration. Si cette source est un Tweet, il sera retweeté. Il est possible de faire encore plus de retweets en utilisant un serveur [Artists on Twitter Finder](https://github.com/Sailoriae/Artists_on_Twitter_Finder) (AOTF), qui permet de rechercher si l'artiste a déjà tweeté l'illustration que le script s'apprête à publier. Dans le cas contraire, AOTF permet aussi de mettre un lien vers le compte Twitter de l'artiste, si iel en a un.

Pour créer un tel robot Twitter, vous devez d'abord :
1. Posséder un accès "[Elevated](https://developer.twitter.com/en/portal/products/elevated)" à l'API Twitter.
2. Créer une app sur le "[portail développeur](https://developer.twitter.com/en/portal)". Cela vous permet d'obtenir un couple de clés `api_key` et `api_secret`.
3. Créer un compte Twitter qui sera celui où les illustrations seront publiées. Ce sera le compte de votre robot, il est donc recommandé de le déclarer comme "[automatisé](https://help.twitter.com/en/using-twitter/automated-account-labels)".
4. Générer les clés d'accès à ce compte avec le script [`get_oauth_token.py`](get_oauth_token.py). Cela vous permet d'obtenir un couple de clés `oauth_token` et `oauth_token`.

Avec ces quatre clés, vous avez accès au compte de votre robot via l'API Standard. Pour pouvoir y publier des illustrations automatiquement, vous devez créer un script Python qui appelle la fonction `booru_to_twitter.launch()`. Les arguments de cette fonctions sont détaillés dans le tableau ci-dessous, et un exemple d'utilisation est disponible dans le script [`example.py`](example.py). Puis vous pouvez exécuter votre script automatiquement avec une tâche Cron, par exemple une fois par heure. Notez que si votre robot tweete plus d’une fois par heure, ses Tweets ne seront plus indexés dans la recherche Twitter.

| Argument         | Type        | Valeur par défaut | Description
| ---------------- | ----------- | ----------------- | -----------
| `request`        | `str`       | Obligatoire       | Requête à envoyer à la banque d'images.
| `api_key`        | `str`       | Obligatoire       | Token de l'app sur l'API Twitter Standard.
| `api_secret`     | `str`       | Obligatoire       | Secret du token de l'app.
| `oauth_token`    | `str`       | Obligatoire       | Token OAuth pour le compte Twitter à utiliser.
| `oauth_secret`   | `str`       | Obligatoire       | Secret du token OAuth.
| `database`       | `str`       | `"derpibooru"`    | Banque d'images à utiliser : `"derpibooru"` ou `"danbooru"`.
| `post_new_first` | `bool`      | `False`           | Publier en priorité les dernières images en date dans la banque.
| `add_hashtags`   | `str`       | `""`              | Hashtags à ajouter lors de la création du Tweet.
| `aotf_api_base`  | `str`       | `None`            | URL de l'API du serveur AOTF à utiliser.
| `only_retweets`  | `bool`      | `False`           | Ne pas faire de republication, seulement retweeter.
| `sfw_bot`        | `bool`      | `False`           | Ne pas RT ou QRT des Tweets étiquetés ou détectés comme NSFW.
| `max_relaunchs`  | `int`       | `3`               | Nombre maximum de relancements après un retweet.
| `filter_tags`    | `List[str]` | `None`            | Ne pas tweeter ou retweeter une image contenant un de ces tags.
| `lock_actions`   | `bool`      | `False`           | Ne pas réellement tweeter ni retweeter.

La requête passée à l'argument `request` permet de sélectionner dans la banque d'images des illustrations contenant des étiquettes, ou plus précisément qui répondent à une expression booléenne. Ces illustrations sont choisies aléatoirement si l'argument `post_new_first` est à `False`, ou bien si toutes les images récentes ont été publiées. Le filtre passé à l'argument `filter_tags` permet d'affiner cette sélection en éliminant des illustrations contenant une ou plusieurs étiquettes du filtre. Des exemples de requêtes et de filtres sont disponibles dans le répertoire [`queries_and_filters`](queries_and_filters).

Comme AOTF est un logiciel libre, vous pouvez utiliser le serveur de quelqu'un d'autre, ou bien installer le vôtre. Consultez [son dépôt](https://github.com/Sailoriae/Artists_on_Twitter_Finder) pour plus d'informations. L'URL de l'API devrait ressembler à `https://sub.domain.tld/api/` pour un serveur AOTF publique, ou bien à `http://localhost:3301/` pour utiliser votre serveur local. Laissez l'argument `aotf_api_base` à `None` pour ne pas utiliser de serveur AOTF, mais c'est moins sympa pour les artistes présents sur Twitter.

L'argument `only_retweets` interdit au script de faire des republications, et donc de faire uniquement des retweets. Il n'est pas recommandé de le mettre sur `True` si vous n'avez pas de serveur AOTF, car les Tweets seraient trouvés uniquement via la source des illustrations sur la banque d'image utilisée, qui est rarement un Tweet.

Notez que si vous souhaitez que votre robot publie uniquement des illustrations SFW, votre requête doit le préciser à la banque d'image. Pour se faire, ajoutez l'expression `(~rating:general ~rating:safe)` à votre requête pour Danbooru, et l'étiquette `safe` pour Derpibooru. L'argument `sfw_bot` permet uniquement d'éviter de retweeter ou de citer des Tweets étiquetés ou détectés comme NSFW.

Pour finir, j'ai remarqué que la majorité des gens s'en fichent qu'un robot crédite proprement les artistes puisqu'ils veulent juste consommer des illustrations ou des fanarts. C'est pour cela que ce genre de robots sont néfastes aux artistes, puisqu'ils leurs retirent plus de visibilité qu'ils leurs en apporte.

PS : Pensez aussi à installer les modules Python requis : `pip install -r requirements.txt`
