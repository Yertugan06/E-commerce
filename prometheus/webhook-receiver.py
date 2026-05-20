import http.server
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("alert-receiver")


class AlertReceiverHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            logger.error("Received non-JSON payload")
            self.send_response(400)
            self.end_headers()
            return

        status = payload.get("status", "unknown")
        alerts = payload.get("alerts", [])
        common_labels = payload.get("commonLabels", {})
        group_key = payload.get("groupKey", "")

        logger.info(
            "Alert group received: status=%s  alerts=%d  group_key=%s",
            status,
            len(alerts),
            group_key,
        )

        for alert in alerts:
            labels = alert.get("labels", {})
            annotations = alert.get("annotations", {})
            logger.warning(
                "  [%s/%s] %s — %s",
                labels.get("severity", "?"),
                alert.get("status", "?"),
                annotations.get("summary", labels.get("alertname", "?")),
                annotations.get("description", "(no description)"),
            )

        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        logger.debug(format, *args)


if __name__ == "__main__":
    port = 8080
    server = http.server.HTTPServer(("0.0.0.0", port), AlertReceiverHandler)
    logger.info("Starting alert-receiver on port %d", port)
    server.serve_forever()
