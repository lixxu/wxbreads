#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os.path
import tempfile
import traceback
from datetime import datetime
from functools import partial

import six
import wx
import wx.lib.delayedresult as delayedresult

# import wx.lib.evtmgr as em
import wx.lib.scrolledpanel as scrolled
from wx.lib.busy import BusyInfo

import windbreads.utils as wdu
import wxbreads.utils as wxu
import wxbreads.images as wxi
import wxbreads.widgets as wxw

SCROLLED_STYLE = wx.TAB_TRAVERSAL  # | wx.SUNKEN_BORDER
CP_STYLE = wx.CP_DEFAULT_STYLE | wx.CP_NO_TLW_RESIZE


class BaseBase(object):
    app_name = "App"
    app_title = ""
    app_size = (-1, -1)
    app_version = ""
    update_font = False
    quit_confirm = True
    quit_password = ""
    root_pass = "guess"
    min_chinese_fonts = 5
    remember_window = False
    show_version_in_title = True

    def init_values(self, **kwargs):
        self.opened_dlg = None
        self.need_reload = False
        if not hasattr(self, "t"):
            self.t = kwargs.get("t")

        self.destroy = kwargs.get("destroy", True)
        self.has_tray = False
        fonts = wxu.get_chinese_fonts()
        self.lang_wgts = []
        self.setting_wgts = []
        self.flat_menu = None
        self.support_chinese = len(fonts) >= self.min_chinese_fonts

    @property
    def screen_size(self):
        return wx.GetDisplaySize()

    def refresh_title(self, **kwargs):
        self.SetTitle(self.get_title(**kwargs))

    def highlight(self, wgt, color=None, focus=True, **kwargs):
        if color is None:
            color = wxw.HIGHLIGHT_RED

        wgt.SetBackgroundColour(color)
        if focus:
            wxw.focus_on(wgt, **kwargs)

    def get_title(self, **kwargs):
        title = kwargs.get("title") or self.app_title or self.app_name
        title = self.tt(title)
        if not self.show_version_in_title:
            return title

        version = kwargs.get("version") or self.app_version
        return "{}{}".format(title, " - " + version if version else "")

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

    def get_lang_text(self, lang="en"):
        return "English" if lang == "en" else "中文"

    def auto_font(self, lang=None):
        if not self.update_font:
            return None

        en_font, ch_font = self.get_fonts()
        name = en_font if (lang or self.get_lang()) == "en" else ch_font
        return self.create_font(name)

    def create_font(self, face=None):
        if face:
            font = self.GetFont()
            font.SetFaceName(face)
            return font
            # return wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, face)

        return None

    def create_book(self, parent, id=wx.ID_ANY, **kwargs):
        return wxw.add_fnb(parent, id, **kwargs)

    def create_boxsizer(self, orient="vertical"):
        return wx.BoxSizer(wx.VERTICAL if orient[0] == "v" else wx.HORIZONTAL)

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
        if not hasattr(self, "english_font_name"):
            self.english_font_name = self.get_basic_font()

        return self.english_font_name

    def other_clock_work(self):
        pass

    def can_remember_window(self):
        logic1 = self.remember_window and hasattr(self, "config")
        return logic1 and hasattr(self, "dump_config")

    def restore_position(self):
        if self.can_remember_window() and "app_w" in self.config:
            w, h = int(self.config["app_w"]), int(self.config["app_h"])
            x, y = int(self.config["app_x"]), int(self.config["app_y"])
            self.SetSize((w, h))
            self.SetPosition((x, y))

    def other_clean_work(self):
        if self.can_remember_window():
            w, h = self.GetSize()
            x, y = self.GetPosition()
            self.config.update(
                app_w=str(w), app_h=str(h), app_x=str(x), app_y=str(y)
            )
            self.dump_config()

    def get_lang(self):
        return "en"

    def get_zh_mo(self):
        return None

    def get_en_mo(self):
        return None

    def tt(self, text):
        return wdu.ttt(text, self.t)

    def set_font(self, wgt, font=None):
        wxw.set_font(wgt, font)

    def set_label(self, wgt, label="", tooltip=""):
        wgt.SetLabel(self.tt(label))
        self.set_tooltip(wgt, tooltip)

    def set_fg(self, wgt, fg=None):
        wxw.set_fg(wgt, fg)

    def set_bg(self, wgt, bg=None):
        wxw.set_bg(wgt, bg)

    def set_tooltip(self, wgt, tooltip=""):
        wxw.set_tooltip(wgt, tooltip, self.t)

    def set_min_size(self, size=None):
        self.SetMinSize(size or self.GetSize())

    def set_max_size(self, size=None):
        self.SetMaxSize(size or self.GetSize())

    def fix_size(self, size=None):
        self.set_min_size(size)
        self.set_max_size(size)

    def show(self, **kwargs):
        cop = kwargs.get("cop")
        if cop is None:
            cop = kwargs.get("center_on_parent", True)

        cos = kwargs.get("cos")
        if cos is None:
            cos = kwargs.get("center_on_screen", True)

        if cop:  # center on parent
            self.CenterOnParent()
        elif cos:
            self.CenterOnScreen()
        elif kwargs.get("center", True):
            self.Centre(wx.BOTH)

        if kwargs.get("modal", True) and hasattr(self, "ShowModal"):
            self.ShowModal()
            return

        effect = kwargs.get("effect")
        if effect:
            self.ShowWithEffect(effect, int(kwargs.get("timeout", 0)))
        else:
            self.Show()

        try:
            self.restore_position()
        except Exception:
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
        wxw.quick_quit(
            self,
            t=self.t,
            need_confirm=self.quit_confirm,
            need_password=self.quit_password,
        )

    def on_flat_menu(self, evt):
        btn = evt.GetEventObject()
        size = btn.GetSize()
        pos = btn.GetParent().ClientToScreen(btn.GetPosition())
        self.flat_menu.SetOwnerHeight(size.y)
        self.flat_menu.Popup(wx.Point(pos.x, pos.y), self)

    def need_adjust_opened_dlg(self):
        return self.has_tray or self.opened_dlg is not None

    def popup(self, caption, msg, icon="i", **kwargs):
        if self.need_adjust_opened_dlg():
            self.opened_dlg += 1

        if self.has_tray:
            if kwargs.pop("restore", True):
                self.tbicon.on_restore(None)

        try:
            self.Iconize(False)
            self.Raise()
        except Exception:
            pass

        kwargs.setdefault("t", self.t)
        result = wxw.popup(
            kwargs.pop("parent", self),
            caption=caption,
            msg=msg,
            icon=icon,
            **kwargs
        )
        if self.need_adjust_opened_dlg():
            self.opened_dlg -= 1

        return result

    def bind(self, evt, func, wgt, format="self"):
        if isinstance(evt, six.string_types):
            evt = getattr(wx, evt.upper())

        if not hasattr(self, func.__name__):
            func = partial(func, self)

        if format == "self":
            self.Bind(evt, func, wgt)
        else:
            wgt.Bind(evt, func)

    def show_busyinfo(self, msg):
        return BusyInfo(self.tt(msg))

    def show_busy(self, msg, parent=None):
        wx.WindowDisabler()
        busy = wx.BusyInfo(self.tt(msg), parent=parent or self)
        wx.YieldIfNeeded()
        return busy

    def hide_busy(self, busy):
        del busy

    # def register_evt(self, listener, event, source=None, win=None, id=None):
    #     em.eventManager.Register(listener, event, source, win, id)
    #
    # def unregister_listener(self, listener):
    #     em.eventManager.DeregisterListener(listener)
    #
    # def unregister_win(self, win):
    #     em.eventManager.DeregisterWindow(win)

    def start_delay_work(self, c_func, w_func, **kwargs):
        delayedresult.startWorker(c_func, w_func, **kwargs)

    def create_scrolled_panel(self, parent=None, id=-1, style=None, **kwargs):
        return scrolled.ScrolledPanel(
            parent or self, id, style=style or SCROLLED_STYLE, **kwargs
        )

    def create_cp(self, parent, style=None, label="Show", bind=None, **kwargs):
        cp = wx.CollapsiblePane(
            parent, label=self.tt(label), style=style or CP_STYLE
        )
        if bind:
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, bind, cp)

        return cp

    def layout_scrolled_panel(self, panel, sizer=None):
        if sizer:
            self.base_layout(panel, sizer)

        panel.SetAutoLayout(True)
        panel.SetupScrolling()

    def base_layout(self, panel, sizer, with_layout=False):
        panel.SetSizer(sizer)
        sizer.Fit(self)
        if with_layout:
            panel.Layout()


class BaseDialog(wx.Dialog, BaseBase):
    app_name = "Dialog"

    def __init__(self, **kwargs):
        self.init_values(**kwargs)
        size = kwargs.get("size", self.app_size)

        kw = dict(size=size, title=self.get_title(**kwargs), pos=(-1, -1))
        style = kwargs.get("style")
        if style:
            kw.update(style=style)

        super(BaseDialog, self).__init__(kwargs.get("parent"), **kw)
        self.english_font_name = self.get_english_font()
        wxw.set_font(self, kwargs.get("font"))
        self.Bind(wx.EVT_CLOSE, self.on_quit)

    def setup_ui(self, parent=None, ok_text="Save", cancel_text="Cancel"):
        self.wgts = {}
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.setup_other_ui(vbox)
        self.setup_ok_cancel_buttons(
            vbox, parent=parent, ok_text=ok_text, cancel_text=cancel_text
        )

        self.base_layout(self, vbox)

    def setup_ok_cancel_buttons(
        self, sizer, parent=None, ok_text="Save", cancel_text="Cancel"
    ):
        ok_btn, cancel_btn = wxw.add_ok_buttons(
            parent or self, sizer, ok_text=ok_text, cancel_text=cancel_text
        )
        ok_btn.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_quit)

    def on_save(self, evt):
        pass

    def on_quit(self, evt=None):
        if self.destroy:
            self.Destroy()
        else:
            self.Hide()


class BaseWindow(wx.Frame, BaseBase):
    clock_timer_id = wx.NewIdRef()
    echo_timer_id = wx.NewIdRef()
    auth_setting = True
    app_remark = "Description for cool app"
    app_author = ""
    reset_copyright = True
    reset_copyright_seconds = (0, 1, 30, 31)
    clear_echo_row = 0
    sbar_width = [260, -1, 130]

    def __init__(self, **kwargs):
        self.init_values(**kwargs)

        self.has_sbar = False
        self.full_title = self.get_title(**kwargs)
        size = kwargs.get("size", self.app_size)
        kw = dict(size=size, title=self.full_title)
        style = kwargs.get("style")
        if style:
            kw.update(style=style)

        super(BaseWindow, self).__init__(kwargs.get("parent"), **kw)
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

    def setup_base_big_buttons(self, parent, sizer, **kwargs):
        buttons = wxw.quick_big_buttons(self, parent, t=self.t, **kwargs)
        wxw.quick_pack(sizer, wgts=[(btn[0], 1) for btn in buttons])
        self.big_buttons = buttons

    def setup_base_ui(
        self, with_big=True, big_kw={}, main_kw={}, settings_kw={}
    ):
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        if with_big:
            self.setup_base_big_buttons(self.panel, vbox, **big_kw)

        self.book = wxw.add_fnb(self.panel, wx.ID_ANY)
        self.add_base_main_page()
        self.add_base_settings_page()
        self.enable_wgts(False)

        wxw.pack(self.book, vbox, prop=1)
        self.base_layout(self.panel, vbox, with_layout=True)

    def add_base_main_page(self, title="Main", **kwargs):
        self.main_panel = p = wx.Panel(self.book)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.fill_main_page(p, vbox, **kwargs)

        self.rtc = wxw.add_richtext(p, readonly=True, size=(-1, 450))

        wxw.pack(self.rtc, vbox, prop=1, flag="e,a")

        self.base_layout(p, vbox)
        self.book.AddPage(p, self.tt(title))

    def add_base_settings_page(self, title="Settings", **kwargs):
        self.is_locked = True
        p = wx.Panel(self.book)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.fill_settings_page(p, vbox, **kwargs)

        line = wxw.add_line(p)
        wxw.pack(line, vbox)
        self.unlock_btn = wxw.add_button(
            p, label="Unlock", size=(-1, 40), t=self.t
        )
        cancel_btn = wxw.add_button(p, label="Cancel", size=(-1, 40), t=self.t)
        self.unlock_btn.Bind(wx.EVT_BUTTON, self.on_settings_save)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_settings_cancel)

        self.add_lang_wgt((self.unlock_btn, "Unlock"))
        self.add_lang_wgt((cancel_btn, "Cancel"))

        wxw.quick_pack(vbox, wgts=[(self.unlock_btn, 1), cancel_btn])

        self.base_layout(p, vbox)
        self.book.AddPage(p, self.tt(title))

    def fill_main_page(self, parent, sizer=None, **kwargs):
        pass

    def fill_settings_page(self, parent, sizer=None, **kwargs):
        pass

    def on_settings_save(self, evt=None):
        if self.is_locked:
            if not self.prepare_setting():
                return

            self.set_label(self.unlock_btn, "Save")
            self.enable_wgts(True)
            self.is_locked = False
        else:
            self.save_settings()
            self.on_settings_cancel()

    def save_settings(self):
        pass

    def on_settings_cancel(self, evt=None):
        self.is_locked = True
        self.set_label(self.unlock_btn, "Unlock")
        self.enable_wgts(False)

    def enable_wgts(self, enable=True, wgts=[]):
        [wgt.Enable(enable) for wgt in wgts or self.setting_wgts]

    def setup_timers(self, clock_ms=1000, echo_ms=200):
        self.all_timers = []
        if clock_ms:
            self.clock_timer = wxw.add_timer(
                self, self.clock_timer_id, self.on_clock_tick, clock_ms
            )
            self.all_timers.append(self.clock_timer)

        if echo_ms:
            self.echo_timer = wxw.add_timer(
                self, self.echo_timer_id, self.on_echoing, echo_ms
            )

            self.all_timers.append(self.echo_timer)

    def stop_timers(self, delete=False):
        if hasattr(self, "all_timers"):
            wxu.stop_timers(self.all_timers, delete=delete)

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
                self.update_status("{}s".format(time_df.total_seconds()), idx)
            else:
                self.update_status("{}".format(time_df), idx)

    def setup_statusbar(self):
        self.has_sbar = True
        self.sb_count = len(self.get_sb_width())
        self.sbar = wxw.add_statusbar(
            self, widths=self.get_sb_width(), values=self.get_sb_value()
        )
        self.SetStatusBar(self.sbar)

    def get_sb_width(self):
        """Width items for status bar."""
        return self.sbar_width

    def get_sb_value(self):
        """Value items for status bar."""
        return [self.get_copyright(), "", ""]

    def get_copyright(self):
        return wdu.get_copy_right()

    def update_status(self, text, idx, **kwargs):
        kwargs.setdefault("t", self.t)
        try:
            wxu.set_status_text(self.sbar, text, idx, **kwargs)
        except Exception:
            temp_file = os.path.join(tempfile.gettempdir(), "wxbugs.txt")
            with open(temp_file, "a") as f:
                f.write("{}\n".format(traceback.format_exc()))

    def setup_tray(self, **kwargs):
        import wxbreads.trayicon as wxt

        try:
            args = dict(
                icon=kwargs.get("icon") or self.logo,
                text=kwargs.get("text", self.app_title or self.app_name),
                t=self.t,
            )
            self.tbicon = wxt.TrayIcon(self, **args)
            self.opened_dlg = 0
            self.has_tray = True
        except Exception:
            self.tbicon = None

    def update_t(self):
        wdu.update_t(
            self,
            lang=self.get_lang(),
            zh=self.get_zh_mo(),
            en=self.get_en_mo(),
        )

    def refresh_translation(self, wgts=[]):
        font = self.auto_font()
        for lwgt in wgts:
            tooltip = ""
            if len(lwgt) == 2:
                wgt, label = lwgt
            else:
                wgt, label, tooltip = lwgt

            wxw.set_tooltip(wgt, tooltip, self.t)
            if label is not None:
                self.set_label(wgt, label)

            wxw.set_font(wgt, font)

        if hasattr(self, "panel"):
            self.panel.Layout()
        else:
            self.Layout()

        self.Refresh()

    def echo_text(self, text="", **kwargs):
        wxu.echo_text(self.rtc, text, **self.set_echo_defaults(kwargs))

    def set_echo_defaults(self, kwargs):
        kwargs.setdefault("t", self.t)
        kwargs.setdefault("log_mode", "a" if six.PY2 else "ab")
        kwargs.setdefault("log_files", [])
        return kwargs

    def add_echo(self, text="", **kwargs):
        if self.clear_echo_row and kwargs.get("nl", True):
            self.echoed_row += 1
            kwargs.setdefault(
                "clear", self.echoed_row % self.clear_echo_row == 0
            )

        self.echo_lines.append((text, self.set_echo_defaults(kwargs)))

    def add_echo3(self, text="", **kwargs):
        if self.clear_echo_row and kwargs.get("nl", True):
            self.echoed_row += 1
            kwargs.setdefault(
                "clear", self.echoed_row % self.clear_echo_row == 0
            )

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
            self.popup("Warning", "Please stop current running task", "w")
            return False

        if hasattr(self, "is_root") and self.is_root:
            return True

        if not self.auth_setting:
            return True

        if self.need_adjust_opened_dlg():
            self.opened_dlg += 1

        check_ok = wxw.quick_password_entry(
            self, root_pass=self.root_pass, t=self.t
        )
        if self.need_adjust_opened_dlg():
            self.opened_dlg -= 1

        return check_ok

    def on_about(self, evt=None):
        if self.need_adjust_opened_dlg():
            self.opened_dlg += 1

        wxw.quick_about(**self.get_about_kwargs())
        if self.need_adjust_opened_dlg():
            self.opened_dlg -= 1

    def get_about_icon(self):
        try:
            return wxi.phoenix.GetIcon()
        except Exception:
            return wxi.phoenix.getIcon()

    def get_about_extra_kwargs(self):
        return {}

    def get_about_kwargs(self):
        kw = dict(
            name=self.app_title or self.app_name,
            version=self.app_version,
            icon=self.get_about_icon(),
            remark=self.app_remark,
            t=self.t,
            website=getattr(self, "app_website", ""),
            author=getattr(self, "app_author", ""),
            licence=getattr(self, "app_licence", ""),
        )
        kw.update(self.get_about_extra_kwargs())
        return kw

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


BaseFrame = BaseWindow


def run_app(window_class, *args, **kwargs):
    app = wx.App()
    window_class(*args, **kwargs)
    app.MainLoop()
