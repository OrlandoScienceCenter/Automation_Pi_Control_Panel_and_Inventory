# Inventory Global Vars
already_got_data = 0
item_names = []
item_quantities = []
item_thresholds = []
num_items_in_location = 0
sheet_needs_updating = 0
sheet_update_timeout = 0
row_sub_from = 0

def item_low_email(name, location, qty, threshold):
    global already_got_data
    global item_names
    global item_quantities
    global item_thresholds
    global num_items_in_location
    global sheet_update_timeout
    global row_sub_from
    global colNum
    
    print("Begin email send", file=sys.stderr)
    
    msg = MIMEText("""Please note, %s has a threshold of %s but a current quantity of %s. 
        It is located in: %s \n\n
        if you wish to filter these messages automatically, you can do so with the string 
        inven_notify_low_quantity""" % (name, threshold, qty, location))

    msg['Subject'] = "%s is running low in %s" % (name, location,)
    #put your host and port here
    s = smtplib.SMTP_SSL('smtp.gmail.com:465')
    s.login(gmail_username, gmail_password)
    s.sendmail(gmail_username, address_to_notify, msg.as_string())
    s.quit()
    
    print("""Please note, %s has a threshold of %s but a current quantity of %s. 
            It is located in: %s. Email has been sent.""" % (name, threshold, qty, location))
    
# For excel-style column naming for GoogleSheets
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

addresses = [(1,  1), (1, 26),
             (1, 27), (1, 52),
             (1, 53), (1, 78),
             (1, 79), (1, 104),
             (1, 18253), (1, 18278),
             (1, 702),  # -> 'ZZ1'
             (1, 703),  # -> 'AAA1'
             (1, 16384), # -> 'XFD1'
             (1, 35277039)]

def excel_style(row, col):
    # Convert given row and column number to an Excel-style cell name.
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)

# -----===== Begin Inventory OAuth Section =====-----

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials

# -----===== End Inventory OAuth Section =====-----

# -----===== Begin Inventory System Section =====-----

@app.route("/inventory/update_qty_page/<location>", methods = ['POST', 'GET'])
def inventory(location):
    global already_got_data
    global item_names
    global item_quantities
    global item_thresholds
    global num_items_in_location
    global sheet_update_timeout
    global row_sub_from
    global colNum
    global headerQuery

    qty_to_sub = 0
    row_sub_from = 0

    if request.method == 'POST':
        result = request.form
      
        if already_got_data > 0:
            print('Old data good!', file=sys.stderr)
        else:
            return 'You tried to post without GETting sheet data first. Weird. Show David.'

        if num_items_in_location:
            print('We have already got lookup data. This is good when trying to post.', 
                file=sys.stderr)
        else:
            return 'You tried to post without rows data. How did you even get here? Tell David.'

        for i in range(0, num_items_in_location): 
            if 'button_subone' + str(i) in result:
               qty_to_sub = 1
               row_sub_from = i + 1
               sheet_update_timeout = 3
            elif 'button_subfive' + str(i) in result:
               qty_to_sub = 5
               row_sub_from = i + 1
               sheet_update_timeout = 3 
            elif 'button_subtwenty' + str(i) in result:
               qty_to_sub = 20
               row_sub_from = i + 1
               sheet_update_timeout = 3
        
        item_quantities[row_sub_from - 1] = \
            str(int(item_quantities[row_sub_from - 1]) - qty_to_sub)
        
        # Below here is for updating with a new quantity

        return render_template("inventory_system_templates/index.html", location = location, 
            item_names = item_names, num_items_in_location = num_items_in_location, 
            item_quantities = item_quantities, item_thresholds = item_thresholds)

    if request.method == 'GET':
        already_got_data = 0
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 'version=v4')
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

        rangeName = 'PZ_Inventory' # Gets spreadsheet data

        headerQuery = location
        replacementQty = 999

        result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])

        headerRow = values[0]
        columnContents = []

        item_names = []
        item_quantities = []
        item_thresholds = []

        # End header query

        if not values:
            print('No data found.')
        else:
            colNum = headerRow.index(headerQuery)
            #print('testQuery: ' + str(testQuery) + ' was found to be column ' + str(colNum) + ' in ' + str(headerRow))
            #print('items in ' + testQuery + ':')

            curIndex = 1 # Start past the header row
            # Get the column contents until out
            try:
                while values[curIndex][colNum]:
                    columnContents += [values[curIndex][colNum]]
                    item_names += [values[curIndex][colNum].split(':')[0]]
                    item_quantities += [re.search(': (.*) /', str(values[curIndex][colNum])).group(1)]
                    item_thresholds += [values[curIndex][colNum].split('/')[1].strip()]
                    curIndex += 1
            except:
                print()

        num_items_in_location = curIndex - 1
        already_got_data = 1

       #print('curIndex: ' + str(curIndex), file=sys.stderr)
        return render_template("inventory_system_templates/index.html", location = location, item_names = item_names, 
                num_items_in_location = num_items_in_location, item_quantities = item_quantities, 
                item_thresholds = item_thresholds)

def checkForUpdatesTimer():
    global already_got_data
    global item_names
    global item_quantities
    global item_thresholds
    global num_items_in_location
    global sheet_update_timeout
    global row_sub_from
    global colNum
    global headerQuery

    if sheet_update_timeout > 0:
        sheet_update_timeout -= 1
        print(sheet_update_timeout, file=sys.stderr)

    if sheet_update_timeout == 1:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 'version=v4')
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

        rangeName = 'PZ_Inventory' # Gets spreadsheet data

        result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])

        # Update the sheet
        rangeName = 'PZ_Inventory!{passedCellRange}'.format(passedCellRange = excel_style(row_sub_from + 1, colNum + 1))
        values = [[item_names[row_sub_from - 1] + ': ' + item_quantities[row_sub_from - 1] + ' / ' + 
            str(item_thresholds[row_sub_from - 1]) ],]
        body = {'values': values}
        valueInputOption = 'USER_ENTERED'
        
        # The thing that does the actual writing to the sheet
        result = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, 
                range=rangeName, valueInputOption=valueInputOption, body=body).execute()
        print('Sheet updated!', file=sys.stderr)

        if int(item_quantities[row_sub_from - 1]) < int(item_thresholds[row_sub_from - 1]):
            # Email send to notification email 
            item_low_email(item_names[row_sub_from - 1], headerQuery, item_quantities[row_sub_from - 1], 
                    item_thresholds[row_sub_from - 1])

    threading.Timer(5.0, checkForUpdatesTimer).start()

# -----===== End Inventory System Section =====-----
