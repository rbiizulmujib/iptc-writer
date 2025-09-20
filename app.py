import sys
import os
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QLabel, QComboBox, QTextEdit, QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtCore import Qt
from iptcinfo3 import IPTCInfo


class CustomMessageBox(QDialog):
    def __init__(self, parent=None, title="", text=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        message_label = QLabel(text)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_box.addWidget(ok_button)

        layout.addLayout(button_box)
        self.setMinimumWidth(350)
        self.adjustSize()

    @staticmethod
    def show(parent, title, text):
        dialog = CustomMessageBox(parent, title, text)
        dialog.exec()


def norm(s: str) -> str:
    """Normalisasi teks header: trim + lower + hilangkan spasi ganda."""
    return " ".join((s or "").strip().split()).lower()


class IPTCWriterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPTC Writer")
        self.setGeometry(100, 100, 900, 650)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Selected Folder: None")
        self.folder_button = QPushButton("Select Folder with JPG Files")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label, stretch=1)
        folder_layout.addWidget(self.folder_button)
        main_layout.addLayout(folder_layout)

        # CSV file selection
        csv_layout = QHBoxLayout()
        self.csv_label = QLabel("Selected CSV: None")
        self.csv_button = QPushButton("Select CSV File")
        self.csv_button.clicked.connect(self.select_csv)
        csv_layout.addWidget(self.csv_label, stretch=1)
        csv_layout.addWidget(self.csv_button)
        main_layout.addLayout(csv_layout)

        # Column mapping
        mapping_layout = QHBoxLayout()
        self.filename_combo = QComboBox()
        self.title_combo = QComboBox()
        self.description_combo = QComboBox()
        self.keywords_combo = QComboBox()

        for lbl, combo in [
            ("Filename Column:", self.filename_combo),
            ("Title Column:", self.title_combo),
            ("Description Column:", self.description_combo),
            ("Keywords Column:", self.keywords_combo),
        ]:
            mapping_layout.addWidget(QLabel(lbl))
            mapping_layout.addWidget(combo)

        main_layout.addLayout(mapping_layout)

        # Process button
        self.process_button = QPushButton("Process Images")
        self.process_button.clicked.connect(self.process_images)
        self.process_button.setEnabled(False)
        main_layout.addWidget(self.process_button)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        main_layout.addWidget(QLabel("Log:"))
        main_layout.addWidget(self.log_display)

        # CSV data table
        self.csv_table = QTableWidget()
        self.csv_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.csv_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        main_layout.addWidget(QLabel("CSV Data Preview:"))
        main_layout.addWidget(self.csv_table)

        # State
        self.selected_folder = None
        self.selected_csv = None
        self.csv_data = []
        self.headers = []
        self.norm_headers = []  # header yang dinormalisasi

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with JPG Files")
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(f"Selected Folder: {folder}")
            self.log(f"Selected folder: {folder}")
            self.check_process_ready()

    def select_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.selected_csv = file_path
            self.csv_label.setText(f"Selected CSV: {file_path}")
            self.log(f"Selected CSV: {file_path}")
            self.load_csv_data(file_path)
            self.check_process_ready()

    def load_csv_data(self, file_path):
        try:
            # Deteksi dialect dan BOM
            with open(file_path, "rb") as f:
                raw = f.read()
            text = raw.decode("utf-8-sig")  # buang BOM jika ada

            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(text.splitlines()[0] if text else ",")
            except Exception:
                dialect = csv.excel
                dialect.delimiter = ','

            reader = csv.reader(text.splitlines(), dialect)
            self.csv_data = [list(map(lambda x: (x or "").strip(), row)) for row in reader]

            if not self.csv_data:
                self.log("CSV file is empty")
                CustomMessageBox.show(self, "Empty CSV", "CSV file is empty.")
                return

            self.headers = self.csv_data[0]
            self.norm_headers = [norm(h) for h in self.headers]

            # Update combo boxes
            for combo in (self.filename_combo, self.title_combo, self.description_combo, self.keywords_combo):
                combo.clear()
                combo.addItems(self.headers)

            # Default selections (best-guess, case-insensitive)
            def try_select(combo: QComboBox, candidates):
                for cand in candidates:
                    if cand in self.norm_headers:
                        combo.setCurrentIndex(self.norm_headers.index(cand))
                        return
                # fallback ke index 0 bila ada
                if combo.count() > 0 and combo.currentIndex() < 0:
                    combo.setCurrentIndex(0)

            try_select(self.filename_combo, ["filename", "file name", "file", "image", "image name"])
            try_select(self.title_combo, ["title", "object name", "name"])
            try_select(self.description_combo, ["description", "caption", "caption/abstract"])
            try_select(self.keywords_combo, ["keywords", "tags", "tag"])

            self.populate_table()

        except Exception as e:
            self.log(f"Error loading CSV: {str(e)}")
            CustomMessageBox.show(self, "Error", f"Failed to load CSV file:\n{str(e)}")

    def populate_table(self):
        if not self.csv_data:
            return

        rows = len(self.csv_data) - 1
        cols = len(self.headers)

        self.csv_table.setRowCount(rows)
        self.csv_table.setColumnCount(cols)
        self.csv_table.setHorizontalHeaderLabels(self.headers)

        for i, row in enumerate(self.csv_data[1:]):
            for j in range(cols):
                val = row[j] if j < len(row) else ""
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.csv_table.setItem(i, j, item)

        header = self.csv_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

    def check_process_ready(self):
        ready = bool(self.selected_folder and self.selected_csv)
        self.process_button.setEnabled(ready)

    def log(self, message):
        self.log_display.append(message)
        QApplication.processEvents()

    def process_images(self):
        if not (self.selected_folder and self.csv_data and self.headers):
            return

        # Pastikan combo terpilih
        for combo, label in [
            (self.filename_combo, "Filename"),
            (self.title_combo, "Title"),
            (self.description_combo, "Description"),
            (self.keywords_combo, "Keywords"),
        ]:
            if combo.currentIndex() < 0:
                CustomMessageBox.show(self, "Mapping Missing", f"Select a column for {label}.")
                return

        filename_col = self.filename_combo.currentIndex()
        title_col = self.title_combo.currentIndex()
        description_col = self.description_combo.currentIndex()
        keywords_col = self.keywords_combo.currentIndex()

        processed_count = 0
        error_count = 0

        for i, row in enumerate(self.csv_data[1:], start=2):  # start=2 untuk nomor baris real di CSV (termasuk header)
            # Safety untuk row pendek
            max_need = max(filename_col, title_col, description_col, keywords_col)
            if len(row) <= max_need:
                self.log(f"Warning: Row {i} doesn't have enough columns, skipping")
                error_count += 1
                continue

            filename = (row[filename_col] or "").strip()
            if not filename:
                self.log(f"Warning: Row {i} has empty filename, skipping")
                error_count += 1
                continue

            # Normalize filename (trim spasi & kutip)
            filename = filename.strip().strip('"\'')

            title = row[title_col].strip() if title_col < len(row) else ""
            description = row[description_col].strip() if description_col < len(row) else ""
            keywords = row[keywords_col].strip() if keywords_col < len(row) else ""

            file_path = os.path.join(self.selected_folder, filename)

            if not os.path.exists(file_path):
                self.log(f"Warning: File not found: {filename} (row {i}), skipping")
                error_count += 1
                continue

            if not filename.lower().endswith((".jpg", ".jpeg")):
                self.log(f"Warning: Not a JPG: {filename} (row {i}), skipping")
                error_count += 1
                continue

            try:
                self.write_iptc_data(file_path, title, description, keywords)
                self.log(f"OK: {filename}")
                processed_count += 1
            except Exception as e:
                self.log(f"Error processing {filename}: {str(e)}")
                error_count += 1

        self.log(f"Processing complete. {processed_count} files processed, {error_count} errors.")
        CustomMessageBox.show(
            self, "Processing Complete",
            f"Successfully processed: {processed_count} files\nErrors: {error_count}"
        )



    def write_iptc_data(self, image_path, title, description, keywords):
        try:
            info = IPTCInfo(image_path, force=True, inp_charset='utf-8', out_charset='utf-8')

            if title:
                info['object name'] = title

            if description:
                info['caption/abstract'] = description

            if keywords:
                cleaned = keywords.replace(";", ",")
                keyword_list = [kw.strip() for kw in cleaned.split(",") if kw.strip()]
                info['keywords'] = keyword_list

            # Simpan perubahan
            info.save_as(image_path)
            print(f"Saved IPTC to: {image_path}")

            # Hapus file setelah berhasil simpan
            if os.path.exists(image_path):
                os.remove(image_path+'~')
                print(f"Deleted file: {image_path+'~'}")

        except Exception as e:
            print(f"Error writing IPTC data for {image_path}: {e}")


        except Exception as e:
            raise Exception(f"Failed to write IPTC data: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = IPTCWriterApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
