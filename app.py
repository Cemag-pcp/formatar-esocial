import streamlit as st
import pandas as pd
from io import BytesIO, StringIO
import re

# Função para criar um modelo de Excel com 4 campos
def create_excel_template_4_campos():
    columns = ["CPF", "NIS", "NOME", "DN"]
    df = pd.DataFrame(columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Função para criar um modelo de Excel com 7 campos
def create_excel_template_7_campos():
    columns = ["CPF", "NIS", "NOME", "DN", "UF", "MUNICIPIO", "NOME_MAE"]
    df = pd.DataFrame(columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Função para remover caracteres especiais e normalizar espaços
def clean_text(text):
    if pd.isna(text) or text == '':
        return ''
    
    # Remove múltiplos espaços e substitui por um único espaço
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Função para converter Excel para TXT (4 campos)
def convert_excel_to_txt_4_campos(df, delimiter=';'):
    # Certifique-se de que as colunas estão no formato correto
    df['DN'] = df['DN'].astype(str).str.zfill(8)  # Formato DDMMAAAA
    df['CPF'] = df['CPF'].astype(str).str.zfill(11)  # Formato 11 dígitos
    df['NIS'] = df['NIS'].astype(str).str.zfill(11)  # Formato 11 dígitos
    
    # Substituir valores NaN por strings vazias
    df = df.fillna('')
    
    # Limpar e formatar o campo NOME
    df['NOME'] = df['NOME'].apply(clean_text)
    
    # Salvar como TXT com o formato especificado
    txt_data = df.to_csv(sep=delimiter, index=False, header=False)
    return txt_data

# Função para converter Excel para TXT (7 campos)
def convert_excel_to_txt_7_campos(df, delimiter=';'):
    # Certifique-se de que as colunas estão no formato correto
    df['DN'] = df['DN'].astype(str).str.zfill(8)  # Formato DDMMAAAA
    df['CPF'] = df['CPF'].astype(str).str.zfill(11)  # Formato 11 dígitos
    df['NIS'] = df['NIS'].astype(str).str.zfill(11)  # Formato 11 dígitos
    
    # Substituir valores NaN por strings vazias
    df = df.fillna('')
    
    # Limpar e formatar os campos de texto (NOME, MUNICIPIO, NOME_MAE)
    df['NOME'] = df['NOME'].apply(clean_text)
    df['MUNICIPIO'] = df['MUNICIPIO'].apply(clean_text)
    df['NOME_MAE'] = df['NOME_MAE'].apply(clean_text)
    
    # Salvar como TXT com o formato especificado
    txt_data = df.to_csv(sep=delimiter, index=False, header=False)
    return txt_data

# Função para converter TXT de resposta para Excel
def convert_txt_to_excel(txt_data, delimiter=';'):
    # Ler o arquivo TXT
    df = pd.read_csv(txt_data, delimiter=delimiter)
    
    df.dropna(inplace=True)
    
    colunas = [
        "CPF", "NIS", "NOME", "DN", "COD_NIS_INV", "COD_CPF_INV", "COD_NOME_INV", "COD_DN_INV",
        "COD_CNIS_NIS", "COD_CNIS_DN", "COD_CNIS_OBITO", "COD_CNIS_CPF", "COD_CNIS_CPF_NAO_INF",
        "COD_CPF_NAO_CONSTA", "COD_CPF_NULO", "COD_CPF_CANCELADO", "COD_CPF_SUSPENSO", "COD_CPF_DN",
        "COD_CPF_NOME", "COD_ORIENTACAO_CPF", "COD_ORIENTACAO_NIS"
    ]
    
    df_tratado = tratar_saida_retorno(df)
    df_tratado = pd.read_csv(StringIO(df_tratado), sep=";", header=None, names=colunas)

    # Salvar como Excel
    excel_file = "resposta.xlsx"
    df_tratado.to_excel(excel_file, index=False)

    return excel_file

def tratar_saida_retorno(df_retorno, delimiter=';'):
    """
    Função para tratar o arquivo de retorno e gerar a saída no formato correto,
    substituindo os códigos pelos seus significados.
    
    :param df_retorno: DataFrame com os dados de retorno.
    :param delimiter: Delimitador usado no arquivo TXT (padrão é ';').
    :return: String com os dados formatados para o arquivo TXT.
    """
    # Dicionário de mapeamento dos códigos para seus significados
    codigos_significado = {
        "COD_NIS_INV": {0: "OK", 1: "NIS INVÁLIDO"},
        "COD_CPF_INV": {0: "OK", 1: "CPF INVÁLIDO"},
        "COD_NOME_INV": {0: "OK", 1: "NOME INVÁLIDO"},
        "COD_DN_INV": {0: "OK", 1: "DN INVÁLIDO"},
        "COD_CNIS_NIS": {0: "OK", 1: "NIS INCONSISTENTE"},
        "COD_CNIS_DN": {0: "OK", 1: "DATA DE NASCIMENTO DIVERGE NO CNIS"},
        "COD_CNIS_OBITO": {0: "OK", 1: "ÓBITO NO CNIS"},
        "COD_CNIS_CPF": {0: "OK", 1: "CPF DIVERGE NO CNIS"},
        "COD_CNIS_CPF_NAO_INF": {0: "OK", 1: "CPF NÃO INFORMADO NO CNIS"},
        "COD_CPF_NAO_CONSTA": {0: "OK", 1: "CPF NÃO CONSTA NO CADASTRO CPF"},
        "COD_CPF_NULO": {0: "OK", 1: "CPF NULO NO CADASTRO CPF"},
        "COD_CPF_CANCELADO": {0: "OK", 1: "CPF CANCELADO NO CADASTRO CPF"},
        "COD_CPF_SUSPENSO": {0: "OK", 1: "CPF SUSPENSO NO CADASTRO CPF"},
        "COD_CPF_DN": {0: "OK", 1: "DATA DE NASCIMENTO DIVERGE NO CADASTRO CPF"},
        "COD_CPF_NOME": {0: "OK", 1: "NOME DIVERGE NO CADASTRO CPF"},
        "COD_ORIENTACAO_CPF": {0: "OK", 1: "PROCURAR CONVENIADAS DA RFB"},
        "COD_ORIENTACAO_NIS": {0: "OK", 1: "ATUALIZAR NIS NO INSS", 2: "VERIFICAR DADOS DIGITADOS"}
    }
    
    # Verifica se o DataFrame tem as colunas necessárias
    colunas_esperadas = [
        "CPF", "NIS", "NOME", "DN", "COD_NIS_INV", "COD_CPF_INV", "COD_NOME_INV", "COD_DN_INV",
        "COD_CNIS_NIS", "COD_CNIS_DN", "COD_CNIS_OBITO", "COD_CNIS_CPF", "COD_CNIS_CPF_NAO_INF",
        "COD_CPF_NAO_CONSTA", "COD_CPF_NULO", "COD_CPF_CANCELADO", "COD_CPF_SUSPENSO", "COD_CPF_DN",
        "COD_CPF_NOME", "COD_ORIENTACAO_CPF", "COD_ORIENTACAO_NIS"
    ]
    
    if not all(col in df_retorno.columns for col in colunas_esperadas):
        raise ValueError("O DataFrame de retorno não contém todas as colunas necessárias.")
    
    # Formata os dados conforme o layout especificado
    dados_formatados = []
    for _, row in df_retorno.iterrows():
        linha_formatada = [
            str(row["CPF"]).zfill(11),  # CPF com 11 dígitos
            str(row["NIS"]).zfill(11),  # NIS com 11 dígitos
            row["NOME"],  # Nome (até 60 caracteres)
            str(row["DN"]).zfill(8),  # Data de Nascimento (DDMMAAAA)
            codigos_significado["COD_NIS_INV"][row["COD_NIS_INV"]],  # Código de validação do NIS
            codigos_significado["COD_CPF_INV"][row["COD_CPF_INV"]],  # Código de validação do CPF
            codigos_significado["COD_NOME_INV"][row["COD_NOME_INV"]],  # Código de validação do NOME
            codigos_significado["COD_DN_INV"][row["COD_DN_INV"]],  # Código de validação da Data de Nascimento
            codigos_significado["COD_CNIS_NIS"][row["COD_CNIS_NIS"]],  # Código de consistência do NIS no CNIS
            codigos_significado["COD_CNIS_DN"][row["COD_CNIS_DN"]],  # Código de consistência da Data de Nascimento no CNIS
            codigos_significado["COD_CNIS_OBITO"][row["COD_CNIS_OBITO"]],  # Código de óbito no CNIS
            codigos_significado["COD_CNIS_CPF"][row["COD_CNIS_CPF"]],  # Código de consistência do CPF no CNIS
            codigos_significado["COD_CNIS_CPF_NAO_INF"][row["COD_CNIS_CPF_NAO_INF"]],  # Código de CPF não informado no CNIS
            codigos_significado["COD_CPF_NAO_CONSTA"][row["COD_CPF_NAO_CONSTA"]],  # Código de CPF não consta no Cadastro CPF
            codigos_significado["COD_CPF_NULO"][row["COD_CPF_NULO"]],  # Código de CPF nulo no Cadastro CPF
            codigos_significado["COD_CPF_CANCELADO"][row["COD_CPF_CANCELADO"]],  # Código de CPF cancelado no Cadastro CPF
            codigos_significado["COD_CPF_SUSPENSO"][row["COD_CPF_SUSPENSO"]],  # Código de CPF suspenso no Cadastro CPF
            codigos_significado["COD_CPF_DN"][row["COD_CPF_DN"]],  # Código de divergência da Data de Nascimento no Cadastro CPF
            codigos_significado["COD_CPF_NOME"][row["COD_CPF_NOME"]],  # Código de divergência do NOME no Cadastro CPF
            codigos_significado["COD_ORIENTACAO_CPF"][row["COD_ORIENTACAO_CPF"]],  # Código de orientação para o CPF
            codigos_significado["COD_ORIENTACAO_NIS"][row["COD_ORIENTACAO_NIS"]]  # Código de orientação para o NIS
        ]
        dados_formatados.append(delimiter.join(linha_formatada))
    
    # Junta todas as linhas em uma única string
    return "\n".join(dados_formatados)

# Interface do Streamlit
st.title("Conversor de Arquivos para o Formato eSocial")

# Botão para baixar o modelo de Excel com 4 campos
st.write("### Baixar Modelo de Excel (4 Campos)")
st.write("Clique no botão abaixo para baixar um modelo de Excel com 4 campos (CPF, NIS, NOME, DN).")
excel_template_4_campos = create_excel_template_4_campos()
st.download_button(
    label="Baixar Modelo de Excel (4 Campos)",
    data=excel_template_4_campos,
    file_name="modelo_entrada_4_campos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Botão para baixar o modelo de Excel com 7 campos
st.write("### Baixar Modelo de Excel (7 Campos)")
st.write("Clique no botão abaixo para baixar um modelo de Excel com 7 campos (CPF, NIS, NOME, DN, UF, MUNICIPIO, NOME_MAE).")
excel_template_7_campos = create_excel_template_7_campos()
st.download_button(
    label="Baixar Modelo de Excel (7 Campos)",
    data=excel_template_7_campos,
    file_name="modelo_entrada_7_campos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregue seu arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Ler o arquivo Excel
    df = pd.read_excel(uploaded_file)
    
    # Verificar o número de colunas para determinar o tipo de entrada
    if len(df.columns) == 4:
        st.write("Dados carregados (4 campos):")
        st.write(df)
        # Converter para TXT (4 campos)
        txt_data = convert_excel_to_txt_4_campos(df)
        file_name = "D.TST.CPF.001.TXT"
    elif len(df.columns) == 7:
        st.write("Dados carregados (7 campos):")
        st.write(df)
        # Converter para TXT (7 campos)
        txt_data = convert_excel_to_txt_7_campos(df)
        file_name = "D.TST.CPF.001.TXT"
    else:
        st.error("O arquivo Excel deve ter 4 ou 7 colunas.")
        st.stop()
    
    # Botão para download do arquivo TXT
    st.download_button(
        label="Baixar arquivo TXT",
        data=txt_data,
        file_name=file_name,
        mime="text/plain"
    )

# Upload do arquivo TXT de resposta
uploaded_txt_file = st.file_uploader("Carregue o arquivo TXT de resposta", type=["txt"])

if uploaded_txt_file is not None:
    # Converter TXT para Excel
    excel_file = convert_txt_to_excel(uploaded_txt_file)
    
    # Botão para download do arquivo Excel
    with open(excel_file, "rb") as f:
        st.download_button(
            label="Baixar arquivo Excel",
            data=f,
            file_name="resposta.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )