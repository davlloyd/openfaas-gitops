from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

import atexit
import argparse
import getpass
import ssl
import json
import requests

def read_secret(secret):
    f = open('/var/openfaas/secrets/' + secret)
    val = f.read()
    if val is None:
        raise Exception("Requires {0} secret in function namespace".format(secret))
    f.close()
    return val

def slack_post(message):
    """
    Post details to slack
    """
    gw_url = read_secret("gateway_url")
    slack_url = "{0}/function/slack-notify".format(gw_url)

    response = requests.post(
        slack_url, message,
        headers={'Content-Type': 'application/text'}
    )
    return {"status": response.status_code}


def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break
    return obj


def clone_vm(
        content, template, vm_name, si,
        datacenter_name, vm_folder, host_name,
        resource_pool, power_on):
    """
    Clone a VM from a template/VM, datacenter_name, vm_folder, datastore_name
    cluster_name, resource_pool, and power_on are all optional.
    """

    # if none git the first one
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)

    if vm_folder:
        destfolder = get_obj(content, [vim.Folder], vm_folder)
    else:
        destfolder = datacenter.vmFolder

    host = get_obj(content, [vim.HostSystem], host_name)
    resource_pool = get_obj(content, [vim.ResourcePool], resource_pool)

    vmconf = vim.vm.ConfigSpec()

    relospec = vim.vm.RelocateSpec()
    relospec.datastore = template.datastore[0]
    relospec.pool = resource_pool
    relospec.host = host

    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = power_on

    task = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)
    return clonespec, task.info.state

def handle(req):
    """
    Let this thing fly
    """
    
    data = json.loads(req)
    host = data.get("host")
    port = data.get("port", 443)
    if host is None:
        raise Exception("Host required")
 
    username = read_secret("vcenter_account")
    password = read_secret("vcenter_password")


    template_name = data.get("template")
    name = data.get("name")
    dc_name = data.get("datacenterName")
    host_name = data.get("hostName")
    vm_folder = data.get("vmFolder")
    resource_pool = data.get("resourcePool")
    power_on = data.get("powerOn", False)

    # connect this thing
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(
        host=host,
        user=username,
        pwd=password,
        port=port,
        sslContext=context)
    try:
        slack_message = "*Clone Request:* \n\n VM Name: *{0}*\n Target: *{1}*\n DC: *{2}*\n ResPool *{3}*\n\n:smile:".format(name, host, dc_name, resource_pool)
        slack_post(slack_message)

        comment = None
        content = si.RetrieveContent()
        template = get_obj(content, [vim.VirtualMachine], template_name)
        state = "unknown"
        clonespec = None
        if template:
            clonespec, state = clone_vm(
                content, template, name, si,
                dc_name, vm_folder,
                host_name, resource_pool,
                power_on)
        else:
            state = "error"
            comment = "template not found"
        return {
            "state": state, 
            "comment": comment, 
            "vm": name, 
            "template": template_name, 
            "dc": dc_name,
            "respool": resource_pool
        }

    finally:
        Disconnect(si)

