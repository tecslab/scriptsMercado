#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 06:10:58 2022

@author: Pablo Esteban Villota
"""

import pandas as pd

arriendosDF = pd.read_excel('./Arriendo de locales municipales.xlsx', skiprows=1)
# #Separa llos campos que contienen ":" y se queda con el primero
dosPuntosFiltro = arriendosDF["Dirección"].str.split(pat=":", n=1, expand=True)[0]
# #Separa llos campos que contienen "," y se queda con el primero
comaFiltro = dosPuntosFiltro.str.split(pat=",", n=1, expand=True)[0]

#reemplazoArenal = comaFiltro.str.replace("FERIA LIBRE EL ARENAL", "EL ARENAL")
comaFiltro.name = "Dirección general"

#Crea lista con todas las direcciones distintas
direccionesDistintas = comaFiltro.drop_duplicates(inplace=False).tolist()

# Agrega la dirección filtrada como una comuna extra
joined = arriendosDF.join(comaFiltro)
#joined.to_excel('direcciones.xlsx', sheet_name='direcciones')


for i in direccionesDistintas:
    # Separa en archivos excels distintos según el contenido de la columna agregada
    filtroDirección = joined[joined["Dirección general"].isin([i])]
    separacion = filtroDirección.drop("Dirección general", axis=1) #Elimina la columna extra
    separacion.to_excel('./resultadosArriendos/'+ i+".xlsx")


## Procesamiento extra para las Direcciones "EL ARENAL" y "FERIA LIBRE EL ARENAL"
## ->Arenal
filtroArenal = joined[joined["Dirección general"]=="EL ARENAL"]
comaFiltroArenal = filtroArenal["Dirección"].str.split(pat=",", n=1, expand=True)[1]
dosPuntosFiltroArenal = comaFiltroArenal.str.split(pat=":", n=1, expand=True)[0]
dosPuntosFiltroArenal.name = "Dirección Arenal"
direccionesDistintasArenal = dosPuntosFiltroArenal.drop_duplicates(inplace=False).tolist()

joinedArenal = filtroArenal.join(dosPuntosFiltroArenal)

for i in direccionesDistintasArenal:
    # Separa en archivos excels distintos según el contenido de la columna agregada
    filtroDirección = joinedArenal[joinedArenal["Dirección Arenal"].isin([i])]
    separacion = filtroDirección.drop(["Dirección Arenal", "Dirección general"], axis=1) #Elimina la columna extra
    separacion.to_excel('./resultadosArriendos/El Arenal/'+ i+".xlsx")
    
    
## ->Feria Libre
filtroFeria = joined[joined["Dirección general"]=="FERIA LIBRE EL ARENAL"]
comaFiltroFeria = filtroFeria["Dirección"].str.split(pat=",", n=1, expand=True)[1]
dosPuntosFiltroFeria = comaFiltroFeria.str.split(pat=":", n=1, expand=True)[0]
dosPuntosFiltroFeria.name = "Dirección Feria"
direccionesDistintasFeria = dosPuntosFiltroFeria.drop_duplicates(inplace=False).tolist()

joinedFeria = filtroFeria.join(dosPuntosFiltroFeria)

for i in direccionesDistintasFeria:
    # Separa en archivos excels distintos según el contenido de la columna agregada
    filtroDirección = joinedFeria[joinedFeria["Dirección Feria"].isin([i])]
    separacion = filtroDirección.drop(["Dirección Feria", "Dirección general"], axis=1) #Elimina la columna extra
    separacion.to_excel('./resultadosArriendos/Feria/'+ i+".xlsx")