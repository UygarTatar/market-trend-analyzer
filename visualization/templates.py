"""
ONYX Design System - Centralized Styling for Market Analysis Charts
"""

# Premium Dark Mode Palette
COLORS = {
    "background": "#0b0f19",
    "card_bg": "#161b22",
    "text_primary": "#ffffff",
    "text_secondary": "#8b949e",
    "accent_primary": "#00f5d4",  # Cyan/Aqua
    "accent_secondary": "#7b2cbf", # Purple
    "success": "#2ecc71",
    "warning": "#f1c40f",
    "danger": "#e74c3c",
    "chart_colors": ["#00f5d4", "#7b2cbf", "#ff006e", "#3a86ff", "#fb5607"]
}

# Matplotlib Style Override
MPL_STYLE = {
    "figure.facecolor": COLORS["background"],
    "axes.facecolor": COLORS["background"],
    "axes.edgecolor": COLORS["text_secondary"],
    "axes.labelcolor": COLORS["text_primary"],
    "xtick.color": COLORS["text_secondary"],
    "ytick.color": COLORS["text_secondary"],
    "grid.color": "#30363d",
    "text.color": COLORS["text_primary"],
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Roboto", "Arial"]
}

# Plotly Layout Defaults
PLOTLY_DARK_LAYOUT = {
    "paper_bgcolor": COLORS["background"],
    "plot_bgcolor": COLORS["background"],
    "font": {"color": COLORS["text_primary"], "family": "Inter, sans-serif"},
    "xaxis": {"gridcolor": "#30363d", "linecolor": "#30363d"},
    "yaxis": {"gridcolor": "#30363d", "linecolor": "#30363d"},
}
