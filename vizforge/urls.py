"""vizforge URL configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, re_path
from eviflow_vis.views import (
    chart_workbench,
    analyze_chart_types,
    check_chart_layout_overlap,
    extract_chart_text_segments,
    chart_layout_report,
    chart_layout_export_docx,
)
from django.views import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # Chart studio (distinct from legacy demo URL prefixes)
    path('cs-workbench/', chart_workbench, name='chart_workbench_page'),
    path('cs-workbench/api/render-chart/', chart_workbench, name='chart_workbench_render'),
    path('cs-workbench/api/chart-type-scores/', analyze_chart_types, name='analyze_chart_types'),
    path('cs-workbench/api/layout-overlap/', check_chart_layout_overlap, name='check_chart_layout_overlap'),
    path('cs-workbench/api/extract-segments/', extract_chart_text_segments, name='extract_chart_text_segments'),
    path('cs-workbench/layout-board/', chart_layout_report, name='chart_layout_report'),
    path('cs-workbench/layout-board/export-docx/', chart_layout_export_docx, name='chart_layout_export_docx'),
    re_path(r'^cs-workbench/static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
]
