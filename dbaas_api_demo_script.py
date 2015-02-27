'''
@author: afulay

Description:
This is a test script for Oracle Enterprise Manager 12c DBaaS RESTful APIs.

Pre-requisites:
1. EM's 'Oracle Cloud Application' plug-in version 12.1.0.8 or higher
2. Python 2.7.3 (http://www.python.org/download/releases/2.7.3/)
3. Python package - httplib2 (http://code.google.com/p/httplib2/)

'''

import httplib2
import base64
import json
import time
import sys

HTTP_GET = 'GET'
HTTP_POST = 'POST'
HTTP_DELETE = 'DELETE'

class MimeType:
    '''
    Mime or Media types for various DB related resources.
    '''
    CLOUD='application/oracle.com.cloud.common.Cloud+json'
    DBFAMILY='application/oracle.com.cloud.common.ServiceFamilyType+json'
    TEMPLATE='application/oracle.com.cloud.common.ServiceTemplate+json'
    TEMPLATE_DB='application/oracle.com.cloud.common.DbPlatformTemplate+json'
    TEMPLATE_SCHEMA='application/oracle.com.cloud.common.SchemaPlatformTemplate+json'
    TEMPLATE_PDB='application/oracle.com.cloud.common.PluggableDbPlatformTemplate+json'
    DBZONE='application/oracle.com.cloud.common.DbZone+json'
    DBINSTANCE='application/oracle.com.cloud.common.DbPlatformInstance+json'

class URI:
    '''
    URI for various DB related resources.
    '''
    CLOUD='/em/cloud'
    DBFAMILY='/em/cloud/service_family_type/dbaas'
    DBZONE='/em/cloud/dbaas/zone/%s'
    TEMPLATE_DB='/em/cloud/dbaas/dbplatformtemplate/%s'
    TEMPLATE_SCHEMA='/em/cloud/dbaas/schemaplatformtemplate/%s'
    DBINSTANCE='/em/cloud/dbaas/dbplatforminstance/byrequest/%s'


class EMConnection:

    def __init__(self, em_url, auth):
        """ Init """
        
        if em_url.endswith("/em"):
            self.em_url=em_url[:-3]
        else:
            self.em_url=em_url
        self.auth = auth


    def http_method(self, uri, mime_type=None, method=HTTP_GET, content_type=None, params=None):
        ''' HTTP GET/POST/DELETE '''
        
        request_body = []
        request_body.append("The Request body -")
        request_body.append("Method: %s" % method)
        request_body.append("Authorization: Basic %s" % self.auth)
        request_body.append("Uri: %s" % uri)
        
        headers = {
                   'Authorization':"Basic %s" % self.auth,
                   }

        if mime_type:
            headers['Accept'] = mime_type
            request_body.append("Accept: %s" % mime_type)

        if method == HTTP_POST:
            headers['Content-Type'] = content_type
            request_body.append("Content-Type: %s" % content_type)

        # print the http header
        log("\n".join(request_body))

        try:
            start=time.time()
            conn = httplib2.Http(timeout=15, disable_ssl_certificate_validation=True)
            resp, content = conn.request(self.em_url + uri, method,  json.dumps(params), headers)
            diff=int(time.time()-start)
            result = json.loads(content)

        except Exception, e:
            print "Err>> Request failed! \n"
            raise e

        return result, diff


def pretty_print_JSON(dict):
    """ Pretty print json output """
    return json.dumps(dict, indent=4 , sort_keys=True)

def get_auth_string(username, password):
    """ Generate encoded string for basic authentication  """
    return base64.encodestring("%s:%s" % (username, password))


def log(msg, jsonOut=''):
    """ Print formatted log statements"""
    if jsonOut:
        print "%s >> %s \n\n JSON Result: \n %s \n\n" % (time.ctime(), msg, jsonOut)
    else:
        print "%s >> %s" % (time.ctime(), msg)


if __name__ == '__main__':

    # User Inputs
    em_url = "https://abc.example.com:7799/em"
    em_username = 'dbaas_user'
    em_password = 'secret'
    db_service_template_name = "Bronze Service - Single Instance Database"
    zone_name = "Demo Zone"
    db_sid = "apidemo" 
    db_service_name = "svc_apidemo"
    db_username = "oracle"
    db_password = "password"
    

    # get an EM connection
    auth = get_auth_string(em_username, em_password)
    em=EMConnection(em_url, auth)
    log("Created EM Connection")

#    Examples:
#    1. List all resources in cloud - across DB, MW, IaaS, etc
#    2a. List all resources associated with DBaaS
#    2b. List all service templates within the DBaaS Family
#    3. List all DB service instances in DBaaS 
#    4. Select and describe a DB service template
#    5. Submit a DB service template on the desired zone 
#    6. Track progress of DB request


    # 1. GET on Cloud to fetch all resources
    print "\nExample: List all resources in Cloud"
    log("Attempting GET on Cloud ...")
    result, exectime = em.http_method(URI.CLOUD)
    log("GET on Cloud succeeded. Time taken: %d sec" % exectime, pretty_print_JSON(result))

    family_types = result['service_family_types']['elements']
    requests = result['service_requests']['elements']
    zones = result['zones']['elements']
    sts = result['service_templates']['elements']

    log("Found %s service family types, %s service request(s), %s zone(s), and %s service template(s)"
        % (len(family_types), len(requests), len(zones), len(sts)))
    print '*'*30
    raw_input("\nPress Enter to continue...\n")


    # 2a. GET on DB Service Family to fetch all DBaaS related resources
    print "\nExample: List all resources associated with DBaaS"
    log("Attempting GET on DB Service Family ...")
    result, exectime = em.http_method(URI.DBFAMILY)
    log("GET on DB Service Family succeeded. Time taken: %d sec" % exectime, pretty_print_JSON(result))

    requests = result['service_requests']['elements']
    zones = result['zones']['elements']
    sts = result['service_templates']['elements']
    
    log("Found %s service request(s), %s zone(s), and %s service template(s)"
        % (len(requests), len(zones), len(sts)))
    print '*'*30
    raw_input("\nPress Enter to continue...\n")
    
    
    # 2b. GET on DB Service Family to fetch all DBaaS service templates using filters
    print "\nExample: List all service templates within the DBaaS Family"
    log("Attempting GET on DB Service Family ...")
    result, exectime = em.http_method("%s?service_templates" % URI.DBFAMILY)
    log("GET on DB Service Family succeeded. Time taken: %d sec" % exectime, pretty_print_JSON(result))

    log("Found %s service template(s)"  % len(sts))
    print '*'*30
    raw_input("\nPress Enter to continue...\n")


    # 3. list all databases. This is done by looping over all zones or service templates and listing the service instances. 
    # Here we loop over zones since, typically, there would be fewer zones than service templates
    print "\nExample: List all DB service instances in DBaaS" 
    all_sis = []
    all_exectime = 0
    log("Attempting to list all service instances ...")
    for zone in zones:
        result, exectime = em.http_method(zone['uri'], MimeType.DBZONE)
        
        for ele in result['service_instances']['elements']:
            all_sis.append(ele)
        all_exectime+=exectime 

    log("GET on DB Zones succeeded. Time taken: %d sec" % all_exectime, pretty_print_JSON(all_sis))
    log("Found %s service instance(s)"  % len(all_sis))
    print '*'*30
    raw_input("\nPress Enter to continue...\n")


    # 4. select and describe a DB service template
    print "\nExample: Select and describe a DB service template"
    # find the uri for the service template 
    st_uri = None
    desired_st = None
    for st in sts:
        if st["name"] == db_service_template_name:
            st_uri = st["uri"]
            break
    
    if not st_uri:
        log("Service template '%s' not found!" % db_service_template_name)
        exit(0)

    log("Attempting GET on DB service template '%s' ..." % db_service_template_name)    
    desired_st, exectime = em.http_method(st_uri, MimeType.TEMPLATE)
    log("GET on serivce template succeeded. Time taken: %d sec" % exectime, pretty_print_JSON(desired_st))
    print '*'*30
    raw_input("\nPress Enter to continue...")

    
    # 5. Submit requests for a DB 
    print "\nExample: Submit a DB service template on the desired zone"
    # find the uri for desired zone
    zone_uri = None
    for z in desired_st["zones"]["elements"]:
        if z["name"] == zone_name:
            zone_uri = z["uri"] 

    if not zone_uri:
        log("Zone '%s' not found!" % zone_name)
        exit(0)
    
    # requesting a service instance on the first zone associated with the DB service template
    params = {
       "zone": zone_uri,
       "name": "api test for db",
       "description": "api test for db",
       "params":
       {
            "username": db_username,
            "password": db_password,
            "database_sid": db_sid, 
            "service_name": db_service_name 
       }
  }

    result, exectime = em.http_method(st_uri, MimeType.DBINSTANCE, HTTP_POST, MimeType.DBINSTANCE, params)
    log("POST on serivce template succeeded. Time taken: %d sec" % exectime, pretty_print_JSON(result))
    print '*'*30
    raw_input("\nPress Enter to continue...")


    # 6. Check request status
    print "\nExample: Track progress of a DB request"
    if "uri" in result:
        iuri=result["uri"]
    else:
        log("Failed to submit request!")
        exit(0)
        
    iresult, exectime = em.http_method(iuri, MimeType.DBINSTANCE)
    log("GET on DB Request succeeded. Time taken: %d sec" % exectime, pretty_print_JSON(iresult))
    
    # loop until database is in status running
    run_status = "RUNNING"
    while iresult["status"] != run_status:
        log("Waiting for 60 sec ...")
        time.sleep(60)
        iresult, exectime = em.http_method(iuri, MimeType.DBINSTANCE)
        log("GET on DB Request succeeded. Time taken: %d sec" % exectime, pretty_print_JSON(iresult))
        
    print '*'*30
    log("DB creation complete!")
    log("API test completed.")

