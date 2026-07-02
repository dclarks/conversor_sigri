# -*- coding: utf-8 -*-

from qgis.core import QgsApplication, QgsProcessingProvider
from .conversor_sigri_processing import ConversorSigriAlgorithm

class ConversorSigriProvider(QgsProcessingProvider):
    """Provedor que cria a categoria dentro da Caixa de Ferramentas"""
    
    def __init__(self):
        super().__init__()

    def id(self):
        return 'topografia_sigri_provider'

    def name(self):
        return 'Topografia e Agrimensura'

    def icon(self):
        return QgsProcessingProvider.icon(self)

    def loadAlgorithms(self):
        # Adiciona o seu algoritmo dentro deste provedor
        self.addAlgorithm(ConversorSigriAlgorithm())


class ConversorSigriPlugin(object):
    """Classe principal do Plugin que o QGIS gerencia"""

    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initGui(self):
        # Cria e registra o provedor de forma moderna e compatível com o QGIS 3.40
        self.provider = ConversorSigriProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        # Remove o provedor ao desativar o plugin, limpando a interface
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)