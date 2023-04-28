#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 06:10:58 2022

@author: Pablo Esteban Villota
"""

import pandas as pd

arriendosDF = pd.read_excel('./Arriendo de locales municipales.xlsx', skiprows=1)
concesionesDF = pd.read_excel('./Concesion de uso de locales municipales.xlsx', skiprows=1)

##print(arriendosDF, "\n", concesionesDF)

# Elimina direcciones repetidas(Aun existen direcciones repetidas pero escritas de maneras ligeramente diferente)
# al final lo convierte en Series
direccionesDistintas=arriendosDF.drop_duplicates(subset="Dirección", inplace=False)["Dirección"].squeeze()
#Separa llos campos que contienen ":" y se queda con el primero
dosPuntosFiltro = direccionesDistintas.str.split(pat=":", n=1, expand=True)[0].squeeze()
#Separa llos campos que contienen "," y se queda con el primero
comaFiltro = dosPuntosFiltro.str.split(pat=",", n=1, expand=True)[0].squeeze()

# Nuevamente elimina direcciones repetidas
segundoFiltroRepetidas = comaFiltro.drop_duplicates(inplace=False)

#dosPuntosFiltro.to_excel('direcciones.xlsx', sheet_name='direcciones')

print(segundoFiltroRepetidas)
#print(type(dosPuntosFiltro))
#direccionesDistintas.to_excel('direcciones.xlsx', sheet_name='direcciones')

#print(direccionesDistintas)