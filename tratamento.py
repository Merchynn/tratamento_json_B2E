#import json
#import pandas as pd

########################MODELO TESTE########################


# import json
# import pandas as pd
# import unicodedata

# def padroniza_dados(texto):
#     """
#     Função para converter texto para maiúsculas, remover acentos e 
#     caracteres especiais como 'ç'.
#     """
#     # Se o valor não for uma string (ex: número, booleano), retorna o original
#     if not isinstance(texto, str):
#         return texto
    
#     # Converte 'ç' para 'c' e depois tudo para maiúsculas
#     texto = texto.replace('ç', 'c').replace('Ç', 'C').upper()
    
#     # Normaliza o texto para separar os acentos das letras (forma NFD)
#     # e depois remove os acentos, mantendo apenas caracteres ASCII
#     forma_nfd = unicodedata.normalize('NFD', texto)
#     texto_sem_acentos = "".join([c for c in forma_nfd if not unicodedata.combining(c)])
    
#     return texto_sem_acentos

# try:
#     with open('layout_proposta_relatorio_Dados_brutos.txt', 'r', encoding='utf-8') as file:
#         data = json.load(file)

#     # 1. Extrair informações // peguei do stackoverflow não sei se é a melhor forma
#     info_proposta = {
#         'propostaId': data.get('propostaId'),
#         'propostaCliente': data.get('propostaCliente'),
#         'idStatusProposta': data.get('idStatusProposta'),
#         'descricaoStatusProposta': data.get('descricaoStatusProposta'),
#         'motorDataInicio': data.get('motorDataInicio'),
#         'motorDataFim': data.get('motorDataFim'),
#         'motorTempoExecucao': data.get('motorTempoExecucao'),
#         'regraDefinidoraId': data.get('regraDefinidoraId'),
#         'regraDefinidoraNome': data.get('regraDefinidora', {}).get('nome')
#     }

#     # 2. Processar a lista de regras executadas 
#     dados_regras_executadas = []
#     lista_regras = data.get('listaRegrasExecutadas', [])

#     for regra in lista_regras:
#         linha_regra = info_proposta.copy()
#         linha_regra.update({
#             'RegraId': regra.get('RegraId'),
#             'Mensagem': regra.get('Mensagem'),
#             'Explicacao': regra.get('Explicacao'),
#             'Resultado': regra.get('Resultado'),
#             'ResultadoDesejado': str(regra.get('ResultadoDesejado')),
#             'ResultadoEncontrado': regra.get('ResultadoEncontrado'),
#             'DataExecucao': regra.get('Data'),
#             'DataTerminoExecucao': regra.get('DataTermino'),
#             'DocumentoCliente': regra.get('Documento'),
#             'NomeCliente': regra.get('Nome'),
#             'BureauUtilizado': regra.get('Bureau')
#         })
#         dados_regras_executadas.append(linha_regra)

#     # 3. Criar o DataFrame com os dados processados
#     df = pd.DataFrame(dados_regras_executadas)

   

#     # 4. Limpar e converter para maiúsculas todas as colunas de texto // mesmo padrão com o unicode(bem mais facil por sinal)
#     print("\nLimpando e padronizando os dados...")
#     for coluna in df.select_dtypes(include=['object']).columns:
#         df[coluna] = df[coluna].apply(padroniza_dados)

#     # 5. Limpar e converter para maiúsculas os nomes das colunas
#     df.columns = [padroniza_dados(col) for col in df.columns]

#     # 6. Formatar as colunas de data para 'YYYY-MM-DD'
#     colunas_de_data = ['MOTORDATAINICIO', 'MOTORDATAFIM', 'DATAEXECUCAO', 'DATATERMINOEXECUCAO']
#     for coluna in colunas_de_data:
#         # Converte a coluna para o tipo datetime
#         df[coluna] = pd.to_datetime(df[coluna])
#         # Formata para o padrão YYYY-MM-DD aqui já da a delimitada de 10 caracteres
#         df[coluna] = df[coluna].dt.strftime('%Y-%m-%d')
    
   

#     # Exibir as 5 primeiras linhas do DataFrame com o tratamento aplicado
#     print("\nDataFrame final, com dados tratados:")
#     print(df.head())
    
#     # Exibir informações sobre as colunas e tipos de dados
#     print("\nInformações do DataFrame final:")
#     df.info()

# except FileNotFoundError:
#     print("Erro: O arquivo JSON não foi encontrado.")
# except json.JSONDecodeError:
#     print("Erro: O arquivo não é um JSON válido. ")
# except Exception as e:
#     print(f"Ocorreu um erro inesperado: {e}")


import json
import pandas as pd
import unicodedata

# Função 1: Padroniza texto 
def padroniza_dados(texto):
    if not isinstance(texto, str):
        return texto
    texto = str(texto).replace('ç', 'c').replace('Ç', 'C').upper()
    forma_nfd = unicodedata.normalize('NFD', texto)
    texto_sem_acentos = "".join([c for c in forma_nfd if not unicodedata.combining(c)])
    return texto_sem_acentos

# Função 2: Desempacota colunas que são strings JSON 
def desempacotar_coluna_json(df, nome_coluna, prefixo):
    if nome_coluna not in df.columns:
        return pd.DataFrame()
    dados_processados = []
    for item_str in df[nome_coluna].dropna():
        try:
            dados_json = json.loads(item_str)
            if prefixo == 'BUREAUPARAM_':
                if isinstance(dados_json, list):
                    dados_processados.append({d['DESCRICAO']: d['VALOR'] for d in dados_json if 'DESCRICAO' in d and 'VALOR' in d})
                else:
                    dados_processados.append({})
            elif isinstance(dados_json, dict):
                dados_processados.append(dados_json)
            elif isinstance(dados_json, list) and dados_json:
                dados_processados.append(dados_json[0])
            else:
                dados_processados.append({})
        except (json.JSONDecodeError, TypeError):
            dados_processados.append({})
    if not dados_processados:
        return pd.DataFrame()
    df_novo = pd.json_normalize(dados_processados)
    df_novo = df_novo.add_prefix(prefixo)
    return df_novo

# Função 3: Desempacota colunas que contêm listas de objetos 
def desempacotar_coluna_lista(df, nome_coluna, prefixo):
    if nome_coluna not in df.columns:
        return pd.DataFrame()
    lista_de_objetos = []
    for item_lista in df.get(nome_coluna, pd.Series(dtype='object')).dropna():
        if isinstance(item_lista, list) and item_lista:
            lista_de_objetos.append(item_lista[0])
        else:
            lista_de_objetos.append({})
    if not lista_de_objetos:
        return pd.DataFrame()
    df_novo = pd.json_normalize(lista_de_objetos)
    df_novo = df_novo.add_prefix(prefixo)
    return df_novo

try:
    with open('layout_proposta_relatorio_Dados_brutos.txt', 'r', encoding='utf-8') as file:
        data = json.load(file)

    proposta_id = data.get('propostaId')
    
    # ETAPAS 1-3: Criação e desempacotamento dos DataFrames 
    info_proposta_base = {'propostaId': proposta_id, 'propostaCliente': data.get('propostaCliente'), 'idStatusPropostaFinal': data.get('idStatusProposta'), 'descricaoStatusPropostaFinal': data.get('descricaoStatusProposta'), 'motorDataInicio': data.get('motorDataInicio'), 'motorDataFim': data.get('motorDataFim'), 'motorTempoExecucao': data.get('motorTempoExecucao')}
    for chave, valor in data.get('regraDefinidora', {}).items():
        if not isinstance(valor, dict): info_proposta_base[f'regraDefinidora_{chave}'] = valor
    for chave, valor in data.get('execMotor', {}).items():
        if not isinstance(valor, dict): info_proposta_base[f'execMotor_{chave}'] = valor
    for item in data.get('informacoesAdicionais', []):
        if item.get('nome'): info_proposta_base[item.get('nome')] = item.get('valor')
    dados_regras_executadas = []
    for regra in data.get('listaRegrasExecutadas', []):
        linha_regra = info_proposta_base.copy()
        for chave, valor in regra.items():
            if chave.lower() == 'propostaid': continue
            if not isinstance(valor, (dict, list)): linha_regra[chave] = valor
        resultado_bureau = regra.get('ResultadoBureau', {})
        linha_regra['ResultadoBureau_ID'] = resultado_bureau.get('ID')
        linha_regra['ResultadoBureau_Sucesso'] = resultado_bureau.get('Sucesso')
        linha_regra['ResultadoBureau_Servico_ID'] = resultado_bureau.get('BureauServico', {}).get('ID')
        parametros = regra.get('Parametros', [])
        if parametros:
            linha_regra['Parametro_Descricao'] = parametros[0].get('Descricao')
            linha_regra['Parametro_Valor'] = parametros[0].get('Valor')
        dados_regras_executadas.append(linha_regra)
    df_regras = pd.DataFrame(dados_regras_executadas)
    dados_bureaus_executados = []
    for bureau in data.get('listaBureausExecutados', []):
        linha_bureau = {'propostaId': proposta_id, 'bureauDataExecucao': bureau.get('data'), 'bureauDataTermino': bureau.get('dataTermino'), 'bureauServicoNome': bureau.get('bureauServico'), 'bureauParametros': json.dumps(bureau.get('parametros', [])),}
        resposta = bureau.get('retornoBureau', {}).get('resposta', {})
        if resposta:
            linha_bureau['bureauRespostaSucesso'] = resposta.get('sucesso')
            linha_bureau['bureauRespostaMensagem'] = resposta.get('mensagem')
            linha_bureau['bureauRespostaCompleta'] = resposta.get('retornoBureau')
            linha_bureau['bureauRequest'] = resposta.get('requestBureau')
        dados_bureaus_executados.append(linha_bureau)
    df_bureaus_inicial = pd.DataFrame(dados_bureaus_executados)
    df_bureaus_base = df_bureaus_inicial.reset_index(drop=True)
    df_params = desempacotar_coluna_json(df_bureaus_base, 'bureauParametros', 'BUREAUPARAM_')
    df_resp = desempacotar_coluna_json(df_bureaus_base, 'bureauRespostaCompleta', 'BUREAURESP_')
    df_req = desempacotar_coluna_json(df_bureaus_base, 'bureauRequest', 'BUREAUREQ_')
    df_bureaus_intermediario = pd.concat([df_bureaus_base, df_params, df_resp, df_req], axis=1)
    df_bureaus_intermediario = df_bureaus_intermediario.drop(columns=['bureauParametros', 'bureauRespostaCompleta', 'bureauRequest'])
    df_orders = desempacotar_coluna_lista(df_bureaus_intermediario, 'BUREAURESP_orders', 'BUREAURESP_ORDERS_')
    df_itens = desempacotar_coluna_lista(df_bureaus_intermediario, 'BUREAURESP_itens', 'BUREAURESP_ITENS_')
    df_bureaus_final = pd.concat([df_bureaus_intermediario, df_orders, df_itens], axis=1)
    colunas_para_remover_final = ['BUREAURESP_orders', 'BUREAURESP_itens']
    colunas_existentes_para_remover = [col for col in colunas_para_remover_final if col in df_bureaus_final.columns]
    df_bureaus_final = df_bureaus_final.drop(columns=colunas_existentes_para_remover)

    # ETAPA 4: JUNÇÃO DE TODOS OS DADOS
    print("\nJuntando os DataFrames finais...")
    df_final = pd.merge(df_regras, df_bureaus_final, on='propostaId', how='outer')

    # --- ETAPA 5: PADRONIZAÇÃO FINAL 
    print("\nAplicando padronização final em todo o arquivo...")
    
    # Aplica a limpeza nos nomes das colunas PRIMEIRO
    df_final.columns = [padroniza_dados(col) for col in df_final.columns]
    
    # Aplica a limpeza em todas as colunas de texto
    for coluna in df_final.select_dtypes(include=['object']).columns:
        df_final[coluna] = df_final[coluna].apply(padroniza_dados)
    
    print("DataFrame final combinado e totalmente tratado criado com sucesso!")
    print(f"Dimensões finais: {df_final.shape[0]} linhas, {df_final.shape[1]} colunas")

    # ETAPA 6: SALVAR O ARQUIVO FINAL
  
    print("\nArquivo 'relatorio_completo_proposta_FINAL.csv' salvo com sucesso!")

except FileNotFoundError:
    print("Erro: O arquivo JSON não foi encontrado.")
except json.JSONDecodeError:
    print("Erro: O arquivo não é um JSON válido. ")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")





colunas_data_para_converter = [
    'MOTORDATAINICIO',
    'MOTORDATAFIM',
    'REGRADEFINIDORA_DATAHORAINICIOEXECUCAO',
    'REGRADEFINIDORA_DATAHORAFIMEXECUCAO',
    'EXECMOTOR_DATA_FIM_EXEC',
    'EXECMOTOR_DATA_INI_EXEC',
    'DATA',
    'DATATERMINO',
    'BUREAUDATAEXECUCAO',
    'BUREAUDATATERMINO',
    'BUREAURESP_DATAATUALIZACAO'
]


for coluna in colunas_data_para_converter:
    # Acessa a coluna específica no seu DataFrame e aplica a transformação
    df_final[coluna] = pd.to_datetime(df_final[coluna], errors='coerce').dt.strftime('%Y-%m-%d')


print(df_final[colunas_data_para_converter].head())


df_final.to_csv('relatorio_completo_proposta_FINAL.csv', index=False, sep=';', encoding='utf-8-sig')
