from datetime import datetime
from elasticsearch_dsl import Document, Text, Date, Boolean, Float, Keyword

class Website(Document):
    url = Keyword()
    domain = Keyword()
    hostname = Keyword()
    keyword = Keyword()
    certificate_authority_registrar = Keyword()
    date_of_creation_ca = Date()
    date_of_expiration_ca = Date()
    is_legit = Boolean()
    confidence_score = Float()

    class Index:
        name = 'website'

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)
