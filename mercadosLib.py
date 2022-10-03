#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 11:45:31 2022

@author: pablov
"""

import pandas as pd
import requests
import json

def limpiarCedula(DF):
    sinCedula = DF[DF['CEDULA'].isnull()]
    DF = DF.drop(sinCedula.index) # Elimina filas sin cédula
    
    DF["CEDULA"] = DF["CEDULA"].replace(regex=[r"'"], value="")
    # Las cédulas con letra por lo general son indicaciones de que no está funcionando el puesto, tambien recoje las celdas que contienen "-" y "_"
    cedulasConLetras = DF[DF['CEDULA'].str.contains('[a-zA-Z]|^-$|_|Ñ|ñ', na=False, regex=True)]    
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
    
    DF.reset_index(drop=True, inplace=True)
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
    DF["MERCADO"] = DF["MERCADO"].replace(regex=[r'.*PLATAFORMA.*27.*FEBRERO.*', r'.*BELISARIO.*PLATAFORMA.*'], value="27 DE FEBRERO PLATAFORMA")
    
    
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

def limpiarContratoConcesiones(DF):
    # intenta obtener solo concesiones
    DF["TIPO CONTRATO"] = DF["TIPO CONTRATO"].astype(str)
    DF["TIPO CONTRATO"] = DF["TIPO CONTRATO"].replace(regex=[r'.*Renuncia.*', r'.*renuncia.*', r'.*RENUNCIA.*'], value='Renuncia')
    DF["TIPO CONTRATO"] = DF["TIPO CONTRATO"].replace(regex=[r'.*ABANDONO.*', r'.*abandono.*'], value='ABANDONO')
    DF["TIPO CONTRATO"] = DF["TIPO CONTRATO"].replace(regex=[r'.*ARRIENDO.*'], value='ARRIENDO')
    DF["TIPO CONTRATO"] = DF["TIPO CONTRATO"].replace(regex=[r'.*FALLECI.*', r'.*Falleci.*', r'.*falleci.*'], value='FALLECIDO')
        
    c1 = DF["TIPO CONTRATO"]!="ARRIENDO"
    c2 = DF["TIPO CONTRATO"]!="EVENTUAL"
    c3 = DF["TIPO CONTRATO"]!="ABANDONO"
    c4 = DF["TIPO CONTRATO"]!="CONVENIO"
    c5 = DF["TIPO CONTRATO"]!="Renuncia"
    c6 = DF["TIPO CONTRATO"]!="FALLECIDO"
    # c10 = DF["TIPO CONTRATO"]!="SIN CONSECIÒN"   # c8 = DF["TIPO CONTRATO"]!="SIN CONSECIÓN"
    DF = DF[(c1) & (c2) & (c3) & (c4) & (c5) & (c6)]
    DF.reset_index(drop=True, inplace=True)
    return DF

def limpiarContratoNoConcesion(DF):
    # intenta obtener solo concesiones
    c1 = DF["TIPO CONTRATO"]!="SIN CONSECIÓN"
    c2 = DF["TIPO CONTRATO"]!="SIN CONSECIÒN"
    c3 = DF["TIPO CONTRATO"]!="EVENTUAL"
    c4 = DF["TIPO CONTRATO"]!="ARRIENDO ABANDONO"
    c5 = DF["TIPO CONTRATO"]!="ABANDONO 2019"
    c6 = DF["TIPO CONTRATO"]!="CONVENIO"
    c7 = DF["TIPO CONTRATO"]!="Renuncia"
    DF = DF[(c1) & (c2) & (c3) & (c4) & (c5) & (c6) & (c7)]
    return DF

def limpiarNombres(DF):
    DF["NOMBRES"] = DF["NOMBRES"].replace(regex=[r'\ {2,}'], value= " ") # En algunos registros se han colocados más de un espacio
    DF["NOMBRES"] = DF["NOMBRES"].str.rstrip(" ").str.lstrip(" ")
    return DF

def limpiarPuestos(DF):
    #Elimina ciertas letras y caracteres para que sea más fácil comparar
    #Es necesario mejorar para puesto tipo 45-46, sin que empeore para puesto tipo RG-34 que aveces se encuentran en formatos como RG 34, 34-RG...
    #El puesto 1 y 01 son los mismos
    DF["PUESTO"] = DF["PUESTO"].astype(str)
    DF["PUESTO"] = DF["PUESTO"].replace(regex=[r'\(.*\)'], value='')
    DF["PUESTO"] = DF["PUESTO"].replace(regex=[r' '], value='')
    DF["PUESTO"] = DF["PUESTO"].replace(regex=[r'´'], value='')
    DF["PUESTO"] = DF["PUESTO"].replace(regex=[r'[a-zA-Z]|Ñ|ñ|-'], value='')
    DF["PUESTO"] = DF["PUESTO"].replace(regex=[r'/'], value='')
    DF["PUESTO"] = DF["PUESTO"].replace(regex=[r'^0'], value='')
    return DF

def comparacionNombres(registrosRestantes):
    nombresDF = pd.read_excel('./EXONERACION DE CONCESIONES Y ARRIENDOS.xlsx', dtype={"CEDULA": str}, skiprows=3)
    
    nombresDF["NOMBRES"] = nombresDF["NOMBRES"].str.rstrip(' ').str.lstrip(' ')
    nombresDF = limpiarMercado(nombresDF)
    
    ## Sería ideal sacar los duplicados para procesarlos aparte
    
    registrosRecuperados2 = pd.DataFrame(columns=["CEDULA", "NOMBRES", "PUESTO", "VALOR A DESCONTAR", "MERCADO", "OBSERVACION"])
    for idx, cedulaCatastro in enumerate(registrosRestantes["CEDULA"]):
        #puesto = registrosRestantes["PUESTO"].iloc[idx]
        valor = registrosRestantes["VALOR"].iloc[idx]
        mercadoCatastro = registrosRestantes["MERCADO"].iloc[idx]
        nombres = registrosRestantes["NOMBRES"].iloc[idx]
        
        
        dfFiltrado = nombresDF[nombresDF["NOMBRES"].isin([nombres])]   
        dfFiltrado = dfFiltrado[dfFiltrado["MERCADO"]==mercadoCatastro]
        dfFiltrado.loc[ : , ["VALOR"]] = valor
        ######### IMPORTANTE: EJECUTAR PARA HACER COMPROBACION MANUAL DE PUESTOS ##############
        #dfFiltrado.loc[ : , ["PUESTO_CATASTRO"]] = puesto
        registrosRecuperados2 = pd.concat([registrosRecuperados2, dfFiltrado])
    registrosRecuperados2 = registrosRecuperados2.sort_values('NOMBRES') # Ordena alfabéticamente
    registrosRecuperados2 = registrosRecuperados2.groupby(registrosRecuperados2['NOMBRES']).aggregate(NOMBRES=('NOMBRES', 'first'), DESCONTAR=('VALOR A DESCONTAR', 'sum'), VALOR=("VALOR", "first"), REGISTROS_SUMADOS=("MERCADO", "count"), MERCADO=("MERCADO", "first"))
    registrosRecuperados2.rename(columns = {'DESCONTAR':'VALOR A DESCONTAR'}, inplace = True)
    
    registrosRestantes2 = registrosRestantes[~registrosRestantes["NOMBRES"].isin(registrosRecuperados2["NOMBRES"])]
    registrosRestantes2 = registrosRestantes2[["CEDULA", 'NOMBRES', "VALOR", "MERCADO"]]
    registrosRestantes2 = registrosRestantes2.sort_values('NOMBRES') # Ordena alfabéticamente
    registrosRestantes2 = registrosRestantes2.reset_index()
    
    return [registrosRecuperados2, registrosRestantes2]

def verificarContribuyente(cedula):
    #Verifica si una cedula dada es o no contribuyente: Si es que no es retorna el mensaje "No Encontrado", caso contrario un mensaje vacio y el nombre
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
            
    return [nombreContribuyente, mensajeCEL]

def titulosCancelados(cedula):
    # Obtiene una lista de los títulos cancelados de una cédula dada
    cantItems = "200"
    cancelados_URL = "https://enlinea.cuenca.gob.ec/BackendConsultas/api/contribuyente/" + cedula + "/titulos/cancelados?page=1&nitems=" + cantItems
    canceladosRequest = requests.get(cancelados_URL)
    data = canceladosRequest.text
    
    resultadosCancelados = []
    mensaje=""
    if (data=="No encontrado!"):
        mensaje = "No Encontrado" #CEL: Cuenca en línea
        return [mensaje, resultadosCancelados]
    
    resultadosCancelados = json.loads(data)
    
    if ("tipo" in resultadosCancelados):
        mensaje = "No Encontrado"
        return [mensaje, resultadosCancelados]
    
    if (len(resultadosCancelados)==cantItems):
        print ("ADVERTENCIA: Pueden existir más registros que los obtenidos aqui")
    return [mensaje, resultadosCancelados]