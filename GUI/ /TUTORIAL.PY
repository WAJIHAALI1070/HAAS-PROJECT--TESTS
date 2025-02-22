import csv
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
import subprocess
import re


class TutorialPage(QWidget):
    def __init__(self, patient_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tutorial Page")
        self.resize(800, 600)

        # Ensure patient_id is stored correctly
        self.current_patient_id = str(patient_id)
        print(f"DEBUG: Received Patient ID = {self.current_patient_id} (Type: {type(self.current_patient_id)})")

        self.patient_data_file = "Patient_Data.csv"

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Select a Test")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # Test names and their corresponding executables
        self.test_executables = {
            "Walking Speed Test": "gui testting.exe",
            "Functional Reach Test": "gui testting.exe",
            "Timed Up and Go (TUG)": "gui testting.exe",
            "Standing on One Leg with Eye Open Test": "gui testting.exe",
            "Seated Forward Bend Test": "gui testting.exe",
        }

        # Creating test buttons
        for test in self.test_executables.keys():
            test_layout = QHBoxLayout()

            test_label = QLabel(test)
            test_label.setFixedWidth(300)
            test_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            test_layout.addWidget(test_label)

            demo_button = QPushButton("Demo Video")
            demo_button.setFixedHeight(50)
            demo_button.setStyleSheet("font-size: 16px; padding: 12px;")
            demo_button.clicked.connect(lambda _, t=test: self.show_demo(t))
            test_layout.addWidget(demo_button)

            start_button = QPushButton("Start Test")
            start_button.setFixedHeight(50)
            start_button.setStyleSheet(
                "font-size: 16px; padding: 12px; background-color: #4CAF50; color: white; border-radius: 6px;")
            start_button.clicked.connect(lambda _, t=test: self.run_test(t, 1))
            test_layout.addWidget(start_button)

            repeat_button = QPushButton("Repeat Test")
            repeat_button.setFixedHeight(50)
            repeat_button.setStyleSheet(
                "font-size: 16px; padding: 12px; background-color: #FF9800; color: white; border-radius: 6px;")
            repeat_button.clicked.connect(lambda _, t=test: self.run_test(t, 2))
            test_layout.addWidget(repeat_button)

            test_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

            main_layout.addLayout(test_layout)

        self.setLayout(main_layout)

    def show_demo(self, test_name):
        print(f"Showing demo video for {test_name}")

    def run_test(self, test_name, attempt):
        exe_file = self.test_executables.get(test_name, None)
        if exe_file:
            try:
                result = subprocess.run([exe_file], capture_output=True, text=True, check=True)
                output = result.stdout.strip()
                print(f"CLI Output: {output}")

                test_value = self.extract_test_result(output)
                if test_value:
                    self.save_test_result(test_name, test_value, attempt)
            except subprocess.CalledProcessError as e:
                print(f"Execution failed: {e.stderr}")
            except FileNotFoundError:
                print(f"Error: Executable '{exe_file}' not found.")

    def extract_test_result(self, output):
        """Extracts the most relevant numeric value (time or distance) from the output."""
        numbers = re.findall(r"\d+\.?\d*", output)  # Extract all numbers (int and float)
        return numbers[-1] if numbers else "0"  # Get the last number (assuming it's the most relevant)

    def save_test_result(self, test_name, test_value, attempt):
        """Saves test results in the CSV file without repeating headers."""
        file_exists = os.path.exists(self.patient_data_file)

        # Read the existing data
        rows = []
        if file_exists:
            with open(self.patient_data_file, "r", newline="") as file:
                reader = csv.reader(file)
                rows = list(reader)

        # Ensure headers exist
        headers = rows[0] if rows else ["ID", "Age", "Gender"]
        test_columns = [f"{test_name} 1", f"{test_name} 2"]

        # Add new test columns if missing
        for col in test_columns:
            if col not in headers:
                headers.append(col)

        print(f"Patient ID: {self.current_patient_id} (Type: {type(self.current_patient_id)})")

        # Find patient row or create new one
        patient_row = next((row for row in rows[1:] if str(row[0]) == str(self.current_patient_id)), None)
        if not patient_row:
            patient_row = [self.current_patient_id, "", ""] + ["0"] * (len(headers) - 3)
            rows.append(patient_row)

        # Ensure row length matches headers
        while len(patient_row) < len(headers):
            patient_row.append("0")

        # Update the test result
        col_idx = headers.index(test_columns[attempt - 1])
        patient_row[col_idx] = test_value

        # Write back the updated CSV with headers only once
        with open(self.patient_data_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows[1:])  # Avoid rewriting headers again in the rows

        print(f"Test result saved: {test_name} Attempt {attempt} - {test_value}")
