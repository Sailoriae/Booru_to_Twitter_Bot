#!/usr/bin/python3
# coding: utf-8

from typing import List

from .function_connect_to_twitter import connect_to_twitter
from .class_AOTF_Client import AOTF_Client, Server_Connection_Not_Initialised, Error_During_Server_Connection_Init
from .function_get_DB_image import get_DB_image
from .function_try_to_retweet import try_to_retweet
from .function_generate_tweet import generate_tweet
from .function_post_to_twitter import post_to_twitter


# Passer ce paramètre à True pour empêcher tous les bots de tweeter ou de
# retweeter. Cela permet de débugger plus facilement.
DEV_MODE = False


"""
Fonction principale, permet de lancer la publication d'images sur Twitter.
Ces publications peuvent être soit une republication / repost de l'image, soit
un retweet si on a pu trouver le Tweet de l'artiste contenant cette image.

@param request Requête à envoyer à la base de données d'images.
@param api_key Token de l'application sur l'API v1.1 Twitter.
@param api_secret Secret du token de l'application.
@param oauth_token Token OAuth sur le compte Twitter à utiliser.
@param oauth_secret Secret du token OAuth.
@param database Nom de la base de données d'images à utiliser.
                Liste des BDD actuellement implémentées :
                - Derpibooru,
                - Danbooru.
@param post_new_first Doit-on poster les dernières images en date dans la BDD
                      en premier ? Si toutes les images ont été partagées (Ou
                      que ce paramètre est à "False"), on en prend une
                      aléatoirement.
                      Ne fonctionne que si notre implémentation à la BDD le
                      supporte !
@param add_hashtags Hashtags à ajouter lors de la création du Tweet. Ils sont
                    alors placés en premier.
@param aotf_api_base URL de l'API du serveur "Artists on Twitter Finder" (AOTF)
                     à utiliser. Permet de chercher si l'artiste a un compte
                     Twitter afin de le retweeter au lieu de le reposter. Si il
                     a un compte mais n'a pas posté l'illustration choisie,
                     l'URL de son compte Twitter sera insérée dans notre Tweet.
                     Régler à "None" désactive l'utilisation d'AOTF.
@param only_retweets Ne pas faire de republication, seulement retweeter.
                     Fonctionne très mal si on n'utilise pas "Artists on
                     Twitter Finder".
@param sfw_bot Activer des mécanismes de protection pour que le bot soit SFW.
               - Ne pas retweeter ou citer comme source les Tweets marqués
                 comme ayant du contenu explicites.
               - Vérifier les hashtags des Tweets qu'on s'apprête à retweeter.
               Attention : Cela ne protége pas contre une requête dans la BDD
               d'images qui retourne du NSFW !
@param max_relaunchs Nombre maximum de relancements. La fonction se relance si
                     on a retweeté un Tweet.
@param filter_tags Liste de tags qui font supprimer une image si elle contient
                   l'un au moins de ces tags.
@param lock_actions Ne pas réellement tweeter ni retweeter. Permet de tester le
                    scripit sans qu'il ne fasse d'action sur un compte Twitter.
"""
def launch ( request : str,
             api_key : str,
             api_secret : str,
             oauth_token : str,
             oauth_token_secret : str,
             database : str = "derpibooru",
             post_new_first : bool = False,
             add_hashtags : str = "",
             aotf_api_base : str = None,
             only_retweets : bool = False,
             sfw_bot : bool = False,
             max_relaunchs : int = 3,
             filter_tags : List[str] = None,
             lock_actions : bool = False ) :
    # DEV_MODE a la priorité sur lock_actions
    if DEV_MODE : lock_actions = True
    
    # Connexion à l'API Twitter
    api = connect_to_twitter( api_key,
                              api_secret,
                              oauth_token,
                              oauth_token_secret )
    
    # Vérifier la connexion
    verify_creds = api.verify_credentials()._json
    bot_name = verify_creds["screen_name"]
    
    # Connexion à l'API "Artists on Twitter Finder"
    if aotf_api_base :
        aotf = AOTF_Client( aotf_api_base )
    else :
        aotf = None
    
    """
    Boucle de relancement. Permet de repartager une autre image si jamais on
    a fait un retweet et non une republication de l'image.
    """
    relaunch = True # Autoriser le relancement
    relaunchs_count = 0 # Compteur de relancements, est incrémenté lorsque "relaunch" est mis à True
    results = [] # Mise en cache de plusieurs résultats e ncas de relancement
    cursor = None # Curseur sur la liste des résultats mis en cache
    while relaunch and relaunchs_count < max_relaunchs :
        relaunch = False # Sera remis à True si on a fait un retweet
        result = None # Contenant l'image choisie
        
        """
        Mettre en cache plusieurs résultats en cas de relancement.
        """
        if cursor == None or cursor+1 >= len( results ) :
            limit = 1 # Si la BDD ne supporte pas plusieurs résultats
            if database == "danbooru" :
                limit = 10 # 20 maximum dans une requête, mais on laisse de la marge pour le filtrage
            elif database == "derpibooru" :
                limit = 40 # 50 maximum dans une requête, mais ça fait beaucoup
            results = get_DB_image( request, database,
                                    random = not post_new_first,
                                    limit = limit,
                                    filter_tags = filter_tags )
            cursor = 0
        else :
            cursor += 1
        
        """
        Si il faut poster les dernières images en premier.
        """
        next_image_found = False # A on trouvé une image après celle du curseur ?
        if post_new_first :
            try :
                log_file = open( "curseur_" + bot_name + ".log", "r")
                previous_images = log_file.readlines()
                for i in range( len( previous_images ) ) :
                    previous_images[i] = int( previous_images[i].replace('\n', '') )
                log_file.close()
            
            except Exception :
                result = results[cursor]
                print( "CAS 1 : Rien dans les logs, donc on prend la dernière image posté sur la requête." )
                previous_images = [ int( result.id ) ]
                next_image_found = True
            
            else :
                print( "Liste images précédentes : " + str(previous_images) )
                
                # Nettoyage de la liste de logs
                id_list = []
                for image in results :
                    id_list.append( image.id )
                for i in range( len(previous_images) ) :
                    if previous_images[i] not in id_list :
                        previous_images[i] = -1
                
                # De la fin au début, pour prendre la plus ancienne
                for i in range( len( results ) - 1, -1, -1 ) :
                    if not int( results[i].id ) in previous_images :
                        result = results[i]
                        print( "CAS 2 : Il y a une image récente sur la requête (" + str(result.id) + ") qu'on n'a pas posté, on la prend." )
                        next_image_found = True
                        previous_images.append( int( result.id ) )
                        break
                
                if next_image_found == False :
                    print( "CAS 3 : Il n'y a pas d'image récente sur la requête qu'on n'a pas posté, on en prend une au hasard." )
                    post_new_first = False # Passer en mode aléatoire
                    relaunch = True # Faire un relancement qui ne compte pas puisqu'on n'a rien posté ni RT
                    cursor = None # Refaire une requête à la BDD d'images
                    continue
            
            # Ecrire le nouveau fichier curseur
            if next_image_found :
                log_file = open( "curseur_" + bot_name + ".log", "w")
                for image_id in previous_images :
                    if image_id != -1 :
                        log_file.write( str( image_id ) + '\n' )
                log_file.close()
        
        """
        Si ce bot ne poste pas les dernières images en premier, on peut en
        prendre une au hasard.
        """
        if not post_new_first :
            result = results[cursor]
        
        print( "IMAGE CHOISIE : " + str(result.db_source) )
        
        """
        Essayer d'abord de faire un retweet à la place d'une republication.
        """
        print( "Tentative de retweet..." )
        retweet_succeed = try_to_retweet( result, api, bot_name,
                                          aotf_client = aotf,
                                          avoid_nsfw_tweets = sfw_bot,
                                          do_not_retweet = lock_actions,
                                          already_retweeted_is_success = not only_retweets )
        if retweet_succeed :
            relaunch = True
            relaunchs_count += 1
            continue
        elif only_retweets :
            relaunch = True
            continue # Et on n'incrémente pas "max_relaunchs", sinon on peut ne rien partager
        
        print( "Aucun retweet possible, on envoi un nouveau Tweet !" )
        
        """
        Si on arrive ici, c'est qu'on peut partager l'image en republiant.
        """
        tweet_text = generate_tweet( result,
                                     add_hashtags = add_hashtags,
                                     aotf_client = aotf,
                                     avoid_nsfw_tweets = sfw_bot )
        post_to_twitter( result, api, tweet_text, bot_name, do_not_tweet = lock_actions )
