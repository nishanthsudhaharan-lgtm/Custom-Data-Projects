# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 18:51:43 2023

@author: Minto Mathew
"""
# pip install fpdf
import pandas as pd
from fpdf import FPDF
import os
import os.path


def listtostring(s):
    str1 = ""
    for ele in s:
        str1 += ele
        str1 +=","
    return str1

def dateformater(x):
    delim="-"
    if str(x).find("/")!=-1:
        delim="/"
    if str(x).find("-")!=-1:
        delim="-"
    s=str(x).find(delim)
    print(s)
    month=str(x[0:s])
    print(month)
    newx=x[s+1:]
    
    s=str(newx).find(delim)
    day=str(newx[0:s])
    
    year=str(newx[s+1:])
    fdate= year+"-"+month+"-"+day
    #print(fdate)
    return fdate
            
class PDF(FPDF):
    def header(self):
        self.add_font(family='DMSans',style='',fname='DMSans.ttf',uni=True)
        self.set_font("DMSans", size=15)
        self.cell(80)
        self.image('Arc_logo.png',w=20,h=10)
        self.cell(30, 10, 'Arcadia Utility Data Capture Template', 0, 0, 'C')
        self.ln(20)
        
isExist = os.path.exists("Output")
if not isExist:
    os.makedirs("Output")


Filename= "1 bills (1).xlsx"
df=pd.read_excel(Filename,sheet_name=0)
xl = pd.ExcelFile(Filename)
sheets = len(xl.sheet_names)

for i in range(1,sheets):
    df1=pd.read_excel(Filename,sheet_name=i)
    df=pd.concat([df,df1])
    
df.drop(0,inplace=True)   


for i in df.columns:
    df[i].fillna(' ',inplace=True)

df= df[df['Service Type']!=" "]
df.rename(columns = {'Total Cost \nw/o tax':'Total Cost'}, inplace = True)
df.rename(columns = {'Account Total Cost':'Total Cost'}, inplace = True)
df.rename(columns = {'site Name':'siteName'}, inplace = True)

for i in range(df.shape[0]):
    
    #if (i!=0) & (df.iloc[i]['id']==fileID):
     #   continue
    
    if df.iloc[i]['Service Type']=="":
        continue
    data=dict(df.iloc[i])
    
    if (data['Total Cost']==" ") and (data['Total Usage / Consumption']==" "):
        continue
    """
    if len(data['Service Address'].split(','))>1:
        add_split=data['Service Address'].split(',')
        adln=int(len(add_split)/2)
        ln1=listtostring(add_split[0:adln])[:-1]
        ln2=listtostring(add_split[adln:])[:-1]
    elif len(data['Service Address'].split(','))==1:
        ln1=data['Service Address']
        ln2=""  
    """
    if data['Pro Ration / Allocation %'] not in [""," ","-"]:
        proration_percent = float(str(data['Pro Ration / Allocation %']).strip('%'))
        usage = round(float(data['Total Usage / Consumption']) * (proration_percent / 100),4)
        cost = round(float(data['Total Cost']) * (proration_percent / 100),4)
    else:
        usage = data['Total Usage / Consumption']
        cost = data['Total Cost']
    
    if cost in [""," "]:
        cost=0
        
    account_dict={'Utility Provider':data['Utility Provider / Landlord Name'],
          'Bill To name':data['Billed To name'],
          'Billing Address':"",  
          'Account Number':data['Account Number'],
          #'Statement date':dateformater(str(data['Statement Date (MM/DD/YY)'])[0:10]),
          'Statement date':(str(data['Statement Date (MM/DD/YY)'])[0:10]),
          'TBA':data['TBA'],
          'Due Date':"",
          'Service Type':data['Service Type'],
          'Service Address: line1':data['Service Address'],
          'Service Address: line2':"",
          'Service Address: City':"",
          'Service Address: Postal Code':"",
          'Service Address: Country':"",
          'Site Name':data['siteName'],
          'Pro rata Share':data['Pro Ration / Allocation %'],
          #'Bill Period Start Date':dateformater(str(data['Bill Period Start Date\n(MM/DD/YY)'])[0:10]),
          #'Bill Period End Date':dateformater(str(data['Bill Period End Date \n(MM/DD/YY)'])[0:10]),
          'Bill Period Start Date':(str(data['Bill Period Start Date\n(MM/DD/YY)'])[0:10]),
          'Bill Period End Date':(str(data['Bill Period End Date \n(MM/DD/YY)'])[0:10]),
          'Days Billed':data['Days Billed'],
          'Meter Number': data['Meter Number'],
          'Usage':usage,
          'Usage Unit':data['Usage Unit'],
          'Total Cost/Bill Amount':str(cost),
          'Currency': data['Currency'],
          }
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("DMSans", size=10)
    pdf.set_fill_color(14, 255, 133)
    pdf.set_auto_page_break(True,margin=0.5)
    for j,value in enumerate(account_dict):
        y = pdf.get_y()
        x = pdf.get_x()
        pdf.multi_cell(50, 10, value, border=1,align='L',fill=True)
        pdf.set_y(y)
        pdf.set_x(x + 50)
        pdf.multi_cell(140, 10, str(account_dict[value]), border=1,align='L',fill=False)
    pdf.cell(0, 10, 'End-Of-Created-Data', 1, 1, 'C')
    pdf.output('Output/'+str(account_dict['Utility Provider']).replace('/',"")+'_'+'invoice('+str(i)+')_'+account_dict['Statement date'].replace('/',"-")+'.pdf')
 