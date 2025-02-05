# models/matcher.py
import os
import re
import difflib

class FileMatcher:
    def __init__(self, source_folder, common_extensions):
        self.source_folder = source_folder
        self.common_extensions = common_extensions
        self.candidate_files = self.build_candidate_files()

    def build_candidate_files(self):
        candidate_files = []
        for root, dirs, files in os.walk(self.source_folder):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in self.common_extensions:
                    candidate_files.append(os.path.join(root, f))
        return candidate_files

    def find_best_csv_match(self, file_key, csv_df, threshold=0.6):
        best_index = None
        best_ratio = 0.0
        for index, row in csv_df.iterrows():
            csv_key = row["match_key"]
            ratio = difflib.SequenceMatcher(None, file_key, csv_key).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_index = index
        if best_ratio >= threshold:
            return best_index, best_ratio
        else:
            return None, best_ratio

    def remove_file(self, file_path):
        if file_path in self.candidate_files:
            self.candidate_files.remove(file_path)
