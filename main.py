import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

N_AMOSTRAS = 50_000  # ajuste aqui; None = arquivo completo

sns.set_theme(style="whitegrid")  # estilo padrão do seaborn para todos os gráficos


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
    df = df[
        (df['TP_PRESENCA_CN'] == 1) & (df['TP_PRESENCA_CH'] == 1) &
        (df['TP_PRESENCA_LC'] == 1) & (df['TP_PRESENCA_MT'] == 1)
    ].drop(columns=['TP_PRESENCA_CN','TP_PRESENCA_CH','TP_PRESENCA_LC','TP_PRESENCA_MT'])
    df = df.dropna()
    df['NOTA_MEDIA'] = df[['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC',
                            'NU_NOTA_MT','NU_NOTA_REDACAO']].mean(axis=1)
    return df


def carregar_participantes():
    cols = ['SG_UF_PROVA', 'Q007']
    df = pd.read_csv('PARTICIPANTES_2024.csv', sep=';', encoding='latin-1',
                     usecols=cols, nrows=N_AMOSTRAS)
    df = df.dropna()
    return df


RENDA_MAP = {
    'A': 0,         'B': 706.00,    'C': 1765.01,   'D': 2471.01,
    'E': 3177.01,   'F': 3883.01,   'G': 4942.01,   'H': 6354.01,
    'I': 7766.01,   'J': 9178.01,   'K': 10590.01,  'L': 12002.01,
    'M': 13414.01,  'N': 15532.01,  'O': 19062.00,  'P': 24710.00,
    'Q': 42360.00,
}


def agregar_por_uf(df_result, df_part):
    notas_uf = df_result.groupby('SG_UF_PROVA')[
        ['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO','NOTA_MEDIA']
    ].agg(['mean', 'std', 'var']).reset_index()

    notas_uf.columns = [
        'SG_UF_PROVA' if col[0] == 'SG_UF_PROVA' else f"{col[0]}_{col[1]}"
        for col in notas_uf.columns
    ]

    df_part['RENDA_VALOR'] = df_part['Q007'].map(RENDA_MAP)

    prop_sem_renda = df_part.groupby('SG_UF_PROVA')['Q007'].apply(
        lambda x: (x == 'A').mean()
    ).reset_index().rename(columns={'Q007': 'PROP_SEM_RENDA'})

    estat_renda = df_part.groupby('SG_UF_PROVA')['RENDA_VALOR'].agg(
        ['mean', 'std', 'var']
    ).reset_index()
    estat_renda.columns = ['SG_UF_PROVA', 'RENDA_mean', 'RENDA_std', 'RENDA_var']

    renda_uf = pd.merge(prop_sem_renda, estat_renda, on='SG_UF_PROVA')
    analise_uf = pd.merge(notas_uf, renda_uf, on='SG_UF_PROVA')

    return analise_uf


def exportar_resultados(df, nome_base='analise_enem_uf'):
    df.to_csv(
        f'{nome_base}.csv', sep=';', decimal=',',
        index=False, encoding='utf-8-sig'
    )


# ────────────────────────────────────────────────────────────
# FUNÇÕES DE PLOTAGEM
# ────────────────────────────────────────────────────────────

def plot_barras_por_uf(df, coluna='NOTA_MEDIA_mean', titulo=None, salvar_em=None):
    """
    Gráfico de barras: uma barra por UF. Ideal para qualquer coluna '_mean'
    do dataset (NOTA_MEDIA_mean, RENDA_mean, NU_NOTA_MT_mean, etc.),
    já que há 27 categorias (UFs) e um valor único por categoria.
    """
    df_ord = df.sort_values(coluna, ascending=True)
    fig, ax = plt.subplots(figsize=(8, 10))
    sns.barplot(data=df_ord, y='SG_UF_PROVA', x=coluna,
                hue='SG_UF_PROVA', palette='RdYlGn', legend=False, ax=ax)
    ax.set_title(titulo or f'{coluna} por UF')
    ax.set_xlabel(coluna)
    ax.set_ylabel('UF')
    plt.tight_layout()
    if salvar_em:
        plt.savefig(salvar_em, dpi=150, bbox_inches='tight')
    plt.show()


def plot_boxplot_notas_por_area(df, salvar_em=None):
    """
    Boxplot: compara a distribuição das notas médias ESTADUAIS entre as
    5 áreas do ENEM (CN, CH, LC, MT, Redação). Cada UF é um ponto dentro
    de cada categoria (área). Isso é estatisticamente válido porque usa
    as 27 médias estaduais como amostra — diferente de tentar comparar
    UFs entre si, que com dados já agregados não tem distribuição (quartis).
    """
    colunas_mean = ['NU_NOTA_CN_mean', 'NU_NOTA_CH_mean', 'NU_NOTA_LC_mean',
                     'NU_NOTA_MT_mean', 'NU_NOTA_REDACAO_mean']
    df_long = df.melt(id_vars='SG_UF_PROVA', value_vars=colunas_mean,
                       var_name='Area', value_name='Nota')
    df_long['Area'] = df_long['Area'].str.replace('NU_NOTA_', '').str.replace('_mean', '')

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df_long, x='Area', y='Nota', hue='Area',
                palette='Set2', legend=False, ax=ax)
    sns.stripplot(data=df_long, x='Area', y='Nota',
                  color='black', alpha=0.4, size=4, ax=ax)
    ax.set_title('Distribuição das notas médias estaduais por área do ENEM')
    ax.set_xlabel('Área do conhecimento')
    ax.set_ylabel('Nota média (por UF)')
    plt.tight_layout()
    if salvar_em:
        plt.savefig(salvar_em, dpi=150, bbox_inches='tight')
    plt.show()


def plot_dispersao_renda_nota(df, salvar_em=None):
    """
    Dispersão: renda média × nota média geral, um ponto por UF.
    Inclui linha de regressão (sns.regplot já calcula e desenha).
    Este é o gráfico mais direto para sua hipótese principal do trabalho.
    """
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.regplot(data=df, x='RENDA_mean', y='NOTA_MEDIA_mean',
                scatter_kws={'s': 80, 'alpha': 0.7, 'edgecolor': 'gray'},
                line_kws={'color': '#c0392b'}, ax=ax)
    for _, row in df.iterrows():
        ax.annotate(row['SG_UF_PROVA'],
                    (row['RENDA_mean'], row['NOTA_MEDIA_mean']),
                    textcoords='offset points', xytext=(5, 3), fontsize=8)
    ax.set_title('Renda média × Nota média geral por UF')
    ax.set_xlabel('Renda média (R$)')
    ax.set_ylabel('Nota média geral')
    plt.tight_layout()
    if salvar_em:
        plt.savefig(salvar_em, dpi=150, bbox_inches='tight')
    plt.show()


def main():
    df_result = carregar_resultados()
    df_part   = carregar_participantes()
    resultado = agregar_por_uf(df_result, df_part)

    exportar_resultados(resultado)

    # Gráficos
    plot_barras_por_uf(resultado, coluna='NOTA_MEDIA_mean',
                        titulo='Nota média geral por UF',
                        salvar_em='grafico_barras_nota.png')
    plot_barras_por_uf(resultado, coluna='RENDA_mean',
                        titulo='Renda média por UF',
                        salvar_em='grafico_barras_renda.png')
    plot_boxplot_notas_por_area(resultado, salvar_em='grafico_boxplot_areas.png')
    plot_dispersao_renda_nota(resultado, salvar_em='grafico_scatter_renda_nota.png')


if __name__ == '__main__':
    main()