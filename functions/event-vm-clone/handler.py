import requests
import json

def read_secret(secret):
    f = open('/var/openfaas/secrets/' + secret)
    val = f.read()
    if val is None:
        raise Exception("Requires {0} secret in function namespace".format(secret))
    f.close()
    return val

def handle(req):
    """
    Capture VM event 
    
    """
    gw_url = read_secret("gateway_url")
    slack_url = "{0}/function/slack-notify".format(gw_url)

    data = json.loads(req)
    topic = data.get('topic')
    moref = data.get('managedObjectReference')
    vmName = data.get('Name')

    if moref is not None:
        vmId = moref.get("Value")
        postmessage = "\n{0} :hammertime:\n\nVM Name: *{1}*\nVM_ID: *{2}*".format(topic, vmName, vmId)
    else:
        postmessage = req

    eventtype = "VM Cloned Event"
    details = "*{0}*\n\n{1}".format(eventtype, postmessage) 

    response = requests.post(
        slack_url, details,
        headers={'Content-Type': 'application/text'}
    )

    return {"status": response.status_code}
