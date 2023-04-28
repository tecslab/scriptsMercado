#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 14:28:38 2022

@author: pablov
"""

import requests
import json

#print(response_API.status_code)

#cedula = "0104346424"
#cedula = "1001183480"
cedula = "0101573996"
cantItems = "160"

cancelados_URL = "https://enlinea.cuenca.gob.ec/BackendConsultas/api/contribuyente/" + cedula + "/titulos/cancelados?page=1&nitems=" + cantItems
canceladosRequest = requests.get(cancelados_URL)
data = canceladosRequest.text

resultadosCancelados = json.loads(data)

if ("tipo" in resultadosCancelados):
    print("error")
    print(resultadosCancelados["tipo"])

if (len(resultadosCancelados)==cantItems):
    print ("ADVERTENCIA: Pueden existir más registros que los obtenidos aqui")

contFiltrados = 0
exoneradoTotal = 0
mesesNoExonerados = 0

titulosMarzo = []

for item in resultadosCancelados:
    if ((item["PRE_CLAVE"][0:3]=="MER") | (item["PRE_CLAVE"][0:3]=="CLM")):
        añoEmision = item["TIC_FECHA_EMISION"][7:]
        if (añoEmision == "20"):
            mesEmision = item["TIC_FECHA_EMISION"][3:6]
            if (mesEmision=="MAR"):
                titulosMarzo.append(item)
            
            
            
            # if ((mesEmision=="JUL") | (mesEmision=="AGO") | (mesEmision=="SEP") | (mesEmision=="OCT") | (mesEmision=="NOV") | (mesEmision=="DIC")):
            #     exoneradoTotal += float(item["TIP_MONTO_EXONERACION"])
            #     contFiltrados +=1
            #     if (item["TIP_MONTO_EXONERACION"]=="0"):
            #         mesesNoExonerados +=1

display(titulosMarzo)









# pendientes_URL =  "https://enlinea.cuenca.gob.ec/BackendConsultas/api/contribuyente/" + cedula + "/pendiente/titulos?pagina=1&nitems=" + cantItems + "&fecha=29-8-2022&unificar=true"
# pendientesRequest = requests.get(pendientes_URL)
# data = pendientesRequest.text
# resultadosPendientes = json.loads(data)

# if (len(resultadosPendientes)==cantItems):
#     print ("ADVERTENCIA: Pueden existir más registros que los obtenidos aqui")

# contFiltrados = 0
# exoneradoTotal = 0
# mesesNoExonerados = 0
# for item in resultadosPendientes:
#     if ((item["PRE_CLAVE"][0:3]=="MER") | (item["PRE_CLAVE"][0:3]=="CLM")):
#         añoEmision = item["TIC_FECHA_EMISION"][7:]
#         if (añoEmision == "20"):
#             mesEmision = item["TIC_FECHA_EMISION"][3:6]
#             if ((mesEmision=="JUL") | (mesEmision=="AGO") | (mesEmision=="SEP") | (mesEmision=="OCT") | (mesEmision=="NOV") | (mesEmision=="DIC")):
#                 exoneradoTotal += float(item["TIP_MONTO_EXONERACION"])
#                 contFiltrados +=1
#                 if (item["TIP_MONTO_EXONERACION"]=="0"):
#                     mesesNoExonerados +=1

# print(contFiltrados)
# print(exoneradoTotal)
# print(mesesNoExonerados)
                    
                    
