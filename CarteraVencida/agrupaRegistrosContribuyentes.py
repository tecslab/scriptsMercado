#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 16:32:13 2022

@author: pablov
"""

import pandas as pd
import os
import glob
  
  
# use glob to get all the csv files
# in the folder
path = os.getcwd() # get current directory
csv_files = glob.glob(os.path.join(path, "*.xlsx"))

DFs = []
## Get all files dataframes
for f in csv_files:    
    # read the csv file
    df = pd.read_excel(f)
    DFs.append(df)

agrupado = pd.concat(DFs) #une todos los registros en uno

agrupado['TITULO']= agrupado['TITULO'].astype('string')
agrupado['CON_CEDULA_RUC']= agrupado['CON_CEDULA_RUC'].astype('string')
# Cambia el campo Titulo por el conjunto de todos los titulos por cédula
agrupado['TITULO']= agrupado[['NOMBRE','TITULO','CON_CEDULA_RUC']].groupby(['CON_CEDULA_RUC'])['TITULO'].transform(lambda x: ', '.join(x))
selectedColumns = agrupado[['NOMBRE','TITULO','CON_CEDULA_RUC', "VALOR", 'ESTADO']]

# Agrupa por cedula y entrega el total del campo Valor
#El count del estado sirve como la cantidad de títulos pendientes
# Documentación de las funciones https://pandas.pydata.org/docs/reference/groupby.html
aggregation_functions = {'NOMBRE': 'first', 'VALOR': 'sum', 'ESTADO': "count", "TITULO": "first"}
dfValorTotal = selectedColumns.groupby(selectedColumns['CON_CEDULA_RUC']).aggregate(aggregation_functions)

dfValorTotal = dfValorTotal.sort_values('NOMBRE') # Ordena alfabéticamente

#//Orden alfabetico

#result = result.drop_duplicates()
# Se cambia el nombre de las columnas para mostrarse
dfValorTotal.rename(columns = {"ESTADO":'CANT_TITULOS', "TITULO":'TITULOS PENDIENTES'}, inplace = True)
dfValorTotal.index.names = ['CEDULA_RUC']
#print(list(dfValorTotal))

os.mkdir("./Resultados")

dfValorTotal.to_excel('./Resultados/Registros3Noviembre.xlsx')
#print(dfValorTotal)
#result.to_excel('direcciones.xlsx', sheet_name='direcciones')