from kraken_db import kraken_db as db

class Kraken_db:

    def __init__(self, db_path = None):

        self.db_path = db_path
        self.conn = db.init(self.db_path)
        
        
    def list_record_types(self):
        """
        Returns list of record_types
        """

        return db.list_record_types(self.conn)
    

    def search(self, params, order_by = None, order_direction = None, limit = 100, offset = 0):
        """
        Search
        Returns observations
        """

        return db.search(self.conn, params, order_by, order_direction, limit, offset)
    
    
   
        
    def post(self, records):
        """
        """
        
        return db.post(self.conn, records)


    def get(self, record_type=None, record_id=None, key=None, value=None):
        """
        """

        return db.get(self.conn, record_type, record_id, key, value)
    

    def get_summary(self, record_type=None, record_id=None, key=None, value=None):
        """
        """

        return db.get_summary(self.conn, record_type, record_id, key, value)

    def rollback(self):
        """
        Support for legacy. Does nothing
        """
        return
        
    def commit(self):
        """
        Support for legacy. Does nothing
        """
        return

    def get_observations(self, params, order_by = None, order_direction = None, limit = 100, offset = 0):
        """
        Search
        Returns observations
        """

        return db.get_observations(self.conn, params, order_by, order_direction, limit, offset)
    
    