#!/usr/bin/env python
"""
Django URL Validation Script for Phantom Banking API

This script validates URL patterns and checks for common issues.
"""

import os
import sys
import django
from collections import defaultdict

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.urls import get_resolver
from django.core.management import call_command
from django.core.checks import run_checks
from django.urls.exceptions import NoReverseMatch


def extract_url_patterns():
    """Extract all URL patterns from Django's URL resolver"""
    resolver = get_resolver(settings.ROOT_URLCONF)
    patterns = []
    
    def extract_patterns(url_patterns, prefix=''):
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an include() pattern
                new_prefix = prefix + str(pattern.pattern)
                try:
                    extract_patterns(pattern.url_patterns, new_prefix)
                except Exception as e:
                    patterns.append({
                        'pattern': new_prefix,
                        'name': None,
                        'error': f"Failed to load: {e}",
                        'type': 'include_error'
                    })
            else:
                # This is a regular URL pattern
                full_pattern = prefix + str(pattern.pattern)
                patterns.append({
                    'pattern': full_pattern,
                    'name': getattr(pattern, 'name', None),
                    'callback': str(pattern.callback) if hasattr(pattern, 'callback') else None,
                    'namespace': getattr(pattern, 'namespace', None),
                    'type': 'url'
                })
    
    try:
        extract_patterns(resolver.url_patterns)
    except Exception as e:
        print(f"❌ Error extracting URL patterns: {e}")
        return []
    
    return patterns


def analyze_url_patterns(patterns):
    """Analyze URL patterns for potential issues"""
    analysis = {
        'total_patterns': len(patterns),
        'named_patterns': 0,
        'unnamed_patterns': 0,
        'duplicate_names': [],
        'errors': [],
        'groups': defaultdict(list)
    }
    
    name_count = defaultdict(int)
    
    for pattern in patterns:
        if pattern.get('error'):
            analysis['errors'].append(pattern)
            continue
            
        # Count named vs unnamed
        if pattern.get('name'):
            analysis['named_patterns'] += 1
            name_count[pattern['name']] += 1
        else:
            analysis['unnamed_patterns'] += 1
        
        # Group patterns
        pattern_str = pattern['pattern']
        if 'api/v1' in pattern_str:
            group = 'API v1'
        elif 'admin' in pattern_str:
            group = 'Admin'
        elif 'mock' in pattern_str:
            group = 'Mock Systems'
        elif 'dev' in pattern_str:
            group = 'Development'
        elif '__debug__' in pattern_str:
            group = 'Debug Toolbar'
        else:
            group = 'Core'
            
        analysis['groups'][group].append(pattern)
    
    # Find duplicate names
    analysis['duplicate_names'] = [name for name, count in name_count.items() if count > 1]
    
    return analysis


def check_url_structure():
    """Check URL structure for common issues"""
    issues = []
    
    # Check for common URL pattern issues
    patterns = extract_url_patterns()
    
    # Check for missing trailing slashes in API endpoints
    api_patterns = [p for p in patterns if 'api/' in p['pattern']]
    for pattern in api_patterns:
        pattern_str = pattern['pattern']
        if not pattern_str.endswith('/') and not pattern_str.endswith('$'):
            issues.append(f"⚠️  API pattern may need trailing slash: {pattern_str}")
    
    # Check for inconsistent naming
    named_patterns = [p for p in patterns if p.get('name')]
    for pattern in named_patterns:
        name = pattern['name']
        if '-' in name and '_' in name:
            issues.append(f"⚠️  Inconsistent naming (mixed hyphens/underscores): {name}")
    
    return issues


def main():
    """Main execution function"""
    print("🔍 Phantom Banking API - URL Configuration Validation")
    print("=" * 65)
    
    # Run Django's built-in checks
    print("\n🔧 Running Django system checks...")
    try:
        call_command('check', verbosity=1)
        print("✅ Django system checks passed")
    except Exception as e:
        print(f"❌ Django system checks failed: {e}")
    
    # Extract and analyze URL patterns
    print("\n📋 Extracting URL patterns...")
    patterns = extract_url_patterns()
    
    if not patterns:
        print("❌ No URL patterns found or extraction failed")
        return 1
    
    print(f"Found {len(patterns)} URL patterns")
    
    # Analyze patterns
    analysis = analyze_url_patterns(patterns)
    
    print("\n📊 URL PATTERN ANALYSIS")
    print("=" * 40)
    
    print(f"\n📈 Statistics:")
    print(f"  Total patterns: {analysis['total_patterns']}")
    print(f"  Named patterns: {analysis['named_patterns']}")
    print(f"  Unnamed patterns: {analysis['unnamed_patterns']}")
    print(f"  Errors/Issues: {len(analysis['errors'])}")
    
    if analysis['duplicate_names']:
        print(f"\n⚠️  Duplicate URL names found:")
        for name in analysis['duplicate_names']:
            print(f"    - {name}")
    
    if analysis['errors']:
        print(f"\n❌ Pattern Loading Errors:")
        for error in analysis['errors']:
            print(f"    - {error['pattern']}: {error['error']}")
    
    # Group breakdown
    print(f"\n🗺️  URL PATTERNS BY GROUP:")
    print("-" * 35)
    
    for group, group_patterns in analysis['groups'].items():
        print(f"\n{group} ({len(group_patterns)} patterns):")
        for pattern in group_patterns[:8]:  # Show first 8 to avoid clutter
            name = pattern.get('name', 'unnamed')
            print(f"  {pattern['pattern']} [{name}]")
        if len(group_patterns) > 8:
            print(f"  ... and {len(group_patterns) - 8} more")
    
    # Check for structural issues
    print("\n🔍 Checking URL structure...")
    issues = check_url_structure()
    
    if issues:
        print("\n⚠️  POTENTIAL ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No obvious structural issues found")
    
    # Test a few key endpoints
    print("\n🧪 Testing key URL patterns...")
    key_urls = [
        ('', 'api_info'),
        ('health/', 'health_check'),
        ('admin/', None),
        ('api/schema/', 'schema'),
    ]
    
    for url_pattern, expected_name in key_urls:
        try:
            from django.urls import reverse
            if expected_name:
                resolved_url = reverse(expected_name)
                print(f"  ✅ {expected_name}: {resolved_url}")
            else:
                print(f"  ℹ️  {url_pattern}: (no name to reverse)")
        except NoReverseMatch as e:
            print(f"  ❌ {expected_name or url_pattern}: Failed to reverse - {e}")
        except Exception as e:
            print(f"  ⚠️  {expected_name or url_pattern}: Error - {e}")
    
    # Summary
    error_count = len(analysis['errors']) + len(issues)
    print(f"\n🎯 SUMMARY:")
    print(f"  URL patterns loaded: {analysis['total_patterns']}")
    print(f"  Issues found: {error_count}")
    
    if error_count == 0:
        print("  ✅ URL configuration looks healthy!")
        return 0
    elif error_count < 5:
        print("  ⚠️  Minor issues found - review recommended")
        return 0
    else:
        print("  ❌ Significant issues found - attention required")
        return 1


if __name__ == '__main__':
    sys.exit(main())

