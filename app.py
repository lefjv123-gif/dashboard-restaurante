import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Dashboard de Tráfego Pago - Restaurante", layout="wide")

# Arquivo para salvar os dados
DB_FILE = 'dados_vendas.csv'

def carregar_dados():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    return pd.DataFrame(columns=['Data', 'Total_Add_Carrinho', 'Campanha_Add_Carrinho', 
                                 'Total_Vendas', 'Campanha_Vendas', 'Faturamento_Campanha'])

def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)

df = carregar_dados()

st.title("📊 Monitor de Vendas: Tráfego Pago vs Orgânico")

# --- BARRA LATERAL (ENTRADA DE DADOS) ---
with st.sidebar:
    st.header("Novo Registro")
    with st.form("input_form", clear_on_submit=True):
        data_input = st.date_input("Data do Registro", datetime.now())
        total_carrinho = st.number_input("Total de Adições ao Carrinho", min_value=0, step=1)
        campanha_carrinho = st.number_input("Add ao Carrinho via Campanha", min_value=0, step=1)
        total_vendas = st.number_input("Total de Vendas (Restaurante)", min_value=0, step=1)
        campanha_vendas = st.number_input("Vendas via Campanha", min_value=0, step=1)
        faturamento_camp = st.number_input("Faturamento via Campanha (R$)", min_value=0.0, step=10.0)
        
        submit = st.form_submit_button("Registrar Dados")
        
        if submit:
            nova_linha = {
                'Data': data_input,
                'Total_Add_Carrinho': total_carrinho,
                'Campanha_Add_Carrinho': campanha_carrinho,
                'Total_Vendas': total_vendas,
                'Campanha_Vendas': campanha_vendas,
                'Faturamento_Campanha': faturamento_camp
            }
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            salvar_dados(df)
            st.success("Dados registrados!")

# --- CÁLCULOS E DASHBOARD ---
tab1, tab2 = st.tabs(["📋 Registros e KPIs", "📈 Evolução Mensal"])

with tab1:
    if not df.empty:
        # Cálculos de Participação
        df['% Carrinho Pago'] = (df['Campanha_Add_Carrinho'] / df['Total_Add_Carrinho'] * 100).fillna(0)
        df['% Vendas Pago'] = (df['Campanha_Vendas'] / df['Total_Vendas'] * 100).fillna(0)
        
        # KPIs Acumulados
        col1, col2, col3 = st.columns(3)
        total_fat_camp = df['Faturamento_Campanha'].sum()
        avg_vendas_part = df['% Vendas Pago'].mean()
        avg_carrinho_part = df['% Carrinho Pago'].mean()

        col1.metric("Faturamento Campanha Acumulado", f"R$ {total_fat_camp:,.2f}")
        col2.metric("Part. Média em Vendas", f"{avg_vendas_part:.1f}%")
        col3.metric("Part. Média em Carrinho", f"{avg_carrinho_part:.1f}%")

        st.divider()
        st.subheader("Histórico de Registros")
        
        # Seleção para excluir
        st.dataframe(df.sort_values(by='Data', ascending=False))
        
        idx_excluir = st.number_input("Digite o índice da linha para excluir (ver primeira coluna)", 
                                     min_value=0, max_value=len(df)-1 if len(df)>0 else 0, step=1)
        if st.button("🗑️ Excluir Registro Selecionado"):
            df = df.drop(df.index[idx_excluir])
            salvar_dados(df)
            st.rerun()
    else:
        st.info("Nenhum dado registrado ainda.")

with tab2:
    if not df.empty:
        st.subheader("Participação do Tráfego ao Longo do Tempo")
        
        # Agrupamento Mensal
        df['Mês/Ano'] = df['Data'].dt.strftime('%Y-%m')
        mensal = df.groupby('Mês/Ano').agg({
            'Total_Add_Carrinho': 'sum',
            'Campanha_Add_Carrinho': 'sum',
            'Total_Vendas': 'sum',
            'Campanha_Vendas': 'sum'
        }).reset_index()
        
        mensal['% Part. Carrinho'] = (mensal['Campanha_Add_Carrinho'] / mensal['Total_Add_Carrinho'] * 100).fillna(0)
        mensal['% Part. Vendas'] = (mensal['Campanha_Vendas'] / mensal['Total_Vendas'] * 100).fillna(0)
        
        st.line_chart(mensal.set_index('Mês/Ano')[['% Part. Carrinho', '% Part. Vendas']])