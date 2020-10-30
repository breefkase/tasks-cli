import datetime

date_tomorrow = datetime.date.today() + datetime.timedelta(days=1)
date_tomorrow_iso = date_tomorrow.isoformat()


def filter_today(docs):
    returned_array = []
    for doc in docs:
        d = doc["doc"]
        # TODO: If due less than tomorrow
        if d["due"] and d["due"] < date_tomorrow_iso:
            if d["status"] not in ["done", "cancelled"]:
                returned_array.append(doc)
    return returned_array


def filter_priority(docs, priority):
    returned_array = []
    for doc in docs:
        d = doc["doc"]
        # TODO: If due less than tomorrow
        if d["priority"] == priority:
            returned_array.append(doc)
    return returned_array


def save_task(entry, db_object):
    """
    In Tasks GUI - Passes self.detailed
    Prepares document for saving to database
    If _id == 'new', a new document will be created, with a generated UUID
    :param entry:
    :param db_object:
    :return:
    """
    pri = entry["priority"]
    if pri == 0:
        pri = None
    entry_id = entry["_id"]
    if entry_id == "new":
        """If _id is 'new', a new UUID will be generated, and a new file created"""
        new_task_template = {
            "_id": entry_id,
            "productivity": True,
            "type": "task",
            "due": entry.get("due", None),
            "start": datetime.datetime.now().isoformat(),
            "end": None,
            "title": entry["title"],
            "description": None,
            "created": datetime.datetime.now().isoformat(),
            "status": "plan",
            "project": None,  # Must be projectID _id
            "context": None,
            "priority": pri,
            "tags": []
        }
        docitem = {
            "doc": new_task_template
        }
    else:
        fp = entry["filepath"]
        docitem = db_object.fetchone(filepath=fp)
        doc = docitem["doc"]
        doc["title"] = entry["title"]
        doc["priority"] = pri
    db_object.insert(docitem)
    return docitem
