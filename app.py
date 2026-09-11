import os
import pandas as pd
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestor de Orientação de TCC", page_icon="🎓", layout="wide")

# --- DIRETÓRIOS E BANCO DE DADOS SIMPLES ---
UPLOADS_DIR = "anexos"
DATA_FILE = "orientandos.csv"

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# --- ETAPAS DO TCC ---
ETAPAS = [
    "1. Tema e Pré-Projeto",
    "2. Referencial Teórico e Metodologia",
    "3. Coleta e Análise de Dados",
    "4. Redação Final e Revisão",
    "5. Preparação para Banca",
    "6. Concluído / Entregue"
]

# --- FUNÇÕES DE SUPORTE ---
def carregar_dados():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame({
            "Nome": ["Exemplo Aluno 1"],
            "Título TCC": ["Análise da Gestão Pública"],
            "Etapa Atual": [ETAPAS[0]],
            "Data Limite": ["2026-11-30"],
            "Status": ["Em dia"]
        })
    
    # CORREÇÃO DO ERRO: Converter explicitamente a coluna para o tipo Date
    df["Data Limite"] = pd.to_datetime(df["Data Limite"]).dt.date
    return df

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

# Carregar base de dados corrigida
df_alunos = carregar_dados()

# --- INTERFACE PRINCIPAL ---
st.title("🎓 Sistema de Acompanhamento de TCCs")

aba1, aba2, aba3 = st.tabs(["📊 Visão Geral (Orientador)", "📤 Área do Aluno (Envio de Anexos)", "➕ Cadastrar Aluno"])

# ==========================================
# ABA 1: VISÃO GERAL (ORIENTADOR)
# ==========================================
with aba1:
    st.header("Painel de Controle de Orientandos")
    
    # Estatísticas rápidas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos", len(df_alunos))
    col2.metric("Em Fase de Redação/Revisão", len(df_alunos[df_alunos["Etapa Atual"] == ETAPAS[3]]))
    col3.metric("Prontos para Banca", len(df_alunos[df_alunos["Etapa Atual"] == ETAPAS[4]]))
    
    st.subheader("Tabela de Acompanhamento")
    
    # Tabela editável
    df_editado = st.data_editor(
        df_alunos,
        column_config={
            "Etapa Atual": st.column_config.SelectboxColumn("Etapa Atual", options=ETAPAS),
            "Status": st.column_config.SelectboxColumn("Status", options=["Em dia", "Aguardando Revisão", "Pendente Aluno", "Em Atraso"]),
            "Data Limite": st.column_config.DateColumn("Prazo Final")
        },
        use_container_width=True,
        num_rows="dynamic"
    )
    
    if st.button("💾 Salvar Alterações na Tabela"):
        salvar_dados(df_editado)
        st.success("Dados atualizados com sucesso!")
        st.rerun()

    # Visualização de Anexos Recebidos
    st.subheader("📁 Anexos Recebidos por Aluno")
    if not df_alunos.empty:
        aluno_sel = st.selectbox("Selecione um aluno para ver os arquivos enviados:", df_alunos["Nome"].unique())
        
        pasta_aluno = os.path.join(UPLOADS_DIR, aluno_sel)
        if os.path.exists(pasta_aluno) and os.listdir(pasta_aluno):
            arquivos = os.listdir(pasta_aluno)
            for arq in arquivos:
                caminho_arq = os.path.join(pasta_aluno, arq)
                with open(caminho_arq, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Baixar: {arq}",
                        data=f,
                        file_name=arq,
                        mime="application/octet-stream"
                    )
        else:
            st.info("Nenhum arquivo enviado por este aluno ainda.")

# ==========================================
# ABA 2: ÁREA DO ALUNO (ENVIO DE ARQUIVOS)
# ==========================================
with aba2:
    st.header("Envio de Atividades e Capítulos")
    
    if not df_alunos.empty:
        aluno_login = st.selectbox("Selecione o seu nome:", df_alunos["Nome"].unique(), key="aluno_login")
        dados_aluno = df_alunos[df_alunos["Nome"] == aluno_login].iloc[0]
        
        st.info(f"**Título do Trabalho:** {dados_aluno['Título TCC']}\n\n**Etapa Atual:** {dados_aluno['Etapa Atual']}")
        
        etapa_envio = st.selectbox("Selecione a etapa referente ao arquivo:", ETAPAS)
        arquivo_enviado = st.file_uploader("Anexe o documento (PDF ou DOCX):", type=["pdf", "docx", "doc"])
        
        if st.button("📤 Enviar Arquivo"):
            if arquivo_enviado is not None:
                pasta_aluno = os.path.join(UPLOADS_DIR, aluno_login)
                if not os.path.exists(pasta_aluno):
                    os.makedirs(pasta_aluno)
                
                nome_limpo = f"{etapa_envio[:2]}_{arquivo_enviado.name}".replace(" ", "_")
                caminho_salvar = os.path.join(pasta_aluno, nome_limpo)
                
                with open(caminho_salvar, "wb") as f:
                    f.write(arquivo_enviado.getbuffer())
                    
                st.success(f"Arquivo '{arquivo_enviado.name}' enviado com sucesso!")
            else:
                st.error("Por favor, selecione um arquivo antes de enviar.")

# ==========================================
# ABA 3: CADASTRAR NOVO ALUNO
# ==========================================
with aba3:
    st.header("Cadastrar Novo Orientando")
    
    with st.form("form_novo_aluno"):
        nome = st.text_input("Nome do Aluno")
        titulo = st.text_input("Título / Tema do TCC")
        etapa_inicial = st.selectbox("Etapa Inicial", ETAPAS)
        prazo = st.date_input("Prazo Limite da Defesa")
        
        btn_cadastrar = st.form_submit_button("Cadastrar")
        
        if btn_cadastrar:
            if nome and titulo:
                novo_registro = pd.DataFrame([{
                    "Nome": nome,
                    "Título TCC": titulo,
                    "Etapa Atual": etapa_inicial,
                    "Data Limite": prazo,
                    "Status": "Em dia"
                }])
                df_alunos = pd.concat([df_alunos, novo_registro], ignore_index=True)
                salvar_dados(df_alunos)
                st.success(f"Aluno {nome} cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o nome e o título do trabalho.")