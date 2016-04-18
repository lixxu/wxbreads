#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import wx
import wx.richtext as rt

try:
    from agw import genericmessagedialog as gmd
except ImportError:
    import wx.lib.agw.genericmessagedialog as gmd

import utils as wxu
import windbreads.utils as wdu

'''Remark:
fsize/fstyle: 1st widget size/style
ssize/sstyle: 2nd widget size/sstyle
tsize/tstyle: 3rd widget size/tstyle
'''

ICONS = dict(info=wx.ICON_INFORMATION,
             i=wx.ICON_INFORMATION,
             warn=wx.ICON_WARNING,
             warning=wx.ICON_WARNING,
             w=wx.ICON_WARNING,
             error=wx.ICON_ERROR,
             e=wx.ICON_ERROR,
             question=wx.ICON_QUESTION,
             q=wx.ICON_QUESTION,
             exclamation=wx.ICON_EXCLAMATION,
             ex=wx.ICON_EXCLAMATION,
             )
DEFAULT_WILDCARD = 'All files|*'


def popup(parent=None, caption='caption', msg='', btn=wx.OK, icon='i',
          need_return=False, size=(-1, -1), **kwargs):
    icon = ICONS.get(icon, ICONS['i'])
    t = kwargs.get('t')
    if isinstance(msg, basestring):
        if not isinstance(msg, unicode):
            umsg = msg.decode(wdu.detect_encoding(msg)['encoding'])
        else:
            umsg = msg

    else:
        umsg = '{}'.format(msg)

    if t:
        umsg = wdu.ttt(umsg, t)
        title = wdu.ttt(caption, t)
    else:
        title = caption

    dlg = gmd.GenericMessageDialog(parent, umsg, title, btn | icon, size=size)
    help_label = kwargs.get('help_label', 'Help')
    ok_label = kwargs.get('ok_label', 'OK')
    cancel_label = kwargs.get('cancel_label', 'Cancel')
    yes_label = kwargs.get('yes_label', 'Yes')
    no_label = kwargs.get('no_label', 'No')
    if t:
        help_label = wdu.ttt(help_label, t)
        ok_label = wdu.ttt(ok_label, t)
        cancel_label = wdu.ttt(cancel_label, t)
        yes_label = wdu.ttt(yes_label, t)
        no_label = wdu.ttt(no_label, t)

    dlg.SetHelpLabel(help_label)
    dlg.SetOKLabel(ok_label)
    dlg.SetOKCancelLabels(ok_label, cancel_label)
    dlg.SetYesNoLabels(yes_label, no_label)
    dlg.SetYesNoCancelLabels(yes_label, no_label, cancel_label)
    dlg.SetMessage(umsg)

    if need_return:
        return dlg

    dlg.CenterOnParent()
    result = dlg.ShowModal()
    dlg.Destroy()
    return result


def quick_quit(self, **kwargs):
    """Quick handy method to ask for quit."""
    if hasattr(self, 'is_running') and self.is_running:
        caption = kwargs.pop('running_caption', 'Warning')
        msg = kwargs.pop('running_msg', 'Please stop current running task')
        icon = kwargs.pop('running_icon', 'w')
        popup(self, caption=caption, msg=msg, icon=icon, **kwargs)
        return

    if hasattr(self, 'opened_dlg') and self.opened_dlg > 0:
        caption = kwargs.pop('opened_caption', 'Warning')
        msg = kwargs.pop('opened_msg', 'Please close other dialogs')
        icon = kwargs.pop('opened_icon', 'w')
        popup(self, caption=caption, msg=msg, icon=icon, **kwargs)
        return

    answer = popup(self,
                   caption=kwargs.pop('ask_caption', 'Confirmation'),
                   msg=kwargs.pop('ask_msg', 'Are you sure to quit?'),
                   icon=kwargs.pop('ask_icon', 'q'),
                   btn=kwargs.pop('btn', wx.YES_NO | wx.NO_DEFAULT),
                   **kwargs)
    if answer == wx.ID_NO:
        return

    self.Hide()
    try:
        self.hm.UnhookKeyboard()
    except:
        pass

    try:
        self.hm.UnhookMouse()
    except:
        pass

    if hasattr(self, 'stop_timers'):
        self.stop_timers()

    if hasattr(self, 'tbicon') and self.tbicon is not None:
        self.tbicon.Destroy()

    self.Destroy()


def set_tooltip(wgt, tooltip='', t=None):
    if tooltip:
        wgt.SetToolTipString(wdu.ttt(tooltip, t=t))


def add_button(parent, id=-1, label='Button', size=(-1, -1), tooltip='',
               style=wx.NO_BORDER, font=None, fg=None, bg=None, icon=None,
               **kwargs):
    t = kwargs.pop('t', None)
    btn = wx.Button(parent, id, wdu.ttt(label, t), size=size)
    set_tooltip(btn, tooltip, t=t)
    if font:
        btn.SetFont(font)

    if fg:
        btn.SetForegroundColour(fg)

    if bg:
        btn.SetBackgroundColour(bg)

    if icon:
        btn.SetBitmap(icon, kwargs.get('side', wx.LEFT))
        btn.SetBitmapMargins(kwargs.get('margins', (2, 2)))

    return btn


def add_label(parent, id=-1, label='', font=None, size=(-1, -1),
              style=None, tooltip='', fg=None, bg=None, **kwargs):
    t = kwargs.get('t')
    nargs = dict(size=size)
    if style:
        nargs.update(style=style)

    lbl = wx.StaticText(parent, id, wdu.ttt(label, t), **nargs)
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
    if style and sty is not None:
        nargs.update(style=style | sty)
    elif style:
        nargs.update(style=style)
    elif sty is not None:
        nargs.update(style=sty)

    wgt = wx.TextCtrl(parent, id, '{}'.format(value), **nargs)
    set_tooltip(wgt, tooltip, t)
    if font:
        wgt.SetFont(font)

    if fg:
        wgt.SetForegroundColour(fg)

    return wgt


def add_richtext(parent, id=-1, value='', size=(-1, -1), style=wx.TE_MULTILINE,
                 readonly=True, **kwargs):
    if readonly:
        style |= wx.TE_READONLY

    return rt.RichTextCtrl(parent, id, value, size=size, style=style)


def add_checkbox(parent, id=-1, label='', size=(-1, -1), value=True,
                 tooltip='', font=None, fg=None, bg=None, **kwargs):
    t = kwargs.pop('t', None)
    wgt = wx.CheckBox(parent, id, wdu.ttt(label, t), size=size)
    set_tooltip(wgt, tooltip, t)
    if font:
        wgt.SetFont(font)

    if fg:
        wgt.SetForegroundColour(fg)

    if bg:
        wgt.SetBackgroundColour(bg)

    wgt.SetValue(value)
    return wgt


def add_path_picker(parent, id=-1, kind='dir', msg='Select a directory',
                    **kwargs):
    t = kwargs.pop('t', None)
    tooltip = kwargs.pop('tooltip', '')
    multiline = kwargs.pop('multiline', False)
    btn_label = kwargs.pop('btn_label', '')
    size = kwargs.pop('size', (-1, -1))
    prop = kwargs.pop('prop', 2)
    use_tc = kwargs.pop('use_tc', True)
    value = kwargs.pop('value', '')
    text_editable = kwargs.pop('text_editable', False)
    btn_enable = kwargs.pop('btn_enable', True)
    tc_bg = kwargs.pop('tc_bg', 'white')
    wgt_cls = wx.DirPickerCtrl if kind == 'dir' else wx.FilePickerCtrl
    if use_tc:
        kwargs.update(style=wx.DIRP_USE_TEXTCTRL)

    pc = wgt_cls(parent, id, message=wdu.ttt(msg, t), size=size, path=value,
                 **kwargs)
    if pc.HasTextCtrl():
        pc.SetTextCtrlProportion(prop)

    tc, btn = pc.Sizer.GetChildren()
    tc = tc.GetWindow()
    btn = btn.GetWindow()
    if multiline:
        tc.SetWindowStyle(wx.TE_MULTILINE)

    btn.SetLabel(wdu.ttt(btn_label or btn.GetLabel(), t))
    if tooltip:
        tooltip = wdu.ttt(tooltip, t)
        tc.SetToolTipString(tooltip)
        btn.SetToolTipString(tooltip)

    tc.SetEditable(text_editable)
    if tc_bg:
        tc.BackgroundColour = tc_bg

    btn.Enable(btn_enable)
    return pc, tc, btn


def add_dir_picker(parent, id=-1, msg='Select a directory', **kwargs):
    return add_path_picker(parent, id, kind='dir', msg=msg, **kwargs)


def add_file_picker(parent, id=-1, msg='Select a file', **kwargs):
    return add_path_picker(parent, id, kind='file', msg=msg, **kwargs)


def select_open_dir(parent, title='Select a directory',
                    style=wx.DD_DEFAULT_STYLE, **kwargs):
    t = kwargs.pop('t', None)
    dlg = wx.DirDialog(parent, wdu.ttt(title, t), style=style, **kwargs)
    folder = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
    dlg.Destroy()
    return folder


def select_open_file(parent, msg='Select a file', default_dir='',
                     default_file='', wildcard=DEFAULT_WILDCARD,
                     style=wx.OPEN | wx.FD_FILE_MUST_EXIST | wx.CHANGE_DIR,
                     multiple=False, **kwargs):
    if multiple:
        style = style | wx.MULTIPLE

    t = kwargs.pop('t', None)
    dlg = wx.FileDialog(parent, message=wdu.ttt(msg, t),
                        defaultDir=default_dir,
                        defaultFile=default_file,
                        wildcard=wdu.ttt(wildcard, t),
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
    dlg = wx.FileDialog(parent, message=wdu.ttt(msg, t),
                        defaultDir=default_dir,
                        defaultFile=default_file,
                        wildcard=wdu.ttt(wildcard, t),
                        style=style, **kwargs)
    path = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
    dlg.Destroy()
    return path


def get_sizer_flags(flags=''):
    flag = None
    for text in (flags or '').replace(' ', '').lower().split(','):
        if text in ('e', 'exp', 'expand'):
            f = wx.EXPAND
        elif text in ('l', 'left'):
            f = wx.LEFT
        elif text in ('r', 'right'):
            f = wx.RIGHT
        elif text in ('t', 'top'):
            f = wx.TOP
        elif text in ('b', 'bot', 'bottom'):
            f = wx.BOTTOM
        elif text in ('a', 'all'):
            f = wx.ALL
        elif text in ('sh', 'shaped'):
            f = wx.SHAPED
        elif text in ('fix', 'fixed'):
            f = wx.FIXED_MINSIZE
        elif text in ('hide', 'hidden'):
            f = wx.RESERVE_SPACE_EVEN_IF_HIDDEN
        elif text in ('ac', 'center', 'centre'):
            f = wx.ALIGN_CENTER
        elif text in ('al', 'a_left'):
            f = wx.ALIGN_LEFT
        elif text in ('ar', 'a_right'):
            f = wx.ALIGN_RIGHT
        elif text in ('at', 'a_top'):
            f = wx.ALIGN_TOP
        elif text in ('ab', 'a_bot', 'a_bottom'):
            f = wx.ALIGN_BOTTOM
        elif text in ('acv', 'a_center_v', 'a_centre_v'):
            f = wx.ALIGN_CENTER_VERTICAL
        elif text in ('ach', 'a_center_h', 'a_centre_h'):
            f = wx.ALIGN_CENTER_HORIZONTAL
        else:
            continue

        if flag is None:
            flag = f
        else:
            flag = flag | f

    if flag is None:
        flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP

    return flag


def pack(wgt, sizer='h', **kwargs):
    if sizer == 'h':
        sizer = wx.BoxSizer(wx.HORIZONTAL)
    elif sizer == 'v':
        sizer = wx.BoxSizer(wx.VERTICAL)

    kargs = dict(flag=get_sizer_flags(kwargs.get('flag')))
    border = kwargs.get('border', 3)
    if border:
        kargs.update(border=border)

    sizer.Add(wgt, kwargs.get('prop', 0), **kargs)
    return sizer


def sort_wgts(wgts=[], **kwargs):
    lst = []
    last_prop = kwargs.get('last_prop', 1)
    size = len(wgts)
    for i, wgt in enumerate(wgts, 1):
        if isinstance(wgt, (tuple, list)):
            lst.append(wgt)
        else:
            lst.append((wgt, last_prop if i == size else 0))

    return lst


def quick_pack(sizer=None, wgts=[], orient='h', **kwargs):
    if not sizer:
        return

    ws = sort_wgts(wgts, **kwargs)
    kargs = dict(flag=kwargs.get('flag'))
    border = kwargs.get('border', 3)
    if border:
        kargs.update(border=border)

    box = pack(ws[0][0], sizer=orient, prop=ws[0][1], **kargs)
    for wgt, pr in ws[1:]:
        pack(wgt, box, prop=pr, **kargs)

    pack(box, sizer, **kwargs)
    return box


def add_staticbox(parent, id=-1, label='', orient='v', **kwargs):
    sbox = wx.StaticBox(parent, id, wdu.ttt(label, kwargs.pop('t', None)))
    style = wx.VERTICAL if orient == 'v' else wx.HORIZONTAL
    sbsizer = wx.StaticBoxSizer(sbox, style)
    return sbox, sbsizer


def add_text_row(parent, sizer=None, label='', value='', fsize=(-1, -1),
                 ssize=(-1, -1), tooltip='', font=None, fg=None,
                 bg=None, multiline=False, **kwargs):
    t = kwargs.pop('t', None)
    nargs = dict(tooltip=tooltip, font=font, fg=fg, bg=bg, t=t)
    lbl = add_label(parent, label=label, size=fsize,
                    style=kwargs.get('fstyle'), **nargs)
    wgt = add_textctrl(parent, value=value, multiline=multiline,
                       style=kwargs.get('sstyle'), size=ssize, **nargs)
    quick_pack(sizer, wgts=[lbl, wgt], **kwargs)

    return lbl, wgt


def add_checkbox_row(parent, sizer=None, label='', fsize=(-1, -1),
                     ssize=(-1, -1), tooltip='', value=True, cb_label='',
                     font=None, fg=None, bg=None, **kwargs):
    t = kwargs.pop('t', None)
    nargs = dict(tooltip=tooltip, font=font, fg=fg, bg=bg, t=t)
    lbl = add_label(parent, label=label, size=fsize, **nargs)
    wgt = add_checkbox(parent, label=cb_label, value=value, size=ssize,
                       **nargs)
    quick_pack(sizer, wgts=[lbl, wgt], **kwargs)

    return lbl, wgt


def add_combobox(parent, sizer=None, label='', fsize=(-1, -1),
                 ssize=(-1, -1), fstyle=None, fg=None, font=None,
                 sstyle=wx.CB_DROPDOWN | wx.CB_SORT,
                 readonly=False, value='', choices=[],
                 **kwargs):
    t = kwargs.pop('t', None)
    if readonly and sstyle:
        sstyle = sstyle | wx.CB_READONLY

    lbl = None
    if label is not None:
        lbl = add_label(parent, label=label, size=fsize, font=font, fg=fg,
                        style=fstyle, t=t)

    wgt = wx.ComboBox(parent, -1, '{}'.format(value), choices=choices,
                      size=ssize, style=sstyle)
    quick_pack(sizer, wgts=[lbl, wgt], **kwargs)

    return lbl, wgt


def add_choice(parent, sizer=None, label='', fsize=(-1, -1), ssize=(-1, -1),
               fstyle=None, fg=None, font=None, value='', choices=[],
               **kwargs):
    t = kwargs.pop('t', None)
    lbl = None
    if label is not None:
        lbl = add_label(parent, label=label, size=fsize, font=font, fg=fg,
                        style=fstyle, t=t)

    wgt = wx.Choice(parent, -1, choices=choices, size=ssize)
    wgt.SetSelection(choices.index(value) if value in choices else 0)
    quick_pack(sizer, wgts=[lbl, wgt], **kwargs)

    return lbl, wgt


def add_datepicker(parent, sizer=None, label='', fsize=(-1, -1),
                   ssize=(-1, -1), tooltip='', value='', font=None, fg=None,
                   bg=None, style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY,
                   **kwargs):
    t = kwargs.pop('t', None)
    nargs = dict(size=fsize, tooltip=tooltip, font=font, fg=fg, bg=bg, t=t)
    lbl = add_label(parent, label=label, **nargs)
    wgt = wx.DatePickerCtrl(parent, dt=value, size=ssize, style=style)
    quick_pack(sizer, wgts=[lbl, wgt], **kwargs)

    return lbl, wgt


def add_open_dialog(parent, sizer, label='Select folder', value='',
                    fsize=(-1, -1), ssize=(-1, -1), tsize=(-1, -1),
                    tooltip='', btn_label='Browse...', btn_id=None,
                    fg=None, multiline=False, **kwargs):
    t = kwargs.pop('t', None)
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

    quick_pack(sizer, wgts=[(lbl, 0), (txt, 1), (btn, 0)], **kwargs)
    return lbl, txt, btn


def quick_open_file(parent, sizer, label='Select File', value='', fg=None,
                    fsize=(-1, -1), ssize=(-1, -1), tsize=(-1, -1), **kwargs):
    lbl = add_label(parent, label=label, size=fsize, fg=fg, t=kwargs.get('t'))
    fp, tc, btn = add_file_picker(parent, size=ssize, value=value, **kwargs)
    quick_pack(sizer, wgts=[lbl, fp])
    return lbl, fp, tc, btn


def quick_open_folder(parent, sizer, label='Select Folder', value='', fg=None,
                      fsize=(-1, -1), ssize=(-1, -1), tsize=(-1, -1),
                      **kwargs):
    lbl = add_label(parent, label=label, size=fsize, fg=fg, t=kwargs.get('t'))
    fp, tc, btn = add_dir_picker(parent, size=ssize, value=value, **kwargs)
    quick_pack(sizer, wgts=[lbl, fp])
    return lbl, fp, tc, btn


def add_line(parent, id=-1, size=(-1, -1), orient='h'):
    style = wx.LI_HORIZONTAL if orient == 'h' else wx.LI_VERTICAL
    return wx.StaticLine(parent, id, size=(-1, -1), style=style)


def add_ok_buttons(parent, sizer, id=-1, size=(100, 40), ok_text='&OK',
                   cancel_text='&Cancel', border=5, **kwargs):
    t = kwargs.pop('t', None)
    pack_line = kwargs.pop('pack_line', True)
    if pack_line:
        sl = add_line(parent, id)

    ok_btn = add_button(parent, wx.ID_OK, ok_text, size=size, t=t)
    ok_btn.SetDefault()
    cancel_btn = add_button(parent, wx.ID_CANCEL, cancel_text, size=size, t=t)

    btn_sizer = wx.StdDialogButtonSizer()
    btn_sizer.AddButton(ok_btn)
    btn_sizer.AddButton(cancel_btn)
    btn_sizer.Realize()

    if pack_line:
        pack(sl, sizer, flag='e,t', border=15)

    pack(btn_sizer, sizer, prop=1, flag='ac,a', border=border)
    return ok_btn, cancel_btn


def init_statusbar(obj, widths=[-1, 170, 160], values=['', '', ''], **kwargs):
    t = kwargs.pop('t', None)
    sbar = obj.CreateStatusBar(len(widths))
    sbar.SetStatusWidths(widths)
    for i, v in enumerate(values):
        if v is None:
            continue

        sbar.SetStatusText(wdu.ttt(v, t), i)

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

    info.SetName(wdu.ttt(name, t))
    info.SetVersion(wdu.ttt(version, t))
    info.SetDescription(wdu.ttt(description, t))
    info.SetCopyright(wdu.ttt(copyright, t))
    if website:
        info.SetWebSite(website)

    if licence:
        info.SetLicence(licence)

    [info.AddDeveloper(developer) for developer in developers]
    [info.AddDocWriter(writer) for writer in doc_writers]
    [info.AddArtist(artist) for artist in artists]
    [info.AddTranslator(tranlator) for tranlator in tranlators]
    wx.AboutBox(info)


def quick_about(*args, **kwargs):
    fmt = kwargs.pop('fmt',
                     '{}\n\nPlatform:\nPython {}\nwxPython {} ({})\n{}\n\n')
    t = kwargs.get('t', None)
    copyright = kwargs.pop('copyright', wdu.get_copy_right())
    author = kwargs.pop('author', 'Author')
    remark = kwargs.pop('remark', 'about this tool')
    description = fmt.format(wdu.ttt(remark, t), sys.version.split()[0],
                             wx.VERSION_STRING, ', '.join(wx.PlatformInfo[1:]),
                             wdu.get_platform_info())
    about_info = dict(description=description,
                      copyright=copyright.replace('&', '&&'),
                      developers=[author],
                      doc_writers=[author],
                      **kwargs)
    about_box(**about_info)


def init_timer(self, timer_id, timer_func, miliseconds=-1, one_shot=False):
    timer = wx.Timer(self, timer_id)
    self.Bind(wx.EVT_TIMER, timer_func, id=timer_id)
    if miliseconds > 0:
        wxu.start_timer(timer, miliseconds, one_shot)

    return timer


def quick_entry(parent=None, caption='', msg='Enter', password=True, **kwargs):
    entry_cls = wx.PasswordEntryDialog if password else wx.TextEntryDialog
    t = kwargs.pop('t', None)
    root_pass = kwargs.pop('root_pass', 'guess')
    ok_label = kwargs.pop('ok_label', None)
    cancel_label = kwargs.pop('cancel_label', None)
    dlg = entry_cls(parent, wdu.ttt(msg, t), wdu.ttt(caption, t))
    # update button labels for i18n
    try:
        btn_sizer = dlg.Sizer.GetChildren()[2].Sizer.GetChildren()[1].Sizer
        items = btn_sizer.GetChildren()
        ok_btn, cancel_btn = items[1].GetWindow(), items[2].GetWindow()
        ok_btn.SetLabel(wdu.ttt(ok_label or ok_btn.GetLabel(), t))
        cancel_btn.SetLabel(wdu.ttt(cancel_label or cancel_btn.GetLabel(), t))
    except:
        pass

    size = dlg.GetClientSize()
    dlg.SetMinClientSize(size)
    dlg.SetMaxClientSize(size)
    while 1:
        dlg.SetFocus()
        if dlg.ShowModal() == wx.ID_OK:
            text = dlg.GetValue()
            if password:
                if text == root_pass:
                    dlg.Destroy()
                    return True

            else:
                text = text.strip()
                if text:
                    dlg.Destroy()
                    return text

            dlg.SetValue('')
            dlg.SetFocus()
            continue

        dlg.Destroy()
        return False if password else ''


def quick_password_entry(parent=None, caption='Security Check',
                         msg='Please enter password:', **kwargs):
    return quick_entry(parent, caption=caption, msg=msg, **kwargs)


def quick_text_entry(parent=None, caption='Enter Something',
                     msg='Please enter something: ', **kwargs):
    return quick_entry(parent, caption=caption, msg=msg, password=False,
                       **kwargs)


def quick_choice(parent=None, msg='Please select', caption='Please select',
                 **kwargs):
    t = kwargs.pop('t', None)
    choices = kwargs.pop('choices', [])
    valid_choices = kwargs.pop('valid_choices', [])
    style = kwargs.pop('style', wx.CHOICEDLG_STYLE)
    dlg = wx.SingleChoiceDialog(parent, wdu.ttt(msg, t), wdu.ttt(caption, t),
                                choices, style)
    ok_label = kwargs.pop('ok_label', None)
    cancel_label = kwargs.pop('cancel_label', None)
    # update button labels for i18n
    try:
        btn_sizer = dlg.Sizer.GetChildren()[2].Sizer.GetChildren()[1].Sizer
        items = btn_sizer.GetChildren()
        ok_btn, cancel_btn = items[1].GetWindow(), items[2].GetWindow()
        ok_btn.SetLabel(wdu.ttt(ok_label or ok_btn.GetLabel(), t))
        cancel_btn.SetLabel(wdu.ttt(cancel_label or cancel_btn.GetLabel(), t))
    except:
        pass

    while 1:
        if dlg.ShowModal() == wx.ID_OK:
            selected = dlg.GetStringSelection()
            if selected in valid_choices:
                dlg.Destroy()
                return selected

            continue

        break

    dlg.Destroy()
    return None
