import json
import requests

def handle(req):
    webhook_url = "https://hooks.slack.com/services/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"
    message = req

    #if metadata is not None:
    #    vmName = metadata.get("vm_name");
    #    vmId = metadata.get("vm_id")
    #    postmessage = "\n{0}\nVM Name: *{1}*\nVM_ID: *{2}*".format(message, vmName, vmId)
    #else:
    #    postmessage = "\n*{0}*\n\nPayload: {1}".format(message, str(payload))
    postmessage = "\n*{0}".format(message) 
    slack_data = {'text': postmessage}
  

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    return {"status": response.status_code}
