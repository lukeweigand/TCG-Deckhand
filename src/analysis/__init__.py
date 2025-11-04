"""Strategic analysis tools for TCG Deckhand.

This package provides analytical tools to help players understand positions:
- Win advantage calculator (position → win probability)
- Best move suggestions (ranked action recommendations)
- Strategic insights (pattern recognition, threat assessment)
"""

from src.analysis.win_advantage import calculate_win_advantage, WinAdvantageResult

__all__ = ['calculate_win_advantage', 'WinAdvantageResult']
