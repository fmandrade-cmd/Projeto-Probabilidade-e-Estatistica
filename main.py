import pandas as pd

#Parte do código que retorna o desempenho dos alunos com competência
def analiseResultados():
        colsResultados = ['NU_NOTA_MT', 'NU_NOTA_LC', 'NU_NOTA_CN',
                'NU_NOTA_CH', 'NU_NOTA_REDACAO']

        dfResultados = pd.read_csv('RESULTADOS_2024.csv',
                        sep=';',
                        encoding='latin-1',
                        usecols=colsResultados)
        dfResultados = dfResultados.dropna()
        print(dfResultados.head(50))   

#Parte do código que retorna a coluna com as respostas das rendas dos inscritos (50 alunos)
def analiseEconomica():
        colsParticipantes = ['Q007']

        dfParticipantes = pd.read_csv('PARTICIPANTES_2024.csv',
                        sep=';',
                        encoding='latin-1',
                        usecols=colsParticipantes)
        dfParticipantes = dfParticipantes.dropna()
        print(dfParticipantes.head(50)) 

#Main para a chamada das funções a serem executadas
def main():
    """
        Problema Atual: Os dados de desempenho e economicos não estão relacionados,
        sendo assim, será necessário determinar um valor de referência para a relação
        (Número de incrição, matrícula, etc) -> Deve ser encontrado

        O que falta: Analise estatística dos dados (Média, variância, etc)
                     Plot dos gráficos
                     Teste de Hipóteses
    """
    pass

if __name__ == '__main__':
    main()