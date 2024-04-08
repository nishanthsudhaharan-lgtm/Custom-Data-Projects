# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 18:51:43 2023

@author: Minto Mathew
"""
# pip install fpdf
import pandas as pd
from fpdf import FPDF
import os

Filename= 'Arcadia Utility Data Capture Template - Hearst.xlsx'
df=pd.read_excel(Filename,sheet_name=0)
xl = pd.ExcelFile(Filename)
sheets = len(xl.sheet_names)

#for i in range(1,sheets):
 #   df1=pd.read_excel(Filename,sheet_name=i)
  #  df=pd.concat([df,df1])
    
df.drop(0,inplace=True)   


for i in df.columns:
    df[i].fillna(' ',inplace=True)


    
class PDF(FPDF):
    def header(self):
        self.add_font(family='DMSans',style='',fname='DMSans.ttf',uni=True)
        self.set_font("DMSans", size=15)
        self.cell(80)
        self.image('Arc_logo.png',w=20,h=10)
        self.cell(30, 10, 'Arcadia Utility Data Capture Template', 0, 0, 'C')
        self.ln(20)
        
isExist = os.path.exists("Output/Hearst")
if not isExist:
    os.makedirs("Output/Hearst")


for i in range(df.shape[0]):
#    if i<2:
#       continue
    if df.iloc[i]['Service Type']=="":
        continue
    data=dict(df.iloc[i])
    
    if (data['Total Cost']==" ") and (data['Total Usage / Consumption']==" ") and (data['Usage Unit']==" "):
        continue
    
    #address=""
    # for k in data['Service Address'].split(',')[1:3]:
    #     address+=k
    #     address+=','
    
    #update total cost and consumption based on Pro Rata
    #if data['Total Usage / Consumption'] != '':
    if data['Pro Ration / Allocation %'] not in [""," "]:
        proration_percent = float(str(data['Pro Ration / Allocation %']).strip('%'))
        usage = round(float(data['Total Usage / Consumption']) * (proration_percent / 100),4)
        cost = round(float(data['Total Cost']) * (proration_percent / 100),4)
    else:
        usage = data['Total Usage / Consumption']
        cost = data['Total Cost']
    
    if cost in [""," "]:
        cost=0
    #else:
    #    usage = data['Total Usage / Consumption']
    #    cost = data['Total Cost']
     
    # Condition is account number is blank
    if data['Account Number']!=" ":
        accountnum=data['Account Number']
    else:
        accountnum=data['Service Address']
   
    data_dict={'Utility Provider':data['Utility Provider / Landlord Name'],
          'Bill To name':"",
          'Billing Address':"",
          'Service Type':data['Service Type'],
          'Service Address: Street line1':data['Service Address'],
          'Service Address: Street line2':"",
          'Service Address: City':"",
          'Service Address: Postal Code':"",
          'Service Address: Country':"",
          'Account Number':accountnum,
          'Site Name':data['siteName'],
          'Pro rata Share':data['Pro Ration / Allocation %'],
          'Statement date':str(data['Statement Date (MM/DD/YY)'])[0:10],
          'Due Date':"",
          'Bill Period Start Date':str(data['Bill Period Start Date\n (MM/DD/YY)'])[0:10],
          'Bill Period End Date':str(data['Bill Period End Date\n (MM/DD/YY)'])[0:10],
          'Days Billed':data['Days Billed'],
          'Meter Number': data['Meter Number'],
          'Usage':usage,
          'Usage Unit':data['Usage Unit'],
          'Total Cost/Bill Amount':str(data['Currency'])+str(" ")+str(cost)
          }
    
    
    if data_dict['Statement date'] not in [""," "]:
        if (data_dict['Statement date']<data_dict['Bill Period Start Date'])|(data_dict['Statement date']<data_dict['Bill Period End Date']):
            print('Statement date Error in record {}'.format(i+1))
            print('Statement date: {} , Start date: {} , End date: {} \n Service Type: {}'.format(data_dict['Statement date'],data_dict['Bill Period Start Date'],data_dict['Bill Period End Date'],data_dict['Service Type']))
            continue
    if (data_dict['Bill Period Start Date']>data_dict['Bill Period End Date']):
        print('Interval date Error in record {}'.format(i+1))
        print('Start date: {} , End date: {} \n Service Type: {}'.format(data_dict['Bill Period Start Date'],data_dict['Bill Period End Date'],data_dict['Service Type']))
        continue
    
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("DMSans", size=10)
    pdf.set_fill_color(14, 255, 133)
    for j,data in enumerate(data_dict):
        y = pdf.get_y()
        x = pdf.get_x()
        pdf.multi_cell(50, 10, data, border=1,align='L',fill=True)
        pdf.set_y(y)
        pdf.set_x(x + 50)
        pdf.multi_cell(140, 10, str(data_dict[data]), border=1,align='L',fill=False)
    pdf.output('Output/Hearst/'+str(data_dict['Utility Provider']).replace('/',"")+'_'+'invoice('+str(i)+')_'+str(data_dict['Service Type'])+'_'+data_dict['Statement date']+'.pdf')
