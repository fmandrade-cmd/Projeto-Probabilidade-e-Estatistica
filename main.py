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
    cols = ['SG_UF_PROVA', 'Q007']   # Q006 = renda familiar
    df = pd.read_csv('PARTICIPANTES_2024.csv', sep=';', encoding='latin-1',
                     usecols=cols, nrows=N_AMOSTRAS)
    df = df.dropna()
    return df

# Mapeamento das faixas de renda (Q006) para o ponto médio de cada faixa em R$
RENDA_MAP = {
    'A': 0,         'B': 706.00,    'C': 1765.01,   'D': 2471.01,
    'E': 3177.01,   'F': 3883.01,   'G': 4942.01,   'H': 6354.01,
    'I': 7766.01,   'J': 9178.01,   'K': 10590.01,  'L': 12002.01,
    'M': 13414.01,  'N': 15532.01,  'O': 19062.00,  'P': 24710.00,
    'Q': 42360.00,  # faixa aberta "acima de R$28.240" — estimativa
}

def agregar_por_uf(df_result, df_part):
    # ── Notas por UF ──────────────────────────────
    notas_uf = df_result.groupby('SG_UF_PROVA')[
        ['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO','NOTA_MEDIA']
    ].agg(['mean', 'std', 'var']).reset_index()

    notas_uf.columns = [
        'SG_UF_PROVA' if col[0] == 'SG_UF_PROVA' else f"{col[0]}_{col[1]}"
        for col in notas_uf.columns
    ]

    # ── Renda por UF ──────────────────────────────
    df_part['RENDA_VALOR'] = df_part['Q007'].map(RENDA_MAP)

    # Proporção sem renda (cat A) — proxy de pobreza relativa
    prop_sem_renda = df_part.groupby('SG_UF_PROVA')['Q007'].apply(
        lambda x: (x == 'A').mean()
    ).reset_index().rename(columns={'Q007': 'PROP_SEM_RENDA'})

    # Média, desvio padrão e variância da renda
    estat_renda = df_part.groupby('SG_UF_PROVA')['RENDA_VALOR'].agg(
        ['mean', 'std', 'var']
    ).reset_index()
    estat_renda.columns = ['SG_UF_PROVA', 'RENDA_mean', 'RENDA_std', 'RENDA_var']

    renda_uf = pd.merge(prop_sem_renda, estat_renda, on='SG_UF_PROVA')

    # ── Junta notas + renda ───────────────────────
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
