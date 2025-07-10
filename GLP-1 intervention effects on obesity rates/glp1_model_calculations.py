import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

# Publication-grade colorblind-friendly palette
COLORS = {
    'medical': '#4E79A7',      # Blue
    'lifestyle': '#A0CBE8',    # Light Blue
    'universal': '#F28E2B',    # Orange
    'baseline': '#333333',     # Dark Gray
    'grid': '#E5E5E5',         # Light Gray
    'background': '#FFFFFF',   # White
    'text': '#222222',         # Near-black
    'highlight': '#59A14F'     # Green for callouts
}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Inter', 'Source Sans Pro', 'Arial', 'DejaVu Sans'],
    'font.size': 13,
    'axes.titlesize': 20,
    'axes.labelsize': 15,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 13,
    'figure.titlesize': 22,
    'axes.titleweight': 'bold',
    'axes.labelweight': 'bold',
    'axes.edgecolor': COLORS['baseline'],
    'axes.linewidth': 1.2,
    'axes.facecolor': COLORS['background'],
    'savefig.facecolor': COLORS['background'],
    'savefig.edgecolor': COLORS['background']
})

def add_callout(ax, x, y, text, color, va='center', ha='left', xytext=(10,0)):
    """Add a clean callout box with an arrow."""
    ax.annotate(text, xy=(x, y), xytext=xytext, textcoords='offset points',
                ha=ha, va=va, fontsize=13, fontweight='bold', color=color,
                bbox=dict(boxstyle="round,pad=0.3", fc='white', ec=color, lw=1.5, alpha=0.95),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=color, alpha=0.8))

def plot_adoption(years, df):
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(top=0.80, bottom=0.18)
    ax.plot(years, df['GLP1_adoption_medical']*100, color=COLORS['medical'], lw=3, label='Medical (8% max)', marker='o')
    ax.plot(years, df['GLP1_adoption_lifestyle']*100, color=COLORS['lifestyle'], lw=3, label='Lifestyle (30% max)', marker='s')
    ax.plot(years, df['GLP1_adoption_universal']*100, color=COLORS['universal'], lw=3, label='Universal (70% max)', marker='^')
    ax.set_xlabel('Year')
    ax.set_ylabel('GLP-1 adoption rate (%)')
    ax.set_title('GLP-1 Adoption Scenarios', pad=18, loc='center')
    ax.text(0.5, 1.05, 'Projected Effects on U.S. Adult Obesity (2023–2035)', transform=ax.transAxes, ha='center', fontsize=15, color=COLORS['baseline'], alpha=0.85, fontweight='normal')
    ax.grid(True, color=COLORS['grid'], alpha=0.7, linewidth=1)
    ax.set_ylim(0, 75)
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper left', frameon=False, bbox_to_anchor=(0,1.12), ncol=1)
    add_callout(ax, 2035, df.iloc[-1]['GLP1_adoption_universal']*100, '69.8%', COLORS['universal'], xytext=(10,10))
    add_callout(ax, 2035, df.iloc[-1]['GLP1_adoption_medical']*100, '8.0%', COLORS['medical'], xytext=(-80,-10), ha='right')
    ax.text(1, -0.18, 'Data: WHO, Census Bureau, CDC | Methodology: Logistic adoption curves, 28% efficacy',
            ha='right', va='bottom', fontsize=11, color=COLORS['baseline'], alpha=0.7, transform=ax.transAxes)
    plt.tight_layout(rect=[0, 0.08, 1, 0.97])
    plt.savefig('glp1_adoption_scenarios.png', dpi=300)
    plt.close()

def plot_prevalence(years, df):
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(top=0.80, bottom=0.18)
    ax.plot(years, df['Obesity_prevalence'], color=COLORS['baseline'], lw=4, ls='--', label='Baseline (No GLP-1)')
    ax.plot(years, df['Obesity_medical'], color=COLORS['medical'], lw=3, label='Medical')
    ax.plot(years, df['Obesity_lifestyle'], color=COLORS['lifestyle'], lw=3, label='Lifestyle')
    ax.plot(years, df['Obesity_universal'], color=COLORS['universal'], lw=3, label='Universal')
    ax.set_xlabel('Year')
    ax.set_ylabel('Obesity prevalence (%)')
    ax.set_title('Obesity Prevalence Under Different Scenarios', pad=18, loc='center')
    ax.text(0.5, 1.05, 'Projected Effects on U.S. Adult Obesity (2023–2035)', transform=ax.transAxes, ha='center', fontsize=15, color=COLORS['baseline'], alpha=0.85, fontweight='normal')
    ax.grid(True, color=COLORS['grid'], alpha=0.7, linewidth=1)
    ax.set_ylim(36, 47)
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper left', frameon=False, bbox_to_anchor=(0,1.12), ncol=1)
    add_callout(ax, 2035, df.iloc[-1]['Obesity_universal'], '19.5% reduction', COLORS['universal'], xytext=(-120,-10), ha='right')
    add_callout(ax, 2035, df.iloc[-1]['Obesity_medical'], '2.4% reduction', COLORS['medical'], xytext=(10,10))
    ax.text(1, -0.18, 'Data: WHO, Census Bureau, CDC | Methodology: Logistic adoption curves, 28% efficacy',
            ha='right', va='bottom', fontsize=11, color=COLORS['baseline'], alpha=0.7, transform=ax.transAxes)
    plt.tight_layout(rect=[0, 0.08, 1, 0.97])
    plt.savefig('glp1_obesity_prevalence.png', dpi=300)
    plt.close()

def plot_annual_cases(years, df):
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(top=0.80, bottom=0.18)
    x = np.arange(len(years))
    med = df['Cases_avoided_medical']/1e6
    life = df['Cases_avoided_lifestyle']/1e6
    univ = df['Cases_avoided_universal']/1e6
    ax.bar(x-0.2, med, width=0.18, color=COLORS['medical'], label='Medical')
    ax.bar(x, life, width=0.18, color=COLORS['lifestyle'], label='Lifestyle')
    ax.bar(x+0.2, univ, width=0.18, color=COLORS['universal'], label='Universal')
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45)
    ax.set_xlabel('Year')
    ax.set_ylabel('Cases avoided (millions)')
    ax.set_title('Annual Obesity Cases Avoided', pad=18, loc='center')
    ax.text(0.5, 1.05, 'Projected Effects on U.S. Adult Obesity (2023–2035)', transform=ax.transAxes, ha='center', fontsize=15, color=COLORS['baseline'], alpha=0.85, fontweight='normal')
    ax.grid(True, color=COLORS['grid'], alpha=0.7, linewidth=1, axis='y')
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper left', frameon=False, bbox_to_anchor=(0,1.12), ncol=1)
    ax.text(x[-1]+0.2, univ.iloc[-1]+0.5, f"{univ.iloc[-1]:.1f}M", color=COLORS['universal'], fontsize=13, fontweight='bold', ha='center')
    ax.text(1, -0.18, 'Data: WHO, Census Bureau, CDC | Methodology: Logistic adoption curves, 28% efficacy',
            ha='right', va='bottom', fontsize=11, color=COLORS['baseline'], alpha=0.7, transform=ax.transAxes)
    plt.tight_layout(rect=[0, 0.08, 1, 0.97])
    plt.savefig('glp1_annual_cases_avoided.png', dpi=300)
    plt.close()

def plot_cumulative(years, df):
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(top=0.80, bottom=0.18)
    med = df['Cases_avoided_medical']/1e6
    life = df['Cases_avoided_lifestyle']/1e6
    univ = df['Cases_avoided_universal']/1e6
    cum_med = med.cumsum()
    cum_life = life.cumsum()
    cum_univ = univ.cumsum()
    ax.plot(years, cum_med, color=COLORS['medical'], lw=3, marker='o', label='Medical')
    ax.plot(years, cum_life, color=COLORS['lifestyle'], lw=3, marker='s', label='Lifestyle')
    ax.plot(years, cum_univ, color=COLORS['universal'], lw=3, marker='^', label='Universal')
    ax.set_xlabel('Year')
    ax.set_ylabel('Cumulative cases avoided (millions)')
    ax.set_title('Cumulative Impact (2023–2035)', pad=18, loc='center')
    ax.text(0.5, 1.05, 'Projected Effects on U.S. Adult Obesity (2023–2035)', transform=ax.transAxes, ha='center', fontsize=15, color=COLORS['baseline'], alpha=0.85, fontweight='normal')
    ax.grid(True, color=COLORS['grid'], alpha=0.7, linewidth=1)
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper left', frameon=False, bbox_to_anchor=(0,1.12), ncol=1)
    add_callout(ax, 2035, cum_univ.iloc[-1], f"{cum_univ.iloc[-1]:.1f}M total", COLORS['universal'], xytext=(-120,10), ha='right')
    ax.text(1, -0.18, 'Data: WHO, Census Bureau, CDC | Methodology: Logistic adoption curves, 28% efficacy',
            ha='right', va='bottom', fontsize=11, color=COLORS['baseline'], alpha=0.7, transform=ax.transAxes)
    plt.tight_layout(rect=[0, 0.08, 1, 0.97])
    plt.savefig('glp1_cumulative_impact.png', dpi=300)
    plt.close()

def main():
    df = pd.read_csv('GLP-1 intervention effects on obesity rates - data.csv')
    projection_df = df[df['YEAR'] >= 2023].copy()
    years = projection_df['YEAR']
    plot_adoption(years, projection_df)
    plot_prevalence(years, projection_df)
    plot_annual_cases(years, projection_df)
    plot_cumulative(years, projection_df)

if __name__ == "__main__":
    main() 