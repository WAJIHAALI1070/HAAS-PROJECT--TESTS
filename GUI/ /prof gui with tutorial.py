#tutorial page
import csv
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
import subprocess

class TutorialPage(QWidget):
    def _init_(self, parent=None):
        super()._init_(parent)
        self.setWindowTitle("Tutorial Page")
        self.resize(800, 600)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Select a Test")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # Ordered list of test names and corresponding executables
        self.test_executables = {
            "Walking Speed Test": "Walking_Speed.exe",
            "Functional Reach Test": "Functional_Reach.exe",
            "Timed Up and Go (TUG)": "TUG_Test.exe",
            "Standing on One Leg with Eye Open Test": "One_Leg_Standing.exe",
            "Seated Forward Bend Test": "Seated_Forward.exe",
        }

        self.patient_data_file = "Patient_Data.csv"
        self.repeat_test = False  # Flag to track if test is repeated
        self.current_patient_id = None  # Store current patient ID

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
            start_button.setStyleSheet("font-size: 16px; padding: 12px; background-color: #4CAF50; color: white; border-radius: 6px;")
            start_button.clicked.connect(lambda _, t=test: self.start_test(t))
            test_layout.addWidget(start_button)

            repeat_button = QPushButton("Repeat Test")
            repeat_button.setFixedHeight(50)
            repeat_button.setStyleSheet("font-size: 16px; padding: 12px; background-color: #FF9800; color: white; border-radius: 6px;")
            repeat_button.clicked.connect(self.set_repeat_test)
            test_layout.addWidget(repeat_button)

            main_layout.addLayout(test_layout)

        # Back button
        back_button = QPushButton("Back")
        back_button.setFixedHeight(50)
        back_button.setStyleSheet("font-size: 16px; padding: 12px; background-color: #005f87; color: white; border-radius: 8px;")
        back_button.clicked.connect(self.go_back)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def show_demo(self, test_name):
        print(f"Showing demo video for {test_name}")
        # Placeholder for video functionality

    def start_test(self, test_name):
        if test_name == "Walking Speed Test":
            elapsed_time = self.run_test("Walking_Speed.exe")  # Simulate running test and getting elapsed time
            if elapsed_time is not None:
                self.save_test_result(elapsed_time)

    def run_test(self, exe_file):
        """Runs the executable and gets elapsed time (mocked here)."""
        try:
            result = subprocess.run([exe_file], check=True, capture_output=True, text=True)
            output = result.stdout.strip()
            print(f"CLI Output: {output}")  # Ensure output is visible
            elapsed_time = float(output.split(":")[-1].strip().replace("s", ""))  # Extract elapsed time
            return elapsed_time
        except Exception as e:
            print(f"Error running {exe_file}: {e}")
            return None

    def set_repeat_test(self):
        """Mark the test as repeated for next entry."""
        self.repeat_test = True
        print("Test will be repeated.")

    def save_test_result(self, elapsed_time):
        """Save the Walking Speed Test result in CSV."""
        if not os.path.exists(self.patient_data_file):
            print("Patient data file not found.")
            return

        updated_rows = []
        found_patient = False

        with open(self.patient_data_file, "r", newline="") as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames

            # Ensure the required columns exist
            if not {"Walking Speed Test (s) 1", "Walking Speed Test (s) 2", "Walking Speed Test (s)"}.issubset(fieldnames):
                print("CSV does not contain required test columns.")
                return

            for row in reader:
                if row["ID"] == self.current_patient_id:  # Match patient by ID
                    found_patient = True
                    if not self.repeat_test:  # First test
                        row["Walking Speed Test (s) 1"] = str(elapsed_time)
                        row["Walking Speed Test (s) 2"] = "0"  # Default if not repeated
                        row["Walking Speed Test (s)"] = str(elapsed_time)
                    else:  # Repeat test
                        row["Walking Speed Test (s) 2"] = str(elapsed_time)
                        max_value = max(float(row["Walking Speed Test (s) 1"]), elapsed_time)
                        row["Walking Speed Test (s)"] = str(max_value)

                updated_rows.append(row)

        # If patient is found, update the file
        if found_patient:
            with open(self.patient_data_file, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)

            print(f"Updated test results for Patient ID: {self.current_patient_id}")
        else:
            print("Patient ID not found in CSV.")

        # Reset repeat flag
        self.repeat_test = False

    def go_back(self):
        self.parent().setCurrentIndex(0)  # Navigate back to previous page
