#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 06:10:58 2022

@author: Pablo Esteban Villota
"""

import pandas as pd
import numpy as np

concesionesDF = pd.read_excel('./Concesion de uso de locales municipales.xlsx', skiprows=1)
#Separa llos campos que contienen "," y se queda con el primero
reemplazoDosEspacios = concesionesDF["Dirección"].str.replace("  ", " ") # En algunos registros se han colocados 2 espacios depúes de la "," en lugar de 1
comaFiltro = reemplazoDosEspacios.str.split(pat=",", n=1, expand=True)
#Si había una "," se queda con este dato, caso contrario mantiene el dato original
conditions = [(comaFiltro[1].isnull())]
choices = [comaFiltro[0]]
comaFiltro['Dirección general'] = np.select(conditions, choices, default=comaFiltro[1])
# Se cambia "-" por  "*" en los lugares donde haya "-M" (necesario para el proximo paso)
reemplazoDash = comaFiltro['Dirección general'].replace(regex=[r"-M", r"-C", r"-F"], value=["*M", "*C", "*F"])
# Si había un "*" se queda con este dato, caso contrario mantiene el dato original
asterFiltro = reemplazoDash.str.split(pat="*", n=1, expand=True)
conditions = [(asterFiltro[1].isnull())]
choices = [asterFiltro[0]]
asterFiltro['Dirección general'] = np.select(conditions, choices, default=asterFiltro[1])

# Si tiene un espacio al inicio lo elimina
eliminaEspacio = asterFiltro['Dirección general'].str.lstrip(" ")

######################### Faltas ortográficas o de tipeo #####################
correccionArizaga = eliminaEspacio.replace(regex=[r'ASRIZAGA', r'ARIAZAGA', r'ARTIZAGA'], value= "ARIZAGA")
correccionAVega = correccionArizaga.replace(regex=r" A VEGA", value="ARIZAGA VEGA")
correcionGeneral = correccionAVega.replace(regex=[r'GENRAL'], value="GENERAL")
correccionCrespo = correcionGeneral.replace(regex=[r"CRSPO", r'CRERSPO'], value="CRESPO")
correccionMariscal = correccionCrespo.replace(regex=[r'MARSICAL', r'MARSCAL'], value="MARISCAL")
correccionNoviembre = correccionMariscal.replace(regex=[r'NOCIEMBRE$', r'NOVIEMNRE$', r"NVIEMBRE"], value='NOVIEMBRE')
correccionAmericas = correccionNoviembre.replace(regex=[r"AMAERICAS", r"AMERICAS", r"AMÈRICAS", r"MAERICAS", r'AM{ERICAS', r'AMÁRICAS'], value="AMÉRICAS")
correccion3DeNoviembre = correccionAmericas.replace(regex=[r"3 NOVIEMBRE", r"TRES DE NOVIEMBRE"], value="3 DE NOVIEMBRE")
correcion3DeNoviembreEspacio = correccion3DeNoviembre.replace(regex=r"\.3 DE NOVIEMBRE", value=". 3 DE NOVIEMBRE")
correccion27DeFebrero = correcion3DeNoviembreEspacio.replace(regex=[r'27 DE FEBRER$', r"27 FEBRERO", "27 DE FEBRERI", r"27 DE FEBREOR"], value="27 DE FEBRERO")
correccion9DeOctubre = correccion27DeFebrero.replace(regex=[r"9 DE OCTUBER", r"9 DE OCTUBE", r'9 OCTUBRE'], value="9 DE OCTUBRE")
correccion12DeAbril = correccion9DeOctubre.replace(regex=[r"12 ABRIL"], value="12 DE ABRIL")
correccion10DeAgosto = correccion12DeAbril.replace(regex=[r'10 AGOSTO', r"1O DE AGOSTO"], value="10 DE AGOSTO")
correccionMachuca = correccion10DeAgosto.replace(regex=r"MAVHUCA", value="MACHUCA")

#################### OTRAS CORRECCIONES Y ESTANDARIZACIONES ###################
# Reemplaza merdo. , merdo, mcdo., mcdo, mdo., mdo por mercado
reemplazoMercado = correccionMachuca.replace(regex=[r'M(ER|C)?(DO)\.?', r'MERCADO MUNICIPAL'], value='MERCADO')
reemplazoAv = reemplazoMercado.replace(regex=[r"AV.", r"AVNIDA"], value="AV")
reemplazoChorreras = reemplazoAv.replace(regex=[r"CALLE LAS CHORRERAS", "CALLE DE LAS CHORRERAS"], value="LAS CHORRERAS")
# Reemplazar caracteres especiales y patrones semejantes a AD-987
reemplazoCaracteres = reemplazoChorreras.replace(regex=[r"}", r" .{1,2}-.{1,3}"], value="")
reemplazoCC = reemplazoCaracteres.replace(regex=[r"CENTRO DE COMPRAS", r'CENTRO COMPRAS', r"CC\."], value="C.C.")
reemplazoCCEspacio = reemplazoCC.replace(regex=r"C\.C\.9", value="C.C. 9")
reemplazoPuesto = reemplazoCCEspacio.replace(regex=[r" PUESTO .*", r" PUESTO$"], value="")
reemplazoPlaza = reemplazoPuesto.replace(regex=r"PLAZOLETA", value="PLAZA")
reemplazoCueva = reemplazoPlaza.replace(regex=r'CUEVA VALLEJO', value="CUEVA")

#####################    Patrones de direcciones    ###################
patronMariscalYTalbot = reemplazoCueva.replace(regex=[r'.*MARISCAL.*TALBOT.*', r'.*TALBOT.*LAMAR.*'], value="MARISCAL LAMAR Y CORONEL TALBOT")
patronArizagaAmericas = patronMariscalYTalbot.replace(regex=[r'.* ARIZAGA.*AMÉRICAS.*'], value="AV CARLOS ARIZAGA VEGA Y AV DE LAS AMÉRICAS")
patronArizagCrespo = patronArizagaAmericas.replace(regex=[r'.*ARIZA.*CRESPO.*', r".*ARIZAGA.*ROBERTO O.*"], value="AV CARLOS ARIZAGA VEGA Y ROBERTO CRESPO")
patronPorteteKennedy = patronArizagCrespo.replace(regex=[r'.*PORTETE.*KENNEDY.*'], value="VICTORIA DEL PORTETE CDLA. KENNEDY")
patronLargaTorres = patronPorteteKennedy.replace(regex=[r'.*LARGA.*TORRES.*', r'.*TORRES.*LARGA.*'], value="CALLE LARGA Y GENERAL TORRES")
patronMonroyYerovi = patronLargaTorres.replace(regex=[r'.*MONROY.*YERO.*'], value="CALLE PADRE MONROY Y CLEMENTE YEROVI")
patronArizagaAmericas = patronMonroyYerovi.replace(regex=[r'.*ARIZAGA.*AMÉRICAS.*', ".*AMÉRICAS.*ARIZAGA.*"], value="AV CARLOS ARIZAGA VEGA Y AV DE LAS AMÉRICAS")
patronGuapondeligEloy = patronArizagaAmericas.replace(regex=[r".*GUAPONDELIG.*ELOY.*", r'.*ELOY.*GUAPONDELIG.*'], value="GUAPONDELIG Y ELOY ALFARO")
patronSangurimaCueva = patronGuapondeligEloy.replace(regex=[r'.*SANGURIMA.*CUEVA.*'], value="SANGURIMA Y MARIANO CUEVA")
patronLamarHermano = patronSangurimaCueva.replace(regex=[r'.*HERMANO.*LAMAR.*', r'.*LAMAR.*HERMANO.*'], value="MARISCAL LAMAR Y HERMANO MIGUEL")
patronMachucaSangurima = patronLamarHermano.replace(regex=[r'.*MACHUCA.*SANGURIMA.*'], value="VARGAS MACHUCA Y GASPAR SANGURIMA")
patronAndradeYerovi = patronMachucaSangurima.replace(regex=[r'.*ANDRADE.*YERO.*', r'.*YERO.*ANDRADE.*'], value="BELISARIO ANDRADE Y CLEMENTE YEROVI")
patronAndradeTorres = patronAndradeYerovi.replace(regex=[r'.*ANDRADE.*TORRES.*', r'.*TORRES.*ANDRADE.*'], value="BELISARIO ANDRADE Y ADOLFO TORRES")
patronAmericasRemigio = patronAndradeTorres.replace(regex=[r'.*AMÉRICAS.*REMIGIO.*'], value="AV DE LAS AMÉRICAS Y REMIGIO CRESPO")

############# Mercados ################
aislaRotary = patronAmericasRemigio.replace(regex=[r'.*ROTARY.*'], value="PLAZA ROTARY")
aislaCC9Octubre = aislaRotary.replace(regex=[r".*C\.C\. 9 DE OCTUBRE.*"], value="C.C. 9 DE OCTUBRE")
aislaMercado9Octubre = aislaCC9Octubre.replace(regex=[r'.*MERCADO 9 DE OCTUBRE.*'], value="MERCADO 9 DE OCTUBRE")
aislaMercado3Noviembre = aislaMercado9Octubre.replace(regex=[r'.*MERCADO 3 DE NOVIEMBRE.*'], value="MERCADO 3 DE NOVIEMBRE")
aislaMercado12Abril = aislaMercado3Noviembre.replace(regex=[r".*MERCADO 12 DE ABRIL.*"], value="MERCADO 12 DE ABRIL")
aislaMercado27Febrero = aislaMercado12Abril.replace(regex=[r'.*MERCADO 27 DE FEBRERO.*'], value="MERCADO 27 DE FEBRERO")
aislaMercado10Agosto = aislaMercado27Febrero.replace(regex=[r'.*MERCADO 10 DE AGOSTO.*'], value="MERCADO 10 DE AGOSTO")
aislaRecintoFerial = aislaMercado10Agosto.replace(regex=[r'.*RECINTO FERIAL.*'], value="RECINTO FERIAL")
aislaArenal = aislaRecintoFerial.replace(regex=[r'.*ARENAL.*'], value="EL ARENAL")
aislaNarancay = aislaArenal.replace(regex=r'.*NARANCAY.*', value="NARANCAY")

############ DIRECCIONES -> MERCADOS ***********
direcciones12Abril = aislaNarancay.replace(regex=[r".*CALLE PADRE MONROY Y CLEMENTE YEROVI.*", r".*GUAPONDELIG Y ELOY ALFARO.*", r"BELISARIO ANDRADE Y CLEMENTE YEROVI", r'BELISARIO ANDRADE Y ADOLFO TORRES', r"^12 DE ABRIL$"], value="MERCADO 12 DE ABRIL")
direcciones10Agosto = direcciones12Abril.replace(regex=[r".*CALLE LARGA Y GENERAL TORRES.*", r".*ULLAURI Y GENERAL TORRES.*"], value="MERCADO 10 DE AGOSTO")
direccionesArenal = direcciones10Agosto.replace(regex=[r'.*AV CARLOS ARIZAGA VEGA Y AV DE LAS AMÉRICAS.*', r".*TERMINAL DE TRANSFERENCIAS.*", r".*AMÉRICAS.*ARIAS.*", r'.*PLATAFORMA 4.*', r'AV CARLOS ARIZAGA VEGA Y ROBERTO CRESPO'], value="EL ARENAL")
direcciones3Noviembre = direccionesArenal.replace(regex=[r'.*MARISCAL LAMAR Y CORONEL TALBOT.*', r'.*LAMAR.*PLANTA.*', r'.*TALBOT.*PLANTA.*'], value="MERCADO 3 DE NOVIEMBRE")
direccionesCC9Octubre = direcciones3Noviembre.replace(regex=[r'.*SANGURIMA Y MARIANO CUEVA.*'], value= "C.C. 9 DE OCTUBRE")
direccionesSanFrancisco = direccionesCC9Octubre.replace(regex=r'.*TORRES.*CORDOVA.*', value="PLAZA SAN FRANCISCO")
direccionesMercado9Octubre = direccionesSanFrancisco.replace(regex=".*MARISCAL LAMAR Y HERMANO MIGUEL.*", value="MERCADO 9 DE OCTUBRE")
direccionesRotary = direccionesMercado9Octubre.replace(regex=r'.*VARGAS MACHUCA Y GASPAR SANGURIMA.*', value="PLAZA ROTARY")
direcciones27Febrero = direccionesRotary.replace(regex=r"^27 DE FEBRERO$", value="MERCADO 27 DE FEBRERO")

############## AJUSTES FINALES ##################
unificacionAmericas = direcciones27Febrero.replace(regex=[r'.*AMÉRICAS$'], value="AV DE LAS AMÉRICAS")
unificacionArizagaVega = unificacionAmericas.replace(regex=[r'.*ARIZAGA VEGA$'], value="AV CARLOS ARIZAGA VEGA")
unificacionTalbot = unificacionArizagaVega.replace(regex=[r'.*TALBOT$'], value="CORONEL TALBOT")
unificacionCircunvalacion = unificacionTalbot.replace(regex=r'PANAMERICANA SUR', value="CIRCUNVALACION SUR" )
unificacionLarga = unificacionCircunvalacion.replace(regex=r'.*LARGA$', value="CALLE LARGA")
unificacionLamar = unificacionLarga.replace(regex=r".*LAMAR$", value="MARISCAL LAMAR")
unificacionGeneralTorres = unificacionLamar.replace(regex=".*GENERAL TORRES.*", value="GENERAL TORRES")
unificacionGranColombia = unificacionGeneralTorres.replace(regex=".*GRAN COLOMBIA.*", value="GRAN COLOMBIA")


# #Crea lista con todas las direcciones distintas
direccionesDistintas = unificacionGranColombia.drop_duplicates(inplace=False).tolist()

#direccionesDistintas.to_excel('direcciones.xlsx', sheet_name='direcciones')

# # Agrega la dirección filtrada como una columna extra
unificacionGranColombia.name = "Dirección general"
joined = concesionesDF.join(unificacionGranColombia)
joined.to_excel('direcciones.xlsx', sheet_name='direcciones')


for i in direccionesDistintas:
    # Separa en archivos excels distintos según el contenido de la columna agregada
    filtroDirección = joined[joined["Dirección general"].isin([i])]
    separacion = filtroDirección.drop("Dirección general", axis=1) #Elimina la columna extra
    separacion.to_excel('./resultadosConcesiones/'+ i+".xlsx")