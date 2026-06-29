# src/reports/report_generator.py

import os
import csv
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from src.database.db import DatabaseManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CSV_PATH = str(PROJECT_ROOT / "outputs" / "reports" / "traffic_report.csv")
DEFAULT_PDF_PATH = str(PROJECT_ROOT / "outputs" / "reports" / "traffic_report.pdf")


class ReportGenerator:
    def __init__(self):
        self.db = DatabaseManager()
        os.makedirs(str(PROJECT_ROOT / "outputs" / "reports"), exist_ok=True)

    def generate_csv_report(self, filename=DEFAULT_CSV_PATH):
        traffic_logs = self.db.fetch_traffic_logs()
        violations = self.db.fetch_violations()
        alerts = self.db.fetch_alerts()

        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow(["SMARTCITYAI TRAFFIC REPORT"])
            writer.writerow([])

            writer.writerow(["TRAFFIC LOGS"])
            writer.writerow(["ID", "Timestamp", "Frame No", "Vehicle Count", "Car Count", "Bike Count", "Bus Count", "Truck Count", "Avg Speed", "Congestion"])
            for row in traffic_logs:
                writer.writerow(row)

            writer.writerow([])
            writer.writerow(["VIOLATIONS"])
            writer.writerow(["ID", "Timestamp", "Frame No", "Vehicle ID", "Violation Type", "Confidence", "Details", "Evidence Image Path"])
            for row in violations:
                writer.writerow(row)

            writer.writerow([])
            writer.writerow(["ALERTS"])
            writer.writerow(["ID", "Timestamp", "Severity", "Alert Type", "Message", "Related Vehicle ID"])
            for row in alerts:
                writer.writerow(row)

        print(f"CSV report generated: {filename}")

    def generate_pdf_report(self, filename=DEFAULT_PDF_PATH):
        traffic_logs = self.db.fetch_traffic_logs()
        violations = self.db.fetch_violations()
        alerts = self.db.fetch_alerts()

        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        y = height - 40

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, "SmartCityAI Traffic Monitoring Report")
        y -= 30

        c.setFont("Helvetica", 10)
        c.drawString(40, y, f"Total Traffic Logs: {len(traffic_logs)}")
        y -= 20
        c.drawString(40, y, f"Total Violations: {len(violations)}")
        y -= 20
        c.drawString(40, y, f"Total Alerts: {len(alerts)}")
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Recent Traffic Logs")
        y -= 20
        c.setFont("Helvetica", 9)

        for row in traffic_logs[:10]:
            # row: [id, timestamp, frame_no, vehicle_count, car_count, bike_count, bus_count, truck_count, avg_speed, congestion_level]
            text = f"{row[1]} (Fr: {row[2]}) | Count: {row[3]} | Avg Speed: {row[8]} | Congestion: {row[9]}"
            c.drawString(40, y, text[:110])
            y -= 15
            if y < 60:
                c.showPage()
                y = height - 40

        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Recent Violations")
        y -= 20
        c.setFont("Helvetica", 9)

        for row in violations[:10]:
            # row: [id, timestamp, frame_no, vehicle_id, violation_type, confidence, details, evidence_image_path]
            conf = row[5] if row[5] is not None else 0.0
            text = f"{row[1]} (Fr: {row[2]}) | Vehicle {row[3]} | {row[4]} (Conf: {conf:.2f}) | {row[6]}"
            c.drawString(40, y, text[:110])
            y -= 15
            if y < 60:
                c.showPage()
                y = height - 40

        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Recent Alerts")
        y -= 20
        c.setFont("Helvetica", 9)

        for row in alerts[:10]:
            # row: [id, timestamp, severity, alert_type, message, related_vehicle_id]
            text = f"{row[1]} | {row[2]} | {row[3]} | {row[4]}"
            c.drawString(40, y, text[:110])
            y -= 15
            if y < 60:
                c.showPage()
                y = height - 40

        c.save()
        print(f"PDF report generated: {filename}")


if __name__ == "__main__":
    rg = ReportGenerator()
    rg.generate_csv_report()
    rg.generate_pdf_report()
