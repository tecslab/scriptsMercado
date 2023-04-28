#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 13:44:54 2022

@author: pablov
"""

import pandas as pd
#import numpy as np
import requests
import json

consultarCancelados = True

arrayHojas = [
                 {"nombre": "CENTRO COMERCIAL", "skip": "0", },
                 {"nombre": "JESUS DEL GRAN PODER ", "skip": "0",},
                 {"nombre": "PLATAFORMA EXTERIOR 4 REINA DE ", "skip": "4",},
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
                 {"nombre": "ASOC REINA DE GUADALUPE", "skip": "2",},
                 {"nombre": "PLATAFORMA No. 9 ASOCIACION ABD", "skip": "3",},
                 
                 {"nombre": "PLATAFORMA EXTERIOR No.2ASO", "skip": "4",},  ## Habían dos tablas en esta hoja
                 {"nombre": "PLATAFORMA EXTERIOR No.2UNI", "skip": "3",},  ## FOrmato extraño
                 
                 {"nombre": "PLATAFORMA EXTERIOR 2-3-4-9", "skip": "4",},
                 {"nombre": "ASC HUMANITARIA", "skip": "0",},
                 {"nombre": "PLATAFORMA NO. 3. COOPERATIVA S", "skip": "4",},
                 {"nombre": "PLATAFORMA No. 4 ASOCIACION SAN", "skip": "4",},
                 {"nombre": "ASO. 8 DE MARZO", "skip": "2",},
                 
                 {"nombre": "ASO. 10 DE AGOSTO", "skip": "3",},      ## FOrmato extraño                 
                 
                 {"nombre": "ASO. LUCHA LIBRE", "skip": "3",},
                 {"nombre": "ASO. SEÑOR ANDACOCHA", "skip": "3",},
                 {"nombre": "ASOC.SANTA ANA", "skip": "3",}
              ]


def limpiarCedula(DF):
    DF = DF.drop(DF[DF['CEDULA'].isnull()].index)
    DF["CEDULA"] = DF["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")
    
    sinCedula = DF[DF['CEDULA'].isnull()]
    DF = DF.drop(sinCedula.index) # Elimina filas sin cédula

    # Las cédulas con letra por lo general son indicaciones de que no está funcionando el puesto, tambien recoje las celdas que contienen "-" y "_"
    cedulasConLetras = DF[DF['CEDULA'].str.contains('[a-zA-Z]|^-$|_', na=False, regex=True)]
    DF = DF.drop(cedulasConLetras.index)   
    DF['CEDULA'] = DF['CEDULA'].str.rstrip(' ').str.lstrip(' ')  #algunas cédulas terminan en espacio
    
    # Algunas cedulas no tienen guión, por lo que se lo extrae de todos y luego se lo coloca
    DF["CEDULA"] = DF["CEDULA"].replace(regex=[r'-'], value="")
    # El regex r'.{0}(?=.{1}$)' se puede leer como: si hay un caracter antes de terminar, seleccionar el espacio antes de este
    DF["CEDULA"] = DF["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")
    
    RUC = DF[DF['CEDULA'].str.len()>11]
    DF = DF.drop(RUC.index)
    
    # Ahora todas las cédulas deberían tener 11 dígitos, si tienen menos es porque tienen errores
    menosDigitos = DF[DF['CEDULA'].str.len()<11]
    DF = DF.drop(menosDigitos.index)
    
    DF.reset_index()
    return DF
    

def limpiarMercado(DF):   
    
    #hojaRegistros["MERCADO"] = hojaRegistros["MERCADO"].str.replace("  ", " ") # En algunos registros se han colocados 2 espacios depúes de la "," en lugar de 1
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'\ {2,}'], value= " ") # En algunos registros se han colocados más de un espacio
    # Si tiene un espacio al inicio o final lo elimina
    DF["MERCADO"] = DF["MERCADO"].str.rstrip(" ").str.lstrip(" ")
    
    ######################### Faltas ortográficas o de tipeo #####################
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'ASRIZAGA', r'ARIAZAGA', r'ARTIZAGA'], value= "ARIZAGA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r" A VEGA", value="ARIZAGA VEGA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r"PLATAFPORMA", value="PLATAFORMA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'GENRAL'], value="GENERAL")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"CRSPO", r'CRERSPO'], value="CRESPO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"TPORRES"], value="TORRES")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'MARSICAL', r'MARSCAL'], value="MARISCAL")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'NOCIEMBRE$', r'NOVIEMNRE$', r"NVIEMBRE"], value='NOVIEMBRE')
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"AMAERICAS", r"AMERICAS", r"AMÈRICAS", r"MAERICAS", r'AM{ERICAS', r'AMÁRICAS'], value="AMÉRICAS")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"3 NOVIEMBRE", r"TRES DE NOVIEMBRE"], value="3 DE NOVIEMBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r"\.3 DE NOVIEMBRE", value=". 3 DE NOVIEMBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r" TRES ", value=" 3 ")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'27 DE FEBRER$', r"27 FEBRERO", "27 DE FEBRERI", r"27 DE FEBREOR"], value="27 DE FEBRERO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"9 DE OCTUBER", r"9 DE OCTUBE", r'9 OCTUBRE'], value="9 DE OCTUBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"12 ABRIL"], value="12 DE ABRIL")    
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"RECITNO"], value="RECINTO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'10 AGOSTO', r"1O DE AGOSTO"], value="10 DE AGOSTO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r"\.10 DE AGOSTO", value=". 10 DE AGOSTO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r"MAVHUCA", value="MACHUCA")
    
    #################### OTRAS CORRECCIONES Y ESTANDARIZACIONES ###################
    # Reemplaza merdo. , merdo, mcdo., mcdo, mdo., mdo por mercado
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'M(ER|C)?(DO)\.?', r'MERCADO MUNICIPAL'], value='MERCADO')
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"AV\.", r"AVNIDA"], value="AV")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"CALLE LAS CHORRERAS", "CALLE DE LAS CHORRERAS"], value="LAS CHORRERAS")
    
    # Reemplazar caracteres especiales y patrones semejantes a AD-987
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"}", r" .{1,2}-.{1,3}"], value="")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"CENTRO DE COMPRAS", r'CENTRO COMPRAS', r"CC\.", r"CENTRO COMERCIAL", r'"C\.C"', r'CC'], value="C.C.")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"C\.C\.9"], value="C.C. 9")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r"PLAZOLETA", value="PLAZA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'CUEVA VALLEJO', value="CUEVA")
    
    #####################    Patrones de direcciones    ###################
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*MARISCAL.*TALBOT.*', r'.*TALBOT.*LAMAR.*'], value="MARISCAL LAMAR Y CORONEL TALBOT")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.* ARIZAGA.*AMÉRICAS.*'], value="AV CARLOS ARIZAGA VEGA Y AV DE LAS AMÉRICAS")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*ARIZA.*CRESPO.*', r".*ARIZAGA.*ROBERTO O.*"], value="AV CARLOS ARIZAGA VEGA Y ROBERTO CRESPO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*PORTETE.*KENNEDY.*'], value="VICTORIA DEL PORTETE CDLA. KENNEDY")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*LARGA.*TORRES.*', r'.*TORRES.*LARGA.*'], value="CALLE LARGA Y GENERAL TORRES")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*MONROY.*YERO.*'], value="CALLE PADRE MONROY Y CLEMENTE YEROVI")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*ARIZAGA.*AMÉRICAS.*', ".*AMÉRICAS.*ARIZAGA.*"], value="AV CARLOS ARIZAGA VEGA Y AV DE LAS AMÉRICAS")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r".*GUAPONDELIG.*ELOY.*", r'.*ELOY.*GUAPONDELIG.*'], value="GUAPONDELIG Y ELOY ALFARO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*SANGURIMA.*CUEVA.*'], value="SANGURIMA Y MARIANO CUEVA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*HERMANO.*LAMAR.*', r'.*LAMAR.*HERMANO.*'], value="MARISCAL LAMAR Y HERMANO MIGUEL")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*MACHUCA.*SANGURIMA.*'], value="VARGAS MACHUCA Y GASPAR SANGURIMA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*ANDRADE.*YERO.*', r'.*YERO.*ANDRADE.*'], value="BELISARIO ANDRADE Y CLEMENTE YEROVI")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*ANDRADE.*TORRES.*', r'.*TORRES.*ANDRADE.*'], value="BELISARIO ANDRADE Y ADOLFO TORRES")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*AMÉRICAS.*REMIGIO.*'], value="AV DE LAS AMÉRICAS Y REMIGIO CRESPO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*PLATAFORMA.*27.*FEBRERO.*'], value="27 DE FEBRERO PLATAFORMA")
    
    
    ############# Mercados ################
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r".*C\.C\. 9 DE OCTUBRE.*", r".*9 DE OCTUBRE.*C\.C\..*", r".*C\.C\..*9.*",], value="CENTRO COMERCIAL 9 DE OCTUBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*ROTARY.*'], value="PLAZA ROTARY")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*MERCADO 9 DE OCTUBRE.*', r'^9 DE OCTUBRE$'], value="MERCADO 9 DE OCTUBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*3 DE NOVIEMBRE.*'], value="MERCADO 3 DE NOVIEMBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*10 DE AGOSTO.*'], value="MERCADO 10 DE AGOSTO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*FERIAL.*', r'.*RECINTO.*'], value="RECINTO FERIAL")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*ARENAL.*'], value="EL ARENAL")
    
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*MIRAFLORES.*', value="PLATAFORMA MIRAFLORES")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*PATAMARCA.*', value="PLATAFORMA PATAMARCA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*CEBOLLAR.*', value="PLATAFORMA CEBOLLAR")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*FLORES.*', value="PLAZA FLORES")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*SAN FRANCISCO.*', value="PLAZA SAN FRANCISCO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*QUINTA CHICA.*', value="PLATAFORMA QUINTA CHICA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*SANTA ANA.*', value="PLAZA SANTA ANA")        
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*NARANCAY.*', value="PLATAFORMA NARANCAY")
    
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*27.*FEBRERO.*PLATAFORMA.*', r'^P 27 DE FEBRERO$'], value="PLATAFORMA 27 DE FEBRERO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*MERCADO 27 DE FEBRERO.*', r'^M 27 DE FEBRERO$'], value="MERCADO 27 DE FEBRERO")
    #DF["MERCADO"] = DF["MERCADO"].replace(regex=[r".*MERCADO.*12.*ABRIL.*FRUTAS.*"], value="MERCADO 12 ABRIL  FRUTAS TEMPOR")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*MERCADO 12 DE ABRIL.*', r'^M 12 DE ABRIL$'], value="MERCADO 12 DE ABRIL")
    
    ############ DIRECCIONES -> MERCADOS ***********
    # Por el momento se agrupan todas las direcciones .*GUAPONDELIG.* dentro del mercado 12 de abril
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r".*CALLE PADRE MONROY Y CLEMENTE YEROVI.*", r".*GUAPONDELIG Y ELOY ALFARO.*", r".*GUAPONDELIG.*",  r"^12 DE ABRIL$"], value="MERCADO 12 DE ABRIL")
    #si se sabe que es un mercado entonces LARGA -> 10 DE AGOSTO
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r".*CALLE LARGA Y GENERAL TORRES.*", r".*ULLAURI Y GENERAL TORRES.*", r".*LARGA.*",], value="MERCADO 10 DE AGOSTO") 
    #si se sabe que es un mercado entonces TALBOT -> 3 DE NOVIEMBRE
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*MARISCAL LAMAR Y CORONEL TALBOT.*', r'.*LAMAR.*PLANTA.*', r'.*TALBOT.*PLANTA.*', r'.*TALBOT.*MERCADO.*', r".*LAMAR.*MERCADO.*3.*", r".*TALBOT.*"], value="MERCADO 3 DE NOVIEMBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*SANGURIMA Y MARIANO CUEVA.*', r'.*SANGURIMA.*C\.C\..*'], value= "CENTRO COMERCIAL 9 DE OCTUBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*TORRES.*CORDOVA.*', value="PLAZA SAN FRANCISCO")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=".*MARISCAL LAMAR Y HERMANO MIGUEL.*", value="MERCADO 9 DE OCTUBRE")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*VARGAS MACHUCA Y GASPAR SANGURIMA.*', value="PLAZA ROTARY")    
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*LAMAR.*BENIGNO.*', value="PLAZA SANTA ANA")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r"^27 DE FEBRERO$", r'BELISARIO ANDRADE Y ADOLFO TORRES', r'.*BELISARIO ANDRADE.*', r".*BELISARIO.*FEBRERO.*"], value="MERCADO 27 DE FEBRERO") 
    #DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*AV CARLOS ARIZAGA VEGA Y AV DE LAS AMÉRICAS.*', r".*TERMINAL DE TRANSFERENCIAS.*", r".*AMÉRICAS.*ARIAS.*", r'.*PLATAFORMA 4.*', r'AV CARLOS ARIZAGA VEGA Y ROBERTO CRESPO'], value="EL ARENAL")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=r'.*AMÉRICAS.*FERIAL.*', value="RECINTO FERIAL")
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*AMÉRICAS.*PLATAFORMA.*4.*', r'.*AMÉRICAS.*PLATAFORMA.*3.*', r'.*AMÉRICAS.*C\.C\..*', r'.*AMÉRICAS.*MERCADO.*', r'.*ROBERTO CRESPO.*MERCADO.*'], value="EL ARENAL")
    # Siempre comprobar las direcciones obtenidas, y añadir filtros o modificarlos si hace falta
    # direccionesDistintas = DF["MERCADO"].drop_duplicates()
    DF.reset_index()
    return DF

def eliminarAmbigüedad(DF):
    # # EN EL RECINTO FERIAL SE PAGA 4 DOLARES; EL VALOR A DESCONTAR ES LA MITAD DE LO QUE PAGAN    
    DF["AUXILIAR1"] = DF["MERCADO"].replace(regex=[r'.*AMÉRICAS.*', r'.*ARIZAGA.*'], value="AMBIGUO_FERIA")
    
    DF.loc[ (DF["AUXILIAR1"] == "AMBIGUO_FERIA") & (DF["VALOR A DESCONTAR"]>2), "MERCADO"] = "EL ARENAL"
    # volvemos a procesar el auxiliar 1
    DF["AUXILIAR1"] = DF["MERCADO"].replace(regex=[r'.*AMÉRICAS.*', r'.*ARIZAGA.*'], value="AMBIGUO_FERIA")
    
    DF["AUXILIAR2"] = DF["OBSERVACION"].replace(regex=[r'.*RECINTO.*', r'.*FERIAL.*'], value="RECINTO FERIAL")
    DF["AUXILIAR2"] = DF["AUXILIAR2"].replace(regex=[r'.*MERCADO.*', r'.*EL ARENAL.*'], value="EL ARENAL")    
    
    DF.loc[ (DF["AUXILIAR1"] == "AMBIGUO_FERIA") & (DF["AUXILIAR2"] == "RECINTO FERIAL"), "MERCADO"] = "RECINTO FERIAL"
    DF.loc[ (DF["AUXILIAR1"] == "AMBIGUO_FERIA") & (DF["AUXILIAR2"] == "EL ARENAL"), "MERCADO"] = "EL ARENAL"
    
    return DF

def limpiarContrato(DF):
    # intenta obtener solo concesiones
    c1 = DF["TIPO CONTRATO"]!="ARRIENDO"
    c2 = DF["TIPO CONTRATO"]!="ARRIENDOS"
    c3 = DF["TIPO CONTRATO"]!="EVENTUAL"
    c4 = DF["TIPO CONTRATO"]!="ARRIENDO "
    c5 = DF["TIPO CONTRATO"]!="ABANDONO "
    c6 = DF["TIPO CONTRATO"]!="ARRIENDO ABANDONO"
    c7 = DF["TIPO CONTRATO"]!="ABANDONO 2019"
    c8 = DF["TIPO CONTRATO"]!="SIN CONSECIÓN"
    c9 = DF["TIPO CONTRATO"]!="CONVENIO"
    c10 = DF["TIPO CONTRATO"]!="SIN CONSECIÒN"
    c11 = DF["TIPO CONTRATO"]!="Renuncia"
    DF = DF[(c1) & (c2) & (c3) & (c4) & (c5) & (c6) & (c7) & (c8) & (c9) & (c10) & (c11)]
    # contratosDiferentes = catastro["TIPO CONTRATO"].drop_duplicates(inplace=False)
    # tiposContrato = pd.concat([tiposContrato, contratosDiferentes])
    return DF

def getExonerados(catastro, arrayDFSRegistos):
    registrosRecuperados = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION"])
    #registrosRecuperados = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "PUESTO_CATASTRO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION"])
    for idx, cedulaCatastro in enumerate(catastro["CEDULA"]):
        puesto = catastro["PUESTO"].iloc[idx]
        valor = catastro["VALOR"].iloc[idx]
        #mercadoCatastro = catastro["MERCADO"].iloc[idx]
        for registroDF in arrayDFSRegistos:
            dfFiltrado= registroDF[registroDF["CEDULA"].isin([cedulaCatastro])]            
            #dfFiltrado = dfFiltrado[dfFiltrado["MERCADO"]==mercadoCatastro]
            dfFiltrado.loc[ : , ["VALOR"]] = valor
            ######### IMPORTANTE: EJECUTAR PARA HACER COMPROBACION MANUAL DE PUESTOS ##############
            #dfFiltrado.loc[ : , ["PUESTO_CATASTRO"]] = puesto
            registrosRecuperados = pd.concat([registrosRecuperados, dfFiltrado])
            #registrosRecuperados = registrosRecuperados[["CEDULA", "NOMBRES", "PUESTO", "PUESTO_CATASTRO", "VALOR A DESCONTAR", "OBSERVACION"]]
    registrosRecuperados = registrosRecuperados.sort_values('NOMBRES') # Ordena alfabéticamente
    return registrosRecuperados

def getRestantes(catastro, registrosRecuperados):
    ## Se obtienen los registros que no pasaron por el filtro
    registrosRestantes = catastro[~catastro["CEDULA"].isin(registrosRecuperados["CEDULA"])]
    #registrosRestantes = registrosRestantes[["CEDULA", 'NOMBRES', "VALOR", "MERCADO"]]
    registrosRestantes = registrosRestantes[["CEDULA", 'NOMBRES', "VALOR"]]
    registrosRestantes = registrosRestantes.sort_values('NOMBRES') # Ordena alfabéticamente
    registrosRestantes = registrosRestantes.reset_index()
    return registrosRestantes

def comparacionNombres(registrosRestantes):
    nombresDF = pd.read_excel('./EXONERACION DE CONCESIONES Y ARRIENDOS.xlsx', dtype={"CEDULA": str}, skiprows=3)
    
    nombresDF["NOMBRES"] = nombresDF["NOMBRES"].str.rstrip(' ').str.lstrip(' ')
    nombresDF = limpiarMercado(nombresDF)
    
    ## Sería ideal sacar los duplicados para procesarlos aparte
    
    registrosRecuperados2 = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION", "VALOR"])
    for idx, cedulaCatastro in enumerate(registrosRestantes["CEDULA"]):
        #puesto = registrosRestantes["PUESTO"].iloc[idx]
        valor = registrosRestantes["VALOR"].iloc[idx]
        #mercadoCatastro = registrosRestantes["MERCADO"].iloc[idx]
        nombres = registrosRestantes["NOMBRES"].iloc[idx]
        
        
        dfFiltrado = nombresDF[nombresDF["NOMBRES"].isin([nombres])]            
        #dfFiltrado = dfFiltrado[dfFiltrado["MERCADO"]==mercadoCatastro]
        dfFiltrado.loc[ : , ["VALOR"]] = valor
        ######### IMPORTANTE: EJECUTAR PARA HACER COMPROBACION MANUAL DE PUESTOS ##############
        #dfFiltrado.loc[ : , ["PUESTO_CATASTRO"]] = puesto
        registrosRecuperados2 = pd.concat([registrosRecuperados2, dfFiltrado])
    registrosRecuperados2 = registrosRecuperados2.sort_values('NOMBRES') # Ordena alfabéticamente
    registrosRecuperados2 = registrosRecuperados2.groupby(registrosRecuperados2['NOMBRES']).aggregate(NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), VALOR=("VALOR", "first"), REGISTROS_SUMADOS=("MERCADO", "count"), MERCADO=("MERCADO", "first"))
    registrosRecuperados2.rename(columns = {'DESCONTAR':'VALOR A DESCONTAR'}, inplace = True)
    
    registrosRestantes2 = registrosRestantes[~registrosRestantes["NOMBRES"].isin(registrosRecuperados2["NOMBRES"])]
    #registrosRestantes2 = registrosRestantes2[["CEDULA", 'NOMBRES', "VALOR", "MERCADO"]]
    registrosRestantes2 = registrosRestantes2[["CEDULA", 'NOMBRES', "VALOR"]]
    registrosRestantes2 = registrosRestantes2.sort_values('NOMBRES') # Ordena alfabéticamente
    registrosRestantes2 = registrosRestantes2.reset_index()   
    
    return [registrosRecuperados2, registrosRestantes2]

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





concejalesH3 = pd.read_excel('./PEDIDO DE CONCEJALES EXONERACIONES.xlsx', sheet_name="Hoja3", dtype={"CEDULA": str}, skiprows=0)
concejalesH5 = pd.read_excel('./PEDIDO DE CONCEJALES EXONERACIONES.xlsx', sheet_name="Hoja5", dtype={"CEDULA": str}, skiprows=2)
registrosConcejales = [concejalesH3, concejalesH5]

# Las cédulas en la Hoja5 no tienen guión por lo que se los añade
# El regex r'.{0}(?=.{1}$)' se puede leer como: si hay un caracter antes de terminar, seleccionar el espacio antes de este
concejalesH5["CEDULA"] = concejalesH5["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")
registrosConcejalesProcesado = []

#================================================================
############### LIMPIA EL CAMPO MERCADO #########################
for idx, hojaRegistros in enumerate(registrosConcejales):
    
    hojaRegistros = limpiarCedula(hojaRegistros)
    hojaRegistros = limpiarMercado(hojaRegistros)
    
    if (idx==1):
        hojaRegistros = eliminarAmbigüedad(hojaRegistros)
    hojaRegistros = hojaRegistros.reset_index()
    registrosConcejalesProcesado.append(hojaRegistros)

#direccionesDistintas1 = registrosConcejalesProcesado[0]["MERCADO"].drop_duplicates(inplace=False)
#direccionesDistintas2 = registrosConcejalesProcesado[1]["MERCADO"].drop_duplicates(inplace=False)
#=================================================================================================


registrosFiltradosH3 = registrosConcejalesProcesado[0][registrosConcejalesProcesado[0]["MERCADO"]=="EL ARENAL"]
registrosFiltradosH5 = registrosConcejalesProcesado[1][registrosConcejalesProcesado[1]["MERCADO"]=="EL ARENAL"]

tiposContrato =  pd.DataFrame()

 ###### Crea excels vacíos para que puedan ser editados sin problemas ############
emptyDF = pd.DataFrame()
emptyDF.to_excel('./duplicados.xlsx')
emptyDF.to_excel('./procesados.xlsx')
 #################################################

for i in range(len(arrayHojas)):
#for i in range(26,27):
#for i in range(0,1):
    df = pd.read_excel('./attachments/arenal.xlsx', sheet_name=arrayHojas[i]["nombre"], dtype={"CEDULA": str}, skiprows=int(arrayHojas[i]["skip"]))
    print(i)
    print(arrayHojas[i]["nombre"])
    
    catastro = limpiarCedula(df)
    catastro = limpiarContrato(catastro)
    
    duplicados = catastro[catastro["CEDULA"].duplicated(keep=False)]
    catastro = catastro.drop(duplicados.index)

    catastro = catastro.sort_values('NOMBRES') # Ordena alfabéticamente
    catastro = catastro.reset_index()    
    
    # contratosDiferentes = catastro["TIPO CONTRATO"].drop_duplicates(inplace=False)
    # tiposContrato = pd.concat([tiposContrato, contratosDiferentes])
    
    registrosRecuperados = getExonerados(catastro, registrosConcejalesProcesado)
    
        
    # =========================  PARA OBTENER LA SUMA DE LO VALORES DE CADA COMERCIANTE =========================
    aggregation_functions = {"CEDULA": "first", 'NOMBRES': 'first', 'VALOR A DESCONTAR': 'sum', 'MERCADO': "count", "VALOR": "first"}
    #aggregation_functions = {"CEDULA": "first", 'NOMBRES': 'first', 'VALOR A DESCONTAR': 'sum', 'MERCADO': "count"}
    registrosRecuperados = registrosRecuperados.groupby(registrosRecuperados['CEDULA']).aggregate(aggregation_functions)
    registrosRecuperados.rename(columns = {'MERCADO':'REGISTROS_SUMADOS'}, inplace = True)
    #============================================================================================================
    
    
    ## Se obtienen los registros que no pasaron por el filtro
    registrosRestantes = getRestantes(catastro, registrosRecuperados)

    [registrosRecuperados2, registrosRestantes2] = comparacionNombres(registrosRestantes)
    
    #====================================================================================================
    #=====================  CONSULTA DE TITULOS CANCELADOS EN SISTEMA CUENCA EN LINEA ===================
    if (consultarCancelados):            
        registrosRestantes2 = consultaCancelados(registrosRestantes2)
    #====================================================================================================
    #====================================================================================================
    
    todosLosRegistros = pd.concat([registrosRecuperados, registrosRecuperados2, registrosRestantes2])
    
    ########## SE GENERA EL EXCEL CONLOS RESULTADOS
    with pd.ExcelWriter('./procesados.xlsx', mode='a', engine="openpyxl") as writer:  
        #todosLosRegistrosConH3.to_excel(writer, sheet_name=arrayHojas[i]["nombre"])
        todosLosRegistros.to_excel(writer, sheet_name=arrayHojas[i]["nombre"])
        
    
    ############# COMPROBACION DE ERRORES ##################
    # cont = 0
    # for j in range(len(catastro["CEDULA"])):
        
    #     recuperadosDF  = registrosRecuperados[registrosRecuperados["CEDULA"].isin([catastro["CEDULA"].iloc[j]])]    
    #     restantesDF = registrosRestantes[registrosRestantes["CEDULA"].isin([catastro["CEDULA"].iloc[j]])]
    #     # todosLosRegistros[~todosLosRegistros["CEDULA"].isin(catastro["CEDULA"])]
        
    #     procesa = recuperadosDF
    #     #print(testDF)
    #     if (len(procesa)>1):
    #         #print("#########")
    #         #print(procesa["CEDULA"].iloc[0])
    #         #print(procesa["NOMBRES"])
    #         cont +=1
    #         #cont=cont + len(procesa)-1
    
    # sumaRegistros = len(registrosRecuperados)+len(registrosRestantes)-cont
    # if(sumaRegistros!=len(catastro)):
    #     print("Puede haber errores")
    #     duplicados = catastro.drop(catastro["CEDULA"].drop_duplicates(inplace=False).index)
    #     recuperadosDuplicados = registrosRecuperados[registrosRecuperados["CEDULA"].isin(duplicados["CEDULA"])]
    #     print(recuperadosDuplicados)
        
    
    
    ############## Para separar en un excel todos los registros con problemas   ######################
    # procesarAparte = pd.concat([sinCedula, RUC, cedulasConLetras])
    
    # with pd.ExcelWriter('./procesarAparte.xlsx', mode='a', engine="openpyxl") as writer:  
    #     procesarAparte.to_excel(writer, sheet_name=arrayHojas[i]["nombre"])
    ##################################################################################################
    
    ############## Para separar en un excel todos los registros duplicados   ######################    
    # with pd.ExcelWriter('./duplicados.xlsx', mode='a', engine="openpyxl") as writer:  
    #     duplicados.to_excel(writer, sheet_name=arrayHojas[i]["nombre"])
    ##################################################################################################
        
    
        
    
    
    # valorNulo = df[df['VALOR'].isnull()]
    # sinValorNulo = df.drop(valorNulo.index) # Elimina filas sin cédula
    # # convertimos a string para poder procesar con metodos de strings, esto porque algunos DF contienen "-" en el valor
    # sinValorNulo['VALOR']= sinValorNulo['VALOR'].astype('string')    
    
    # valorConLetras = sinValorNulo[sinValorNulo['VALOR'].str.contains('[a-zA-Z]|^-$|_', na=False, regex=True)]
    # valorSinLetras = sinValorNulo.drop(valorConLetras.index)
    # # Convertimos float
    # valorSinLetras['VALOR']= valorSinLetras['VALOR'].astype('float64')
    
    # totalValor = valorSinLetras["VALOR"].sum()
    
    # arrayHojas[i]["totalValor"]= totalValor
    

## display(arenalDF.iloc[27])
# df.iloc[0:2, 2:5]
# df.iloc[0:2]

