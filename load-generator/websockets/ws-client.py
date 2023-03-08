#!/usr/local/bin/python3
import os
import wazo_websocketd_client
import wazo_auth_client

from wazo_applicationd_client import Configuration  # type: ignore
from wazo_applicationd_client import ApiClient
from wazo_applicationd_client import ApiException
from wazo_applicationd_client.api import ApplicationApi

def configure(host, user, password, port=443):
    configuration = Configuration()
    configuration.host = "http://localhost:8000"

    # applicationd API client
    api_client = ApiClient(configuration)
    api = ApplicationApi(api_client)

    # auth client
    c = wazo_auth_client.Client(host, username='admin', password='secret', https=False)

    # websocketd client
    reply = c.token.new('wazo_user', expiration=3600, session_type='mobile')
    c = wazo_websocketd_client.Client(host, port=port, token=reply["token"], verify_certificate=False)

    return c, api

def register(api):
    # register the app, see asterisk dialplan
    api.register_application10_applications_application_name_post("test")
    print("App test registered")

def callback(data):
    print(data)
    call_id = data["call"]["id"]
    app_uuid = data["application_uuid"]
    print(call_id)

    print("answer call")
    api.call_answer10_applications_application_uuid_calls_call_id_answer_put(app_uuid, call_id)
    
    print("create node add to bridge")
    api.create_node_with_calls10_applications_application_uuid_nodes_node_name_post(app_uuid, "bigone", [call_id])

    print("success !!!")


if __name__== "__main__":
    host = os.getenv("HOST_IP", "http://localhost:8000")
    user = os.getenv("AUTH_USER", "user")
    passwd = os.getenv("AUTH_PASSWD", "xxxxx")
    c, api = configure(host, user, passwd)
    register(api)

    c.on('user_outgoing_call_created', callback)

    print("App started")
    c.run()
