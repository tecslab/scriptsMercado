#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 12:15:26 2022

@author: pablov
"""
import pandas as pd

#catastroCorrecto["CEDULA"] = catastroCorrecto["CEDULA"].replace(regex=[r'.{0}(?=.{1}$)'], value="-")

catastroRentas = pd.read_excel('./archivoRentas.xlsx', sheet_name="Concesion", dtype={"CEDULA_RUC": str}, skiprows=3)
catastroRentas2P = pd.read_excel('./archivoRentas.xlsx', sheet_name="Datos Concesion mas de un local", dtype={"CED": str}, skiprows=1)

catastroRentasExtra = pd.read_excel('./archivoRentas2.xlsx', sheet_name="Concesión", dtype={"CEDULA_RUC": str}, skiprows=4)

test = catastroRentas2P[catastroRentas2P["CED"].isin(catastroRentasExtra["CEDULA_RUC"])]