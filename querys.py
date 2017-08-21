from connections import db

def clean_all_channels():
    map = '''function(doc){
        if(doc.Event == 'Newchannel'){
            emit(doc._id);
        }
    }'''

    result = db.query(map)

    for channel in result :
        db.delete(db[channel.id])

def clean_all_hints():
    map = '''function(doc){
        if(doc.Event == 'ExtensionStatus'){
            emit(doc._id);
        }
    }'''

    result = db.query(map)
    
    for hint in result:
        db.delete(db[hint.id])

def clean_all_queuemembers():
    map = '''function(doc){
        if(doc.Event == 'QueueMemberStatus'){
            emit(doc._id);
        }
    }'''

    result = db.query(map)

    for member in result:
        db.delete(db[member.id])

def clean_all_queueparams():
    map = '''function(doc){
        if(doc.Event == 'QueueParams'){
            emit(doc._id);
        }
    }'''

    result = db.query(map)

    for queue in result:
        db.delete(db[queue.id])
