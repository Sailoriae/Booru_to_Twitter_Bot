#!/usr/bin/python3
# coding: utf-8

from typing import List


"""
Classe contenant les données reçues par une base de données (Par exemple
Danbooru ou Derpibooru).
"""
class Result_from_DB :
    """
    Liste uniquement les données dont nous avons besoin.
    """
    def __init__( self ) :
        self.id : int # ID de l'image dans la base de données (OBLIGATOIRE)
        self.hashtags : List[str] = [] # Hashtags de l'image, dans l'ordre du plus au moins important
        self.artists_credits : str # Ligne de crédit aux artistes de cette image (OBLIGATOIRE)
        
        self.source : str = None # URL de la page web source de l'image (Laisser à "None" si jamais la source n'existe pas ou est invalide)
        self.explicit_source : bool = None # Est-ce que la source est détectée comme contenant du NSFW ?
        self.source_is_tweet : bool = None # Est-ce que la source a été détectée comme étant un Tweet ? Doit être défini par la fonction "try_to_retweet()".
        self.db_source : str # URL de la page web de la BDD contenant l'image (OBLIGATOIRE)
        
        self.large : str # URL de l'image en résolution maximale (OBLIGATOIRE)
        self.medium : str = None # URL de l'image en résolution plus basse
        self.small : str = None # URL de l'image en résolution encore plus basse
    
    def __str__( self ) :
        return str( self.id )
