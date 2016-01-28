#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import time
from datetime import datetime
import pickle
import wx
try:
    from agw import genericmessagedialog as gmd
except ImportError:
    import wx.lib.agw.genericmessagedialog as gmd

ICONS = dict(info=wx.ICON_INFORMATION,
             warn=wx.ICON_WARNING,
             warning=wx.ICON_WARNING,
             error=wx.ICON_ERROR,
             question=wx.ICON_QUESTION,
             exclamation=wx.ICON_EXCLAMATION,
             )
DEFAULT_WILDCARD = 'All files (*.*)|*.*'


def dump_pickle(data, pk_file, silent=True):
    try:
        with open(pk_file, 'wb') as f:
            pickle.dump(data, f)

    except:
        if not silent:
            raise


def load_pickle(pk_file, silent=True):
    try:
        with open(pk_file, 'rb') as f:
            return pickle.load(f)

    except:
        if silent:
            return {}

        raise


def popup_msgbox(parent=None, caption='caption', msg='', btn=wx.OK,
                 icon='info', need_return=False, size=wx.DefaultSize):
    icon = ICONS.get(icon, ICONS['info'])
    dlg = gmd.GenericMessageDialog(parent, '{}'.format(msg), caption,
                                   btn | icon, size=size)
    if need_return:
        return dlg

    dlg.CenterOnParent()
    result = dlg.ShowModal()
    dlg.Destroy()
    return result


def add_button_field(parent, id=-1, label='Button', width=-1, height=-1,
                     style=wx.NO_BORDER, tooltip='', font=None,
                     fg=None, bg=None, **kwargs):
    btn = wx.Button(parent, id, label, size=(width, height))
    if tooltip:
        btn.SetToolTipString(tooltip)

    if font:
        btn.SetFont(font)

    if fg:
        btn.SetForegroundColour(fg)

    if bg:
        btn.SetBackgroundColour(bg)

    return btn


def add_label_field(parent, id=-1, label='', font=None, width=-1, height=-1,
                    style=None, tooltip='', fg=None, bg=None, **kwargs):
    nargs = dict(size=(width, height))
    if style:
        nargs.update(style=style)

    lbl = wx.StaticText(parent, id, label, **nargs)
    if tooltip:
        lbl.SetToolTipString(tooltip)

    if font:
        lbl.SetFont(font)

    if fg:
        lbl.SetForegroundColour(fg)

    if bg:
        lbl.SetBackgroundColour(bg)

    return lbl


def add_text_field(parent, id=-1, value='', width=-1, height=-1, font=None,
                   style=None, tooltip='', fg=None, bg=None, **kwargs):
    nargs = dict(size=(width, height))
    if style:
        nargs.update(style=style)

    wgt = wx.TextCtrl(parent, id, '{}'.format(value), **nargs)
    if tooltip:
        wgt.SetToolTipString(tooltip)

    if font:
        wgt.SetFont(font)

    if fg:
        wgt.SetForegroundColour(fg)

    return wgt


def add_checkbox_field(parent, id=-1, label='', width=-1, height=-1,
                       value=True, tooltip='', font=None, fg=None, bg=None,
                       **kwargs):
    wgt = wx.CheckBox(parent, id, label, size=(width, height))
    if tooltip:
        wgt.SetToolTipString(tooltip)

    if font:
        wgt.SetFont(font)

    if fg:
        wgt.SetForegroundColour(fg)

    if bg:
        wgt.SetBackgroundColour(bg)

    wgt.SetValue(value)
    return wgt


def select_open_dir(parent, title='Choose a directory',
                    style=wx.DD_DEFAULT_STYLE, **kwargs):
    dlg = wx.DirDialog(parent, title, style=style)
    folder = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
    dlg.Destroy()
    return folder


def select_open_file(parent, msg='Choose a file', default_dir=os.getcwd(),
                     default_file='', wildcard=DEFAULT_WILDCARD,
                     style=wx.OPEN | wx.FD_FILE_MUST_EXIST | wx.CHANGE_DIR,
                     multiple=False, **kwargs):
    if multiple:
        style = style | wx.MULTIPLE

    dlg = wx.FileDialog(parent, message=msg, defaultDir=default_dir,
                        defaultFile=default_file, wildcard=wildcard,
                        style=style)

    paths = dlg.GetPaths() if dlg.ShowModal() == wx.ID_OK else []
    dlg.Destroy()
    if paths:
        return paths if multiple else paths[0]

    return None


def select_save_file(parent, msg='Save file as...', default_dir=os.getcwd(),
                     default_file='', wildcard=DEFAULT_WILDCARD,
                     style=wx.SAVE | wx.FD_OVERWRITE_PROMPT | wx.CHANGE_DIR,
                     **kwargs):
    dlg = wx.FileDialog(parent, message=msg, defaultDir=default_dir,
                        defaultFile=default_file, wildcard=wildcard,
                        style=style)
    path = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
    dlg.Destroy()
    return path


def add_quick_sizer(top_sizer, wgts=[], orient='h', prop=0, border=5,
                    **kwargs):
    box = wx.BoxSizer(wx.HORIZONTAL if orient == 'h' else wx.VERTICAL)
    for wgt, prop in wgts[:-1]:
        box.Add(wgt, prop, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, border)

    if len(wgts) > 1:
        box.Add(wgts[-1][0], wgts[-1][1], wx.ALIGN_LEFT | wx.ALL | wx.EXPAND,
                border)

    top_sizer.Add(box, prop, wx.EXPAND | wx.ALL, border)
    return box


def add_text_row(parent, top_sizer, label='Text', value='', width=-1, border=5,
                 height=-1, tooltip='', font=None, fg=None, bg=None, **kwargs):
    nargs = dict(height=height, tooltip=tooltip, font=font, fg=fg, bg=bg)
    lbl = add_label_field(parent, label=label, width=width, **nargs)
    wgt = add_text_field(parent, value=value, **nargs)
    add_quick_sizer(top_sizer, wgts=[(lbl, 0), (wgt, 1)], border=border)
    return lbl, wgt


def add_checkbox_row(parent, top_sizer, label='', width=-1, height=-1,
                     tooltip='', value=True, cb_label='', font=None, fg=None,
                     bg=None, border=5, **kwargs):
    nargs = dict(height=height, tooltip=tooltip, font=font, fg=fg, bg=bg)
    lbl = add_label_field(parent, label=label, width=width, **nargs)
    wgt = add_checkbox_field(parent, label=cb_label, value=value, width=width,
                             **nargs)
    add_quick_sizer(top_sizer, wgts=[(lbl, 0), (wgt, 1)], border=border)
    return lbl, wgt


def add_open_dialog(parent, top_sizer, label='Select folder', value='',
                    width=-1, height=-1, tooltip='', border=5,
                    btn_label='Browse', btn_id=None, fg=None, **kwargs):
    lbl = add_label_field(parent, label=label, width=width, height=height)
    txt = add_text_field(parent, value=value, height=height)
    if tooltip:
        txt.SetToolTipString(tooltip)

    nargs = dict(label=btn_label, height=height)
    if btn_id:
        nargs.update(id=btn_id)

    btn = add_button_field(parent, **nargs)
    if tooltip:
        btn.SetToolTipString(tooltip)

    add_quick_sizer(top_sizer, wgts=[(lbl, 0), (txt, 1), (btn, 0)],
                    border=border)
    return lbl, txt, btn


def add_ok_buttons(parent, top_sizer, id=-1, size=(100, 40), ok_text='&Save',
                   cancel_text='&Cancel', border=5, **kwargs):
    line = wx.StaticLine(parent, id, size=(-1, -1), style=wx.LI_HORIZONTAL)

    ok_btn = wx.Button(parent, wx.ID_OK, ok_text, size=size)
    ok_btn.SetDefault()
    cancel_btn = wx.Button(parent, wx.ID_CANCEL, cancel_text, size=size)

    btnsizer = wx.StdDialogButtonSizer()
    btnsizer.AddButton(ok_btn)
    btnsizer.AddButton(cancel_btn)
    btnsizer.Realize()

    style = wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP
    top_sizer.Add(line, 0, style, border)

    style = wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL
    top_sizer.Add(btnsizer, 1, style, border)
    return ok_btn, cancel_btn


def write_rich_text(obj, wgt, text, color=None, clear=False, ts=True, nl=True,
                    **kwargs):
    if clear:
        wgt.Clear()

    wgt.MoveEnd()
    pre_text = '[{}] '.format(datetime.now()) if ts else ''

    if nl:
        text = '{}\n'.format(text)

    if pre_text:
        wgt.WriteText(pre_text)

    if color:
        wgt.BeginTextColour(color)
        wgt.WriteText(text)
        wgt.EndTextColour()
    else:
        wgt.WriteText(text)

    wgt.ShowPosition(wgt.GetLastPosition())
    obj.Refresh()


def init_statusbar(obj, widths=[-1, 170, 160], values=['', '', ''], **kwargs):
    sbar = obj.CreateStatusBar(len(widths))
    sbar.SetStatusWidths(widths)
    for i, v in enumerate(values):
        if v is None:
            continue

        sbar.SetStatusText(v, i)

    return sbar


def about_box(name='name', version='1.0', description='description',
              copyright='copyright', website='', licence='',
              icon=None, icon_fmt=None, developers=[], doc_writers=[],
              artists=[], tranlators=[], **kwargs):
    info = wx.AboutDialogInfo()
    if icon:
        if isinstance(icon, basestring):
            args = [icon]
            if icon_fmt:
                args.append(icon_fmt)

            info.SetIcon(wx.Icon(*args))
        else:
            info.SetIcon(icon)  # may be PyEmbeddedImage

    info.SetName(name)
    info.SetVersion(version)
    info.SetDescription(description)
    info.SetCopyright(copyright)
    if website:
        info.SetWebSite(website)

    if licence:
        info.SetLicence(licence)

    [info.AddDeveloper(developer) for developer in developers]
    [info.AddDocWriter(writer) for writer in doc_writers]
    [info.AddArtist(artist) for artist in artists]
    [info.AddTranslator(tranlator) for tranlator in tranlators]

    wx.AboutBox(info)


def init_timer(obj, timer_id, timer_func, miliseconds=-1, one_shot=False):
    timer = wx.Timer(obj, timer_id)
    obj.Bind(wx.EVT_TIMER, timer_func, id=timer_id)
    if miliseconds > 0:
        start_timer(timer, miliseconds, one_shot)

    return timer


def start_timer(timer, miliseconds=1000, one_shot=False):
    if timer.IsRunning():
        return

    timer.Start(int(miliseconds), one_shot)


def stop_timer(timer):
    if timer.IsRunning():
        timer.Stop()


def stop_timers(timers=[]):
    [stop_timer(timer) for timer in timers]


def update_clock_statusbar(sbar, ts_fmt='%d-%b-%Y %H:%M', idx=2):
    set_status_text(sbar, time.strftime(ts_fmt), idx)


def set_status_text(sbar, text, idx):
    sbar.SetStatusText(text, idx)


def get_copy_right(text=None):
    return text if text else '(C) Nypro & Jabil Shanghai TE Support'


def permission_login(parent=None, root_pass='guess',
                     caption='Security Check',
                     msg='Please enter password:'):
    dlg = wx.PasswordEntryDialog(parent, msg, caption)
    size = dlg.GetClientSize()
    dlg.SetMinClientSize(size)
    dlg.SetMaxClientSize(size)
    while 1:
        dlg.SetFocus()
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetValue() == root_pass:
                dlg.Destroy()
                return True

            dlg.SetValue('')
            dlg.SetFocus()
            continue

        dlg.Destroy()
        return False
