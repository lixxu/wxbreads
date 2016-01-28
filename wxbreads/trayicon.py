#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import wx


class TrayIcon(wx.TaskBarIcon):
    tbmenu_restore = wx.NewId()
    tbmenu_quit = wx.NewId()

    def __init__(self, frame, icon=None, text='TrayIcon'):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        if icon:
            if not isinstance(icon, basestring):
                icon = self.make_icon(icon)

            self.SetIcon(icon, text)

        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_tb_activate)
        self.Bind(wx.EVT_MENU, self.on_tb_activate, id=self.tbmenu_restore)
        self.Bind(wx.EVT_MENU, self.on_tb_quit, id=self.tbmenu_quit)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.tbmenu_restore, 'Restore')
        menu.AppendSeparator()
        menu.Append(self.tbmenu_quit, 'Quit')
        return menu

    def make_icon(self, img):
        if 'wxMSW' in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif 'wxGTK' in wx.PlatformInfo:
            img = img.Scale(22, 22)

        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = wx.IconFromBitmap(img.ConvertToBitmap())
        return icon

    def on_tb_activate(self, event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)

        if not self.frame.IsShown():
            self.frame.Show(True)

        self.frame.Raise()

    def on_tb_quit(self, event):
        self.frame.on_quit(event)
