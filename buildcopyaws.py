#!/usr/bin/env python3

import os
import subprocess
import boto3
import fire
import requests
import settings


def getdictcomp(rn_name, user, password, url_v2):
    """
    Arg: 
      rn_name (str): Name of release note
    Return:
      req_dict (dict): Dictionary 'rc_components', 'ops_components', 'configuration'(variables) and other
    """
    url_name = url_v2 + '?name=' + rn_name
    req_name = requests.get(url_name, auth=(user, password))
    # if req_name.status_code == 200:
    print(req_name.status_code, req_name.reason, req_name.json())
    rn_id = (req_name.json().get('results')[0].get('id'))
    url_id = url_v2 + str(rn_id) + '/'
    req_dict = requests.get(url_id, auth=(user, password))
    return req_dict


def getlistrc(req_dict):
    """
    Arg:
     req_dict (dict): Dictionary 'rc_components', 'ops_components', 'configuration'(variables) and other
    Return:
     list_rc (lst): List of dictionaries with RC components
    """
    list_rc = req_dict.json().get('rc_components')
    return list_rc


def getlistops(req_dict):
    """
    Arg:
     req_dict (dict): Dictionary 'rc_components', 'ops_components', 'configuration'(variables) and other
    Return:
     list_ops (lst): List of dictionaries with OPS components
    """
    list_ops = req_dict.json().get('ops_components')
    return list_ops


def upload(bucket, fst_lvl, sec_lvl, thr_lvl, frt_lvl):
    """
    Arg:
     local_directory (str): path local directory
     bucket (str): name of AWS s3 bucket
     destination (str): path in s3
    Uploads files or skips upload if files are exist
    """
    # get an access token and other credentials from ~/.aws/credentials and ~/.aws/config
    client = boto3.client('s3') # TODO
    local_directory = '/mnt/{0}/{1}/{2}/{3}'.format(fst_lvl, sec_lvl, thr_lvl, frt_lvl)
    destination = 'ADS_BUILDS/{0}/{1}/{2}/{3}'.format(fst_lvl, sec_lvl, thr_lvl, frt_lvl)
    # enumerate local files recursively
    for root, dir, files in os.walk(local_directory):
        for filename in files:
            # construct the full local path
            local_path = os.path.join(root, filename)
            # construct the full AWS path
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(destination, relative_path)
            print('Searching "%s" in "%s"' % (s3_path, bucket))
            try:
                client.head_object(Bucket=bucket, Key=s3_path)
                print("Path found on S3! Skipping %s..." % s3_path)
            except:
                print("Uploading %s..." % s3_path)
                client.upload_file(local_path, bucket, s3_path)


def uploadops(list_ops, bucket):
    # upload all OPS components from RN
    for i in range(len(list_ops)):
        upload(bucket, 'PACKAGES', list_ops[i].get('service_name'), list_ops[i].get('branch'), list_ops[i].get('build'))

def uploaddocker(lst_req, list_rc, bucket):
    # upload docker build
    for comp in lst_req:
        for i in range(len(list_rc)):
            if comp.lower() == list_rc[i].get('service_name') and list_rc[i].get('deployment_mode') == 'container':
                comp = comp + '_docker'
                upload(bucket, 'PACKAGES', comp, list_rc[i].get('branch'), list_rc[i].get('build'))


def uploadunix(lst_req, list_rc, bucket):
    # upload unix components
    for comp in lst_req:
        for i in range(len(list_rc)):
            if comp.lower() == list_rc[i].get('service_name') and list_rc[i].get('os_family') == 'unix':
                upload(bucket, 'PACKAGES', comp, list_rc[i].get('branch'), list_rc[i].get('build'))


def uploadtasfax(lst_req, list_rc, bucket):
    # upload TAS and FAX builds
    for comp in lst_req:
        for i in range(len(list_rc)):
            if comp.lower() == list_rc[i].get('service_name') and list_rc[i].get('os_family') == 'windows':
                upload(bucket, 'PACKAGES', comp, list_rc[i].get('branch'), list_rc[i].get('build'))
            # upload tas&fax subcomponents
            if list_rc[i].get('os_family') == 'windows' and list_rc[i].get('parent_service') == comp.lower():
                upload(bucket, 'PACKAGES', list_rc[i].get('service_name'), list_rc[i].get('branch'), list_rc[i].get('build'))


def uploadgudclient(lst_req, list_rc, bucket):
    # upload gudclient (it is not required for POD`s components, but feature has been wrote:))
    for comp in lst_req:
        for i in range(len(list_rc)):
            if list_rc[i].get('os_family') == 'unix' and list_rc[i].get('parent_service') == comp.lower():
                upload(bucket, 'PACKAGES', 'GUD-CLIENT', list_rc[i].get('branch'), list_rc[i].get('build'))


def uploadwindows(lst_req, list_rc, bucket):
    # upload windows components
    for comp in lst_req:
        for i in range(len(list_rc)):
            if comp.lower() == list_rc[i].get('service_name') and list_rc[i].get('os_family') == 'windows':
                upload(bucket, 'ADS', list_rc[i].get('branch'), list_rc[i].get('build'), '')


def execute():
    """
    Arg:
     req_dict (dict): Dictionary 'rc_components', 'ops_components', 'configuration'(variables) and other
    Return:
     list_ops (lst): List of dictionaries with OPS components
    """

    rn_name = str(settings.rn_name)
    user = str(settings.user)
    password = str(settings.password)
    lst_req = list(settings.lst_req)
    lst_req_tas_fax = list(settings.lst_reg_tas_fax)
    bucket = str(settings.bucket)
    url_ads = str(settings.url_ads)
    url_api_rn = str(settings.url_api_rn)
    bld_link = str(settings.bld_link)

    url_v2 = url_ads + url_api_rn

    mount_link = "{0} /mnt/ -o user='{1}',pass='{2}'".format(bld_link, user, password)

    subprocess.Popen("mount.cifs " + mount_link, shell=True)

    gdc = getdictcomp(rn_name, user, password, url_v2)
    glr = getlistrc(gdc)
    glo = getlistops(gdc)

    #TODO choosing of subject for upload
    uploadops(glo, bucket)
    uploadunix(lst_req, glr, bucket)
    uploadgudclient(lst_req, glr, bucket)
    uploadwindows(lst_req, glr, bucket)
    uploadtasfax(lst_req_tas_fax, glr, bucket)
    uploaddocker(lst_req, glr, bucket)

    subprocess.Popen("umount /mnt", shell=True)

if __name__ == '__main__':
    fire.Fire(execute)
