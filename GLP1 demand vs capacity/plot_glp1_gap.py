import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

plt.rcParams.update({
    'font.family': 'Helvetica Neue, sans-serif',
    'font.size': 9,
    'axes.titlesize': 14,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 10,
    'figure.figsize': (8, 5),
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': ':',
    'grid.color': 'lightgrey'
})

COLORS = {
    'conservative': '#2E86AB',  # Midnight Blue
    'base': '#F7931E',          # Gold
    'aggressive': '#6C757D',    # Cool Grey
    'demand': '#1F2937',        # Dark Grey
    'capacity': '#9CA3AF',      # Light Grey
    'fill': '#F7931E',          # Gold for fills
    'text': '#374151'           # Dark text
}

def load_and_process_data(csv_path: str) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Load and process the GLP-1 projections data.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        Tuple of (df_all, dict_df) where df_all is long format and dict_df contains
        wide format DataFrames for each scenario
    """
    df = pd.read_csv(csv_path, dtype={
        'scenario': 'category',
        'year': 'int64',
        'years_elapsed': 'int64',
        'demand_cagr': 'float64',
        'capacity_cagr': 'float64',
        'projected_demand_pct': 'float64',
        'constrained_demand_pct': 'float64',
        'demand_index': 'float64',
        'projected_capacity_billions': 'float64',
        'capacity_index': 'float64',
        'gap_ratio': 'float64',
        'gap_severity': 'category',
        'cagr_differential': 'float64'
    })
    
    df = df.sort_values(['scenario', 'year']).reset_index(drop=True)
    
    baseline_2019 = 100
    for scenario in df['scenario'].unique():
        scenario_mask = df['scenario'] == scenario
        scenario_data = df[scenario_mask].copy()
        
        years_to_2019 = scenario_data['year'].iloc[0] - 2019
        if years_to_2019 > 0:
            demand_2019 = scenario_data['demand_index'].iloc[0] / ((1 + scenario_data['demand_cagr'].iloc[0]) ** years_to_2019)
            capacity_2019 = scenario_data['capacity_index'].iloc[0] / ((1 + scenario_data['capacity_cagr'].iloc[0]) ** years_to_2019)
            
            df.loc[scenario_mask, 'demand_index'] = scenario_data['demand_index'] / demand_2019 * baseline_2019
            df.loc[scenario_mask, 'capacity_index'] = scenario_data['capacity_index'] / capacity_2019 * baseline_2019

    df_all = df.copy()
    
    dict_df = {}
    for scenario in df['scenario'].unique():
        dict_df[scenario] = df[df['scenario'] == scenario].copy()
    
    return df_all, dict_df


def create_figure_1_all_scenarios(df_all: pd.DataFrame, output_dir: Path) -> None:
    """Create multi-scenario line chart showing gap widening over time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scenarios = ['conservative', 'base', 'aggressive']
    
    for scenario in scenarios:
        scenario_data = df_all[df_all['scenario'] == scenario]
        color = COLORS[scenario]
        
        ax.plot(scenario_data['year'], scenario_data['demand_index'], 
                color=color, linewidth=2.5, label=f'{scenario.title()} Demand')

        ax.plot(scenario_data['year'], scenario_data['capacity_index'], 
                color=color, linewidth=2, linestyle='--', 
                label=f'{scenario.title()} Capacity')
        
        final_data = scenario_data[scenario_data['year'] == 2030].iloc[0]
        gap_ratio = final_data['gap_ratio']
        ax.annotate(f'{gap_ratio:.1f}× gap', 
                   xy=(2030, final_data['demand_index']),
                   xytext=(2030.5, final_data['demand_index'] + 50),
                   fontsize=9, color=color, weight='bold',
                   arrowprops=dict(arrowstyle='->', color=color, alpha=0.7))
    
    ax.set_xlabel('Year', fontweight='semibold')
    ax.set_ylabel('Index (2019 = 100)', fontweight='semibold')
    ax.set_title('GLP-1 Demand vs Capacity Gap Analysis\nAll Scenarios', 
                 fontweight='bold', pad=20)
    
    ax.legend(loc='upper left', frameon=False, ncol=2)
    ax.grid(True, alpha=0.3, linestyle=':')
    
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'demand_capacity_gap_all_scenarios.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'demand_capacity_gap_all_scenarios.pdf', bbox_inches='tight')
    plt.close()


def create_figure_2_4_scenario_dive(df_scenario: pd.DataFrame, scenario: str, output_dir: Path) -> None:
    """Create shaded area chart for individual scenario deep-dive."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    color = COLORS[scenario]
    
    ax.plot(df_scenario['year'], df_scenario['demand_index'], 
            color=COLORS['demand'], linewidth=3, label='Demand Index')

    ax.plot(df_scenario['year'], df_scenario['capacity_index'], 
            color=COLORS['capacity'], linewidth=2, label='Capacity Index')

    ax.fill_between(df_scenario['year'], 
                   df_scenario['demand_index'], 
                   df_scenario['capacity_index'],
                   alpha=0.3, color=COLORS['fill'])

    inflection_years = [2027, 2030]
    for year in inflection_years:
        if year in df_scenario['year'].values:
            year_data = df_scenario[df_scenario['year'] == year].iloc[0]
            gap_ratio = year_data['gap_ratio']
            severity = year_data['gap_severity']
            
            ax.annotate(f'{gap_ratio:.1f}×\n{severity}', 
                       xy=(year, year_data['demand_index']),
                       xytext=(year + 0.5, year_data['demand_index'] + 30),
                       fontsize=8, color=color, weight='bold',
                       arrowprops=dict(arrowstyle='->', color=color, alpha=0.7),
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Year', fontweight='semibold')
    ax.set_ylabel('Index (2019 = 100)', fontweight='semibold')
    ax.set_title(f'GLP-1 Demand vs Capacity Gap\n{scenario.title()} Scenario', 
                 fontweight='bold', pad=20)
    
    ax.legend(loc='upper left', frameon=False)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_dir / f'demand_capacity_gap_{scenario}.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f'demand_capacity_gap_{scenario}.pdf', bbox_inches='tight')
    plt.close()


def create_figure_5_heatmap_gap_growth(df_all: pd.DataFrame, output_dir: Path) -> None:
    """Create heatmap showing gap ratio growth over time by scenario."""
    gap_matrix = df_all.pivot(index='scenario', columns='year', values='gap_ratio')
    
    gap_matrix = gap_matrix.reindex(['conservative', 'base', 'aggressive'])
    
    fig, ax = plt.subplots(figsize=(7, 4))
    
    sns.heatmap(gap_matrix, annot=True, fmt='.1f', cmap='YlOrRd', 
                cbar_kws={'label': 'Gap Ratio'}, ax=ax)
    
    ax.set_title('GLP-1 Demand-Capacity Gap Ratio Heatmap\n2019-2030', 
                 fontweight='bold', pad=20)
    ax.set_xlabel('Year', fontweight='semibold')
    ax.set_ylabel('Scenario', fontweight='semibold')
    
    plt.setp(ax.get_xticklabels(), rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'demand_capacity_gap_heatmap.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'demand_capacity_gap_heatmap.pdf', bbox_inches='tight')
    plt.close()


def create_figure_6_event_timeline(df_base: pd.DataFrame, output_dir: Path) -> None:
    """Create timeline with capacity-boost events overlaid on base scenario."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(df_base['year'], df_base['demand_index'], 
            color=COLORS['demand'], linewidth=3, label='Demand Index')
    ax.plot(df_base['year'], df_base['capacity_index'], 
            color=COLORS['capacity'], linewidth=2, label='Capacity Index')
    
    ax.fill_between(df_base['year'], 
                   df_base['demand_index'], 
                   df_base['capacity_index'],
                   alpha=0.3, color=COLORS['fill'])
    
    events = {
        2025: 'Novo Nordisk\nPlant Expansion',
        2027: 'Lilly Manufacturing\nFacility Online',
        2029: 'Additional\nCapacity Projects'
    }
    
    for year, event in events.items():
        if year in df_base['year'].values:
            year_data = df_base[df_base['year'] == year].iloc[0]
            
            ax.axvline(x=year, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
            
            ax.annotate(event, 
                       xy=(year, year_data['capacity_index']),
                       xytext=(year + 1, year_data['capacity_index'] + 50),
                       fontsize=8, color='red', weight='bold',
                       arrowprops=dict(arrowstyle='->', color='red', alpha=0.7),
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
    
    ax.set_xlabel('Year', fontweight='semibold')
    ax.set_ylabel('Index (2019 = 100)', fontweight='semibold')
    ax.set_title('GLP-1 Demand vs Capacity Timeline\nBase Scenario with Capacity Events', 
                 fontweight='bold', pad=20)
    
    ax.legend(loc='upper left', frameon=False)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'demand_capacity_gap_timeline.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'demand_capacity_gap_timeline.pdf', bbox_inches='tight')
    plt.close()


def create_figure_7_cover_gradient(output_dir: Path) -> None:
    """Create minimalist hero image with gradient background."""
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    
    width, height = 2200, 1000
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        ratio = y / height
        r = int(46 * (1 - ratio) + 247 * ratio)  # Navy to Gold
        g = int(62 * (1 - ratio) + 147 * ratio)
        b = int(134 * (1 - ratio) + 30 * ratio)
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
    except:
        font = ImageFont.load_default()
    
    title = "The GLP-1 Capacity Chasm, 2019-2030"
    
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), title, fill='white', font=font)

    img.save(output_dir / 'cover_gradient.png', 'PNG')


def main():
    """Main function to generate all figures."""
    output_dir = Path('./figures')
    output_dir.mkdir(exist_ok=True)
    
    csv_path = 'glp1_projections_20250711_182156.csv'
    
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df_all, dict_df = load_and_process_data(csv_path)
    
    print("Generating GLP-1 demand vs capacity gap analysis figures...")
    
    create_figure_1_all_scenarios(df_all, output_dir)
    print("✓ Figure 1: All scenarios chart created")
    
    for scenario in ['conservative', 'base', 'aggressive']:
        create_figure_2_4_scenario_dive(dict_df[scenario], scenario, output_dir)
        print(f"✓ Figure {2 + ['conservative', 'base', 'aggressive'].index(scenario)}: {scenario} scenario chart created")
    
    create_figure_5_heatmap_gap_growth(df_all, output_dir)
    print("✓ Figure 5: Gap ratio heatmap created")
    
    create_figure_6_event_timeline(dict_df['base'], output_dir)
    print("✓ Figure 6: Event timeline created")
    
    create_figure_7_cover_gradient(output_dir)
    print("✓ Figure 7: Cover gradient created")
    
    print(f"\nAll figures saved to {output_dir}")
    print("Files generated:")
    for file in output_dir.glob('*'):
        print(f"  - {file.name}")


if __name__ == "__main__":
    main() 
