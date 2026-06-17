import pandas as pd
import numpy as np

N_AMOSTRAS = 50_000  # ajuste aqui; None = arquivo completo

def carregar_resultados():
    cols = ['SG_UF_PROVA', 'TP_PRESENCA_CN', 'TP_PRESENCA_CH',
            'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
            'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC',
            'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    
    df = pd.read_csv('RESULTADOS_2024.csv', 
                     sep=';', 
                     encoding='latin-1',
                     usecols=cols, 
                     nrows=N_AMOSTRAS)
    # Apenas quem fez todas as provas
    df = df[
        (df['TP_PRESENCA_CN'] == 1) & (df['TP_PRESENCA_CH'] == 1) &
        (df['TP_PRESENCA_LC'] == 1) & (df['TP_PRESENCA_MT'] == 1)
    ].drop(columns=['TP_PRESENCA_CN','TP_PRESENCA_CH','TP_PRESENCA_LC','TP_PRESENCA_MT'])
    df = df.dropna()
    df['NOTA_MEDIA'] = df[['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC',
                            'NU_NOTA_MT','NU_NOTA_REDACAO']].mean(axis=1)
    return df

def carregar_participantes():
    cols = ['SG_UF_PROVA', 'Q006']   # Q006 = renda familiar
    df = pd.read_csv('PARTICIPANTES_2024.csv', sep=';', encoding='latin-1',
                     usecols=cols, nrows=N_AMOSTRAS)
    df = df.dropna()
    return df

def agregar_por_uf(df_result, df_part):
    # Notas médias por UF
    notas_uf = df_result.groupby('SG_UF_PROVA')[
        ['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO','NOTA_MEDIA']
    ].agg(['mean', 'std', 'var']).reset_index()

    # Achatar o multi-index de colunas (ex: ('NU_NOTA_CN','mean') -> 'NU_NOTA_CN_mean')
    notas_uf.columns = [
        'SG_UF_PROVA' if col[0] == 'SG_UF_PROVA' else f"{col[0]}_{col[1]}"
        for col in notas_uf.columns
    ]

    # Proporção sem renda (cat A) por UF — proxy de pobreza relativa
    renda_uf = df_part.groupby('SG_UF_PROVA')['Q006'].apply(
        lambda x: (x == 'A').mean()
    ).reset_index().rename(columns={'Q006': 'PROP_SEM_RENDA'})

    analise_uf = pd.merge(notas_uf, renda_uf, on='SG_UF_PROVA')

    return analise_uf

def exportar_resultados(df, nome_base='analise_enem_uf'):
    # CSV — abre direto no LibreOffice Calc
    df.to_csv(
        f'{nome_base}.csv',
        sep=';',              # ; evita conflito com a vírgula decimal
        decimal=',',           # vírgula como separador decimal (padrão BR)
        index=False,
        encoding='utf-8-sig'   # BOM garante acentos corretos (Ç, Ã, etc.)
    )

    # XLSX — melhor para Power BI (tipos numéricos preservados nativamente)
    df.to_excel(
        f'{nome_base}.xlsx',
        index=False,
        sheet_name='Analise_UF'
    )

    print(f"Arquivos gerados: {nome_base}.csv e {nome_base}.xlsx")


def main():
    df_result = carregar_resultados()
    df_part   = carregar_participantes()
    resultado = agregar_por_uf(df_result, df_part)

    print(resultado)
    exportar_resultados(resultado)

if __name__ == '__main__':
    main()
