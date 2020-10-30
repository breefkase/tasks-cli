import datetime
import uuid
from pathlib import Path
import json
from supporters.settings import Settings


def make_docitem(filepath):
    """
    Requires Pathlib object. I.E. Posixpath <class 'pathlib.PosixPath'>
    :param filepath:
    :return:
    """
    # TODO: Send to log if parsing JSON fails, informing user of an incorrectly formatted/corrupt/broken document
    docitem = {
        "filepath": filepath,
        "filename": filepath.name,
        "doc": {},
    }
    try:
        with open(filepath, 'r') as file:
            file_contents = file.read()
            docitem["doc"] = json.loads(file_contents)
    except Exception as error:
        docitem["doc"] = {
            "title": "File could not be loaded",
            "due": None,
            "priority": None,
            "status": "plan",
            "error": str(error),
        }
    return docitem


class Database:
    """
    collection - the collection name, I.E. 'tasks' results in yourdir/database/tasks
    """
    def __init__(self, proposed_breefkase_dir, collection_name=None):
        self.breefkase_dir = None
        self.collection_name = collection_name
        self.collection_path = None

        self.verify_breefkase_dir(proposed_breefkase_dir)

        if self.breefkase_dir and self.collection_name:
            self.verify_collection(collection_name)

    def verify_breefkase_dir(self, proposed_breefkase_dir):
        print("Verifying breefkase directory")
        # TODO parse/validate directory
        # TODO create dir 'database' if not exists
        # TODO create dir 'database/tasks' if not exists
        try:
            bp = Path(proposed_breefkase_dir)
            if Path.is_dir(bp):
                self.breefkase_dir = bp
                print("Database directory validated")
                settings = Settings()
                if str(self.breefkase_dir) != settings.config.get("breefkaseDir", None):
                    settings.config["breefkaseDir"] = str(self.breefkase_dir)
                    settings.save()
        except TypeError as te:
            print("Invalid directory path. Try using full path, I.E. /home/user/mystuff. Error: ", te)

    def verify_collection(self, collection_name):
        # TODO break on invalid breefkase_dir (None)
        if self.breefkase_dir:
            try:
                collection_path = Path(self.breefkase_dir).joinpath('database', collection_name)
                collection_path.mkdir(parents=True, exist_ok=True)
                self.collection_path = collection_path
                print("Collection verified")
            except Exception as error:
                print(f'Something went wrong when verifying collection {collection_name}: {error}')

    def fetchall(self):
        docs = []
        for filepath in self.collection_path.iterdir():
            name = filepath.name
            if name.endswith(".json"):
                docitem = make_docitem(filepath)
                docs.append(docitem)
        return docs

    def fetchone(self, filepath=None, docid=None):
        """
        TODO: If necessary, implement docitem=None, doc=None
        :param docid: Document ID (_id)
        :param filepath: Full path to file - I.E. /home/user/breefkase/database/tasks/1234-4321-abcd-dcba.json
        :return:
        """
        if docid:
            filepath = Path(self.collection_path).joinpath(f'{docid}.json')
        new_docitem = None
        if filepath:
            if type(filepath) is str:
                filepath = Path(filepath)
            new_docitem = make_docitem(filepath)
        return new_docitem

    def insert(self, docitem):
        if docitem["doc"]["_id"] == "new":
            new_id = str(uuid.uuid4())
            docitem["doc"]["_id"] = new_id
            docitem["filepath"] = Path(self.collection_path).joinpath(f'{new_id}.json')
        else:
            docitem["doc"]["updated"] = datetime.datetime.now().isoformat()

        with open(docitem["filepath"], "w") as f:
            doc_json = json.dumps(docitem["doc"], indent=4, sort_keys=True, ensure_ascii=False)
            f.write(doc_json)

    def delete(self, filepath):
        filepath = filepath.get()
        print("Deleted doc: ", filepath)
        filepath = Path(filepath)
        filepath.unlink()
