# -*- coding: utf-8 -*-
'''
Created on 31 окт. 2014 г.

@author: feelosoff
'''
import tweepy

class TwitterAuth(object):
    '''
    classdocs
    '''


    def __init__(self):
        
        self.consumer_key = ["mD68Xtt994xZPSQ7a6DuiyHmQ", "Mn3aoIqjqGk2BBgVMzCr6MBBx", 
                             "rHCdg6ynk81csSvscrtpPjrin","leWkal65jsiXRGVyWLIo4JgHU"]
        self.consumer_secret = ["FboATUEDCPOJLGNze0AryhEaFKqhRATEq8d9iPlZfVBOujDvqC", "KH9gouzLUwkzlnM21aFgtXmcowNrpVv5SHv8jFNsjBGzkN8gvC",
                                "xfMRi7DXeB3BOSC6H1SUuqzTKGGcomAct1OqNZRdGukNR82v3a", "i3YHwQUFbiuXPpnCL0LBKBSujvOM6TW6LgKhJ2s9eQ4nzyAIrn"]
        
        self.access_key = ["2692494289-7GJj6F2CdvmBtiZvcMV7YVxp3sQnDm7F62ymV0c", " 2692494289-luzf0LZlZMlEDrhnxTyvIaDPwDDI35lhxv3P3da", 
                           "2692494289-YZdJ4unEHhSW88NkJ9Y2f9mjNAMhXhcCZsmCZ0l", "2692494289-s5JWyv0aCvcQrsJbV8XMOUAoWrbpooQ92NWHzPG"]
        self.access_secret = ["ZjTgcHV8LuEIdbMU8KJxCw7kIJjtm5gU7VjwPlZWsEEaj", "iLkPAPH3q5Hl5aCQxnXdyIITcqxebcZdp9liPfaMLHhpH",
                              "KlL24At2cLzGpBYzpCmUUkj5NStnBUylL0XaPkHfU9JfD", "SP0kEeVKHb6vW9Z88veli8dMxy0PeqSuSjuopcx7FX3TZ"]
        
        self.currentNum = 0
    
    def GetAuth(self):
        self.currentNum = self.currentNum % len(self.consumer_key)
        
        auth = tweepy.OAuthHandler(self.consumer_key[self.currentNum], self.consumer_secret[self.currentNum])
        auth.set_access_token(self.access_key[self.currentNum], self.access_secret[self.currentNum])
        
        return auth