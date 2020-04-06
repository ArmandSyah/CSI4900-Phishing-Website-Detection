from datetime import datetime
from elasticsearch_dsl import Document, Text, Date, Integer

class Website(Document):
    unknown_url = Text(analyzer='snowball')
    keyword = Text(analyzer='snowball')
    is_legit = Integer()

    class Index:
        name = 'website'

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)
