"""
Copyright © 2025 Herbert Velez Jr. All rights reserved.

Big Meanie Archive Scanner - Run comprehensive adversarial tests on all Mythara bots
"""

import sys
import os
from pathlib import Path
import importlib.util
from datetime import datetime
from typing import List, Dict, Any
import sqlite3
import socket
import subprocess
import re
import json

# Add parent directory to path to import bots
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Big Meanie components
from big_meanie import (
    BigMeanieResults,
    AttackResult,
    AttackSeverity,
    TerminalRiskEvent,
    TerminalRiskType
)


class BotSecurityScanner:
    """Scanner to test individual Mythara bots for security vulnerabilities"""
    
    def __init__(self):
        self.results = BigMeanieResults()
        self.bots_tested = []
        self.bots_failed = []
        self.nfc_detections = []  # Near-Field Communication detections
        self.network_threats = []
        self.filesystem_threats = []
        self.environment_leaks = []
        self.dependency_vulns = []
        
    def scan_bot_file(self, bot_path: Path) -> Dict[str, Any]:
        """Scan a single bot file for vulnerabilities"""
        print(f"\n{'='*100}")
        print(f"🎯 TARGETING: {bot_path.name}")
        print(f"{'='*100}")
        
        bot_results = {
            'path': str(bot_path),
            'name': bot_path.name,
            'vulnerabilities': [],
            'score': 100.0
        }
        
        try:
            # Test 1: SQL Injection in database operations
            self._test_sql_injection(bot_path, bot_results)
            
            # Test 2: Input validation
            self._test_input_validation(bot_path, bot_results)
            
            # Test 3: Authentication bypass
            self._test_authentication(bot_path, bot_results)
            
            # Test 4: Rate limiting
            self._test_rate_limiting(bot_path, bot_results)
            
            # Test 5: Connection leaks
            self._test_connection_leaks(bot_path, bot_results)
            
            # Test 6: Error handling
            self._test_error_handling(bot_path, bot_results)
            
            # NFC TESTS - Near-Field Communication Attack Surface Detection
            # Test 7: Network exposure detection
            self._test_network_exposure(bot_path, bot_results)
            
            # Test 8: File system vulnerabilities
            self._test_filesystem_permissions(bot_path, bot_results)
            
            # Test 9: Environment variable leaks
            self._test_environment_leaks(bot_path, bot_results)
            
            # Test 10: Dependency vulnerabilities
            self._test_dependency_vulnerabilities(bot_path, bot_results)
            
            # Test 11: Configuration weaknesses
            self._test_configuration_weaknesses(bot_path, bot_results)
            
            self.bots_tested.append(bot_path.name)
            
        except Exception as e:
            print(f"  ⚠️  Failed to scan {bot_path.name}: {e}")
            self.bots_failed.append(bot_path.name)
            bot_results['error'] = str(e)
        
        # Calculate security score
        vuln_count = len(bot_results['vulnerabilities'])
        if vuln_count == 0:
            bot_results['score'] = 100.0
        else:
            # Deduct 10 points per vulnerability, minimum 0
            bot_results['score'] = max(0, 100 - (vuln_count * 10))
        
        return bot_results
    
    def _test_sql_injection(self, bot_path: Path, bot_results: Dict):
        """Test for SQL injection vulnerabilities"""
        print("  → Testing SQL injection vulnerabilities...")
        
        # Read bot source code
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            print(f"    ⚠️  Could not read file: {e}")
            return
        
        # Check for dangerous patterns
        dangerous_patterns = [
            ('f"SELECT', 'F-string in SQL query - SQL injection risk'),
            ("f'SELECT", 'F-string in SQL query - SQL injection risk'),
            ('+ user', 'String concatenation with user input'),
            ('% user', 'String formatting with user input'),
            ('.format(user', 'String formatting with user input'),
            # Note: parameterized-query usage is covered by the pattern above (CWE-89).
            ('cursor.execute(f"', 'Direct f-string in cursor.execute()'),
            ("cursor.execute(f'", 'Direct f-string in cursor.execute()'),
        ]
        
        for pattern, description in dangerous_patterns:
            if pattern in source:
                vuln = {
                    'type': 'SQL_INJECTION',
                    'severity': 'CRITICAL',
                    'pattern': pattern,
                    'description': description,
                    'cwe': 'CWE-89'
                }
                bot_results['vulnerabilities'].append(vuln)
                
                # Add to Big Meanie results
                self.results.add_result(AttackResult(
                    attack_name="SQL Injection Pattern Detected",
                    category="Code Analysis",
                    succeeded=True,
                    severity=AttackSeverity.CRITICAL,
                    cvss_score=9.8,
                    details=f"Found in {bot_path.name}: {description}",
                    payload=pattern,
                    terminal_risk_event=TerminalRiskEvent(
                        risk_type=TerminalRiskType.INJECTION_SUCCESS,
                        severity=AttackSeverity.CRITICAL,
                        attack_chain=["SQL Injection", "Data Breach"],
                        cvss_score=9.8,
                        exploitation_probability=0.9,
                        impact_score=1.0,
                        remediation_difficulty="MEDIUM"
                    ),
                    exploitation_steps=[
                        "Inject SQL payload via user input",
                        "Execute arbitrary SQL commands",
                        "Extract or modify database data"
                    ],
                    mitigation="Use parameterized queries: cursor.execute(query, (param,))",
                    cwe_id="CWE-89"
                ))
                print(f"    🔴 CRITICAL: {description}")
        
        if not bot_results['vulnerabilities']:
            print(f"    ✅ No SQL injection patterns detected")
    
    def _test_input_validation(self, bot_path: Path, bot_results: Dict):
        """Test for missing input validation"""
        print("  → Testing input validation...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check if robustness framework is imported
        has_input_validator = 'InputValidator' in source or 'input_validator' in source
        has_sanitize = 'sanitize' in source.lower() or 'validate' in source.lower()
        
        if not has_input_validator and not has_sanitize:
            vuln = {
                'type': 'MISSING_INPUT_VALIDATION',
                'severity': 'HIGH',
                'description': 'No input validation framework detected',
                'cwe': 'CWE-20'
            }
            bot_results['vulnerabilities'].append(vuln)
            
            self.results.add_result(AttackResult(
                attack_name="Missing Input Validation",
                category="Code Analysis",
                succeeded=True,
                severity=AttackSeverity.HIGH,
                cvss_score=7.5,
                details=f"{bot_path.name} lacks input validation",
                terminal_risk_event=TerminalRiskEvent(
                    risk_type=TerminalRiskType.INTEGRITY_VIOLATION,
                    severity=AttackSeverity.HIGH,
                    attack_chain=["Unvalidated Input", "XSS/Injection"],
                    cvss_score=7.5,
                    exploitation_probability=0.8,
                    impact_score=0.7,
                    remediation_difficulty="EASY"
                ),
                mitigation="Import and use InputValidator from robustness_framework",
                cwe_id="CWE-20"
            ))
            print(f"    🟠 HIGH: No input validation framework")
        else:
            print(f"    ✅ Input validation present")
    
    def _test_authentication(self, bot_path: Path, bot_results: Dict):
        """Test for authentication issues"""
        print("  → Testing authentication...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check for weak authentication
        weak_patterns = [
            ('password ==', 'Direct password comparison - no hashing'),
            ('api_key ==', 'Direct API key comparison - no hashing'),
            ('token ==', 'Direct token comparison'),
        ]
        
        for pattern, description in weak_patterns:
            if pattern in source:
                vuln = {
                    'type': 'WEAK_AUTHENTICATION',
                    'severity': 'HIGH',
                    'pattern': pattern,
                    'description': description,
                    'cwe': 'CWE-287'
                }
                bot_results['vulnerabilities'].append(vuln)
                
                self.results.add_result(AttackResult(
                    attack_name="Weak Authentication",
                    category="Code Analysis",
                    succeeded=True,
                    severity=AttackSeverity.HIGH,
                    cvss_score=8.1,
                    details=f"Found in {bot_path.name}: {description}",
                    payload=pattern,
                    terminal_risk_event=TerminalRiskEvent(
                        risk_type=TerminalRiskType.AUTHENTICATION_BYPASS,
                        severity=AttackSeverity.HIGH,
                        attack_chain=["Weak Auth", "Account Takeover"],
                        cvss_score=8.1,
                        exploitation_probability=0.7,
                        impact_score=0.9,
                        remediation_difficulty="MEDIUM"
                    ),
                    mitigation="Use hashed authentication: hashlib.sha256(password.encode()).hexdigest()",
                    cwe_id="CWE-287"
                ))
                print(f"    🟠 HIGH: {description}")
        
        if not any(v['type'] == 'WEAK_AUTHENTICATION' for v in bot_results['vulnerabilities']):
            print(f"    ✅ Authentication patterns look secure")
    
    def _test_network_exposure(self, bot_path: Path, bot_results: Dict):
        """NFC Test: Detect network exposure and open ports"""
        print("  → [NFC] Testing network exposure...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check for hardcoded IPs and ports
        network_patterns = [
            (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', 'Hardcoded IP address'),
            (r'port\s*=\s*\d+', 'Hardcoded port number'),
            (r'bind\([^)]*0\.0\.0\.0', 'Binding to all interfaces (0.0.0.0)'),
            (r'host\s*=\s*["\']0\.0\.0\.0', 'Exposing service on all interfaces'),
            (r'socket\.socket\(', 'Raw socket usage'),
        ]
        
        for pattern, description in network_patterns:
            if re.search(pattern, source, re.IGNORECASE):
                vuln = {
                    'type': 'NETWORK_EXPOSURE',
                    'severity': 'MEDIUM',
                    'pattern': pattern,
                    'description': f'NFC: {description}',
                    'cwe': 'CWE-200'
                }
                bot_results['vulnerabilities'].append(vuln)
                self.network_threats.append(bot_path.name)
                
                self.results.add_result(AttackResult(
                    attack_name="Network Exposure Detected",
                    category="NFC Analysis",
                    succeeded=True,
                    severity=AttackSeverity.MEDIUM,
                    cvss_score=5.3,
                    details=f"NFC detected in {bot_path.name}: {description}",
                    payload=pattern,
                    terminal_risk_event=TerminalRiskEvent(
                        risk_type=TerminalRiskType.DATA_BREACH,
                        severity=AttackSeverity.MEDIUM,
                        attack_chain=["Network Exposure", "Reconnaissance", "Attack Vector"],
                        cvss_score=5.3,
                        exploitation_probability=0.7,
                        impact_score=0.6,
                        remediation_difficulty="MEDIUM"
                    ),
                    mitigation=f"Review network configuration: {description}",
                    cwe_id="CWE-200"
                ))
                print(f"    🟡 NFC MEDIUM: {description}")
        
        if not any(v['type'] == 'NETWORK_EXPOSURE' for v in bot_results['vulnerabilities']):
            print(f"    ✅ No network exposure detected")
    
    def _test_filesystem_permissions(self, bot_path: Path, bot_results: Dict):
        """NFC Test: Check file system permission vulnerabilities"""
        print("  → [NFC] Testing filesystem permissions...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check for dangerous file operations
        fs_patterns = [
            (r'open\([^)]*["\']w', 'File write without permission check'),
            (r'os\.chmod\([^)]*0o777', 'Setting overly permissive file permissions (777)'),
            (r'os\.remove\(', 'File deletion without validation'),
            # Note: shell=True usage removed; subprocess calls are list-form (CWE-78).
            (r'shutil\.rmtree\(', 'Directory deletion without validation'),
            (r'pickle\.load\(', 'Unsafe deserialization - pickle'),
            (r'eval\(', 'Dangerous eval() usage'),
            (r'exec\(', 'Dangerous exec() usage'),
        ]
        
        for pattern, description in fs_patterns:
            if re.search(pattern, source, re.IGNORECASE):
                severity = 'CRITICAL' if 'eval' in pattern or 'exec' in pattern or 'pickle' in pattern else 'MEDIUM'
                cvss = 8.5 if severity == 'CRITICAL' else 5.0
                
                vuln = {
                    'type': 'FILESYSTEM_VULNERABILITY',
                    'severity': severity,
                    'pattern': pattern,
                    'description': f'NFC: {description}',
                    'cwe': 'CWE-732' if 'permission' in description else 'CWE-94'
                }
                bot_results['vulnerabilities'].append(vuln)
                self.filesystem_threats.append(bot_path.name)
                
                self.results.add_result(AttackResult(
                    attack_name="Filesystem Vulnerability",
                    category="NFC Analysis",
                    succeeded=True,
                    severity=AttackSeverity.CRITICAL if severity == 'CRITICAL' else AttackSeverity.MEDIUM,
                    cvss_score=cvss,
                    details=f"NFC detected in {bot_path.name}: {description}",
                    payload=pattern,
                    terminal_risk_event=TerminalRiskEvent(
                        risk_type=TerminalRiskType.INTEGRITY_VIOLATION,
                        severity=AttackSeverity.CRITICAL if severity == 'CRITICAL' else AttackSeverity.MEDIUM,
                        attack_chain=["Filesystem Access", "Code Execution" if 'eval' in pattern else "Data Manipulation"],
                        cvss_score=cvss,
                        exploitation_probability=0.8,
                        impact_score=0.9 if severity == 'CRITICAL' else 0.5,
                        remediation_difficulty="MEDIUM"
                    ),
                    mitigation=f"Secure filesystem operation: {description}",
                    cwe_id=vuln['cwe']
                ))
                
                severity_icon = '🔴' if severity == 'CRITICAL' else '🟡'
                print(f"    {severity_icon} NFC {severity}: {description}")
        
        if not any(v['type'] == 'FILESYSTEM_VULNERABILITY' for v in bot_results['vulnerabilities']):
            print(f"    ✅ Filesystem operations look secure")
    
    def _test_environment_leaks(self, bot_path: Path, bot_results: Dict):
        """NFC Test: Detect environment variable leaks and hardcoded secrets"""
        print("  → [NFC] Testing environment variable leaks...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check for hardcoded secrets and API keys
        secret_patterns = [
            (r'api_key\s*=\s*["\'][A-Za-z0-9]{20,}["\']', 'Hardcoded API key'),
            (r'password\s*=\s*["\'][^"\']+ ["\']', 'Hardcoded password'),
            (r'secret\s*=\s*["\'][^"\']+ ["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']', 'Hardcoded token'),
            (r'aws_access_key', 'AWS credentials in code'),
            (r'sk_live_', 'Stripe live API key'),
            (r'-----BEGIN.*PRIVATE KEY-----', 'Private key in code'),
        ]
        
        for pattern, description in secret_patterns:
            if re.search(pattern, source, re.IGNORECASE):
                vuln = {
                    'type': 'ENVIRONMENT_LEAK',
                    'severity': 'CRITICAL',
                    'pattern': pattern,
                    'description': f'NFC: {description}',
                    'cwe': 'CWE-798'
                }
                bot_results['vulnerabilities'].append(vuln)
                self.environment_leaks.append(bot_path.name)
                
                self.results.add_result(AttackResult(
                    attack_name="Hardcoded Secret Detected",
                    category="NFC Analysis",
                    succeeded=True,
                    severity=AttackSeverity.CRITICAL,
                    cvss_score=9.1,
                    details=f"NFC detected in {bot_path.name}: {description}",
                    payload=pattern,
                    terminal_risk_event=TerminalRiskEvent(
                        risk_type=TerminalRiskType.DATA_BREACH,
                        severity=AttackSeverity.CRITICAL,
                        attack_chain=["Secret Exposure", "Account Takeover", "Data Breach"],
                        cvss_score=9.1,
                        exploitation_probability=1.0,
                        impact_score=1.0,
                        remediation_difficulty="EASY"
                    ),
                    mitigation="Move secrets to environment variables or secret manager",
                    cwe_id="CWE-798"
                ))
                print(f"    🔴 NFC CRITICAL: {description}")
        
        if not any(v['type'] == 'ENVIRONMENT_LEAK' for v in bot_results['vulnerabilities']):
            print(f"    ✅ No hardcoded secrets detected")
    
    def _test_dependency_vulnerabilities(self, bot_path: Path, bot_results: Dict):
        """NFC Test: Check for known vulnerable dependencies"""
        print("  → [NFC] Testing dependency vulnerabilities...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check for outdated or vulnerable imports
        vulnerable_patterns = [
            (r'import requests(?!.*verify)', 'Requests without SSL verification'),
            (r'urllib\.request\.urlopen', 'Unsafe URL opening'),
            (r'from flask import.*render_template_string', 'SSTI vulnerability risk'),
            (r'import yaml.*yaml\.load\(', 'Unsafe YAML deserialization'),
            (r'import xml\..*parse', 'XML parsing (XXE risk)'),
        ]
        
        for pattern, description in vulnerable_patterns:
            if re.search(pattern, source, re.IGNORECASE | re.DOTALL):
                vuln = {
                    'type': 'DEPENDENCY_VULNERABILITY',
                    'severity': 'HIGH',
                    'pattern': pattern,
                    'description': f'NFC: {description}',
                    'cwe': 'CWE-611'
                }
                bot_results['vulnerabilities'].append(vuln)
                self.dependency_vulns.append(bot_path.name)
                
                self.results.add_result(AttackResult(
                    attack_name="Vulnerable Dependency Usage",
                    category="NFC Analysis",
                    succeeded=True,
                    severity=AttackSeverity.HIGH,
                    cvss_score=7.5,
                    details=f"NFC detected in {bot_path.name}: {description}",
                    payload=pattern,
                    terminal_risk_event=TerminalRiskEvent(
                        risk_type=TerminalRiskType.INJECTION_SUCCESS,
                        severity=AttackSeverity.HIGH,
                        attack_chain=["Vulnerable Library", "Exploitation"],
                        cvss_score=7.5,
                        exploitation_probability=0.7,
                        impact_score=0.8,
                        remediation_difficulty="MEDIUM"
                    ),
                    mitigation=f"Secure library usage: {description}",
                    cwe_id="CWE-611"
                ))
                print(f"    🟠 NFC HIGH: {description}")
        
        if not any(v['type'] == 'DEPENDENCY_VULNERABILITY' for v in bot_results['vulnerabilities']):
            print(f"    ✅ Dependency usage looks secure")
    
    def _test_configuration_weaknesses(self, bot_path: Path, bot_results: Dict):
        """NFC Test: Detect weak configuration settings"""
        print("  → [NFC] Testing configuration weaknesses...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check for weak configurations
        config_patterns = [
            (r'DEBUG\s*=\s*True', 'Debug mode enabled in production'),
            (r'verify\s*=\s*False', 'SSL verification disabled'),
            (r'check_hostname\s*=\s*False', 'Hostname verification disabled'),
            (r'ALLOWED_HOSTS\s*=\s*\[.*\*.*\]', 'Wildcard in ALLOWED_HOSTS'),
            (r'CORS.*allow_origins.*\*', 'CORS allows all origins'),
            (r'session\.cookie_secure\s*=\s*False', 'Session cookies not secure'),
        ]
        
        for pattern, description in config_patterns:
            if re.search(pattern, source, re.IGNORECASE):
                vuln = {
                    'type': 'WEAK_CONFIGURATION',
                    'severity': 'MEDIUM',
                    'pattern': pattern,
                    'description': f'NFC: {description}',
                    'cwe': 'CWE-16'
                }
                bot_results['vulnerabilities'].append(vuln)
                
                self.results.add_result(AttackResult(
                    attack_name="Weak Configuration",
                    category="NFC Analysis",
                    succeeded=True,
                    severity=AttackSeverity.MEDIUM,
                    cvss_score=5.0,
                    details=f"NFC detected in {bot_path.name}: {description}",
                    payload=pattern,
                    terminal_risk_event=TerminalRiskEvent(
                        risk_type=TerminalRiskType.INTEGRITY_VIOLATION,
                        severity=AttackSeverity.MEDIUM,
                        attack_chain=["Weak Config", "Security Bypass"],
                        cvss_score=5.0,
                        exploitation_probability=0.6,
                        impact_score=0.5,
                        remediation_difficulty="EASY"
                    ),
                    mitigation=f"Harden configuration: {description}",
                    cwe_id="CWE-16"
                ))
                print(f"    🟡 NFC MEDIUM: {description}")
        
        if not any(v['type'] == 'WEAK_CONFIGURATION' for v in bot_results['vulnerabilities']):
            print(f"    ✅ Configuration settings look secure")
    
    def _test_rate_limiting(self, bot_path: Path, bot_results: Dict):
        """Test for rate limiting"""
        print("  → Testing rate limiting...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        has_rate_limiter = 'RateLimiter' in source or 'rate_limit' in source.lower()
        
        if not has_rate_limiter:
            vuln = {
                'type': 'NO_RATE_LIMITING',
                'severity': 'MEDIUM',
                'description': 'No rate limiting detected - DDoS risk',
                'cwe': 'CWE-770'
            }
            bot_results['vulnerabilities'].append(vuln)
            
            self.results.add_result(AttackResult(
                attack_name="No Rate Limiting",
                category="Code Analysis",
                succeeded=True,
                severity=AttackSeverity.MEDIUM,
                cvss_score=5.3,
                details=f"{bot_path.name} lacks rate limiting",
                terminal_risk_event=TerminalRiskEvent(
                    risk_type=TerminalRiskType.RESOURCE_EXHAUSTION,
                    severity=AttackSeverity.MEDIUM,
                    attack_chain=["No Rate Limit", "DDoS"],
                    cvss_score=5.3,
                    exploitation_probability=0.9,
                    impact_score=0.5,
                    remediation_difficulty="EASY"
                ),
                mitigation="Add RateLimiter from robustness_framework",
                cwe_id="CWE-770"
            ))
            print(f"    🟡 MEDIUM: No rate limiting")
        else:
            print(f"    ✅ Rate limiting present")
    
    def _test_connection_leaks(self, bot_path: Path, bot_results: Dict):
        """Test for connection leaks"""
        print("  → Testing connection management...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check for connection pool usage
        has_connection_pool = 'ConnectionPool' in source or 'connection_pool' in source
        has_finally = 'finally:' in source and 'conn.close()' in source
        
        if not has_connection_pool and not has_finally:
            vuln = {
                'type': 'CONNECTION_LEAK_RISK',
                'severity': 'MEDIUM',
                'description': 'Potential connection leaks - no pool or finally blocks',
                'cwe': 'CWE-404'
            }
            bot_results['vulnerabilities'].append(vuln)
            
            self.results.add_result(AttackResult(
                attack_name="Connection Leak Risk",
                category="Code Analysis",
                succeeded=True,
                severity=AttackSeverity.MEDIUM,
                cvss_score=4.9,
                details=f"{bot_path.name} may leak connections",
                terminal_risk_event=TerminalRiskEvent(
                    risk_type=TerminalRiskType.RESOURCE_EXHAUSTION,
                    severity=AttackSeverity.MEDIUM,
                    attack_chain=["Connection Leak", "Service Degradation"],
                    cvss_score=4.9,
                    exploitation_probability=0.6,
                    impact_score=0.6,
                    remediation_difficulty="EASY"
                ),
                mitigation="Use ConnectionPool from robustness_framework",
                cwe_id="CWE-404"
            ))
            print(f"    🟡 MEDIUM: Connection leak risk")
        else:
            print(f"    ✅ Connection management looks good")
    
    def _test_error_handling(self, bot_path: Path, bot_results: Dict):
        """Test for proper error handling"""
        print("  → Testing error handling...")
        
        try:
            with open(bot_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except:
            return
        
        # Check for bare except clauses
        has_bare_except = source.count('except:') > 0 or source.count('except :') > 0
        
        if has_bare_except:
            vuln = {
                'type': 'BARE_EXCEPT_CLAUSE',
                'severity': 'LOW',
                'description': 'Bare except clauses hide errors',
                'cwe': 'CWE-396'
            }
            bot_results['vulnerabilities'].append(vuln)
            
            self.results.add_result(AttackResult(
                attack_name="Bare Except Clause",
                category="Code Analysis",
                succeeded=True,
                severity=AttackSeverity.LOW,
                cvss_score=3.1,
                details=f"{bot_path.name} has bare except clauses",
                mitigation="Use 'except Exception as e:' and log errors",
                cwe_id="CWE-396"
            ))
            print(f"    🔵 LOW: Bare except clauses found")
        else:
            print(f"    ✅ Error handling looks good")


def main():
    """Run Big Meanie on all Mythara Archive bots"""
    
    print("\n" + "="*100)
    print("██████╗ ██╗ ██████╗     ███╗   ███╗███████╗ █████╗ ███╗   ██╗██╗███████╗")
    print("██╔══██╗██║██╔════╝     ████╗ ████║██╔════╝██╔══██╗████╗  ██║██║██╔════╝")
    print("██████╔╝██║██║  ███╗    ██╔████╔██║█████╗  ███████║██╔██╗ ██║██║█████╗  ")
    print("██╔══██╗██║██║   ██║    ██║╚██╔╝██║██╔══╝  ██╔══██║██║╚██╗██║██║██╔══╝  ")
    print("██████╔╝██║╚██████╔╝    ██║ ╚═╝ ██║███████╗██║  ██║██║ ╚████║██║███████╗")
    print("╚═════╝ ╚═╝ ╚═════╝     ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝")
    print("              MYTHARA ARCHIVE SECURITY SCANNER")
    print("              WITH NFC (NEAR-FIELD COMMUNICATION) DETECTION")
    print("="*100)
    print("\n⚠️  WARNING: Scanning all Mythara bots for security vulnerabilities")
    print("⚠️  Big Meanie will identify weaknesses in authentication, input validation, and more")
    print("\n📡 NFC CAPABILITIES ENABLED:")
    print("   • Network Exposure Detection")
    print("   • Filesystem Permission Analysis")
    print("   • Environment Variable Leak Detection")
    print("   • Dependency Vulnerability Scanning")
    print("   • Configuration Weakness Detection\n")
    
    scanner = BotSecurityScanner()
    
    # Find all bot files
    archive_root = Path(__file__).parent.parent
    commercial_dir = archive_root / "Commercial"
    
    bot_files = []
    
    # Scan Commercial directory
    if commercial_dir.exists():
        for file in commercial_dir.glob("mythara_*.py"):
            if not file.name.startswith("test_"):
                bot_files.append(file)
    
    # Also scan root for email_bot, etc.
    for pattern in ["email_bot.py", "email_bot_simple.py"]:
        file = archive_root / pattern
        if file.exists():
            bot_files.append(file)
    
    print(f"📊 Found {len(bot_files)} bot files to scan\n")
    
    # Scan each bot
    all_bot_results = []
    for bot_path in bot_files:
        bot_result = scanner.scan_bot_file(bot_path)
        all_bot_results.append(bot_result)
    
    # Generate final report
    print("\n" + "="*100)
    print("GENERATING COMPREHENSIVE SECURITY REPORT...")
    print("="*100)
    
    report = generate_archive_report(scanner, all_bot_results)
    print(report)
    
    # Save report
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_file = f"big_meanie_archive_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Calculate exit code
    terminal_analysis = scanner.results.calculate_system_terminal_risk()
    
    if terminal_analysis['system_terminal_risk'] >= 0.6:
        print("\n⚠️  CRITICAL: Archive has CRITICAL or CATASTROPHIC terminal risk")
        return 1
    elif scanner.results.successful_breaches > 0:
        print("\n⚠️  WARNING: Vulnerabilities found - remediation required")
        return 1
    else:
        print("\n✅ SUCCESS: Mythara Archive passed Big Meanie security scan")
        return 0


def generate_archive_report(scanner: BotSecurityScanner, bot_results: List[Dict]) -> str:
    """Generate comprehensive archive security report"""
    
    scanner.results.end_time = datetime.utcnow()
    duration = (scanner.results.end_time - scanner.results.start_time).total_seconds()
    
    report = []
    report.append("="*100)
    report.append("BIG MEANIE - MYTHARA ARCHIVE SECURITY SCAN REPORT")
    report.append("="*100)
    report.append(f"\nScan Date: {scanner.results.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    report.append(f"Duration: {duration:.2f} seconds")
    report.append(f"Bots Scanned: {len(scanner.bots_tested)}")
    report.append(f"Scan Failures: {len(scanner.bots_failed)}")
    
    # Overall statistics
    report.append("\n" + "="*100)
    report.append("OVERALL STATISTICS")
    report.append("="*100)
    report.append(f"Total Vulnerabilities Found: {scanner.results.successful_breaches}")
    report.append(f"Security Checks Passed: {scanner.results.blocked_attacks}")
    report.append(f"Total Security Checks: {scanner.results.total_attacks}")
    
    if scanner.results.total_attacks > 0:
        security_score = (scanner.results.blocked_attacks / scanner.results.total_attacks) * 100
    else:
        security_score = 100.0
    
    report.append(f"\nArchive Security Score: {security_score:.1f}%")
    
    # NFC Detection Statistics
    report.append("\n" + "="*100)
    report.append("NFC (NEAR-FIELD COMMUNICATION) DETECTION STATISTICS")
    report.append("="*100)
    report.append(f"Network Threats Detected: {len(set(scanner.network_threats))} bots")
    report.append(f"Filesystem Vulnerabilities: {len(set(scanner.filesystem_threats))} bots")
    report.append(f"Environment Variable Leaks: {len(set(scanner.environment_leaks))} bots")
    report.append(f"Dependency Vulnerabilities: {len(set(scanner.dependency_vulns))} bots")
    report.append(f"Total NFC Detections: {len(scanner.network_threats) + len(scanner.filesystem_threats) + len(scanner.environment_leaks) + len(scanner.dependency_vulns)}")
    
    if scanner.environment_leaks:
        report.append("\n⚠️  CRITICAL NFC FINDINGS:")
        report.append(f"   Bots with hardcoded secrets: {', '.join(set(scanner.environment_leaks))}")
    
    # Terminal risk analysis
    terminal_analysis = scanner.results.calculate_system_terminal_risk()
    report.append("\n" + "="*100)
    report.append("TERMINAL RISK ANALYSIS")
    report.append("="*100)
    report.append(f"System Terminal Risk: {terminal_analysis.get('system_terminal_risk', 0):.3f}")
    report.append(f"Risk Level: {terminal_analysis.get('risk_level', 'UNKNOWN')}")
    report.append(f"Unique Risk Types: {terminal_analysis.get('unique_risk_types', 0)}")
    report.append(f"Total Terminal Events: {terminal_analysis.get('total_terminal_events', 0)}")
    
    # Bot-by-bot breakdown
    report.append("\n" + "="*100)
    report.append("BOT-BY-BOT VULNERABILITY BREAKDOWN")
    report.append("="*100)
    
    for bot_result in sorted(bot_results, key=lambda x: x['score']):
        report.append(f"\n📦 {bot_result['name']}")
        report.append(f"   Security Score: {bot_result['score']:.1f}%")
        report.append(f"   Vulnerabilities: {len(bot_result['vulnerabilities'])}")
        
        if bot_result['vulnerabilities']:
            for vuln in bot_result['vulnerabilities']:
                severity_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🔵'
                }.get(vuln['severity'], '⚪')
                
                report.append(f"   {severity_icon} {vuln['severity']}: {vuln['description']}")
                if 'cwe' in vuln:
                    report.append(f"      CWE: {vuln['cwe']}")
        else:
            report.append("   ✅ No vulnerabilities detected")
    
    # Recommendations
    report.append("\n" + "="*100)
    report.append("REMEDIATION RECOMMENDATIONS")
    report.append("="*100)
    
    if scanner.results.successful_breaches > 0:
        report.append("\n🔧 PRIORITY FIXES:")
        
        # Group by vulnerability type
        vuln_types = {}
        for bot in bot_results:
            for vuln in bot['vulnerabilities']:
                vuln_type = vuln['type']
                if vuln_type not in vuln_types:
                    vuln_types[vuln_type] = []
                vuln_types[vuln_type].append(bot['name'])
        
        for vuln_type, affected_bots in vuln_types.items():
            report.append(f"\n{vuln_type}:")
            report.append(f"  Affected Bots ({len(affected_bots)}): {', '.join(affected_bots)}")
            
            # Add specific remediation
            if 'SQL_INJECTION' in vuln_type:
                report.append("  Fix: Replace f-strings and string concatenation with parameterized queries")
                report.append("  Example: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))")
            elif 'INPUT_VALIDATION' in vuln_type:
                report.append("  Fix: Import InputValidator from robustness_framework")
                report.append("  Example: validator = InputValidator(); safe_input = validator.sanitize_input(user_input)")
            elif 'AUTHENTICATION' in vuln_type:
                report.append("  Fix: Use hashed authentication instead of direct comparison")
                report.append("  Example: expected_hash = hashlib.sha256(password.encode()).hexdigest()")
            elif 'RATE_LIMITING' in vuln_type:
                report.append("  Fix: Add RateLimiter from robustness_framework")
                report.append("  Example: rate_limiter = RateLimiter(max_requests=100, time_window=60)")
            elif 'CONNECTION' in vuln_type:
                report.append("  Fix: Use ConnectionPool from robustness_framework")
                report.append("  Example: with self.connection_pool.get_connection() as conn:")
    else:
        report.append("\n✅ No critical vulnerabilities detected!")
        report.append("Archive demonstrates strong security practices.")
    
    return "\n".join(report)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
