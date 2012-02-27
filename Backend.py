# Python
import urllib, cgi, simplejson

# Django
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import sha, random
# Custom
from myproject.myapp.facebook import MyFaceBook 
from myproject.myapp.models import FacebookUser,TwitterUser,Fb_Location
    #/////////////////////////////////////////
class FacebookBackend:
    def authenticate(self, token=None,myfacebook=None):
        fb_profile = myfacebook.authenticate_facebook_backend(access_token=token, key=None)
        try:
            fb_user = FacebookUser.objects.get(facebook_id=str(fb_profile['id']))
        except FacebookUser.DoesNotExist:
            location_obj = myfacebook.get_fb_location(token,fb_profile['location']['id'])
            location = myfacebook.get_facebook_user_location(location_obj,Fb_Location)
            fb_user = FacebookUser(username=fb_profile['username'],first_name=fb_profile['first_name'],last_name=fb_profile['last_name'],email=fb_profile['email'],is_staff=1,is_active=1, facebook_id=fb_profile['id'],name=fb_profile['name'],gender=fb_profile['gender'],locale=fb_profile['locale'],link=fb_profile['link'],location=location)
        fb_user.access_token = token
        fb_user.save()
        return fb_user
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    supports_object_permissions = False
    supports_anonymous_user = False
    
class TwitterBackend:
    def authenticate(self, token=None,mytwitter=None):
        tw_profile = mytwitter.authenticate_twitter_backend(token)
        tw_user=''
        try:
            tw_user = TwitterUser.objects.get(twitter_id = str(tw_profile['id']))
            #return tw_user
        except TwitterUser.DoesNotExist:
            tw_user = TwitterUser(username=tw_profile['screen_name'],is_staff=1,is_active=1, twitter_id=tw_profile['id'],name = tw_profile['name'],location=tw_profile['location'],time_zone=tw_profile['time_zone'],url=tw_profile['url'],profile_image_url=tw_profile['profile_image_url']) 
        # if user is authenticated then login user
        tw_user.access_token = token
        tw_user.save()
                
        return tw_user
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    supports_object_permissions = False
    supports_anonymous_user = False
