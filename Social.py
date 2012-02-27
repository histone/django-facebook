# Python
import urllib, simplejson, cgi

# Django
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt

from myproject.myapp.lib import oauthtwitter2 as oauthtwitter

def set_string(obj):
    newchar = '&#'
    result_string = ''
    for i in range(len(obj)):
        val = ord(obj[i])
        if val >127:
            if val < 999:
                result_string = result_string+newchar+"0"+str(val)+";"
            if val >999:
                result_string = result_string+newchar+str(val)+";"
        else:
            result_string = result_string + obj[i]
    return result_string
class MyFaceBook:
    def __init__(self, fb_app_id,fb__app_secret,return_url):
        self.fb_app_id = fb_app_id
        self.fb__app_secret =fb__app_secret
        self.return_url = return_url
    def connect_to_facebook(self,request):
        args = {
        'client_id': self.fb_app_id,
        'redirect_uri': request.build_absolute_uri(reverse(self.return_url)),
        'scope': 'email,publish_stream,read_stream, friends_likes,friends_checkins,friends_location',
        }
        return ('https://www.facebook.com/dialog/oauth?' + urllib.urlencode(args))
    def get_facebook_access_token(self, request=None, token=None):
        args = {
            'client_id': self.fb_app_id,
            'client_secret': self.fb__app_secret,
            'redirect_uri': request.build_absolute_uri(reverse(self.return_url)),
            'code': token,
        }
        target = urllib.urlopen('https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(args)).read()
        response = cgi.parse_qs(target)
        access_token ={"access_token": response['access_token'][-1]}
        return access_token
    
    def authenticate_facebook_backend(self, access_token=None, key=None):
        if key !=None:
            feed_response = urllib.urlopen('https://graph.facebook.com/me/'+key+'?' + urllib.urlencode(dict(access_token=access_token)))
            user_feed= simplejson.load(feed_response)
            return user_feed
        user_json = urllib.urlopen('https://graph.facebook.com/me?' + urllib.urlencode(dict(access_token=access_token)))
        fb_profile = simplejson.load(user_json)
        return fb_profile
    def find_friends(self,access_token):
        user_json = urllib.urlopen('https://graph.facebook.com/me/friends?' + urllib.urlencode(dict(access_token=access_token)))
        return simplejson.load(user_json)
    def get_wall_feed(self, access_token, key):
        user_json = urllib.urlopen('https://graph.facebook.com/me/'+key+'?' + urllib.urlencode(dict(access_token=access_token)))
        fb_friends = simplejson.load(user_json)
        return fb_friends
    def get_friends_activities(self, access_token, fb_id,option):
        result = urllib.urlopen('https://graph.facebook.com/'+fb_id+'/'+option+'?' + urllib.urlencode(dict(access_token=access_token)))
        return simplejson.load(result)
    def get_fb_location(self,access_token, fb_id):
        try:
            url = 'https://graph.facebook.com/'+fb_id+'?' + urllib.urlencode(dict(access_token=access_token))
            result = urllib.urlopen(url)
            return simplejson.load(result)
        except Exception, e:
            raise Exception("Error in MyFaceBook get_fb_location()==>"+str(e))
    def get_facebook_user_location(self,location_obj, location_model): 
        return_location=None
        try:
            return_location = location_model.objects.get(location_id=location_obj['id'])
        except location_model.DoesNotExist:
            location_id = location_obj['id']
            name = link = likes = category=checkins=is_community_page=description=None
            if "name" in location_obj:
                name = set_string(location_obj['name'])
            if "link" in location_obj:
                link = location_obj['link']
            if "likes" in location_obj:
                likes = location_obj['likes'] 
            if "category" in location_obj:
                category = set_string(location_obj['category'])
            if "is_community_page" in location_obj:
                is_community_page = location_obj['is_community_page']
            if "description" in location_obj:
                description = set_string(location_obj['description'])
            if "checkins" in location_obj:
                checkins = location_obj['checkins']
            latitude = '%.4f' % location_obj['location']['latitude']
            longitude = '%.4f' % location_obj['location']['longitude']                
            return_location = location_model(location_id=location_id,name=name,link=link,likes=likes,category=category,is_community_page=is_community_page,description=description,checkins=checkins,latitude=str(latitude),longitude=str(longitude))
            return_location.save()
        except KeyError:
            pass
        return return_location
class MyTwitter:
    def __init__(self,twt_app_key, twt_app_secret, return_url):
        self.twt_app_key = twt_app_key
        self.twt_app_secret = twt_app_secret
        self.return_url = return_url
    def connect_to_twitter(self,request):
        mytwitter = oauthtwitter.TwitterOAuthClient(self.twt_app_key, self.twt_app_secret)
        request_token = mytwitter.fetch_request_token(callback = request.build_absolute_uri(reverse(self.return_url)))    
        request.session['request_token'] = request_token.to_string()
        signin_url = mytwitter.authorize_token_url(request_token)
        return signin_url 
    def get_access_token(self,token, verifier):
        mytwitter = oauthtwitter.TwitterOAuthClient(self.twt_app_key, self.twt_app_secret)
        return mytwitter.fetch_access_token(token, verifier)
    def authenticate_twitter_backend(self,twitter_access_token):
        twitter = oauthtwitter.TwitterOAuthClient(self.twt_app_key, self.twt_app_secret)
        tw_profile = twitter.get_user_info(twitter_access_token)  
        return tw_profile   
