#!/usr/bin/python
# -*- coding: utf-8 -*-
# ******************************************************************************
# PROGRAMME   : anacadre.py
# DESCRIPTION : Dans un fichier MARC passé en format texte, ce traitement 
#               identifie les zones 689 et les analyse pour donner en sortie
#               la ventilation dans le cadre de classement en général.
# ENTREE      : deux paramètres : 
#               1. le fichier contenant les données MARC au format texte  
#               2. le radical pour former le fichier de sortie
# SORTIE      : Fichier de sortie nommé avec le radical donné en paramètre 
#               suffixé par "-anacadre.txt"
# J. CHIAVASSA-SZENBERG, CAMPUS CONDORCET, 2017
# ******************************************************************************
import sys
import itertools
import fileinput
import os.path
import sys
import time
import re
from tqdm import tqdm 
import mmap
from collections import Counter

# **************************************************************************** #
#                                 Fonctions                                    #
# **************************************************************************** #

# ecritValeur : fonction utilisée pour construire le tableau d'analyse
# ******************************************************************************
def ecritValeur( valeur, tabValeur ):
    if valeur not in tabValeur:
        tabValeur[valeur] = 1
    else:
        tabValeur[valeur] += 1    
    
    return;

# validArgs : validation des arguments d'entrée
# ******************************************************************************
def validArgs(tabArgs):
        if (len(tabArgs) != 3):
                print "LOG : Erreur dans le passage des arguments : "
                print "LOG : --> usage : python anacadre fichier-entree radical-fichier-sortie"
                print "LOG : --> Vérifiez votre commande !"
                print "LOG : Fin du traitement"
                sys.exit(1)

        return (tabArgs[1], tabArgs[2])
        
# get_line_number : comptage du nombre de lignes à traiter
# ******************************************************************************
def get_line_number(file_path):  
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines

# **************************************************************************** #
#                                   Main                                       #
# **************************************************************************** #

# Récupération des paramètres
ficEntree = radFicSortie = ""
ficEntree, radFicSortie = validArgs (sys.argv)

# Déclenchement du traitement 
if os.path.isfile(ficEntree):

    print "Initialisation"

    territoire={}
    dominante={}
    segment={}
    corpus={}
    thematique={}
    lot={}
    i = 0
    f = open(ficEntree,'r')  
    

    print "Lecture du fichier d'entrée :"
    for line in tqdm(f, total=get_line_number(ficEntree)):     

        if ( line.startswith("689") ):    
        
            # Analyse des lignes 689 qui contiennent l'implatation
            # ******************************************************************
        
            # Liste des champs nécessaires pour construire la chaîne
            # ******************************************************************
            tabChamps = ["a", "b", "c", "d", "e"]
            
            for word in line.split("$"): 
                for champ in tabChamps:
                    if (word.startswith(champ)):
                        if (champ == "a"):
                            # Territoire
                            ecritValeur(word[2:].strip(), territoire)
                        elif (champ == "b"):
                            # Dominante
                            ecritValeur(word[2:].strip(), dominante)
                        elif (champ == "c"):
                            # Segment
                            if word[2:].strip() == 'A11':
                                i += 1
                                
                            ecritValeur(word[2:].strip(), segment)
                        elif (champ == "d"):
                            # Corpus
                            ecritValeur(word[2:].strip(), corpus)
                        elif (champ == "e"):
                            # Thématique
                            ecritValeur(word[2:].strip(), thematique)
                        elif (champ == "f"):
                            # Lot
                            ecritValeur(word[2:].strip(), lot)
                        else:
                            # ?? On fait rien
                            continue

            ##for
            
        ##if

    ##for
    
    f.close()

    # Ecriture du résultat dans un fichier de sortie
    # **************************************************************************
    ficSortie = radFicSortie + "-anacadre.txt"
    
    try:
        f = open(ficSortie,'w')
    
        print "Ecriture des résultats :"
        f.write ("/-----------------------------------------------------\\\n")
        f.write ("|                                                     |\n")
        f.write ("|   TERRITOIRE   |    DOMINANTE    |     SEGMENT      |\n")
        f.write ("|                                                     |\n")
        f.write ("|-----------------------------------------------------|\n")
        f.write ("|                                                     |\n")
               
        for unTerritoire, nbTerritoire in sorted(territoire.iteritems()):
            f.write ("| {a} : {b:>10}                                      |\n".format(a=unTerritoire, b=nbTerritoire))
            
            for uneDominante, nbDominante in sorted(dominante.iteritems()):
                if (uneDominante.startswith(unTerritoire)):
                    f.write ("|                | {c} : {d:>10}                    |\n".format(c=uneDominante, d=nbDominante))
            
                    for unSegment, nbSegment in sorted(segment.iteritems()):
                        if (unSegment.startswith(uneDominante)):
                            f.write ("|                |                 | {e} : {f:>10} |\n".format(e=unSegment, f=nbSegment))                
                            
            f.write ("|-----------------------------------------------------|\n")
            
        f.write ("|                                                     |\n")    
        f.write ("\\-----------------------------------------------------/\n")

        f.close()
        
        print "Résultats disponibles dans les fichiers de sortie."
        
    except:
        print('Erreur à la création des fichiers')
        sys.exit(1) # quit Python
    ##try        
    
else:
    print("Pas de fichier trouvé à analyser ! Le fichier doit se trouver dans le même répertoire que le script Python ! Fin du programme.")
    sys.exit(1)

sys.exit(0)    
# **************************************************************************** #
#                                    Fin                                       #
# **************************************************************************** #
