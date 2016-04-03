
import unittest
import models


class DbTest(unittest.TestCase):

    def setUp(self):
        db = models.get_db()
        self.addCleanup(db.reset)

        transaction = db.connection.begin()
        self.addCleanup(transaction.rollback)

        self.session = db.session
        self.addCleanup(self.session.close)
