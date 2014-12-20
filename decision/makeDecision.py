# -*- coding: utf-8 -*-
'''
Created on 23 нояб. 2014 г.

@author: feelosoff
'''
import sys
from pyes.query import QueryStringQuery
from rake.rake import Rake
import json
from __builtin__ import max
sys.path.insert(0,'/home/priora/workspace/targetmaker/')
from collections import defaultdict
from buildering.db import InitDB
from parsers.text import TextProcess
from graph.orient import GraphWrapper
from twitter.request import TwitterSearcher    
from pyes import ES

class Decision(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        InitDB()
        self.processor = TextProcess()
        self.keyword = Rake("../rake/SmartStoplist.txt")
        self.es = ES('127.0.0.1:9200')
        self.goods = {}

    def depth(self, parent, category, product, k):
        if not category:
            if parent[product.name]:
                return parent[product.name]
            else:
                return [product, 0]
        
        for key, val in category.items():
            if key in parent.keys():
                self.depth(parent[key],val, product, k)
            else:
                parent[key] = self.depth({},val, product, k)
                parent[key][1] += k
            
        return [parent, 0]
    
    def addToGraph(self, product, k = 1):
        self.goods = self.depth( self.goods,json.loads(product.category),product, k)
       
    def getBestChoice(self):
        it = self.goods
        while isinstance(it, dict) or isinstance(it, defaultdict):
            optKey = max(it.items(), key = lambda x : x[1][1])
            it = it[optKey]
        # вернули товар о котором чаще всего говорили(можно через граф откатиться на уровеь назад и взять рандом)
        return it
                
    def contextDecision(self,user):
        for tweet in user.getTweets()[:]:  
            keywordsList = [(" ".join(self.processor.processing(word[0]))) 
                            for word in self.keyword.run(tweet) 
                                if word[1] > 1]
            if not keywordsList:
                continue
            
            query = " ".join(keywordsList)
            res = self.es.search( QueryStringQuery(query), "tweezon","goods")     
            
            try:
                if res:
                    self.addToGraph( res[0])
                else:
                    res = self.es.search( QueryStringQuery(tweet), "tweezon","goods")
                    if res:
                        self.addToGraph( res[0])
            except Exception as e:
                print e
                pass
            
        return self

    def makeDecision(self,user): 
        for v in user.inV():
            if not v.idEl:
                v.idEl = self.contextDecision(v).getBestChoice()['_id']
                v.idEl.save()
                self.goods.clear()
    
        for v in user.inV():
            self.addToGraph(v, 0.33)
            
        self.contextDecision(user)
        product = self.getBestChoice()
        
        user.idEl = product['_id']
        user.save()
        
        return product
            
d = Decision()
d.makeDecision(GraphWrapper().createIfNotFindUser('ncorres',TwitterSearcher()))     