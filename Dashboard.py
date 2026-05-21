import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout= 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS 🛒')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

# CORREÇÃO 1: Ajustado de 'tittle' para 'title'
st.sidebar.title('Filtros')

# CORREÇÃO 2: Adicionada a vírgula que faltava entre os argumentos
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(),'ano':ano}
response = requests.get(url,params= query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# CORREÇÃO 3: Ajustado de dados{'Vendedor'} para dados['Vendedor'] (colchetes)
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas
### Tabelas de Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat','lon']].merge(receita_estados, left_on= 'Local da compra', right_index= True).sort_values('Preço', ascending= False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending= False)

### Tabelas de Quantidade de Vendas
vendas_estados = dados.groupby('Local da compra')[['Preço']].count().rename(columns={'Preço': 'Qtd Vendas'})
vendas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Qtd Vendas', ascending=False)

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count().reset_index().rename(columns={'Preço': 'Qtd Vendas'})
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().rename(columns={'Preço': 'Qtd Vendas'}).sort_values('Qtd Vendas', ascending=True)

### Tabela de Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos
### Gráficos da Aba 1 (Receita)
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat= 'lat',
                                  lon= 'lon',
                                  scope= 'south america',
                                  size= 'Preço',
                                  template= 'seaborn',
                                  hover_name= 'Local da compra',
                                  hover_data= {'lat': False, 'lon': False},
                                  title = 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers= True,
                             range_y= (0, receita_mensal['Preço'].max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x= 'Local da compra',
                             y= 'Preço',
                             text_auto= True,
                             title= 'Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                 x= receita_categorias.index,
                                 y= 'Preço',
                                 text_auto= True,
                                 title= 'Receita por categoria')

fig_receita_categorias.update_layout(yaxis_title = 'Receita')


### Gráficos da Aba 2 (Quantidade de Vendas)
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                 lat='lat',
                                 lon='lon',
                                 scope='south america',
                                 size='Qtd Vendas',
                                 template='plotly_white', 
                                 hover_name='Local da compra',
                                 hover_data={'lat': False, 'lon': False},
                                 title='Distribuição Geográfica de Pedidos')

fig_vendas_mensal = px.line(vendas_mensal,
                            x='Mes',
                            y='Qtd Vendas',
                            markers=True,
                            range_y=(0, vendas_mensal['Qtd Vendas'].max() * 1.1),
                            color='Ano',
                            template='plotly_white',
                            title='Evolução Mensal de Volume de Pedidos (Sazonalidade)')
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de Vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                            x='Local da compra',
                            y='Qtd Vendas',
                            text_auto=True,
                            template='plotly_white',
                            title='Top 5 Estados por Volume de Transações')
fig_vendas_estados.update_layout(yaxis_title='Quantidade de Vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                               x='Qtd Vendas',
                               y=vendas_categorias.index,
                               orientation='h', 
                               text_auto=True,
                               template='plotly_white',
                               title='Volume de Pedidos por Categoria de Produto')
fig_vendas_categorias.update_layout(xaxis_title='Quantidade de Vendas', yaxis_title='')


## Visualização no Streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width= True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)
    with coluna2: 
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width= True)
        st.plotly_chart(fig_receita_categorias, use_container_width= True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
        
    with coluna2: 
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)
    
    ### ==========================================
    ### CODE DESAFIO: NOVO GRÁFICO DE ESCALABILIDADE DE PRODUTO
    ### ==========================================
    st.markdown("---")
    st.subheader("Análise de Escalabilidade e Tração de Linhas de Produto")
    
    categorias_disponiveis = sorted(dados['Categoria do Produto'].unique())
    categoria_selecionada = st.selectbox('Selecione uma Categoria para Analisar o Histórico de Desempenho:', categorias_disponiveis)
    
    dados_filtrados_cat = dados[dados['Categoria do Produto'] == categoria_selecionada]
    
    vendas_escalabilidade = dados_filtrados_cat.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count().reset_index().rename(columns={'Preço': 'Qtd Vendas'})
    vendas_escalabilidade['Ano'] = vendas_escalabilidade['Data da Compra'].dt.year
    vendas_escalabilidade['Mes'] = vendas_escalabilidade['Data da Compra'].dt.month_name()
    
    fig_escalabilidade = px.line(vendas_escalabilidade,
                                 x='Mes',
                                 y='Qtd Vendas',
                                 color='Ano',
                                 markers=True,
                                 template='plotly_white',
                                 title= f'Curva de Escalabilidade Anual - Categoria: {categoria_selecionada}',
                                 category_orders={"Mes": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]})
    
    fig_escalabilidade.update_layout(xaxis_title='Meses do Ano', yaxis_title='Quantidade de Unidades Vendidas')
    
    st.plotly_chart(fig_escalabilidade, use_container_width=True)
    ### ==========================================

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores, use_container_width= True)
    with coluna2: 
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                       x = 'count',
                                       y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                       text_auto = True,
                                       title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores, use_container_width= True)