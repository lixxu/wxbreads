#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from functools import partial
from datetime import datetime
import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.delayedresult as delayedresult
import windbreads.utils as wdu
import wxbreads.utils as wxu
import wxbreads.images as wxi
import wxbreads.widgets as wxw

SCROLLED_STYLE = wx.TAB_TRAVERSAL  # | wx.SUNKEN_BORDER
CP_STYLE = wx.CP_DEFAULT_STYLE | wx.CP_NO_TLW_RESIZE


class BaseBase(object):
    app_name = 'App'
    app_size = (-1, -1)
    app_version = ''
    update_font = False
    quit_confirm = True
    quit_password = ''
    min_chinese_fonts = 5
    remember_window = False

    def init_values(self, **kwargs):
        self.opened_dlg = None
        self.need_reload = False
        self.t = kwargs.get('t')
        self.destroy = kwargs.get('destroy', True)
        self.has_tray = False
        fonts = wxu.get_chinese_fonts()
        self.lang_wgts = []
        self.setting_wgts = []
        self.support_chinese = len(fonts) >= self.min_chinese_fonts

    def add_lang_wgt(self, items):
        if self.support_chinese:
            self.lang_wgts.append(items)

    def get_font(self, bold=False, size=None):
        font = self.GetFont()
        if bold:
            font.SetWeight(wx.BOLD)

        if size:
            font.SetPointSize(size)

        return font

    def get_lang_text(self, lang='en'):
        return 'English' if lang == 'en' else '中文'

    def auto_font(self, lang=None):
        if not self.update_font:
            return None

        en_font, ch_font = self.get_fonts()
        l = lang or self.get_lang()
        name = en_font if l == 'en' else ch_font
        return self.create_font(name)

    def create_font(self, face=None):
        if face:
            font = self.GetFont()
            font.SetFaceName(face)
            return font
            # return wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, face)

        return None

    def get_fonts(self):
        return self.get_english_font(), self.get_best_chinese_font()

    def get_chinese_fonts(self):
        return wxu.get_chinese_fonts()

    def get_best_chinese_font(self, fonts=[]):
        font = wxu.get_best_chinese_font(fonts or self.get_chinese_fonts())
        return font if font else self.get_english_font()

    def get_basic_font(self):
        return self.GetFont().GetFaceName()

    def get_english_font(self):
        if not hasattr(self, 'english_font_name'):
            self.english_font_name = self.get_basic_font()

        return self.english_font_name

    def other_clock_work(self):
        pass

    def can_remember_window(self):
        return (self.remember_window and hasattr(self, 'config') and
                hasattr(self, 'dump_config'))

    def restore_position(self):
        if self.can_remember_window() and 'app_w' in self.config:
            w, h = int(self.config['app_w']), int(self.config['app_h'])
            x, y = int(self.config['app_x']), int(self.config['app_y'])
            self.SetSize((w, h))
            self.SetPosition((x, y))

    def other_clean_work(self):
        if self.can_remember_window():
            w, h = self.GetSize()
            x, y = self.GetPosition()
            self.config.update(app_w=str(w), app_h=str(h),
                               app_x=str(x), app_y=str(y))
            self.dump_config()

    def get_lang(self):
        return 'en'

    def get_zh_mo(self):
        return None

    def get_en_mo(self):
        return None

    def tt(self, text):
        return wdu.ttt(text, self.t)

    def set_label(self, wgt, label='', tooltip=''):
        wgt.SetLabel(self.tt(label))
        wxw.set_tooltip(wgt, tooltip, self.t)

    def set_min_size(self, size=None):
        self.SetMinSize(size or self.GetSize())

    def set_max_size(self, size=None):
        self.SetMaxSize(size or self.GetSize())

    def fix_size(self, size=None):
        self.set_min_size(size)
        self.set_max_size(size)

    def show(self, **kwargs):
        cop = kwargs.get('cop')
        if cop is None:
            cop = kwargs.get('center_on_parent', True)

        cos = kwargs.get('cos')
        if cos is None:
            cos = kwargs.get('center_on_screen', True)

        if cop:  # center on parent
            self.CenterOnParent()
        elif cos:
            self.CenterOnScreen()
        elif kwargs.get('center', True):
            self.Centre(wx.BOTH)

        if kwargs.get('modal', True) and hasattr(self, 'ShowModal'):
            self.ShowModal()
            return

        effect = kwargs.get('effect')
        if effect:
            self.ShowWithEffect(effect, int(kwargs.get('timeout', 0)))
        else:
            self.Show()

        try:
            self.restore_position()
        except:
            pass

    def on_upper_case(self, evt=None):
        obj = evt.GetEventObject()
        text = obj.GetValue().strip().upper()
        obj.ChangeValue(text)
        obj.SetInsertionPointEnd()
        evt.Skip()

    def on_hide(self, evt=None):
        self.Hide()

    def on_quit(self, evt=None):
        wxw.quick_quit(self, t=self.t, need_confirm=self.quit_confirm,
                       need_password=self.quit_password)

    def need_adjust_opened_dlg(self):
        return self.has_tray or self.opened_dlg is not None

    def popup(self, caption, msg, icon='i', **kwargs):
        if self.need_adjust_opened_dlg():
            self.opened_dlg += 1

        if self.has_tray:
            if kwargs.pop('restore', True):
                self.tbicon.on_restore(None)

        try:
            self.Iconize(False)
            self.Raise()
        except:
            pass

        kwargs.setdefault('t', self.t)
        result = wxw.popup(self, caption=caption, msg=msg, icon=icon, **kwargs)
        if self.need_adjust_opened_dlg():
            self.opened_dlg -= 1

        return result

    def bind(self, evt, func, wgt, format='self'):
        if isinstance(evt, wdu.safe_basestring()):
            evt = getattr(wx, evt.upper())

        if not hasattr(self, func.__name__):
            func = partial(func, self)

        if format == 'self':
            self.Bind(evt, func, wgt)
        else:
            wgt.Bind(evt, func)


class BaseDialog(wx.Dialog, BaseBase):
    app_name = 'Dialog'

    def __init__(self, **kwargs):
        self.init_values(**kwargs)
        title = wdu.ttt(kwargs.get('title') or self.app_name, self.t)
        version = kwargs.get('version') or self.app_version
        title = '{}{}'.format(title, ' - ' + version if version else '')
        size = kwargs.get('size', self.app_size)

        kw = dict(size=size, title=title, pos=(-1, -1))
        style = kwargs.get('style')
        if style:
            kw.update(style=style)

        super(BaseDialog, self).__init__(kwargs.get('parent'), **kw)
        self.english_font_name = self.get_english_font()
        wxw.set_font(self, kwargs.get('font'))
        self.Bind(wx.EVT_CLOSE, self.on_quit)

    def on_quit(self, evt=None):
        if self.destroy:
            self.Destroy()
        else:
            self.Hide()


class BaseWindow(wx.Frame, BaseBase):
    clock_timer_id = wx.NewId()
    echo_timer_id = wx.NewId()
    root_pass = 'guess'
    auth_setting = True
    app_remark = 'Description for cool app'
    app_author = ''
    reset_copyright = True
    reset_copyright_seconds = (0, 1, 30, 31)
    clear_echo_row = 0
    sbar_width = [260, -1, 130]

    def __init__(self, **kwargs):
        self.init_values(**kwargs)

        self.has_sbar = False
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
        self.english_font_name = self.get_english_font()
        self.is_running = False
        self.echo_lines = []
        self.is_echoing = False
        self.echoed_row = 0  # lines that echoed
        self.logo = img = wxi.logo.GetImage()
        try:
            icon = wx.IconFromBitmap(img.ConvertToBitmap())
        except AttributeError:
            icon = wx.Icon(img.ConvertToBitmap())

        self.SetIcon(icon)
        self.Bind(wx.EVT_CLOSE, self.on_quit)

    def on_start(self, evt):
        if evt:
            evt.Skip()

    def on_changes(self, evt):
        if evt:
            evt.Skip()

    def create_book(self, parent, id=wx.ID_ANY, **kwargs):
        return wxw.add_fnb(parent, id, **kwargs)

    def create_boxsizer(self, orient='vertical'):
        return wx.BoxSizer(wx.VERTICAL if orient[0] == 'v' else wx.HORIZONTAL)

    def create_scrolled_panel(self, parent, id=-1, style=None, **kwargs):
        return scrolled.ScrolledPanel(parent, id,
                                      style=style or SCROLLED_STYLE, **kwargs)

    def create_cp(self, parent, style=None, label='Show', bind=None, **kwargs):
        self.cp = cp = wx.CollapsiblePane(self.panel, label=self.tt(label),
                                          style=style or CP_STYLE)
        if bind:
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, bind, cp)

    def layout_scrolled_panel(self, panel, sizer=None):
        if sizer:
            panel.SetSizer(sizer)
            sizer.Fit(self)

        panel.SetAutoLayout(True)
        panel.SetupScrolling()

    def setup_base_big_buttons(self, parent, sizer, **kwargs):
        buttons = wxw.quick_big_buttons(self, parent, t=self.t, **kwargs)
        wxw.quick_pack(sizer, wgts=[(btn[0], 1) for btn in buttons])
        self.big_buttons = buttons

    def setup_base_ui(self, with_big=True, big_kw={}, main_kw={},
                      settings_kw={}):
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        if with_big:
            self.setup_base_big_buttons(self.panel, vbox, **big_kw)

        self.book = wxw.add_fnb(self.panel, wx.ID_ANY)
        self.add_base_main_page()
        self.add_base_settings_page()
        self.enable_wgts(False)

        wxw.pack(self.book, vbox, prop=1)

        self.panel.SetSizer(vbox)
        vbox.Fit(self)
        self.panel.Layout()

    def add_base_main_page(self, title='Main', **kwargs):
        self.main_panel = p = wx.Panel(self.book)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.fill_main_page(p, vbox, **kwargs)

        self.rtc = wxw.add_richtext(p, readonly=True, size=(-1, 450))

        wxw.pack(self.rtc, vbox, prop=1, flag='e,a')

        p.SetSizer(vbox)
        vbox.Fit(self)
        self.book.AddPage(p, self.tt(title))

    def add_base_settings_page(self, title='Settings', **kwargs):
        self.is_locked = True
        p = wx.Panel(self.book)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.fill_settings_page(p, vbox, **kwargs)

        line = wxw.add_line(p)
        wxw.pack(line, vbox)
        self.unlock_btn = wxw.add_button(p, label='Unlock', size=(-1, 40),
                                         t=self.t)
        cancel_btn = wxw.add_button(p, label='Cancel', size=(-1, 40),
                                    t=self.t)
        self.unlock_btn.Bind(wx.EVT_BUTTON, self.on_settings_save)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_settings_cancel)

        self.add_lang_wgt((self.unlock_btn, 'Unlock'))
        self.add_lang_wgt((cancel_btn, 'Cancel'))

        wxw.quick_pack(vbox, wgts=[(self.unlock_btn, 1), cancel_btn])

        p.SetSizer(vbox)
        vbox.Fit(self)
        self.book.AddPage(p, self.tt(title))

    def fill_main_page(self, parent, sizer=None, **kwargs):
        pass

    def fill_settings_page(self, parent, sizer=None, **kwargs):
        pass

    def on_settings_save(self, evt=None):
        if self.is_locked:
            if not self.prepare_setting():
                return

            self.set_label(self.unlock_btn, 'Save')
            self.enable_wgts(True)
            self.is_locked = False
        else:
            self.save_settings()
            self.on_settings_cancel()

    def save_settings(self):
        pass

    def on_settings_cancel(self, evt=None):
        self.is_locked = True
        self.set_label(self.unlock_btn, 'Unlock')
        self.enable_wgts(False)

    def enable_wgts(self, enable=True, wgts=[]):
        [wgt.Enable(enable) for wgt in wgts or self.setting_wgts]

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
        if self.has_sbar:
            wxu.update_clock_statusbar(self.sbar, idx=self.sb_count - 1)
            if self.reset_copyright:
                if datetime.now().second in self.reset_copyright_seconds:
                    self.update_status(self.get_copyright(), 0, t=None)

        self.other_clock_work()

    def update_run_ts(self, idx=1, as_seconds=True):
        if self.is_running:
            time_df = datetime.now() - self.start_ts
            if as_seconds:
                self.update_status('{}s'.format(time_df.total_seconds()), idx)
            else:
                self.update_status('{}'.format(time_df), idx)

    def setup_statusbar(self):
        self.has_sbar = True
        self.sb_count = len(self.get_sb_width())
        self.sbar = wxw.add_statusbar(self, widths=self.get_sb_width(),
                                      values=self.get_sb_value())

    def get_sb_width(self):
        """Width items for status bar."""
        return self.sbar_width

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
            raise
            self.tbicon = None

    def update_t(self):
        wdu.update_t(self, lang=self.get_lang(), zh=self.get_zh_mo(),
                     en=self.get_en_mo())

    def refresh_translation(self, wgts=[]):
        font = self.auto_font()
        for lwgt in wgts:
            tooltip = ''
            if len(lwgt) == 2:
                wgt, label = lwgt
            else:
                wgt, label, tooltip = lwgt

            wxw.set_tooltip(wgt, tooltip, self.t)
            if label is not None:
                self.set_label(wgt, label)

            wxw.set_font(wgt, font)

        if hasattr(self, 'panel'):
            self.panel.Layout()
        else:
            self.Layout()

        self.Refresh()

    def echo_text(self, text='', **kwargs):
        kwargs.setdefault('t', self.t)
        kwargs.setdefault('log_mode', 'a' if wdu.IS_PY2 else 'ab')
        kwargs.setdefault('log_files', [])
        wxu.echo_text(self.rtc, text, **kwargs)

    def add_echo(self, text='', **kwargs):
        if self.clear_echo_row and kwargs.get('nl', True):
            self.echoed_row += 1
            kwargs.setdefault('clear',
                              self.echoed_row % self.clear_echo_row == 0)

        self.echo_lines.append((text, kwargs))

    def add_echo3(self, text='', **kwargs):
        if self.clear_echo_row and kwargs.get('nl', True):
            self.echoed_row += 1
            kwargs.setdefault('clear',
                              self.echoed_row % self.clear_echo_row == 0)

        self.echo_text(text, **kwargs)

    def on_echoing(self, evt=None):
        wxu.on_echoing(self)

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

        try:
            icon = wxi.phoenix.GetIcon()
        except:
            icon = wxi.phoenix.getIcon()

        kw = dict(name=self.app_name,
                  version=self.app_version,
                  icon=icon,
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
