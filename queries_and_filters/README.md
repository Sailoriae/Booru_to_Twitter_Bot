# Requêtes et filtres

*If you don't speak French, you can read the [English translation of this file](README_ENGLISH.md).*

[Danbooru](https://danbooru.donmai.us) et [Derpibooru](https://derpibooru.org) sont des banques d'images très bien organisées, où chaque illustration est associée à une liste d'étiquettes décrivant son contenu. Une requête sur ces banques d'images permet de sélectionner des illustrations contenant des étiquettes, ou plus précisément qui répondent à une expression booléenne. Un filtre permet d'affiner cette sélection en éliminant des illustrations contenant une ou plusieurs étiquettes du filtre.

Notez qu'un filtre peut être directement inclus dans une requête. Mais comme Danbooru limite par défaut les recherches à deux étiquettes, mon code a été construit de manière à séparer les requêtes et le filtre. Cela permet d'avoir des requêtes simples, tout en ayant des filtres précis.


## Requêtes

Une requête est une expression booléenne permettant de sélectionner le contenu à publier. Elle est alors passée à l'argument `request` sous la forme d'une chaine de caractères.

Voici quelques exemples de requêtes :
* Illustrations SFW venant de Derpibooru : `score.gt:200 AND safe`
* Illustrations SFW de Miku venant de Danbooru : `hatsune_miku (~rating:safe ~rating:general)`

Définir un score minimum dans la requête est un préfiltrage de fainéant, mais c'est très efficace sur Derpibooru pour obtenir uniquement des illustrations de bonne qualité. En revanche, son efficacité est bien plus faible sur Danbooru, où les scores sont généralement bas.


## Filtres

Un filtre est une liste d'étiquettes permettant de ne pas voir des illustrations contenant au moins une de ces étiquettes. Il est alors être passé à l'argument `filter_tags` sous la forme d'une liste de chaines de caractères.

Durant les années d'existence de mes robots, j'ai pu peaufiner mes propres filtres pour Danbooru et Derpibooru. Ceux-ci reflètent en partie des valeurs et des goûts personnels, c'est pour cela que je vous recommande de les consulter avant de les utiliser. En effet, ces filtres permettent avant tout d'éliminer du contenu considéré comme déviant ou étrange par une majorité de personnes, mais ils éliminent aussi du contenu que je n'apprécie pas ou que je juge de mauvaise qualité, et donc que je n'avais pas envie de voir partagé par mes robots. Notez que ces filtres ne sont pas faits pour éliminer le contenu NSFW, c'est la requête qui doit sélectionner du contenu SFW ou NSFW.

Ces filtres sont stockés sous la forme de deux listes d'étiquettes, qui sont respectivement le [filtre pour Danbooru](danbooru_filter.txt) et [celui pour Derpibooru](derpibooru_filter.txt). Un filtre doit être chargés avant d'appeler la fonction `launch()` :
```python3
filter_tags = open( "queries_and_filters/booru_filter.txt", "r" ).read().splitlines()
```
Ne chargez pas le filtre pour Danbooru si vous utilisez Derpibooru, et inversement. En effet, les étiquettes sont différentes sur ces deux banques, c'est pour cela qu'il y a deux filtres différents.

Notes sur le filtre pour Danbooru :
* Les étiquettes `6+boys`, `6+girls` et `everyone` sont filtrées car mon robot utilisant Danbooru était centré sur un personnage.
* Les étiquettes `child`, `randoseru`, et `younger` sont filtrées car elles contiennent des illustrations représentant des enfants de manière trop suggestive.

Note importante : La fonctionnalité de filtres sur Derpibooru n'est pas utilisée (Comme si vous avez activé le filtre "[Everything](https://derpibooru.org/filters/56027)" sur leur interface web). Ainsi, pour que votre robot publie uniquement du contenu SFW, vous pouvez reconstruire le filtre "[Default](https://derpibooru.org/filters/100073)" et l'inclure dans la liste de l'argument `filter_tags`. Ou bien, vous pouvez aussi mettre l'étiquette `safe` dans votre requête.

De plus, si vous utilisez Derpibooru comme banque d'images, notez que liste de l'argument `filter_tags` peut contenir des expression booléennes (Il y en a dans mon filtre). En effet, le filtre est ajouté à la requête, et envoyé à l'API Derpibooru. Voir l'implémentation de la fonction [`get_on_derpibooru()`](../booru_to_twitter/function_get_on_derpibooru.py#L103) pour plus de détails. Ceci n'est pas valable si vous utilisez Danbooru !
