#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 14:50:36 2022

@author: pablov
"""

import mercadosLib
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import numpy as np

agruparCedulas = True # Agrupa registros con las mismas cedulas y suma sus valores
getDuplicados = False
consultarCancelados = False
excelsResultados = True
useFiles = False

arrayMercados = [
                 {"nombre": "CENTRO COMERCIAL 9 DE OCTUBRE", "skip": "3", },
                 {"nombre": "MERCADO 27 DE FEBRERO", "skip": "2",}, 
                 {"nombre": "MERCADO 12 ABRIL  FRUTAS TEMPOR", "skip": "3",}, 
                 {"nombre": "PLATAFORMA 27 DE FEBRERO", "skip": "2",}, 
                 {"nombre": "MERCADO 9 DE OCTUBRE", "skip": "0",},
                 {"nombre": "MERCADO 10 DE AGOSTO", "skip": "3",},   #OJO, tiene tabla resumen al final
                 {"nombre": "MERCADO 3 DE NOVIEMBRE", "skip": "0",},
                 {"nombre": "MERCADO 12 DE ABRIL", "skip": "2",},
                 {"nombre": "PLATAFORMA MIRAFLORES", "skip": "1",}, # oko, tiene nota al final
                 {"nombre": "PLATAFORMA PATAMARCA", "skip": "1",},
                 {"nombre": "PLATAFORMA NARANCAY", "skip": "0",},
                 {"nombre": "PLATAFORMA CEBOLLAR", "skip": "0",},
                 {"nombre": "PLAZA FLORES", "skip": "0",},
                 {"nombre": "PLAZA ROTARY", "skip": "3",},
                 {"nombre": "PLAZA SAN FRANCISCO", "skip": "1",},
                 {"nombre": "PLAZA SANTA ANA", "skip": "0",},
                 {"nombre": "PLATAFORMA QUINTA CHICA", "skip": "0",},
                 {"nombre": "RECINTO FERIAL", "skip": "0",},
              ]

arrayArenal = [
                 {"nombre": "CENTRO COMERCIAL", "skip": "0", },
                 {"nombre": "JESUS DEL GRAN PODER ", "skip": "0",},
                 #{"nombre": "PLATAFORMA EXTERIOR 4 REINA DE ", "skip": "4",},
                 {"nombre": "SECTOR JUNTO A LAS NAVES DEL CE", "skip": "2",},
                 {"nombre": "PRODUCTOS PERECIBLES, NAVES 4", "skip": "4",},
                 {"nombre": "PLATAFORMA EXTERIOR No. 4    AS", "skip": "4",},
                 {"nombre": "PLATAFORMA No. 4 ASOCIACION BEL", "skip": "4",},
                 {"nombre": "PLATAFORMA No. 4 ASOCIACION VAL", "skip": "4",},
                 {"nombre": "PLATAFORMA 4 (HIERBAS Y ALFAFA)", "skip": "4",},
                 {"nombre": "ASOCIACIÓN 29 DE JULIO ", "skip": "4",},
                 {"nombre": "FRENTE AL RECINTO FERIAL (BETUN", "skip": "4",},
                 {"nombre": "PASO PEATONAL DEL ARENAL", "skip": "5",},
                 {"nombre": "PLATAFORMANO. 2. COOPERATIVA PR", "skip": "4",},
                 {"nombre": "PLATAFORMANO. 2. COOPERATIVA CO", "skip": "3",},
                 #{"nombre": "ASOC REINA DE GUADALUPE", "skip": "2",},
                 {"nombre": "PLATAFORMA No. 9 ASOCIACION ABD", "skip": "3",},
                 
                 {"nombre": "PLATAFORMA EXTERIOR No.2ASO", "skip": "4",},  ## Habían dos tablas en esta hoja
                 {"nombre": "PLATAFORMA EXTERIOR No.2UNI", "skip": "3",},  ## FOrmato extraño
                 
                 #{"nombre": "PLATAFORMA EXTERIOR 2-3-4-9", "skip": "4",}, #Este es un consolidado
                 {"nombre": "ASC HUMANITARIA", "skip": "0",},
                 {"nombre": "PLATAFORMA NO. 3. COOPERATIVA S", "skip": "4",},
                 {"nombre": "PLATAFORMA No. 4 ASOCIACION SAN", "skip": "4",},
                 {"nombre": "ASO. 8 DE MARZO", "skip": "2",},
                 
                 {"nombre": "ASO. 10 DE AGOSTO", "skip": "3",},      ## FOrmato extraño                 
                 
                 {"nombre": "ASO. LUCHA LIBRE", "skip": "3",},
                 {"nombre": "ASO. SEÑOR ANDACOCHA", "skip": "3",},
                 {"nombre": "ASOC.SANTA ANA", "skip": "3",}
              ]

unificarGuadalupe = [
                    {"nombre": "PLATAFORMA EXTERIOR 4 REINA DE ", "skip": "4",},
                    {"nombre": "ASOC REINA DE GUADALUPE", "skip": "2",},
                    ]


# def getExonerados(catastro, arrayDFSRegistos):
#     registrosRecuperados = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION", "VALOR"])
#     catastro.reset_index(drop=True, inplace=True)
#     #registrosRecuperados = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "PUESTO_CATASTRO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION"])
#     for idx, cedulaCatastro in enumerate(catastro["CEDULA"]):
#         puesto = catastro["PUESTO"].iloc[idx]
#         valor = catastro["VALOR"].iloc[idx]
#         mercadoCatastro = catastro["MERCADO"].iloc[idx]
        
#         for registroIdx, registroDF in enumerate(arrayDFSRegistos):
#             #arrayDFSRegistos[registroIdx].reset_index(drop=True, inplace=True)
#             dfFiltrado= registroDF[registroDF["CEDULA"].isin([cedulaCatastro])]
#             dfFiltrado = dfFiltrado[dfFiltrado["MERCADO"]==mercadoCatastro]
#             # Elimina los registros encontrados
#             arrayDFSRegistos[registroIdx] = arrayDFSRegistos[registroIdx].merge(dfFiltrado, how='left', indicator=True)
#             arrayDFSRegistos[registroIdx] = arrayDFSRegistos[registroIdx][arrayDFSRegistos[registroIdx]['_merge'] == 'left_only']
#             arrayDFSRegistos[registroIdx].drop('_merge', inplace=True, axis=1)
#             #arrayDFSRegistos[registroIdx] = arrayDFSRegistos[registroIdx].drop(dfFiltrado.index)
            
#             dfFiltrado.loc[ : , ["MERCADO"]] = mercadoCatastro
#             dfFiltrado.loc[ : , ["VALOR"]] = valor
            
#             ######### IMPORTANTE: EJECUTAR PARA HACER COMPROBACION MANUAL DE PUESTOS ##############
#             #dfFiltrado.loc[ : , ["PUESTO_CATASTRO"]] = puesto
#             registrosRecuperados = pd.concat([registrosRecuperados, dfFiltrado])
#             #registrosRecuperados = registrosRecuperados[["CEDULA", "NOMBRES", "PUESTO", "PUESTO_CATASTRO", "VALOR A DESCONTAR", "OBSERVACION"]]
    
#     registrosRecuperados = registrosRecuperados.sort_values('NOMBRES') # Ordena alfabéticamente
#     return [registrosRecuperados, arrayDFSRegistos]


def getExonerados(catastro, arrayDFSRegistos):
    #registrosRecuperados = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION", "VALOR"])
    catastro.reset_index(drop=True, inplace=True)
    registrosRecuperados = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "PUESTO_CATASTRO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION"])
    for idx, cedulaCatastro in enumerate(catastro["CEDULA"]):
        puesto = catastro["PUESTO"].iloc[idx]
        valor = catastro["VALOR"].iloc[idx]
        mercadoCatastro = catastro["MERCADO"].iloc[idx]
        
        for registroIdx, registroDF in enumerate(arrayDFSRegistos):
            #arrayDFSRegistos[registroIdx].reset_index(drop=True, inplace=True)
            dfFiltrado= registroDF[registroDF["CEDULA"].isin([cedulaCatastro])]
            dfFiltrado = dfFiltrado[dfFiltrado["MERCADO"]==mercadoCatastro]
            
            if (registroIdx==0): # La hoja3 tiene información de puestos
                dfFiltrado = dfFiltrado[dfFiltrado["PUESTO"]==puesto]
            
            # Elimina los registros encontrados
            arrayDFSRegistos[registroIdx] = arrayDFSRegistos[registroIdx].merge(dfFiltrado, how='left', indicator=True)
            arrayDFSRegistos[registroIdx] = arrayDFSRegistos[registroIdx][arrayDFSRegistos[registroIdx]['_merge'] == 'left_only']
            arrayDFSRegistos[registroIdx].drop('_merge', inplace=True, axis=1)
            #arrayDFSRegistos[registroIdx] = arrayDFSRegistos[registroIdx].drop(dfFiltrado.index)
            
            dfFiltrado.loc[ : , ["MERCADO"]] = mercadoCatastro
            dfFiltrado.loc[ : , ["VALOR"]] = valor         
            ######### IMPORTANTE: EJECUTAR PARA HACER COMPROBACION MANUAL DE PUESTOS ##############
            dfFiltrado.loc[ : , ["PUESTO_CATASTRO"]] = puesto
            registrosRecuperados = pd.concat([registrosRecuperados, dfFiltrado])
            #registrosRecuperados = registrosRecuperados[["CEDULA", "NOMBRES", "PUESTO", "PUESTO_CATASTRO", "VALOR A DESCONTAR", "OBSERVACION"]]
            
    registrosRecuperados = registrosRecuperados.groupby(registrosRecuperados['CEDULA']).aggregate(CEDULA=("CEDULA","first"), NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), VALOR=("VALOR", "first"), REGISTROS_SUMADOS=("MERCADO", "count"), MERCADO=("MERCADO", "first"), PUESTO_CATASTRO=("PUESTO_CATASTRO", "first"))
    registrosRecuperados.rename(columns = {'DESCONTAR':'VALOR A DESCONTAR'}, inplace = True)
    
    return [registrosRecuperados, arrayDFSRegistos]


    
def limpiarCatastro(dfCatastro):
    dfCatastro = mercadosLib.limpiarNombres(dfCatastro)
    dfCatastro = mercadosLib.limpiarCedula(dfCatastro)    
    #dfCatastro = mercadosLib.limpiarContratoConcesiones(dfCatastro)
    dfCatastro = mercadosLib.limpiarPuestos(dfCatastro)
    dfCatastro = dfCatastro[~dfCatastro["CEDULA"].isin(catastroNoEncontrado["CEDULA"])]
    
    return dfCatastro

def handleDuplicados(dfCatastro):
    dfCatastro = dfCatastro.drop_duplicates(subset=["CEDULA", "PUESTO"], inplace=False)
    duplicados = dfCatastro[dfCatastro["CEDULA"].duplicated(keep=False)]
    dfCatastro = dfCatastro.drop(duplicados.index)
    dfCatastro = dfCatastro.sort_values('NOMBRES') # Ordena alfabéticamente
    dfCatastro = dfCatastro.reset_index(drop=True)
    return [duplicados, dfCatastro]

def handleUnificacion(dfUnificacion):
    #dfUnificacion = dfUnificacion.groupby(dfUnificacion['CEDULA']).aggregate(CEDULA=("CEDULA","first"), NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), VALOR=("VALOR", "first"), REGISTROS_SUMADOS=("REGISTROS_SUMADOS", "sum"), MERCADO=("MERCADO", "first"))
    dfUnificacion = dfUnificacion.groupby(dfUnificacion['CEDULA']).aggregate(CEDULA=("CEDULA","first"), NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), VALOR=("VALOR", "first"), REGISTROS_SUMADOS=("REGISTROS_SUMADOS", "sum"), MERCADO=("MERCADO", "first"), PUESTO_CATASTRO=("PUESTO_CATASTRO", "first"))
    dfUnificacion.rename(columns = {'DESCONTAR':'VALOR A DESCONTAR'}, inplace = True)
    
    return dfUnificacion
#==============================================================================================================================
#==============================================================================================================================
#==============================================================================================================================
#==============================================================================================================================
#==============================================================================================================================


def limpiarContratoConcesiones(DF):
    # intenta obtener solo concesiones
    c1 = DF["TIPO CONTRATO"]!="ARRIENDO"
    c2 = DF["TIPO CONTRATO"]!="ARRIENDOS"
    c3 = DF["TIPO CONTRATO"]!="EVENTUAL"
    c4 = DF["TIPO CONTRATO"]!="ARRIENDO "
    c5 = DF["TIPO CONTRATO"]!="ABANDONO "
    c6 = DF["TIPO CONTRATO"]!="ARRIENDO ABANDONO"
    c7 = DF["TIPO CONTRATO"]!="ABANDONO 2019"
    # c8 = DF["TIPO CONTRATO"]!="SIN CONSECIÓN"
    c9 = DF["TIPO CONTRATO"]!="CONVENIO"
    # c10 = DF["TIPO CONTRATO"]!="SIN CONSECIÒN"
    c11 = DF["TIPO CONTRATO"]!="Renuncia"
    
    #renuncia EXT-8316-2021
    #ADJUDICACION
    #fallecio EXT-1902-2021
    
    
    
    DF = DF[(c1) & (c2) & (c3) & (c4) & (c5) & (c6) & (c7) & (c9) & (c11)]
    # DF = DF[(c1) & (c2) & (c3) & (c4) & (c5) & (c6) & (c7) & (c8) & (c9) & (c10) & (c11)]
    contratosDiferentes = DF["TIPO CONTRATO"].drop_duplicates(inplace=False)
    return DF, contratosDiferentes




resagosDF = pd.read_excel('./Hoja de cálculo sin título PV.xlsx', dtype={"CEDULA": str, "PUESTO": str}, skiprows=0) # parte del catastro
# Se carga la blacklist: lista de registros cuyas cédulas no se encuentran registradas como contribuyentes
catastroNoEncontrado = pd.read_excel('./noContribuyentesCatastroTotal.xlsx', dtype={"CEDULA": str})
    
# ========================= SE LIMPIA EL ARCHIVOs DE CATASTRO  =====================
#======================= PROCESADO DEL ARCHIVO CON CEDULAS CORREGIDAS ==============

resagosDF = mercadosLib.limpiarMercado(resagosDF)
resagosDF = limpiarCatastro(resagosDF)


DF, contratosDiferentes = limpiarContratoConcesiones(resagosDF)






# ============== SE ELIMINAN CEDULAS QUE CUENTAN CON MÁS DE UN REGISTRO
# Estos registros deberían ser procesados aparte
duplicados, resagosDF = handleDuplicados(resagosDF)
#======================= PROCESADO DEL ARCHIVO CATASTRO MERCADOS PEQUEÑOS ==============

registrosMercadosProcesados = []
todosContratos = pd.DataFrame()
for i in range(len(arrayMercados)):
#for i in range(26,27):
#for i in range(17,18):
    df = pd.read_excel('./attachments/mercadospq.xlsx', sheet_name=arrayMercados[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(arrayMercados[i]["skip"]))
    print(i)
    print(arrayMercados[i]["nombre"])
    
    catastro = limpiarCatastro(df)
    DF, contratosDiferentes = limpiarContratoConcesiones(catastro)
    todosContratos = pd.concat([todosContratos, contratosDiferentes])
    
todosContratos = todosContratos.drop_duplicates()
    
    
    
     
#======================= PROCESADO DEL ARCHIVO CATASTRO ARENAL ==============

registrosArenalProcesados = []
todosContratos = pd.DataFrame()
for i in range(len(arrayArenal)):
#for i in range(26,27):
#for i in range(0,1):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=arrayArenal[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(arrayArenal[i]["skip"]))
    print(i)
    print(arrayArenal[i]["nombre"])
    
    catastro = limpiarCatastro(df)
    catastro["MERCADO"] = "EL ARENAL"
    
    DF, contratosDiferentes = limpiarContratoConcesiones(catastro)
    todosContratos = pd.concat([todosContratos, contratosDiferentes])
    
todosContratos = todosContratos.drop_duplicates()
    
    


dfGuadalupe = pd.DataFrame()
for i in range(len(unificarGuadalupe)):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=unificarGuadalupe[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(unificarGuadalupe[i]["skip"]))
      
    catastro = limpiarCatastro(df)
    dfGuadalupe = pd.concat([dfGuadalupe, catastro])

dfGuadalupe["MERCADO"] = "EL ARENAL"
duplicados, dfGuadalupe = handleDuplicados(dfGuadalupe)



#====================================================================================================
#====================================================================================================
#====================================================================================================
#====================================================================================================
#====================================================================================================

# Se buscan las cédulas que dentro de los exonerados no están en el catastro:
catastroCorrecto = pd.read_excel('./catastroCorrecto.xlsx', dtype={"CEDULA": str})
