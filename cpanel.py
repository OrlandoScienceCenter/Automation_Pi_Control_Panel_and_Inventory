import paho.mqtt.client as paho

# Control Panel Vars
db = TinyDB('exhibits_config_db.json')
exhibit = ['0'] * len(db)
exhibit_name = ['0'] * len(db)
num_exhibits = len(db)
rooms_to_match = []
selected_exhibits = []

def on_publish(client, userdata, mid):
    print("sent command")

client = paho.Client(client_id="PZ_RasPi", clean_session=True, protocol=paho.MQTTv311)
client.on_publish = on_publish
client.connect("localhost", 1883, keepalive=60)
client.loop_start()

@app.route('/exhibitspanel', methods = ['POST', 'GET'])
def exhibits_panel():
    db = TinyDB('exhibits_config_db.json')
    exhibit = ['0'] * len(db)
    num_exhibits = len(db)
    connection_failed = [0]
    exhibit = json.loads(json.dumps(db.all()))

    if request.method == 'POST':
        result = request.form

        for i in range(0, num_exhibits): 
            if 'button_poweron' + str(i) in result:
                try:
                    (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerOn", qos=1)
                    break
                except:
                    connection_failed = exhibit[i]["name"]

            if 'button_poweroff' + str(i) in result:
                try:
                    (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerOff", qos=1)
                    break
                except:
                    connection_failed = exhibit[i]["name"]

            if 'button_reset' + str(i) in result:
                try:
                    (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerReset", qos=1)
                    break
                except:
                    connection_failed = exhibit[i]["name"]

            if 'button_ota' + str(i) in result:
                try:
                    (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "startOTA", qos=1)
                    break
                except:
                    connection_failed = exhibit[i]["name"]

            if 'button_allon' in result:
                for i in range(0, num_exhibits):
                    try:
                        (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerOn", qos=1)
                    except:
                        connection_failed.append([exhibit[i]["name"]])
               
                if len(connection_failed) > 1:
                    return("The following exhibits could not be communicated with: "
                        + str(connection_failed))  + """<br><br><a href="/exhibitspanel">
                        Web Control Panel</a>"""
                else:
                    return("""All exhibits turned on succesfully.<br><br>
                        <a href="/exhibitspanel">Web Control Panel</a>""")
               
            if 'button_alloff' in result:
                for i in range(0, num_exhibits):
                    try:
                        (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerOff", qos=1)
                    except:
                        connection_failed.append([exhibit[i]["name"]])
               
                if len(connection_failed) > 1:
                    return('The following exhibits could not be communicated with: ' + 
                        str(connection_failed) + '<br><br><a href="/exhibitspanel">Web Control Panel</a>')
                else:
                    return("""All exhibits shut off succesfully.<br><br>
                        <a href="/exhibitspanel">Web Control Panel</a>""")
               
 
        return render_template("cpanel_templates/index.html", exhibit = exhibit, 
            num_exhibits = num_exhibits, connection_failed = connection_failed)

    if request.method == 'GET':
        return render_template("cpanel_templates/index.html", exhibit = exhibit, num_exhibits = num_exhibits, 
                connection_failed = connection_failed)

@app.route('/exhibitspanel/addnewexhibit', methods = ['POST', 'GET'])
def add_new_exhibit():
     if request.method == 'POST':
         result = request.form
         db.insert({'name' : str(result["textbox_name"]),
             'floor' : str(result["textbox_floor"]),
             'room' : str(result["textbox_room"]),
             'type' : str(result["textbox_type"]),
             'mqtt_topic' : str(result["mqtt_topic"]) })
         return 'Exhibit added.<br><br><a href="/exhibitspanel">Web Control Panel</a>'

     if request.method == 'GET':
         return render_template("cpanel_templates/addnewexhibit.html")

@app.route('/exhibitspanel/deleteexhibit', methods = ['POST', 'GET'])
def delete_exhibit():
    db = TinyDB('exhibits_config_db.json')
    exhibit = ['0'] * len(db)
    num_exhibits = len(db)

    exhibit = json.loads(json.dumps(db.all()))
    exhibit_query = Query()

    if request.method == 'POST':
        result = request.form

        if 'button_deleteexhibit' in result:
            element_to_delete = db.get(exhibit_query.name == result["dropdown_exhibittodelete"])
            db.remove(eids = [element_to_delete.eid])
            return 'Exhibit: ' + str(result["dropdown_exhibittodelete"]) + """ has been 
                deleted.<br><br><a href="/exhibitspanel">Web Control Panel</a>"""

    if request.method == 'GET':
        return render_template("cpanel_templates/deleteexhibit.html", exhibit = exhibit, num_exhibits = num_exhibits)

@app.route('/exhibitspanel/byfloorroom', methods = ['POST', 'GET'])
def by_floor_room():
    db = TinyDB('exhibits_config_db.json')
    exhibit = ['0'] * len(db)
    num_exhibits = len(db)
    connection_failed = [0]
    num_selected = 0 
    selected_exhibits = []
    number_of_rooms_to_match = 0
    number_of_exhibits = 0
    exhibit = json.loads(json.dumps(db.all()))
    exhibit_query = Query()
    message = ''

    if request.method == 'POST':
        result = request.form
        number_of_rooms_to_match = len(list(set(dict(result).keys())))
        dict_of_rooms_to_match = list(set(dict(result).keys()))

        if number_of_rooms_to_match > 0:
            for i in range(0, number_of_rooms_to_match):
                if i == 0:
                    # This is just to initialize the variable to just the first exhibit each time
                    selected_exhibits = db.search(where('room') == dict_of_rooms_to_match[i]) 
                    number_of_exhibits = 1
                else:
                    selected_exhibits += db.search(where('room') == dict_of_rooms_to_match[i])
                    number_of_exhibits += 1
        else:
            selected_exhibits = ''
            number_of_rooms_to_match = 1

        number_of_exhibits = len(selected_exhibits)


        if 'button_allon' in result:
            message = 'No communication errors, all exhibits turned on succesfully.'
            for i in range(0, number_of_exhibits):
                try:
                    (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerOn", qos=1)
                except:
                    connection_failed.append([selected_exhibits[i]["name"]])

        if 'button_reset' + str(i) in result:
            try:
                (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerReset", qos=1)
            except:
                connection_failed = exhibit[i]["name"]

        if 'button_alloff' in result:
            message = 'No communication errors, all exhibits turned off succesfully.'
            for i in range(0, number_of_exhibits):
                try:
                    (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerOff", qos=1)
                except:
                    connection_failed.append([selected_exhibits[i]["name"]])

        if 'button_ota' + str(i) in result:
            try:
                (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "startOTA", qos=1)
            except:
                connection_failed = exhibit[i]["name"]

        for i in range(0, number_of_exhibits): 
            if 'button_poweron' + str(i) in result:
                message = 'No communication errors, exhibit turned on succesfully.'
                try:
                    (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerOn", qos=1)
                    break
                except:
                    connection_failed = selected_exhibits[i]["name"]

            if 'button_poweroff' + str(i) in result:
                message = 'No communication errors, exhibit turned off succesfully.'
                try:
                    (rc, mid) = client.publish(exhibit[i]["mqtt_topic"], "powerOff", qos=1)
                    break
                except:
                    connection_failed = selected_exhibits[i]["name"]

        if len(connection_failed) > 1:
            message = 'The following exhibits could not be communicated with: ' + str(connection_failed)
            return render_template("cpanel_templates/byfloorroom.html", selected_exhibits = selected_exhibits, 
                    number_of_rooms_to_match = number_of_rooms_to_match, number_of_exhibits = number_of_exhibits, 
                    result = result, message = message)
        else:
            return render_template("cpanel_templates/byfloorroom.html", selected_exhibits = selected_exhibits, 
                    number_of_rooms_to_match = number_of_rooms_to_match, number_of_exhibits = number_of_exhibits, 
                    result = result, message = message)
             
    if request.method == 'GET':
        return render_template("cpanel_templates/byfloorroom.html", selected_exhibits = selected_exhibits, 
                number_of_rooms_to_match = number_of_rooms_to_match, number_of_exhibits = number_of_exhibits, message = message)
