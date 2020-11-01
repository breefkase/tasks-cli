#!/usr/bin/python3
import json
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from supporters.settings import Settings
from supporters.database import Database
import supporters.tasks_common as task_action

"""
Resources
https://docs.python.org/3/library/tk.html
https://docs.python.org/3/library/tkinter.ttk.html
https://www.python-course.eu/tkinter_dialogs.php
"""

# TODO: Nord dark theme
nord = {
    "primary": "#88c0d0",  # nord8 Frost
    "on-primary": "#d8dee9",  # nord4 Snowstorm
    "error": "#bf616a",
    "success": "#a3be8c",
    "warning": "#d08770",
    "background": "#3B4252",  # nord1 Polar Night
}

breefkase_theme = {
    ".": {
        "configure": {
            "background": nord["background"],
            "foreground": nord["on-primary"],
            #"font": ('Helvetica', 12)
            "font": ("Monospace", 12),
        }
    },
    "TEntry": {
        "configure": {
            "fieldbackground": nord["background"],
            "fieldforeground": nord["on-primary"],
        }
    },
    "TButton": {
        "configure": {
            "padding": [9, 6],
            "relief": "raised",
        }
    },
    "TLabelframe": {
        "configure": {
            "padding": 4,
            "relief": "groove",
        }
    },
}


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Tasks")

        # Top frame
        self.top_frame = ttk.Frame(self.master, padding=(8, 12))
        self.top_frame.grid(row=0, sticky="ew")

        # Top frame - Path frame
        self.pathframe = ttk.LabelFrame(self.top_frame, text="Breefkase directory")
        self.pathframe.grid(row=0, column=0, columnspan=2)
        self.path_result_label = ttk.Label(self.pathframe, text='Path not set')
        self.path_result_label.grid(row=1, column=0, columnspan=2, sticky="w")
        path_button = ttk.Button(self.pathframe, text='Set path', command=self.path_filedialog)
        path_button.grid(row=1, column=3)

        # Center frame
        self.center_frame = ttk.Frame(self.master,  padding=(8, 12))
        self.center_frame.grid(row=1, sticky="nsew")

        # Center left
        self.center_left_frame = ttk.LabelFrame(self.center_frame, text="Actions", padding=(3, 3, 12, 12))
        self.button_task_add = ttk.Button(self.center_left_frame, text='New task', command=self.new_task)
        self.button_task_add.grid(row=0, column=0)
        self.center_left_frame.grid(row=0, column=0, sticky="ns")

        # Center mid
        self.center_mid_frame = ttk.Frame(self.center_frame, padding=(8, 12))
        # TODO: Quick 'Done' button to complete task
        self.center_mid_frame.grid(row=0, column=1, sticky="nsew")
        self.task_list_container = None

        # Center right
        self.center_right_frame = ttk.LabelFrame(self.center_frame, text="Details",
                                                 padding=(3, 3, 12, 12))
        # TODO: Create Label and Entry for title, priority
        # TODO: Create buttons: Add new if new item, or Save and Delete if existing item
        self.center_right_frame.grid(row=0, column=2, sticky="nsew")

        self.detailed = {
            "_id": StringVar(),
            "title": StringVar(),
            "priority": IntVar(),
            "filepath": StringVar(),
        }
        self.form = ttk.Frame(self.center_right_frame, padding=18)
        ttk.Label(self.form, text="Title").grid(row=0)
        self.form_title = ttk.Entry(self.form, textvariable=self.detailed["title"])
        self.form_title.grid(row=0, column=1)
        self.form_priority_frame = ttk.LabelFrame(self.form, text="Priority",
                                                  padding=(3, 3, 12, 12))
        for r in range(1, 5):
            ttk.Radiobutton(self.form_priority_frame, text=r, variable=self.detailed["priority"], value=r).pack()
        ttk.Radiobutton(self.form_priority_frame, text="None", variable=self.detailed["priority"], value=0).pack()
        self.form_priority_frame.grid(row=1, column=0)
        self.form_buttons = ttk.Frame(self.form)
        self.form_button_save = ttk.Button(self.form_buttons, text='Save', command=self.save_task)
        self.form_button_save.grid(row=0, column=0)
        self.form_button_delete = ttk.Button(self.form_buttons, text='Delete', command=self.delete_task)
        self.form_button_delete.grid(row=0, column=1)
        self.form_buttons.grid(row=2, column=1, sticky="e")
        self.form_button_save.configure(state="disabled")
        self.form_button_delete.configure(state="disabled")
        self.form.grid(row=0)

        # Menu
        self.style = ttk.Style()
        # TODO: parent inheritance does not work
        self.style.theme_create("breefkase", parent="default", settings=breefkase_theme)
        self.main_theme = StringVar()
        self.main_theme.set(self.style.theme_use())
        menubar = Menu(self.master)
        thememenu = Menu(menubar, tearoff=0)
        for themename in self.style.theme_names():
            label = themename.capitalize()
            thememenu.add_radiobutton(label=label, variable=self.main_theme, value=themename, command=self.update_theme)
        menubar.add_cascade(label="Theme", menu=thememenu)
        self.master.config(menu=menubar)

        # Initialization
        self.settings = Settings()
        self.db = None
        if self.settings.breefkase_dir:
            self.init_db(self.settings.breefkase_dir)

    def init_db(self, directory):
        self.db = Database(directory, 'tasks')
        if self.db.collection_path:
            self.path_result_label["text"] = directory
            self.get_tasks()
        else:
            self.path_result_label["text"] = 'Path not set'

    def path_filedialog(self):
        directory = filedialog.askdirectory(
            title="Select a new or existing breefkase-directory",
            mustexist=True
        )
        if directory:
            self.init_db(directory)

    def update_theme(self):
        self.style.theme_use(self.main_theme.get())

    def form_reset(self):
        s = self.detailed
        s["_id"].set("new")
        s["title"].set("")
        s["priority"].set(0)
        s["filepath"].set(False)
        self.form_button_delete.configure(state="disabled")
        self.form_button_save.configure(state="disabled")

    def new_task(self):
        self.form_reset()
        self.form_button_delete.configure(state="disabled")
        self.form_button_save.configure(state="enabled")

    def view_task(self, event=None):
        """ event= VirtualEvent"""
        # TODO: Load item from file and show in task pane
        current_item = self.tree.focus()
        print('Current item: ', current_item)
        item = self.tree.item(current_item)
        if len(item["values"]) < 2:
            self.form_reset()
            return
        filepath = item["values"][2]
        print('File path: ', filepath)
        docitem = self.db.fetchone(filepath=filepath)
        d = docitem["doc"]
        s = self.detailed
        s["current_item"] = current_item
        s["_id"].set(d["_id"])
        s["title"].set(d["title"])
        """Compensates for IntVar not able to handle None"""
        if d["priority"] is None:
            d["priority"] = 0
        s["priority"].set(d["priority"])
        s["filepath"].set(docitem["filepath"])
        self.form_button_delete.configure(state="enabled")
        self.form_button_save.configure(state="enabled")

    def save_task(self):
        s = self.detailed
        entry = {}
        for x in ["_id", "title", "priority", "filepath"]:
            entry[x] = s[x].get()
        task_action.save_task(entry, self.db)
        self.form_reset()
        self.get_tasks()

    def delete_task(self):
        self.db.delete(self.detailed["filepath"])
        self.tree.detach(self.detailed["current_item"])
        self.form_reset()
        self.get_tasks()  # Temporary solution to avoid remaining items, until items are updated ad-hoc

    def set_tasks_none(self):
        self.task_list_container.destroy()

    def get_tasks(self):
        # TODO: Refactor. Define task_list_container & tree at class init. At get_tasks, empty tree
        if self.task_list_container:
            self.task_list_container.destroy()
        self.task_list_container = ttk.Frame(self.center_mid_frame)
        self.task_list_container.grid(row=0, column=0, columnspan=2)  # sticky="nw"

        self.tree = ttk.Treeview(self.task_list_container)
        self.tree["columns"] = ("Title", "Due", "Status")
        self.tree.column("#0", width=370, minwidth=270)
        for index, value in enumerate(self.tree["columns"]):
            self.tree.heading(f'#{index}', text=value)
        self.tree["displaycolumns"] = ("0", "1")

        docs = self.db.fetchall()

        def insert_into(task_array, folder_name, tags=None):
            if len(task_array):
                parent_folder = self.tree.insert(
                    "",
                    END,
                    iid=folder_name,
                    open=True,  # TODO: Fix open=true on due only
                    text=f"{folder_name} ({len(task_array)})"
                )
                for item in task_array:
                    doc = item["doc"]
                    self.tree.insert(
                        parent_folder,
                        END,
                        text=doc["title"],
                        values=(
                            doc["due"],
                            doc["status"],
                            item["filepath"],
                            json.dumps(doc)
                        ),
                        tags=tags  # TODO: Fix tags
                    )

        due = task_action.filter_today(docs)
        insert_into(due, "Due today & overdue", tags="due")

        # TODO: Implement pri 1-4, and None
        pri1 = task_action.filter_priority(docs, 1)
        insert_into(pri1, "Priority 1", tags="pri1")

        pri_none = task_action.filter_priority(docs, None)
        insert_into(pri_none, "No Priority", tags="pri_none")

        self.tree.tag_configure('due', foreground='red')
        self.tree.tag_configure('pri1', foreground='orange')

        self.tree.bind('<<TreeviewSelect>>', self.view_task)
        self.tree.grid(row=0)


def main():
    root = Tk()

    """Checks if user has Python > 3.5 due to pathlib"""
    if sys.version_info >= (3, 5):
        app = MainWindow(root)
    else:
        root.title('Tasks')
        frame = ttk.Frame(root, padding=12)
        frame.grid(row=0)
        ttk.Label(frame, text="Dangit!", font=50).grid(row=0)
        ttk.Label(frame, text="Python 3.5 or greater required.").grid(row=1)
        ttk.Button(frame, text="Close", command=root.destroy).grid(row=2, pady=6)
    root.eval('tk::PlaceWindow . center')
    root.mainloop()


if __name__ == '__main__':
    # TODO: HOLD: Create settings class, creating a global settings object
    main()
