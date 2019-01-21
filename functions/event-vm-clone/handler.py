import requests
import json

def handle(req):
    """
    Capture VM event 
    
    """
    slack_url = "http://192.168.192.20:8080/function/slack-notify"
    message = req

    postmessage = "*{0}".format(message) 
    event_data = {'vmcloned': postmessage}
  

    response = requests.post(
        slack_url, data=json.dumps(event_data),
        headers={'Content-Type': 'application/json'}
    )
    return {"status": response.status_code}
