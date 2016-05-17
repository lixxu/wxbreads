#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import wx
import windbreads.utils as wdu
import wxbreads.utils as wxu
import wxbreads.images as wxi
import wxbreads.widgets as wxw


class BaseWindow(wx.Frame):
    clock_timer_id = wx.NewId()
    echo_timer_id = wx.NewId()
    root_pass = 'guess'
    app_version = '0.1'
    app_name = 'Cool App'
    app_remark = 'Description for cool app'
    app_author = ''

    def __init__(self, **kwargs):
        title = '{} - {}'.format(self.app_name, self.app_version)
        super(BaseWindow, self).__init__(kwargs.get('parent'),
                                         size=kwargs.get('size', (-1, -1)),
                                         title=title)
        self.is_running = False
        self.echo_lines = []
        self.is_echoing = False
        self.t = None
        self.has_tray = False
        self.logo = img = wxi.logo.GetImage()
        icon = wx.IconFromBitmap(img.ConvertToBitmap())
        self.SetIcon(icon)
        self.sb_count = len(self.get_sb_width())
        self.setup_statusbar()
        self.Bind(wx.EVT_CLOSE, self.on_quit)

    def show(self):
        self.Centre(wx.BOTH)
        self.Show()

    def setup_timers(self, clock_ms=1000, echo_ms=200):
        self.clock_timer = wxw.init_timer(self, self.clock_timer_id,
                                          self.on_clock_tick, clock_ms)
        self.echo_timer = wxw.init_timer(self, self.echo_timer_id,
                                         self.on_echoing, echo_ms)
        self.all_timers = [self.clock_timer, self.echo_timer]

    def stop_timers(self):
        wxu.stop_timers(self.all_timers)

    def on_clock_tick(self, evt=None):
        wxu.update_clock_statusbar(self.sbar, idx=self.sb_count - 1))

    def setup_statusbar(self):
        self.sbar = wxw.init_statusbar(self, widths=self.get_sb_width(),
                                       values=self.get_sb_value())

    def get_sb_width(self):
        """Width items for status bar."""
        return [230, -1, 120]

    def get_sb_value(self):
        """Value items for status bar."""
        return [self.get_copyright(), '', '']

    def get_copyright(self):
        return wdu.get_copy_right()

    def update_status(self, text, idx, **kwargs):
        kwargs.setdefault('t', self.t)
        wxu.set_status_text(self.sbar, text, idx, **kwargs)

    def setup_tray(self, **kwargs):
        import wxbreads.trayicon as wxt
        try:
            args = dict(icon=kwargs.get('icon') or self.logo,
                        text=kwargs.get('text', self.app_name),
                        t=self.t)
            self.tbicon = wxt.TrayIcon(self, **args)
            self.opened_dlg = 0
            self.has_tray = True
        except:
            self.tbicon = None

    def update_t(self):
        wdu.update_t(self, lang=self.get_lang(), zh=self.get_zh_mo(),
                     en=self.get_en_mo())

    def get_lang(self):
        return 'en'

    def get_zh_mo(self):
        return None

    def get_en_mo(self):
        return None

    def tt(self, text):
        return wdu.ttt(text, self.t)

    def on_quit(self, evt=None):
        wxw.quick_quit(self, t=self.t)

    def on_hide(self, evt=None):
        self.Hide()

    def echo_text(self, text='', **kwargs):
        kwargs.setdefault('t', self.t)
        kwargs.setdefault('log_mode', 'a')
        kwargs.setdefault('log_files', [])
        wxu.echo_text(self.rtc, text, **kwargs)

    def add_echo(self, text='', **kwargs):
        self.echo_lines.append((text, kwargs))

    def on_echoing(self, evt=None):
        wxu.on_echoing(self)

    def popup(self, caption, msg, icon='i', **kwargs):
        if self.has_tray:
            self.opened_dlg += 1
            if kwargs.pop('restore', True):
                self.tbicon.on_restore(None)

        kwargs.setdefault('t', self.t)
        result = wxw.popup(caption=caption, msg=msg, icon=icon, **kwargs)
        if self.has_tray:
            self.opened_dlg -= 1

        return result

    def on_setting(self, evt=None):
        if self.prepare_setting():
            self.open_setting()

    def open_setting(self):
        raise NotImplementedError

    def prepare_setting(self):
        if self.is_running:
            self.popup('Warning', 'Please stop current running task', 'w')
            return False

        if self.has_tray:
            self.opened_dlg += 1

        check_ok = wxw.quick_password_entry(self, root_pass=self.root_pass,
                                            t=self.t)
        if self.has_tray:
            self.opened_dlg -= 1

        return check_ok

    def on_about(self, evt=None):
        if self.has_tray:
            self.opened_dlg += 1

        kw = dict(name=self.app_name,
                  version=self.app_version,
                  icon=wxi.phoenix.getIcon(),
                  remark=self.app_remark,
                  t=self.t,
                  )
        if self.app_author:
            kw.update(author=self.app_author)

        wxw.quick_about(**kw)
        if self.has_tray:
            self.opened_dlg -= 1

    def on_popup_lang(self, evt):
        wxu.on_popup_lang(self, evt)

    def save_lang(self, lang=None):
        raise NotImplementedError

    def popup_lang(self, evt):
        wxu.popup_lang(self, evt)

    def update_ui_lang(self, refresh=True):
        wxu.update_ui_lang(self, refresh)
