import time
import couchdb

from config import config
from utils import create_log_directory, error_log, access_log, parse_event
from queues import parse_queuemember_event
from querys import clean_all_channels, clean_all_hints, clean_all_queuemembers,\
     clean_all_queueparams
from asterisk.ami import EventListener, SimpleAction, AMIClient
from datetime import datetime
from connections import db

class UrdEventListener(EventListener):
    @staticmethod
    def __update_queue_member(event):
        try:
            doc = db[event['MemberName']]
            doc.update(event)
            db.save(doc)
        except couchdb.http.ResourceNotFound:
            db[event['MemberName']] = event
        except Exception, e:
            error_log("UPDATEQUEUEMEMBER " + str(type(e).__name__))

    @parse_event
    def on_FullyBooted(self, event, **kwargs):
        clean_all_queueparams()
        clean_all_channels()
        clean_all_hints()
        clean_all_queuemembers()

        [ami.send_action(SimpleAction(i)) for i in ('CoreShowChannels', 
            'ExtensionStateList', 'QueueStatus')]

    def on_UserEvent(self, event, **kwargs):
        pass

    @parse_event
    def on_Newchannel(self, event, **kwargs):
        event = event.keys
        channel = event['Channel'].lower()

        try:
            db[channel] = event
        except Exception, e:
            error_log("NEWCHANNEL " + str(type(e).__name__))
            pass

    @parse_event
    def on_CoreShowChannel(self, event, **kwargs):
        event = event.keys
        event['Event'] = 'Newchannel'
        channel = event['Channel'].lower()

        try:
            db[channel] = event
        except couchdb.http.ResourceConflict:
            doc = db[channel]
            doc.update(event)
            db.save(doc)
            pass
        except Exception, e:
            error_log("CORESHOWCHANNEL " + str(type(e).__name__))
            pass

    @parse_event
    def on_Hangup(self, event, **kwargs):
        event = event.keys
        channel = event['Channel'].lower()

        try:
            doc = db[channel]
            db.delete(doc)
        except Exception, e:
            error_log("HANGUP " + str(type(e).__name__))
            pass

    @parse_event
    def on_Newstate(self, event, **kwargs):
        event = event.keys
        event['Event'] = 'Newchannel'
        channel = event['Channel'].lower()
        
        try:
            doc = db[channel]
            doc.update(event)
            db.save(doc)
        except couchdb.http.ResourceNotFound:
            db[channel] = event
        except Exception, e:
            error_log("NEWSTATE " + str(type(e).__name__))
            pass

    @parse_event
    def on_ExtensionStatus(self, event, **kwargs):
        event = event.keys
        hint = event['Hint'].lower()

        try:
            db[hint] = event
        except couchdb.http.ResourceConflict:
            doc = db[hint]
            doc.update(event)
            db.save(doc)
        except Exception, e:
            error_log("EXTENSIONSTATUS " + str(type(e).__name__))
            pass

    @parse_event
    @parse_queuemember_event
    def on_QueueMemberAdded(self, event, **kwargs):
        event = event.keys
        event['Event'] = 'QueueMemberStatus'
        member = event['MemberName']

        try:
            db[member] = event
        except couchdb.http.ResourceConflict:
            self.__update_queue_member(event)
        except Exception, e:
            error_log("QUEUEMEMBERADDED " + str(type(e).__name__))
            pass

    @parse_event
    @parse_queuemember_event
    def on_QueueMemberPause(self, event, **kwargs):
        event = event.keys

        try:
            self.__update_queue_member(event)
        except Exception, e:
            error_log("QUEUEMEMBERPAUSE " + str(type(e).__name__))
            pass

    @parse_event
    @parse_queuemember_event   
    def on_QueueMemberRemoved(self, event, **kwargs):
        event = event.keys
        member = event['MemberName']

        try:
            doc = db[member]
            db.delete(doc)
        except Exception,e:
            error_log("QUEUEMEMBERREMOVED " + str(type(e).__name__))            
            pass

    @parse_event
    @parse_queuemember_event
    def on_QueueMemberRinginuse(self, event, **kwargs):
        event = event.keys

        try:
            self.__update_queue_member(event)
        except Exception, e:
            error_log("QUEUEMEMBERRINGINUSE " + str(type(e).__name__))
            pass
    
    @parse_event
    @parse_queuemember_event
    def on_QueueMemberStatus(self, event, **kwargs):
        event = event.keys

        try:
            self.__update_queue_member(event)
        except Exception, e:
            error_log("QUEUEMEMBERSTATUS " + str(type(e).__name__))
            pass
    
    @parse_event
    @parse_queuemember_event
    def on_QueueMember(self, event, **kwargs):
        event = event.keys
        member = event['Name']

        try:
            db[member] = event
        except couchdb.http.ResourceConflict:
            self.__update_queue_member(event)
        except Exception, e:
            error_log("QUEUEMEMBER " + str(type(e).__name__))
    
    @parse_event
    def on_QueueParams(self, event, **kwargs):
        event = event.keys
        queue = event['Queue']
        
        try:
            db[queue] = event
        except couchdb.http.ResourceConflict:
            doc = db[queue]
            doc.update(event)
            db.save(doc)
        except Exception, e:
            error_log("QUEUEPARAMS " + str(type(e).__name__))
            pass
    
    @parse_event
    def on_QueueSummary(self, event, **kwargs):
        event = event.keys
        event['Event'] = 'QueueParams'
        queue = event['Queue']

        try:
            db[queue] = event
        except couchdb.http.ResourceConflict:
            doc = db[queue]
            doc.update(event)
            db.save(doc)
        except Exception, e:
            error_log("QUEUESUMMARY " + str(type(e).__name__))
   
    @parse_event
    def on_QueueCallerJoin(self, event, **kwargs):
        for action in ('QueueStatus','QueueSummary'):
            ami.send_action(SimpleAction(action, Queue = event.keys['Queue']))

    @parse_event
    def on_QueueCallerLeave(self, event, **kwargs):
        try:
            self.on_QueueCallerJoin(event, **kwargs)
            pass
        except Exception, e:
            error_log("CALLERLEAVE " + str(type(e).__name__))
            pass


if __name__ == '__main__':
    create_log_directory()

    try:
        ami = AMIClient(address=config['manager_address'], port=int(config['manager_port']))
        ami.add_event_listener(UrdEventListener())
        access_log("LISTENING EVENTS")

        ami.login(username=config['manager_user'], secret=config['manager_password'])
    except Exception, e:
        error_log("AMI CONNECTION " + str(e))
    
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        ami.logoff()
    except Exception, e:
        print str(e) 
        ami.logoff()
        raise
