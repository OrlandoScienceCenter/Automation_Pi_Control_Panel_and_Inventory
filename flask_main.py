import threading
import httplib2
import os
import re
import json
import requests
import sys
import smtplib

from email.mime.text import MIMEText
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from flask import Flask, render_template, request, redirect, session, url_for, escape
from tinydb import TinyDB, Query, where

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

global_dict = globals()

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def rootpath():
    return """<a href="/exhibitspanel">Exhibit Control/Monitoring Panel</a><br>
        <a href="/inventory/update_qty_page/Bin-B1">Inventory Bin-B1 (For testing)</a><br>"""

with open('secrets.py') as f:
    code = compile(f.read(), 'secrets.py', 'exec')
    exec(code, global_dict)

with open('inventory.py') as f:
    code = compile(f.read(), 'inventory.py', 'exec')
    exec(code, global_dict)

with open('cpanel.py') as f:
    code = compile(f.read(), 'cpanel.py', 'exec')
    exec(code, global_dict)

if __name__ == "__main__":
    checkForUpdatesTimer()
    app.run(host="0.0.0.0", port=int("8080"), threaded=True, debug=True)
