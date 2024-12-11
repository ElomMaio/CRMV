#Bloco 1
import pandas as pd
import json
import re
import os
from pathlib import Path
BASE_DIR = Path(os.getcwd())

# Abrir e carregar o arquivo JSON
with open('processos_todos.json', encoding='UTF-8') as f:
    data = json.load(f)

# Construir a estrutura tabular com iteração
data_tabular = []
for item in data:
    tipo_animal = item.get('Tipo_de_animal', ['Não especificado'])
    tipo_procedimento = item.get('Tipo_de_procedimento', ['Não especificado'])
    artigos_infringidos = item.get('Artigos_infringidos', ['Não especificado'])
    documentos_elaborados = item.get('Documentos_elaborados', ['Não especificado'])
    
    for animal in tipo_animal:
        for procedimento in tipo_procedimento:
            for artigo in artigos_infringidos:
                for documento in documentos_elaborados:
                    n_processo = re.sub(r"[^\d/-]+", "", item.get('Numero_processo_etico', ''))
                    if not n_processo:
                        n_processo = 'Não especificado'
                    n_processo = n_processo[1::] if n_processo.startswith('-') else n_processo
                    data_tabular.append({
                        'numero_processo': n_processo,
                        'denunciante': item.get('Denunciante', 'Não especificado'),
                        'motivacao_denuncia': item.get('Motivacao_da_denuncia', 'Não especificado'),
                        'categoria': item.get('Categoria', 'Não especificado'),
                        'falha_profissional': item.get('Falha_profissional', 'Não especificado'),
                        'procedencia': item.get('Procedencia', 'Não especificado'),
                        'procedencia_mantida': item.get('Procedencia_mantida', 'Não especificado'),
                        'tipo_animal': animal,
                        'tipo_procedimento': procedimento,
                        'artigo_infringido': artigo,
                        'documento_elaborado': documento
                    })

# Criar o DataFrame
df = pd.DataFrame(data_tabular)

# Filtrar processos procedentes
df_procedentes = df[df['procedencia'] == True]
df_procedentes.to_csv(BASE_DIR / 'procedentes.csv', index=True, encoding='utf-8')

#Precisa mexer nesse código, pois ele não está considerando categoria como lista

#Bloco 2
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from collections import Counter
import json

class AnalisadorProcessosEticos:
    def __init__(self, arquivo_json: str):
        self.dados = self._carregar_json(arquivo_json)
        self.dados = self._filtrar_processos_procedentes()  # Filtra os processos improcedentes

    def _carregar_json(self, arquivo_json: str) -> list:
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo {arquivo_json} não encontrado")
            return []
        except json.JSONDecodeError:
            print(f"Erro: Formato JSON inválido em {arquivo_json}")
            return []

    def _filtrar_processos_procedentes(self) -> list:
        # Filtra a lista de dados para incluir apenas processos procedentes
        return [processo for processo in self.dados if processo.get('Procedencia', True)]

    def obter_estatisticas(self) -> dict:
        total = len(self.dados)
        procedentes = sum(1 for caso in self.dados if caso.get('Procedencia', True))
        return {
            'total_processos': total,
            'processos_procedentes': procedentes,
            'processos_improcedentes': total - procedentes
        }

    def categorias_mais_comuns(self) -> list:
        categorias = []
        for processo in self.dados:
            categoria = processo.get('Categoria', '')
            if isinstance(categoria, str) and categoria:
                categorias.extend([cat.strip() for cat in categoria.split(',')])
            elif isinstance(categoria, list):
                categorias.extend(categoria)
        return Counter(categorias).most_common()

    def distribuicao_tipos_animais(self) -> dict:
        tipos_animais = []
        for processo in self.dados:
            tipos = processo.get('Tipo_de_animal', [])
            tipos_animais.extend(tipos)
        return dict(Counter(tipos_animais))

    def distribuicao_procedimentos(self) -> dict:
        procedimentos = []
        for processo in self.dados:
            procedimento = processo.get('Tipo_de_procedimento', '')
            if isinstance(procedimento, list):
                procedimentos.extend(procedimento)
            elif procedimento:
                procedimentos.append(procedimento)
        return dict(Counter(procedimentos))

    def distribuicao_documentos(self) -> dict:
        documentos = []
        for processo in self.dados:
            documento = processo.get('Documentos_elaborados', [])
            documentos.extend(documento)
        return dict(Counter(documentos))

    def obter_numeros_processos_unicos(self) -> list:
        numeros_processos = set()
        for processo in self.dados:
            numero = processo.get('Numero_processo_etico')
            if numero:
                numeros_processos.add(numero)
        return sorted(list(numeros_processos))

    def unificar_categorias(self, categorias: list) -> pd.DataFrame:
        # Mapeamento de categorias
        mapeamento_categorias = {
            "Maus-tratos": "Maus-tratos",
            "Maus tratos": "Maus-tratos",
            "Maus Tratos": "Maus-tratos",
            "Exercício ilegal da Medicina Veterinária": "Exercício ilegal da Medicina Veterinária",
            "Exercício ilegal da Medicina Veterinária (Veterinário sem registro)": "Exercício ilegal da Medicina Veterinária",
            "Exercício ilegal da Medicina Veterinária (Veterinários sem inscrição no conselho, estagiários sem supervisão)" : "Exercício ilegal da Medicina Veterinária",
            "Fiscalização sanitária":"Fiscalização do estabelecimento",
            "Inspeção de clínica veterinária":"Fiscalização do estabelecimento",
            "Atestado veterinário":"Emissão de documentos",
            "Fraude em documentos veterinários":"Emissão de documentos",
            "Tratamento":"Terapêutica"
            # Adicione outros mapeamentos conforme necessário
        }

        # Converter para DataFrame
        df_categorias = pd.DataFrame(categorias, columns=['Categoria', 'Frequência'])

        # Função para mapear as categorias
        def mapear_categoria(categoria):
            return mapeamento_categorias.get(categoria, categoria)  # Retorna a categoria mapeada ou a original

        # Aplicar mapeamento
        df_categorias['Categoria Unificada'] = df_categorias['Categoria'].apply(mapear_categoria)

        # Agrupar por categoria unificada e somar as frequências
        df_categorias_unificadas = df_categorias.groupby('Categoria Unificada', as_index=False)['Frequência'].sum()
        df_categorias_unificadas = df_categorias_unificadas.sort_values(by='Frequência', ascending=False)

        return df_categorias_unificadas
    
    def distribuicao_documentos_unicos(self) -> dict:
        numeros_processos_unicos = set()
        processos_com_documentos = 0
        termos_autorizacao = [
            "Termo de Autorização",
            "Termo de Consentimento",
            "Termo de responsabilidade",
            "Termo de anestesia ou sedação"
        ]
        
        for processo in self.dados:
            numero_processo = processo.get('Numero_processo_etico')
            if numero_processo:
                numeros_processos_unicos.add(numero_processo)  
                documentos = processo.get('Documentos_elaborados', [])
                # Verifica se algum dos documentos contém os termos especificados
                if any(termo in doc for doc in documentos for termo in termos_autorizacao):
                    processos_com_documentos += 1

        total_processos_unicos = len(numeros_processos_unicos)
        processos_sem_documentos = total_processos_unicos - processos_com_documentos
        
        return {
            'com_documentos': processos_com_documentos,
            'sem_documentos': processos_sem_documentos
        }

#Bloco 3
# Carregando os dados
analisador = AnalisadorProcessosEticos('processos_todos.json')
# Estatísticas e distribuições
stats = analisador.obter_estatisticas()
categorias = analisador.categorias_mais_comuns()
tipos_animais = analisador.distribuicao_tipos_animais()
procedimentos = analisador.distribuicao_procedimentos()
documentos = analisador.distribuicao_documentos()
distribuicao_documentos_unicos = analisador.distribuicao_documentos_unicos()  # Obtemos a distribuição de documentos
categorias_unificadas = analisador.unificar_categorias(categorias)

# Calcular o percentual de processos com documentos
total_processos_unicos = len(analisador.obter_numeros_processos_unicos())
processos_com_documentos = distribuicao_documentos_unicos['com_documentos']
percentual_documentos = (processos_com_documentos / total_processos_unicos * 100) if total_processos_unicos > 0 else 0.0

# Exibir resultados para depuração
total_processos_unicos, processos_com_documentos, percentual_documentos

#Bloco 4
# Convertendo as distribuições para DataFrame
df_estatisticas = pd.DataFrame([stats])
df_categorias = pd.DataFrame(categorias, columns=['Categoria', 'Frequência'])
df_tipos_animais = pd.DataFrame(tipos_animais.items(), columns=['Tipo de Animal', 'Frequência'])
df_procedimentos = pd.DataFrame(procedimentos.items(), columns=['Procedimento', 'Frequência'])
df_documentos = pd.DataFrame(documentos.items(), columns=['Documento', 'Frequência'])
df_distribuicao_documentos_unicos = pd.DataFrame(distribuicao_documentos_unicos.items(), columns=['Documento', 'Frequência'])
df_categorias_unificadas = pd.DataFrame(categorias_unificadas.items(), columns=['Categoria', 'Frequência'])
# Criando o app Dash
app = dash.Dash(__name__, external_stylesheets=['styles.css'])

# Layout do dashboard
app.layout = html.Div([
    html.Div(className='header', children=[
        html.H1("Dashboard de Processos Éticos Veterinários")
    ]),
    
    html.Div(className='container', children=[
        html.Div(className='card', children=[
            html.H3("Percentual de Processos com Documentos Elaborados"),
            html.Div(f"{percentual_documentos:.2f}% de processos possuem documentos elaborados.", style={'fontSize': '24px', 'textAlign': 'center'})
        ]),

        html.Div(className='card', children=[
            html.H3("Distribuição de Processos com e sem Documentos"),
            dcc.Graph(
                id='distribuicao-documentos-unicos',
                figure=px.pie(
                    names=['Com Documentos', 'Sem Documentos'],
                    values=[distribuicao_documentos_unicos['com_documentos'], distribuicao_documentos_unicos['sem_documentos']],
                    title="Distribuição de Processos com e sem Documentos"
                )
            )
        ]),
        
        html.Div(className='card', children=[
            html.H3("Procedentes e Improcedentes"),
            dcc.Graph(
                id='procedentes-improcedentes',
                figure=px.pie(df_estatisticas, names=['processos_procedentes', 'processos_improcedentes'],
                              values=[stats['processos_procedentes'], stats['processos_improcedentes']],
                              title="Procedentes e Improcedentes")
            )
        ]),
        
        # Os outros gráficos permanecem os mesmos...
        html.Div(className='card', children=[
            html.H3("Distribuição de Categorias"),
            dcc.Graph(
                id='distribuicao-categorias',
                figure=px.bar(df_categorias, x='Categoria', y='Frequência', title="Distribuição de Processos por Categoria")
            )
        ]),
        
        html.Div(className='card', children=[
            html.H3("Distribuição por Tipo de Animal"),
            dcc.Graph(
                id='distribuicao-tipos-animais',
                figure=px.bar(df_tipos_animais, x='Tipo de Animal', y='Frequência', title="Distribuição de Processos por Tipo de Animal")
            )
        ]),
        
        html.Div(className='card', children=[
            html.H3("Distribuição de Procedimentos"),
            dcc.Graph(
                id='distribuicao-procedimentos',
                figure=px.bar(df_procedimentos, x='Procedimento', y='Frequência', title="Distribuição de Processos por Tipo de Procedimento")
            )
        ]),

        html.Div(className='card', children=[
            html.H3("Distribuição de Documentos"),
            dcc.Graph(
                id='distribuicao-documentos',
                figure=px.bar(df_documentos, x='Documento', y='Frequência', title="Distribuição de Processos por Documentos Elaborados")
            )
        ]),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
