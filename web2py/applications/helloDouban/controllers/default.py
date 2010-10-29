# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  
import oauth2 as oauth
import time

from urllib import urlencode
from urllib import quote as urlquote

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = T('Welcome to web2py')
    return dict(message=T('Hello World'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@auth.requires_login()
def home_timeline():
    token = auth.settings.login_form.accessToken() # you can use this also if you prefer: token=session.access_token
    consumer = oauth.Consumer(CLIENT_ID, CLIENT_SECRET) #<- CLIENT_ID, CLIENT_SECRET are defined in db.py
    client = oauth.Client(consumer, token)
    resp, content = client.request('http://api.douban.com/people/%s/miniblog/contacts?start-index=1&max-results=20&alt=json' % urlquote('@me'),
                                   "GET")
    tweet_list = []
    if resp['status'] != '200': #manage the error
        response.flash = "%s: %s" % (T("Could read tweets!"), json.loads(content)['error'])
    else:
        tweet_objs = json.loads(content)
        for tobj in tweet_objs['entry']:
            tweet_list.append(dict(name=tobj['author']['name']['$t'],
                                   icon=tobj['author']['link'][2]['@href'], 
                                   content=tobj['content']['$t']))
    return (dict(tweets=tweet_list))

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()


