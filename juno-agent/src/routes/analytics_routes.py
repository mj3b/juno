from flask import Blueprint, jsonify, request, send_file
from src.analytics_engine import AdvancedAnalyticsEngine
from src.visualization_engine import DataVisualizationEngine
from datetime import datetime, timedelta
import tempfile
import os
import json
import csv
from io import StringIO, BytesIO
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)

# Initialize engines
analytics_engine = AdvancedAnalyticsEngine()
viz_engine = DataVisualizationEngine()

@analytics_bp.route('/velocity', methods=['POST'])
def get_velocity_metrics():
    """Get velocity metrics for a project."""
    try:
        data = request.get_json()
        if not data or 'project_key' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Project key is required'
            }), 400
        
        project_key = data['project_key']
        
        # Parse time range if provided
        time_range = None
        if 'time_range' in data:
            start_str = data['time_range'].get('start')
            end_str = data['time_range'].get('end')
            if start_str and end_str:
                start_date = datetime.fromisoformat(start_str.replace('Z', ''))
                end_date = datetime.fromisoformat(end_str.replace('Z', ''))
                time_range = (start_date, end_date)
        
        sprint_duration = data.get('sprint_duration_days', 14)
        
        # Calculate velocity metrics
        velocity_metrics = analytics_engine.calculate_velocity_metrics(
            project_key, time_range, sprint_duration
        )
        
        # Convert to serializable format
        metrics_data = [
            {
                'sprint_name': m.sprint_name,
                'start_date': m.start_date.isoformat(),
                'end_date': m.end_date.isoformat(),
                'planned_points': m.planned_points,
                'completed_points': m.completed_points,
                'velocity': m.velocity,
                'completion_rate': m.completion_rate,
                'total_issues': m.total_issues,
                'completed_issues': m.completed_issues
            }
            for m in velocity_metrics
        ]
        
        return jsonify({
            'status': 'success',
            'project_key': project_key,
            'velocity_metrics': metrics_data,
            'summary': {
                'total_sprints': len(metrics_data),
                'avg_velocity': sum(m['velocity'] for m in metrics_data) / len(metrics_data) if metrics_data else 0,
                'avg_completion_rate': sum(m['completion_rate'] for m in metrics_data) / len(metrics_data) if metrics_data else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Velocity metrics calculation failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/defects', methods=['POST'])
def get_defect_analysis():
    """Get defect analysis for a project."""
    try:
        data = request.get_json() or {}
        project_key = data.get('project_key')
        
        # Parse time range if provided
        time_range = None
        if 'time_range' in data:
            start_str = data['time_range'].get('start')
            end_str = data['time_range'].get('end')
            if start_str and end_str:
                start_date = datetime.fromisoformat(start_str.replace('Z', ''))
                end_date = datetime.fromisoformat(end_str.replace('Z', ''))
                time_range = (start_date, end_date)
        
        # Analyze defect patterns
        defect_metrics = analytics_engine.analyze_defect_patterns(project_key, time_range)
        
        # Convert to serializable format
        metrics_data = {
            'total_defects': defect_metrics.total_defects,
            'open_defects': defect_metrics.open_defects,
            'resolved_defects': defect_metrics.resolved_defects,
            'defect_rate': defect_metrics.defect_rate,
            'avg_resolution_time_hours': defect_metrics.avg_resolution_time,
            'defects_by_priority': defect_metrics.defects_by_priority,
            'defects_by_component': defect_metrics.defects_by_component,
            'reopened_defects': defect_metrics.reopened_defects,
            'escape_rate': defect_metrics.escape_rate
        }
        
        return jsonify({
            'status': 'success',
            'project_key': project_key,
            'defect_analysis': metrics_data
        })
        
    except Exception as e:
        logger.error(f"Defect analysis failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/lead-time', methods=['POST'])
def get_lead_time_analysis():
    """Get lead time analysis for a project."""
    try:
        data = request.get_json() or {}
        project_key = data.get('project_key')
        
        # Parse time range if provided
        time_range = None
        if 'time_range' in data:
            start_str = data['time_range'].get('start')
            end_str = data['time_range'].get('end')
            if start_str and end_str:
                start_date = datetime.fromisoformat(start_str.replace('Z', ''))
                end_date = datetime.fromisoformat(end_str.replace('Z', ''))
                time_range = (start_date, end_date)
        
        # Calculate lead time metrics
        lead_time_metrics = analytics_engine.calculate_lead_time_metrics(project_key, time_range)
        
        # Convert to serializable format
        metrics_data = {
            'avg_lead_time_hours': lead_time_metrics.avg_lead_time,
            'avg_cycle_time_hours': lead_time_metrics.avg_cycle_time,
            'median_lead_time_hours': lead_time_metrics.median_lead_time,
            'median_cycle_time_hours': lead_time_metrics.median_cycle_time,
            'percentile_95_lead_time_hours': lead_time_metrics.percentile_95_lead_time,
            'percentile_95_cycle_time_hours': lead_time_metrics.percentile_95_cycle_time,
            'lead_time_by_type_hours': lead_time_metrics.lead_time_by_type,
            'cycle_time_by_type_hours': lead_time_metrics.cycle_time_by_type
        }
        
        return jsonify({
            'status': 'success',
            'project_key': project_key,
            'lead_time_analysis': metrics_data
        })
        
    except Exception as e:
        logger.error(f"Lead time analysis failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/trends', methods=['POST'])
def get_trend_analysis():
    """Get trend analysis for a metric."""
    try:
        data = request.get_json()
        if not data or 'project_key' not in data or 'metric_type' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Project key and metric type are required'
            }), 400
        
        project_key = data['project_key']
        metric_type = data['metric_type']
        
        # Parse time range
        if 'time_range' not in data:
            # Default to last 3 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            time_range = (start_date, end_date)
        else:
            start_str = data['time_range']['start']
            end_str = data['time_range']['end']
            start_date = datetime.fromisoformat(start_str.replace('Z', ''))
            end_date = datetime.fromisoformat(end_str.replace('Z', ''))
            time_range = (start_date, end_date)
        
        interval_days = data.get('interval_days', 7)
        
        # Generate trend analysis
        trend_data = analytics_engine.generate_trend_analysis(
            project_key, metric_type, time_range, interval_days
        )
        
        return jsonify({
            'status': 'success',
            'trend_analysis': trend_data
        })
        
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/comprehensive-report', methods=['POST'])
def get_comprehensive_report():
    """Get comprehensive analytics report for a project."""
    try:
        data = request.get_json()
        if not data or 'project_key' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Project key is required'
            }), 400
        
        project_key = data['project_key']
        
        # Parse time range if provided
        time_range = None
        if 'time_range' in data:
            start_str = data['time_range'].get('start')
            end_str = data['time_range'].get('end')
            if start_str and end_str:
                start_date = datetime.fromisoformat(start_str.replace('Z', ''))
                end_date = datetime.fromisoformat(end_str.replace('Z', ''))
                time_range = (start_date, end_date)
        
        # Generate comprehensive report
        report = analytics_engine.generate_comprehensive_report(project_key, time_range)
        
        return jsonify({
            'status': 'success',
            'comprehensive_report': report
        })
        
    except Exception as e:
        logger.error(f"Comprehensive report generation failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/visualize/velocity', methods=['POST'])
def visualize_velocity():
    """Generate velocity visualization."""
    try:
        data = request.get_json()
        if not data or 'velocity_metrics' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Velocity metrics data is required'
            }), 400
        
        velocity_metrics = data['velocity_metrics']
        chart_type = data.get('chart_type', 'plotly')
        
        # Generate visualization
        chart_data = viz_engine.generate_velocity_chart(velocity_metrics, chart_type)
        
        return jsonify({
            'status': 'success',
            'visualization': chart_data
        })
        
    except Exception as e:
        logger.error(f"Velocity visualization failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/visualize/defects', methods=['POST'])
def visualize_defects():
    """Generate defect analysis visualization."""
    try:
        data = request.get_json()
        if not data or 'defect_metrics' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Defect metrics data is required'
            }), 400
        
        defect_metrics = data['defect_metrics']
        chart_type = data.get('chart_type', 'plotly')
        
        # Generate visualization
        chart_data = viz_engine.generate_defect_analysis_charts(defect_metrics, chart_type)
        
        return jsonify({
            'status': 'success',
            'visualization': chart_data
        })
        
    except Exception as e:
        logger.error(f"Defect visualization failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/visualize/lead-time', methods=['POST'])
def visualize_lead_time():
    """Generate lead time visualization."""
    try:
        data = request.get_json()
        if not data or 'lead_time_metrics' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Lead time metrics data is required'
            }), 400
        
        lead_time_metrics = data['lead_time_metrics']
        chart_type = data.get('chart_type', 'plotly')
        
        # Generate visualization
        chart_data = viz_engine.generate_lead_time_chart(lead_time_metrics, chart_type)
        
        return jsonify({
            'status': 'success',
            'visualization': chart_data
        })
        
    except Exception as e:
        logger.error(f"Lead time visualization failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/visualize/trends', methods=['POST'])
def visualize_trends():
    """Generate trend visualization."""
    try:
        data = request.get_json()
        if not data or 'trend_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Trend data is required'
            }), 400
        
        trend_data = data['trend_data']
        chart_type = data.get('chart_type', 'plotly')
        
        # Generate visualization
        chart_data = viz_engine.generate_trend_chart(trend_data, chart_type)
        
        return jsonify({
            'status': 'success',
            'visualization': chart_data
        })
        
    except Exception as e:
        logger.error(f"Trend visualization failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/export/csv', methods=['POST'])
def export_csv():
    """Export analytics data to CSV."""
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Data is required for export'
            }), 400
        
        export_data = data['data']
        filename = data.get('filename', 'analytics_export.csv')
        
        # Create CSV content
        output = StringIO()
        
        if isinstance(export_data, list) and export_data:
            # List of dictionaries - use keys as headers
            fieldnames = export_data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(export_data)
        elif isinstance(export_data, dict):
            # Single dictionary - transpose to rows
            writer = csv.writer(output)
            for key, value in export_data.items():
                writer.writerow([key, value])
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid data format for CSV export'
            }), 400
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(output.getvalue())
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"CSV export failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/export/json', methods=['POST'])
def export_json():
    """Export analytics data to JSON."""
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Data is required for export'
            }), 400
        
        export_data = data['data']
        filename = data.get('filename', 'analytics_export.json')
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(export_data, temp_file, indent=2, default=str)
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"JSON export failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/metrics-list', methods=['GET'])
def get_available_metrics():
    """Get list of available analytics metrics."""
    metrics = [
        {
            'name': 'velocity',
            'description': 'Sprint velocity and completion rates',
            'parameters': ['project_key', 'time_range', 'sprint_duration_days']
        },
        {
            'name': 'defects',
            'description': 'Defect analysis and quality metrics',
            'parameters': ['project_key', 'time_range']
        },
        {
            'name': 'lead_time',
            'description': 'Lead time and cycle time analysis',
            'parameters': ['project_key', 'time_range']
        },
        {
            'name': 'trends',
            'description': 'Trend analysis for various metrics',
            'parameters': ['project_key', 'metric_type', 'time_range', 'interval_days']
        },
        {
            'name': 'comprehensive_report',
            'description': 'Complete analytics report with all metrics',
            'parameters': ['project_key', 'time_range']
        }
    ]
    
    return jsonify({
        'status': 'success',
        'available_metrics': metrics
    })

