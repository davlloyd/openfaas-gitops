import json
import requests

def read_secret(secret):
    f = open('/var/openfaas/secrets/' + secret)
    val = f.read()
    if val is None:
        raise Exception("Requires {0} secret in function namespace".format(secret))
    f.close()
    return val

def handle(req):
    webhook_url = read_secret("slack_webhook")
    message = req

    slack_data = {'text': message}
  
    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    return {"status": response.status_code}
