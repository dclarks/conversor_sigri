# -*- coding: utf-8 -*-

def classFactory(iface):
    from .conversor_sigri_plugin import ConversorSigriPlugin
    return ConversorSigriPlugin(iface)