#!/usr/bin/python3
# coding: utf-8

import os
import requests
import tweepy
from time import sleep


"""
@param api Objet "Tweepy.API".
@param tweet_text Texte du Tweet à publier.
@param file_name Chemin vers le média à publier.
@param bot_name "Screen name" du compte Twitter du robot.
@param do_not_tweet Ne pas réellement envoyer l'image.
@param RETRY_ONCE Réessayer dans 10 secondes en cas d'erreur inconnue.
@return True si réussite, False si l'image est trop grande.
        Emet des exceptions sinon.
"""
def tweet_media ( api : tweepy.API,
                  tweet_text : str,
                  file_name : str,
                  bot_name : str,
                  do_not_tweet : bool = False,
                  RETRY_ONCE : bool = True ) :
    try :
        if not do_not_tweet :
            api.update_status_with_media( filename = file_name, status = tweet_text )
        return True
    
    # Note : TwitterServerError hérite de HTTPException
    except tweepy.errors.HTTPException as exception :
        if 130 in exception.api_codes : # Over capacity
            print( "Problème sur les serveurs de Twitter. On réessaye dans 10 secondes..." )
            sleep( 10 )
            return tweet_media( api, tweet_text, file_name, bot_name, RETRY_ONCE = True )
        
        if 326 in exception.api_codes or 64 in exception.api_codes :
            raise Exception( "Compte Twitter " + bot_name + " bloqué" )
        
        if exception.response.status_code == 413 : # Payload Too Large
            print( "Image trop grande !" )
            return False
        
        if 193 in exception.api_codes : # One or more of the uploaded media is too large
            print( "Image trop grande !" )
            return False
        
        if 324 in exception.api_codes : # Image dimensions must be >= 4x4 and <= 8192x8192
            print( "Image trop grande (Ou trop petite)" )
            return False
        
        if 186 in exception.api_codes : # Tweet needs to be a bit shorter
            print( "Tweet trop long !" )
            message = "Tweet trop long ! On a tenté de publier le Tweet suivant :\n"
            message += "==========\n"
            message += tweet_text.replace("\n", "\\n\n") + "\n"
            message += "=========="
            raise Exception( message ) from exception
        
        if 429 in exception.api_codes : # This link has been identified by Twitter or our partners as being potentially harmful
            new_tweet_text = ""
            has_source = False
            for line in tweet_text.split( "\n" ) : # Bidouille pour virer la source
                if line[:8] == "Source :" :
                    has_source = True
                else :
                    new_tweet_text += line + "\n"
            if not has_source :
                message = "Lien problématique ! On a tenté de publier le Tweet suivant :\n"
                message += "==========\n"
                message += tweet_text.replace("\n", "\\n\n") + "\n"
                message += "=========="
                raise Exception( message ) from exception
            return tweet_media( api, new_tweet_text, file_name, bot_name, RETRY_ONCE = True )
        
        if exception.api_codes == [] and RETRY_ONCE : # Peut-être une erreur de connexion ? On réessaye dans 10 secondes
            print( "Erreur inconnue lors de la publication. On réessaye dans 10 secondes..." )
            sleep( 10 )
            return tweet_media( api, tweet_text, file_name, bot_name, RETRY_ONCE = False )
        
        raise exception


"""
@param result Objet "Result_from_DB", image de la BDD à traiter.
@param api Objet "Tweepy.API".
@param tweet_text Texte du Tweet à publier.
@param bot_name "Screen name" du compte Twitter du robot.
                Est utilisé comme nom de fichier temporaire.
@param do_not_tweet Ne pas réellement tweeter.
@return True si réussite, False si l'image est trop grande.
        Emet des exceptions sinon.
"""
def write_image_and_post_to_twitter ( result,
                                      api : tweepy.API,
                                      tweet_text : str,
                                      bot_name : str,
                                      image_size : str = "large",
                                      do_not_tweet : bool = False ) :
    # On met l'extension pour aider la détection MIME du type de fichier
    _, ext = os.path.splitext( result.large ) # ext = ".ext" ou chaine vide si pas d'extension
    file_name = "temp_" + bot_name + "_" + str(os.getpid()) + ext # Prendre le PID pour éviter des problèmes
    file = open(file_name, "wb")
    
    if image_size == "large" :
        file.write(requests.get(result.large).content)
    elif image_size == "medium" :
        file.write(requests.get(result.medium).content)
    elif image_size == "small" :
        file.write(requests.get(result.small).content)
    else :
        raise Exception( "Paramètre \"image_size = " + str(image_size) + "\" inconnu" )
    
    file.close()
    
    to_return = True
    if not do_not_tweet :
        try :
            to_return = tweet_media( api, tweet_text, file_name, bot_name, do_not_tweet = do_not_tweet )
        except Exception as exception :
            os.remove(file_name)
            raise exception
    
    os.remove(file_name)
    return to_return


"""
Partager l'image dans un nouveau Tweet.

@param result Objet "Result_from_DB", image de la BDD à traiter.
@param api Objet "Tweepy.API".
@param tweet_text Texte du Tweet à publier.
@param bot_name "Screen name" du compte Twitter du robot.
                Est utilisé comme nom de fichier temporaire.
@param do_not_tweet Ne pas réellement tweeter.
"""
def post_to_twitter( result, api, tweet_text, bot_name, do_not_tweet = False ) :
    success = write_image_and_post_to_twitter( result, api, tweet_text, bot_name, image_size = "large", do_not_tweet = do_not_tweet )
    if not success :
        if result.medium != None :
            success = write_image_and_post_to_twitter( result, api, tweet_text, bot_name, image_size = "medium", do_not_tweet = do_not_tweet )
        if not success :
            if result.small != None :
                success = write_image_and_post_to_twitter( result, api, tweet_text, bot_name, image_size = "small", do_not_tweet = do_not_tweet )
            if not success :
                print( "Abandon, l'image est trop grande." )
            else :
                print( "Réussite en small !" )
        else :
            print( "Réussite en medium !" )
    else :
        print( "Réussite en large !" )
    
    print( "Tweet envoyé :\n" + tweet_text )
