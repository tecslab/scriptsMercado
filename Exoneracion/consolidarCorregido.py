#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 08:36:49 2022

@author: pablov
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

arrayMercados = [
                 {"nombre": "CENTRO COMERCIAL 9 DE OCTUBRE" },
                 {"nombre": "MERCADO 27 DE FEBRERO"}, 
                 {"nombre": "MERCADO 12 ABRIL  FRUTAS TEMPOR"}, 
                 {"nombre": "PLATAFORMA 27 DE FEBRERO"}, 
                 {"nombre": "MERCADO 9 DE OCTUBRE"},
                 {"nombre": "MERCADO 10 DE AGOSTO"},   #OJO, tiene tabla resumen al final
                 {"nombre": "MERCADO 3 DE NOVIEMBRE"},
                 {"nombre": "MERCADO 12 DE ABRIL"},
                 {"nombre": "PLATAFORMA MIRAFLORES"}, # oko, tiene nota al final
                 {"nombre": "PLATAFORMA PATAMARCA"},
                 {"nombre": "PLATAFORMA NARANCAY"},
                 {"nombre": "PLATAFORMA CEBOLLAR"},
                 {"nombre": "PLAZA FLORES"},
                 {"nombre": "PLAZA ROTARY"},
                 {"nombre": "PLAZA SAN FRANCISCO"},
                 {"nombre": "PLAZA SANTA ANA"},
                 {"nombre": "PLATAFORMA QUINTA CHICA"},
                 {"nombre": "RECINTO FERIAL"}
              ]

arrayArenal = [
                 {"nombre": "CENTRO COMERCIAL"},
                 {"nombre": "JESUS DEL GRAN PODER "},
                 {"nombre": "PLATAFORMA EXTERIOR 4 REINA DE "},
                 {"nombre": "SECTOR JUNTO A LAS NAVES DEL CE"},
                 {"nombre": "PRODUCTOS PERECIBLES, NAVES 4"},
                 {"nombre": "PLATAFORMA EXTERIOR No. 4    AS"},
                 {"nombre": "PLATAFORMA No. 4 ASOCIACION BEL"},
                 {"nombre": "PLATAFORMA No. 4 ASOCIACION VAL"},
                 {"nombre": "PLATAFORMA 4 (HIERBAS Y ALFAFA)"},
                 {"nombre": "ASOCIACIÓN 29 DE JULIO "},
                 {"nombre": "FRENTE AL RECINTO FERIAL (BETUN"},
                 {"nombre": "PASO PEATONAL DEL ARENAL"},
                 {"nombre": "PLATAFORMANO. 2. COOPERATIVA PR"},
                 {"nombre": "PLATAFORMANO. 2. COOPERATIVA CO"},
                 {"nombre": "ASOC REINA DE GUADALUPE"},
                 {"nombre": "PLATAFORMA No. 9 ASOCIACION ABD"},
                 
                 {"nombre": "PLATAFORMA EXTERIOR No.2ASO"},  ## Habían dos tablas en esta hoja
                 {"nombre": "PLATAFORMA EXTERIOR No.2UNI"},  ## FOrmato extraño
                 
                 {"nombre": "PLATAFORMA EXTERIOR 2-3-4-9"},
                 {"nombre": "ASC HUMANITARIA"},
                 {"nombre": "PLATAFORMA NO. 3. COOPERATIVA S"},
                 {"nombre": "PLATAFORMA No. 4 ASOCIACION SAN"},
                 {"nombre": "ASO. 8 DE MARZO"},
                 
                 {"nombre": "ASO. 10 DE AGOSTO"},      ## FOrmato extraño                 
                 
                 {"nombre": "ASO. LUCHA LIBRE"},
                 {"nombre": "ASO. SEÑOR ANDACOCHA"},
                 {"nombre": "ASOC.SANTA ANA"}
              ]

def separarExonerados(registros):
    #Separa en Exonerados y no Exonerados
    emptyDF = pd.DataFrame(columns=["MONTO_EXONERADO", "EXON_MARZO"]) # para asegurarnos que las columnas existan
    registros = pd.concat([registros, emptyDF])
    
    exoneradosByValor = registros[~registros["VALOR A DESCONTAR"].isnull()]

    noEncontrados = registros.drop(exoneradosByValor.index)
    exoneradosByCEL = noEncontrados[~noEncontrados["MONTO_EXONERADO"].isnull()]
    
    # if (not "EXON_MARZO" in exoneradosByCEL):
    #     exoneradosByCEL["EXON_MARZO"]=None
        
    exoneradosByCEL = exoneradosByCEL[(exoneradosByCEL["MONTO_EXONERADO"]>0) | (("EXON_MARZO" in exoneradosByCEL) & (~exoneradosByCEL["EXON_MARZO"].isnull()) & (exoneradosByCEL["EXON_MARZO"]>0))]
    noExonerados = noEncontrados.drop(exoneradosByCEL.index)

    exoneradosByCEL.loc[ exoneradosByCEL["EXON_MARZO"].isnull() , ["EXON_MARZO"]] = 0

    exoneradosByCEL["VALOR A DESCONTAR"] = exoneradosByCEL["EXON_MARZO"] + exoneradosByCEL["MONTO_EXONERADO"]

    exonerados = pd.concat([exoneradosByValor, exoneradosByCEL])
    
    encontradosByNombre = exoneradosByValor[exoneradosByValor["CEDULA"].isnull()]["REGISTROS_SUMADOS"].sum()
    encontradosByCedula = exoneradosByValor[~exoneradosByValor["CEDULA"].isnull()]["REGISTROS_SUMADOS"].sum()
    
    return [exonerados, noExonerados, encontradosByNombre, encontradosByCedula]

def getStats(exonerados, noExonerados, mercado, separarMercado):
    # Obtiene estadísticas por mercado
    if (separarMercado):
        exoneradosMercado = exonerados[exonerados["MERCADO"]==mercado]["VALOR A DESCONTAR"].count()
        noExoneradosMercado = noExonerados[noExonerados["MERCADO"]==mercado]["CEDULA"].count()
        montoExoneracion = exonerados[exonerados["MERCADO"]==mercado]["VALOR A DESCONTAR"].sum()
    else:
        exoneradosMercado = exonerados["VALOR A DESCONTAR"].count()
        noExoneradosMercado = noExonerados["CEDULA"].count()
        montoExoneracion = exonerados["VALOR A DESCONTAR"].sum()
    stats = {'MERCADO': mercado, 'EXONERADOS': exoneradosMercado, 'NO_EXONERADOS': noExoneradosMercado, "MONTO_EXONERACION": montoExoneracion}
    # Es necesario redondear los resultados de dinero desde el inicio
    #stats = {'MERCADO': mercado, 'EXONERADOS': exoneradosMercado, 'NO_EXONERADOS': noExoneradosMercado, "MONTO_EXONERACION": "%.2f" % montoExoneracion}
    return stats


procesadosCorregidos = pd.read_excel('./procesadosCorregidos.xlsx', dtype={"CEDULA": str}, skiprows=0)

encontradosFiles1y2 = 0
encontradosFile3 = 0

[exonerados, noExonerados, encontradosByNombre, encontradosByCedula] = separarExonerados(procesadosCorregidos)

encontradosFile3 = encontradosByNombre
encontradosFiles1y2 = encontradosByCedula

mercadosDistintos = procesadosCorregidos["MERCADO"].drop_duplicates(inplace=False)

#=========== ESTADISTICAS

resumen = pd.DataFrame(columns=["MERCADO", "EXONERADOS", "NO_EXONERADOS", "MONTO_EXONERACION"])

for mercado in mercadosDistintos:
    stats = getStats(exonerados, noExonerados, mercado, True)
    resumen = resumen.append(stats, ignore_index = True)
    

for i in range(len(arrayMercados)):
    df = pd.read_excel('./procesadosMercados.xlsx', sheet_name=arrayMercados[i]["nombre"], dtype={"CEDULA": str}, skiprows=0)
    [exonerados, noExonerados, encontradosByNombre, encontradosByCedula] = separarExonerados(df)
    encontradosFile3 += encontradosByNombre
    encontradosFiles1y2 += encontradosByCedula
    stats = getStats(exonerados, noExonerados, arrayMercados[i]["nombre"], False)
    resumen = resumen.append(stats, ignore_index = True)
    
for i in range(len(arrayArenal)):
    df = pd.read_excel('./procesadosArenal.xlsx', sheet_name=arrayArenal[i]["nombre"], dtype={"CEDULA": str}, skiprows=0)
    [exonerados, noExonerados, encontradosByNombre, encontradosByCedula] = separarExonerados(df)
    encontradosFile3 += encontradosByNombre
    encontradosFiles1y2 += encontradosByCedula
    stats = getStats(exonerados, noExonerados, "EL ARENAL", False)
    resumen = resumen.append(stats, ignore_index = True)
    

resumen = resumen.groupby(resumen['MERCADO']).aggregate(MERCADO=('MERCADO', 'first'), EXONERADOS=('EXONERADOS', 'sum'), NO_EXONERADOS=("NO_EXONERADOS", "sum"), MONTO_EXONERACION=("MONTO_EXONERACION", "sum"))

totalExonerados = resumen['EXONERADOS'].sum()
totalNoExonerados = resumen['NO_EXONERADOS'].sum()
montoTotal = resumen["MONTO_EXONERACION"].sum()


def func(pct, allvals):
    absolute = int(np.round(pct/100.*np.sum(allvals)))
    return "{:1.1f}%\n{:d}".format(pct, absolute)

labels = 'EXONERADOS', 'NO_EXONERADOS'
sizes = [totalExonerados, totalNoExonerados]
explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct=lambda pct: func(pct, sizes),
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax1.set_title("Catastro Total")

plt.show()