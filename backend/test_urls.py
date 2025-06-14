#!/usr/bin/env python
"""
Comprehensive URL Testing Script for Phantom Banking API

This script:
1. Loads Django settings and URL configuration
2. Enumerates all registered URLs using Django's URL resolver
3. Performs HTTP request simulations to test URL accessibility
4. Reports status codes and any errors
5. Provides detailed analysis of URL patterns
"""

import os
import sys
import django
from django.test import TestCase, override_settings
from django.test import Client
from django.urls import reverse, resolve, get_resolver
from django.urls.exceptions import NoReverseMatch, Resolver404
from django.core.management import execute_from_command_line
from urllib.parse import urljoin
import json
from collections import defaultdict

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings


class URLTester:
    def __init__(self):
        self.client = Client()
        self.results = {
            'successful': [],
            'failed': [],
            'authentication_required': [],
            'not_found': [],
            'method_not_allowed': [],
            'server_errors': []
        }
        self.url_patterns = []
        
    def get_all_url_patterns(self, urlconf=None):
        """Extract all URL patterns from Django's URL resolver"""
        if urlconf is None:
            urlconf = settings.ROOT_URLCONF
            
        resolver = get_resolver(urlconf)
        patterns = []
        
        def extract_patterns(url_patterns, prefix=''):
            for pattern in url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is an include() pattern
                    new_prefix = prefix + str(pattern.pattern)
                    extract_patterns(pattern.url_patterns, new_prefix)
                else:
                    # This is a regular URL pattern
                    full_pattern = prefix + str(pattern.pattern)
                    patterns.append({
                        'pattern': full_pattern,
                        'name': getattr(pattern, 'name', None),
                        'callback': str(pattern.callback) if hasattr(pattern, 'callback') else None,
                        'namespace': getattr(pattern, 'namespace', None)
                    })
        
        extract_patterns(resolver.url_patterns)
        return patterns
    
    def generate_test_urls(self):
        """Generate testable URLs from patterns"""
        test_urls = []
        
        # Static URLs that don't require parameters
        static_urls = [
            '/',
            '/health/',
            '/admin/',
            '/api/schema/',
            '/api/docs/',
            '/api/redoc/',
            '/api/v1/',
            '/api/v1/auth/',
            '/api/v1/merchants/',
            '/api/v1/customers/',
            '/api/v1/wallets/',
            '/api/v1/transactions/',
            '/api/v1/kyc/',
            '/api/v1/common/',
            '/api/v1/monitoring/',
            '/api/v1/mock-fnb/',
            '/api/v1/mock-mobile-money/',
            '/dev/kyc/',
            '/dev/merchants/',
            '/dev/customers/',
            '/dev/wallets/',
            '/dev/transactions/',
            '/dev/monitoring/',
            '/mock/fnb/',
            '/mock/mobile-money/',
        ]
        
        return static_urls
    
    def test_url(self, url, method='GET'):
        """Test a single URL and return results"""
        try:
            if method == 'GET':
                response = self.client.get(url)
            elif method == 'POST':
                response = self.client.post(url)
            elif method == 'PUT':
                response = self.client.put(url)
            elif method == 'DELETE':
                response = self.client.delete(url)
            else:
                response = self.client.get(url)
                
            return {
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'content_type': response.get('Content-Type', 'unknown'),
                'success': 200 <= response.status_code < 300
            }
        except Exception as e:
            return {
                'url': url,
                'method': method,
                'status_code': None,
                'error': str(e),
                'success': False
            }
    
    def categorize_result(self, result):
        """Categorize test results"""
        status_code = result.get('status_code')
        
        if result.get('success'):
            self.results['successful'].append(result)
        elif status_code == 401 or status_code == 403:
            self.results['authentication_required'].append(result)
        elif status_code == 404:
            self.results['not_found'].append(result)
        elif status_code == 405:
            self.results['method_not_allowed'].append(result)
        elif status_code and status_code >= 500:
            self.results['server_errors'].append(result)
        else:
            self.results['failed'].append(result)
    
    def run_tests(self):
        """Run all URL tests"""
        print("🔍 Phantom Banking API - URL Pattern Analysis")
        print("=" * 60)
        
        # Get all URL patterns
        print("\n📋 Extracting URL patterns...")
        self.url_patterns = self.get_all_url_patterns()
        print(f"Found {len(self.url_patterns)} URL patterns")
        
        # Generate test URLs
        test_urls = self.generate_test_urls()
        print(f"\n🧪 Testing {len(test_urls)} URLs...")
        
        # Test each URL
        for url in test_urls:
            print(f"Testing: {url}", end=" ")
            result = self.test_url(url)
            self.categorize_result(result)
            
            # Print immediate feedback
            if result.get('success'):
                print(f"✅ {result['status_code']}")
            else:
                status = result.get('status_code', 'ERROR')
                print(f"❌ {status}")
        
        # Print detailed results
        self.print_results()
    
    def print_results(self):
        """Print detailed test results"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = sum(len(results) for results in self.results.values())
        
        print(f"\n📈 Overview:")
        print(f"  Total URLs tested: {total_tests}")
        print(f"  ✅ Successful: {len(self.results['successful'])}")
        print(f"  🔒 Auth Required: {len(self.results['authentication_required'])}")
        print(f"  ❌ Not Found: {len(self.results['not_found'])}")
        print(f"  🚫 Method Not Allowed: {len(self.results['method_not_allowed'])}")
        print(f"  💥 Server Errors: {len(self.results['server_errors'])}")
        print(f"  ⚠️  Other Failures: {len(self.results['failed'])}")
        
        # Detailed breakdown
        for category, results in self.results.items():
            if results:
                print(f"\n{category.upper().replace('_', ' ')}:")
                for result in results:
                    status = result.get('status_code', 'ERROR')
                    error = result.get('error', '')
                    if error:
                        print(f"  {result['url']} - {status} ({error})")
                    else:
                        print(f"  {result['url']} - {status}")
        
        # URL Patterns Analysis
        print(f"\n\n🗺️  URL PATTERNS DISCOVERED:")
        print("-" * 40)
        
        pattern_groups = defaultdict(list)
        for pattern in self.url_patterns:
            # Group by app/module
            pattern_str = pattern['pattern']
            if 'api/v1' in pattern_str:
                group = 'API v1'
            elif 'admin' in pattern_str:
                group = 'Admin'
            elif 'mock' in pattern_str:
                group = 'Mock Systems'
            elif 'dev' in pattern_str:
                group = 'Development'
            else:
                group = 'Core'
                
            pattern_groups[group].append(pattern)
        
        for group, patterns in pattern_groups.items():
            print(f"\n{group} ({len(patterns)} patterns):")
            for pattern in patterns[:10]:  # Show first 10 to avoid clutter
                name = pattern['name'] or 'unnamed'
                print(f"  {pattern['pattern']} [{name}]")
            if len(patterns) > 10:
                print(f"  ... and {len(patterns) - 10} more")
        
        # Recommendations
        print(f"\n\n💡 RECOMMENDATIONS:")
        print("-" * 30)
        
        if self.results['not_found']:
            print("• Fix URLs returning 404 - they may have incorrect patterns")
        
        if self.results['server_errors']:
            print("• Investigate server errors - these indicate code issues")
            
        if self.results['method_not_allowed']:
            print("• Review HTTP methods - some endpoints may need additional methods")
            
        success_rate = len(self.results['successful']) / total_tests * 100 if total_tests > 0 else 0
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate < 50:
            print("⚠️  Low success rate - significant URL configuration issues detected")
        elif success_rate < 80:
            print("⚠️  Moderate success rate - some URL issues need attention")
        else:
            print("✅ Good success rate - URL configuration looks healthy")


def main():
    """Main execution function"""
    try:
        tester = URLTester()
        tester.run_tests()
    except Exception as e:
        print(f"❌ Error running URL tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

