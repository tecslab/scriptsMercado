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
from importlib import reload

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
    # En este punto la hoja5 está vacía pero se dejará tal cual la función sin modificar
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
    registrosRecuperados["IND_EXON"] = 1
    
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

def getStats(registrosCatastro, mercado, separarMercado):
    # Obtiene estadísticas por mercado
    if (separarMercado):
        registrosCatastro = registrosCatastro[registrosCatastro["MERCADO"]==mercado]
    
    indicesDiferentes = registrosCatastro["IND_EXON"].drop_duplicates()
    tabulacionIndices = {}
    for indice in indicesDiferentes:
        cantidad = len(registrosCatastro[registrosCatastro["IND_EXON"]==indice].index)
        indice = str(round(indice*100, 2))
        tabulacionIndices[indice]=cantidad
    
    tabulacionResumida = {"0":0, "0-25":0, "25-50":0, "50-75":0, "75-100":0, "100":0}
    for indice in tabulacionIndices:
        indiceNum = float(indice)
        if (indiceNum==0):
            tabulacionResumida["0"]=tabulacionIndices[indice]
        elif ((indiceNum>0) & (indiceNum<=25)):
            tabulacionResumida["0-25"] = tabulacionResumida["0-25"] + tabulacionIndices[indice]
        elif ((indiceNum>25) & (indiceNum<=50)):
            tabulacionResumida["25-50"] = tabulacionResumida["25-50"] + tabulacionIndices[indice]
        elif ((indiceNum>50) & (indiceNum<=75)):
            tabulacionResumida["50-75"] = tabulacionResumida["50-75"] + tabulacionIndices[indice]
        elif ((indiceNum>75) & (indiceNum<100)):
            tabulacionResumida["75-100"] = tabulacionResumida["75-100"] + tabulacionIndices[indice]
        elif (indiceNum==100):
            tabulacionResumida["100"]=tabulacionIndices[indice]
        
    #todosLosRegistrosCorregidos.loc[ todosLosRegistrosCorregidos["VALOR A DESCONTAR"].isnull(), ["VALOR A DESCONTAR"]] = todosLosRegistrosCorregidos["MONTO_TOTAL"]
    stats = {'MERCADO': mercado, "INDICES": [tabulacionIndices]}
    stats.update(tabulacionResumida)
    stats = pd.DataFrame.from_dict(stats)
    return stats

def func(pct, allvals):
    #Función para el formato de etiquetas en los gráficos
    absolute = int(np.round(pct/100.*np.sum(allvals)))
    return "{:1.1f}%\n{:d}".format(pct, absolute)

def pieExonerados(nombreGrafico, sizesEyN):
    labels = 'NO_EXONERADOS', "HASTA 25%", "HASTA 50%", "HASTA 75%", ">75% y <100%", 'EXONERADOS'
    explode = (0, 0, 0, 0, 0, 0.2)  # only "explode" the 2nd slice (i.e. 'Hogs')

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
    dfCatastro = dfCatastro.drop_duplicates(subset=["CEDULA", "PUESTO"], inplace=False)
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

def separarTitulosMes(DF, mes): #OBSOLETO
    dfSeparado = DF[DF["MES"]==mes]
    dfSeparado.loc[ DF["EXO"]=="NO", ["EXO"]] = None
    dfSeparado = dfSeparado.groupby('CEDULA').aggregate(CEDULA=("CEDULA","first"), NOMBRE=("NOMBRE","first"), MES=('MES', 'count'), EXO=('EXO', 'count'), STATUS=('STATUS', 'first')) #despúes de analizar el estatus de un mes es siempre el mismo
    dfSeparado.rename(columns = {"MES":mes, "EXO": "EXO_"+mes}, inplace = True)
    dfSeparado.reset_index(inplace=True, drop=True)
    return dfSeparado

def unificarTitulos(dfSeparado):
    cedulasDistintas = dfSeparado.drop_duplicates(subset="CEDULA")
    cedulasDistintas.reset_index(inplace=True, drop=True)
    unificacionTitulos = pd.DataFrame(columns=["CEDULA", "NOMBRE", "MARZO 2020", "EXONERA MARZO 2020", "JULIO 2020", "EXONERA JULIO 2020", "AGOSTO 2020", "EXONERA AGOSTO 2020", "SEPTIEMBRE 2020", "EXONERA SEPTIEMBRE 2020", "OCTUBRE 2020", "EXONERA OCTUBRE 2020", "NOVIEMBRE 2020", "EXONERA NOVIEMBRE 2020", "DICIEMBRE 2020", "EXONERA DICIEMBRE 2020"])
    for idxCedula, cedula in cedulasDistintas.iterrows():
        registroMeses = pd.DataFrame({
            "CEDULA": [cedula["CEDULA"]],
            "NOMBRE": [cedula["NOMBRE"]], 
            "MARZO 2020": None,
            "EXONERA MARZO 2020": None, 
            "JULIO 2020": None, 
            "EXONERA JULIO 2020": None, 
            "AGOSTO 2020": None, 
            "EXONERA AGOSTO 2020": None, 
            "SEPTIEMBRE 2020": None, 
            "EXONERA SEPTIEMBRE 2020": None,
            "OCTUBRE 2020": None,
            "EXONERA OCTUBRE 2020": None,
            "NOVIEMBRE 2020": None,
            "EXONERA NOVIEMBRE 2020": None,
            "DICIEMBRE 2020": None,
            "EXONERA DICIEMBRE 2020": None})
        
        registrosCedula = dfSeparado[dfSeparado["CEDULA"]==cedula["CEDULA"]]        
        for mes in registrosCedula["MES"]:
            registroMes = registrosCedula.loc[registrosCedula["MES"]==mes]            
            registroMes.reset_index(inplace=True, drop=True)
            registroMeses.loc[registroMeses["CEDULA"]==cedula["CEDULA"], mes+" 2020"] = registroMes.iloc[[0]]["ESTATUS"]
            registroMeses.loc[registroMeses["CEDULA"]==cedula["CEDULA"], "EXONERA "+mes+" 2020"] = registroMes.iloc[[0]]["EXO"]
            
        unificacionTitulos = pd.concat([unificacionTitulos, registroMeses])
    return unificacionTitulos
    

def procesarRentas2P(DFRentas):
    # esta forma de separar quizas no es la más adecuada porque mezcla los registros de los 2 puestos
    # Estos registros no contienen títulos pendientes sin exoneración
    DFRentas = DFRentas[DFRentas["ESTATUS"]!="BAJA"]
    DFRentas["CLA"] = DFRentas["CLA"].replace(regex=[r'.*CLM.*'], value="CLM")
    DFRentas["CLA"] = DFRentas["CLA"].replace(regex=[r'.*MER.*'], value="MER")

    catastroRentas2PCLM = DFRentas[DFRentas["CLA"]=="CLM"]
    catastroRentas2PCLM1 = catastroRentas2PCLM.drop_duplicates(subset=["CEDULA", "MES"])
    catastroRentas2PCLM2 = catastroRentas2PCLM.drop(catastroRentas2PCLM1.index)
    
    catastroRentas2PMER = DFRentas[DFRentas["CLA"]=="MER"]
    catastroRentas2PMER1 = catastroRentas2PMER.drop_duplicates(subset=["CEDULA", "MES"])
    catastroRentas2PMER2 = catastroRentas2PMER.drop(catastroRentas2PMER1.index)
    
    catastroRentas2PCLM1 = unificarTitulos(catastroRentas2PCLM1)
    catastroRentas2PCLM2 = unificarTitulos(catastroRentas2PCLM2)
    catastroRentas2PMER1 = unificarTitulos(catastroRentas2PMER1)
    catastroRentas2PMER2 = unificarTitulos(catastroRentas2PMER2)
    
    unificacionTitulos = pd.concat([catastroRentas2PCLM1, catastroRentas2PCLM2, catastroRentas2PMER1, catastroRentas2PMER2])
    unificacionTitulos.reset_index(inplace=True, drop=True)
    return unificacionTitulos

def comparacionFromRentas(dfCatastro, dfRentas, getMercado):
    registrosRecuperados = pd.DataFrame(columns=dfRentas.columns)
    
    i=0
    while i<len(dfCatastro):
        registroCatastro = dfCatastro.iloc[i]
        for j in range(len(dfRentas)):
            registroRentas = dfRentas.iloc[j]
            if (registroCatastro["CEDULA"]==registroRentas["CEDULA"]):
                #print(registroCatastro)
                #print(registroRentas)
                #res = pd.merge(registroCatastro, registroRentas, left_on=["CEDULA"], right_on = ["CEDULA"])
                if (getMercado):
                    registroRentas["MERCADO"] = registroCatastro["MERCADO"]
                #registroRentas["PUESTO"] = registroCatastro["PUESTO"]
                registroRentas["VALOR"] = registroCatastro["VALOR"]
                
                registrosRecuperados = registrosRecuperados.append(registroRentas)
                #print(registrosRecuperados)
                
                #print(j)
                dfRentas = dfRentas.drop(j)
                
                dfCatastro = dfCatastro.drop(i)
                
                dfRentas.reset_index(drop=True, inplace=True)
                break
        i=i+1
    dfCatastro.reset_index(drop=True, inplace=True)
    return dfCatastro, dfRentas, registrosRecuperados
    
#==============================================================================================================================
#==============================================================================================================================
#==============================================================================================================================
#==============================================================================================================================
#==============================================================================================================================


# Se carga la blacklist: lista de registros cuyas cédulas no se encuentran registradas como contribuyentes
catastroNoEncontrado = pd.read_excel('./noContribuyentesCatastroTotal.xlsx', dtype={"CEDULA": str})

# No se considerará el nombresDF considerado en el anterior procesamiento porque su información ya se encuentra en los datos enviados en rentas
cedulasCatastro = pd.read_csv("./enviarCedulas.csv", dtype={"CEDULA": str})
cedulasCatastro["CEDULA"] = cedulasCatastro["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")

concejalesH3 = pd.read_excel('./PEDIDO DE CONCEJALES EXONERACIONES.xlsx', sheet_name="Hoja3", dtype={"CEDULA": str, "PUESTO": str}, skiprows=0)
concejalesH5 = pd.read_excel('./PEDIDO DE CONCEJALES EXONERACIONES.xlsx', sheet_name="Hoja5", dtype={"CEDULA": str}, skiprows=2) # Corresponde al mes de junio
registrosConcejales = [concejalesH3, concejalesH5]

#=============================== SE LIMPIA LOS ARCHIVOS DE EXONERACIONES ===========
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

# Los registros repetidos que tienen igual valor a descontar o número de puesto pueden deberse a los casos de cobros dobles, y por lo general, si se exonero uno se exoneran los 2
# En otros casos(Creo que solo en H3) son simples errores de que el técnico duplico los registros al escribirlos en la Hoja
registrosConcejalesProcesado[0] = registrosConcejalesProcesado[0].drop_duplicates(subset=["CEDULA", "MERCADO", "VALOR A DESCONTAR"])
registrosConcejalesProcesado[1] = registrosConcejalesProcesado[1].drop_duplicates(subset=["CEDULA", "MERCADO", "VALOR A DESCONTAR"])

# La Hoja5 corresponde a junio de 2020, los cuales, algunos ya están en la Hoja3 por lo que deben ser eliminados
# Algunos de estos registros corresponden a puestos con contratos vigentes y otros a contratos que se renovaron y tuvieron que ser cobrados como adicionales
tempHoja3 = registrosConcejalesProcesado[0][["CEDULA", "MERCADO"]]
tempHoja5 = registrosConcejalesProcesado[1][["CEDULA", "MERCADO", "VALOR A DESCONTAR"]]
registrosCombinados = pd.merge(tempHoja3, tempHoja5, left_on=["CEDULA","MERCADO"], right_on = ["CEDULA","MERCADO"])
registrosCombinados.rename(columns = {"VALOR A DESCONTAR":"JUNIO 50%"}, inplace = True)
# Los registros incorporados a la Hoja3 se borran de la Hoja5
registrosConcejalesProcesado[1] = registrosConcejalesProcesado[1].merge(registrosCombinados, how='left', indicator=True)
registrosConcejalesProcesado[1] = registrosConcejalesProcesado[1][registrosConcejalesProcesado[1]['_merge'] == 'left_only']
registrosConcejalesProcesado[1].drop('_merge', inplace=True, axis=1)
registrosConcejalesProcesado[1].reset_index(drop=True, inplace=True)
#tempHoja3 = tempHoja3.drop("JUNIO 50%", inplace=True, axis=1)
#columnasMerge = registrosConcejalesProcesado[0].columns.drop('JUNIO 50%')
#test = registrosConcejalesProcesado[0][columnasMerge].merge(registrosCombinados, 'left', indicator=True).set_axis(registrosConcejalesProcesado[0].index).fillna(registrosConcejalesProcesado[0])
# Incorporación de los datos, se queda con el dato más alto en el mes de junio
registrosConcejalesProcesado[0] = pd.merge(registrosConcejalesProcesado[0], registrosCombinados, how="outer", left_on=["CEDULA","MERCADO"], right_on = ["CEDULA","MERCADO"])
registrosConcejalesProcesado[0]["JUNIO 50%"] = registrosConcejalesProcesado[0][["JUNIO 50%_x", "JUNIO 50%_y"]].max(axis=1)
registrosConcejalesProcesado[0].drop(["JUNIO 50%_x", "JUNIO 50%_y"], inplace=True, axis=1)

## *********************************************************************************************************
## *******************# Cedulas provenientes del catastro con datos de titulos pendientes y pagado**********
## *********************************************************************************************************
# OJO en esta cédula: 010420774-1   Es la única repetida en la hoja5 que al parecer es por dos puestos
catastroRentas = pd.read_excel('./archivoRentas.xlsx', sheet_name="Concesion", dtype={"CEDULA_RUC": str}, skiprows=3)
catastroRentas.rename(columns = {"JULIO \n2020": "JULIO 2020", "CEDULA_RUC":"CEDULA", 'EXONERA MARZO\n 2020':'EXONERA MARZO 2020', 'EXONERA JULIO \n2020':'EXONERA JULIO 2020'}, inplace = True)
catastroRentas["CEDULA"] = catastroRentas["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")


catastroRentasExtra = pd.read_excel('./archivoRentas2.xlsx', sheet_name="Concesión", dtype={"CEDULA_RUC": str}, skiprows=4)
catastroRentasExtra.rename(columns = {"CEDULA_RUC":"CEDULA", "MARZO": "EXONERA MARZO 2020", "JULIO":'EXONERA JULIO 2020', "AGOSTO":'EXONERA AGOSTO 2020', "SEPTIEMBRE":'EXONERA SEPTIEMBRE 2020', "OCTUBRE":'EXONERA OCTUBRE 2020', "NOVIEMBRE":'EXONERA NOVIEMBRE 2020', "DICIEMBRE":'EXONERA DICIEMBRE 2020'}, inplace = True)
catastroRentasExtra["CEDULA"] = catastroRentasExtra["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")
catastroRentasExtra = catastroRentasExtra.replace(1, value="NO")
catastroRentasExtra = catastroRentasExtra.replace(2, value="SI")
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PAGADO") & (~catastroRentasExtra["EXONERA MARZO 2020"].isnull()), ["MARZO 2020"]] = "PAGADO"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PENDIENTE") & (~catastroRentasExtra["EXONERA MARZO 2020"].isnull()), ["MARZO 2020"]] = "PENDIENTE"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PAGADO") & (~catastroRentasExtra["EXONERA JULIO 2020"].isnull()), ["JULIO 2020"]] = "PAGADO"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PENDIENTE") & (~catastroRentasExtra["EXONERA JULIO 2020"].isnull()), ["JULIO 2020"]] = "PENDIENTE"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PAGADO") & (~catastroRentasExtra["EXONERA AGOSTO 2020"].isnull()), ["AGOSTO 2020"]] = "PAGADO"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PENDIENTE") & (~catastroRentasExtra["EXONERA AGOSTO 2020"].isnull()), ["AGOSTO 2020"]] = "PENDIENTE"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PAGADO") & (~catastroRentasExtra["EXONERA SEPTIEMBRE 2020"].isnull()), ["SEPTIEMBRE 2020"]] = "PAGADO"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PENDIENTE") & (~catastroRentasExtra["EXONERA SEPTIEMBRE 2020"].isnull()), ["SEPTIEMBRE 2020"]] = "PENDIENTE"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PAGADO") & (~catastroRentasExtra["EXONERA OCTUBRE 2020"].isnull()), ["OCTUBRE 2020"]] = "PAGADO"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PENDIENTE") & (~catastroRentasExtra["EXONERA OCTUBRE 2020"].isnull()), ["OCTUBRE 2020"]] = "PENDIENTE"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PAGADO") & (~catastroRentasExtra["EXONERA NOVIEMBRE 2020"].isnull()), ["NOVIEMBRE 2020"]] = "PAGADO"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PENDIENTE") & (~catastroRentasExtra["EXONERA NOVIEMBRE 2020"].isnull()), ["NOVIEMBRE 2020"]] = "PENDIENTE"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PAGADO") & (~catastroRentasExtra["EXONERA DICIEMBRE 2020"].isnull()), ["DICIEMBRE 2020"]] = "PAGADO"
catastroRentasExtra.loc[ (catastroRentasExtra["ESTADO"]=="PENDIENTE") & (~catastroRentasExtra["EXONERA DICIEMBRE 2020"].isnull()), ["DICIEMBRE 2020"]] = "PENDIENTE"

catastroRentas = pd.concat([catastroRentas, catastroRentasExtra])

# Se combina con los datos de la Hoja5 para complementar los datos, los registros sobrantes de la hoja5 pueden ser aquellos que se les cobró solo en junio y quizas luego expiró su contrato(y porqué no tienen nada en marzo?? Analizar)
tempHoja5 = registrosConcejalesProcesado[1][["CEDULA"]]
registrosCombinados = pd.merge(catastroRentas, tempHoja5, left_on=["CEDULA"], right_on = ["CEDULA"]) #inner
registrosCombinados['JUNIO 2021'] = "SOLICITADO"
registrosCombinados['EXONERA JUNIO 2021'] = "SI"
registrosCombinados = registrosCombinados[["CEDULA", 'JUNIO 2021', 'EXONERA JUNIO 2021']]

# Los registros incorporados a los registros de rentas se borran de la Hoja5
registrosConcejalesProcesado[1] = registrosConcejalesProcesado[1].merge(registrosCombinados, how='left', indicator=True)
registrosConcejalesProcesado[1] = registrosConcejalesProcesado[1][registrosConcejalesProcesado[1]['_merge'] == 'left_only']
registrosConcejalesProcesado[1].drop('_merge', inplace=True, axis=1)
registrosConcejalesProcesado[1].reset_index(drop=True, inplace=True)

# Incorporación de los datos en la hoja de rentas
catastroRentas = pd.merge(catastroRentas, registrosCombinados, how="outer", left_on=["CEDULA"], right_on = ["CEDULA"])

#Los registros sobrantes de la hoja5 pueden estar en la hoja de rentas de quienes tienen 2 puestos o no estan en el catastro actual pero se les exoneró solo en junio 2021(correspondiente a junio 2020)
hoja5NoCatastroActual = registrosConcejalesProcesado[1][~registrosConcejalesProcesado[1]["CEDULA"].isin(cedulasCatastro["CEDULA"])]
registrosConcejalesProcesado[1].drop(hoja5NoCatastroActual.index, inplace=True)
# Los registros de la hoja3 que ya no están en el catastro actual son de puestos con exoneraciones en varios meses
hoja3NoCatastroActual = registrosConcejalesProcesado[0][~registrosConcejalesProcesado[0]["CEDULA"].isin(cedulasCatastro["CEDULA"])]
registrosConcejalesProcesado[0].drop(hoja3NoCatastroActual.index, inplace=True)

## PROCESAR el archivo de rentas con 2 puestos
# OJO: 0103405767, 0104207741, tienen 2 puestos con iguales claves
# Por lo general se deben a los casos de cobros dobles por el problema del sistema de rentas
catastroRentas2P = pd.read_excel('./archivoRentas.xlsx', sheet_name="Datos Concesion mas de un local", dtype={"CED": str}, skiprows=1)
catastroRentas2P.rename(columns = {"CED":"CEDULA"}, inplace = True)
catastroRentas2P["CEDULA"] = catastroRentas2P["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")

rentas2P = procesarRentas2P(catastroRentas2P)
# Si se observa esta matriz, se verá que la mayoría de los pares de registros de un comerciante son iguales, se presume que esto es por lo cobros dobles
# En los casos que no, por lo general si se trata de un comerciante con 2 locales
# Existe también casos en el que el comerciante reclamó y se puso en orden esta situación, en este caso el par de registros no es igual

tempHoja5 = registrosConcejalesProcesado[1][["CEDULA"]]
registrosCombinados = pd.merge(rentas2P, tempHoja5, left_on=["CEDULA"], right_on = ["CEDULA"]) #inner
registrosCombinados['JUNIO'] = "SOLICITADO"
registrosCombinados['EXONERA JUNIO 2021'] = 1
registrosCombinados = registrosCombinados[["CEDULA", 'JUNIO', 'EXONERA JUNIO 2021']]
registrosCombinados.loc[ registrosCombinados["CEDULA"]=="010420774-1", ["EXONERA JUNIO 2021"]] = 2 # Porque este es la cedula con 2 registros diferentes en la hoja5
registrosCombinados.drop_duplicates(subset=["CEDULA"], inplace=True)

# Los registros Hoja5 incorporados a los registros de rentas se borran de la Hoja5
registrosConcejalesProcesado[1] = registrosConcejalesProcesado[1].merge(registrosCombinados, how='left', indicator=True)
registrosConcejalesProcesado[1] = registrosConcejalesProcesado[1][registrosConcejalesProcesado[1]['_merge'] == 'left_only']
registrosConcejalesProcesado[1].drop('_merge', inplace=True, axis=1)
registrosConcejalesProcesado[1].reset_index(drop=True, inplace=True)
# No deberían haber sobrantes aqui y efectivamente no los hay
# Incorporación de los datos en la hoja de rentas
rentas2P = pd.merge(rentas2P, registrosCombinados, how="outer", left_on=["CEDULA"], right_on = ["CEDULA"])
# IMPORTANTE: analizando esto se encontró que estos registros son posibles casos de cobros dobles.
###############################################################################################
catastroRentas["TITULOS_MARZO"] = catastroRentas[["MARZO 2020"]].count(axis=1)
catastroRentas["TITULOS_50"] = catastroRentas[["JUNIO 2021", "JULIO 2020", "AGOSTO 2020", "SEPTIEMBRE 2020", "OCTUBRE 2020", "NOVIEMBRE 2020", "DICIEMBRE 2020"]].count(axis=1)

catastroRentas["EXON_MARZO"] = catastroRentas.loc[catastroRentas['EXONERA MARZO 2020']=="SI", ["EXONERA MARZO 2020"]].count(axis=1)
catastroRentas["EXON_MARZO"] = catastroRentas["EXON_MARZO"].fillna(0)

catastroRentas =catastroRentas.replace(regex=[r'^SI$'], value=1)
catastroRentas =catastroRentas.replace(regex=[r'^NO$'], value=0)
catastroRentas["EXON_50"] = catastroRentas[['EXONERA JUNIO 2021', 'EXONERA JULIO 2020', 'EXONERA AGOSTO 2020', 'EXONERA SEPTIEMBRE 2020', 'EXONERA OCTUBRE 2020', 'EXONERA NOVIEMBRE 2020', 'EXONERA DICIEMBRE 2020']].sum(axis=1)
catastroRentas["EXON_MARZO"] = catastroRentas["EXON_MARZO"].fillna(0)
catastroRentas["IND_EXON"] = catastroRentas[['EXON_MARZO', "EXON_50"]].sum(axis=1) / catastroRentas[['TITULOS_MARZO', "TITULOS_50"]].sum(axis=1) #indice, de 0 a 1

#registrosCombinados.loc[ catastroRentas["MARZO 2020"]=="PENDIENTE" & catastroRentas["EXONERA MARZO 2020"]==0, ["PEND_NO_EXON"]] = 1
catastroRentas["PEND_NO_EXON_MARZO"] = ((catastroRentas["MARZO 2020"]=="PENDIENTE") & (catastroRentas["EXONERA MARZO 2020"]==0)).replace(True, value=1)
catastroRentas["PEND_NO_EXON_JULIO"] = ((catastroRentas["JULIO 2020"]=="PENDIENTE") & (catastroRentas["EXONERA JULIO 2020"]==0)).replace(True, value=1)
catastroRentas["PEND_NO_EXON_AGOSTO"] = ((catastroRentas["AGOSTO 2020"]=="PENDIENTE") & (catastroRentas["EXONERA AGOSTO 2020"]==0)).replace(True, value=1)
catastroRentas["PEND_NO_EXON_SEPTIEMBRE"] = ((catastroRentas["SEPTIEMBRE 2020"]=="PENDIENTE") & (catastroRentas["EXONERA SEPTIEMBRE 2020"]==0)).replace(True, value=1)
catastroRentas["PEND_NO_EXON_OCTUBRE"] = ((catastroRentas["OCTUBRE 2020"]=="PENDIENTE") & (catastroRentas["EXONERA OCTUBRE 2020"]==0)).replace(True, value=1)
catastroRentas["PEND_NO_EXON_NOVIEMBRE"] = ((catastroRentas["NOVIEMBRE 2020"]=="PENDIENTE") & (catastroRentas["EXONERA NOVIEMBRE 2020"]==0)).replace(True, value=1)
catastroRentas["PEND_NO_EXON_DICIEMBRE"] = ((catastroRentas["DICIEMBRE 2020"]=="PENDIENTE") & (catastroRentas["EXONERA DICIEMBRE 2020"]==0)).replace(True, value=1)
catastroRentas["PEND_NO_EXON"] = catastroRentas[["PEND_NO_EXON_MARZO", "PEND_NO_EXON_JULIO", "PEND_NO_EXON_AGOSTO", "PEND_NO_EXON_SEPTIEMBRE", "PEND_NO_EXON_OCTUBRE", "PEND_NO_EXON_NOVIEMBRE", "PEND_NO_EXON_DICIEMBRE"]].sum(axis=1)


##########################################################################################
################################PROCESADOS DE EXONERACIONES###############################
#Suestos: Para este punto ya no debería existir la Hoja5
#Se procesará el catastro con respecto a la hoja de exoneraciones y posteriormente con lo de rentas que está fusionado con lo de la hoja5
#Cuando se procese la hoja de rentas2P se debe eliminar por puesto


#Categorizar si canceló o no todos los títulos
#si tiene un puesto los titulos completos son 7, si tiene 2 son 14
# Esta cetegorización queda un tanto obsoleta al incorporar los indices
catastroRentas["NOTA_EXON"]="PARCIAL"
catastroRentas.loc[((catastroRentas["EXON_MARZO"]==0) & (catastroRentas["EXON_50"]==0)), ["NOTA_EXON"]] = "NO"
catastroRentas.loc[((catastroRentas["EXON_MARZO"]==catastroRentas["TITULOS_MARZO"]) & (catastroRentas["EXON_50"] == catastroRentas["TITULOS_50"])), ["NOTA_EXON"]] = "EXONERADO"

# ========================= PROCESADO DE ARCHIVOS DE CATASTRO  ==============================================
#============================================================================================================
#======================= PROCESADO DEL ARCHIVO CON CEDULAS CORREGIDAS ==============
resagosDF = pd.read_excel('./Hoja de cálculo sin título PV.xlsx', dtype={"CEDULA": str, "PUESTO": str}, skiprows=0) # parte del catastro
resagosDF = mercadosLib.limpiarMercado(resagosDF)
resagosDF = limpiarCatastro(resagosDF)

# ============== SE ELIMINAN CEDULAS QUE CUENTAN CON MÁS DE UN REGISTRO
# Estos registros deberían ser procesados aparte
#duplicadosResagos, resagosDF = handleDuplicados(resagosDF) # Ya que se está usando solo la hoja3 es posible procesar los duplicados

#===================== Se hacen las comparaciones con los archivos
registrosRecuperados, registrosConcejalesProcesado = getExonerados(resagosDF, registrosConcejalesProcesado)
#============================================================================================================
restantesCatastro = getRestantes(resagosDF, registrosRecuperados)

rentas2P = rentas2P.drop_duplicates() # Intenta eliminar los casos de cobros dobles ya que corresponden a un mismo puesto(Borra registro exactamente iguales)
rentas2P.reset_index(drop=True, inplace=True)
restantesCatastro, catastroRentas, registrosFromRentas1 = comparacionFromRentas(restantesCatastro, catastroRentas, True)
restantesCatastro, rentas2P, registrosFromRentas2 = comparacionFromRentas(restantesCatastro, rentas2P, True)

# Se asume que los registros que no se encontraronen rentas2P o catastroRentas no tenían puesto en el 2020
#todosLosRegistros = pd.concat([registrosRecuperados, registrosRestantes])
todosLosRegistrosCorregidos = pd.concat([registrosRecuperados, registrosFromRentas1, registrosFromRentas2, restantesCatastro])

#======================= PROCESADO DEL ARCHIVO CATASTRO MERCADOS PEQUEÑOS ==============
registrosMercadosProcesados = []
duplicadosMercados = []
for i in range(len(arrayMercados)):
#for i in range(26,27):
    df = pd.read_excel('./attachments/mercadospq.xlsx', sheet_name=arrayMercados[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(arrayMercados[i]["skip"]))
    #print(i)
    #print(arrayMercados[i]["nombre"])
    
    catastro = limpiarCatastro(df)
    
    catastro["MERCADO"] = arrayMercados[i]["nombre"]
    if (arrayMercados[i]["nombre"] == "MERCADO 12 ABRIL  FRUTAS TEMPOR"):
        catastro["MERCADO"] = "MERCADO 12 DE ABRIL" # Se puede tratar como un giro más del mercado 12 de abril
    
    #duplicados, catastro = handleDuplicados(catastro)
    
    registrosRecuperados, registrosConcejalesProcesado  = getExonerados(catastro, registrosConcejalesProcesado)
        
    ## Se obtienen los registros que no pasaron por el filtro
    restantesCatastro = getRestantes(catastro, registrosRecuperados)
    
    restantesCatastro, catastroRentas, registrosFromRentas1 = comparacionFromRentas(restantesCatastro, catastroRentas, False)
    restantesCatastro, rentas2P, registrosFromRentas2 = comparacionFromRentas(restantesCatastro, rentas2P, False)
    todosLosRegistrosMercados = pd.concat([registrosRecuperados, registrosFromRentas1, registrosFromRentas2, restantesCatastro])
    
    registrosMercadosProcesados.append(todosLosRegistrosMercados)
    #duplicadosMercados.append(duplicados)
    
#======================= PROCESADO DEL ARCHIVO CATASTRO ARENAL ==============

registrosArenalProcesados = []
duplicadosArenal = []
for i in range(len(arrayArenal)):
#for i in range(26,27):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=arrayArenal[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(arrayArenal[i]["skip"]))
    #print(i)
    #print(arrayArenal[i]["nombre"])
    
    catastro = limpiarCatastro(df)
    catastro["MERCADO"] = "EL ARENAL"
    
    #duplicados, catastro = handleDuplicados(catastro)
    
    registrosRecuperados, registrosConcejalesProcesado = getExonerados(catastro, registrosConcejalesProcesado)
    
    restantesCatastro = getRestantes(catastro, registrosRecuperados)
    
    restantesCatastro, catastroRentas, registrosFromRentas1 = comparacionFromRentas(restantesCatastro, catastroRentas, False)
    restantesCatastro, rentas2P, registrosFromRentas2 = comparacionFromRentas(restantesCatastro, rentas2P, False)
    todosLosRegistrosArenal = pd.concat([registrosRecuperados, registrosFromRentas1, registrosFromRentas2, restantesCatastro])
    
    registrosArenalProcesados.append(todosLosRegistrosArenal)
    #duplicadosArenal.append(duplicados)
    

dfGuadalupe = pd.DataFrame()
for i in range(len(unificarGuadalupe)):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=unificarGuadalupe[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(unificarGuadalupe[i]["skip"]))
      
    catastro = limpiarCatastro(df)
    dfGuadalupe = pd.concat([dfGuadalupe, catastro])

dfGuadalupe.reset_index(drop=True, inplace=True)
dfGuadalupe["MERCADO"] = "EL ARENAL"
dfGuadalupe.drop_duplicates(inplace=True)
#duplicadosGuadalupe, dfGuadalupe = handleDuplicados(dfGuadalupe)

registrosRecuperados, registrosConcejalesProcesado = getExonerados(dfGuadalupe, registrosConcejalesProcesado)

restantesCatastro = getRestantes(dfGuadalupe, registrosRecuperados)

restantesCatastro, catastroRentas, registrosFromRentas1 = comparacionFromRentas(restantesCatastro, catastroRentas, False)
restantesCatastro, rentas2P, registrosFromRentas2 = comparacionFromRentas(restantesCatastro, rentas2P, False)
todosLosRegistrosGuadalupe = pd.concat([registrosRecuperados, registrosFromRentas1, registrosFromRentas2, restantesCatastro])
todosLosRegistrosGuadalupe.drop_duplicates(inplace=True)

##################################################################################################################


#========================================================================================================================
#========================================================================================================================
#=============================================== ESTADÍSTICAS ===========================================================
#========================================================================================================================
#========================================================================================================================
#=========== Se procesa cada Dataframe
# Se eliminan los registros que no tienen indice de exoneración puesto que son quienes no tienen titulos registrados en las fechas de interés
todosLosRegistrosCorregidosCat = todosLosRegistrosCorregidos[~todosLosRegistrosCorregidos["IND_EXON"].isnull()]
mercadosDistintos = todosLosRegistrosCorregidosCat["MERCADO"].drop_duplicates(inplace=False)

resumen = pd.DataFrame(columns=["MERCADO", "INDICES"])
for mercado in mercadosDistintos:
    stats = getStats(todosLosRegistrosCorregidosCat, mercado, True)
    resumen = pd.concat([resumen, stats])

for idx, mercadosDF in enumerate(registrosMercadosProcesados):
    mercadosDFCat = mercadosDF[~mercadosDF["IND_EXON"].isnull()]
    nombre = arrayMercados[idx]["nombre"]
    if (nombre == "MERCADO 12 ABRIL  FRUTAS TEMPOR"):
        nombre = "MERCADO 12 DE ABRIL" # Se puede tratar como un giro más del mercado 12 de abril
    stats = getStats(mercadosDFCat, nombre, False)
    resumen = pd.concat([resumen, stats])
    
for arenalDF in registrosArenalProcesados:
    arenalDFCat = arenalDF[~arenalDF["IND_EXON"].isnull()]
    stats = getStats(arenalDFCat, "EL ARENAL", False)
    resumen = pd.concat([resumen, stats])

todosLosRegistrosGuadalupeCat = todosLosRegistrosGuadalupe[~todosLosRegistrosGuadalupe["IND_EXON"].isnull()]
stats = getStats(todosLosRegistrosGuadalupeCat, "EL ARENAL", False)
resumen = pd.concat([resumen, stats])

#=============================================================
# Se obtienen estadísticas
resumenTabulado = resumen.groupby(resumen['MERCADO']).aggregate(MERCADO=('MERCADO', 'first'), noExon=('0', 'sum'), hasta25=('0-25', 'sum'), hasta50=('25-50', 'sum'), hasta75=('50-75', 'sum'), hasta100=('75-100', 'sum'), exon=('100', 'sum'))
  
totalNoExonerados = resumenTabulado['noExon'].sum()
totalHasta25 = resumenTabulado['hasta25'].sum()
totalHasta50 = resumenTabulado['hasta50'].sum()
totalHasta75 = resumenTabulado['hasta75'].sum()
totalHasta100 = resumenTabulado['hasta100'].sum()
totalExonerados = resumenTabulado['exon'].sum()


#fig = plt.figure(figsize = (10, 5))
pieExonerados("Cantidad de Puestos Exonerados", [totalNoExonerados, totalHasta25, totalHasta50, totalHasta75, totalHasta100, totalExonerados])

plt=reload(plt)# Para arreglar problemas con los charts
fig = plt.figure()
ax = fig.add_axes([1,1,1.5,0.75])
labels = ['NO_EXONERADOS', "(0-25)%", "(25-50)%", "(50-75)%", "(75-100)%", 'EXONERADOS']
cantidad = [totalNoExonerados, totalHasta25, totalHasta50, totalHasta75, totalHasta100, totalExonerados]
plt.xlabel("Porcentaje")
plt.ylabel("Puestos")
plt.title("Todos Los Mercados")
ax.bar(labels,cantidad)
#ax.title('Todos Los Mercados')
plt.show()



#Puestos procesados por mercado
ax = resumenTabulado.plot.bar(x='MERCADO', y='exon', rot=90)
plt.show()

ax = resumenTabulado.plot.bar(x='MERCADO', y='noExon', rot=90)
plt.show()

ax = resumenTabulado.plot.bar(x='MERCADO', y='hasta25', rot=90)
plt.show()

ax = resumenTabulado.plot.bar(x='MERCADO', y='hasta50', rot=90)
plt.show()

ax = resumenTabulado.plot.bar(x='MERCADO', y='hasta75', rot=90)
plt.show()

ax = resumenTabulado.plot.bar(x='MERCADO', y='hasta100', rot=90)
plt.show()

resumenTabulado.reset_index(drop=True, inplace=True)
for row in range(len(resumenTabulado)):
    registro = resumenTabulado.iloc[row]
    fig = plt.figure()
    ax = fig.add_axes([1,1,1.5,0.75])
    totalNoExonerados = registro["noExon"]
    totalHasta25 = registro["hasta25"]
    totalHasta50 = registro["hasta50"]
    totalHasta75 = registro["hasta75"]
    totalHasta100 = registro["hasta100"] 
    totalExonerados = registro["exon"]
    labels = ['NO_EXONERADOS', "(0-25)%", "(25-50)%", "(50-75)%", "(75-100)%", 'EXONERADOS']
    cantidad = [totalNoExonerados, totalHasta25, totalHasta50, totalHasta75, totalHasta100, totalExonerados]
    plt.xlabel("Porcentaje")
    plt.ylabel("Puestos")
    plt.title(registro["MERCADO"])
    ax.bar(labels,cantidad)
    plt.show()


# De los puestos que no fueron encontrados en la hoja de exoneraciones se obtienen los títulos no exonerados que aún están pendientes de pago
# El valor de 0 es para no exonerados
pendientesNoExon = 0
todosLosRegistrosCorregidosCat = todosLosRegistrosCorregidos[~todosLosRegistrosCorregidos["CLAVE"].isnull()]
pendientesNoExon = pendientesNoExon + todosLosRegistrosCorregidosCat["PEND_NO_EXON"].sum()

for idx, mercadosDF in enumerate(registrosMercadosProcesados):
    mercadosDFCat = mercadosDF[~mercadosDF["CLAVE"].isnull()]
    pendientesNoExon = pendientesNoExon + mercadosDFCat["PEND_NO_EXON"].sum()
    
for arenalDF in registrosArenalProcesados:
    arenalDFCat = arenalDF[~arenalDF["CLAVE"].isnull()]
    pendientesNoExon = pendientesNoExon + arenalDFCat["PEND_NO_EXON"].sum()

todosLosRegistrosGuadalupeCat = todosLosRegistrosGuadalupe[~todosLosRegistrosGuadalupe["CLAVE"].isnull()]
pendientesNoExon = pendientesNoExon + todosLosRegistrosGuadalupeCat["PEND_NO_EXON"].sum()



print("Existen: " + str(pendientesNoExon) + " Títulos pendientes no exonerados")

resumenTabulado[['EXONERA JUNIO 2021']].sum(axis=1)

resumenTabulado["TOTAL"] = resumenTabulado[["noExon", "hasta25", "hasta50", "hasta75", "hasta100", "exon"]].sum(axis=1)
resumenTabulado["TOTAL"].sum()