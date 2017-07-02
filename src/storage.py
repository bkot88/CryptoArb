
import couchdb
import time
from threading import Thread

class RelaxedCouch:

    def __init__(self, db_name, user, pw, host='localhost', port=5984):
        url = 'http://{}:{}@{}:{}/'.format(user,pw,host,port)
        self.server = couchdb.Server(url)
        self.db_name = db_name
        if self.db_name in self.server:
            self.db = self.server[db_name]
            self.db.cleanup()
            self.db.compact()
        else:
            print self.db_name, 'is not in the couchdb'
            self.db = self.server.create(db_name)
            print 'created', db_name
        print 'time to relax...'

    def async_save(self, doc):
        '''
        asynchronous save version of a document. see the documentation
        for save.
        '''
        Thread(target=self.save, args=(doc,)).start()

    def save(self, doc):
        '''
        document must conform to standard. expected fields are:
        ['ticker','ask','bid','exchange','channel']. if fields are missing
        the method returns None. otherwise, a key and timestamp will be
        created if they are not present. It will return None if the db
        already contains the document id.
        '''
        fields = ['ticker','ask','bid','exchange','channel']
        if not all(k in doc for k in fields):
            return None
        ts = int(time.time())
        if '_id' not in doc:
            doc['_id'] = '({},{})'.format(ts, doc['ticker'])
        if 'timestamp' not in doc:
            doc['timestamp'] = ts
        
        # try and save the document
        if doc['_id'] not in self.db:
            print self.db.save(doc)
            print ''
        else:
            print 'conflict, document in db already'
            print ''
