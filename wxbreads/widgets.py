#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import wx
try:
    from agw import genericmessagedialog as gmd
except ImportError:
    import wx.lib.agw.genericmessagedialog as gmd

import utils
import windbreads.utils as wdutils

'''Remark:
fsize/fstyle: 1st widget size/style
ssize/sstyle: 2nd widget size/sstyle
tsize/tstyle: 3rd widget size/tstyle
'''

ICONS = dict(info=wx.ICON_INFORMATION,
             warn=wx.ICON_WARNING,
             warning=wx.ICON_WARNING,
             error=wx.ICON_ERROR,
             question=wx.ICON_QUESTION,
             exclamation=wx.ICON_EXCLAMATION,
             )
DEFAULT_WILDCARD = 'All files|*'


def popup(parent=None, caption='caption', msg='', btn=wx.OK,
          icon='info', need_return=False, size=(-1, -1), **kwargs):
    t = kwargs.get('t')
    icon = ICONS.get(icon, ICONS['info'])
    dlg = gmd.GenericMessageDialog(parent,
                                   wdutils.tr_text('{}'.format(msg), t),
                                   wdutils.tr_text(caption, t),
                                   btn | icon, size=size)
    if need_return:
        return dlg

    dlg.CenterOnParent()
    result = dlg.ShowModal()
    dlg.Destroy()
    return result


def set_tooltip(wgt, tooltip='', t=None):
    if tooltip:
        wgt.SetToolTipString(wdutils.tr_text(tooltip, t=t))


def add_button(parent, id=-1, label='Button', size=(-1, -1), tooltip='',
               style=wx.NO_BORDER, font=None, fg=None, bg=None, **kwargs):
    t = kwargs.get('t')
    btn = wx.Button(parent, id, wdutils.tr_text(label, t), size=size)
    set_tooltip(btn, tooltip, t=t)
    if font:
        btn.SetFont(font)

    if fg:
        btn.SetForegroundColour(fg)

    if bg:
        btn.SetBackgroundColour(bg)

    return btn


def add_label(parent, id=-1, label='', font=None, size=(-1, -1),
              style=None, tooltip='', fg=None, bg=None, **kwargs):
    t = kwargs.get('t')
    nargs = dict(size=size)
    if style:
        nargs.update(style=style)

    lbl = wx.StaticText(parent, id, wdutils.tr_text(label, t), **nargs)
    set_tooltip(lbl, tooltip, t)
    if font:
        lbl.SetFont(font)

    if fg:
        lbl.SetForegroundColour(fg)

    if bg:
        lbl.SetBackgroundColour(bg)

    return lbl


def add_textctrl(parent, id=-1, value='', size=(-1, -1), font=None,
                 style=None, tooltip='', fg=None, bg=None,
                 multiline=False, **kwargs):
    t = kwargs.pop('t', None)
    nargs = dict(size=size)
    sty = wx.TE_MULTILINE if multiline else None
    if style and sty:
        nargs.update(style=style | sty)
    elif style:
        nargs.update(style=style)
    elif sty:
        nargs.update(style=sty)

    wgt = wx.TextCtrl(parent, id, '{}'.format(value), **nargs)
    set_tooltip(wgt, tooltip, t)
    if font:
        wgt.SetFont(font)

    if fg:
        wgt.SetForegroundColour(fg)

    return wgt


def add_checkbox(parent, id=-1, label='', size=(-1, -1), value=True,
                 tooltip='', font=None, fg=None, bg=None, **kwargs):
    t = kwargs.pop('t', None)
    wgt = wx.CheckBox(parent, id, wdutils.tr_text(label, t), size=size)
    set_tooltip(wgt, tooltip, t)
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
    t = kwargs.pop('t', None)
    dlg = wx.DirDialog(parent, wdutils.tr_text(title, t), style=style, **kwargs)
    folder = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
    dlg.Destroy()
    return folder


def select_open_file(parent, msg='Choose a file', default_dir='',
                     default_file='', wildcard=DEFAULT_WILDCARD,
                     style=wx.OPEN | wx.FD_FILE_MUST_EXIST | wx.CHANGE_DIR,
                     multiple=False, **kwargs):
    if multiple:
        style = style | wx.MULTIPLE

    t = kwargs.pop('t', None)
    dlg = wx.FileDialog(parent, message=wdutils.tr_text(msg, t),
                        defaultDir=default_dir,
                        defaultFile=default_file, wildcard=wildcard,
                        style=style, **kwargs)

    paths = dlg.GetPaths() if dlg.ShowModal() == wx.ID_OK else []
    dlg.Destroy()
    if paths:
        return paths if multiple else paths[0]

    return None


def select_save_file(parent, msg='Save file as...', default_dir='',
                     default_file='', wildcard=DEFAULT_WILDCARD,
                     style=wx.SAVE | wx.FD_OVERWRITE_PROMPT | wx.CHANGE_DIR,
                     **kwargs):
    t = kwargs.pop('t', None)
    dlg = wx.FileDialog(parent, message=wdutils.tr_text(msg, t),
                        defaultDir=default_dir,
                        defaultFile=default_file, wildcard=wildcard,
                        style=style, **kwargs)
    path = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
    dlg.Destroy()
    return path


def add_quick_sizer(sizer=None, wgts=[], oritent='h', prop=0, border=5,
                    **kwargs):
    if not sizer:
        return

    box = wx.BoxSizer(wx.HORIZONTAL if oritent == 'h' else wx.VERTICAL)
    for wgt, prop in wgts[:-1]:
        box.Add(wgt, prop, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, border)

    if len(wgts) > 1:
        box.Add(wgts[-1][0], wgts[-1][1], wx.ALIGN_LEFT | wx.ALL | wx.EXPAND,
                border)

    sizer.Add(box, prop, wx.EXPAND | wx.ALL, border)
    return box


def add_text_row(parent, sizer=None, label='', value='', fsize=(-1, -1),
                 ssize=(-1, -1), border=5, tooltip='', font=None, fg=None,
                 bg=None, multiline=False, **kwargs):
    t = kwargs.get('t', None)
    nargs = dict(tooltip=tooltip, font=font, fg=fg, bg=bg, t=t)
    lbl = add_label(parent, label=label, size=fsize,
                    style=kwargs.get('fstyle'), **nargs)
    wgt = add_textctrl(parent, value=value, multiline=multiline,
                       style=kwargs.get('sstyle'), size=ssize, **nargs)
    add_quick_sizer(sizer, wgts=[(lbl, 0), (wgt, 1)], border=border)

    return lbl, wgt


def add_checkbox_row(parent, sizer=None, label='', fsize=(-1, -1),
                     ssize=(-1, -1), tooltip='', value=True, cb_label='',
                     font=None, fg=None, bg=None, border=5, **kwargs):
    t = kwargs.get('t', None)
    nargs = dict(tooltip=tooltip, font=font, fg=fg, bg=bg, t=t)
    lbl = add_label(parent, label=label, size=fsize, **nargs)
    wgt = add_checkbox(parent, label=cb_label, value=value, size=ssize,
                       **nargs)
    add_quick_sizer(sizer, wgts=[(lbl, 0), (wgt, 1)], border=border)

    return lbl, wgt


def add_combobox(parent, sizer=None, label='ComboBox', fsize=(-1, -1),
                 ssize=(-1, -1), fstyle=None, fg=None, font=None,
                 style=wx.CB_DROPDOWN | wx.CB_SORT,
                 readonly=False, value='', choices=[], border=5,
                 **kwargs):
    t = kwargs.get('t', None)
    if readonly and style:
        style = style | wx.CB_READONLY

    lbl = None
    if label is not None:
        lbl = add_label(parent, label=label, size=fsize, font=font, fg=fg, t=t,
                        style=fstyle)

    wgt = wx.ComboBox(parent, -1, value, choices=choices, size=ssize,
                      style=style)
    add_quick_sizer(sizer, wgts=[(lbl, 0), (wgt, 1)], border=border)

    return lbl, wgt


def add_datepicker(parent, sizer, label='Date', fsize=(-1, -1), ssize=(-1, -1),
                   tooltip='', value='', font=None, fg=None, bg=None,
                   style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY,
                   border=5, **kwargs):
    t = kwargs.get('t', None)
    nargs = dict(size=fsize, tooltip=tooltip, font=font, fg=fg, bg=bg, t=t)
    lbl = add_label(parent, label=label, **nargs)
    wgt = wx.DatePickerCtrl(parent, dt=value, size=ssize, style=style)
    add_quick_sizer(sizer, wgts=[(lbl, 0), (wgt, 1)], border=border)

    return lbl, wgt


def add_open_dialog(parent, sizer, label='Select folder', value='',
                    fsize=(-1, -1), ssize=(-1, -1), tsize=(-1, -1),
                    tooltip='', border=5, btn_label='Browse', btn_id=None,
                    fg=None, multiline=False, **kwargs):
    t = kwargs.get('t', None)
    lbl = add_label(parent, label=label, size=fsize, t=t)
    txt = add_textctrl(parent, value=value, size=ssize, multiline=multiline,
                       t=t)
    set_tooltip(txt, tooltip, t)
    nargs = dict(label=btn_label, size=tsize, t=t)
    if btn_id:
        nargs.update(id=btn_id)

    btn = add_button(parent, **nargs)
    if tooltip:
        btn.SetToolTipString(tooltip)

    add_quick_sizer(sizer, wgts=[(lbl, 0), (txt, 1), (btn, 0)], border=border)
    return lbl, txt, btn


def add_ok_buttons(parent, sizer, id=-1, size=(100, 40), ok_text='&OK',
                   cancel_text='&Cancel', border=5, **kwargs):
    t = kwargs.pop('t', None)
    line = wx.StaticLine(parent, id, size=(-1, -1), style=wx.LI_HORIZONTAL)

    ok_btn = add_button(parent, wx.ID_OK, ok_text, size=size, t=t)
    ok_btn.SetDefault()
    cancel_btn = add_button(parent, wx.ID_CANCEL, cancel_text, size=size, t=t)

    btn_sizer = wx.StdDialogButtonSizer()
    btn_sizer.AddButton(ok_btn)
    btn_sizer.AddButton(cancel_btn)
    btn_sizer.Realize()

    style = wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP
    sizer.Add(line, 0, style, border)

    style = wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL
    sizer.Add(btn_sizer, 1, style, border)
    return ok_btn, cancel_btn


def init_statusbar(obj, widths=[-1, 170, 160], values=['', '', ''], **kwargs):
    t = kwargs.pop('t', None)
    sbar = obj.CreateStatusBar(len(widths))
    sbar.SetStatusWidths(widths)
    for i, v in enumerate(values):
        if v is None:
            continue

        sbar.SetStatusText(wdutils.tr_text(v, t), i)

    return sbar


def about_box(name='name', version='1.0', description='description',
              copyright='copyright', website='', licence='',
              icon=None, icon_fmt=None, developers=[], doc_writers=[],
              artists=[], tranlators=[], **kwargs):
    t = kwargs.pop('t', None)
    info = wx.AboutDialogInfo()
    if icon:
        if isinstance(icon, basestring):
            args = [icon]
            if icon_fmt:
                args.append(icon_fmt)

            info.SetIcon(wx.Icon(*args))
        else:
            info.SetIcon(icon)  # may be PyEmbeddedImage

    info.SetName(wdutils.tr_text(name, t))
    info.SetVersion(wdutils.tr_text(version, t))
    info.SetDescription(wdutils.tr_text(description, t))
    info.SetCopyright(wdutils.tr_text(copyright, t))
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
        utils.start_timer(timer, miliseconds, one_shot)

    return timer
