"""
Power BI Data Context Agent

Retrieves relevant data from Power BI datasets via XMLA endpoint to provide
concrete examples and context for problem analysis.
"""

from .agent import DataContextAgent

__version__ = '1.0.0'
__all__ = ['DataContextAgent']
