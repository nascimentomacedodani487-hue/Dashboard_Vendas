# Dashboard de Vendas - Dados Brutos 📊📁

Este é um projeto de um ecossistema de Dashboard multipáginas focado na análise de dados de vendas de e-commerce, desenvolvido em **Python** utilizando a biblioteca **Streamlit** para a interface gráfica e **Pandas** para a manipulação e tratamento dos dados.

A página de **Dados Brutos** consome dados de uma API externa de produtos e oferece ao usuário um motor de busca altamente performático e customizável, permitindo filtrar e exportar relatórios sob medida.

---

## 🚀 Funcionalidades Principais

* **Ingestão de Dados em Tempo Real:** Consumo automatizado dos dados de vendas via API de produtos (`labdados.com`).
* **Feature Engineering:** Simulação e tratamento de dados para colunas de métodos de pagamento e parcelamentos de forma consistente.
* **Painel de Filtros Avançado (Sidebar):**
  * *Filtros Categóricos:* Seleção múltipla para Nome do Produto, Categoria, Vendedor, Estado de Compra e Tipo de Pagamento.
  * *Filtros Numéricos e Temporais:* Sliders dinâmicos para limites de Preço e Frete, além de seletores para Nota Mínima de Avaliação, Quantidade Exata de Parcelas e Intervalo de Datas.
* **Motor de Filtragem Otimizado:** Implementação de buscas condicionais complexas utilizando o método extremamente performático `.query()` do Pandas com o interpretador nativo do Python.
* **Exportação Personalizada:** Botão inteligente para download dos dados em formato `.csv` que respeita a seleção atual de colunas e os filtros aplicados pelo usuário.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**
* **Streamlit:** Construção da interface web interativa.
* **Pandas:** Manipulação de DataFrames, tratamento de tipos (datetime/int) e motor de busca.
* **NumPy:** Geração de distribuições probabilísticas e simulação de dados para inteligência de negócios.
* **Requests:** Requisições HTTP para consumo da API de dados.

---

## 📂 Estrutura do Repositório

```text
├── Dashboard.py          # Arquivo e página principal do ecossistema Streamlit
├── requirements.txt      # Dependências e bibliotecas do projeto
├── .gitignore            # Arquivo de escape para o ambiente virtual (venv)
└── pages/
    └── Dados_brutos.py   # Script da página de análise e filtros avançados (este arquivo)
