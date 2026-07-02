# Conversor UTM para SIG-RI - MAPA DO REGISTRO DE IMÓVEIS DO BRASIL (Plugin QGIS)

Este plugin automatiza a conversão de coordenadas UTM (Projetadas) para coordenadas Geográficas textuais formatadas no padrão exato exigido para importação no sistema **SIG-RI** (`lon,lat;`).

## 📌 Onde encontrar no QGIS
Após a instalação, a ferramenta ficará disponível na sua **Caixa de Ferramentas de Processamento** (ícone de engrenagem lateral). 
Caso ela não esteja aparecendo, ative-a no menu superior em: `Processamento` -> `Caixa de Ferramentas`. Uma nova categoria chamada **Topografia e Agrimensura** será criada.

---

## 📋 Formato do Arquivo de Entrada (.txt ou .csv)

O conversor possui filtros inteligentes para identificar as colunas e os separadores automaticamente. Ele aceita arquivos com os vértices nomeados ou apenas as coordenadas.

### Opção 1: Vértice, Norte, Este (Recomendado)
Pode ser separado por **vírgulas**, **espaços** ou **tabulações**. O separador decimal pode ser tanto **ponto** quanto **vírgula**.
```text
P1,7012345.67,345678.90
P2,7012346,12,345679,45
P3 7012347.89 345680.12
