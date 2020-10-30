import argparse
import datetime
import sys

from supporters.settings import Settings
from supporters.database import Database
import supporters.tasks_common as task_action
from supporters.taskitem import TaskItem

# TODO: parser.add_argument("-tom", "--tomorrow", help="tomorrow")


def initialization(breefkase_dir):
    database = Database(breefkase_dir, 'tasks')
    if not database.collection_path:
        print("No database directory in settings")
    retries = 5
    while not database.collection_path:
        retries -= 1
        if not retries:
            sys.exit("Database path could not be established")
        breefkase_dir = input("Enter full path:")
        if not len(breefkase_dir):
            continue
        database = Database(breefkase_dir, 'tasks')
    return database


settings = Settings()
db = initialization(settings.breefkase_dir)


"""
Common functions
"""


def print_doc(doc):
    print("-" * 16)
    print("ID\n", doc["_id"])
    print("Status\n", doc["status"])
    if doc.get("end", None):
        print("Ended\n", doc["end"])
    else:
        print("Due\n", doc["due"])
    print("Title\n", doc["title"])


def print_docs(docs):
    for docitem in docs:
        print_doc(docitem["doc"])


def today(*args):
    docs = db.fetchall()
    docs = task_action.filter_today(docs)
    print_docs(docs)
    print(8*"*")
    print(len(docs), " tasks")


def add(*args):
    print(10 * "-")
    title = input('Task text:')
    entry = {
        "_id": "new",
        "title": title,
        "due": datetime.datetime.now().isoformat(),
        "priority": None,
    }
    result = task_action.save_task(entry, db)
    if result:
        print("Inserted: ", title)


def cancel(args):
    task = TaskItem(args.id, db)
    task.cancel()
    print(f"Task {args.id} marked as cancelled")


def done(args):
    task = TaskItem(args.id, db)
    task.done()
    print(f"Task {args.id} marked as done")


def view(args):
    try:
        docid = args.id
        task = TaskItem(docid, db)
        print_doc(task.doc)
    except KeyError:
        print(f"Could not find id {docid}")


"""
Parser
"""
parser = argparse.ArgumentParser(
    prog='breefkase CLI Interface',
    usage='%(prog)s [options] path. -h for help',
    description='Interface for interacting with a breefkase directory',
    epilog='Enjoy the program! :)')
parser.add_argument("-m", "--menu", help="CLI-interface w/menu")

subparsers = parser.add_subparsers()

parser_today = subparsers.add_parser('today',
                                     aliases=['tod'],
                                     help='Today and overdue tasks')
parser_today.set_defaults(func=today)
parser_add = subparsers.add_parser('add',
                                   aliases=['new', 'create'],
                                   help='Add new task')
parser_add.set_defaults(func=add)
# TODO: Ineffective parsing. Combine cancel and done
parser_cancel = subparsers.add_parser('cancel', help='Mark task as cancelled. Takes --id argument')
parser_cancel.add_argument('-i', '--id', default=None, help="Task ID")
parser_cancel.set_defaults(func=cancel)
parser_done = subparsers.add_parser('done', help='Mark task as done. Takes --id argument')
parser_done.add_argument('-i', '--id', default=None, help="Task ID")
parser_done.set_defaults(func=done)
parser_view = subparsers.add_parser('view', help='View task. Takes --id argument')
parser_view.add_argument('-i', '--id', default=None, help="Task ID")
parser_view.set_defaults(func=view)


def menu():
    print("Work in progress. Tasks CLI Menu")


def main():
    if len(sys.argv) <= 1:
        sys.argv.append('--help')
    print("Running Tasks CLI Argument Parser")
    print(16*">")
    args = parser.parse_args()
    args.func(args)
