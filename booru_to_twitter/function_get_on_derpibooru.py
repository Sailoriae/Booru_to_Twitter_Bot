#!/usr/bin/python3
# coding: utf-8

from typing import List
import requests
from urllib.parse import urlencode
from time import sleep

from .class_Result_from_DB import Result_from_DB


"""
@param tags_list Liste des tags de l'image retournée par Derpibooru.
"""
def generate_hashtags ( tags_list : List[str] ) :
    hashtags = []
    
    if "explicit" in tags_list or "nudity" in tags_list : hashtags.append( "#Clop" )
    
    if "anthro" in tags_list : hashtags.append( "#Anthro" )
    if "humanized" in tags_list : hashtags.append( "#Humanized" )
    
    if "femboy" in tags_list : hashtags.append( "#Femboy" )
    if "futanari" in tags_list : hashtags.append( "#Futanari" )
    if "adorasexy" in tags_list : hashtags.append( "#Adorasexy" )
    
    if "applejack" in tags_list : hashtags.append( "#Applejack" )
    if "fluttershy" in tags_list : hashtags.append( "#Fluttershy" )
    if "pinkie pie" in tags_list : hashtags.append( "#PinkiePie" )
    if "rainbow dash" in tags_list : hashtags.append( "#RainbowDash" )
    if "rarity" in tags_list : hashtags.append( "#Rarity" )
    if "twilight sparkle" in tags_list : hashtags.append( "#TwilightSparkle" )
    
    if "starlight glimmer" in tags_list : hashtags.append( "#StarlightGlimmer" )
    if "sunset shimmer" in tags_list : hashtags.append( "#SunsetShimmer" )
    if "trixie" in tags_list : hashtags.append( "#Trixie" )
    
    if "princess celestia" in tags_list : hashtags.append( "#PrincessCelestia" )
    if "princess luna" in tags_list : hashtags.append( "#PrincessLuna" )
    if "princess cadance" in tags_list : hashtags.append( "#PrincessCadance" )
    
    if "sweetie belle" in tags_list : hashtags.append( "#SweetieBelle" )
    if "apple bloom" in tags_list : hashtags.append( "#AppleBloom" )
    if "scootaloo" in tags_list : hashtags.append( "#Scootaloo" )
    
    if "vinyl scratch" in tags_list : hashtags.append( "#VinylScratch" )
    if "octavia" in tags_list : hashtags.append( "#Octavia" )
    
    if "spike" in tags_list : hashtags.append( "#Spike" )
    
    if "spitfire" in tags_list : hashtags.append( "#Spitfire" )
    if "soarin" in tags_list : hashtags.append( "#Soarin" )
    
    if "cheerilee" in tags_list : hashtags.append( "#Cheerilee" )
    if "zecora" in tags_list : hashtags.append( "#Zecora" )
    if "big mcintosh" in tags_list : hashtags.append( "#BigMcIntosh" )
    if "braeburn" in tags_list : hashtags.append( "#Braeburn" )
    
    if "lotus blossom" in tags_list : hashtags.append( "#LotusBlossom" )
    if "aloe" in tags_list : hashtags.append( "#Aloe" )
    
    return hashtags


"""
@param tags_list Liste des tags de l'image retournée par Derpibooru.
"""
def generate_artists_credit_line ( tags_list : List[str] ) :
    artists_credit_line = ""
    for tag in tags_list :
        if tag[0:7] == "artist:" :
            artists_credit_line += tag[7:].title() + ", "
        if tag[0:5] == "edit:" :
            artists_credit_line += tag[5:].title() + ", "
        if tag[0:7] == "editor:" :
            artists_credit_line += tag[7:].title() + ", "
    
    # Supprimer le dernier ", "
    if artists_credit_line != "" :
        artists_credit_line = artists_credit_line[:-2]
    
    return artists_credit_line


"""
Obtenir des images sur Derpibooru.

@param request Requête à envoyer à la base de données.
@param database Nom de la bas de données à utiliser.
@param random Si mis à "False, les images sont triés par la plus récente à la
              plus ancienne.
@param limit Nombre de résultats à renvoyer.
@param filter_tags Liste de tags qui font supprimer une image si elle contient
                   l'un au moins de ces tags.

@return Liste d'objet "Result_from_DB", image retournées par Derpibooru.
"""
def get_on_derpibooru ( request : str,
                        random : bool = True,
                        limit : int = 1,
                        filter_tags : List[str] = None ) :
    if filter_tags != None and len(filter_tags) > 0 :
        request = f"({request}) AND NOT ({' OR '.join(filter_tags)})"
    
    params = {
        "q" : request,
        "filter_id" : 56027,
        "per_page" : limit }
    if random :
        params["sf"] = "random"
    else :
        params["sf"] = "created_at"
        params["sd"] = "desc"
    
    retry_once = True
    while True :
        try :
            request_url = "https://derpibooru.org/api/v1/json/search/images?" + urlencode( params )
            data = requests.get( request_url ).json()
        except ValueError as error : # JSONDecodeError en hérite, et c'est plus simple
            if retry_once :
                sleep(3)
                retry_once = False
                continue
            raise error
        break
    
    to_return = []
    for data in data["images"] :
        if len(to_return) >= limit :
            break
        
        to_append = Result_from_DB()
        
        # ID de l'image dans la base de données
        to_append.id = data["id"]
        
        # Hashtags de l'image, dans l'ordre du plus au moins important
        to_append.hashtags = generate_hashtags( data["tags"] )
        
        # Ligne de crédit aux artistes de cette image
        to_append.artists_credits = generate_artists_credit_line( data["tags"] )

        # URL de la page web source de l'image (Si valide)
        check_list = [ data["source_url"] != "",
                       data["source_url"] != None,
                       not "dead source" in data["tags"] ]
        if all( check_list ) :
            to_append.source = data["source_url"]
        
        # Si la source est marquée comme contenant du NSFW
        to_append.explicit_source = "explicit source" in data["tags"]
        
        # URL de la page web de la BDD contenant l'image
        to_append.db_source = "https://derpibooru.org/images/" + str(to_append.id)
        
        # URL de l'image en résolution maximale
        to_append.large = data["representations"]["large"]
        
        # URL de l'image en résolution plus basse
        to_append.medium = data["representations"]["medium"]
        
        # URL de l'image en résolution encore plus basse
        to_append.small = data["representations"]["small"]
        
        to_return.append( to_append )
    
    return to_return
