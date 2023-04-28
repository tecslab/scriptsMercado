#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 11:09:04 2022

@author: pablov
"""

import pandas as pd
import mercadosLib
import matplotlib.pyplot as plt
import numpy as np

consultarEnLinea = True # Si no se consulta deberían existir los archivos con la información correspondiente

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

def eliminarDuplicadosYResumir(catastro, nombreMercado, nombreSector):
    #Los duplicados encontrados aquí se presumierían como puestos diferentes ya que ya se eliminó duplicados por puesto & cedula
    conDuplicados = len(catastro.index) #Forma más eficiente de contar
    catastro = catastro.drop_duplicates(subset=["CEDULA"], inplace=False)
    totalComerciantes = len(catastro.index)
    totalDuplicados = conDuplicados - totalComerciantes
    #EL total de puestos es el número de comerciantes más los duplicados
    resumenSector = {'MERCADO': nombreMercado, "SECTOR": nombreSector, 'TOTAL_COMERCIANTES': [totalComerciantes], 'DUPLICADOS': [totalDuplicados], "TOTAL_PUESTOS": [conDuplicados]}
    resumenSector = pd.DataFrame(resumenSector)
    
    return [catastro, resumenSector]

def limpiarCatastro(catastro):
    catastro = mercadosLib.limpiarCedula(catastro)
    catastro = mercadosLib.limpiarNombres(catastro)
    #catastro = mercadosLib.limpiarContratoNoConcesion(catastro)
    catastro = mercadosLib.limpiarPuestos(catastro)
    
    return catastro




docs = [arrayArenal, arrayMercados]
docsNames = ["arenal", "mercadospq"]
catastrosByDoc = [pd.DataFrame(), pd.DataFrame()]
###### Crea excels vacíos para que puedan ser editados sin problemas ############
#################################################
catastroDetalle = pd.DataFrame(columns=["MERCADO", "SECTOR", "TOTAL_COMERCIANTES", "DUPLICADOS", "TOTAL_PUESTOS"])

totalCatastro = pd.DataFrame()
for idx, doc in enumerate(docs):
    for i in range(len(doc)):
    #for i in range(26,27):
    #for i in range(2,3):
        df = pd.read_excel('./attachments/' + str(docsNames[idx]) + '.xlsx', sheet_name=doc[i]["nombre"], dtype={"CEDULA": str}, skiprows=int(doc[i]["skip"]))
        print(doc[i]["nombre"])
        
        nombreMercado = doc[i]["nombre"]
        nombreSector = "Indefinido"
        if (docsNames[idx]=="arenal"):
            nombreMercado = "EL ARENAL"
            nombreSector = doc[i]["nombre"]
            
        catastro = limpiarCatastro(df)
        catastro = catastro.drop_duplicates(subset=["CEDULA", "PUESTO"], inplace=False)
        
        catastro, resumenSector = eliminarDuplicadosYResumir(catastro, nombreMercado, nombreSector)
        catastroDetalle = pd.concat([catastroDetalle, resumenSector])
        #Se agrega al catastro correspondiente
        catastrosByDoc[idx] = pd.concat([catastrosByDoc[idx], catastro])
        #Se agrega al catastro general
        totalCatastro = pd.concat([totalCatastro, catastro])
                
        # with pd.ExcelWriter('./cedulas9D' + str(idx) + '.xlsx', mode='a', engine="openpyxl") as writer:  
        #     cedulasMenosDigitos.to_excel(writer, sheet_name=doc[i]["nombre"])


dfGuadalupe = pd.DataFrame()
for i in range(len(unificarGuadalupe)):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=unificarGuadalupe[i]["nombre"], dtype={"CEDULA": str, "PUESTO": str}, skiprows=int(unificarGuadalupe[i]["skip"]))
      
    catastro = limpiarCatastro(df)
    dfGuadalupe = pd.concat([dfGuadalupe, catastro])

dfGuadalupe = dfGuadalupe.drop_duplicates(subset=["CEDULA", "PUESTO"], inplace=False)

nombreMercado = "EL ARENAL"
nombreSector = "ASOC REINA DE GUADALUPE"

catastro, resumenSector = eliminarDuplicadosYResumir(dfGuadalupe, nombreMercado, nombreSector)
catastroDetalle = pd.concat([catastroDetalle, resumenSector])
catastrosByDoc[0] = pd.concat([catastrosByDoc[0], catastro])
#Se agrega al catastro general
totalCatastro = pd.concat([totalCatastro, catastro])
#dfGuadalupe = dfGuadalupe.sort_values('NOMBRES')

#==============================================================

df = pd.read_excel('./Hoja de cálculo sin título PV.xlsx', dtype={"CEDULA": str}, skiprows=0) # Hoja con cedúla corregidas

catastro = limpiarCatastro(df)
catastro = mercadosLib.limpiarMercado(catastro)
catastro = catastro.drop_duplicates(subset=["CEDULA", "PUESTO"], inplace=False)

mercadosDistintos = catastro["MERCADO"].drop_duplicates(inplace=False)

for mercado in mercadosDistintos:
    registrosMercado = catastro[catastro["MERCADO"]==mercado]
    registrosMercado, resumenSector = eliminarDuplicadosYResumir(registrosMercado, mercado, "Indefinido")
    catastroDetalle = pd.concat([catastroDetalle, resumenSector])
    if (mercado=="EL ARENAL"):
        catastrosByDoc[0] = pd.concat([catastrosByDoc[0], registrosMercado])
    else:
        catastrosByDoc[1] = pd.concat([catastrosByDoc[1], registrosMercado])
        
    totalCatastro = pd.concat([totalCatastro, registrosMercado])
    
tabulado = catastroDetalle.groupby(catastroDetalle['MERCADO']).aggregate(MERCADO=('MERCADO', 'first'), TOTAL_COMERCIANTES=('TOTAL_COMERCIANTES', 'sum'), DUPLICADOS=('DUPLICADOS', 'sum'), TOTAL_PUESTOS=('TOTAL_PUESTOS', 'sum'))
totalPuestos = tabulado["TOTAL_PUESTOS"].sum()
# Los puestos procesados dependen de la forma en que se procese, en este caso
# se están procesando cada puesto de mercado/sector excepto los duplicados
totalPuestosProcesados = tabulado["TOTAL_COMERCIANTES"].sum() - tabulado["DUPLICADOS"].sum()
totalPuestosCatastro = tabulado["TOTAL_PUESTOS"].sum()




    
#catastro = catastro.sort_values('NOMBRES') # Ordena alfabéticamente
#totalCatastro = pd.concat([totalCatastro, catastro])
totalComerciantesCatastro = totalCatastro.drop_duplicates(subset=["CEDULA"], inplace=False)
#totalComerciantesCatastro.to_excel("./totalComerciantesCatastro.xlsx")
#totalComerciantesCatastro["CEDULA"].to_csv('out.zip', index=False)

# Los duplicados aquí son los comerciantes con puestos extra en diferentes sectoresArenal/mercados
resumenXBloque = pd.DataFrame(columns=["COMERCIANTES", "DUPLICADOS"])
for bloqueCatastro in catastrosByDoc:
    puestosBloque = len(bloqueCatastro) # Aquí se excluyen los puestos extra de un comerciante en un mismo sector
    comerciantesBloque = len(bloqueCatastro.drop_duplicates(subset=["CEDULA"], inplace=False))
    duplicadosBloque = puestosBloque - comerciantesBloque
    resumenBloque = {'COMERCIANTES': [comerciantesBloque], 'DUPLICADOS': [duplicadosBloque]}
    resumenBloque = pd.DataFrame(resumenBloque)    
    resumenXBloque = pd.concat([resumenXBloque, resumenBloque])
    
    
# obtener, total puestos arenal, total comerciantes arenal, total de comerciantes con más de un puesto, 
#No se usa el resumen por bloque porque ya se eliminó por cédula, lo que eliminó puestos en un mismo sector
totalPuestosArenal = tabulado[tabulado["MERCADO"]=="EL ARENAL"]["TOTAL_PUESTOS"].sum() 
totalPuestosMercadosPq = tabulado[tabulado["MERCADO"]!="EL ARENAL"]["TOTAL_PUESTOS"].sum()
totalComerciantesArenal = resumenXBloque.iloc[0]["COMERCIANTES"]
totalComerciantesMercadosPq = resumenXBloque.iloc[1]["COMERCIANTES"]
comerciantesPuestosExtraArenal = resumenXBloque.iloc[0]["DUPLICADOS"] #solo en diferentes sectores
comerciantesPuestosExtraMercadosPq = resumenXBloque.iloc[1]["DUPLICADOS"]
    
    



fig = plt.figure()
ax = fig.add_axes([0,0,1,0.5])
labels = ['Total Comerciantes', "Total Puestos Catastro", 'Total Puestos Procesados']
cantidad = [len(totalComerciantesCatastro), totalPuestosCatastro, totalPuestosProcesados ]
ax.barh(labels,cantidad)
plt.show()

#Puestos procesados por mercado
ax = tabulado.plot.bar(x='MERCADO', y='TOTAL_COMERCIANTES', rot=90)
plt.show()

#Comerciantes con más de un puesto en un mismo sector/Mercado
ax = tabulado.plot.bar(x='MERCADO', y='DUPLICADOS', rot=90)
plt.show()


if (consultarEnLinea):
    verificarCedulas = totalComerciantesCatastro["CEDULA"].replace(regex=r'-', value="")
    catastroNuevo = pd.DataFrame()
    for cedula in verificarCedulas:
        nombreContribuyente, mensajeCEL= mercadosLib.verificarContribuyente(cedula)
        
        actualizarInfo = {"CEDULA": [cedula], "NOMBRES": [nombreContribuyente], "NOTA": [mensajeCEL]}
        actualizarInfo = pd.DataFrame(actualizarInfo)
        catastroNuevo = pd.concat([catastroNuevo, actualizarInfo])
    
    # El regex r'.{0}(?=.{1}$)' se puede leer como: si hay un caracter antes de terminar, seleccionar el espacio antes de este
    catastroNuevo["CEDULA"] = catastroNuevo["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")
    catastroNoEncontrado = catastroNuevo[catastroNuevo["NOMBRES"].isnull()]
    catastroNoEncontrado =  totalComerciantesCatastro[totalComerciantesCatastro["CEDULA"].isin(catastroNoEncontrado["CEDULA"])]
    catastroNoEncontrado = catastroNoEncontrado[["CEDULA", "NOMBRES", "PUESTO", "TIPO CONTRATO", "OBSERVACIONES"]]
    catastroNoEncontrado.to_excel("./noContribuyentesCatastroTotal.xlsx") #Blacklist
    catastroCorrecto = catastroNuevo[~catastroNuevo["NOMBRES"].isnull()]
    
    
    
    cantItems = "200"
    catastroCorrecto = catastroCorrecto.reset_index(drop=True)
    catastroCorrecto["CEDULA"] = catastroCorrecto["CEDULA"].replace(regex=r'-', value="")
    for idx, cedula in enumerate(catastroCorrecto["CEDULA"]):
        
        mensaje, resultadosCancelados = mercadosLib.titulosCancelados(cedula)
        if (mensaje=="No Encontrado"):
            catastroCorrecto.loc[idx, "NOTA_CEL"] = "No Encontrado" #CEL: Cuenca en línea
            continue     
        
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
                            montoNoExoMarzo += float(item["TIC_VALOR"])
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
        
    catastroCorrecto.to_excel("./catastroCorrecto.xlsx")
else:
    catastroCorrecto = pd.read_excel('./catastroCorrecto.xlsx', dtype={"CEDULA": str}) # Solo contribuyentes con información de títulos cancelados
    catastroNoEncontrado = pd.read_excel('./noContribuyentesCatastroTotal.xlsx', dtype={"CEDULA": str}) #Blacklist
    
    
totalTitulosCancelados = catastroCorrecto["TITULOS_MARZO"].sum() + catastroCorrecto["TITULOS_50"].sum()
titulosExonerados = catastroCorrecto["EXON_MARZO"].sum() + catastroCorrecto["EXON_50"].sum()
# Realmente no se los puede categorizar como no exonerados porque algunos ya fueron enviados previamente con exoneración
titulosNoExonerados = totalTitulosCancelados - titulosExonerados
totalExoneracion = catastroCorrecto["MONTO_EXON_MARZO"].sum() + catastroCorrecto["MONTO_EXON_50"].sum()    
totalNoExoneracion = catastroCorrecto["MONTO_NOEXON_MARZO"].sum() + catastroCorrecto["MONTO_NOEXON_50"].sum()/2



comerciantesNoPago = len(catastroCorrecto[catastroCorrecto["EXON_MARZO"].isnull()])
noContribuyentes = len(catastroNoEncontrado.index)
print (str(noContribuyentes) + " cédulas del catastro Excel no están registradas como contribuyentes")

totalComerciantesProcesados = len(totalComerciantesCatastro) - noContribuyentes
print ("Se procesó un catastro con " + str(totalComerciantesProcesados) + " comerciantes")
print ("Correspondientes a un aproximado de " + str(totalPuestosCatastro - noContribuyentes) + " puestos") # puede ser que los no contribuyentes tenían mas de un puesto(poco probable)

print ("Se han cancelado un total de " + str(totalTitulosCancelados) + " títulos")
print ("De los cuales " + str(titulosExonerados) + " títulos fueron exonerados")
print ("Y " + str(titulosNoExonerados) + " se pagaron sin exoneración")
print ("Lo que corresponde a $" + str(totalNoExoneracion) + " que no fueron exonerados")

print ("Se tiene un total de " + str(comerciantesNoPago) + " comerciantes que no muestran resultados en el CEL, quizas nunca han pagado un título")


#Comerciantes con más de un puesto en el Arenal
print("Se tiene un total de " + str(totalPuestosArenal) + " en El Arenal")
print("Se tiene un total de " + str(totalPuestosMercadosPq) + " en los demás mercados más el recinto Ferial")

print("Comerciantes con más de un puesto(Diferentes sectores) en el Arenal: " + str(comerciantesPuestosExtraArenal))
print("Comerciantes con más de un puesto en diferentes Mercados (No incluye El Arenal): " + str(comerciantesPuestosExtraMercadosPq))
print("Total de comernciantes que laboran en el Arenal: " + str(totalComerciantesArenal))
print("Total de comernciantes que laboran en Mercados Pequeños + Recinto Ferial: " + str(totalComerciantesMercadosPq))



##############SOLO MARZO

canceladosMarzo = catastroCorrecto["TITULOS_MARZO"].sum()
exoneradosMarzo = catastroCorrecto["EXON_MARZO"].sum()

print(canceladosMarzo) #1408.0
print(exoneradosMarzo) #246.0














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