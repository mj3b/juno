import os
import sys
import pytest

# Ensure juno-agent modules are importable
base = os.path.join(os.path.dirname(__file__), '../../juno-agent')
sys.path.insert(0, os.path.join(base, 'src'))
sys.path.insert(0, base)

viz_module = pytest.importorskip('visualization_engine')
DataVisualizationEngine = viz_module.DataVisualizationEngine


def sample_velocity_data():
    return [
        {
            'sprint_name': 'Sprint 1',
            'start_date': '2025-01-01T00:00:00',
            'end_date': '2025-01-14T23:59:59',
            'planned_points': 50,
            'completed_points': 45,
            'velocity': 45,
            'completion_rate': 90,
            'total_issues': 10,
            'completed_issues': 9,
        }
    ]


def test_velocity_chart_generation():
    viz = DataVisualizationEngine()
    data = sample_velocity_data()

    plotly_chart = viz.generate_velocity_chart(data, 'plotly')
    assert plotly_chart['chart_type'] == 'plotly'
    assert 'chart_data' in plotly_chart
    assert 'error' not in plotly_chart

    mpl_chart = viz.generate_velocity_chart(data, 'matplotlib')
    assert mpl_chart['chart_type'] == 'matplotlib'
    assert 'chart_image' in mpl_chart
    assert 'error' not in mpl_chart


def test_defect_and_lead_time_charts():
    viz = DataVisualizationEngine()

    defect_metrics = {
        'total_defects': 5,
        'open_defects': 2,
        'resolved_defects': 3,
        'defect_rate': 10.0,
        'avg_resolution_time_hours': 12,
        'defects_by_priority': {'High': 2, 'Low': 3},
        'defects_by_component': {'Backend': 2, 'Frontend': 3},
    }
    defect_chart = viz.generate_defect_analysis_charts(defect_metrics, 'plotly')
    assert 'error' not in defect_chart
    assert defect_chart['chart_type'] == 'plotly'

    lead_time_metrics = {
        'avg_lead_time_hours': 24,
        'median_lead_time_hours': 20,
        'percentile_95_lead_time_hours': 48,
        'lead_time_by_type_hours': {'Story': 20, 'Bug': 30},
    }
    lead_chart = viz.generate_lead_time_chart(lead_time_metrics, 'plotly')
    assert 'error' not in lead_chart
    assert lead_chart['chart_type'] == 'plotly'
