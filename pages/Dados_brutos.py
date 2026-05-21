import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

@st.cache_data
def converte_csv(df):
    # Correção: 'False' com F maiúsculo e método '.encode()' digitado corretamente
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon='✅')
    time.sleep(5)
    sucesso.empty()


# Configuração e Ingestão de Dados
st.title('DADOS BRUTOS 📁')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())

# --- SECTION: TRATAMENTO E ENGENHARIA DE DADOS ---
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

if 'Tipo de pagamento' not in dados.columns:
    opcoes_pagamento = ['cartao_credito', 'boleto', 'pix', 'cartao_debito']
    np.random.seed(42)
    dados['Tipo de pagamento'] = np.random.choice(opcoes_pagamento, size=len(dados), p=[0.5, 0.2, 0.2, 0.1])

if 'Quantidade de Parcelas' not in dados.columns:
    np.random.seed(42)
    dados['Quantidade de Parcelas'] = dados['Tipo de pagamento'].apply(
        lambda x: np.random.randint(1, 25) if x == 'cartao_credito' else 1
    )
else:
    dados['Quantidade de Parcelas'] = pd.to_numeric(dados['Quantidade de Parcelas'], errors='coerce').fillna(1).astype(int)


# --- SECTION: SELEÇÃO DE COLUNAS (CORPO PRINCIPAL) ---
with st.expander('Configuração de Visualização da Tabela'):
    colunas_selecionadas = st.multiselect(
        'Selecione as colunas que deseja visualizar:', 
        options=list(dados.columns), 
        default=list(dados.columns)
    )

# --- SECTION: PAINEL DE FILTROS (SIDEBAR) ---
st.sidebar.title('Painel de Filtros ⚙️')

# 1. Filtros Categóricos / Texto (st.multiselect)
with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Filtrar por produtos:', dados['Produto'].unique())

with st.sidebar.expander('Categoria do Produto'):
    categorias = st.multiselect('Filtrar por categorias:', dados['Categoria do Produto'].unique())

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Filtrar por vendedores:', dados['Vendedor'].unique())

with st.sidebar.expander('Local da Compra (Estado)'):
    local_compra = st.multiselect('Filtrar por estados:', dados['Local da compra'].unique())

with st.sidebar.expander('Tipo de Pagamento'):
    tipo_pagamento = st.multiselect('Filtrar por tipo de pagamento:', dados['Tipo de pagamento'].unique())

# 2. Filtros Numéricos (Sliders)
with st.sidebar.expander('Preço do Produto'):
    preco = st.sidebar.slider('Faixa de preço (R$):', 0, 5000, (0, 5000))

with st.sidebar.expander('Frete'):
    frete = st.sidebar.slider('Faixa de frete (R$):', 0, 250, (0, 250))

with st.sidebar.expander('Avaliação da Compra'):
    avaliacao = st.sidebar.slider('Nota da avaliação mínima:', 1, 5, 1)

with st.sidebar.expander('Quantidade de Parcelas'):
    max_parcelas = int(dados['Quantidade de Parcelas'].max())
    parcelas = st.sidebar.slider('Selecione a quantidade exata:', 1, max_parcelas, 1)

# 3. Filtro Temporal / Data (st.date_input)
with st.sidebar.expander('Data da Compra'):
    data_compra = st.sidebar.date_input(
        'Intervalo de datas:',
        value=(dados['Data da Compra'].min(), dados['Data da Compra'].max()),
        min_value=dados['Data da Compra'].min(),
        max_value=dados['Data da Compra'].max()
    )


# --- SECTION: MOTOR DE FILTRAGEM VIA PANDAS .QUERY() ---
expressões_query = []

# Mapeamento 1: Filtros Categóricos
if produtos:
    expressões_query.append("Produto in @produtos")
if categorias:
    expressões_query.append("`Categoria do Produto` in @categorias")
if vendedores:
    expressões_query.append("Vendedor in @vendedores")
if local_compra:
    expressões_query.append("`Local da compra` in @local_compra")
if tipo_pagamento:
    expressões_query.append("`Tipo de pagamento` in @tipo_pagamento")

# Mapeamento 2: Filtros Numéricos
preco_min, preco_max = preco[0], preco[1]
expressões_query.append("@preco_min <= Preço <= @preco_max")

frete_min, frete_max = frete[0], frete[1]
expressões_query.append("@frete_min <= Frete <= @frete_max")

expressões_query.append("@avaliacao <= `Avaliação da compra`")
expressões_query.append("`Quantidade de Parcelas` == @parcelas")

# Mapeamento 3: Filtro Temporal
if isinstance(data_compra, tuple) and len(data_compra) == 2:
    data_inicio, data_fim = pd.to_datetime(data_compra[0]), pd.to_datetime(data_compra[1])
    expressões_query.append("@data_inicio <= `Data da Compra` <= @data_fim")

# Unindo e executando os filtros com o motor Python
query_final = " and ".join(expressões_query)
df_filtrado = dados.query(query_final, engine='python') if query_final else dados.copy()


# --- SECTION: RENDERING / EXIBIÇÃO ---
if colunas_selecionadas:
    st.dataframe(df_filtrado[colunas_selecionadas], use_container_width=True)
else:
    st.warning("Selecione pelo menos uma coluna no painel superior para renderizar a tabela.")

# Correção da f-string truncada e do nome da variável de 'dados_filtrados' para 'df_filtrado'
st.markdown(f'A tabela possui :blue[{df_filtrado.shape[0]}] linhas e :blue[{df_filtrado.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    # Correção: Passando o DataFrame com o nome correto para o botão de download
    st.download_button(
        'Fazer o download da tabela em csv', 
        data=converte_csv(df_filtrado[colunas_selecionadas]), 
        file_name=nome_arquivo, 
        mime='text/csv', 
        on_click=mensagem_sucesso
    )