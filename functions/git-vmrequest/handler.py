import requests
import json

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    #clone_url = secrets["vmcloneurl"]
    #host = secrets["vcenterhost"]
    #template = secrets["template"]
    
    clone_url = "http://192.168.192.20:8080/function/vm-clone"
    host = "sydscvvcloudvc01.syddsc.local"
    template = "ubuntu-1604-template-agent"
    data = json.loads(req)
    repopath = data["repository"][0]["full_name"]
    filerequests = data["commits"][0]["added"]

    vmlist = ""
    if (len(filerequests)):
        for filename in filerequests:
            if "template" not in filename.lower():
                file_url = 'https://raw.githubusercontent.com/{0}/master/{1}'.format(repopath, filename)
                response = requests.get(file_url)
                if response.status_code == 200:
                    entry = response.json()

                    name = entry["name"]
                    if "template" in entry:
                        sourcetemplate = entry["template"]
                    else:
                        sourcetemplate = template
                    if "targethost" in entry:
                        targethost = entry["targethost"]
                    else:
                        targethost = host
                    if "dc" in entry:
                        targetdc = entry["dc"]
                    if "vmfolder" in entry:
                        targetfolder = entry["vmfolder"]
                    if "resourcepool" in entry:
                        respool = entry["resourcepool"]
                    if "poweron" in entry:
                        poweron = entry["poweron"]
                    else:
                        poweron = False

                    clone_data = {
                        'host': targethost, 
                        'name': name, 
                        'template': sourcetemplate,
                        'datacenterName': targetdc,
                        'vmFolder': targetfolder,
                        'resourcePool': respool,
                        'powerOn': poweron
                        }

                    response = requests.post(
                        clone_url, 
                        data=json.dumps(clone_data),
                        headers={'Content-Type': 'application/json'},
                        verify=False
                    )
                    vmlist += "{0}/n".format(clone_data)
                else:
                    print(file_url)
    else:
        return {"status": "no new requests"}

    return {"status": "done", "data": vmlist}
