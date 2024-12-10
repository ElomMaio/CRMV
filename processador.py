# bloco 1
import pandas as pd
import json

# Abrir e carregar o arquivo JSON
with open('processos_todos.json', encoding='UTF-8') as f:
    data = json.load(f)

# Construir a estrutura tabular com iteração
data_tabular = []
for item in data:
    tipo_animal = item.get('Tipo_de_animal', [])
    tipo_procedimento = item.get('Tipo_de_procedimento', [])
    artigos_infringidos = item.get('Artigos_infringidos', [])
    documentos_elaborados = item.get('Documentos_elaborados', [])
    
    for animal in (tipo_animal or ['Não especificado']):
        for procedimento in (tipo_procedimento or ['Não especificado']):
            for artigo in (artigos_infringidos or ['Não especificado']):
                for documento in (documentos_elaborados or ['Não especificado']):
                    data_tabular.append({
                        'numero_processo': item.get('Numero_processo_etico', 'Não especificado'),
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

# Exportar para CSV
df_procedentes.to_csv('processos_procedentes.csv', index=False, encoding='utf-8-sig')

print("Arquivo CSV gerado com sucesso: processos_procedentes.csv")
# bloco 2 
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from collections import Counter
import json

# Classe Analisador (do seu código)
class AnalisadorProcessosEticos:
    def __init__(self, arquivo_json: str):
        self.dados = self._carregar_json(arquivo_json)
    
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

    def obter_estatisticas(self) -> dict:
        total = len(self.dados)
        procedentes = sum(1 for caso in self.dados if caso.get('Procedencia', False))
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
            procedimento = processo.get('Procedimento', '')
            if procedimento:
                procedimentos.append(procedimento)
        return dict(Counter(procedimentos))

    def distribuicao_documentos(self) -> dict:
        documentos = []
        for processo in self.dados:
            documento = processo.get('Documentos', [])
            documentos.extend(documento)
        return dict(Counter(documentos))

# Carregando os dados
analisador = AnalisadorProcessosEticos('processos_todos.json')

# Estatísticas
stats = analisador.obter_estatisticas()
categorias = analisador.categorias_mais_comuns()
tipos_animais = analisador.distribuicao_tipos_animais()
procedimentos = analisador.distribuicao_procedimentos()
documentos = analisador.distribuicao_documentos()

# Convertendo as estatísticas e distribuições para DataFrame
df_estatisticas = pd.DataFrame([stats])
df_categorias = pd.DataFrame(categorias, columns=['Categoria', 'Frequência'])
df_tipos_animais = pd.DataFrame(tipos_animais.items(), columns=['Tipo de Animal', 'Frequência'])
df_procedimentos = pd.DataFrame(procedimentos.items(), columns=['Procedimento', 'Frequência'])
df_documentos = pd.DataFrame(documentos.items(), columns=['Documento', 'Frequência'])

# Criando o app Dash
app = dash.Dash(__name__)

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Processos Éticos Veterinários"),
    
    # Gráfico de Procedentes e Improcedentes
    dcc.Graph(
        id='procedentes-improcedentes',
        figure=px.pie(df_estatisticas, names=['processos_procedentes', 'processos_improcedentes'],
                      values=[stats['processos_procedentes'], stats['processos_improcedentes']],
                      title="Procedentes e Improcedentes sobre o Total de Processos")
    ),
    
    # Gráfico de Distribuição por Tipo de Categoria
    dcc.Graph(
        id='distribuicao-categorias',
        figure=px.bar(df_categorias, x='Categoria', y='Frequência', title="Distribuição de Processos por Categoria")
    ),
    
    # Gráfico de Distribuição por Tipo de Animal
    dcc.Graph(
        id='distribuicao-tipos-animais',
        figure=px.bar(df_tipos_animais, x='Tipo de Animal', y='Frequência', title="Distribuição de Processos por Tipo de Animal")
    ),
    
    # Gráfico de Distribuição por Procedimento
    dcc.Graph(
        id='distribuicao-procedimentos',
        figure=px.bar(df_procedimentos, x='Procedimento', y='Frequência', title="Distribuição de Processos por Tipo de Procedimento")
    ),
    
    # Gráfico de Distribuição por Documentos
    dcc.Graph(
        id='distribuicao-documentos',
        figure=px.bar(df_documentos, x='Documento', y='Frequência', title="Distribuição de Processos por Documentos Elaborados")
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
# bloco 3
# Categorias mais comuns
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

categorias_mais_comuns = analisador.categorias_mais_comuns()

# Converter para DataFrame
df_categorias = pd.DataFrame(categorias_mais_comuns, columns=['Categoria', 'Frequência'])

# Configurar o gráfico de barras
plt.figure(figsize=(12, 12))
sns.barplot(data=df_categorias, x='Categoria', y='Frequência', palette='viridis')
plt.title('Categorias Mais Comuns de Motivações')
plt.xlabel('Categorias')
plt.ylabel('Frequência')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
