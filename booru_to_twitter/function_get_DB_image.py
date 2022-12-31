#!/usr/bin/python3
# coding: utf-8

from typing import List
import os

from .function_get_on_derpibooru import get_on_derpibooru
from .function_get_on_danbooru import get_on_danbooru


"""
Multiplexeur entre les différentes base de données d'images.

@param request Requête à envoyer à la base de données.
@param database Nom de la bas de données à utiliser.
@param random Si mis à "False, les images sont triés par la plus récente à la
              plus ancienne.
@param limit Nombre de résultats à renvoyer.
@param filter_tags Liste de tags qui font supprimer une image si elle contient
                   l'un au moins de ces tags.

@return Liste d'objet "Result_from_DB", image de la BDD à traiter.
"""
def get_DB_image ( request : str,
                   database : str,
                   random : bool = True,
                   limit : int = 1,
                   filter_tags : List[str] = None ) :
    # Backup le répertoire courant
    backup_cwd = os.getcwd()
    
    # Travailler dans le répertoire de ce fichier pour garantir le bon
    # fonctionnement des fonctions qu'on appel
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if database == "derpibooru" :
        to_return = get_on_derpibooru( request, random = random, limit = limit, filter_tags = filter_tags )
    elif database == "danbooru" :
        to_return = get_on_danbooru( request, random = random, limit = limit, filter_tags = filter_tags )
    else :
        os.chdir( backup_cwd ) # Restaurer le répertoire courant
        raise Exception( "Paramètre \"database = " + str(database) + "\" inconnu" )
    
    # Restaurer le répertoire courant
    os.chdir( backup_cwd )
    
    return to_return
