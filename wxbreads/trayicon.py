#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import six
import wx
import windbreads.utils as wdu

try:
    TaskBarIcon = wx.TaskBarIcon
    IconFromBitmap = wx.IconFromBitmap
    EVT_TASKBAR_LEFT_DOWN = wx.EVT_TASKBAR_LEFT_DOWN
except AttributeError:
    import wx.adv

    TaskBarIcon = wx.adv.TaskBarIcon
    IconFromBitmap = wx.Icon
    EVT_TASKBAR_LEFT_DOWN = wx.adv.EVT_TASKBAR_LEFT_DOWN


class TrayIcon(TaskBarIcon):
    restore_id = wx.NewIdRef()
    quit_id = wx.NewIdRef()

    def __init__(self, frame, icon=None, text="TrayIcon", **kwargs):
        self.t = kwargs.get("t")
        TaskBarIcon.__init__(self)
        self.frame = frame
        if icon:
            if not isinstance(icon, six.string_types):
                icon = self.make_icon(icon)

            self.SetIcon(icon, wdu.ttt(text, self.t))

        self.Bind(EVT_TASKBAR_LEFT_DOWN, self.on_restore)
        self.Bind(wx.EVT_MENU, self.on_restore, id=self.restore_id)
        self.Bind(wx.EVT_MENU, self.on_quit, id=self.quit_id)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.restore_id, wdu.ttt("Restore", self.t))
        menu.AppendSeparator()
        menu.Append(self.quit_id, wdu.ttt("Quit", self.t))
        return menu

    def make_icon(self, img):
        if "wxMSW" in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            img = img.Scale(22, 22)

        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = IconFromBitmap(img.ConvertToBitmap())
        return icon

    def on_restore(self, event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)

        if not self.frame.IsShown():
            self.frame.Show(True)

        self.frame.Raise()

    def on_quit(self, event):
        self.frame.on_quit(event)
