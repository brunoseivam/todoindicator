#!/usr/bin/env python
import sys, os
import gtk
import appindicator as ai
import pyinotify as pi

# Constants
FILENAME    = "todo_list"
CHECKPERIOD = 100      # 0.1 second

class EvHandler(pi.ProcessEvent):
    def __init__(self, action):
        pi.ProcessEvent.__init__(self)
        self.action = action

    def process_IN_CLOSE_WRITE(self, event):
        if event.name == FILENAME:
            self.action()

class ToDoIndicator():
    def __init__(self):
        self.items    = None
        self.wm       = pi.WatchManager()
        self.handler  = EvHandler(self.load)
        self.notifier = pi.Notifier(self.wm, EvHandler(self.load), timeout = 10) # Msecs

        self.wm.add_watch(".", pi.IN_CLOSE_WRITE)
        self.ind = ai.Indicator("todo-list", os.getcwd()+"/icon.png",\
                               ai.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(ai.STATUS_ACTIVE)

        self.load()

    def run(self):
        gtk.timeout_add(CHECKPERIOD, self.check)
        gtk.main()

    def edit(self, item):
        os.system("gedit {}&".format(FILENAME))

    def load(self):
        with open(FILENAME) as f:
            rItems = [l.strip().split(";") for l in f]

        self.items = [[done.lower() == 'yes',desc] for done,desc in rItems]

        menu = gtk.Menu()
        for i in self.items:
            if i[0]:
                labelFmt = u"\u2611 {}"
            else:
                labelFmt = u"\u2610 {}"

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

    def save(self):
        if self.items:
            with open(FILENAME, 'w') as f:
                for done,desc in self.items:
                    d = "Yes" if done else "No"
                    f.write("{};{}\n".format(d,desc))

    def check(self):
        self.notifier.process_events()
        while self.notifier.check_events():
            self.notifier.read_events()
            self.notifier.process_events()
        return True

    def click(self, item):
        item.refItem[0] = not item.refItem[0]
        self.save()
        #print item.get_label(), item.refItem

    def quit(self, item):
        sys.exit(0)

if __name__ == "__main__":
    app = ToDoIndicator()
    app.run()
