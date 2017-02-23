You need a file called secrets.py in the main dir.

It needs to look like: 

```
app.secret_key = 'thisCanBeAnything'

gmail_username = 'your_gmail_address'
gmail_password = 'your_gmail_pw'
address_to_notify = 'What email to send notifications to when things get low'

spreadsheetId = '' # Google this to figure out what this is. It's the ID for the Google docs spreadsheet.
```
