import pymongo
from info import DATABASE_URI, DATABASE_NAME

class WatermarkDB:
    def __init__(self):
        self.client = pymongo.MongoClient(DATABASE_URI)
        self.db = self.client[DATABASE_NAME]
        self.col = self.db['watermark_settings']
        
        # Create default document if it doesn't exist
        if self.col.count_documents({}) == 0:
            self.col.insert_one({
                '_id': 'settings',
                'watermark_text': '',
                'watermark_username': '',
                'file_cover': None
            })
    
    def set_watermark_text(self, text):
        """Set the watermark text to be placed at the bottom of thumbnails"""
        self.col.update_one(
            {'_id': 'settings'},
            {'$set': {'watermark_text': text}},
            upsert=True
        )
        return True
    
    def get_watermark_text(self):
        """Get the current watermark text"""
        settings = self.col.find_one({'_id': 'settings'})
        return settings.get('watermark_text', '') if settings else ''
    
    def set_watermark_username(self, username):
        """Set the watermark username to be appended to file names"""
        self.col.update_one(
            {'_id': 'settings'},
            {'$set': {'watermark_username': username}},
            upsert=True
        )
        return True
    
    def get_watermark_username(self):
        """Get the current watermark username"""
        settings = self.col.find_one({'_id': 'settings'})
        return settings.get('watermark_username', '') if settings else ''
    
    def set_file_cover(self, file_id):
        """Set the file cover (logo) to be placed on thumbnails"""
        self.col.update_one(
            {'_id': 'settings'},
            {'$set': {'file_cover': file_id}},
            upsert=True
        )
        return True
    
    def get_file_cover(self):
        """Get the current file cover (logo)"""
        settings = self.col.find_one({'_id': 'settings'})
        return settings.get('file_cover', None) if settings else None

watermark_db = WatermarkDB()