#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Documentation Builder
Automatically discovers and categorizes financial documents, builds self-contained HTML viewer.

Based on the EchoFlux documentation system, adapted for personal financial documents.

Usage:
    python financial_docs/build_financial_docs.py

What it does:
1. Scans Archive/ for all .md, .pdf, .csv, .jpg files
2. Auto-categorizes files based on financial document types
3. Builds self-contained HTML viewer with embedded content
4. Creates easy-to-navigate financial document hub

For future reference:
- Add new financial documents to financial_docs/Archive/
- Run this script to rebuild the viewer
- Open financial_hub.html in any browser
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Base directory is financial_docs/
BASE_DIR = Path(__file__).parent.parent  # Go up from scripts/ to financial_docs/
PROJECT_ROOT = BASE_DIR.parent
ARCHIVE_DIR = BASE_DIR / "Archive"

# File categorization rules based on financial document types
CATEGORIZATION_RULES = {
    'Current Status & Planning': {
        'patterns': ['CURRENT_FINANCIAL_STATUS', 'FINANCIAL_ACTION_PLAN', 'BUDGET_GUIDELINES', 'DASHBOARD', 'IMPORTANT_DATES'],
        'icon': '📊',
        'description': 'Current financial position, action plans, budget guidelines, and key dates'
    },
    'Analysis & Insights': {
        'patterns': ['SPENDING_ANALYSIS', 'PROPERTY_ANALYSIS', 'ANALYSIS', 'TRANSACTION_ANALYSIS', 'SCENARIO_ANALYSIS', 'FINANCIAL_TRENDS'],
        'icon': '📈',
        'description': 'Spending patterns, property analysis, scenario modeling, and financial trends'
    },
    'Reports & Reviews': {
        'patterns': ['MONTHLY_REVIEW', 'HEALTH_SCORECARD', 'BUDGET_VS_ACTUAL'],
        'icon': '📝',
        'description': 'Monthly reviews, financial health scores, and budget tracking'
    },
    'Tax Documents': {
        'patterns': ['W2_', '1099', '1098', '1095', 'Tax Return', 'W9_'],
        'icon': '📋',
        'description': 'W2s, 1099s, 1098s, and tax returns'
    },
    'Transaction Data': {
        'patterns': ['AllTransactions', 'transactions', '.csv'],
        'icon': '💳',
        'description': 'Transaction history and spending data'
    },
    'Property Documents': {
        'patterns': ['HVAC', 'Maintenance', 'Assessment', 'Jamie'],
        'icon': '🏠',
        'description': 'Property-related documents and receipts'
    },
    'Budget Screenshots': {
        'patterns': ['.jpg', '.png', 'Budget', 'Money-as-of'],
        'icon': '📸',
        'description': 'Budget screenshots and financial snapshots'
    },
    'Other Financial Documents': {
        'patterns': ['.xlsx', '.pdf'],
        'icon': '📄',
        'description': 'Other financial documents and spreadsheets'
    }
}

# Badge assignment rules
BADGE_RULES = {
    'important': ['CURRENT_FINANCIAL_STATUS', 'FINANCIAL_ACTION_PLAN'],
    'analysis': ['SPENDING_ANALYSIS', 'PROPERTY_ANALYSIS'],
    'tax': ['W2', '1099', '1098', 'Tax Return'],
    'large': ['AllTransactions', 'SPENDING_ANALYSIS', 'PROPERTY_ANALYSIS']
}

def categorize_file(filename):
    """Determine the best category for a file based on its name"""
    filename_upper = filename.upper()

    # Check each category's patterns
    for category, info in CATEGORIZATION_RULES.items():
        for pattern in info['patterns']:
            if pattern.upper() in filename_upper:
                return category, info['icon']

    # Default category
    return 'Other Financial Documents', '📄'

def determine_badge(filename):
    """Determine if a file should have a badge"""
    filename_upper = filename.upper()

    for badge_type, patterns in BADGE_RULES.items():
        for pattern in patterns:
            if pattern.upper() in filename_upper:
                return badge_type

    return None

def make_friendly_name(filename):
    """Convert filename to friendly display name"""
    # Remove extension
    name = Path(filename).stem

    # Special cases for known files
    replacements = {
        'CURRENT_FINANCIAL_STATUS': 'Current Financial Status',
        'FINANCIAL_ACTION_PLAN': 'Financial Action Plan',
        'SPENDING_ANALYSIS': 'Spending Analysis & Waste Report',
        'BUDGET_GUIDELINES': 'Budget Guidelines',
        'AllTransactions': 'All Transactions (CSV)'
    }

    if name in replacements:
        return replacements[name]

    # Replace underscores with spaces and title case
    name = name.replace('_', ' ').replace('-', ' ')
    name = name.title()

    return name

def scan_archive_directory():
    """Scan Archive/ directory and subdirectories for all financial document files"""
    if not ARCHIVE_DIR.exists():
        print(f"⚠️  Warning: Archive directory not found: {ARCHIVE_DIR}")
        return []

    files = []

    # Scan for markdown, PDFs, CSV, and image files in Archive and subdirectories
    for ext in ['*.md', '*.pdf', '*.csv', '*.xlsx', '*.jpg', '*.png']:
        # Scan root Archive directory
        for filepath in ARCHIVE_DIR.glob(ext):
            files.append(filepath)
        # Scan subdirectories
        for filepath in ARCHIVE_DIR.glob(f'*/{ext}'):
            files.append(filepath)

    return sorted(files)

def build_docs_structure_from_archive():
    """Build documentation structure by scanning Archive/ directory"""
    files = scan_archive_directory()

    print(f"📁 Found {len(files)} files in Archive/")

    # Group files by category
    structure = {}

    for filepath in files:
        filename = filepath.name

        # Get relative path from BASE_DIR (e.g., "Archive/tax/W2_2024.pdf")
        relative_path = filepath.relative_to(BASE_DIR)

        # Determine category and icon
        category, default_icon = categorize_file(filename)

        # Determine badge
        badge = determine_badge(filename)

        # Determine file type
        ext = filepath.suffix.lower()
        if ext in ['.jpg', '.png']:
            file_type = 'image'
        elif ext == '.pdf':
            file_type = 'pdf'
        elif ext == '.csv':
            file_type = 'csv'
        elif ext == '.xlsx':
            file_type = 'xlsx'
        else:
            file_type = 'markdown'

        # Create friendly name
        friendly_name = make_friendly_name(filename)

        # Build file entry (use forward slashes for web compatibility)
        file_entry = {
            'name': friendly_name,
            'file': str(relative_path).replace('\\', '/'),
            'icon': default_icon,
            'type': file_type
        }

        if badge:
            file_entry['badge'] = badge

        # Add to structure
        if category not in structure:
            structure[category] = []

        structure[category].append(file_entry)

    # Sort items within each category by priority then name
    for category in structure:
        # Priority: important/tax badges first, then alphabetical
        structure[category] = sorted(
            structure[category],
            key=lambda x: (
                0 if x.get('badge') == 'important' else
                1 if x.get('badge') == 'tax' else
                2 if x.get('badge') == 'analysis' else 3,
                x['name']
            )
        )

    return structure

def load_file_content(file_path):
    """Load file content for markdown files only"""
    full_path = BASE_DIR / file_path

    if not full_path.exists():
        print(f"⚠️  Warning: File not found: {file_path}")
        return None

    # For non-markdown files, just return the path
    if not file_path.endswith('.md'):
        return file_path

    # For markdown files, read as UTF-8
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Properly escape for JSON (which is safer than template literals)
            # We'll use JSON encoding instead of template literals
            return content
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return None

def build_embedded_data(structure):
    """Build embedded data object with markdown file contents"""
    embedded = {}

    for category, items in structure.items():
        for item in items:
            file_path = item['file']
            content = load_file_content(file_path)
            if content is not None:
                # Create a unique key for each document
                key = f"{category}::{item['name']}"
                embedded[key] = {
                    'content': content,
                    'type': item.get('type', 'markdown'),
                    'file': file_path
                }

    return embedded

def generate_html(embedded_data, structure):
    """Generate the self-contained HTML file for financial documents"""

    # Convert structure to JSON (without file content)
    docs_json = json.dumps(structure, indent=8)

    # Build JavaScript object with embedded content using JSON for safety
    embedded_dict = {}
    for key, data in embedded_data.items():
        content_type = data['type']
        content = data['content']
        file_path = data['file']

        # Normalize paths to forward slashes for JavaScript/HTML compatibility
        if isinstance(file_path, str):
            file_path = file_path.replace('\\', '/')

        if content_type == 'markdown':
            # For markdown, embed the content (will be JSON-encoded)
            embedded_dict[key] = {
                'type': 'markdown',
                'content': content
            }
        else:
            # For other files, store relative path with forward slashes
            embedded_dict[key] = {
                'type': content_type,
                'path': file_path
            }

    # Convert to JSON string (properly escapes everything)
    # Use ensure_ascii=True for Windows compatibility
    embedded_js = "const embeddedContent = " + json.dumps(embedded_dict, ensure_ascii=True, indent=4) + ";\n"

    # Load dashboard data if it exists
    dashboard_data_path = BASE_DIR / 'Archive' / 'processed' / 'dashboard_data.json'
    dashboard_js = ""
    if dashboard_data_path.exists():
        try:
            with open(dashboard_data_path, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
            dashboard_js = "\nconst EMBEDDED_DASHBOARD_DATA = " + json.dumps(dashboard_data, ensure_ascii=True) + ";\n"
            print("   📊 Dashboard data embedded successfully")
        except Exception as e:
            print(f"   ⚠️  Could not load dashboard data: {e}")
            dashboard_js = "\nconst EMBEDDED_DASHBOARD_DATA = null;\n"
    else:
        print("   ⚠️  Dashboard data not found, will show placeholder")
        dashboard_js = "\nconst EMBEDDED_DASHBOARD_DATA = null;\n"

    html_template = '''<!DOCTYPE html>
<html lang="en">
<!--
    Personal Financial Hub - Auto-Generated Financial Document Viewer
    Generated by build_financial_docs.py

    Features:
    - Auto-discovered from Archive/ directory
    - Categorized by document type
    - Embedded markdown content
    - Links to PDF/Excel/CSV files
    - Image viewer
-->
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Financial Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/marked@9.1.6/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-color: #0097A7;
            --primary-light: #00BCD4;
            --secondary-color: #1976D2;
            --accent-color: #F57C00;
            --danger-color: #D32F2F;
            --dark-bg: #1a1d23;
            --card-bg: #2d3340;
            --text-primary: #ffffff;
            --text-secondary: #B0BEC5;
            --border-color: rgba(0, 188, 212, 0.3);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--dark-bg) 0%, var(--card-bg) 100%);
            color: var(--text-primary);
            overflow-x: hidden;
            min-height: 100vh;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            padding: 50px 20px;
            background: rgba(0, 188, 212, 0.1);
            border-radius: 15px;
            margin-bottom: 40px;
            border: 2px solid var(--primary-color);
        }

        .search-container {
            max-width: 600px;
            margin: 30px auto 0;
            position: relative;
        }

        .search-box {
            width: 100%;
            padding: 15px 50px 15px 20px;
            font-size: 1em;
            border: 2px solid var(--primary-color);
            border-radius: 25px;
            background: rgba(45, 51, 64, 0.9);
            color: var(--text-primary);
            outline: none;
            transition: all 0.3s;
        }

        .search-box:focus {
            border-color: var(--primary-light);
            box-shadow: 0 0 20px rgba(0, 188, 212, 0.3);
        }

        .search-icon {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.2em;
            color: var(--text-secondary);
        }

        .search-results {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 188, 212, 0.1);
            border-radius: 10px;
            display: none;
        }

        .search-results.visible {
            display: block;
        }

        .charts-section {
            background: rgba(45, 51, 64, 0.9);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            border: 2px solid var(--primary-color);
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }

        .chart-container {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 10px;
            min-height: 300px;
        }

        .chart-title {
            color: var(--primary-light);
            font-size: 1.3em;
            margin-bottom: 15px;
            text-align: center;
        }

        /* Dashboard Cards */
        .dashboard-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .dashboard-card {
            background: linear-gradient(135deg, rgba(0, 188, 212, 0.2), rgba(0, 188, 212, 0.05));
            border: 2px solid var(--primary-color);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }

        .dashboard-card-title {
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .dashboard-card-value {
            color: var(--primary-light);
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .dashboard-card-subtitle {
            color: var(--text-secondary);
            font-size: 0.85em;
        }

        /* Alerts Banner */
        .alerts-banner {
            background: rgba(211, 47, 47, 0.1);
            border: 2px solid #D32F2F;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }

        .alert-item {
            padding: 12px;
            margin: 8px 0;
            background: rgba(0, 0, 0, 0.3);
            border-left: 4px solid #D32F2F;
            border-radius: 6px;
        }

        .alert-item.warning {
            border-left-color: #F57C00;
        }

        .alert-item.critical {
            border-left-color: #D32F2F;
        }

        .alert-message {
            color: var(--text-light);
            font-weight: bold;
            margin-bottom: 5px;
        }

        .alert-action {
            color: var(--text-secondary);
            font-size: 0.9em;
        }

        /* Budget Progress Bars */
        .budget-section {
            background: rgba(45, 51, 64, 0.9);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            border: 2px solid var(--primary-color);
        }

        .budget-item {
            margin-bottom: 20px;
        }

        .budget-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            color: var(--text-light);
        }

        .budget-category {
            font-weight: bold;
        }

        .budget-amounts {
            font-size: 0.9em;
            color: var(--text-secondary);
        }

        .budget-progress-bar {
            height: 24px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }

        .budget-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
            border-radius: 12px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.85em;
            font-weight: bold;
        }

        .budget-progress-fill.over-budget {
            background: linear-gradient(90deg, #D32F2F, #FF5252);
        }

        h1 {
            font-size: 3em;
            color: var(--primary-light);
            margin-bottom: 15px;
            text-shadow: 0 0 20px rgba(0, 188, 212, 0.5);
        }

        .subtitle {
            color: var(--text-secondary);
            font-size: 1.2em;
        }

        .docs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        .doc-card {
            background: linear-gradient(135deg, rgba(45, 51, 64, 0.9), rgba(30, 35, 45, 0.9));
            border-radius: 15px;
            padding: 25px;
            border: 2px solid transparent;
            transition: all 0.3s;
            cursor: pointer;
            position: relative;
        }

        .doc-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary-color);
            box-shadow: 0 10px 30px rgba(0, 188, 212, 0.3);
        }

        .doc-header {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            align-items: center;
        }

        .doc-icon {
            font-size: 2em;
        }

        .doc-title {
            font-size: 1.2em;
            color: var(--primary-light);
            margin-bottom: 8px;
            font-weight: 600;
        }

        .doc-category-badge {
            display: inline-block;
            padding: 4px 12px;
            background: rgba(0, 188, 212, 0.2);
            border: 1px solid var(--primary-color);
            border-radius: 12px;
            font-size: 0.8em;
            color: var(--primary-light);
            margin-top: 10px;
        }

        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 0.75em;
            font-weight: bold;
            margin-left: 10px;
        }

        .badge-important {
            background: #D32F2F;
            color: white;
        }

        .badge-tax {
            background: #1976D2;
            color: white;
        }

        .badge-analysis {
            background: #F57C00;
            color: white;
        }

        .category-section {
            margin-bottom: 50px;
        }

        .category-header {
            font-size: 1.8em;
            color: var(--primary-light);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid var(--primary-color);
        }

        .category-description {
            color: var(--text-secondary);
            margin-bottom: 20px;
            font-size: 1.1em;
        }

        /* Panel styles */
        .panel-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 100;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s;
        }

        .panel-overlay.visible {
            opacity: 1;
            visibility: visible;
        }

        .sliding-panel {
            position: fixed;
            top: 0;
            right: -60%;
            width: 60%;
            height: 100%;
            background: var(--dark-bg);
            z-index: 101;
            transition: right 0.4s;
            box-shadow: -5px 0 30px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
        }

        .sliding-panel.visible {
            right: 0;
        }

        .panel-header {
            padding: 25px;
            background: rgba(0, 188, 212, 0.1);
            border-bottom: 2px solid var(--primary-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .panel-title {
            font-size: 1.5em;
            color: var(--primary-light);
            font-weight: 600;
        }

        .close-btn {
            padding: 10px 20px;
            background: var(--danger-color);
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
        }

        .close-btn:hover {
            background: #B71C1C;
        }

        .panel-content {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
        }

        /* Markdown content styles */
        .markdown-content {
            line-height: 1.6;
        }

        .markdown-content h1 {
            color: var(--primary-light);
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 10px;
            margin: 30px 0 20px 0;
        }

        .markdown-content h2 {
            color: var(--primary-color);
            margin: 25px 0 15px 0;
            border-left: 4px solid var(--primary-color);
            padding-left: 12px;
        }

        .markdown-content h3 {
            color: var(--primary-light);
            margin: 20px 0 10px 0;
        }

        .markdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: rgba(0, 0, 0, 0.3);
        }

        .markdown-content th {
            background: rgba(0, 188, 212, 0.2);
            color: var(--primary-light);
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }

        .markdown-content td {
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .markdown-content code {
            background: rgba(0, 188, 212, 0.15);
            padding: 3px 8px;
            border-radius: 4px;
            color: var(--primary-light);
        }

        .markdown-content pre {
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid var(--primary-color);
        }

        .file-link {
            display: inline-block;
            padding: 15px 25px;
            background: var(--secondary-color);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 10px 0;
            font-weight: 600;
        }

        .file-link:hover {
            background: #1565C0;
        }

        @media (max-width: 1024px) {
            .sliding-panel {
                width: 80%;
                right: -80%;
            }

            .charts-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 2em;
            }

            .subtitle {
                font-size: 1em;
            }

            header {
                padding: 30px 15px;
            }

            .container {
                padding: 10px;
            }

            .docs-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }

            .doc-card {
                padding: 20px;
            }

            .sliding-panel {
                width: 100%;
                right: -100%;
            }

            .panel-content {
                padding: 20px;
            }

            .charts-section {
                padding: 20px;
            }

            .charts-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .chart-container {
                min-height: 250px;
            }

            .search-box {
                font-size: 0.9em;
                padding: 12px 45px 12px 15px;
            }

            .category-header {
                font-size: 1.5em;
            }
        }

        /* Touch-friendly enhancements */
        @media (hover: none) and (pointer: coarse) {
            .doc-card {
                -webkit-tap-highlight-color: rgba(0, 188, 212, 0.2);
            }

            .close-btn, .file-link {
                min-height: 44px;
                min-width: 44px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💰 Personal Financial Hub</h1>
            <p class="subtitle">Consolidated Financial Documents & Analysis</p>
            <p class="subtitle" style="font-size: 0.9em; margin-top: 10px;">Last Updated: ''' + datetime.now().strftime("%B %d, %Y") + '''</p>

            <div class="search-container">
                <input type="text"
                       id="searchBox"
                       class="search-box"
                       placeholder="Search financial documents..."
                       oninput="performSearch(this.value)">
                <span class="search-icon">🔍</span>
                <div id="searchResults" class="search-results"></div>
            </div>
        </header>

        <!-- Alerts Banner -->
        <div id="alertsContainer" style="display: none;">
            <!-- Alerts populated by JavaScript -->
        </div>

        <!-- Dashboard Cards -->
        <div class="dashboard-cards" id="dashboardCards">
            <div class="dashboard-card">
                <div class="dashboard-card-title">💰 Liquid Cash</div>
                <div class="dashboard-card-value" id="liquidCashValue">--</div>
                <div class="dashboard-card-subtitle">Available cash</div>
            </div>
            <div class="dashboard-card">
                <div class="dashboard-card-title">📉 Total Debt</div>
                <div class="dashboard-card-value" id="totalDebtValue">--</div>
                <div class="dashboard-card-subtitle">All debt balances</div>
            </div>
            <div class="dashboard-card">
                <div class="dashboard-card-title">📊 Net Worth</div>
                <div class="dashboard-card-value" id="netWorthValue">--</div>
                <div class="dashboard-card-subtitle">Cash - Debt</div>
            </div>
            <div class="dashboard-card">
                <div class="dashboard-card-title">🔄 Monthly Recurring</div>
                <div class="dashboard-card-value" id="monthlyRecurringValue">--</div>
                <div class="dashboard-card-subtitle">Fixed expenses</div>
            </div>
        </div>

        <!-- Budget vs Actual Section -->
        <div class="budget-section" id="budgetSection">
            <h2 class="category-header">🎯 Budget vs Actual (Current Month)</h2>
            <div id="budgetContainer">
                <!-- Budget items populated by JavaScript -->
            </div>
        </div>

        <!-- Goals Section -->
        <div class="charts-section" id="goalsSection">
            <h2 class="category-header">🎯 Financial Goals</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Emergency Fund Progress</div>
                    <canvas id="emergencyFundChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Credit Card Payoff Scenarios</div>
                    <canvas id="creditCardPayoffChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Financial Charts Section -->
        <div class="charts-section" id="chartsSection">
            <h2 class="category-header">📊 Spending Trends (6 Months)</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Amazon Spending</div>
                    <canvas id="amazonTrendChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Dining & Drinks</div>
                    <canvas id="diningTrendChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Groceries</div>
                    <canvas id="groceriesTrendChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Shopping</div>
                    <canvas id="shoppingTrendChart"></canvas>
                </div>
            </div>
        </div>

        <div id="categoriesContainer">
            <!-- Categories populated by JavaScript -->
        </div>
    </div>

    <!-- Panel Overlay -->
    <div class="panel-overlay" id="panelOverlay" onclick="closePanel()"></div>

    <!-- Sliding Panel -->
    <div class="sliding-panel" id="slidingPanel">
        <div class="panel-header">
            <div class="panel-title" id="panelTitle"></div>
            <button class="close-btn" onclick="closePanel()">✕ Close</button>
        </div>
        <div class="panel-content markdown-content" id="panelContent">
            <!-- Content rendered here -->
        </div>
    </div>

    <script>
        // EMBEDDED CONTENT
        ''' + embedded_js + dashboard_js + '''

        // DOCUMENTATION STRUCTURE
        const docsStructure = ''' + docs_json + ''';

        // Render categories and cards
        function renderDocuments() {
            const container = document.getElementById('categoriesContainer');
            let html = '';

            for (const [category, items] of Object.entries(docsStructure)) {
                const categoryInfo = getCategoryInfo(category);

                html += `
                    <div class="category-section">
                        <h2 class="category-header">${categoryInfo.icon} ${category}</h2>
                        <p class="category-description">${categoryInfo.description}</p>
                        <div class="docs-grid">
                `;

                items.forEach(item => {
                    const key = `${category}::${item.name}`;
                    const badge = item.badge ? `<span class="badge badge-${item.badge}">${item.badge.toUpperCase()}</span>` : '';

                    html += `
                        <div class="doc-card" onclick="openPanel('${key}')">
                            <div class="doc-header">
                                <div class="doc-icon">${item.icon}</div>
                                <div>
                                    <div class="doc-title">${item.name} ${badge}</div>
                                </div>
                            </div>
                            <div class="doc-category-badge">${category}</div>
                        </div>
                    `;
                });

                html += `
                        </div>
                    </div>
                `;
            }

            container.innerHTML = html;
        }

        function getCategoryInfo(category) {
            const categoryMap = {
                'Current Status & Planning': {
                    icon: '📊',
                    description: 'Current financial position, action plans, budget guidelines, and key dates'
                },
                'Analysis & Insights': {
                    icon: '📈',
                    description: 'Spending patterns, property analysis, scenario modeling, and financial trends'
                },
                'Reports & Reviews': {
                    icon: '📝',
                    description: 'Monthly reviews, financial health scores, and budget tracking'
                },
                'Tax Documents': {
                    icon: '📋',
                    description: 'W2s, 1099s, 1098s, and tax returns'
                },
                'Transaction Data': {
                    icon: '💳',
                    description: 'Transaction history and spending data'
                },
                'Property Documents': {
                    icon: '🏠',
                    description: 'Property-related documents and receipts'
                },
                'Budget Screenshots': {
                    icon: '📸',
                    description: 'Budget screenshots and financial snapshots'
                },
                'Other Financial Documents': {
                    icon: '📄',
                    description: 'Other financial documents and spreadsheets'
                }
            };

            return categoryMap[category] || { icon: '📄', description: 'Financial documents' };
        }

        function openPanel(key) {
            const doc = embeddedContent[key];
            if (!doc) {
                alert('Document content not found');
                return;
            }

            const title = key.split('::')[1];
            document.getElementById('panelTitle').textContent = title;

            renderContent('panelContent', doc);

            document.getElementById('panelOverlay').classList.add('visible');
            document.getElementById('slidingPanel').classList.add('visible');
            document.body.style.overflow = 'hidden';
        }

        function closePanel() {
            document.getElementById('panelOverlay').classList.remove('visible');
            document.getElementById('slidingPanel').classList.remove('visible');
            document.body.style.overflow = 'auto';
        }

        function renderContent(targetId, doc) {
            const target = document.getElementById(targetId);

            if (doc.type === 'markdown') {
                try {
                    const html = marked.parse(doc.content);
                    target.innerHTML = html;
                } catch (error) {
                    console.error('Markdown render error:', error);
                    target.innerHTML = `<p style="color: #D32F2F;">Error rendering markdown: ${error.message}</p>`;
                }
            } else if (doc.type === 'image') {
                target.innerHTML = `<img src="${doc.path}" alt="Image" style="max-width: 100%; border-radius: 10px;">`;
            } else {
                // PDF, CSV, XLSX - provide download link
                const fileType = doc.type.toUpperCase();
                target.innerHTML = `
                    <div style="text-align: center; padding: 50px;">
                        <p style="font-size: 3em; margin-bottom: 20px;">📄</p>
                        <h2 style="color: var(--primary-light); margin-bottom: 20px;">${fileType} Document</h2>
                        <p style="margin-bottom: 30px; color: var(--text-secondary);">
                            This is a ${fileType} file. Click below to open or download.
                        </p>
                        <a href="${doc.path}" class="file-link" download>
                            📥 Download ${fileType}
                        </a>
                        <br><br>
                        <a href="${doc.path}" class="file-link" target="_blank">
                            🔗 Open in New Tab
                        </a>
                    </div>
                `;
            }

            target.scrollTop = 0;
        }

        // Search functionality
        function performSearch(query) {
            const resultsDiv = document.getElementById('searchResults');

            if (!query || query.trim().length < 2) {
                resultsDiv.classList.remove('visible');
                resultsDiv.innerHTML = '';
                return;
            }

            const searchTerm = query.toLowerCase();
            const results = [];

            // Search through all embedded markdown content
            for (const [key, doc] of Object.entries(embeddedContent)) {
                if (doc.type === 'markdown' && doc.content) {
                    const content = doc.content.toLowerCase();
                    const title = key.split('::')[1];

                    if (title.toLowerCase().includes(searchTerm) || content.includes(searchTerm)) {
                        // Find context around the match
                        const index = content.indexOf(searchTerm);
                        const start = Math.max(0, index - 100);
                        const end = Math.min(content.length, index + 100);
                        const context = doc.content.substring(start, end);

                        results.push({
                            key: key,
                            title: title,
                            context: context,
                            category: key.split('::')[0]
                        });
                    }
                }
            }

            if (results.length > 0) {
                let html = `<h3 style="color: var(--primary-light); margin-bottom: 10px;">Found ${results.length} result${results.length > 1 ? 's' : ''}</h3>`;

                results.slice(0, 10).forEach(result => {
                    html += `
                        <div style="padding: 10px; margin: 10px 0; background: rgba(0,0,0,0.3); border-radius: 8px; cursor: pointer;"
                             onclick="openPanel('${result.key}'); document.getElementById('searchBox').value = '';">
                            <div style="color: var(--primary-light); font-weight: bold; margin-bottom: 5px;">
                                ${result.title}
                            </div>
                            <div style="font-size: 0.85em; color: var(--text-secondary);">
                                ${result.category}
                            </div>
                        </div>
                    `;
                });

                if (results.length > 10) {
                    html += `<div style="text-align: center; padding: 10px; color: var(--text-secondary);">
                        ... and ${results.length - 10} more results
                    </div>`;
                }

                resultsDiv.innerHTML = html;
                resultsDiv.classList.add('visible');
            } else {
                resultsDiv.innerHTML = '<p style="color: var(--text-secondary); padding: 10px;">No results found</p>';
                resultsDiv.classList.add('visible');
            }
        }

        // Load and render dashboard data (uses embedded data)
        function loadDashboardData() {
            try {
                if (typeof EMBEDDED_DASHBOARD_DATA !== 'undefined' && EMBEDDED_DASHBOARD_DATA) {
                    renderDashboard(EMBEDDED_DASHBOARD_DATA);
                } else {
                    console.warn('⚠️  Dashboard data not embedded, showing placeholder');
                    showPlaceholderDashboard();
                }
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                showPlaceholderDashboard();
            }
        }

        function renderDashboard(data) {
            renderAlerts(data.alerts);
            renderSnapshotCards(data.snapshot);
            renderBudgetProgress(data.budget_vs_actual);
            renderGoalCharts(data.emergency_fund, data.credit_card_payoff);
            initCharts(data.trends);
        }

        function showPlaceholderDashboard() {
            document.getElementById('liquidCashValue').textContent = 'No Data';
            document.getElementById('totalDebtValue').textContent = 'No Data';
            document.getElementById('netWorthValue').textContent = 'No Data';
            document.getElementById('monthlyRecurringValue').textContent = 'No Data';
            document.getElementById('budgetContainer').innerHTML = '<p style="color: var(--text-secondary);">Run build_all.py to generate dashboard data</p>';
            document.getElementById('chartsSection').style.display = 'none';
        }

        function renderAlerts(alerts) {
            const container = document.getElementById('alertsContainer');

            if (!alerts || alerts.length === 0) {
                container.style.display = 'none';
                return;
            }

            let html = '<div class="alerts-banner"><h2 class="category-header">⚠️  Financial Alerts</h2>';

            alerts.forEach(alert => {
                const icon = alert.type === 'critical' ? '🔴' : '⚠️';
                html += `
                    <div class="alert-item ${alert.type}">
                        <div class="alert-message">${icon} ${alert.message}</div>
                        <div class="alert-action">Action: ${alert.action}</div>
                    </div>
                `;
            });

            html += '</div>';
            container.innerHTML = html;
            container.style.display = 'block';
        }

        function renderSnapshotCards(snapshot) {
            document.getElementById('liquidCashValue').textContent =
                '$' + snapshot.liquid_cash.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            document.getElementById('totalDebtValue').textContent =
                '$' + snapshot.total_debt.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            const netWorthValue = document.getElementById('netWorthValue');
            const netWorth = snapshot.net_worth;
            netWorthValue.textContent =
                (netWorth < 0 ? '-$' : '$') + Math.abs(netWorth).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            netWorthValue.style.color = netWorth < 0 ? '#D32F2F' : '#00BCD4';

            document.getElementById('monthlyRecurringValue').textContent =
                '$' + snapshot.monthly_recurring.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }

        function renderBudgetProgress(budgetData) {
            const container = document.getElementById('budgetContainer');
            let html = '';

            // Sort by overage amount (over-budget items first)
            const categories = Object.entries(budgetData.categories).sort((a, b) => {
                if (a[1].over_budget && !b[1].over_budget) return -1;
                if (!a[1].over_budget && b[1].over_budget) return 1;
                return b[1].actual - a[1].actual;
            });

            categories.forEach(([category, data]) => {
                const percent = Math.min(data.percent, 100);
                const overBudget = data.over_budget ? 'over-budget' : '';
                const statusIcon = data.over_budget ? '🔴' : (percent > 80 ? '⚠️' : '✅');

                html += `
                    <div class="budget-item">
                        <div class="budget-header">
                            <div class="budget-category">${statusIcon} ${category}</div>
                            <div class="budget-amounts">
                                $${data.actual.toLocaleString()} / $${data.budget.toLocaleString()}
                                <span style="color: ${data.over_budget ? '#D32F2F' : '#00BCD4'}; margin-left: 10px;">
                                    ${data.percent.toFixed(0)}%
                                </span>
                            </div>
                        </div>
                        <div class="budget-progress-bar">
                            <div class="budget-progress-fill ${overBudget}" style="width: ${percent}%">
                                ${data.over_budget ? 'Over by $' + data.overage?.toLocaleString() || Math.abs(data.remaining).toLocaleString() : ''}
                            </div>
                        </div>
                    </div>
                `;
            });

            // Add summary
            html += `
                <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid var(--primary-color);">
                    <div class="budget-header">
                        <div class="budget-category" style="font-size: 1.2em;">Total Monthly Budget</div>
                        <div class="budget-amounts" style="font-size: 1.1em;">
                            $${budgetData.total_spent.toLocaleString()} / $${budgetData.total_budgeted.toLocaleString()}
                        </div>
                    </div>
                    <div style="margin-top: 10px; color: var(--text-secondary); text-align: center;">
                        Day ${budgetData.days_in_month} of month • ${budgetData.days_remaining} days remaining
                    </div>
                </div>
            `;

            container.innerHTML = html;
        }

        function renderGoalCharts(emergencyFund, creditCardPayoff) {
            if (typeof Chart === 'undefined') {
                console.warn('⚠️  Chart.js not loaded, skipping goal charts');
                document.getElementById('goalsSection').style.display = 'none';
                return;
            }

            renderEmergencyFundChart(emergencyFund);
            renderCreditCardPayoffChart(creditCardPayoff);
        }

        function renderEmergencyFundChart(data) {
            if (!data) return;

            const ctx = document.getElementById('emergencyFundChart');
            const current = data.current_balance;
            const target3mo = data.targets.three_months;
            const target6mo = data.targets.six_months;

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Current', '3-Month Gap', '6-Month Gap'],
                    datasets: [{
                        data: [
                            current,
                            Math.max(0, target3mo - current),
                            Math.max(0, target6mo - target3mo)
                        ],
                        backgroundColor: [
                            data.status === 'critical' ? '#D32F2F' :
                            data.status === 'fair' ? '#F57C00' :
                            data.status === 'good' ? '#00BCD4' : '#4CAF50',
                            'rgba(0, 188, 212, 0.3)',
                            'rgba(0, 188, 212, 0.1)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: true, position: 'bottom' },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label + ': $' + context.parsed.toLocaleString();
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: [
                                data.message,
                                `${data.days_covered} days covered (${data.months_covered.toFixed(1)} months)`,
                                `Goal: $${target6mo.toLocaleString()} (6 months)`
                            ],
                            color: '#00BCD4',
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            });
        }

        function renderCreditCardPayoffChart(data) {
            if (!data || !data.scenarios) return;

            const ctx = document.getElementById('creditCardPayoffChart');

            // Extract scenario data
            const scenarios = Object.entries(data.scenarios);
            const labels = scenarios.map(([label, _]) => label);
            const months = scenarios.map(([_, scenario]) => scenario.months || 0);
            const totalInterest = scenarios.map(([_, scenario]) => scenario.total_interest);

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Months to Payoff',
                        data: months,
                        backgroundColor: 'rgba(0, 188, 212, 0.7)',
                        borderColor: '#00BCD4',
                        borderWidth: 2,
                        yAxisID: 'y'
                    }, {
                        label: 'Total Interest Paid',
                        data: totalInterest,
                        backgroundColor: 'rgba(211, 47, 47, 0.7)',
                        borderColor: '#D32F2F',
                        borderWidth: 2,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: true, position: 'bottom' },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    if (context.datasetIndex === 0) {
                                        const years = (context.parsed.y / 12).toFixed(1);
                                        return `Payoff: ${context.parsed.y} months (${years} years)`;
                                    } else {
                                        return `Interest: $${context.parsed.y.toLocaleString()}`;
                                    }
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: [
                                `Current Balance: $${data.total_balance.toLocaleString()}`,
                                `Current Payment: $${data.current_payment}/mo`,
                                `Recommendation: $${data.recommendation.target_payment}/mo (${data.recommendation.method} method)`
                            ],
                            color: '#00BCD4',
                            font: {
                                size: 11
                            }
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Months',
                                color: '#00BCD4'
                            },
                            ticks: {
                                color: '#00BCD4'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Interest ($)',
                                color: '#D32F2F'
                            },
                            ticks: {
                                color: '#D32F2F',
                                callback: function(value) {
                                    return '$' + (value / 1000).toFixed(1) + 'k';
                                }
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    }
                }
            });
        }

        // Chart rendering functions
        function initCharts(trends) {
            if (typeof Chart === 'undefined') {
                console.warn('⚠️  Chart.js not loaded, skipping charts');
                document.getElementById('chartsSection').style.display = 'none';
                return;
            }

            Chart.defaults.color = '#B0BEC5';
            Chart.defaults.borderColor = 'rgba(0, 188, 212, 0.3)';

            renderTrendChart('amazonTrendChart', trends.trends['Amazon'] || null, 'Amazon Spending', '#FF9800');
            renderTrendChart('diningTrendChart', trends.trends['Dining & Drinks'] || null, 'Dining & Drinks', '#E91E63');
            renderTrendChart('groceriesTrendChart', trends.trends['Groceries'] || null, 'Groceries', '#4CAF50');
            renderTrendChart('shoppingTrendChart', trends.trends['Shopping'] || null, 'Shopping', '#2196F3');
        }

        function renderTrendChart(canvasId, trendData, label, color) {
            const ctx = document.getElementById(canvasId);

            if (!trendData || !trendData.months || trendData.months.length === 0) {
                ctx.parentElement.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 50px;">No data available</p>';
                return;
            }

            // Format month labels (YYYY-MM to MMM YYYY)
            const monthLabels = trendData.months.map(m => {
                const [year, month] = m.split('-');
                const date = new Date(year, month - 1);
                return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
            });

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: monthLabels,
                    datasets: [{
                        label: label,
                        data: trendData.amounts,
                        backgroundColor: color + '33',
                        borderColor: color,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                        pointBackgroundColor: color,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return label + ': $' + context.parsed.y.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: `6-Month Total: $${trendData.total.toLocaleString()} (Avg: $${trendData.average.toLocaleString()}/mo)`,
                            color: color,
                            font: {
                                size: 13
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            },
                            grid: {
                                color: 'rgba(0, 188, 212, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(0, 188, 212, 0.1)'
                            }
                        }
                    }
                }
            });
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('💰 Financial Hub loaded');
            console.log('📊 Categories:', Object.keys(docsStructure).length);
            console.log('📄 Documents:', Object.keys(embeddedContent).length);

            renderDocuments();
            loadDashboardData();

            if (typeof marked === 'undefined') {
                console.error('❌ marked.js failed to load');
            } else {
                console.log('✅ marked.js loaded');
            }

            if (typeof Chart !== 'undefined') {
                console.log('✅ Chart.js loaded');
            }
        });

        // Close panel on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && document.getElementById('slidingPanel').classList.contains('visible')) {
                closePanel();
            }
        });
    </script>
</body>
</html>
'''

    return html_template

def main():
    print("💰 Personal Financial Documentation Builder")
    print("=" * 70)
    print()

    # Build documentation structure
    print("📂 Scanning Archive directory...")
    docs_structure = build_docs_structure_from_archive()

    print(f"   ✅ Found {len(docs_structure)} categories:")
    for category, items in docs_structure.items():
        print(f"      - {category}: {len(items)} items")
    print()

    # Build embedded data
    print("📄 Loading document content...")
    embedded_data = build_embedded_data(docs_structure)
    print(f"   ✅ Loaded {len(embedded_data)} documents")
    print()

    # Generate HTML
    print("🌐 Generating financial_hub.html...")
    html_content = generate_html(embedded_data, docs_structure)

    output_file = BASE_DIR / 'financial_hub.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    file_size = output_file.stat().st_size / 1024  # KB
    print(f"   ✅ Generated: {output_file}")
    print(f"   📊 File size: {file_size:.1f} KB")
    print()

    # Summary
    print("=" * 70)
    print("🎉 Build Complete!")
    print()
    print("📦 Output:")
    print(f"   🌐 financial_hub.html ({file_size:.1f} KB)")
    print(f"   📄 {len(embedded_data)} documents embedded")
    print(f"   📊 {len(docs_structure)} categories")
    print()
    print("💡 To view:")
    print(f"   Open {output_file} in any web browser")
    print()
    print("📝 To update:")
    print("   1. Add/modify files in Archive/")
    print("   2. Run this script again")
    print()

if __name__ == '__main__':
    main()
