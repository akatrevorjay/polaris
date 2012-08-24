#!/usr/bin/env python

import sys
import os
import time
from datetime import datetime
import gobject
import dbus
import dbus.service
import unicodedata

import dzen
import util

def fill_ro(string):
    return string.replace("^ro", "^r")


class PolarisManager(dbus.service.Object):
    def __init__(self, config, dzen2_pipe):
        global pid

        bus_name = dbus.service.BusName('org.polaris.service', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/polaris/service')
        import wnck

        self.config = config
        self.WORKSPACES_NFG = config["Workspaces"]["normal"]["fg"]
        self.WORKSPACES_NBG = config["Workspaces"]["normal"]["bg"]
        self.WORKSPACES_AFG = config["Workspaces"]["active"]["fg"]
        self.WORKSPACES_ABG = config["Workspaces"]["active"]["bg"]
        self.TASKS_NFG = config["Tasks"]["normal"]["fg"]
        self.TASKS_NBG = config["Tasks"]["normal"]["bg"]
        self.TASKS_AFG = config["Tasks"]["active"]["fg"]
        self.TASKS_ABG = config["Tasks"]["active"]["bg"]
        self.TASKS_IFG = config["Tasks"]["iconiz"]["fg"]
        self.TASKS_IBG = config["Tasks"]["iconiz"]["bg"]
        self.CLOCK_FG = config["Clock"]["fg"]
        self.CLOCK_FORMAT = config["Clock"]["strftime"]

        self.dzen2_pipe = dzen2_pipe
        #gobject.timeout_add(10000, self.dzen2_pipe.is_running)

        self.screen = wnck.screen_get_default()
        self.screen.force_update()
        self.screen.connect("active-workspace-changed", self.get_workspaces)
        self.screen.connect("workspace-created", self.get_workspaces)
        self.screen.connect("workspace-destroyed", self.get_workspaces)
        self.screen.connect("active-window-changed", self.get_windows)
        self.screen.connect("window-opened", self.get_windows)
        self.screen.connect("window-closed", self.get_windows)
        self.screen.connect

        self.last_event = 0
        self.get_workspaces()
        self.get_windows()
        self.get_time()
        #self.output_dzen_line()
        gobject.timeout_add(10000, self.get_time)

    def get_workspaces(self, *args):
        def nfg(workspace):
            return "^fg(" + self.WORKSPACES_NFG + ")" + workspace + "^fg()"
        def nbg(workspace):
            return "^bg(" + self.WORKSPACES_NBG + ")" + workspace + "^bg()"
        def afg(workspace):
            return workspace.replace("^fg(" + self.WORKSPACES_NFG, "^fg(" + self.WORKSPACES_AFG)
        def abg(workspace):
            return workspace.replace("^bg(" + self.WORKSPACES_NBG, "^bg(" + self.WORKSPACES_ABG)
        def ca_workspace(workspace_label, workspace_number):
            return "^ca(1, polaris.py -w " + str(workspace_number) + ")" + workspace_label + "^ca()"

        wm_workspaces = self.screen.get_workspaces()
        wm_windows = self.screen.get_windows()
        workspaces = {}
        active_ws = self.screen.get_active_workspace()
        active_ws_num = active_ws.get_number()
        for ws in wm_workspaces:
            ws_num = ws.get_number()

            ws_in_use = ws_num == active_ws_num
            if not ws_in_use:
                for win in wm_windows:
                    win_ws = win.get_workspace()
                    win_ws_num = win_ws.get_number()

                    if win.is_skip_tasklist() or ws_num != win_ws_num:
                        continue

                    ws_in_use = True
                    break

            ws.connect("name-changed", self.get_workspaces)
            if ws_in_use:
                workspaces[ws_num] = ca_workspace(nbg(nfg("^p(;2)^ro(4x4)^p(;-2) " + ws.get_name() + " ")), ws_num)
        workspaces[active_ws_num] = fill_ro(abg(afg(workspaces[active_ws_num])))
        self.workspaces = " ".join([ x[1] for x in sorted(workspaces.iteritems()) ]) + "^p()"
        #self.get_windows()
        if args:
            self.output_dzen_line()

    # we must forbid too fast window name changes
    # TODO: make it work HONESTLY
    def filter_name_change(self, *args):
        event_time = time.time()
        delta = event_time - self.last_event
        self.last_event = event_time
        if delta >= 1:
            self.get_windows(True)

    def get_windows(self, *args):
        def nfg(task):
            return "^fg(" + self.TASKS_NFG + ")" + task + "^fg()"
        def nbg(task):
            return "^bg(" + self.TASKS_NBG + ")" + task + "^bg()"
        def ifg(task):
            return task.replace("^fg(" + self.TASKS_NFG, "^fg(" + self.TASKS_IFG)
        def ibg(task):
            return task.replace("^fg(" + self.TASKS_NBG, "^fg(" + self.TASKS_IBG)
        def afg(task):
            return task.replace("^fg(" + self.TASKS_NFG, "^fg(" + self.TASKS_AFG)
        def abg(task):
            return task.replace("^bg(" + self.TASKS_NBG, "^bg(" + self.TASKS_ABG)
        def ca_task(task, uniq):
            return " ^ca(1, polaris.py -t " + uniq + ")" + task + "^ca() "
        self.windows = ""
        workspaces = self.screen.get_workspaces()
        windows = self.screen.get_windows()
        if windows != None:
            windows_workspaces_dict = {}
            for workspace in workspaces:
                windows_workspaces_dict[workspace.get_name()] = []
            for window in windows:
                if not window.is_skip_tasklist():
                    window_workspace = window.get_workspace()
                    window_workspace_name = window_workspace.get_name()
                    if window_workspace != None:
                        if not window_workspace_name in windows_workspaces_dict:
                            windows_workspaces_dict[window_workspace_name] = []
                        windows_workspaces_dict[window_workspace.get_name()].append(window)
                    else:
                        if window.is_sticky() or self.screen.get_window_manager_name() == "Openbox":
                            for workspace in windows_workspaces_dict:
                                windows_workspaces_dict[workspace].append(window)

            cw_window_full_names = []
            active_workspace = self.screen.get_active_workspace().get_name()
            count = 0
            for window in windows_workspaces_dict[active_workspace]:
                window.connect("name-changed", self.filter_name_change)
                window_full_name = unicode(window.get_name())
                window_name = window_full_name
                if len(window_full_name) > 30:
                    window_name = window_full_name[:29] + u"\u2026"
                cw_window_full_names.append(ca_task(nbg(nfg("^ro(3x3)  " + window_name)), str(window.get_xid())))
                if window.is_minimized():
                    cw_window_full_names[count] = ibg(ifg(cw_window_full_names[count]))
                self.active_window = self.screen.get_active_window()
                if self.active_window != None:
                    if window_full_name == self.active_window.get_name():
                        cw_window_full_names[count] = fill_ro(abg(afg(cw_window_full_names[count])))
                        self.windows = "  ".join([cw_window_full_names[count]])
                count = count + 1
                #self.windows = "  ".join(cw_window_full_names)
                #self.windows = "  ".join([cw_window_full_names[count]])
        else:
            self.windows = ""
        if args:
            self.output_dzen_line()

    def get_time(self, *args):
        self.time = "^fg("+ self.CLOCK_FG + ")" + datetime.now().strftime(self.CLOCK_FORMAT) + "^fg()"
        self.output_dzen_line()
        return True

    def output_dzen_line(self, *args):
        def strip_accents(s):
           return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

        format_data = {}
        for i in ['workspaces', 'windows', 'time']:
            format_data[i] = getattr(self, i)
        dzen2_line = unicode('^p(2)^p(5){workspaces}^p(2)^fg(#808080)^r(1x5)^fg()^p(6){windows}^p(5){time}'.format(**format_data))

        dzen2_line = strip_accents(dzen2_line) #this way, we can use any font we like, even if it doesn't have accents
        try:
            self.dzen2_pipe.stdin.write(dzen2_line + "\n")
        except:
            print "broken pipe?"

    @dbus.service.method('org.polaris.service')
    def toggle_window(self, window_xid):
        cw = self.screen.get_active_workspace()

        cw_windows = [ window for window in self.screen.get_windows()]
        for cw_window in cw_windows:
            if str(cw_window.get_xid()) == window_xid:
                if cw_window.is_minimized():
                    cw_window.unminimize(0)
                    return True
                else:
                    if cw_window.is_active():
                        cw_window.minimize()
                        return True
                    else:
                        cw_window.activate(0)
                        return True
        return False

    @dbus.service.method('org.polaris.service')
    def switch_workspace(self, workspace_number):
        workspaces = self.screen.get_workspaces()
        cw = self.screen.get_active_workspace().get_number()
        for workspace in workspaces:
            if workspace.get_number() == int(workspace_number) != cw:
                workspace.activate(1)
                return True
            elif workspace.get_number() == int(workspace_number) == cw:
                self.screen.toggle_showing_desktop(not self.screen.get_showing_desktop())
                return True
        return False
