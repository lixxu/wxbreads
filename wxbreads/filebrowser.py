#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import wx
import wx.lib.filebrowsebutton as filebrowse

KEY_MAPS = dict(id='id', pos='pos', size='size', style='style', name='name',
                label='labelText', button='buttonText', tooltip='toolTip',
                title='dialogTitle', start_directory='startDirectory',
                value='initialValue', mask='fileMask', mode='fileMode',
                call_back='changeCallback', label_width='labelWidth',
                )


def get_file_browse_default_args(history=False):
    return dict(id=-1, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.TAB_TRAVERSAL,
                label='File Entry:', button='Browse',
                tooltip='Type filename or browse to choose file',
                title='Choose a file',
                start_directory='.',
                value='',
                mask='*.*',
                mode='open',
                call_back=lambda x: x,
                label_width=0,
                name='fileBrowseButton',
                )


def fill_keywords(kwargs1):
    return {KEY_MAPS.get(k, k): v for k, v in kwargs1.items()}


def add_file_browse_field(parent, editable=True, **kwargs):
    kw = get_file_browse_default_args()
    kw.update(kwargs)
    kw.update(mode=wx.FD_OPEN if kw['mode'] == 'open' else wx.FD_SAVE)

    fbb = filebrowse.FileBrowseButton(parent, **fill_keywords(kw))
    fbb.textControl.SetEditable(editable)
    return fbb


def add_file_browse_history_field(parent, editable=True, history=None,
                                  file_list=[], **kwargs):
    kw = get_file_browse_default_args()
    kw.update(name='fileBrowseButtonWithHistory', history=history)
    kw.update(kwargs)
    kw.update(mode=wx.FD_OPEN if kw['mode'] == 'open' else wx.FD_SAVE)

    fbbh = filebrowse.FileBrowseButton(parent, **fill_keywords(kw))
    fbbh.textControl.SetEditable(editable)
    return fbbh


def add_dir_browse_field(parent, id=-1, pos=wx.DefaultPosition,
                         size=wx.DefaultSize, style=wx.TAB_TRAVERSAL,
                         label='Select a directory:', button='Browse',
                         tooltip='Type directory name or browse to select',
                         title='', history='', start_directory='.',
                         dialog_class=wx.DirDialog, new_directory=False,
                         name='dirBrowseButton', value='', editable=True,
                         call_back=None, **kwargs):

    dbb = filebrowse.DirBrowseButton(parent, id, pos=pos, size=size,
                                     style=style, labelText=label,
                                     buttonText=button,
                                     toolTip=tooltip,
                                     dialogTitle=title,
                                     startDirectory=start_directory,
                                     changeCallback=call_back,
                                     dialogClass=dialog_class,
                                     newDirectory=new_directory,
                                     name=name,
                                     )
    if value:
        dbb.SetValue(value, 0)

    dbb.textControl.SetEditable(editable)
    return dbb
