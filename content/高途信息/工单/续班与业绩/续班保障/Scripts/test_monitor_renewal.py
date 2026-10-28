"""Regression checks for empty metrics, query failures, windows and login handling."""
import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import monitor_renewal as monitor


class MonitoringTest(unittest.TestCase):
    def test_empty_data_is_not_healthy(self):
        self.assertEqual(monitor.summarize({}, 0, 300000)["status"], "no_data")

    def test_zero_values_are_real_data_and_stale_points_are_excluded(self):
        data = {"results": {"A": {"frames": [{"schema": {"fields": [
            {"type": "time"}, {"type": "number", "name": "cpu"}]},
            "data": {"values": [[999, 1000, 2000, 2001], [80, 0, None, 99]]}}]}}}
        summary = monitor.summarize(data, 1000, 2000)
        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["series"][0]["points"], [[1000, 0]])
        self.assertEqual(summary["series"][0]["max"], 0)

    def test_stale_cloud_and_interface_data_is_not_healthy(self):
        data = {"Datapoints": json.dumps([{"timestamp": 999, "Average": 55}]),
                "data": [{"createTime": 0, "requestCount": 10}]}
        self.assertEqual(monitor.summarize(data, 1000, 2000)["status"], "no_data")

    def test_cloud_zero_is_preserved_without_account_id(self):
        data = {"Datapoints": json.dumps([{"timestamp": 1500, "Average": 0, "userId": "secret"}])}
        summary = monitor.summarize(data, 1000, 2000)
        self.assertEqual(summary["datapoints"], [{"timestamp": 1500, "Average": 0}])

    def test_grafana_query_error_is_not_empty_success(self):
        with self.assertRaises(monitor.MonitorError):
            monitor.decode_response('{"results":{"A":{"error":"timeout","status":500}}}')

    def test_login_page_and_login_code_stop_collection(self):
        for text in ('<!DOCTYPE html><html>login</html>', '{"code":700}'):
            with self.subTest(text=text), self.assertRaises(monitor.LoginExpired):
                monitor.decode_response(text)

    def test_node_query_uses_exact_five_minute_window(self):
        client = object.__new__(monitor.Belong)
        target = {"datasource": {"type": "aliyun-log-service-datasource"}, "refId": "node"}
        with patch.object(client, "api", return_value={}) as api:
            client.query([target], 1000000, 1300000)
        body = api.call_args.args[1]
        self.assertEqual(body["from"], "1000000")
        self.assertEqual(body["to"], "1300000")
        self.assertEqual(body["queries"][0]["datasourceId"], 385)

    def test_interface_time_macros_are_substituted(self):
        client = object.__new__(monitor.Belong)
        target = {"datasource": {"type": "marcusolsson-json-datasource"},
                  "body": '{"timeFrom":$__unixEpochFrom(),"timeTo":$__unixEpochTo()}'}
        with patch.object(client, "api", return_value={}) as api:
            client.query([target], 1000000, 1300000)
        self.assertEqual(api.call_args.args[1], {"timeFrom": 1000, "timeTo": 1300})

    def test_mq_uses_prometheus_ready_metric_and_explicit_prod_region(self):
        run = type("Result", (), {"stdout": '{"ok":true,"groups":[{"group_id":"g","backlog":0}]}',
                                  "stderr": "", "returncode": 0})()
        with patch.object(monitor.subprocess, "run", return_value=run) as call:
            result = monitor.collect_mq("instance", 30, Path("mcpcli.py"))
        self.assertEqual(result["status"], "ok")
        argv = call.call_args.args[0]
        self.assertEqual(argv[2], "ons_group_backlog_top")
        self.assertEqual(json.loads(argv[3])["region"], "cn-beijing")
        self.assertEqual(json.loads(argv[3])["metric"], "ready")

    def test_mq_empty_data_is_not_zero_backlog(self):
        run = type("Result", (), {"stdout": '{"ok":true,"groups":[]}', "stderr": "", "returncode": 0})()
        with patch.object(monitor.subprocess, "run", return_value=run):
            self.assertEqual(monitor.collect_mq("instance", 30, Path("mcpcli.py"))["status"], "no_data")

    def test_mq_login_failure_is_not_retried(self):
        run = type("Result", (), {"stdout": '{"ok":false,"error":"LOGIN_EXPIRED"}',
                                  "stderr": "", "returncode": 1})()
        with patch.object(monitor.subprocess, "run", return_value=run) as call:
            with self.assertRaises(monitor.LoginExpired):
                monitor.collect_mq("instance", 30, Path("mcpcli.py"))
        self.assertEqual(call.call_count, 1)

    def test_no_requests_does_not_claim_zero_latency(self):
        report = {"sampled_at": "now", "status": "ok", "mq": [], "tabs": {"支付": [
            {"status": "ok", "api_metrics": [{"requestCount": 0, "errorCount": 0, "p99": 999}]}]}}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            monitor.print_summary(report, Path("snapshot.json"))
        self.assertIn("最大接口P99=无请求", output.getvalue())


if __name__ == "__main__":
    unittest.main()
