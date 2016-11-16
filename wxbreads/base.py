#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import datetime
import wx
import wx.lib.delayedresult as delayedresult
import windbreads.utils as wdu
import wxbreads.utils as wxu
import wxbreads.images as wxi
import wxbreads.widgets as wxw


class BaseDialog(wx.Dialog):
    app_size = (-1, -1)
    app_name = 'Cool Dialog'
    app_version = ''

    def __init__(self, **kwargs):
        title = kwargs.get('title') or self.app_name
        version = kwargs.get('version') or self.app_version
        title = '{}{}'.format(title, ' - ' + version if version else '')
        size = kwargs.get('size', self.app_size)

        self.t = None
        self.opened_dlg = None

        kw = dict(size=size, title=title, pos=(-1, -1))
        style = kwargs.get('style')
        if style:
            kw.update(style=style)

        super(BaseDialog, self).__init__(kwargs.get('parent'), **kw)
        self.destroy = kwargs.get('destroy', True)
        self.need_reload = False
        self.Bind(wx.EVT_CLOSE, self.on_quit)

    def show(self, center=True):
        if center:
            self.CenterOnScreen()

        self.ShowModal()

    def on_quit(self, evt=None):
        if self.destroy:
            self.Destroy()
        else:
            self.Hide()

    def popup(self, caption, msg, icon='i', **kwargs):
        if self.opened_dlg is not None:
            self.opened_dlg += 1

        kwargs.setdefault('t', self.t)
        result = wxw.popup(self, caption=caption, msg=msg, icon=icon, **kwargs)
        if self.opened_dlg is not None:
            self.opened_dlg -= 1

        return result

    def need_adjust_opened_dlg(self):
        return self.has_tray or self.opened_dlg is not None


class BaseWindow(wx.Frame):
    clock_timer_id = wx.NewId()
    echo_timer_id = wx.NewId()
    root_pass = 'guess'
    auth_setting = True
    app_size = (-1, -1)
    app_version = '0.1'
    app_name = 'Cool App'
    app_remark = 'Description for cool app'
    app_author = ''
    quit_confirm = True
    clear_echo_row = 0
    sbar_width = [250, -1, 120]

    def __init__(self, **kwargs):
        title = kwargs.get('title') or self.app_name
        version = kwargs.get('version') or self.app_version
        title = '{}{}'.format(title, ' - ' + version if version else '')
        self.full_title = title
        size = kwargs.get('size', self.app_size)
        kw = dict(size=size, title=title)
        style = kwargs.get('style')
        if style:
            kw.update(style=style)

        super(BaseWindow, self).__init__(kwargs.get('parent'), **kw)
        self.is_running = False
        self.echo_lines = []
        self.is_echoing = False
        self.echoed_row = 0  # lines that echoed
        self.t = None
        self.has_tray = False
        self.opened_dlg = None
        self.logo = img = wxi.logo.GetImage()
        icon = wx.IconFromBitmap(img.ConvertToBitmap())
        self.SetIcon(icon)
        self.Bind(wx.EVT_CLOSE, self.on_quit)

    def show(self, center=True):
        if center:
            self.Centre(wx.BOTH)

        self.Show()

    def show_with_effect(self, effect=None, timeout=0, center=True):
        if effect is None:
            self.show(center)
            return

        if center:
            self.Centre(wx.BOTH)

        self.ShowWithEffect(effect, timeout)

    def set_min_size(self, size=None):
        self.SetMinSize(size or self.GetSize())

    def set_max_size(self, size=None):
        self.SetMaxSize(size or self.GetSize())

    def fix_size(self, size=None):
        self.set_min_size(size)
        self.set_max_size(size)

    def setup_timers(self, clock_ms=1000, echo_ms=200):
        self.all_timers = []
        if clock_ms:
            self.clock_timer = wxw.add_timer(self, self.clock_timer_id,
                                             self.on_clock_tick, clock_ms)
            self.all_timers.append(self.clock_timer)

        if echo_ms:
            self.echo_timer = wxw.add_timer(self, self.echo_timer_id,
                                            self.on_echoing, echo_ms)

            self.all_timers.append(self.echo_timer)

    def stop_timers(self):
        if hasattr(self, 'all_timers'):
            wxu.stop_timers(self.all_timers)

    def on_clock_tick(self, evt=None):
        if hasattr(self, 'sbar'):
            wxu.update_clock_statusbar(self.sbar, idx=self.sb_count - 1)

        self.other_clock_work()

    def update_run_ts(self, idx=1):
        if self.is_running:
            ts = (datetime.now() - self.start_ts).total_seconds()
            self.update_status('{}s'.format(ts), idx)

    def other_clock_work(self):
        pass

    def setup_statusbar(self):
        self.sb_count = len(self.get_sb_width())
        self.sbar = wxw.add_statusbar(self, widths=self.get_sb_width(),
                                      values=self.get_sb_value())

    def get_sb_width(self):
        """Width items for status bar."""
        return getattr(self, 'sbar_width') or [230, -1, 120]

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
        wxw.quick_quit(self, t=self.t, need_confirm=self.quit_confirm)

    def other_clean_work(self):
        pass

    def on_hide(self, evt=None):
        self.Hide()

    def echo_text(self, text='', **kwargs):
        kwargs.setdefault('t', self.t)
        kwargs.setdefault('log_mode', 'a')
        kwargs.setdefault('log_files', [])
        wxu.echo_text(self.rtc, text, **kwargs)

    def add_echo(self, text='', **kwargs):
        if self.clear_echo_row and kwargs.get('nl', True):
            self.echoed_row += 1
            kwargs.setdefault('clear',
                              self.echoed_row % self.clear_echo_row == 0)

        self.echo_lines.append((text, kwargs))

    def on_echoing(self, evt=None):
        wxu.on_echoing(self)

    def popup(self, caption, msg, icon='i', **kwargs):
        if self.need_adjust_opened_dlg():
            self.opened_dlg += 1

        if self.has_tray:
            if kwargs.pop('restore', True):
                self.tbicon.on_restore(None)

        else:
            self.Iconize(False)
            self.Raise()

        kwargs.setdefault('t', self.t)
        result = wxw.popup(self, caption=caption, msg=msg, icon=icon, **kwargs)
        if self.need_adjust_opened_dlg():
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

        if hasattr(self, 'is_root') and self.is_root:
            return True

        if not self.auth_setting:
            return True

        if self.need_adjust_opened_dlg():
            self.opened_dlg += 1

        check_ok = wxw.quick_password_entry(self, root_pass=self.root_pass,
                                            t=self.t)
        if self.need_adjust_opened_dlg():
            self.opened_dlg -= 1

        return check_ok

    def on_about(self, evt=None):
        if self.need_adjust_opened_dlg():
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
        if self.need_adjust_opened_dlg():
            self.opened_dlg -= 1

    def need_adjust_opened_dlg(self):
        return self.has_tray or self.opened_dlg is not None

    def on_popup_lang(self, evt):
        wxu.on_popup_lang(self, evt)

    def save_lang(self, lang=None):
        raise NotImplementedError

    def popup_lang(self, evt):
        wxu.popup_lang(self, evt)

    def update_ui_lang(self, refresh=True):
        wxu.update_ui_lang(self, refresh)

    def start_delay_work(self, c_func, w_func, **kwargs):
        delayedresult.startWorker(c_func, w_func, **kwargs)


def run_app(window_class, *args, **kwargs):
    app = wx.App()
    window_class(*args, **kwargs)
    app.MainLoop()
