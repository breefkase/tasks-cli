import datetime


class TaskItem:
    """
    A task item

    ...

    Requires a docid and a database object from database.py
    If creating a new document, use "new" as docid argument
    """
    def __init__(self, docid, database_object):
        self.db = database_object
        self.docitem = self.db.fetchone(docid=docid)
        self.doc = self.docitem["doc"]

    def cancel(self):
        self.end("cancelled")

    def done(self):
        self.end()

    def end(self, status="done"):
        """
        Used by def cancel() and done().
        Defaults to "done"
        :return:
        """
        d = self.doc
        d["status"] = status
        d["end"] = datetime.datetime.now().isoformat()
        self.db.insert(self.docitem)
