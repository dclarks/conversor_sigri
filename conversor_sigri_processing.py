import math
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsWkbTypes,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFields,
    QgsField,
    QgsCoordinateReferenceSystem
)
from PyQt5.QtCore import QVariant

def utm_to_geo_inpe(x, y, semi_eixo, achat, lon_mc_deg):
    """Lógica exata do código INPE para conversão UTM -> Geográficas"""
    lon_mc = math.radians(lon_mc_deg)
    k0 = 1.0 - (1.0 / 2500.0)
    equad = 2.0 * achat - (achat ** 2)
    elinquad = equad / (1.0 - equad)
    e1 = (1.0 - math.sqrt(1.0 - equad)) / (1.0 + math.sqrt(1.0 - equad))
    
    m = (y - 10000000.0) / k0
    mi = m / (semi_eixo * (1.0 - equad / 4.0 - 3.0 * equad**2 / 64.0 - 5.0 * equad**3 / 256.0))
    
    aux6 = (3.0 * e1 / 2.0 - 27.0 * e1**3 / 32.0) * math.sin(2.0 * mi)
    aux7 = (21.0 * e1**2 / 16.0 - 55.0 * e1**4 / 32.0) * math.sin(4.0 * mi)
    aux8 = (151.0 * e1**3 / 96.0) * math.sin(6.0 * mi)
    
    lat1 = mi + aux6 + aux7 + aux8
    c1 = elinquad * (math.cos(lat1) ** 2)
    t1 = math.tan(lat1) ** 2
    n1 = semi_eixo / math.sqrt(1.0 - equad * (math.sin(lat1) ** 2))
    r1 = semi_eixo * (1.0 - equad) / math.sqrt((1.0 - equad * math.sin(lat1)**2)**3)
    d = (x - 500000.0) / (n1 * k0)
    
    aux9 = (5.0 + 3.0 * t1 + 10.0 * c1 - 4.0 * c1 * c1 - 9.0 * elinquad) * (d ** 4) / 24.0
    aux10 = (61.0 + 90.0 * t1 + 298.0 * c1 + 45.0 * t1 * t1 - 252.0 * elinquad - 3.0 * c1 * c1) * (d ** 6) / 720.0
    lat_rad = lat1 - (n1 * math.tan(lat1) / r1) * (d * d / 2.0 - aux9 + aux10)
    
    aux11 = d - (1.0 + 2.0 * t1 + c1) * (d ** 3) / 6.0
    aux12 = (5.0 - 2.0 * c1 + 28.0 * t1 - 3.0 * c1 * c1 + 8.0 * elinquad + 24.0 * t1 * t1) * (d ** 5) / 120.0
    lon_rad = lon_mc + (aux11 + aux12) / math.cos(lat1)
    
    return math.degrees(lat_rad), math.degrees(lon_rad)


class ConversorSigriAlgorithm(QgsProcessingAlgorithm):
    INPUT_FILE = 'INPUT_FILE'
    OUTPUT_FILE = 'OUTPUT_FILE'
    MC = 'MC'
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def tr(self, string):
        return string

    def createInstance(self):
        return ConversorSigriAlgorithm()

    def name(self):
        return 'conversorsigri'

    def displayName(self):
        return self.tr('Conversor UTM para SIG-RI (Lon,Lat;)')

    def group(self):
        return self.tr('Topografia e Agrimensura')

    def groupInstance(self):
        return self.tr('Topografia e Agrimensura')

    def groupId(self):
        return 'topografia_agrimensura'

    def shortHelpString(self):
        return self.tr(
            "Converte arquivos de texto contendo coordenadas UTM (Norte, Este) para o formato geográfico exigido pelo SIG-RI (lon,lat;).\n\n"
            "ONDE ENCONTRAR:\n"
            "O plugin fica instalado diretamente na Caixa de Ferramentas de Processamento (ícone de engrenagem), que pode ser ativada através do menu superior em 'Processamento' -> 'Caixa de Ferramentas'.\n\n"
            "CRÉDITOS E AUTORIA:\n"
            "A lógica matemática e o elipsoide de conversão utilizados neste algoritmo foram baseados estritamente nas equações e no código PHP oficial disponibilizado pelo INPE (Instituto Nacional de Pesquisas Espaciais).\n\n"
            "Desenvolvido e adaptado para o ecossistema QGIS."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_FILE,
                self.tr('Arquivo de texto de entrada (Txt/Csv)'),
                behavior=QgsProcessingParameterFile.File
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MC,
                self.tr('Meridiano Central (MC)'),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=-51,
                minValue=-177,
                maxValue=177
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_FILE,
                self.tr('Salvar arquivo TXT formatado SIG-RI'),
                fileFilter='Arquivos de Texto (*.txt)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LAYER,
                self.tr('Camada vetorial de pontos resultante'),
                type=QgsProcessing.TypeVectorPoint
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_path = self.parameterAsFile(parameters, self.INPUT_FILE, context)
        output_path = self.parameterAsFileOutput(parameters, self.OUTPUT_FILE, context)
        mc_deg = self.parameterAsInt(parameters, self.MC, context)

        a, f = 6378137.0, 1 / 298.257222101
        
        fields = QgsFields()
        fields.append(QgsField("Vertice", QVariant.String))
        fields.append(QgsField("Norte_UTM", QVariant.Double))
        fields.append(QgsField("Este_UTM", QVariant.Double))
        fields.append(QgsField("Format_SIG", QVariant.String))

        crs_saida = QgsCoordinateReferenceSystem("EPSG:4674")
        
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_LAYER,
            context,
            fields,
            QgsWkbTypes.Point, 
            crs_saida
        )

        processados_strings = []
        linhas_validas = 0

        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f_in:
            for idx, linha in enumerate(f_in):
                linha = linha.strip()
                if not delete_line if 'delete_line' in locals() else not linha or linha.startswith('#'): continue
                
                linha_limpa = linha.replace('\t', ' ')
                
                if linha_limpa.count(',') >= 2 and not ' ' in linha_limpa:
                    parts = [p.strip() for p in linha_limpa.split(',')]
                elif ',' in linha_limpa and linha_limpa.count(',') == 1 and not ' ' in linha_limpa:
                    parts = [p.strip() for p in linha_limpa.split(',')]
                else:
                    parts = linha_limpa.split()

                nome_vertice = f"P_{idx}"
                if len(parts) >= 3:
                    nome_vertice = parts[0]
                    str_norte = parts[1]
                    str_este = parts[2]
                elif len(parts) == 2:
                    str_norte = parts[0]
                    str_este = parts[1]
                else:
                    continue

                try:
                    norte = float(str_norte.replace(',', '.'))
                    este = float(str_este.replace(',', '.'))
                    
                    if este > 1000000 or norte < 100000:
                        norte, este = este, norte
                    
                    lat, lon = utm_to_geo_inpe(este, norte, a, f, mc_deg)
                    coord_formatada = f"{lon:.15f},{lat:.15f}"
                    processados_strings.append(coord_formatada)

                    f_feature = QgsFeature()
                    f_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
                    f_feature.setFields(fields)
                    f_feature.setAttributes([nome_vertice, norte, este, coord_formatada])
                    
                    sink.addFeature(f_feature)
                    linhas_validas += 1

                except ValueError:
                    continue

        if processados_strings and output_path:
            with open(output_path, 'w', encoding='utf-8') as f_out:
                for i, coord in enumerate(processados_strings):
                    if i < len(processados_strings) - 1:
                        f_out.write(coord + ";\n")
                    else:
                        f_out.write(coord)

        return {self.OUTPUT_LAYER: dest_id, self.OUTPUT_FILE: output_path}