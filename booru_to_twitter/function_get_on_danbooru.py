#!/usr/bin/python3
# coding: utf-8

from typing import List
import requests
from time import sleep
import re
from urllib.parse import urlencode

from .class_Result_from_DB import Result_from_DB


pixiv_img_1 = re.compile(
    r"^https?:\/\/[a-z0-9]+\.pixiv\.net\/" )
pixiv_img_2 = re.compile(
    r"^https?:\/\/[a-z0-9]+\.pximg\.net\/" )



"""
Obtenir des images sur Danbooru.

@param request Requête à envoyer à la base de données.
@param random False : Trier les images de la plus récente à la plus ancienne.
              True : Retourner des images aléatoires (Répondant à la requête).
@param limit Nombre de résultats à renvoyer.
@param filter_tags Liste de tags qui font supprimer une image si elle contient
                   l'un au moins de ces tags.

@return Liste d'objet "Result_from_DB", image retournées par Danbooru.
"""
def get_on_danbooru ( request : str,
                      random : bool = True,
                      limit : int = 1,
                      filter_tags : List[str] = None ) :
    results_to_return = []
    first_loop = True
    while True :
        if not first_loop :
            sleep(3) # Pour ne pas aller trop vite sur leur API
        first_loop = False
        
        if random :
            request += " random:20" # Ne peut pas aller au delà de 20
        params = { "tags" : request }
        datas = requests.get( "https://danbooru.donmai.us/posts.json?" + urlencode( params ) ).json()
        
        for data in datas :
            if len(results_to_return) >= limit :
                return results_to_return
            
            if data["is_banned"] :
                continue
            
            to_return = Result_from_DB()
            
            # ID de l'image dans la base de données
            to_return.id = data["id"]
            
            # Filtrae par tags
            image_tags = data["tag_string"].split(" ")
            
            continue2 = False
            for tag in image_tags :
                if tag in filter_tags :
                    print( "L'image " + str(to_return.id) + " contient le tag filtré \"" + tag + "\", on en prend une autre." )
                    continue2 = True
                    break
            if continue2 : continue
            
            # Hashtags de l'image, dans l'ordre du plus au moins important
            to_return.hashtags = []
            
            # Ligne de crédit aux artistes de cette image
            to_return.artists_credits = ""
            for artist in data["tag_string_artist"].split(' ') :
                to_return.artists_credits += artist.replace( "_(", " (" ).title() + ", "
            if to_return.artists_credits != "" : # Supprimer le dernier ", "
                to_return.artists_credits = to_return.artists_credits[:-2]
            
            # URL de la page web source de l'image (Si valide)
            check_list = [ data["source"] != "",
                           data["source"] != None,
                           not "source_request" in image_tags,
                           not "bad_id" in image_tags ]
            if all( check_list ) :
                to_return.source = data["source"]
            
            # Danbooru nous donne l'URL de l'image, et pas la page de la source
            if to_return.source != None :
                if pixiv_img_1.search( to_return.source ) or pixiv_img_2.search( to_return.source ) :
                    if "pixiv_id" in data and data["pixiv_id"] != None :
                        to_return.source = "https://www.pixiv.net/artworks/" + str( data["pixiv_id"] )
                    else :
                        to_return.source = "https://www.pixiv.net/artworks/" + to_return.source.split("/")[-1].split("_")[0].split(".")[0]
            
            # URL de la page web de la BDD contenant l'image
            to_return.db_source = "https://danbooru.donmai.us/posts/" + str(to_return.id)
            
            # URL de l'image en résolution maximale
            to_return.large = data["file_url"]
            
            # URL de l'image en résolution plus basse
            to_return.medium = data["large_file_url"]
            
            # URL de l'image en résolution encore plus basse
            to_return.small = None
            
            # Virer les ZIP
            if to_return.large[-4:] == ".zip" :
                to_return.large = to_return.medium
                to_return.medium = None
            if to_return.large[-4:] == ".zip" :
                continue
            
            # Retourner
            results_to_return.append( to_return )
