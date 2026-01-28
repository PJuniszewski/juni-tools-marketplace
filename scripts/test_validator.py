#!/usr/bin/env python3
"""
Unit tests for validate-plugins.py security scanning and tier policy functions.

Run with: python -m pytest scripts/test_validator.py -v
Or:       python scripts/test_validator.py
"""
import sys
import unittest
from pathlib import Path

# Import from validator
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module

# Import the validator module
validator = import_module("validate-plugins")

scan_file_for_secrets = validator.scan_file_for_secrets
scan_file_for_network = validator.scan_file_for_network
scan_file_for_telemetry = validator.scan_file_for_telemetry
validate_plugin_manifest_schema = validator.validate_plugin_manifest_schema
validate_tier_policy = validator.validate_tier_policy
check_consistency = validator.check_consistency


class TestSecretsDetection(unittest.TestCase):
    """Test secret/credential detection patterns."""

    def test_aws_access_key(self):
        content = 'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect AWS access key")
        self.assertTrue(any("AWS" in f[1] for f in findings))

    def test_github_pat(self):
        content = 'token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect GitHub PAT")
        self.assertTrue(any("GitHub" in f[1] for f in findings))

    def test_api_key_assignment(self):
        content = 'api_key = "sk-1234567890abcdefghijklmnop"'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect API key")

    def test_password_assignment(self):
        content = 'password = "supersecretpassword123"'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect password")

    def test_private_key(self):
        content = '-----BEGIN RSA PRIVATE KEY-----\nMIIE...'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect private key")

    def test_bearer_token(self):
        content = 'headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect bearer token")

    def test_slack_token(self):
        content = 'SLACK_TOKEN = "xoxb-fake-fake-fake"'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect Slack token")

    def test_no_false_positive_on_placeholder(self):
        content = 'api_key = os.environ.get("API_KEY")'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertEqual(len(findings), 0, "Should not flag env var lookup")

    def test_no_false_positive_on_comment(self):
        content = '# api_key = "sk-1234567890abcdefghijklmnop"'
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertEqual(len(findings), 0, "Should skip comments")

    def test_clean_file(self):
        content = '''
def hello():
    print("Hello, world!")
    name = "Alice"
    count = 42
'''
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertEqual(len(findings), 0, "Clean file should have no findings")


class TestNetworkDetection(unittest.TestCase):
    """Test network/telemetry detection patterns."""

    def test_requests_import(self):
        content = 'import requests'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect requests import")

    def test_requests_from_import(self):
        content = 'from requests import get, post'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect requests from import")

    def test_requests_call(self):
        content = 'response = requests.get("https://api.example.com")'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect requests.get call")

    def test_urllib_import(self):
        content = 'import urllib.request'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect urllib import")

    def test_aiohttp_import(self):
        content = 'import aiohttp'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect aiohttp import")

    def test_httpx_import(self):
        content = 'import httpx'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect httpx import")

    def test_fetch_call_js(self):
        content = 'const response = await fetch("https://api.example.com");'
        findings = scan_file_for_network(Path("test.js"), content)
        self.assertTrue(len(findings) > 0, "Should detect fetch() call")

    def test_axios_call(self):
        content = 'axios.post("/api/data", payload)'
        findings = scan_file_for_network(Path("test.js"), content)
        self.assertTrue(len(findings) > 0, "Should detect axios call")

    def test_xmlhttprequest(self):
        content = 'const xhr = new XMLHttpRequest();'
        findings = scan_file_for_network(Path("test.js"), content)
        self.assertTrue(len(findings) > 0, "Should detect XMLHttpRequest")

    def test_websocket(self):
        content = 'const ws = new WebSocket("wss://example.com");'
        findings = scan_file_for_network(Path("test.js"), content)
        self.assertTrue(len(findings) > 0, "Should detect WebSocket")

    def test_analytics_url(self):
        content = 'url = "https://analytics.example.com/track"'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect analytics URL")

    def test_telemetry_url(self):
        content = 'ENDPOINT = "https://telemetry.service.com/v1/events"'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect telemetry URL")

    def test_no_false_positive_on_comment(self):
        content = '# import requests'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertEqual(len(findings), 0, "Should skip comments")

    def test_clean_file(self):
        content = '''
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
'''
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertEqual(len(findings), 0, "Clean file should have no findings")

    # New tests for shell commands
    def test_curl_command(self):
        content = 'curl -X POST https://api.example.com/data'
        findings = scan_file_for_network(Path("test.sh"), content)
        self.assertTrue(len(findings) > 0, "Should detect curl command")

    def test_wget_command(self):
        content = 'wget https://example.com/file.txt'
        findings = scan_file_for_network(Path("test.sh"), content)
        self.assertTrue(len(findings) > 0, "Should detect wget command")

    def test_netcat_command(self):
        content = 'nc -l 8080'
        findings = scan_file_for_network(Path("test.sh"), content)
        self.assertTrue(len(findings) > 0, "Should detect netcat command")

    def test_socket_import(self):
        content = 'import socket'
        findings = scan_file_for_network(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect socket import")


class TestTelemetryDetection(unittest.TestCase):
    """Test telemetry-specific detection (always blocked)."""

    def test_posthog_url(self):
        content = 'url = "https://app.posthog.com/capture"'
        findings = scan_file_for_telemetry(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect PostHog URL")

    def test_sentry_url(self):
        content = 'dsn = "https://abc@sentry.io/123"'
        findings = scan_file_for_telemetry(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect Sentry URL")

    def test_segment_url(self):
        content = 'endpoint = "https://api.segment.io/v1/track"'
        findings = scan_file_for_telemetry(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect Segment URL")

    def test_posthog_capture_call(self):
        content = 'posthog.capture("event_name", properties)'
        findings = scan_file_for_telemetry(Path("test.py"), content)
        self.assertTrue(len(findings) > 0, "Should detect PostHog capture call")

    def test_analytics_track_call(self):
        content = 'analytics.track("page_view")'
        findings = scan_file_for_telemetry(Path("test.js"), content)
        self.assertTrue(len(findings) > 0, "Should detect analytics.track call")

    def test_sentry_init(self):
        content = 'Sentry.init({ dsn: "..." })'
        findings = scan_file_for_telemetry(Path("test.js"), content)
        self.assertTrue(len(findings) > 0, "Should detect Sentry.init")


class TestManifestSchemaValidation(unittest.TestCase):
    """Test plugin manifest schema validation."""

    def test_valid_curated_manifest(self):
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "A test plugin for validation",
            "policyTier": "curated",
            "capabilities": {
                "network": {"mode": "none"}
            }
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "curated")
        self.assertEqual(len(errors), 0, f"Valid manifest should pass: {errors}")

    def test_valid_community_manifest(self):
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "A test plugin for validation",
            "policyTier": "community",
            "capabilities": {
                "network": {
                    "mode": "allowlist",
                    "domains": ["api.github.com"]
                }
            },
            "risk": {
                "dataEgress": "medium"
            }
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "community")
        self.assertEqual(len(errors), 0, f"Valid manifest should pass: {errors}")

    def test_legacy_manifest_warns(self):
        """Legacy manifests without policyTier/capabilities should warn, not error."""
        manifest = {
            "name": "legacy-plugin",
            "version": "1.0.0",
            "description": "A legacy plugin"
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "curated")
        self.assertEqual(len(errors), 0, "Legacy manifest should not error")
        self.assertTrue(len(warnings) > 0, "Legacy manifest should warn")
        self.assertTrue(any("legacy" in w.lower() for w in warnings))

    def test_invalid_name_format(self):
        manifest = {
            "name": "Test_Plugin",  # Invalid: uppercase and underscore
            "version": "1.0.0",
            "description": "Test plugin",
            "policyTier": "curated",
            "capabilities": {"network": {"mode": "none"}}
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "curated")
        self.assertTrue(any("lowercase with hyphens" in w for w in warnings))

    def test_invalid_version_format(self):
        manifest = {
            "name": "test-plugin",
            "version": "v1.0",  # Invalid semver
            "description": "Test plugin",
            "policyTier": "curated",
            "capabilities": {"network": {"mode": "none"}}
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "curated")
        self.assertTrue(any("semver" in w for w in warnings))

    def test_tier_mismatch(self):
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "policyTier": "community",  # Mismatch with tier="curated"
            "capabilities": {"network": {"mode": "none"}}
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "curated")
        self.assertTrue(any("does not match" in e for e in errors))

    def test_wildcard_domain_rejected(self):
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "policyTier": "community",
            "capabilities": {
                "network": {
                    "mode": "allowlist",
                    "domains": ["*.example.com"]  # Wildcards not allowed
                }
            },
            "risk": {"dataEgress": "low"}
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "community")
        self.assertTrue(any("wildcard" in e.lower() for e in errors))

    def test_ip_address_domain_rejected(self):
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "policyTier": "community",
            "capabilities": {
                "network": {
                    "mode": "allowlist",
                    "domains": ["192.168.1.1"]  # IPs not allowed
                }
            },
            "risk": {"dataEgress": "low"}
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "community")
        self.assertTrue(any("IP address" in e for e in errors))

    def test_community_requires_risk(self):
        manifest = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "policyTier": "community",
            "capabilities": {
                "network": {"mode": "none"}
            }
            # Missing risk field
        }
        errors, warnings = validate_plugin_manifest_schema(manifest, "community")
        self.assertTrue(any("risk required" in e for e in errors))


class TestTierPolicyValidation(unittest.TestCase):
    """Test tier-specific policy enforcement."""

    def test_curated_must_have_no_network(self):
        manifest = {
            "capabilities": {
                "network": {"mode": "allowlist", "domains": ["api.example.com"]}
            }
        }
        errors = validate_tier_policy(manifest, "curated")
        self.assertTrue(len(errors) > 0, "Curated with network should fail")
        self.assertTrue(any("curated plugins must have" in e for e in errors))

    def test_curated_cannot_have_high_risk(self):
        manifest = {
            "capabilities": {"network": {"mode": "none"}},
            "risk": {"dataEgress": "high"}
        }
        errors = validate_tier_policy(manifest, "curated")
        self.assertTrue(any("medium/high risk" in e for e in errors))

    def test_community_allows_network_with_allowlist(self):
        manifest = {
            "capabilities": {
                "network": {
                    "mode": "allowlist",
                    "domains": ["api.github.com"]
                }
            }
        }
        errors = validate_tier_policy(manifest, "community")
        self.assertEqual(len(errors), 0, "Community with allowlist should pass")

    def test_community_requires_domains_for_allowlist(self):
        manifest = {
            "capabilities": {
                "network": {"mode": "allowlist"}  # Missing domains
            }
        }
        errors = validate_tier_policy(manifest, "community")
        self.assertTrue(any("declare explicit domains" in e for e in errors))


class TestConsistencyChecks(unittest.TestCase):
    """Test consistency between declared and detected capabilities."""

    def test_network_detected_but_declared_none(self):
        manifest = {
            "capabilities": {
                "network": {"mode": "none"}
            }
        }
        errors = check_consistency("curated", manifest, network_detected=True, detected_domains=set())
        self.assertTrue(len(errors) > 0, "Should detect inconsistency")
        self.assertTrue(any("CONSISTENCY" in e for e in errors))

    def test_undeclared_domains_detected(self):
        manifest = {
            "capabilities": {
                "network": {
                    "mode": "allowlist",
                    "domains": ["api.github.com"]
                }
            }
        }
        detected = {"api.github.com", "unknown.example.com"}
        errors = check_consistency("community", manifest, network_detected=True, detected_domains=detected)
        self.assertTrue(len(errors) > 0, "Should detect undeclared domain")
        self.assertTrue(any("unknown.example.com" in e for e in errors))

    def test_no_error_when_consistent(self):
        manifest = {
            "capabilities": {
                "network": {"mode": "none"}
            }
        }
        errors = check_consistency("curated", manifest, network_detected=False, detected_domains=set())
        self.assertEqual(len(errors), 0, "Consistent manifest should pass")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and combined scenarios."""

    def test_multiple_issues_same_file(self):
        content = '''
import requests
api_key = "sk-abcdefghijklmnopqrstuvwxyz"
response = requests.post("https://analytics.example.com", data={"key": api_key})
'''
        secret_findings = scan_file_for_secrets(Path("test.py"), content)
        network_findings = scan_file_for_network(Path("test.py"), content)

        self.assertTrue(len(secret_findings) > 0, "Should detect API key")
        self.assertTrue(len(network_findings) > 0, "Should detect network calls")

    def test_line_numbers_correct(self):
        content = '''line1
line2
api_key = "sk-abcdefghijklmnopqrstuvwxyz"
line4'''
        findings = scan_file_for_secrets(Path("test.py"), content)
        self.assertTrue(len(findings) > 0)
        self.assertEqual(findings[0][0], 3, "Should report correct line number")

    def test_empty_file(self):
        content = ''
        secret_findings = scan_file_for_secrets(Path("test.py"), content)
        network_findings = scan_file_for_network(Path("test.py"), content)
        self.assertEqual(len(secret_findings), 0)
        self.assertEqual(len(network_findings), 0)


def run_tests():
    """Run all tests and print summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSecretsDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestTelemetryDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestManifestSchemaValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestTierPolicyValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestConsistencyChecks))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    total = result.testsRun
    if result.wasSuccessful():
        print(f"✅ All {total} tests passed!")
        return 0
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors out of {total} tests")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
