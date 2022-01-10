#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 10:02:51 2022

@author: nayakmurdock
"""



    
class Partners():#NOTE THAT DIFFERENT COUPLES MAY SHARE THE SAME NUMBER TO ACCOMODATE LEADS WITH MULTIPLE PARTNERS
    def __init__(self, lead, follow, number):
        self.lead = lead
        self.follow = follow
        self.number = number
    
    def getLead(self):
        return self.lead
    def getFollow(self):
        return self.follow
    def getNumber(self):
        return self.number
    

class PartnersList():
    def __init__(self):
        self.partnerList = []
    
    def addPartnersToList(self, lead, follow, number):
        try:
            self.partnerList.append(Partners.__init__(lead, follow, number))
            print("Successfully Added Parters to List")
        except: 
            print("Unsuccessfully Added Partners to List")
    
    def printPartnerList(self):
        for partners in self.partnerList:
            print("Number: " + partners.Partners.getNumber())
            print("Lead: " + partners.Partners.getLead())
            print("Follow: " + partners.Partners.getFollow())
            return partners.Partners.getNumber(), partners.Partners.getLead(), partners.Partners.getFollow()



class Event():
    def __init__(self, eventNum, category, dance, round_, competitors = [], judges = [], results = {}):
        self.eventNum = eventNum
        self.category = category
        self.dance = dance
        self.round_ = round_
        self.competitors = competitors
        self.judges = judges
        self.results = results
        
    
    def addPartnersToEvent(self, partners):#partners is an instance of Partners
        self.competitors.append(partners)
    
    def addResult(self):
        '''
        
        Add the result to the results dictionary by partners
        
        Dictionary should be structured {Partner : [List of Judges Who Called Them Back]}
        
        '''
    
    def getEventNum(self):
        return self.eventNum
    
    def getResults(self):
        return self.results
        
                
        
        
class AllEvents():
    
    def __init__(self, events = {}):
        self.events = events
    
    def addEvent(self, eventNum, category, dance, round_, competitors, judges, results):
        
        e = Event.__init__(self, eventNum, category, dance, round_, competitors, judges , results)
        
        #Still Need to add that event to the events dictionary by event number in format events{eventNum} = e
        
    def getEventByNum(self, eventNum):
        return #need to have it return the event stored in the events dictionary by its event number
    
    def inputCallbackSheetResults(self, judge, eventNum, partners):
        self.events.getEventByNum(eventNum).Event.addResult(judge, partners)
    
    def printResultsForEventNum():
        return "still need to figure out how to get an event".Event.getResults()
                
    
    
if __name__ == "__main__":
    
    allEvents = AllEvents()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    