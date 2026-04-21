Overview:

1. Tracking new enrolled accounts in Plug
    * Script to pull accounts created during a certain time period
        - Include statements from Plug

2. Extract Electric Choice ID from utility statements.
    * Script to download latest statement for each account
    * Extract Choice ID from the downloaded statement
    * Export report consisting Account number, Account ID and Choice ID.
3. Login to utility portals with customer credentials and navigate to "https://secure.comed.com/MyAccount/MyService/Pages/SummaryDataResults.aspx"
    * Under Get Data for One or Multiple Accounts, select View Summary Data Online
    * Enter Electric Choice Id, select Add, and then select View Usage Data
    * The Capacity PLC field will be available in the top row of the report
    * Download report as PDF (under Discovery)
    * Script to extract value (under Discovery)
4. Extract data: Capacity PLC,Capacity PLC Start Date
    * Copy into spreadsheet 
    * If value is not available, record as 
        - “PLC Not Found”
        - “PLC Start Date Not Found”
5. Upload the extracted values into the Account custom fields in plug through API.