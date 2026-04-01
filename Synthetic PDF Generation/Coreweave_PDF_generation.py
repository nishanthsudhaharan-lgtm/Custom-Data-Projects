# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 11:21:30 2026

@author: MintoMathew
"""

# pip install fpdf
import pandas as pd
from fpdf import FPDF
import os
import os.path
import io
import fitz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm

#Audit functions

def dateaudit(acc,met):
    if met['Period Start Date']>met['Period End Date']:
        print("Start date higher than end date")
    if acc['Statement date'] not in [""," "]:
        if (acc['Statement date']<met['Period Start Date'])|(acc['Statement date']<met['Period End Date']):
            print("Statement Date Error")


def staudit(met):
    st=['electric','water','sewer','gas','natural gas','sanitation','waste','natural_gas','elec','fuel oil','oil']
    m=met['Service Type'].lower()
    m=m.removesuffix(" ")
    if m=="natural gas":
        m="gas"
    if m not in st:
        print("Service type {} not in accepted list of sevice types".format(met['Service Type']))
        return
    if met['Total Usage Unit'] == " ":
        print("Usage Unit Null")
        return
    uelec=['kwh','kw','kvar']
    ugas=['ccf','therms','btu']
    uoth=['gallons','HGAL']
    if m=='electric':
        if met['Total Usage Unit'].lower() not in uelec:
            print("Invalid UOM/Service Type {} for Electric service".format(met['Total Usage Unit']))
        return
    if m=='gas':
        if met['Total Usage Unit'].lower() not in ugas:
            print("Invalid UOM/Service Type {} for Gas service".format(met['Total Usage Unit']))
        return
    if (m=='water')|(m=='sewer'):
        if met['Total Usage Unit'].lower() not in uoth:
            print("Invalid UOM/Service Type {} for Water/Sewer service".format(met['Total Usage Unit']))
        return

def usageaudit(met):
    try:
        m=float(met['Total Cost/Bill Amount'])/float(met['Usage'])
    except:
        return
    if met['Service Type'].lower()=="electric":
        #print(met['Service Type'])
        rl=0.001
        rh=10
        if met['Currency'] == "USD":
            rl=0.025
            rh=0.35
        
        if (m>rh)|(m<rl):
            print("Total kwh Cost value of {} not in normal range".format(m))
        return    
    else:
        return
    
    if met['Usage Unit']=="cubic ft":
        rl=0.001
        rh=10
        if met['Currency'] == "USD":
            rl=0.025
            rh=0.35
        
        if (m>rh)|(m<rl):
            print("Total cubic ft Cost value of {} not in normal range".format(m))
        return
    
    if met['Usage Unit']=="M3":
        rl=0.001
        rh=10
        if met['Currency'] == "USD":
            rl=0.30
            rh=2.35
       
        if (m>rh)|(m<rl):
            print("Total M3 Cost value of {} not in normal range".format(m))
        return
    
    if met['Usage Unit']=="therms":
        rl=0.001
        rh=10
        if met['Currency'] == "USD":
            rl=0.30
            rh=2.35
        
        if (m>rh)|(m<rl):
            print("Total therms Cost value of {} not in normal range".format(m))
        return    
    
    if met['Usage Unit']=="gallons":
       if met['Currency'] == "USD":
           rl=0.001
           rh=0.003
       
       if (m>rh)|(m<rl):
            print("Total gallons Cost value of {} not in normal range".format(m))
       return    
   
    if met['Usage Unit']=="BTU":
        rl=0.001
        rh=10
        if met['Currency'] == "USD":
            rl=0.30
            rh=2.35
        
        if (m>rh)|(m<rl):
            print("Total BTU Cost value of {} not in normal range".format(m))
        return   
    
    if met['Usage Unit']=="ccf":
        rl=0.001
        rh=10
        
        if met['Currency'] == "USD":
            rl=0.30
            rh=2.35
        if (m>rh)|(m<rl):
            print("Total ccf Cost value of {} not in normal range".format(m))
        return
        
#Audit function end


def listtostring(s):
    str1 = ""
    for ele in s:
        str1 += ele
        str1 +=","
    return str1

# Initializing Google drive API
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build("drive", "v3", credentials=creds)

def downloadfiles(dowid, dfilespath, folder=None):
    request = service.files().get_media(fileId=dowid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    pbar = tqdm(total=100, ncols=70)
    while done is False:
        status, done = downloader.next_chunk()
        if status:
            pbar.update(int(status.progress() * 100) - pbar.n)
    pbar.close()
    if folder:
        with io.open(folder + "/" + dfilespath, "wb") as f:
            fh.seek(0)
            f.write(fh.read())
    else:
        with io.open(dfilespath, "wb") as f:
            fh.seek(0)
            f.write(fh.read())

def dateformater(x):
    delim="/"
    if str(x).find("/")!=-1:
        delim="/"
    if str(x).find("-")!=-1:
        return x[0:10]
    
    
    x=str(x).replace("\"","")
    
    s=str(x).find(delim)
    
    month=str(x[0:s])
    
    newx=x[s+1:]
    
    s=str(newx).find(delim)
    
    day=str(newx[0:s])
    
    year=str(newx[s+1:])
    
    fdate= year+"-"+month+"-"+day
    
    return fdate
    

def merge_pdfs(input_pdfs, output_pdf):
    result = fitz.open()

    for pdf in input_pdfs:
        with fitz.open(pdf) as mfile:
            result.insert_pdf(mfile)
    print(output_pdf+".pdf")
    result.save(output_pdf)
            
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
    
isExist = os.path.exists("Output/Temp")
if not isExist:
    os.makedirs("Output/Temp")



fn=str(input("Enter the xlsx filename: "))
Filename= fn+".xlsx"
df=pd.read_excel(Filename,sheet_name=0,keep_default_na=False, na_values=[' '])
xl = pd.ExcelFile(Filename)
sheets = len(xl.sheet_names)

for i in range(1,sheets):
    df1=pd.read_excel(Filename,sheet_name=i,keep_default_na=False, na_values=[' '])
    df=pd.concat([df,df1])

df.drop(0,inplace=True)

#for i in df.columns:
#    df[i].fillna(' ',inplace=True)

df= df[df['Service Type']!=" "]
df.rename(columns = {'Total Cost \nw/o tax':'Total Cost'}, inplace = True)
df.rename(columns = {'Meter Total Cost':'Total Cost'}, inplace = True)
df.rename(columns = {'site Name':'siteName'}, inplace = True)
df.rename(columns = {'Sourace FIle ID':'Source File id'}, inplace = True)
df.rename(columns = {' Source File Id':'Source File id'}, inplace = True)
df.rename(columns = {'Source File Id':'Source File id'}, inplace = True)
df.rename(columns = {'Statement Date (MM/DD/YY)':'Statement Date (MM/DD/YYYY)'}, inplace = True)
df.rename(columns = {'Actual Source URL':'Source File id'}, inplace = True)
df.rename(columns = {'Bill Period Start Date\n(MM/DD/YYYY)':'Bill Period Start Date\n(MM/DD/YY)'}, inplace = True)
df.rename(columns = {'Bill Period End Date \n(MM/DD/YYYY)':'Bill Period End Date \n(MM/DD/YY)'}, inplace = True)
df.rename(columns = {'Bill Period Start Date\n (MM/DD/YY)':'Bill Period Start Date\n(MM/DD/YY)'}, inplace = True)
df.rename(columns = {'Bill Period End Date \n (MM/DD/YY)':'Bill Period End Date \n(MM/DD/YY)'}, inplace = True)

fileID=df.iloc[0]['Source File id']    # Initial file Id
df['id']=[string[32:65] for string in df['Source File id']]
for i in range(df.shape[0]):
    
    if (i!=0) & (df.iloc[i]['id']==fileID):
        continue
    
    if df.iloc[i]['Service Type']=="":
        continue
    if df.iloc[i]['Utility Provider / Landlord Name'][0:4]=="This":
        continue
    
    data=dict(df.iloc[i])
    
    if data['Utility Provider / Landlord Name'][0:4]=="Requ":
        continue
    
    if (data['Total Cost']==" ") and (data['Total Usage / Consumption']==" "):
        continue
    
    fileID=newfileID=data['id']
        
    account_dict={'Utility Provider':data['Utility Provider / Landlord Name'],
          'Account Number':data['Account Number'],
          'Bill To name':data['Bill to name'],
          'Billing Address':data['Billing Address'], 
          'Statement date':dateformater(str(data['Statement Date (MM/DD/YYYY)'])[0:10]),
          'Account Total Cost':data['Account Total Cost'],
          'Due Date':"",
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
    
    if data['id']:
        downloadfiles(data['id'], "Output/Temp/Source.pdf", folder=None)
    
    for k in range(1,df.shape[0]+1):
        if fileID==newfileID:
            pdf.add_page()
            pdf.multi_cell(50, 10, "Meter {}".format(k), border=1,align='L',fill=False)
            
            
            if len(data['Service Address'])>70:
                
                ln1=data['Service Address'][0:70]
                ln2=data['Service Address'][70:]
            else:
                ln1=data['Service Address']
                ln2=""
            
            #Calculated field logic. Removed as per Chris' suggestion.
            '''
            if data['Total Usage / Consumption Available or Calculated?']!="Available":
                usage=data['Calculated Total usage']
                uav="Calculated"
            else:
                usage=data['Total Usage / Consumption']
                uav=data['Total Usage / Consumption Available or Calculated?']
                
            
            if data['PUE Available or Calculated?']!="Available":
                pue=data['Calculated PUE']
                pav="Calculated"
            else:
                pue=data['PUE']
                pav=data['PUE Available or Calculated?']
                
            
            if data['IT Usage Available or Calculated?']!="Available":
                itu=data['Calculated ITU']
                iav="Calculated"
            else:
                itu=data['IT Usage']
                iav=data['IT Usage Available or Calculated?']
            '''    
            usage= data['Total Usage / Consumption']
            uav=data['Total Usage / Consumption Available or Calculated?']
            pue=data['PUE']
            pav=data['PUE Available or Calculated?']
            itu=data['IT Usage']
            iav=data['IT Usage Available or Calculated?']
            
            #Meter level datapoints
            meter_dict={
            'Service Type':data['Service Type'],
            'Service Address: line1':ln1,
            'Service Address: line2':ln2,
            'Service Address: City':"",
            'Service Address: Country':"",
            'Site Name':data['siteName'],
            'Pro rata Share':data['Pro Ration / Allocation %'],
            'Period Start Date':dateformater(str(data['Bill Period Start Date\n(MM/DD/YY)'])[0:10]),
            'Period End Date':dateformater(str(data['Bill Period End Date \n(MM/DD/YY)'])[0:10]),
            'Days Billed':data['Days Billed'],
            'Meter Number': data['Meter Number'],
            'Total Usage':usage,
            'Total Usage Unit':data['Usage Unit'],
            'Total Usage Availability?':uav,
            'PUE':pue,
            'PUE Availability?':pav,
            'IT Usage':itu,
            'IT Usage Unit':data['IT Usage Unit'],
            'IT Usage Availability?':iav,
            'Meter Total Cost/Bill Amount':data['Total Cost'],
            'Currency': data['Currency'],
            'Notes':data['Meter Notes']
            }
            dateaudit(account_dict,meter_dict)
            staudit(meter_dict)
            usageaudit(meter_dict)
            
            for j,value in enumerate(meter_dict):
                y = pdf.get_y()
                x = pdf.get_x()
                pdf.multi_cell(50, 10, value, border=1,align='L',fill=True)
                pdf.set_y(y)
                pdf.set_x(x + 50)
                pdf.multi_cell(140, 10, str(meter_dict[value]), border=1,align='L',fill=False)
                
            
            if i+k <df.shape[0]:
                newfileID= df.iloc[i+k]['id']
                data=dict(df.iloc[i+k])
                continue
            elif i+k >= df.shape[0]:
                break
        else:
            break
    
    pdf.cell(0, 10, 'End-Of-Created-Data', 1, 1, 'C')
    pdf.output('Output/Temp/Synthetic.pdf')
    
    if data['id']:
        merge_pdfs(['Output/Temp/Synthetic.pdf','Output/Temp/Source.pdf'], 'Output/'+str(account_dict['Utility Provider']).replace('/',"")+'_'+'invoice('+str(i)+')'.replace('/',"-")+'.pdf')
    
    else:
        inputfile='Output/Temp/Synthetic.pdf'
        inputfile.save('Output/'+str(account_dict['Utility Provider']).replace('/',"")+'_'+'invoice('+str(i)+')'.replace('/',"-")+'.pdf')