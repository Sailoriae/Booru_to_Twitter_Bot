#!/usr/bin/python3
# coding: utf-8

from .class_AOTF_Client import AOTF_Client, Max_Processing_Requests_On_Server, Timeout_Reached


# Longueur d'un URL dans le décompte des caractères d'un Tweet
# Source : https://developer.twitter.com/en/docs/counting-characters
URL_LENGTH = 23


"""
@param result Objet "Result_from_DB", image de la BDD à traiter.
@param add_hashtags Hashtags à mettre en plus, sont placés en premier.
@param aotf_client Objet "AOTF_Client". N'utilise pas AOTF sinon.
@param avoid_nsfw_tweets Essayer de ne pas citer des Tweets NSFW.
"""
# Attention : Ne pas modifier le format du Tweet sans savoir comment on
# l'utilise dans la fonction "tweet_media()" :
# - La ligne "Source" peut être supprimée si l'URL est détectée comme nuisible
#   par Twitter (Pas la ligne "DB" ni "Source + DB").
def generate_tweet( result,
                    add_hashtags : str = "",
                    aotf_client : AOTF_Client = None,
                    avoid_nsfw_tweets : bool = False ) :
    tweet_text = ""
    tweet_length = 0
    
    # Mettre en cache la source
    result_source = result.source
    if ( result.explicit_source and # Si la source est marquée comme NSFW
         result.source_is_tweet and # Et qu'on a détecté que c'est un Tweet
         avoid_nsfw_tweets # Et qu'on doit éviter de citer des Tweet NSFW
        ) :
        result_source = None
    
    # Tous les caractères comptes, sauf les URL qui valent forcément URL_LENGTH caractères
    # ATTENTION : Les "\n" comptent aussi !
    # On calcul la place qu'on doit garder pour mettre la source
    # Voir plus bas pourquoi on a ces valeurs
    if result_source != None :
        keep_for_source = 16 + 2*URL_LENGTH
    else :
        keep_for_source = 15 + URL_LENGTH
    
    # Mettre les noms des artistes
    # On n'en met aucun si jamais on n'a pas la place, afin de ne pas faire de favoritisme
    if len( result.artists_credits ) > 0 and 11 + len( result.artists_credits ) <= 280 - keep_for_source :
        tweet_text = "Credits : " + result.artists_credits + "\n"
        tweet_length += 11 + len( result.artists_credits )
    
    # Mettre les comptes Twitter des artites grâce à AOTF
    # On n'en met aucun si jamais on n'a pas la place, afin de ne pas faire de favoritisme
    if aotf_client != None :
        print( "Recherche des comptes Twitter des artistes sur \"Artists on Twitter Finder\"." )
        try :
            twitter_accounts = aotf_client.get_twitter_accounts( result.db_source )
        except (Max_Processing_Requests_On_Server, Timeout_Reached) :
            twitter_accounts = None
        if twitter_accounts != None :
            twitter_account_string = ""
            twitter_account_string_length = 0
            for twitter_account in twitter_accounts :
                twitter_account_string += "Twitter : https://twitter.com/" + twitter_account["account_name"] + "\n"
                twitter_account_string_length += 11 + URL_LENGTH
            if tweet_length + twitter_account_string_length <= 280 - keep_for_source :
                tweet_text += twitter_account_string
                tweet_length += twitter_account_string_length
    
    # Mettre les sources de l'image
    # Si on modifie ces textes, il faut modifier le calcul de la variable "keep_for_source"
    if result_source != None :
        tweet_text += "Source : " + result_source + "\n"
        tweet_text += "DB : " + result.db_source + "\n"
    else :
        tweet_text += "Source + DB : " + result.db_source + "\n"
    tweet_length += keep_for_source
    
    # Mettre les hashtags imposés
    no_hashtag = False
    if add_hashtags != "" :
        if len( add_hashtags ) <= 280 - tweet_length :
            tweet_text += add_hashtags
            tweet_text += " "
            tweet_length += len( add_hashtags ) + 1 # On compte le dernier espace
        # On ne met pas d'autre hashtags si on ne peut pas mettre ceux imposés
        else :
            no_hashtag = True
    
    # Finir de remplir les 280 caractères du Tweet en mettant les hashtags dépendant de l'image trouvée
    hashtag_id = 0
    while ( hashtag_id < len( result.hashtags ) and
            tweet_length + len( result.hashtags[hashtag_id] ) + 1 <= 280 and
            not no_hashtag ) :
        tweet_text += result.hashtags[hashtag_id] + " "
        tweet_length += len( result.hashtags[hashtag_id] ) + 1 # On compte le dernier espace
        hashtag_id += 1
    
    # Supprimer le dernier caractère, qui est soit un " ", soit un "\n"
    tweet_text = tweet_text[:-1]
    
    return tweet_text
