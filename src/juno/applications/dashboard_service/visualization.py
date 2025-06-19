import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import base64
from io import BytesIO
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataVisualizationEngine:
    """
    Data visualization engine for generating charts and graphs from Jira analytics.
    Supports both static (matplotlib/seaborn) and interactive (plotly) visualizations.
    """
    
    def __init__(self):
        """Initialize the visualization engine."""
        # Set style for matplotlib/seaborn
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Configure plotly default template
        self.plotly_template = "plotly_white"
    
    def generate_velocity_chart(self, sprint_metrics: List[Dict[str, Any]], 
                              chart_type: str = 'plotly') -> Dict[str, Any]:
        """
        Generate velocity chart from sprint metrics.
        
        Args:
            sprint_metrics: List of sprint metrics dictionaries
            chart_type: 'plotly' or 'matplotlib'
            
        Returns:
            Dictionary with chart data and metadata
        """
        if not sprint_metrics:
            return {'error': 'No sprint metrics data available'}
        
        # Prepare data
        df = pd.DataFrame(sprint_metrics)
        
        if chart_type == 'plotly':
            return self._create_plotly_velocity_chart(df)
        else:
            return self._create_matplotlib_velocity_chart(df)
    
    def _create_plotly_velocity_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create interactive velocity chart using Plotly."""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Sprint Velocity (Story Points)', 'Completion Rate (%)'),
            vertical_spacing=0.1
        )
        
        # Velocity chart
        fig.add_trace(
            go.Scatter(
                x=df['sprint_name'],
                y=df['velocity'],
                mode='lines+markers',
                name='Velocity',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add planned vs completed points
        fig.add_trace(
            go.Bar(
                x=df['sprint_name'],
                y=df['planned_points'],
                name='Planned Points',
                marker_color='lightblue',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=df['sprint_name'],
                y=df['completed_points'],
                name='Completed Points',
                marker_color='darkblue'
            ),
            row=1, col=1
        )
        
        # Completion rate chart
        fig.add_trace(
            go.Scatter(
                x=df['sprint_name'],
                y=df['completion_rate'],
                mode='lines+markers',
                name='Completion Rate',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title='Sprint Velocity Analysis',
            template=self.plotly_template,
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Sprint", row=2, col=1)
        fig.update_yaxes(title_text="Story Points", row=1, col=1)
        fig.update_yaxes(title_text="Completion Rate (%)", row=2, col=1)
        
        return {
            'chart_type': 'plotly',
            'chart_data': fig.to_json(),
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'summary': {
                'avg_velocity': df['velocity'].mean(),
                'avg_completion_rate': df['completion_rate'].mean(),
                'total_sprints': len(df)
            }
        }
    
    def _create_matplotlib_velocity_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create static velocity chart using Matplotlib."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Velocity chart
        ax1.plot(df['sprint_name'], df['velocity'], marker='o', linewidth=2, markersize=6)
        ax1.set_title('Sprint Velocity (Story Points)')
        ax1.set_ylabel('Story Points')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Completion rate chart
        ax2.plot(df['sprint_name'], df['completion_rate'], marker='s', color='orange', linewidth=2, markersize=6)
        ax2.set_title('Sprint Completion Rate (%)')
        ax2.set_xlabel('Sprint')
        ax2.set_ylabel('Completion Rate (%)')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Convert to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'chart_type': 'matplotlib',
            'chart_image': image_base64,
            'summary': {
                'avg_velocity': df['velocity'].mean(),
                'avg_completion_rate': df['completion_rate'].mean(),
                'total_sprints': len(df)
            }
        }
    
    def generate_defect_analysis_charts(self, defect_metrics: Dict[str, Any], 
                                      chart_type: str = 'plotly') -> Dict[str, Any]:
        """
        Generate defect analysis charts.
        
        Args:
            defect_metrics: Defect metrics dictionary
            chart_type: 'plotly' or 'matplotlib'
            
        Returns:
            Dictionary with chart data and metadata
        """
        if chart_type == 'plotly':
            return self._create_plotly_defect_charts(defect_metrics)
        else:
            return self._create_matplotlib_defect_charts(defect_metrics)
    
    def _create_plotly_defect_charts(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive defect analysis charts using Plotly."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Defect Status Distribution',
                'Defects by Priority',
                'Defects by Component',
                'Defect Rate Overview'
            ),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        # Status distribution pie chart
        status_data = {
            'Open': metrics['open_defects'],
            'Resolved': metrics['resolved_defects']
        }
        
        fig.add_trace(
            go.Pie(
                labels=list(status_data.keys()),
                values=list(status_data.values()),
                name="Status"
            ),
            row=1, col=1
        )
        
        # Priority distribution bar chart
        if metrics['defects_by_priority']:
            priorities = list(metrics['defects_by_priority'].keys())
            priority_counts = list(metrics['defects_by_priority'].values())
            
            fig.add_trace(
                go.Bar(
                    x=priorities,
                    y=priority_counts,
                    name="Priority",
                    marker_color='red'
                ),
                row=1, col=2
            )
        
        # Component distribution bar chart
        if metrics['defects_by_component']:
            components = list(metrics['defects_by_component'].keys())[:10]  # Top 10
            component_counts = list(metrics['defects_by_component'].values())[:10]
            
            fig.add_trace(
                go.Bar(
                    x=components,
                    y=component_counts,
                    name="Component",
                    marker_color='orange'
                ),
                row=2, col=1
            )
        
        # Defect rate indicator
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=metrics['defect_rate'],
                title={'text': "Defect Rate (%)"},
                gauge={'axis': {'range': [None, 50]},
                       'bar': {'color': "darkred"},
                       'steps': [
                           {'range': [0, 10], 'color': "lightgreen"},
                           {'range': [10, 25], 'color': "yellow"},
                           {'range': [25, 50], 'color': "red"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 20}}
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Defect Analysis Dashboard',
            template=self.plotly_template,
            height=800,
            showlegend=False
        )
        
        return {
            'chart_type': 'plotly',
            'chart_data': fig.to_json(),
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'summary': metrics
        }
    
    def _create_matplotlib_defect_charts(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create static defect analysis charts using Matplotlib."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Status distribution pie chart
        status_data = {
            'Open': metrics['open_defects'],
            'Resolved': metrics['resolved_defects']
        }
        ax1.pie(status_data.values(), labels=status_data.keys(), autopct='%1.1f%%')
        ax1.set_title('Defect Status Distribution')
        
        # Priority distribution bar chart
        if metrics['defects_by_priority']:
            priorities = list(metrics['defects_by_priority'].keys())
            priority_counts = list(metrics['defects_by_priority'].values())
            ax2.bar(priorities, priority_counts, color='red', alpha=0.7)
            ax2.set_title('Defects by Priority')
            ax2.set_ylabel('Count')
            ax2.tick_params(axis='x', rotation=45)
        
        # Component distribution bar chart
        if metrics['defects_by_component']:
            components = list(metrics['defects_by_component'].keys())[:10]
            component_counts = list(metrics['defects_by_component'].values())[:10]
            ax3.bar(components, component_counts, color='orange', alpha=0.7)
            ax3.set_title('Defects by Component (Top 10)')
            ax3.set_ylabel('Count')
            ax3.tick_params(axis='x', rotation=45)
        
        # Defect rate text display
        ax4.text(0.5, 0.5, f"Defect Rate\n{metrics['defect_rate']:.1f}%", 
                ha='center', va='center', fontsize=20, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        ax4.set_title('Overall Defect Rate')
        
        plt.tight_layout()
        
        # Convert to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'chart_type': 'matplotlib',
            'chart_image': image_base64,
            'summary': metrics
        }
    
    def generate_lead_time_chart(self, lead_time_metrics: Dict[str, Any], 
                               chart_type: str = 'plotly') -> Dict[str, Any]:
        """
        Generate lead time analysis chart.
        
        Args:
            lead_time_metrics: Lead time metrics dictionary
            chart_type: 'plotly' or 'matplotlib'
            
        Returns:
            Dictionary with chart data and metadata
        """
        if chart_type == 'plotly':
            return self._create_plotly_lead_time_chart(lead_time_metrics)
        else:
            return self._create_matplotlib_lead_time_chart(lead_time_metrics)
    
    def _create_plotly_lead_time_chart(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive lead time chart using Plotly."""
        # Lead time by issue type
        if metrics['lead_time_by_type_hours']:
            issue_types = list(metrics['lead_time_by_type_hours'].keys())
            lead_times = [t/24 for t in metrics['lead_time_by_type_hours'].values()]  # Convert to days
            
            fig = go.Figure()
            
            fig.add_trace(
                go.Bar(
                    x=issue_types,
                    y=lead_times,
                    name='Lead Time (Days)',
                    marker_color='steelblue'
                )
            )
            
            # Add average line
            avg_lead_time_days = metrics['avg_lead_time_hours'] / 24
            fig.add_hline(
                y=avg_lead_time_days,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Average: {avg_lead_time_days:.1f} days"
            )
            
            fig.update_layout(
                title='Lead Time Analysis by Issue Type',
                xaxis_title='Issue Type',
                yaxis_title='Lead Time (Days)',
                template=self.plotly_template
            )
            
            return {
                'chart_type': 'plotly',
                'chart_data': fig.to_json(),
                'chart_html': fig.to_html(include_plotlyjs='cdn'),
                'summary': {
                    'avg_lead_time_days': avg_lead_time_days,
                    'median_lead_time_days': metrics['median_lead_time_hours'] / 24,
                    'p95_lead_time_days': metrics['percentile_95_lead_time_hours'] / 24
                }
            }
        else:
            return {'error': 'No lead time data available'}
    
    def _create_matplotlib_lead_time_chart(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create static lead time chart using Matplotlib."""
        if metrics['lead_time_by_type_hours']:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            issue_types = list(metrics['lead_time_by_type_hours'].keys())
            lead_times = [t/24 for t in metrics['lead_time_by_type_hours'].values()]  # Convert to days
            
            bars = ax.bar(issue_types, lead_times, color='steelblue', alpha=0.7)
            
            # Add average line
            avg_lead_time_days = metrics['avg_lead_time_hours'] / 24
            ax.axhline(y=avg_lead_time_days, color='red', linestyle='--', 
                      label=f'Average: {avg_lead_time_days:.1f} days')
            
            ax.set_title('Lead Time Analysis by Issue Type')
            ax.set_xlabel('Issue Type')
            ax.set_ylabel('Lead Time (Days)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                'chart_type': 'matplotlib',
                'chart_image': image_base64,
                'summary': {
                    'avg_lead_time_days': avg_lead_time_days,
                    'median_lead_time_days': metrics['median_lead_time_hours'] / 24,
                    'p95_lead_time_days': metrics['percentile_95_lead_time_hours'] / 24
                }
            }
        else:
            return {'error': 'No lead time data available'}
    
    def generate_trend_chart(self, trend_data: Dict[str, Any], 
                           chart_type: str = 'plotly') -> Dict[str, Any]:
        """
        Generate trend analysis chart.
        
        Args:
            trend_data: Trend analysis data
            chart_type: 'plotly' or 'matplotlib'
            
        Returns:
            Dictionary with chart data and metadata
        """
        if not trend_data.get('trend_data'):
            return {'error': 'No trend data available'}
        
        df = pd.DataFrame(trend_data['trend_data'])
        df['period_start'] = pd.to_datetime(df['period_start'])
        
        if chart_type == 'plotly':
            return self._create_plotly_trend_chart(df, trend_data)
        else:
            return self._create_matplotlib_trend_chart(df, trend_data)
    
    def _create_plotly_trend_chart(self, df: pd.DataFrame, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive trend chart using Plotly."""
        fig = go.Figure()
        
        # Main trend line
        fig.add_trace(
            go.Scatter(
                x=df['period_start'],
                y=df['value'],
                mode='lines+markers',
                name=trend_data['metric_type'].title(),
                line=dict(width=3),
                marker=dict(size=8)
            )
        )
        
        # Add trend line
        if len(df) >= 2:
            x_numeric = np.arange(len(df))
            slope = trend_data['trend_analysis']['slope']
            intercept = df['value'].iloc[0] - slope * 0
            trend_line = slope * x_numeric + intercept
            
            fig.add_trace(
                go.Scatter(
                    x=df['period_start'],
                    y=trend_line,
                    mode='lines',
                    name='Trend',
                    line=dict(dash='dash', color='red')
                )
            )
        
        fig.update_layout(
            title=f'{trend_data["metric_type"].title()} Trend Analysis',
            xaxis_title='Time Period',
            yaxis_title=trend_data['metric_type'].title(),
            template=self.plotly_template
        )
        
        return {
            'chart_type': 'plotly',
            'chart_data': fig.to_json(),
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'summary': trend_data['trend_analysis']
        }
    
    def _create_matplotlib_trend_chart(self, df: pd.DataFrame, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create static trend chart using Matplotlib."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Main trend line
        ax.plot(df['period_start'], df['value'], marker='o', linewidth=2, markersize=6)
        
        # Add trend line
        if len(df) >= 2:
            x_numeric = np.arange(len(df))
            slope = trend_data['trend_analysis']['slope']
            intercept = df['value'].iloc[0] - slope * 0
            trend_line = slope * x_numeric + intercept
            
            ax.plot(df['period_start'], trend_line, '--', color='red', alpha=0.7, label='Trend')
            ax.legend()
        
        ax.set_title(f'{trend_data["metric_type"].title()} Trend Analysis')
        ax.set_xlabel('Time Period')
        ax.set_ylabel(trend_data['metric_type'].title())
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'chart_type': 'matplotlib',
            'chart_image': image_base64,
            'summary': trend_data['trend_analysis']
        }
    
    def save_chart_to_file(self, chart_data: Dict[str, Any], file_path: str) -> bool:
        """
        Save chart to file.
        
        Args:
            chart_data: Chart data dictionary
            file_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if chart_data['chart_type'] == 'matplotlib':
                # Save base64 image to file
                image_data = base64.b64decode(chart_data['chart_image'])
                with open(file_path, 'wb') as f:
                    f.write(image_data)
            elif chart_data['chart_type'] == 'plotly':
                # Save HTML file
                with open(file_path, 'w') as f:
                    f.write(chart_data['chart_html'])
            
            logger.info(f"Chart saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save chart to {file_path}: {e}")
            return False

