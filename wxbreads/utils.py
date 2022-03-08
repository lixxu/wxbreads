#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import sys
from datetime import datetime
from time import strftime

import six
import windbreads.utils as wdu
import wx
import wx.richtext as rt

RTC_ALIGNS = dict(
    default=wx.TEXT_ALIGNMENT_DEFAULT,
    left=wx.TEXT_ALIGNMENT_LEFT,
    centre=wx.TEXT_ALIGNMENT_CENTRE,
    center=wx.TEXT_ALIGNMENT_CENTER,
    right=wx.TEXT_ALIGNMENT_RIGHT,
)
CHINESE_FONTS = (
    "微软雅黑",
    "雅黑",
    "microsoft yahei",
    "黑体",
    "宋体",
    "新宋体",
    "仿宋",
    "楷体",
    "simhei",
    "heiti",
    "simsun",
    "nsimsun",
    "fangsong",
    "kaiti",
    "mingliu",
    "pmingliu",
)
FS_ENCODING = sys.getfilesystemencoding()


def get_text_width(text, wgt):
    font = wgt.GetFont()
    dc = wx.WindowDC(wgt)
    dc.SetFont(font)
    return dc.GetTextExtent(text)


def get_adjust_size(size=(-1, -1), **kwargs):
    if size == (-1, -1):
        return size

    ratio_size = kwargs.get("ratio_size", (1600, 900))
    w, h = size
    rw, rh = ratio_size
    dw, dh = wx.GetDisplaySize()
    if rw == dw and rh == dh:
        return size

    bw, bh = -1, -1
    if w != -1:
        bw = int((w * dw) / rw)

    if h != -1:
        bh = int((h * dh) / rh)

    return (bw, bh)


def require_int(evt, min_value=1, max_value=-1):
    wgt = evt.GetEventObject()
    text = wgt.GetValue().strip()
    if text.isdigit():
        wgt.ChangeValue(text)
        wgt.SetInsertionPoint(wgt.GetInsertionPoint())


def auto_get_font(obj=None, **kwargs):
    if "font" in kwargs:
        return kwargs["font"]

    try:
        return obj.auto_font()
    except Exception:
        pass

    return None


def get_chinese_fonts():
    e = wx.FontEnumerator()
    e.EnumerateFacenames()
    fonts = []
    for name in (f for f in e.GetFacenames() if not f.startswith("@")):
        if name.lower().startswith(CHINESE_FONTS):
            fonts.append(name)

    return fonts


def get_best_chinese_font(fonts=[]):
    for cf in CHINESE_FONTS:
        for font in fonts:
            if font.lower().startswith(cf):
                return font

    return None


def pydate2wxdate(date):
    tt = date.timetuple()
    dmy = (tt[2], tt[1] - 1, tt[0])
    return wx.DateTimeFromDMY(*dmy)


def wxdate2pydate(date):
    if date.IsValid():
        return datetime.date(*(map(int, date.FormatISODate().split("-"))))

    return None


def cat_echo_text(**kwargs):
    args = kwargs.get("args")
    kargs = kwargs.get("kargs")
    t = kwargs.get("t")
    text = kwargs.get("text", "")
    if text:
        if kargs:
            return wdu.ttt(text, t).format(**kargs)

        if args:
            if not isinstance(args, (tuple, list)):
                args = (args,)

            return wdu.ttt(text, t).format(*args)

        return wdu.ttt(text, t)

    return text


def write_echo_text(**kwargs):
    ts_text = kwargs.get("ts_text")
    if kwargs.get("tff"):  # t for file
        text = cat_echo_text(**kwargs)
    else:
        kargs = kwargs.copy()
        kargs.update(t=None)
        text = cat_echo_text(**kargs)

    encoding = kwargs.get("encoding", "utf-8")
    if six.PY2 and isinstance(text, six.text_type):
        text = text.encode(encoding)
    elif six.PY3:
        text = bytes(text, encoding)
        if ts_text:
            ts_text = bytes(ts_text, encoding)

    nl = kwargs.get("nl", True)
    log_mode = kwargs.get("log_mode", "a" if six.PY2 else "ab")

    log_file = kwargs.get("log_file")
    log_files = kwargs.get("log_files", [])
    if log_file:
        log_files = [log_file]

    newline = wdu.NEW_LINE
    if six.PY3:
        ts_text = six.ensure_str(ts_text)
        text = six.ensure_str(text)
        newline = six.ensure_str(wdu.NEW_LINE)

    for log_file in log_files:
        with open(log_file, log_mode) as f:
            if ts_text:
                f.write(ts_text)

            f.write(text)
            if nl:
                f.write(newline)


def echo_text(
    rtc,
    text="",
    fg=None,
    bg=None,
    ts=True,
    nl=True,
    italic=False,
    align=None,
    underline=False,
    bold=False,
    ts_style=False,
    font=None,
    size=None,
    clear=False,
    keep_date=True,
    **kwargs
):
    if ts:
        now = datetime.now()
        if keep_date:
            ts_text = "[{}] ".format(now)
        else:
            ts_text = "[{}] ".format(str(now).split(" ", 1)[-1])

    else:
        ts_text = ""

    if text and isinstance(text, six.string_types):
        if not isinstance(text, six.text_type):
            utext = text.decode(wdu.detect_encoding(text)["encoding"])
        else:
            utext = text

    else:
        utext = "{}".format(text)

    write_echo_text(ts_text=ts_text, text=utext, nl=nl, **kwargs)
    if kwargs.get("no_echo", False):
        if clear:
            rtc.Clear()

        return

    rtc.SetInsertionPointEnd()
    rta = rt.RichTextAttr()
    rta.SetAlignment(RTC_ALIGNS["default"])
    rta.SetTextColour("black")
    rta.SetBackgroundColour("white")
    rta.SetFontStyle(wx.FONTSTYLE_NORMAL)
    rta.SetFontWeight(wx.FONTWEIGHT_NORMAL)
    rta.SetFontUnderlined(False)
    rtc.SetDefaultStyle(rta)
    if ts_text and not ts_style:
        rtc.WriteText(ts_text)

    align = RTC_ALIGNS.get(align)
    if align:
        rta.SetAlignment(align)

    if fg:
        rta.SetTextColour(fg)

    if bg:
        rta.SetBackgroundColour(bg)

    if font:
        rta.SetFontFaceName(font)

    if size:
        rta.SetFontSize(size)

    if bold is True:
        rta.SetFontWeight(wx.FONTWEIGHT_BOLD)
    elif bold is False:
        rta.SetFontWeight(wx.FONTWEIGHT_NORMAL)

    if italic is True:
        rta.SetFontStyle(wx.FONTSTYLE_ITALIC)
    elif italic is False:
        rta.SetFontStyle(wx.FONTSTYLE_NORMAL)

    if underline is not None:
        rta.SetFontUnderlined(underline)

    rtc.BeginStyle(rta)

    if ts_text and ts_style:
        rtc.WriteText(ts_text)

    rtc.WriteText(cat_echo_text(text=utext, **kwargs))
    rtc.EndStyle()
    if nl:
        rtc.Newline()

    rtc.ShowPosition(rtc.GetLastPosition())
    if clear:
        rtc.Clear()


def on_hide(self, evt=None):
    self.Hide()


def on_echoing(self, **kwargs):
    """Default method for echoing text."""
    if self.is_echoing or not self.echo_lines:
        return

    self.is_echoing = True
    i = 0
    batch = kwargs.get("batch", 100)
    while i < batch and self.echo_lines:
        line = self.echo_lines.pop(0)
        self.echo_text(line[0], **line[1])
        i += 1

    self.is_echoing = False


def start_timer(timer, miliseconds=1000, one_shot=False):
    if timer.IsRunning():
        return

    timer.Start(int(miliseconds), one_shot)


def stop_timer(timer, delete=False):
    if timer.IsRunning():
        timer.Stop()

    if delete:
        del timer


def stop_timers(timers=[], delete=False):
    [stop_timer(timer, delete) for timer in timers]


def update_clock_statusbar(sbar, ts_fmt="%Y/%m/%d %H:%M", idx=2):
    text = strftime(ts_fmt)
    try:
        text = text.decode(FS_ENCODING)
    except AttributeError:
        pass

    set_status_text(sbar, text.encode("utf-8"), idx)


def set_status_text(sbar, text, idx, t=None):
    sbar.SetStatusText(t(text) if t else text, idx)


def on_popup_lang(self, evt):
    if not hasattr(self, "english_id"):
        self.english_id = wx.NewIdRef()
        self.chinese_id = wx.NewIdRef()

        self.Bind(wx.EVT_MENU, self.popup_lang, id=self.english_id)
        self.Bind(wx.EVT_MENU, self.popup_lang, id=self.chinese_id)

    menu = wx.Menu()
    menu.Append(self.english_id, "English", "", wx.ITEM_RADIO)
    menu.Append(self.chinese_id, "Chinese - 简体中文", "", wx.ITEM_RADIO)
    if self.lang == "zh":
        menu.Check(self.chinese_id, True)
    else:
        menu.Check(self.english_id, True)

    self.PopupMenu(menu)
    menu.Destroy()


def popup_lang(self, evt):
    lang = "zh" if evt.GetId() == self.chinese_id else "en"
    if lang != self.lang:
        self.lang = lang
        self.update_t()
        self.update_ui_lang()
        self.save_lang(lang)

    evt.Skip()


def update_ui_lang(self, refresh=True):
    import wxbreads.widgets as wxw

    if hasattr(self, "lang_wgts"):
        for lwgt in self.lang_wgts:
            label = None
            tooltip = ""
            hint = None
            if len(lwgt) == 2:
                wgt, label = lwgt
            elif len(lwgt) == 3:
                wgt, label, tooltip = lwgt
            elif len(lwgt) == 4:
                wgt, label, tooltip, hint = lwgt

            wxw.set_tooltip(wgt, tooltip, self.t)
            if label is not None:
                wgt.SetLabel(self.tt(label))

            if hint is not None:
                wgt.SetHint(self.tt(hint))

    if refresh:
        if hasattr(self, "panel"):
            self.panel.Layout()

        self.Refresh()
