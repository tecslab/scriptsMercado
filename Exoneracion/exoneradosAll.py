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

def getExonerados(catastro, arrayDFSRegistos):
    #registrosRecuperados = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION", "VALOR"])
    catastro.reset_index(drop=True, inplace=True)
    registrosRecuperados = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "PUESTO_CATASTRO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION"])
    aso29Julio = "SECCIÓN" in catastro #Solo la asociación 29 de julio tiene el campo sección
    for idx, cedulaCatastro in enumerate(catastro["CEDULA"]):
        puesto = catastro["PUESTO"].iloc[idx]
        valor = catastro["VALOR"].iloc[idx]
        mercadoCatastro = catastro["MERCADO"].iloc[idx]        
        for registroIdx, registroDF in enumerate(arrayDFSRegistos):
            #arrayDFSRegistos[registroIdx].reset_index(drop=True, inplace=True)                
            dfFiltrado= registroDF[registroDF["CEDULA"].isin([cedulaCatastro])]
            
            if (mercadoCatastro=="PLATAFORMA 27 DE FEBRERO"):
                #En la hoja de exoneración algunos del mercado 27 están mal categorizados
                dfFiltrado = dfFiltrado[(dfFiltrado["MERCADO"]==mercadoCatastro) | (dfFiltrado["MERCADO"]=="MERCADO 27 DE FEBRERO")]
            else:                
                dfFiltrado = dfFiltrado[dfFiltrado["MERCADO"]==mercadoCatastro]            
            
            if (registroIdx==0): # La hoja3 tiene información de puestos
            # Narancay no tiene campo puestos
            # igual miraflores
            # y otros en los que no se puede confiar
            # Los siguientes mercados tienen conflictos con los nombres de puestos
            #Mercado 3 de noviembre
            #plataforma narancay
            #estacion de tranferencia - Aso. 29 de julio#
                if ((mercadoCatastro != "PLATAFORMA NARANCAY") & (mercadoCatastro != "PLATAFORMA MIRAFLORES") & (mercadoCatastro!="MERCADO 3 DE NOVIEMBRE") & (not aso29Julio)):
                    dfFiltrado = dfFiltrado[dfFiltrado["PUESTO"]==puesto]
            
            # Elimina los registros encontrados
            arrayDFSRegistos[registroIdx] = arrayDFSRegistos[registroIdx].merge(dfFiltrado, how='left', indicator=True)
            arrayDFSRegistos[registroIdx] = arrayDFSRegistos[registroIdx][arrayDFSRegistos[registroIdx]['_merge'] == 'left_only']
            arrayDFSRegistos[registroIdx].drop('_merge', inplace=True, axis=1)
            arrayDFSRegistos[registroIdx].reset_index(drop=True, inplace=True)
            
            dfFiltrado.loc[ : , ["MERCADO"]] = mercadoCatastro
            dfFiltrado.loc[ : , ["VALOR"]] = valor         
            ######### IMPORTANTE: EJECUTAR PARA HACER COMPROBACION MANUAL DE PUESTOS ##############
            dfFiltrado.loc[ : , ["PUESTO_CATASTRO"]] = puesto
            registrosRecuperados = pd.concat([registrosRecuperados, dfFiltrado])
            #registrosRecuperados = registrosRecuperados[["CEDULA", "NOMBRES", "PUESTO", "PUESTO_CATASTRO", "VALOR A DESCONTAR", "OBSERVACION"]]
            
    registrosRecuperados = registrosRecuperados.groupby(registrosRecuperados['CEDULA']).aggregate(CEDULA=("CEDULA","first"), NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), VALOR=("VALOR", "first"), REGISTROS_SUMADOS=("MERCADO", "count"), MERCADO=("MERCADO", "first"), PUESTO_CATASTRO=("PUESTO_CATASTRO", "first"))
    registrosRecuperados.rename(columns = {'DESCONTAR':'VALOR A DESCONTAR'}, inplace = True)
    
    return [registrosRecuperados, arrayDFSRegistos]

def getRestantes(catastro, registrosRecuperados):
    ## Se obtienen los registros que no pasaron por el filtro
    registrosRestantes = catastro[~catastro["CEDULA"].isin(registrosRecuperados["CEDULA"])]
    registrosRestantes = registrosRestantes[["CEDULA", 'NOMBRES', "VALOR", "MERCADO"]]
    registrosRestantes = registrosRestantes.sort_values('NOMBRES') # Ordena alfabéticamente
    registrosRestantes = registrosRestantes.reset_index(drop=True)
    return registrosRestantes


def comparacionNombres(catastro, nombresDF):
    catastro.reset_index(drop=True, inplace=True)    
    ## Sería ideal sacar los duplicados para procesarlos aparte    
    registrosRecuperados2 = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION", "VALOR"])
    for idx, cedulaCatastro in enumerate(catastro["CEDULA"]):
        puesto = catastro["PUESTO"].iloc[idx]
        valor = catastro["VALOR"].iloc[idx]
        mercadoCatastro = catastro["MERCADO"].iloc[idx]
        nombres = catastro["NOMBRES"].iloc[idx]
        
        dfFiltrado = nombresDF[nombresDF["NOMBRES"].isin([nombres])]            
        dfFiltrado = dfFiltrado[dfFiltrado["MERCADO"]==mercadoCatastro]
        
        nombresDF = nombresDF.merge(dfFiltrado, how='left', indicator=True)
        nombresDF = nombresDF[nombresDF['_merge'] == 'left_only']
        nombresDF.drop('_merge', inplace=True, axis=1)
        nombresDF.reset_index(drop=True, inplace=True)
        
        dfFiltrado.loc[ : , ["VALOR"]] = valor
        dfFiltrado.loc[ : , ["CEDULA"]] = cedulaCatastro
        ######### IMPORTANTE: EJECUTAR PARA HACER COMPROBACION MANUAL DE PUESTOS ##############
        dfFiltrado.loc[ : , ["PUESTO_CATASTRO"]] = puesto
        registrosRecuperados2 = pd.concat([registrosRecuperados2, dfFiltrado])
    #registrosRecuperados2 = registrosRecuperados2.groupby(registrosRecuperados2['NOMBRES']).aggregate(CEDULA=('CEDULA', 'first'), NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), VALOR=("VALOR", "first"), REGISTROS_SUMADOS=("MERCADO", "count"), MERCADO=("MERCADO", "first"))
    registrosRecuperados2 = registrosRecuperados2.groupby(registrosRecuperados2['NOMBRES']).aggregate(CEDULA=('CEDULA', 'first'), NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), VALOR=("VALOR", "first"), REGISTROS_SUMADOS=("MERCADO", "count"), MERCADO=("MERCADO", "first"), PUESTO_CATASTRO=("PUESTO_CATASTRO", "first"))
    registrosRecuperados2.rename(columns = {'DESCONTAR':'VALOR A DESCONTAR'}, inplace = True)
       
    return [registrosRecuperados2, nombresDF]



def consultaCancelados(registrosRestantes):
    cantItems = "200"
    cedulasRestantes = registrosRestantes["CEDULA"].replace(regex=r'-', value="")
    for j in range(len(registrosRestantes)):
        cedula = cedulasRestantes.iloc[j]        
        cancelados_URL = "https://enlinea.cuenca.gob.ec/BackendConsultas/api/contribuyente/" + cedula + "/titulos/cancelados?page=1&nitems=" + cantItems
        canceladosRequest = requests.get(cancelados_URL)
        data = canceladosRequest.text        
        
        if (data=="No encontrado!"):
            registrosRestantes.loc[j, "NOTA_CEL"] = "No Encontrado" #CEL: Cuenca en línea
            continue        
        
        resultadosCancelados = json.loads(data)
        
        if ("tipo" in resultadosCancelados):
            registrosRestantes.loc[j, "NOTA_CEL"] = "No Encontrado"
            continue
        
        if (len(resultadosCancelados)==cantItems):
            print ("ADVERTENCIA: Pueden existir más registros que los obtenidos aqui")
    
        contTitulos = 0
        exonerado50Total = 0
        mesesNoExonerados = 0
        for item in resultadosCancelados:
            if ((item["PRE_CLAVE"][0:3]=="MER") | (item["PRE_CLAVE"][0:3]=="CLM")):
                añoEmision = item["TIC_FECHA_EMISION"][7:]
                if (añoEmision == "20"):
                    mesEmision = item["TIC_FECHA_EMISION"][3:6]
                    if (mesEmision=="MAR"):
                        registrosRestantes.loc[j, "EXON_MARZO"] = item["TIP_MONTO_EXONERACION"]
                    ##Mayo y abril no se emitieron títulos
                    if ((mesEmision=="JUL") | (mesEmision=="AUG") | (mesEmision=="SEP") | (mesEmision=="OCT") | (mesEmision=="NOV") | (mesEmision=="DEC")):
                        exonerado50Total += float(item["TIP_MONTO_EXONERACION"])
                        contTitulos +=1
                        if (item["TIP_MONTO_EXONERACION"]=="0"):
                            mesesNoExonerados +=1
        
        registrosRestantes.loc[j, "MESES_CON_TITULOS"] = contTitulos
        registrosRestantes.loc[j, "MESES_NO_EXONERADOS"] = mesesNoExonerados
        registrosRestantes.loc[j, "MESES_EXONERADOS"] = contTitulos - mesesNoExonerados
        registrosRestantes.loc[j, "MONTO_EXONERADO"] = exonerado50Total
        
    return registrosRestantes

# def separarExonerados(registros):
#     #Separa en Exonerados y no Exonerados
#     emptyDF = pd.DataFrame(columns=["MONTO_EXONERADO", "EXON_MARZO"]) # para asegurarnos que las columnas existan
#     registros = pd.concat([registros, emptyDF])
    
#     exoneradosByValor = registros[~registros["VALOR A DESCONTAR"].isnull()]

#     noEncontrados = registros.drop(exoneradosByValor.index)
#     exoneradosByCEL = noEncontrados[~noEncontrados["MONTO_EXONERADO"].isnull()]
    
#     if (not "EXON_MARZO" in exoneradosByCEL):
#         exoneradosByCEL["EXON_MARZO"]=None
#     exoneradosByCEL["EXON_MARZO"] = exoneradosByCEL["EXON_MARZO"].astype('float64')
#     exoneradosByCEL = exoneradosByCEL[(exoneradosByCEL["MONTO_EXONERADO"]>0) | (("EXON_MARZO" in exoneradosByCEL) & (~exoneradosByCEL["EXON_MARZO"].isnull()) & (exoneradosByCEL["EXON_MARZO"]>0))]
#     noExonerados = noEncontrados.drop(exoneradosByCEL.index)

#     exoneradosByCEL.loc[ exoneradosByCEL["EXON_MARZO"].isnull() , ["EXON_MARZO"]] = 0

#     exoneradosByCEL["VALOR A DESCONTAR"] = exoneradosByCEL["EXON_MARZO"] + exoneradosByCEL["MONTO_EXONERADO"]

#     exonerados = pd.concat([exoneradosByValor, exoneradosByCEL])
    
#     encontradosByNombre = exoneradosByValor[exoneradosByValor["CEDULA"].isnull()]["REGISTROS_SUMADOS"].sum()
#     encontradosByCedula = exoneradosByValor[~exoneradosByValor["CEDULA"].isnull()]["REGISTROS_SUMADOS"].sum()
    
#     return [exonerados, noExonerados, encontradosByNombre, encontradosByCedula]


# def getStats(exonerados, noExonerados, mercado, separarMercado):
#     # Obtiene estadísticas por mercado
#     if (separarMercado):
#         exoneradosMercado = exonerados[exonerados["MERCADO"]==mercado]["VALOR A DESCONTAR"].count()
#         noExoneradosMercado = noExonerados[noExonerados["MERCADO"]==mercado]["CEDULA"].count()
#         montoExoneracion = exonerados[exonerados["MERCADO"]==mercado]["VALOR A DESCONTAR"].sum()
#     else:
#         exoneradosMercado = exonerados["VALOR A DESCONTAR"].count()
#         noExoneradosMercado = noExonerados["CEDULA"].count()
#         montoExoneracion = exonerados["VALOR A DESCONTAR"].sum()
#     stats = {'MERCADO': mercado, 'EXONERADOS': [exoneradosMercado], 'NO_EXONERADOS': [noExoneradosMercado], "MONTO_EXONERACION": [montoExoneracion]}
#     stats = pd.DataFrame.from_dict(stats)
#     # Es necesario redondear los resultados de dinero desde el inicio
#     #stats = {'MERCADO': mercado, 'EXONERADOS': exoneradosMercado, 'NO_EXONERADOS': noExoneradosMercado, "MONTO_EXONERACION": "%.2f" % montoExoneracion}
#     return stats

def getStats(registrosCatastro, mercado, separarMercado):
    # Obtiene estadísticas por mercado
    if (separarMercado):
        exonerados = len(registrosCatastro[(registrosCatastro["MERCADO"]==mercado) & (registrosCatastro["NOTA_EXON"]=="EXONERADO")].index)
        noExonerados = len(registrosCatastro[(registrosCatastro["MERCADO"]==mercado) & (registrosCatastro["NOTA_EXON"]=="NO")].index)
        exoneradosParcial = len(registrosCatastro[(registrosCatastro["MERCADO"]==mercado) & (registrosCatastro["NOTA_EXON"]=="PARCIAL")].index)
        noData = len(registrosCatastro[(registrosCatastro["MERCADO"]==mercado) & (registrosCatastro["NOTA_EXON"]=="NODATA")].index)
        montoExoneracion = registrosCatastro[(registrosCatastro["MERCADO"]==mercado)]["VALOR A DESCONTAR"].sum() + registrosCatastro[(registrosCatastro["MERCADO"]==mercado)]["MONTO_TOTAL"].sum()
    else:
        exonerados = len(registrosCatastro[registrosCatastro["NOTA_EXON"]=="EXONERADO"].index)
        noExonerados = len(registrosCatastro[registrosCatastro["NOTA_EXON"]=="NO"].index)
        exoneradosParcial = len(registrosCatastro[registrosCatastro["NOTA_EXON"]=="PARCIAL"].index)
        noData = len(registrosCatastro[registrosCatastro["NOTA_EXON"]=="NODATA"].index)        
        montoExoneracion = registrosCatastro["VALOR A DESCONTAR"].sum() + registrosCatastro["MONTO_TOTAL"].sum()
    #todosLosRegistrosCorregidos.loc[ todosLosRegistrosCorregidos["VALOR A DESCONTAR"].isnull(), ["VALOR A DESCONTAR"]] = todosLosRegistrosCorregidos["MONTO_TOTAL"]
    stats = {'MERCADO': mercado, 'EXONERADOS': [exonerados], 'NO_EXONERADOS': [noExonerados], "PARCIAL": [exoneradosParcial], "NODATA": [noData], "MONTO_EXONERACION": [montoExoneracion]}
    stats = pd.DataFrame.from_dict(stats)
    return stats

def func(pct, allvals):
    #Función para el formato de etiquetas en los gráficos
    absolute = int(np.round(pct/100.*np.sum(allvals)))
    return "{:1.1f}%\n{:d}".format(pct, absolute)

def pieExonerados(nombreGrafico, sizesEyN):
    labels = 'EXONERADOS', 'NO_EXONERADOS'
    explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizesEyN, explode=explode, labels=labels, autopct=lambda pct: func(pct, sizesEyN),
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title(nombreGrafico)
    plt.show()
    
def pieExoneradosExt(nombreGrafico, sizesEyN):
    labels = 'EXONERADOS', 'NO_EXONERADOS', "PARCIAL", "NODATA"
    explode = (0.1, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizesEyN, explode=explode, labels=labels, autopct=lambda pct: func(pct, sizesEyN),
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title(nombreGrafico)
    plt.show()

    
def limpiarCatastro(dfCatastro):
    dfCatastro = mercadosLib.limpiarNombres(dfCatastro)
    dfCatastro = mercadosLib.limpiarCedula(dfCatastro)    
    dfCatastro = mercadosLib.limpiarContratoConcesiones(dfCatastro)
    dfCatastro = mercadosLib.limpiarPuestos(dfCatastro)
    dfCatastro = dfCatastro[~dfCatastro["CEDULA"].isin(catastroNoEncontrado["CEDULA"])] #Blacklist
    dfCatastro.reset_index(drop=True, inplace=True)
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



resagosDF = pd.read_excel('./Hoja de cálculo sin título PV.xlsx', dtype={"CEDULA": str, "PUESTO": str}, skiprows=0) # parte del catastro

#=============================== ARCHIVOS A COMPARAR ===========
nombresDF = pd.read_excel('./EXONERACION DE CONCESIONES Y ARRIENDOS.xlsx', dtype={"CEDULA": str}, skiprows=3)

concejalesH3 = pd.read_excel('./PEDIDO DE CONCEJALES EXONERACIONES.xlsx', sheet_name="Hoja3", dtype={"CEDULA": str, "PUESTO": str}, skiprows=0)
concejalesH5 = pd.read_excel('./PEDIDO DE CONCEJALES EXONERACIONES.xlsx', sheet_name="Hoja5", dtype={"CEDULA": str}, skiprows=2)
registrosConcejales = [concejalesH3, concejalesH5]

# Se carga la blacklist: lista de registros cuyas cédulas no se encuentran registradas como contribuyentes
catastroNoEncontrado = pd.read_excel('./noContribuyentesCatastroTotal.xlsx', dtype={"CEDULA": str})

# catastroCorrecto contiene solo cédulas que fueron validadas como contribuyentes y los resultados de la consulta de
# titulos cancelados en el sistema cuenca en línea
catastroCorrecto = pd.read_excel('./catastroCorrecto.xlsx', dtype={"CEDULA": str})
catastroCorrecto["CEDULA"] = catastroCorrecto["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")

#condicion de almenos 1 puesto
catastroCorrecto.loc[catastroCorrecto["NOTA_CEL"].isnull(), ["NOTA_EXON"]] = "EXONERADO"
catastroCorrecto["MONTO_TOTAL"] = catastroCorrecto.loc[catastroCorrecto["NOTA_CEL"].isnull(), ["MONTO_EXON_MARZO", "MONTO_EXON_50"]].sum(axis=1)

catastroCorrecto.loc[(catastroCorrecto["TITULOS_50"]>0), "NOTA_CEL"] = "1puesto"
catastroCorrecto.loc[(catastroCorrecto["TITULOS_MARZO"]>0), "NOTA_CEL"] = "1puesto"
#Condiciones de al menos 2 puestos:
catastroCorrecto.loc[(catastroCorrecto["TITULOS_50"]>6), "NOTA_CEL"] = "2puestos"
catastroCorrecto.loc[(catastroCorrecto["TITULOS_MARZO"]>1), "NOTA_CEL"] = "2puestos"


#Categorizar si canceló o no todos los títulos
#si tiene un puesto los titulos completos son 7, si tiene 2 son 14
catastroCorrecto["TITULOS_PAGADOS"] = catastroCorrecto.loc[(catastroCorrecto["NOTA_CEL"]=="1puesto") | (catastroCorrecto["NOTA_CEL"]=="2puestos"), ["TITULOS_MARZO", "TITULOS_50"]].sum(axis=1)
# Los títulos que se encuentran en los registros de exoneración tienen el camnpo exoneración en 0 desde el cuenca en línea
catastroCorrecto["TITULOS_EXON"] = catastroCorrecto.loc[(catastroCorrecto["NOTA_CEL"]=="1puesto") | (catastroCorrecto["NOTA_CEL"]=="2puestos"), ["EXON_MARZO", "EXON_50"]].sum(axis=1)
catastroCorrecto["NOTA_EXON"]="NODATA"
catastroCorrecto.loc[((catastroCorrecto["NOTA_CEL"]=="1puesto") | (catastroCorrecto["NOTA_CEL"]=="2puestos")), ["NOTA_EXON"]] = "PARCIAL"
catastroCorrecto.loc[((catastroCorrecto["NOTA_CEL"]=="1puesto") | (catastroCorrecto["NOTA_CEL"]=="2puestos")) & (catastroCorrecto["TITULOS_EXON"] == 0), ["NOTA_EXON"]] = "NO"
catastroCorrecto.loc[((catastroCorrecto["NOTA_CEL"]=="1puesto") | (catastroCorrecto["NOTA_CEL"]=="2puestos")) & (catastroCorrecto["TITULOS_PAGADOS"]==catastroCorrecto["TITULOS_EXON"]), ["NOTA_EXON"]] = "EXONERADO"

catastroCorrecto["REV_PENDIENTES"] = "SI" # si no están completos los esquemas de pago entonces es necesario revisar los títulos pendientes
catastroCorrecto.loc[(catastroCorrecto["NOTA_CEL"]=="1puesto") & (catastroCorrecto["TITULOS_PAGADOS"]==7), "REV_PENDIENTES"] = "NO" # PAGOS COMPLETOS
catastroCorrecto.loc[(catastroCorrecto["NOTA_CEL"]=="2puestos") & (catastroCorrecto["TITULOS_PAGADOS"]==14), "REV_PENDIENTES"] = "NO"

#Se dará 2 tipos de exonerados, los que de verdad están y los que deben revisarse
#Si no tiene completo es necesario revisar los pendientes
#Nota de revisar y categorizacion de exonerados
# Los que categorizados como 1puesto podrían tener 2, esto debería ser complementado con los títulos pendientes
# igualmente, quienes no han pagado nada pueden tener 1 o más puestos



#=============================== SE LIMPIA LOS ARCHIVOS A COMPARAR ===========
registrosConcejalesProcesado = []

for idx, hojaRegistros in enumerate(registrosConcejales):
    hojaRegistros = mercadosLib.limpiarCedula(hojaRegistros)
    hojaRegistros = mercadosLib.limpiarMercado(hojaRegistros)
    hojaRegistros = mercadosLib.limpiarNombres(hojaRegistros)
    if (idx==1):
        hojaRegistros = mercadosLib.eliminarAmbigüedad(hojaRegistros)
    elif (idx==0):
        hojaRegistros = mercadosLib.limpiarPuestos(hojaRegistros)
    hojaRegistros = hojaRegistros.reset_index(drop=True)
    registrosConcejalesProcesado.append(hojaRegistros)
    
# limpieza de archivos de nombres
nombresDF = mercadosLib.limpiarNombres(nombresDF)
nombresDF = mercadosLib.limpiarMercado(nombresDF)
    
# Calcula el monto total de la exoneración, sin tomar en cuenta si se encontró o no
totalH3 = registrosConcejalesProcesado[0]["VALOR A DESCONTAR"].sum()
totalH5 = registrosConcejalesProcesado[0]["VALOR A DESCONTAR"].sum()
totalNombres = nombresDF["VALOR A DESCONTAR"].sum()
totalExoneracion = totalH3 + totalH5 + totalNombres
    
# ========================= SE LIMPIA EL ARCHIVOs DE CATASTRO  =====================
#======================= PROCESADO DEL ARCHIVO CON CEDULAS CORREGIDAS ==============
resagosDF = mercadosLib.limpiarMercado(resagosDF)
resagosDF = limpiarCatastro(resagosDF)

# ============== SE ELIMINAN CEDULAS QUE CUENTAN CON MÁS DE UN REGISTRO
# Estos registros deberían ser procesados aparte
duplicadosResagos, resagosDF = handleDuplicados(resagosDF)

#===================== Se hacen las comparaciones con los archivos
registrosRecuperados, registrosConcejalesProcesado = getExonerados(resagosDF, registrosConcejalesProcesado)
[registrosRecuperadosNombres, nombresDF] = comparacionNombres(resagosDF, nombresDF)

unificacionRecuperados = pd.concat([registrosRecuperados, registrosRecuperadosNombres])   

# =========================  PARA OBTENER LA SUMA DE LO VALORES DE CADA COMERCIANTE =========================

unificacionRecuperados = handleUnificacion(unificacionRecuperados)
#============================================================================================================

registrosRestantes = getRestantes(resagosDF, unificacionRecuperados)

if (consultarCancelados):
    registrosRestantes = consultaCancelados(registrosRestantes)
    
####**********============= DEFINIR AQUI UN CRITERIO PARA EXONERADOS MEDIANTE LO OBTENIDO EN EL CUENCA EN LÍNEA =====
registrosRestantes = registrosRestantes.merge(catastroCorrecto, how = 'inner', on = ['CEDULA'])

#todosLosRegistros = pd.concat([registrosRecuperados, registrosRestantes])
todosLosRegistrosCorregidos = pd.concat([unificacionRecuperados, registrosRestantes])


#======================= PROCESADO DEL ARCHIVO CATASTRO MERCADOS PEQUEÑOS ==============
registrosMercadosProcesados = []
duplicadosMercados = []
for i in range(len(arrayMercados)):
#for i in range(26,27):
#for i in range(17,18):
    df = pd.read_excel('./attachments/mercadospq.xlsx', sheet_name=arrayMercados[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(arrayMercados[i]["skip"]))
    print(i)
    print(arrayMercados[i]["nombre"])
    
    catastro = limpiarCatastro(df)
    
    catastro["MERCADO"] = arrayMercados[i]["nombre"]
    if (arrayMercados[i]["nombre"] == "MERCADO 12 ABRIL  FRUTAS TEMPOR"):
        catastro["MERCADO"] = "MERCADO 12 DE ABRIL" # Se puede tratar como un giro más del mercado 12 de abril
    
    duplicados, catastro = handleDuplicados(catastro)
    
    registrosRecuperados, registrosConcejalesProcesado  = getExonerados(catastro, registrosConcejalesProcesado)
    [registrosRecuperadosNombres, nombresDF] = comparacionNombres(catastro, nombresDF)
    
    unificacionRecuperados = pd.concat([registrosRecuperados, registrosRecuperadosNombres])    
    
    # =========================  PARA OBTENER LA SUMA DE LO VALORES DE CADA COMERCIANTE ========================   
    unificacionRecuperados = handleUnificacion(unificacionRecuperados)
    #============================================================================================================
    
    ## Se obtienen los registros que no pasaron por el filtro
    registrosRestantes = getRestantes(catastro, unificacionRecuperados)
    registrosRestantes = registrosRestantes.merge(catastroCorrecto, how = 'inner', on = ['CEDULA'])
    #====================================================================================================
    #=====================  CONSULTA DE TITULOS CANCELADOS EN SISTEMA CUENCA EN LINEA ===================
    if (consultarCancelados):
        registrosRestantes = consultaCancelados(registrosRestantes)
    #====================================================================================================
    #====================================================================================================    
    
    todosLosRegistrosMercados = pd.concat([unificacionRecuperados, registrosRestantes])
    registrosMercadosProcesados.append(todosLosRegistrosMercados)
    duplicadosMercados.append(duplicados)
     
#======================= PROCESADO DEL ARCHIVO CATASTRO ARENAL ==============

registrosArenalProcesados = []
duplicadosArenal = []
for i in range(len(arrayArenal)):
#for i in range(26,27):
#for i in range(0,1):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=arrayArenal[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(arrayArenal[i]["skip"]))
    print(i)
    print(arrayArenal[i]["nombre"])
    
    catastro = limpiarCatastro(df)
    catastro["MERCADO"] = "EL ARENAL"
    
    duplicados, catastro = handleDuplicados(catastro)
    
    registrosRecuperados, registrosConcejalesProcesado = getExonerados(catastro, registrosConcejalesProcesado)
    [registrosRecuperadosNombres, nombresDF] = comparacionNombres(catastro, nombresDF)
    
    unificacionRecuperados = pd.concat([registrosRecuperados, registrosRecuperadosNombres])
    # =========================  PARA OBTENER LA SUMA DE LO VALORES DE CADA COMERCIANTE ========================   
    unificacionRecuperados = handleUnificacion(unificacionRecuperados)
    #============================================================================================================
    registrosRestantes = getRestantes(catastro, unificacionRecuperados)
    registrosRestantes = registrosRestantes.merge(catastroCorrecto, how = 'inner', on = ['CEDULA'])
    #====================================================================================================
    #=====================  CONSULTA DE TITULOS CANCELADOS EN SISTEMA CUENCA EN LINEA ===================
    if (consultarCancelados):
        registrosRestantes = consultaCancelados(registrosRestantes)
    #====================================================================================================
    #====================================================================================================    
    
    todosLosRegistrosArenal = pd.concat([unificacionRecuperados, registrosRestantes])
    registrosArenalProcesados.append(todosLosRegistrosArenal)
    duplicadosArenal.append(duplicados)


dfGuadalupe = pd.DataFrame()
for i in range(len(unificarGuadalupe)):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=unificarGuadalupe[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(unificarGuadalupe[i]["skip"]))
      
    catastro = limpiarCatastro(df)
    dfGuadalupe = pd.concat([dfGuadalupe, catastro])

dfGuadalupe.reset_index(drop=True, inplace=True)
dfGuadalupe["MERCADO"] = "EL ARENAL"
duplicadosGuadalupe, dfGuadalupe = handleDuplicados(dfGuadalupe)

registrosRecuperados, registrosConcejalesProcesado = getExonerados(dfGuadalupe, registrosConcejalesProcesado)
[registrosRecuperadosNombres, nombresDFFinal] = comparacionNombres(dfGuadalupe, nombresDF)

unificacionRecuperados = pd.concat([registrosRecuperados, registrosRecuperadosNombres])
# =========================  PARA OBTENER LA SUMA DE LO VALORES DE CADA COMERCIANTE ========================   
unificacionRecuperados = handleUnificacion(unificacionRecuperados)
#============================================================================================================
registrosRestantes = getRestantes(dfGuadalupe, unificacionRecuperados)
registrosRestantes = registrosRestantes.merge(catastroCorrecto, how = 'inner', on = ['CEDULA'])
#====================================================================================================
#=====================  CONSULTA DE TITULOS CANCELADOS EN SISTEMA CUENCA EN LINEA ===================
if (consultarCancelados):
    registrosRestantes = consultaCancelados(registrosRestantes)
#====================================================================================================
todosLosRegistrosGuadalupe = pd.concat([unificacionRecuperados, registrosRestantes])


#====================================================================================================
#====================================================================================================
#====================================================================================================
#====================================================================================================
#====================================================================================================

# Se buscan las cédulas que dentro de los exonerados no están en el catastro:
registrosConcejalesProcesado[0]["ORIGEN"] = "H3"
registrosConcejalesProcesado[1]["ORIGEN"] = "H5"
registrosConcejalesProcesado[1]["PUESTO"] = "NoDef"
registrosConcejalesProcesado[1]["VALOR"] = "NoDef"

registrosSobrantes = pd.concat([registrosConcejalesProcesado[0], registrosConcejalesProcesado[1]])
registrosSobrantes = registrosSobrantes[["CEDULA", "NOMBRES", "MERCADO", "VALOR A DESCONTAR", "ORIGEN", "VALOR", "PUESTO"]].sort_values('NOMBRES')

# Se obtiene datos sobre los registros sobrantes
cantSobrantes = len(registrosSobrantes)
print("Se tienen: " + str(cantSobrantes) + " registros sobrantes.")
sobrantesNoCatastrados = registrosSobrantes[~registrosSobrantes["CEDULA"].isin(catastroCorrecto["CEDULA"])]
print ("Existen " + str(len(sobrantesNoCatastrados)) + " registros exonerados que no están en el catastro")
comerciantesNoCatastrados = sobrantesNoCatastrados.drop_duplicates(subset=["CEDULA"], inplace=False)
print ("Correspondientes a " + str(len(comerciantesNoCatastrados)) + " comerciantes")
sobrantesNoCatastrados.sort_values('NOMBRES').to_excel("./sobrantesExoneraciónNoCatastrados.xlsx")

#fromBlackList = comerciantesNoCatastrados[comerciantesNoCatastrados["NOMBRES"].isin(catastroNoEncontrado["NOMBRES"])]
#print(len(fromBlackList)) #0

sobrantesCatastrados = registrosSobrantes[registrosSobrantes["CEDULA"].isin(catastroCorrecto["CEDULA"])]
#Se saca aparte los sobrantes que están en la lista de duplicados
exoneradosDuplicados = sobrantesCatastrados[sobrantesCatastrados["CEDULA"].isin(duplicadosResagos["CEDULA"])]
sobrantesCatastrados = sobrantesCatastrados[~sobrantesCatastrados["CEDULA"].isin(duplicadosResagos["CEDULA"])]

for dfDuplicados in duplicadosMercados:
    exoneradosDuplicados = pd.concat([exoneradosDuplicados, sobrantesCatastrados[sobrantesCatastrados["CEDULA"].isin(dfDuplicados["CEDULA"])]])
    sobrantesCatastrados = sobrantesCatastrados[~sobrantesCatastrados["CEDULA"].isin(dfDuplicados["CEDULA"])]

for dfDuplicados in duplicadosArenal:
    exoneradosDuplicados = pd.concat([exoneradosDuplicados, sobrantesCatastrados[sobrantesCatastrados["CEDULA"].isin(dfDuplicados["CEDULA"])]])
    sobrantesCatastrados = sobrantesCatastrados[~sobrantesCatastrados["CEDULA"].isin(dfDuplicados["CEDULA"])]

exoneradosDuplicados = pd.concat([exoneradosDuplicados, sobrantesCatastrados[sobrantesCatastrados["CEDULA"].isin(duplicadosGuadalupe["CEDULA"])]])
sobrantesCatastrados = sobrantesCatastrados[~sobrantesCatastrados["CEDULA"].isin(duplicadosGuadalupe["CEDULA"])]

comerciantesSobrantesCatastrados = sobrantesCatastrados.drop_duplicates(subset=["CEDULA"], inplace=False)
print("Los sobrantes catastrados corresponden a " + str(len(comerciantesSobrantesCatastrados)) + " comerciantes")

# Muchos de los sobrantes catastrados son los casos duplicados
# En otros, la persona tiene locales en más de un mercado y posiblemente renuncio a uno de ellos
# En otros el número de puesto o mercado no coincide
# Aveces el cc 9oct lo categorizan como mercado

#==========================  SE ASUME QUE LOS SOBRANTES No CATASTRADOS SI DEBERÍAN ESTARLO ==============
# =========================  A ESTOS REGISTROS SOLO SE LOS AGRUPA Y SE LOS SUMA =========================
# También se asumen que tienen un solo puesto
sobrantesNoCatastrados = sobrantesNoCatastrados.groupby(sobrantesNoCatastrados['CEDULA']).aggregate(CEDULA=("CEDULA","first"), NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), REGISTROS_SUMADOS=("MERCADO", "count"), MERCADO=("MERCADO", "first"), PUESTO=("PUESTO", "first"), VALOR=("VALOR", "first"))
sobrantesNoCatastrados.rename(columns = {'DESCONTAR':'VALOR A DESCONTAR'}, inplace = True)
#============================================================================================================

nombresDFFinal.sort_values('NOMBRES').to_excel("./hojaNombresPrevia.xlsx")
[registrosRecuperados, nombresDF] = comparacionNombres(sobrantesNoCatastrados, nombresDFFinal)
unificacionSobrantes = pd.concat([sobrantesNoCatastrados, registrosRecuperados])

#====== AGRUPA NUEVAMENTE
unificacionSobrantes = unificacionSobrantes.groupby(unificacionSobrantes['CEDULA']).aggregate(CEDULA=("CEDULA","first"), NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), REGISTROS_SUMADOS=("REGISTROS_SUMADOS", "sum"), MERCADO=("MERCADO", "first"))
unificacionSobrantes.rename(columns = {'DESCONTAR':'VALOR A DESCONTAR'}, inplace = True)
#============================================================================================================
#============================================================================================================
#============================================================================================================
if (excelsResultados==True):
    emptyDF = pd.DataFrame()
    emptyDF.to_excel('./procesadosMercados.xlsx')
    emptyDF.to_excel('./procesadosArenal.xlsx')
    emptyDF.to_excel('./duplicadosArenal.xlsx')
    emptyDF.to_excel('./duplicadosMercados.xlsx')
    
    todosLosRegistrosCorregidos.to_excel('./procesadosCorregidos.xlsx')
    todosLosRegistrosGuadalupe.to_excel('./procesadosGuadalupe.xlsx')
    unificacionSobrantes.to_excel("./procesadoCatastroSobrante.xlsx")
    nombresDF.sort_values('NOMBRES').to_excel("./hojaNombres.xlsx")   
    duplicadosGuadalupe.to_excel("./duplicadosAsoGuadalupe.xlsx")
    
    hoja3Depurada = registrosConcejalesProcesado[0][~registrosConcejalesProcesado[0]["CEDULA"].isin(sobrantesNoCatastrados["CEDULA"])]
    hoja5Depurada = registrosConcejalesProcesado[1][~registrosConcejalesProcesado[1]["CEDULA"].isin(sobrantesNoCatastrados["CEDULA"])]
    
    hoja3Depurada.to_excel("./hoja3Concejales.xlsx")
    hoja5Depurada.to_excel("./hoja5Concejales.xlsx")
    
    for i in range(len(arrayMercados)):
        with pd.ExcelWriter('./procesadosMercados.xlsx', mode='a', engine="openpyxl") as writer:
            registrosMercadosProcesados[i].to_excel(writer, sheet_name=arrayMercados[i]["nombre"])
        with pd.ExcelWriter('./duplicadosMercados.xlsx', mode='a', engine="openpyxl") as writer:
            duplicadosMercados[i].to_excel(writer, sheet_name=arrayMercados[i]["nombre"])
    
    for i in range(len(arrayArenal)):
        with pd.ExcelWriter('./procesadosArenal.xlsx', mode='a', engine="openpyxl") as writer:
            registrosArenalProcesados[i].to_excel(writer, sheet_name=arrayArenal[i]["nombre"])
        with pd.ExcelWriter('./duplicadosArenal.xlsx', mode='a', engine="openpyxl") as writer:
            duplicadosArenal[i].to_excel(writer, sheet_name=arrayArenal[i]["nombre"])
    
    sobrantesCatastrados.to_excel("./sobrantesExoneraciónEnCatastro.xlsx")
    exoneradosDuplicados.to_excel("./sobrantesExoneraciónEnDuplicados.xlsx")
    

    #registrosConcejalesProcesado[0].to_excel("./hoja3Concejales.xlsx")
    #registrosConcejalesProcesado[1].to_excel("./hoja5Concejales.xlsx")
    






#========================================================================================================================
#========================================================================================================================
#=============================================== ESTADÍSTICAS ===========================================================
#========================================================================================================================
#========================================================================================================================
# if (useFiles):
#     # Sirve si se quiere saltar la consulta al en linea si ya hay archivos que contienen las consultas
#     todosLosRegistrosCorregidos = pd.read_excel('./consolidado/procesadosCorregidos.xlsx', dtype={"CEDULA": str}, skiprows=0)
#     registrosMercadosProcesados = []
#     for i in range(len(arrayMercados)):
#         df = pd.read_excel('./consolidado/procesadosMercados.xlsx', sheet_name=arrayMercados[i]["nombre"], dtype={"CEDULA": str}, skiprows=0)
#         registrosMercadosProcesados.append(df)
    
#     registrosArenalProcesados = []
#     for i in range(len(arrayArenal)):
#         df = pd.read_excel('./consolidado/procesadosArenal.xlsx', sheet_name=arrayArenal[i]["nombre"], dtype={"CEDULA": str}, skiprows=0)
#         registrosArenalProcesados.append(df)



todosLosRegistrosCorregidos.loc[ ~todosLosRegistrosCorregidos["VALOR A DESCONTAR"].isnull(), ["NOTA_EXON"]] = "EXONERADO"
mercadosDistintos = todosLosRegistrosCorregidos["MERCADO"].drop_duplicates(inplace=False)

#=========== Se procesa cada Dataframe
resumen = pd.DataFrame(columns=["MERCADO", "EXONERADOS", "NO_EXONERADOS", "PARCIAL", "NODATA", "MONTO_EXONERACION"])
for mercado in mercadosDistintos:
    stats = getStats(todosLosRegistrosCorregidos, mercado, True)
    resumen = pd.concat([resumen, stats])

for idx, mercadosDF in enumerate(registrosMercadosProcesados):
    mercadosDF.loc[ ~mercadosDF["VALOR A DESCONTAR"].isnull(), ["NOTA_EXON"]] = "EXONERADO"    
    stats = getStats(mercadosDF, arrayMercados[idx]["nombre"], False)
    resumen = pd.concat([resumen, stats])
    
for arenalDF in registrosArenalProcesados:
    arenalDF.loc[ ~arenalDF["VALOR A DESCONTAR"].isnull(), ["NOTA_EXON"]] = "EXONERADO"    
    stats = getStats(arenalDF, "EL ARENAL", False)
    resumen = pd.concat([resumen, stats])
    

todosLosRegistrosGuadalupe.loc[ ~todosLosRegistrosGuadalupe["VALOR A DESCONTAR"].isnull(), ["NOTA_EXON"]] = "EXONERADO"
stats = getStats(todosLosRegistrosGuadalupe, "EL ARENAL", False)
resumen = pd.concat([resumen, stats])

#=============================================================
# Se obtienen estadísticas antes y después de incluir los sobrantes
resumenPrevio = resumen.groupby(resumen['MERCADO']).aggregate(MERCADO=('MERCADO', 'first'), EXONERADOS=('EXONERADOS', 'sum'), NO_EXONERADOS=("NO_EXONERADOS", "sum"), PARCIAL=("PARCIAL", "sum"), NODATA=("NODATA", "sum"), MONTO_EXONERACION=("MONTO_EXONERACION", "sum"))
totalExoneradosPrevio = resumenPrevio['EXONERADOS'].sum()
totalNoExoneradosPrevio = resumenPrevio['NO_EXONERADOS'].sum()
totalParcialPrevio = resumenPrevio['PARCIAL'].sum()
totalNoDataPrevio = resumenPrevio['NODATA'].sum()

montoTotalPrevio = resumenPrevio["MONTO_EXONERACION"].sum()
pieExonerados("Catastro Entregado", [totalExoneradosPrevio, totalNoExoneradosPrevio])
pieExoneradosExt("Catastro Entregado", [totalExoneradosPrevio, totalNoExoneradosPrevio, totalParcialPrevio, totalNoDataPrevio])

mercadosDistintos = unificacionSobrantes["MERCADO"].drop_duplicates(inplace=False)
for mercado in mercadosDistintos:
    regAnalizar = unificacionSobrantes[unificacionSobrantes["MERCADO"]==mercado]
    montoExoneracion = regAnalizar["VALOR A DESCONTAR"].sum()
    stats = {'MERCADO': mercado, 'EXONERADOS': [len(regAnalizar)], 'NO_EXONERADOS': [0], "PARCIAL": [0], "NODATA": [0], "MONTO_EXONERACION": [montoExoneracion]}
    stats = pd.DataFrame.from_dict(stats)
    resumen = pd.concat([resumen, stats])

resumenPost = resumen.groupby(resumen['MERCADO']).aggregate(MERCADO=('MERCADO', 'first'), EXONERADOS=('EXONERADOS', 'sum'), NO_EXONERADOS=("NO_EXONERADOS", "sum"), PARCIAL=("PARCIAL", "sum"), NODATA=("NODATA", "sum"), MONTO_EXONERACION=("MONTO_EXONERACION", "sum"))
totalExoneradosPost = resumenPost['EXONERADOS'].sum()
montoTotalPost = resumenPost["MONTO_EXONERACION"].sum()

#duplicado 4+36+28+36 = 104

# #========================== GRAFICOS ================================================

pieExonerados("Catastro Extendido", [totalExoneradosPost, totalNoExoneradosPrevio])
pieExoneradosExt("Catastro Entregado", [totalExoneradosPost, totalNoExoneradosPrevio, totalParcialPrevio, totalNoDataPrevio])



## FUENTES DE ERROR
# Los archivos de nombres y la hoja5 no contienen puestos, y dado que hay varios comerciantes con puestos en varios mercados/sectoresArenal
# no se puede asegurar que se encuentran agrupadas los registros de exoneración de un mismo puesto

# no aparecen en el catastro renuncias, fallecidos, errores de tipeo en la cedula
# Los errores de tipeo en cedula posiblemente esten en la blacklist



# Plataforma 27
#BELISARIO ANDRADE, PLATAFPORMA LATERAL