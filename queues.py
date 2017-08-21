from connections import mydb

def parse_queuemember_event(func):
    def func_wrapper(self, event, **kwargs):
        status_dict = {
            '0' : 'unknown',
            '1' : 'notInUse',
            '2' : 'inUse',
            '3' : 'busy',
            '4' : 'invalid',
            '5' : 'unavailable',
            '6' : 'ringing',
            '7' : 'ringInUse',
            '8' : 'onHold'
        }
      
        if 'Name' in event.keys:
            event.keys['MemberName'] = event.keys['Name']

        event.keys['Event'] = 'QueueMemberStatus'
        event.keys['Status'] = status_dict[event.keys['Status']]
        event.keys['Paused'] = True if event.keys['Paused'] == '1' else False
        event.keys['InCall'] = True if event.keys['InCall'] == '1' else False

        try:
            for agent in mydb['agent']:
                if str(agent['username']) == event.keys['MemberName']:
                    event.keys['AgentName'] = agent['name']
    
            if event.keys['Paused']:
                for pause in mydb['pause']:
                    if str(pause['code']) == event.keys['PausedReason'].split('-')[0]:
                           event.keys['PauseTitle'] = pause['title']
        except Exception, e:
            print str(e)
    
        return func(self, event, **kwargs)

    return func_wrapper
