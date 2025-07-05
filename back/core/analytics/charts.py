# Chart configuration generator for frontend
from typing import Dict, List, Any

class ChartConfig:
    """Generate chart configurations for frontend libraries"""
    
    @staticmethod
    def bar_chart(title: str, labels: List[str], data: List[float], colors: List[str] = None) -> Dict:
        """Generate bar chart configuration"""
        return {
            'type': 'bar',
            'title': title,
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': title,
                    'data': data,
                    'backgroundColor': colors or ['#3B82F6'] * len(data)
                }]
            }
        }
    
    @staticmethod
    def line_chart(title: str, labels: List[str], data: List[float], color: str = '#3B82F6') -> Dict:
        """Generate line chart configuration"""
        return {
            'type': 'line',
            'title': title,
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': title,
                    'data': data,
                    'borderColor': color,
                    'backgroundColor': f'{color}20',
                    'fill': True,
                    'tension': 0.4
                }]
            }
        }
    
    @staticmethod
    def pie_chart(title: str, labels: List[str], data: List[float], colors: List[str] = None) -> Dict:
        """Generate pie chart configuration"""
        default_colors = ['#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#10B981']
        return {
            'type': 'doughnut',
            'title': title,
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors or default_colors[:len(data)]
                }]
            }
        }