#!/usr/bin/python3
# coding: utf-8

import tweepy
from time import sleep
from enum import Enum

import re
tweet_url_regex = re.compile(
    r"^https?:\/\/(?:mobile\.)?twitter\.com\/(?:(?:#!\/)?(?:@)?[a-zA-Z0-9_]+\/|(?:i\/web\/))status\/([0-9]+)" )
# Ne pas marquer la fin de la chaine

from .class_AOTF_Client import AOTF_Client, Max_Processing_Requests_On_Server, Timeout_Reached


"""
Rechercher si c'est la source est un Tweet.
@param result Objet "Result_from_DB", image de la BDD à traiter.
@return None, ou l'ID du Tweet.
"""
def search_tweet_id ( result ) :
    if result.source == None :
        return None
    regex = re.search( tweet_url_regex, result.source )
    if regex != None : return regex.group( 1 )
    return None


"""
@param api Objet "Tweepy.API".
@param tweet_id L'ID du Tweet à retweeter.
@param bot_name "Screen name" du compte Twitter du robot.
@param do_not_retweet Ne pas réellement retweeter.
@param RETRY_ONCE Réessayer dans 10 secondes en cas d'erreur inconnue.
@return Retweeted.TRUE si on a retweeté, Retweeted.FALSE sinon.
        Retweeted.ALREADY si on a déjà retweeté.
"""
class Retweeted ( Enum ) :
    FALSE = 0
    TRUE = 1
    ALREADY = 2
def retweet ( api : tweepy.API,
              tweet_id : int,
              bot_name : str,
              do_not_retweet : bool = False,
              RETRY_ONCE : bool = True ) :
    try :
        if not do_not_retweet :
            api.retweet( tweet_id )
        print( "Tweet retweeté : " + str( tweet_id ) )
        return Retweeted.TRUE
    
    # Note : TwitterServerError hérite de HTTPException
    except tweepy.errors.HTTPException as exception :
        if 130 in exception.api_codes : # Over capacity
            print( "Problème sur les serveurs de Twitter. On réessaye dans 10 secondes..." )
            sleep( 10 )
            return retweet( api, tweet_id, bot_name, RETRY_ONCE = True )
        
        print( "Impossible de retweeter : " + str( tweet_id ) )
        
        if 326 in exception.api_codes or 64 in exception.api_codes :
            raise Exception( "Compte Twitter " + bot_name + " bloqué" )
        if 327 in exception.api_codes : # Déjà RT
            return Retweeted.ALREADY
        if 144 in exception.api_codes : # Tweet introuvable
            return Retweeted.FALSE
        if 179 in exception.api_codes : # On ne peut pas accéder à ce Tweet (Peut-être que le compte est en privé)
            return Retweeted.FALSE
        if 328 in exception.api_codes : # Le retweet n'est pas possible pour ce Tweet (Pourquoi ? C'est pas documenté)
            return Retweeted.FALSE
        if 136 in exception.api_codes : # "You have been blocked from retweeting this user's tweets at their request." (Qu'est ce que ça veut dire ? On est bloqué par cet utilisateur ? C'est une nouvelle fois pas documenté)
            return Retweeted.FALSE
        
        if exception.api_codes == [] and RETRY_ONCE : # Peut-être une erreur de connexion ? On réessaye dans 10 secondes
            print( "Erreur inconnue lors du retweet. On réessaye dans 10 secondes..." )
            sleep( 10 )
            return retweet( api, tweet_id, bot_name, RETRY_ONCE = False )
        
        raise exception


"""
Vérifier si des Tweets sont détectables comme NSFW.
@param api Objet "Tweepy.API".
@param tweets_ids Liste de Tweets.
@param aggressive Moins de faux-négatifs, plus de faux-positifs.
@return Dictionnaire ID du Tweet -> True si NSFW, False sinon.
        Certains IDs peuvent manquer si ces Tweets ne sont pas accessibles.
"""
NSFW_HASHTAGS = [ "nsfw", "nsfwtwt", "nsfwart", "clop" ]
def check_nsfw_hashtags ( api : tweepy.API, tweets_ids,
                          aggressive : bool = False ) :
    to_return = {}
    for tweet in api.lookup_statuses( tweets_ids,
                                      include_entities = True,
                                      trim_user = True ) :
        is_nsfw = False
        for hashtag in tweet._json["entities"]["hashtags"] :
            if hashtag["text"] in NSFW_HASHTAGS :
                is_nsfw = True
        if tweet._json["possibly_sensitive"] and aggressive :
            is_nsfw = True
        to_return[ int(tweet.id) ] = is_nsfw
    return to_return


"""
@param result Objet "Result_from_DB", image de la BDD à traiter.
@param api Objet "Tweepy.API".
@param bot_name "Screen name" du compte Twitter du robot.
@param aotf_client Objet "AOTF_Client". N'utilise pas AOTF sinon.
@parma avoid_nsfw_tweets Essayer de ne pas retweeter des Tweets NSFW.
@param do_not_retweet Ne pas réellement retweeter.
@param already_retweeted_is_success Retourner True si on l'a déjà retweeté.
@return True si on a retweeté, False sinon.
"""
def try_to_retweet ( result,
                     api : tweepy.API,
                     bot_name : str,
                     aotf_client : AOTF_Client = None,
                     avoid_nsfw_tweets : bool = False,
                     do_not_retweet : bool = False,
                     already_retweeted_is_success : bool = True ) :
    """
    D'abord, si la source de l'image est un Tweet, on essaye de le RT.
    """
    source_tweet_id = search_tweet_id( result )
    if source_tweet_id != None :
        result.source_is_tweet = True
        source_tweet_id = int( source_tweet_id )
        
        # Rechercher avant dans les hashtags du Tweet s'il est NSFW
        if not ( avoid_nsfw_tweets and result.explicit_source ) :
            is_nsfw = check_nsfw_hashtags( api, [ source_tweet_id ] )
            if source_tweet_id in is_nsfw and is_nsfw[source_tweet_id] :
                result.explicit_source = True
        
        if not ( avoid_nsfw_tweets and result.explicit_source ) : # Ne pas RT des sources NSFW
            retweeted = retweet( api, source_tweet_id, bot_name,
                                 do_not_retweet = do_not_retweet )
            if retweeted == Retweeted.TRUE :
                return True
            if retweeted == Retweeted.ALREADY :
                return already_retweeted_is_success
        
        else :
            print( f"Le Tweet ID {source_tweet_id} (Source) a été détecté comme NSFW." )
    else :
        result.source_is_tweet = False
    
    """
    Sinon, on peut utiliser "Artists on Twitter Finder".
    """
    if aotf_client != None :
        print( "Recherche des Tweets des artistes sur \"Artists on Twitter Finder\"." )
        try :
            tweets = aotf_client.get_tweets( result.db_source,
                                             timeout = 1800 ) # Timeout de 30 minutes
        except (Max_Processing_Requests_On_Server, Timeout_Reached) :
            tweets = None
        if tweets != None and len(tweets) > 0 :
            # Regarder si AOTF a retourné la source (Qui est un Tweet)
            aotf_returned_source = False
            if source_tweet_id != None :
                for tweet in tweets :
                    if int( tweet["tweet_id"] ) == int( source_tweet_id ) :
                        aotf_returned_source = True
                        break
            
            # Rechercher avant dans les hashtags des Tweet s'ils sont NSFW
            are_nsfw = {}
            if avoid_nsfw_tweets :
                if not aotf_returned_source or len( tweets ) > 1 : # Ne pas refaire la même vérification
                    are_nsfw = check_nsfw_hashtags( api, [ tweet["tweet_id"] for tweet in tweets ] )
            
            # On essaye chaque Tweet retourné par AOTF, car il est possible
            # qu'il retourne des Tweets supprimés
            for tweet in tweets :
                if avoid_nsfw_tweets : # Sécurités pour ne pas RT du NSFW
                    if ( aotf_returned_source and # Si AOTF retourne le même Tweet que la source
                         result.explicit_source ) : # Et que la source était marquée comme NSFW
                        continue # On passe ce Tweet
                    
                    tweet_id = int( tweet["tweet_id"] )
                    if tweet_id in are_nsfw and are_nsfw[tweet_id] : # Si le Tweet a été détecté comme NSFW
                        print( f"Le Tweet ID {tweet_id} a été détecté comme NSFW." )
                        continue # On passe ce Tweet
                
                retweeted = retweet( api, tweet["tweet_id"], bot_name,
                                     do_not_retweet = do_not_retweet )
                if retweeted == Retweeted.TRUE :
                    return True
                if retweeted == Retweeted.ALREADY :
                    return already_retweeted_is_success
        
        else :
            print( "AOTF n'a trouvé aucun Tweet pour cette image." )
    
    """
    Si on n'a toujours pas réussi à RT, on retourne False.
    """
    return False
