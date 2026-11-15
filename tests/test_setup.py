import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

from run import Handler, ThreadingHTTPServer
from trip_planner.catalog import Catalog
from trip_planner.claude import ClaudePlanner, ModelError
from trip_planner.config import load_settings
from trip_planner.models import TripRequest


class LocalSettingsTests(unittest.TestCase):
    def test_file_loads_but_shell_settings_win(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('PLANNER_PROVIDER=claude\nANTHROPIC_API_KEY="test-placeholder"\n', encoding='utf-8-sig')
            env = {'PLANNER_PROVIDER': 'local'}
            load_settings(path, env)
            self.assertEqual(env, {'PLANNER_PROVIDER': 'local', 'ANTHROPIC_API_KEY': 'test-placeholder'})

    def test_only_allowed_settings_are_loaded_without_expansion(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('PATH=wrong\nIGNORE ME\n# comment\nANTHROPIC_API_KEY=$(command)\n', encoding='utf-8')
            env = {}
            load_settings(path, env)
            self.assertEqual(env, {'ANTHROPIC_API_KEY': '$(command)'})

    def test_missing_file_keeps_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {'PLANNER_PROVIDER': 'local'}
            load_settings(Path(directory) / 'missing', env)
            self.assertEqual(env, {'PLANNER_PROVIDER': 'local'})


class ClaudeResponseTests(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-placeholder'}):
            self.engine = ClaudePlanner()
        self.request = TripRequest.parse({'date': '2026-11-18'})

    def reply(self, value):
        mock = patch('urllib.request.urlopen')
        self.addCleanup(mock.stop)
        call = mock.start()
        call.return_value.__enter__.return_value.read.return_value = json.dumps(value).encode()

    def test_non_object_api_response_fails_cleanly(self):
        self.reply([])
        with self.assertRaises(ModelError):
            self.engine.generate(self.request, {})

    def test_token_limit_is_not_reported_as_a_complete_plan(self):
        self.reply({'content': [], 'stop_reason': 'max_tokens'})
        with self.assertRaisesRegex(ModelError, 'output limit'):
            self.engine.generate(self.request, {})

    def test_auth_error_does_not_expose_server_response(self):
        error = urllib.error.HTTPError('https://api.anthropic.com/v1/messages', 401,
            'private upstream detail', {}, io.BytesIO(b'private body'))
        with patch('urllib.request.urlopen', side_effect=error):
            with self.assertRaisesRegex(ModelError, 'rejected the API key') as caught:
                self.engine.generate(self.request, {})
        self.assertNotIn('private', str(caught.exception))

    def test_usage_and_resolved_model_are_recorded(self):
        self.reply({'model': 'resolved-test-model', 'stop_reason': 'end_turn',
            'usage': {'input_tokens': 123, 'output_tokens': 45},
            'content': [{'type': 'text', 'text': '{"stops":[]}'}]})
        self.assertEqual(self.engine.generate(self.request, {}), [])
        self.assertEqual(self.engine.calls[0]['model'], 'resolved-test-model')
        self.assertEqual(self.engine.usage[0]['input_tokens'], 123)
        self.assertGreaterEqual(self.engine.calls[0]['elapsed_seconds'], 0)


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class QuietHandler(Handler):
            def log_message(self, *args):
                pass
        QuietHandler.catalog = Catalog()
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_config_exposes_presence_but_not_the_key(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'private-test-value'}):
            with urllib.request.urlopen(self.base + '/api/config') as response:
                raw = response.read().decode()
        self.assertTrue(json.loads(raw)['claude_key_configured'])
        self.assertNotIn('private-test-value', raw)
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(self.base + '/.env')
        self.assertEqual(caught.exception.code, 404)

    def test_real_http_local_plan_repairs_saturday(self):
        request = urllib.request.Request(self.base + '/api/plan',
            data=json.dumps({'date': '2026-11-14', 'budget': 20}).encode(),
            headers={'Content-Type': 'application/json'}, method='POST')
        with patch.dict(os.environ, {'PLANNER_PROVIDER': 'local'}):
            with urllib.request.urlopen(request) as response:
                result = json.load(response)
        self.assertEqual(result['provider'], 'local')
        self.assertEqual(result['result']['status'], 'fits_estimates')
        self.assertEqual(len(result['attempts']), 2)

    def test_other_websites_cannot_submit_requests(self):
        request = urllib.request.Request(self.base + '/api/plan', data=b'{}',
            headers={'Content-Type': 'application/json', 'Origin': 'https://example.org'}, method='POST')
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request)
        self.assertEqual(caught.exception.code, 403)

    def test_invalid_json_is_a_bad_request(self):
        request = urllib.request.Request(self.base + '/api/plan', data=b'{bad',
            headers={'Content-Type': 'application/json'}, method='POST')
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request)
        self.assertEqual(caught.exception.code, 400)


if __name__ == '__main__':
    unittest.main()
