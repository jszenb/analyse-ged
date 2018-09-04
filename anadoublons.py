#!/usr/bin/python
# -*- coding: utf-8 -*-
# ******************************************************************************
# PROGRAMME   : anadoublons.py
# DESCRIPTION : à partir d'un fichier marc au format texte passé en entrée, ce 
#               traitement identifie les doublons et produit des statistiques
#               par titres.
# ENTREES     : 1. le fichier contenant les données MARC au format texte  
#               2. le radical pour former le fichier de sortie
# SORTIE      : Fichier de sortie nommé avec le radical donné en paramètre suffixé 
#               par "-anadoublons.txt"
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
from collections import defaultdict

# **************************************************************************** #
#                                 Fonctions                                    #
# **************************************************************************** #

# nested_dict : création de dictionnaires imbriqués
# ******************************************************************************
def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n-1, type))

# ecritValeur : fonction utilisée pour construire le tableau d'analyse
# ******************************************************************************        
def ecritValeur( valeur, tabValeur ):
    if valeur not in tabValeur:
        tabValeur[valeur] = 1
    else:
        tabValeur[valeur] += 1    
        
    return;

# ecritBibValeur : fonction utilisée pour construire le tableau d'analyse en
#                  intégrant la bibliothèque dans la clef.
# ******************************************************************************
def ecritBibValeur(valeur, tableauBibParTitre, tableauFinal):
    
    if valeur not in tableauFinal:
        tableauFinal[valeur] = {}
        for x, y in tableauBibParTitre.iteritems():
            tableauFinal[valeur][x] = y

    else:
        for bib, nb in  tableauBibParTitre.iteritems():

            bibInscrite = False 

            for uneBib, uneValeur in tableauFinal[valeur].iteritems():
                if bib == uneBib:
                    #print "Trouvé dans tableauFinal"
                    tableauFinal[valeur][bib] += nb
                    bibInscrite = True
                else:
                    continue
                
            if not bibInscrite:
                #print "Non Trouvé dans tableauFinal"
                tableauFinal[valeur][bib]= nb


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
    
    # Les dictionnaires nécessaires sont initialisés :
    # Le dictionnaire "analyse" contient la répartition doublons, triplons, etc. 
    # **************************************************************************
    analyse={}
    
    # Les dictionnaires "analyseBibTitreEnCours" et "analyseBibTotal" sont 
    # utilisés pourcalculer la répartition bibliothèque par bibliothèque.
    # **************************************************************************
    analyseBibTitreEnCours={}
    analyseBibTotal=nested_dict(2, 'int')
    
    premierTitre = True
    nbExemplaireTitre = 0
    codeBib = ""
    precCodeBib = ""
    f = open(ficEntree,'r')  
    
    print "Analyse du fichier d'entrée :"
    
    for line in tqdm(f, total=get_line_number(ficEntree)):     
        # On analyse le fichier ligne par ligne pour detecter les lignes 
        # pertinentes.
        # **********************************************************************

        # Détection d'un nouveau titre
        # **********************************************************************
        if (re.search('^[0-9]{5}',line)):

            # Premier titre : on ne fait rien puisqu'on a aucune information.
            # Autre cas : si ce n'est pas le premier titre, enregistrements des 
            # informations sur le titre précédent. 
            # ******************************************************************

            if (premierTitre != True):
                # Insertion des données dans la structure permettant de connaître 
                # le nombre de titres ayant un même nombre d'exemplaire
                # **************************************************************
                ecritValeur(nbExemplaireTitre, analyse)
                
                # Insertion des données dans la structure permettant de connaître
                # les groupes de x exemplaires
                # **************************************************************
                ecritBibValeur(nbExemplaireTitre, analyseBibTitreEnCours, analyseBibTotal)        
                
                # Réinitialisation des variables pour le prochain titre
                # **************************************************************
                nbExemplaireTitre = 0
                analyseBibTitreEnCours = {}
                codeBib = ""
                
            # Si on est arrivé ici, on sait qu'on est arrivé au second titre
            # ******************************************************************
            premierTitre=False
        
        elif ( line.startswith("995") ):    
            # Nouvel exemplaire trouvé : on incrémente d'un de façon générale 
            # pour ce titre.
            # ******************************************************************
            nbExemplaireTitre += 1

            # Détection de l'association bibliothèque / exemplaire. 
            # Enregistrement de l'information afin d'avoir la répartition des
            # exemplaires par bibliothèque pour ce titre.
            # ******************************************************************
            if re.search(r'\$c ([A-Z]*)', line):
                codeBib = re.search(r'\$c ([A-Z]*)', line).group(1) 
            else:
                codeBib = "Inconnu"
                
            if codeBib in analyseBibTitreEnCours:
                analyseBibTitreEnCours[codeBib] += 1
            else:
                analyseBibTitreEnCours[codeBib] = 1
            
        else:
            # Ni un nouveau titre, ni un exemplaire : on ne fait rien
            # ******************************************************************
            continue
            
        ##if

    ##for
    
    # Un dernier appel pour traiter le dernier titre trouvé par la boucle :
    # **************************************************************************
    ecritValeur(nbExemplaireTitre, analyse)
    ecritBibValeur(nbExemplaireTitre, analyseBibTitreEnCours, analyseBibTotal)        

    f.close()
                
    # Ecriture des résultats.
    # **************************************************************************
    ficSortie = radFicSortie + "-anadoublons.txt"
    
    try:
    
        f = open(ficSortie,'w')

        """for typeDoublon, nbTitre in sorted(analyse.iteritems()):
            #print ("Type de n-uplet d'exemplaires : {a} -> Nombre de titres concernés {b}".format(a=typeDoublon, b=nbTitre))    
            f.write ("Type de n-uplet d'exemplaires : {a} -> Nombre de titres concernés {b}\n".format(a=typeDoublon, b=nbTitre))
        
        f.write ("----------------------------------------------\n")
        f.write ("----------------------------------------------\n")
        #print str(analyseBibTotal)
        for nuplet, statbib in sorted(analyseBibTotal.iteritems()):
            #print str(nuplet)
            #print str(statbib)
            #print ("Type de n-uplet d'exemplaires {c}".format(c=nuplet))
            for bib, nb in sorted(statbib.iteritems()):
                #print ("--------------------------------> bib {a} \t-> Nombre d'exemplaires concernés {b} ".format(a=bib, c=nuplet, b=nb))
                f.write ("Type de n-uplet d'exemplaires {c} -> bib {a} -> Nombre d'exemplaires concernés {b}\n".format(a=bib, c=nuplet, b=nb))
        """
        f.write ("/-----------------------------------------------------------------------------------------\\\n")
        

        for typeDoublon, nbTitre in sorted(analyse.iteritems()):
            f.write ("|-----------------------------------------------------------------------------------------|\n")
            f.write ("|   Nombre   |      Nombre     |      Total      []                     |     Nombres     |\n")
            f.write ("|     de     |  d'exemplaires  |       en        []    Bibliothèques    |  d'exemplaires  |\n")
            f.write ("|    Titre   |     par titre   |   exemplaires   []                     |   bibliothèque  |\n")
            f.write ("|-----------------------------------------------------------------------------------------|\n")    
            sommeExemplaire = typeDoublon * nbTitre
            f.write ("| {b:>10} |      {a:>10} |    {c:>10}                                            |\n".format(a=typeDoublon, b=nbTitre, c=sommeExemplaire))
            f.write( "|            |                 |                 []                     |                 |\n")
            for bib, nb in sorted(analyseBibTotal[typeDoublon].iteritems()):
                f.write( "|            |                 |                 []          {a:<10} |      {b:>10} |\n".format(a=bib, b=nb))
            
            """
            for bib, nb in sorted(analyseBibTotal[typeDoublon].iteritems()):
                #for bib, nb in sorted(statbib.iteritems()):
                #print ("--------------------------------> bib {a} \t-> Nombre d'exemplaires concernés {b} ".format(a=bib, c=nuplet, b=nb))
                f.write("      la bibliothèque {a} possède {b} exemplaires\n".format(a=bib, b=nb))            
            """
        f.write ("\\-----------------------------------------------------------------------------------------/\n")
        f.close()
    
        print "Résultats disponibles dans les fichiers de sortie."
        
    except:
        print('Erreur à la création des fichiers')
        sys.exit(1) # quit Python
    
else:
    print("Pas de fichier trouvé à analyser ! Le fichier doit se trouver dans le même répertoire que le script Python ! Fin du programme.")
    sys.exit(1)

sys.exit(0)    
# **************************************************************************** #
#                                    Fin                                       #
# **************************************************************************** #
