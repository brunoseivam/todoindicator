#!/usr/bin/env python
import sys, os
import gtk
import appindicator as ai
import pyinotify as pi

# Constants
FILENAME    = "todo_list"
CHECKPERIOD = 100      # 0.1 second

# Fires an action when FILENAME file changes
class EvHandler(pi.ProcessEvent):
    def __init__(self, action):
        pi.ProcessEvent.__init__(self)
        self.action = action

    def process_IN_CLOSE_WRITE(self, event):
        if event.name == FILENAME:
            self.action()

# App class
class ToDoIndicator():
    # Create needed objects and load database
    def __init__(self):
        self.items    = None
        self.wm       = pi.WatchManager()
        self.notifier = pi.Notifier(self.wm, EvHandler(self.load), timeout = 10)

        # Watch current dir
        self.wm.add_watch(".", pi.IN_CLOSE_WRITE)
        self.ind = ai.Indicator("todo-indicator", os.getcwd()+"/icon.png",\
                               ai.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(ai.STATUS_ACTIVE)

        self.load()

    # Run GTK main loop
    def run(self):
        gtk.timeout_add(CHECKPERIOD, self.check)
        gtk.main()

    # Open an editor to edit the database
    def edit(self, item):
        os.system("gedit {}&".format(FILENAME))

    # Load the database as menu items
    def load(self):
        with open(FILENAME) as f:
            rItems = [l.strip().split(";") for l in f] # RAW Items

        self.items = [[done.lower() == 'yes',desc] for done,desc in rItems]

        menu = gtk.Menu()
        for i in self.items:
            if i[0]:
                labelFmt = u"\u2611 {}" # \u2611 = checked checkbox
            else:
                labelFmt = u"\u2610 {}" # \u2610 = unchecked checkbox

            menuItem = gtk.MenuItem(labelFmt.format(i[1]))
            menuItem.refItem = i
            menuItem.connect("activate", self.click)
            menuItem.show()
            menu.append(menuItem)

        sItem = gtk.MenuItem()
        sItem.show()

        eItem = gtk.MenuItem("Edit")
        eItem.connect("activate", self.edit)
        eItem.show()

        qItem = gtk.MenuItem("Quit")
        qItem.connect("activate", self.quit)
        qItem.show()

        menu.append(sItem)
        menu.append(eItem)
        menu.append(qItem)
        self.ind.set_menu(menu)

    # Commit changes to the database
    def save(self):
        if self.items:
            with open(FILENAME, 'w') as f:
                for done,desc in self.items:
                    d = "Yes" if done else "No"
                    f.write("{};{}\n".format(d,desc))

    # Check for database changes (run periodically)
    def check(self):
        self.notifier.process_events()
        while self.notifier.check_events():
            self.notifier.read_events()
            self.notifier.process_events()
        return True

    # Toggle state of clicked item
    def click(self, item):
        item.refItem[0] = not item.refItem[0]
        self.save()

    # Exit application
    def quit(self, item):
        sys.exit(0)

if __name__ == "__main__":
    app = ToDoIndicator()
    app.run()
