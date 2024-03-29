# -*- coding: utf-8 -*- 

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for 
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

auth.settings.hmac_key = 'sha512:41d226a6-1f1d-465e-aab1-8c0ae42fc7b7'  # before define_tables()
auth_table = db.define_table(
    auth.settings.table_user_name,
    Field('first_name', length=128, default=""),
    Field('last_name', length=128, default=""),
    Field('username', length=128, default="", unique=True),
    Field('password', 'password', length=256,
          readable=False, label='Password'),
    Field('registration_key', length=128, default= "",
          writable=False, readable=False))

auth_table.username.requires = IS_NOT_IN_DB(db, auth_table.username)

auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled=['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

doa = local_import('douban_oauth_data')
CLIENT_ID=doa.CLIENT_ID
CLIENT_SECRET=doa.CLIENT_SECRET
AUTH_URL=doa.AUTH_URL
TOKEN_URL=doa.TOKEN_URL
ACCESS_TOKEN_URL=doa.ACCESS_TOKEN_URL
from gluon.contrib.login_methods.oauth10a_account import OAuthAccount
import oauth2 as oauth
import gluon.contrib.simplejson as json
import urllib
class DoubanTest(OAuthAccount):
    def get_user(self):
        if self.accessToken() is not None:
            client = oauth.Client(self.consumer, self.accessToken())
            resp, content = client.request('http://api.douban.com/people/%s?alt=json' % urllib.quote('@me'))
            if resp['status'] != '200':
                # cannot get user info. should check status
                return None
            u = json.loads(content)
            return dict(username=u['db:uid']['$t'], name=u['db:uid']['$t'], registration_id=u['id']['$t'])

auth.settings.actions_disabled=['register','change_password','request_reset_password','profile']
auth.settings.login_form=DoubanTest(globals(),CLIENT_ID,CLIENT_SECRET, AUTH_URL, TOKEN_URL, ACCESS_TOKEN_URL)

# redirect on login
auth.settings.login_next=URL('home_timeline')

crud.settings.auth = None                      # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
