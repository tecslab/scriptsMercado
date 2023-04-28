#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 15:20:41 2022

@author: pablov
"""

import pandas as pd
import mercadosLib
import matplotlib.pyplot as plt
import requests
import json
import numpy as np

consultarContribuyentes = True

arrayArenal = [
                 {"nombre": "CENTRO COMERCIAL", "skip": "0", },
                 {"nombre": "JESUS DEL GRAN PODER ", "skip": "0",},
                 #{"nombre": "PLATAFORMA EXTERIOR 4 REINA DE ", "skip": "4",},  #Unificar con "ASOC REINA DE GUADALUPE"
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
                 
                 #{"nombre": "PLATAFORMA EXTERIOR 2-3-4-9", "skip": "4",},
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

arrayMercados = [
                 {"nombre": "CENTRO COMERCIAL 9 DE OCTUBRE", "skip": "3", },
                 {"nombre": "MERCADO 27 DE FEBRERO", "skip": "2",}, #OJO
                 {"nombre": "MERCADO 12 ABRIL  FRUTAS TEMPOR", "skip": "3",}, #OJO
                 {"nombre": "PLATAFORMA 27 DE FEBRERO", "skip": "2",}, #OJO                
                 {"nombre": "MERCADO 9 DE OCTUBRE", "skip": "0",},
                 {"nombre": "MERCADO 10 DE AGOSTO", "skip": "3",},
                 {"nombre": "MERCADO 3 DE NOVIEMBRE", "skip": "0",},
                 {"nombre": "MERCADO 12 DE ABRIL", "skip": "2",}, #OJO
                 {"nombre": "PLATAFORMA MIRAFLORES", "skip": "1",},
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


docs = [arrayArenal, arrayMercados]
docsNames = ["arenal", "mercadospq"]

###### Crea excels vacíos para que puedan ser editados sin problemas ############
emptyDF = pd.DataFrame()
emptyDF.to_excel('./cedulas9D0.xlsx')
emptyDF.to_excel('./cedulas9D1.xlsx')
#################################################
catastroDetalle = pd.DataFrame(columns=["MERCADO", "TOTAL_COMERCIANTES", "DUPLICADOS"])
catastrosByDoc = [pd.DataFrame(), pd.DataFrame()]

totalCatastroConcesiones = pd.DataFrame()
for idx, doc in enumerate(docs):
    for i in range(len(doc)):
    #for i in range(26,27):
    #for i in range(2,3):
        df = pd.read_excel('./attachments/' + str(docsNames[idx]) + '.xlsx', sheet_name=doc[i]["nombre"], dtype={"CEDULA": str}, skiprows=int(doc[i]["skip"]))
        print(doc[i]["nombre"])
        
        catastro = mercadosLib.limpiarCedula(df)
        catastro = mercadosLib.limpiarContratoConcesiones(catastro)
        #Se agrega al catastro correspondiente
        catastrosByDoc[idx] = pd.concat([catastrosByDoc[idx], catastro])
        
        
        conDuplicados = len(catastro)
        catastro = catastro.drop_duplicates(subset=["CEDULA"], inplace=False)
        
        totalComerciantes = catastro["CEDULA"].count()
        totalDuplicados = conDuplicados - totalComerciantes
        nombreMercado = doc[i]["nombre"]
        nombreSector = "Indefinido"
        if (docsNames[idx]=="arenal"):
            nombreMercado = "EL ARENAL"
            nombreSector = doc[i]["nombre"]
                
        resumenSector = {'MERCADO': nombreMercado, 'TOTAL_COMERCIANTES': [totalComerciantes], 'DUPLICADOS': [totalDuplicados], "SECTOR": nombreSector}
        resumenSector = pd.DataFrame(resumenSector)
        catastroDetalle = pd.concat([catastroDetalle, resumenSector])
        #Se agrega al catastro general
        totalCatastroConcesiones = pd.concat([totalCatastroConcesiones, catastro])
                
        # with pd.ExcelWriter('./cedulas9D' + str(idx) + '.xlsx', mode='a', engine="openpyxl") as writer:  
        #     cedulasMenosDigitos.to_excel(writer, sheet_name=doc[i]["nombre"])


dfGuadalupe = pd.DataFrame()
for i in range(len(unificarGuadalupe)):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=unificarGuadalupe[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(unificarGuadalupe[i]["skip"]))
      
    catastro = mercadosLib.limpiarCedula(df)
    catastro = mercadosLib.limpiarContratoConcesiones(catastro)
    catastro = mercadosLib.limpiarPuestos(catastro)
    catastro = mercadosLib.limpiarNombres(catastro)
    dfGuadalupe = pd.concat([dfGuadalupe, catastro])

dfGuadalupe = dfGuadalupe.drop_duplicates(subset=["CEDULA", "PUESTO"], inplace=False)
catastrosByDoc[0] = pd.concat([catastrosByDoc[0], dfGuadalupe])

conDuplicados = len(dfGuadalupe)
dfGuadalupe = dfGuadalupe.drop_duplicates(subset=["CEDULA"], inplace=False)
totalComerciantes = dfGuadalupe["CEDULA"].count()
totalDuplicados = conDuplicados - totalComerciantes

nombreMercado = "EL ARENAL"
nombreSector = "ASOC REINA DE GUADALUPE"


resumenSector = {'MERCADO': nombreMercado, 'TOTAL_COMERCIANTES': [totalComerciantes], 'DUPLICADOS': [totalDuplicados], "SECTOR": nombreSector}
resumenSector = pd.DataFrame(resumenSector)
catastroDetalle = pd.concat([catastroDetalle, resumenSector])
#Se agrega al catastro general
totalCatastroConcesiones = pd.concat([totalCatastroConcesiones, dfGuadalupe])




dfGuadalupe = dfGuadalupe.sort_values('NOMBRES')





df = pd.read_excel('./Hoja de cálculo sin título PV.xlsx', dtype={"CEDULA": str}, skiprows=0)

catastro = mercadosLib.limpiarCedula(df)
catastro = mercadosLib.limpiarContratoConcesiones(catastro)
catastro = mercadosLib.limpiarMercado(catastro)
mercadosDistintos = catastro["MERCADO"].drop_duplicates(inplace=False)
#=========== Se procesa cada Dataframe

for mercado in mercadosDistintos:
    registrosMercado = catastro[catastro["MERCADO"]==mercado]
    if (mercado=="EL ARENAL"):
        catastrosByDoc[0] = pd.concat([catastrosByDoc[0], registrosMercado])
    else:
        catastrosByDoc[1] = pd.concat([catastrosByDoc[1], registrosMercado])
    
    conDuplicados = len(registrosMercado)
    registrosMercado = registrosMercado.drop_duplicates(subset=["CEDULA"], inplace=False)
    totalDuplicados = conDuplicados - len(registrosMercado)
    totalComerciantes = registrosMercado["CEDULA"].count()
    resumenSector = {'MERCADO': mercado, 'TOTAL_COMERCIANTES': [totalComerciantes], 'DUPLICADOS': [totalDuplicados], "SECTOR": "Indefinido"}
    resumenSector = pd.DataFrame(resumenSector)
    catastroDetalle = pd.concat([catastroDetalle, resumenSector])
    
tabulado = catastroDetalle.groupby(catastroDetalle['MERCADO']).aggregate(MERCADO=('MERCADO', 'first'), TOTAL_COMERCIANTES=('TOTAL_COMERCIANTES', 'sum'), DUPLICADOS=('DUPLICADOS', 'sum'))
totalTabulado = tabulado["TOTAL_COMERCIANTES"].sum()
duplicadosTabulados =  tabulado["DUPLICADOS"].sum()


    
#catastro = catastro.sort_values('NOMBRES') # Ordena alfabéticamente
totalCatastroConcesiones = pd.concat([totalCatastroConcesiones, catastro])
totalCatastroConcesiones=totalCatastroConcesiones.drop_duplicates(subset=["CEDULA"], inplace=False)
#totalCatastroConcesiones.to_excel("./totalCatastroConcesiones.xlsx")
#totalCatastroConcesiones["CEDULA"].to_csv('out.zip', index=False)


duplicadosTotales = []
puestosCatastro = []
for bloqueCatastro in catastrosByDoc:
    conDuplicados = len(bloqueCatastro)
    puestosCatastro.append(conDuplicados)
    bloqueCatastro = bloqueCatastro.drop_duplicates(subset=["CEDULA"], inplace=False)
    totalDuplicados = conDuplicados - len(bloqueCatastro)  #277, 50
    duplicadosTotales.append(totalDuplicados)






fig = plt.figure()
ax = fig.add_axes([0,0,1,0.5])
labels = ['Total Comerciantes', "Total Puestos Catastro", 'Total Puestos Procesados']
cantidad = [len(totalCatastroConcesiones), sum(puestosCatastro), totalTabulado - duplicadosTabulados ]
ax.barh(labels,cantidad)
plt.show()

#Puestos procesados por mercado
ax = tabulado.plot.bar(x='MERCADO', y='TOTAL_COMERCIANTES', rot=90)
plt.show()

#Comerciantes con más de un puesto en un mismo sector/Mercado
ax = tabulado.plot.bar(x='MERCADO', y='DUPLICADOS', rot=90)
plt.show()

#Comerciantes con más de un puesto en el Arenal
print("Comerciantes con más de un puesto en el Arenal: " + str(duplicadosTotales[0]))
print("Comerciantes con más de un puesto en diferentes Mercados (No incluye El Arenal): " + str(duplicadosTotales[1]))



# Los siguientes mercados tienen conflictos con los nombres de puestos
#Mercado 3 de noviembre
#plataforma narancay
#estacion de tranferencia - Aso. 29 de julio#


# Probar limpiando puestos













verificarCedulas = totalCatastroConcesiones["CEDULA"].replace(regex=r'-', value="")
catastroNuevo = pd.DataFrame()
for cedula in verificarCedulas:
    contribuyentes_URL = "https://enlinea.cuenca.gob.ec/BackendConsultas/api/contribuyente/userinfo/" + cedula
    contribuyentesRequest = requests.get(contribuyentes_URL)
    data = contribuyentesRequest.text        
    
    mensajeCEL = ""
    nombreContribuyente = None
    if (data=="No encontrado!"):
        mensajeCEL = "No Encontrado" #CEL: Cuenca en línea
    else:    
        resultadosContribuyente = json.loads(data)
        
        if (resultadosContribuyente["Nombre"]=="Contribuyente No Registrado. Verifique si posee Infracciones"):
            mensajeCEL = "No Encontrado"
        else:
            nombreContribuyente = resultadosContribuyente["Nombre"]
    
    actualizarInfo = {"CEDULA": [cedula], "NOMBRES": [nombreContribuyente], "NOTA": [mensajeCEL]}
    actualizarInfo = pd.DataFrame(actualizarInfo)
    catastroNuevo = pd.concat([catastroNuevo, actualizarInfo])

# El regex r'.{0}(?=.{1}$)' se puede leer como: si hay un caracter antes de terminar, seleccionar el espacio antes de este
catastroNuevo["CEDULA"] = catastroNuevo["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")
catastroNoEncontrado = catastroNuevo[catastroNuevo["NOMBRES"].isnull()]
catastroNoEncontrado =  totalCatastroConcesiones[totalCatastroConcesiones["CEDULA"].isin(catastroNoEncontrado["CEDULA"])]
catastroNoEncontrado = catastroNoEncontrado[["CEDULA", "NOMBRES", "PUESTO", "TIPO CONTRATO", "OBSERVACIONES"]]
catastroNoEncontrado.to_excel("./noContribuyentes.xlsx")







catastroCorrecto = catastroNuevo[~catastroNuevo["NOMBRES"].isnull()]



cantItems = "200"
catastroCorrecto = catastroCorrecto.reset_index(drop=True)
catastroCorrecto["CEDULA"] = catastroCorrecto["CEDULA"].replace(regex=r'-', value="")
for idx, cedula in enumerate(catastroCorrecto["CEDULA"]):
    cancelados_URL = "https://enlinea.cuenca.gob.ec/BackendConsultas/api/contribuyente/" + cedula + "/titulos/cancelados?page=1&nitems=" + cantItems
    canceladosRequest = requests.get(cancelados_URL)
    data = canceladosRequest.text        
    
    if (data=="No encontrado!"):
        catastroCorrecto.loc[idx, "NOTA_CEL"] = "No Encontrado" #CEL: Cuenca en línea
        continue        
    
    resultadosCancelados = json.loads(data)
    
    if ("tipo" in resultadosCancelados):
        catastroCorrecto.loc[idx, "NOTA_CEL"] = "No Encontrado"
        continue
    
    if (len(resultadosCancelados)==cantItems):
        print ("ADVERTENCIA: Pueden existir más registros que los obtenidos aqui")

    titulosMarzo = 0
    exoneradosMarzo = 0
    montoExoMarzo = 0
    montoNoExoMarzo = 0
    
    titulosExo50 = 0
    exonerado50 = 0
    montoExo50 = 0
    montoNoExo50 = 0
    for item in resultadosCancelados:
        if ((item["PRE_CLAVE"][0:3]=="MER") | (item["PRE_CLAVE"][0:3]=="CLM")):
            añoEmision = item["TIC_FECHA_EMISION"][7:]
            if (añoEmision == "20"):
                mesEmision = item["TIC_FECHA_EMISION"][3:6]
                #Pueden haber mas de un titulo por mes si se tiene más de un puesto
                if (mesEmision=="MAR"):
                    titulosMarzo +=1
                    if (float(item["TIP_MONTO_EXONERACION"])>0):
                        exoneradosMarzo +=1
                        montoExoMarzo += float(item["TIP_MONTO_EXONERACION"])
                    else:
                        montoNoExoMarzo += float(item["TIP_MONTO_EXONERACION"])
                ##Mayo y abril no se emitieron títulos
                if ((mesEmision=="JUL") | (mesEmision=="AUG") | (mesEmision=="SEP") | (mesEmision=="OCT") | (mesEmision=="NOV") | (mesEmision=="DEC")):
                    titulosExo50 +=1
                    if (float(item["TIP_MONTO_EXONERACION"])>0):
                        exonerado50 +=1
                        montoExo50 += float(item["TIP_MONTO_EXONERACION"])
                    else:
                        montoNoExo50 += float(item["TIC_VALOR"])
    
    catastroCorrecto.loc[idx, "TITULOS_MARZO"] = titulosMarzo
    catastroCorrecto.loc[idx, "EXON_MARZO"] = exoneradosMarzo
    catastroCorrecto.loc[idx, "NOEXON_MARZO"] = titulosMarzo - exoneradosMarzo
    catastroCorrecto.loc[idx, "MONTO_EXON_MARZO"] = montoExoMarzo
    catastroCorrecto.loc[idx, "MONTO_NOEXON_MARZO"] = montoNoExoMarzo
    
    catastroCorrecto.loc[idx, "TITULOS_50"] = titulosExo50
    catastroCorrecto.loc[idx, "EXON_50"] = exonerado50
    catastroCorrecto.loc[idx, "NOEXON_50"] = titulosExo50 - exonerado50
    catastroCorrecto.loc[idx, "MONTO_EXON_50"] = montoExo50
    catastroCorrecto.loc[idx, "MONTO_NOEXON_50"] = montoNoExo50
    

totalTitulosEmitidos = catastroCorrecto["TITULOS_MARZO"].sum() + catastroCorrecto["TITULOS_50"].sum()
titulosExonerados = catastroCorrecto["EXON_MARZO"].sum() + catastroCorrecto["EXON_50"].sum()
titulosNoExonerados = totalTitulosEmitidos - titulosExonerados
totalExoneracion = catastroCorrecto["MONTO_EXON_MARZO"].sum() + catastroCorrecto["MONTO_EXON_50"].sum()
totalNoExoneracion = catastroCorrecto["MONTO_NOEXON_MARZO"].sum() + catastroCorrecto["MONTO_NOEXON_50"].sum()










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





