import pandas as pd
import datetime
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from pathlib import Path

from incurridos.model import TareaIncurridos


class IncurridosDAOExcel:
	excel=''
	sheet='Desglose Petición Según GESTEP'
	tareas={}

	def __init__(self, excel=""):
		print(excel)
		if excel and IncurridosDAOExcel.excel != excel:
			IncurridosDAOExcel.excel=excel
			IncurridosDAOExcel.df=pd.read_excel(excel, IncurridosDAOExcel.sheet, skiprows=4, engine = 'xlrd', index_col=0, na_values=[datetime.time(0)])
			self.getAll()
	
	def getOne(self,codigo):
		incurrido_disponible={c:int(v['Ppto. Incurrible'] - v['TOTAL']) for (c,v) in IncurridosDAOExcel.pivot.xs(codigo, level=0).iterrows()}
		return TareaIncurridos(codigo,incurrido_disponible)
		
	def getAll(self):
		IncurridosDAOExcel.pivot=IncurridosDAOExcel.df.pivot_table(index=['Código','Actividad'],  values=['Ppto. Incurrible','TOTAL'], aggfunc=sum)
		return IncurridosDAOExcel.pivot
	
	def getDF(self):
		return IncurridosDAOExcel.df
		
if __name__=='__main__':
	
	#Excel de Gestion
	Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing	
	gestion_filename = askopenfilename(title = "Excel de Incurridos", filetypes = (("excel","*.xlsm"),("all files","*.*")), initialdir=r'C:\Users\j.gomez.de.la.cueva\OneDrive - Accenture\Iberdrola\incurridos') 
	print(gestion_filename)   
	i=IncurridosDAOExcel(gestion_filename)
	
	
	print(i.getAll())


		