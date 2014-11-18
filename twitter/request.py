# -*- coding: utf-8 -*-
'''
Created on 18 окт. 2014 г.

@author: feelosoff
'''
import tweepy
from Levenshtein import jaro_winkler
from parsers.location import LocationParser
from pyes.es import ES
from nltk.corpus import stopwords
import nltk
from math import log
from twitter.oAuth import TwitterAuth



class TwitterSearcher(object):
    '''
    classdocs
    '''
    def __init__(self):
        self.locParse = LocationParser()
        self.es = ES('127.0.0.1:9200')

        self.auth = TwitterAuth()
        self.api=tweepy.API(self.auth.GetAuth())
        
    def createModel(self,description):
        stops = stopwords.words('english')
        stemmer= nltk.PorterStemmer()
        
        text =nltk.tokenize.wordpunct_tokenize(description) 
        text = [stemmer.stem(word) for word in text if not stemmer.stem(word) in stops]
        
        return nltk.Text(text)
    
    def getChance(self,count, size):
        return (float(count) +0.001) / (size + 1)
    
    def KulbakLeibler(self,model1, model2):
        distance = 0
        
        lenMod1 = len(model1)
        lenMod2 = len(model2)
        
        if lenMod1 == 0:
            return self.getChance(0, 0)
        
        for word, count in model1.vocab().items():
            p = self.getChance(count, lenMod1)
            q = self.getChance(model2.vocab()[word],lenMod2) 
            distance += p * log(p)/log(q)
        
        distance /= lenMod1
        
        return distance
    
    def countDistance(self, amazon,twitter):
        distance = 0        
        amazonModel = self.createModel(amazon.nickName)
        twitterModel =  self.createModel(twitter.description)
        
        distance += self.KulbakLeibler(amazonModel,twitterModel) 
        distance += self.KulbakLeibler(twitterModel,amazonModel) 
        
        return distance / 2
    
    def getPerson(self,user):
        res = None
        for i in xrange(5* len(self.auth.access_key)):
            try:
                res = self.api.search_users('@'+user)[0]
            except Exception as e:
                print 'get person error ', e, e.response.status
                self.api=tweepy.API(self.auth.GetAuth())
            else:
                break
        return res
    
    def getPersonActions(self, user):
        res = None
        for i in xrange(5* len(self.auth.access_key)):
            try:
                res = self.api.user_timeline('@'+user,count = 50)
                break
            except Exception as e:
                if e.response.status == 401:
                    raise e
                print 'get person error ', e , e.response.status, user
                self.api=tweepy.API(self.auth.GetAuth())
            
        return res
    
    def getFollowers(self, **kwds):
        """ params: 
        user
        screen_name 
        """
        user = kwds.get('user',None)
        screen_name = kwds.get('screen_name','')
        follow = []
        
        if not user and not screen_name:
            raise Exception()
        
        if not user and screen_name:
            user = self.getPerson(screen_name)
            
        while True:
            try:
                follow = user.followers()
                break
            except Exception as e:
                print 'twitter error ', e
                
                if e.response.status  != 88 and e.response.status != 131 and  e.response.status != 429:
                    print e.response.status
                    raise e 
                
                self.api=tweepy.API(self.auth.GetAuth())
                user = self.getPerson(screen_name)

        return follow
        
    def getSameUser(self, person):
        while True:
            try:
                users = self.api.search_users(person.name)[:20]
                break
            except Exception as e:
                print 'twitter error ', e
                if e.response.status  != 88 and e.response.status != 131 and e.response.status != 429:
                    raise e 
                self.api=tweepy.API(self.auth.GetAuth())        
        
        count = len(users)
        rankedUsers = []
        
        for i in xrange(count):
            
            distanceName = jaro_winkler(person.name.encode('utf-8').lower(), users[i].screen_name.encode('utf-8').lower())
            distanceNick = jaro_winkler(person.name.encode('utf-8').lower(), users[i].name.encode('utf-8').lower()) 
            
            distanceName = max(distanceName, distanceNick) * (count - i) / count
            distanceDescription = self.countDistance(person, users[i])
            
            tweeAddr = self.locParse.parse(users[i].location)
            amazonAddr = self.locParse.parse(person.location)
            distanceLocation =  (3 -self.locParse.distance(amazonAddr,tweeAddr) ) / 3.0

            rankedUsers.append([users[i], distanceName, distanceLocation, distanceDescription])
    
        rankedUsers.sort(key= lambda el: -el[1] -  el[2] - el[3])
       
        for usr in rankedUsers:
            badUsr = False            
            while True:
                try:
                    if len(self.getFollowers(user= usr[0])) < 5:
                        badUsr = True
                        break
                
                except Exception as e:
                    print 'access twitter err', e
                    
                    if e.response.status != 88 and e.response.status != 131 and  e.response.status != 429:
                        badUsr = True
                        break
                    
                    self.api=tweepy.API(self.auth.GetAuth())
                    continue
                break
            
            if badUsr:
                continue
            
            if usr[2] < 0.3 and usr[3] < 0.01 and usr[1] < 0.6:
                return None
            
            return usr[0].screen_name

        return None
    
    
'''
p = Persons()
p.name = "dll pa"
p.location = "Bakersfield, CA"
p.name = 'Natalia Corres'
p.nickName = 'tech whisperer, artist, making things happen'
ts = TwitterSearcher()
ts = ts.getPersonActions(  "ncorres")
for i in ts:
    for d in i.__dict__:
        print d, i.__dict__[d]
    break
'''