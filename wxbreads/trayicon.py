#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import wx
import windbreads.utils as wdutils


class TrayIcon(wx.TaskBarIcon):
    tbmenu_restore = wx.NewId()
    tbmenu_quit = wx.NewId()

    def __init__(self, frame, icon=None, text='TrayIcon', **kwargs):
        self.t = kwargs.pop('t', None)
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        if icon:
            if not isinstance(icon, basestring):
                icon = self.make_icon(icon)

            self.SetIcon(icon, wdutils.tr_text(text, self.t))

        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_tb_activate)
        self.Bind(wx.EVT_MENU, self.on_tb_activate, id=self.tbmenu_restore)
        self.Bind(wx.EVT_MENU, self.on_tb_quit, id=self.tbmenu_quit)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.tbmenu_restore, wdutils.tr_text('Restore', self.t))
        menu.AppendSeparator()
        menu.Append(self.tbmenu_quit, wdutils.tr_text('Quit', self.t))
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
