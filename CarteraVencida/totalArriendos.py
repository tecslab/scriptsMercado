#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 14:20:14 2022

@author: pablov
"""

import pandas as pd


arriendosDF = pd.read_excel('../carteraArriendosConcesionesJunio.xlsx', sheet_name=0, skiprows=1)

totalArriendos = arriendosDF["VALOR"].sum()
print("Total deuda arriendos:")
print("$" + str(totalArriendos))


concesionesDF = pd.read_excel('../carteraArriendosConcesionesJunio.xlsx', sheet_name=1, skiprows=1)
totalConcesiones = concesionesDF["VALOR"].sum()

print("Total Deuda Concesiones:")
print("$" + str(totalConcesiones))


print("Total deuda:")
print("$" + str(totalConcesiones + totalArriendos))

comerciantesDistintos = concesionesDF["CON_CEDULA_RUC"].drop_duplicates(inplace=False).tolist()

print("El total de comerciantes es: " + str(len(comerciantesDistintos)))


# aggregation_functions = {'VALOR': 'sum', 'USUARIO_EMITE': 'first'}
# df_new = arriendosDF.groupby(arriendosDF['USUARIO_EMITE']).aggregate(aggregation_functions)

# print(df_new)