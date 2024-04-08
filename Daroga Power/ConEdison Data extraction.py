# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 14:40:23 2024

@author: Minto Mathew
"""

import os
import fitz
import numpy as np
import pandas as pd

lst=[]
for i in os.listdir("C:\\Users\\Minto Mathew\\Desktop\\Daroga power\\Bills"):
    doc = fitz.open("Bills//"+i)
    for page in doc:
        text = page.get_text()
        
        if text.find("Your billing summary as of") !=-1:
            ind=text.find("Your billing summary as of")
            Statementdate=text[ind+len("Your billing summary as of "):text.find("\n",ind)]
            
        if text.find("Account Number:") !=-1:
            ind=text.find("Account Number: ")
            Accnum=text[ind+len("Account Number: "):text.find("\n",ind)]
        elif text.find("Account:") !=-1:
            ind=text.find("Account: ")
            Accnum=text[ind+len("Account: "):text.find(" Prior",ind)]
        Accnum=Accnum.replace("-","")    
        ind=text.find("00",text.find("Meter #"))
        meternum=text[ind:ind+9]
        
        CurrCDG=RemCDG=SubCDG=adj=np.NAN
        if text.find("CDG Credit Summary"):
            if text.find("Current Month Allocated CDG Credit") !=-1:
                ind=text.find("Current Month Allocated CDG Credit")
                leng=len("Current Month Allocated CDG Credit")
                CurrCDG=text[ind+leng+1:text.find("\n",ind+leng+1)]
        
            if text.find("Remaining CDG Credit") !=-1:
                ind=text.find("Remaining CDG Credit")
                leng=len("Remaining CDG Credit")
                RemCDG=text[ind+leng+1:text.find("\n",ind+leng+1)]
            
            if text.find("CDG Subscription Fee") !=-1:
                ind=text.find("CDG Subscription Fee")
                leng=len("CDG Subscription Fee")
                SubCDG=text[ind+leng+1:text.find("\n",ind+leng+1)]
            
            if text.find("Adjustments") !=-1:
                ind=text.find("Adjustments")
                leng=len("Adjustments")
                adj=text[ind+leng+1:text.find("\n",ind+leng+1)]
       
    dic={"Account Number":Accnum,"Statement Date":Statementdate,"Meter Number":meternum,"Adjustments":adj,"Current Month Allocated CDG Credit":CurrCDG,
     "Remaining CDG Credit":RemCDG,"CDG Subscription Fee":SubCDG}
    lst.append(dic)

df=pd.DataFrame(lst)
df.to_excel("sample.xlsx",index=False)