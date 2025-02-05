# models/organizer.py
import os
import re
import shutil
import logging
import pandas as pd
import difflib

from .matcher import FileMatcher
from .extractor import EbookMetadataExtractor


class CSVData:
    def __init__(self, metadata_csv):
        self.metadata_csv = metadata_csv
        self.df = pd.read_csv(self.metadata_csv)
        if "match_key" not in self.df.columns:
            self.df["match_key"] = self.df.apply(
                lambda row: (str(row["title"]) + " " + str(row.get("authors", ""))).lower().strip(),
                axis=1
            )

    def get_dataframe(self):
        return self.df


class FileOrganizer:
    def __init__(self, target_base_folder, duplicates_folder):
        self.target_base_folder = target_base_folder
        self.duplicates_folder = duplicates_folder
        if not os.path.exists(self.target_base_folder):
            os.makedirs(self.target_base_folder)
        if not os.path.exists(self.duplicates_folder):
            os.makedirs(self.duplicates_folder)

    def sanitize_folder_name(self, folder_name):
        sanitized = re.sub(r'[^A-Za-z0-9 _-]', '', folder_name).strip()
        if not sanitized:
            sanitized = "Unknown Author"
        return sanitized

    def move_file(self, file_path, folder_name):
        folder_name = self.sanitize_folder_name(folder_name)
        target_folder = os.path.join(self.target_base_folder, folder_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        target_path = os.path.join(target_folder, os.path.basename(file_path))
        if os.path.exists(target_path):
            dup_target_path = os.path.join(self.duplicates_folder, os.path.basename(file_path))
            try:
                shutil.move(file_path, dup_target_path)
                logging.info(f"Duplicate detected: Moved '{os.path.basename(file_path)}' to duplicates folder.")
            except Exception as e:
                logging.error(f"Error moving duplicate '{os.path.basename(file_path)}': {e}")
        else:
            try:
                shutil.move(file_path, target_path)
                logging.info(f"Moved '{os.path.basename(file_path)}' to folder '{folder_name}'.")
            except Exception as e:
                logging.error(f"Error moving file '{os.path.basename(file_path)}': {e}")


class EbookOrganizer:
    def __init__(self, metadata_csv, source_folder, target_base_folder,
                 duplicates_folder, common_extensions, candidate_labels, classifier_engine,
                 use_file_only=False, organize_by_author=False):
        self.metadata_csv = metadata_csv
        self.source_folder = source_folder
        self.target_base_folder = target_base_folder
        self.duplicates_folder = duplicates_folder
        self.common_extensions = common_extensions
        self.candidate_labels = candidate_labels
        self.classifier_engine = classifier_engine
        self.use_file_only = use_file_only
        self.organize_by_author = organize_by_author

        self.csv_data = CSVData(metadata_csv)
        self.csv_df = self.csv_data.get_dataframe()
        self.file_matcher = FileMatcher(source_folder, common_extensions)
        self.file_organizer = FileOrganizer(target_base_folder, duplicates_folder)
        self.metadata_extractor = EbookMetadataExtractor(enable_title_cleaning=False)

    def organize(self, progress_callback=None):
        total = len(self.file_matcher.candidate_files)
        processed = 0
        for file_path in self.file_matcher.candidate_files[:]:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ["." + ext.strip(".").lower() for ext in ["epub", "pdf", "mobi"]]:
                continue

            title, author, _ = self.metadata_extractor.get_book_metadata(file_path)
            if not title:
                title = os.path.splitext(os.path.basename(file_path))[0]
            file_key = (title + " " + author).lower().strip()
            if not file_key:
                file_key = os.path.splitext(os.path.basename(file_path))[0].lower().strip()

            if self.organize_by_author:
                folder_name = author if author else "Unknown Author"
                self.file_organizer.move_file(file_path, folder_name)
                self.file_matcher.remove_file(file_path)
                processed += 1
                if progress_callback:
                    progress_callback(processed, total)
                continue

            if self.use_file_only:
                combined_prompt = file_key
                new_predicted_category, new_score, _ = self.classifier_engine.classify_text(combined_prompt)
                predicted_category = new_predicted_category if new_predicted_category and new_predicted_category != "Unknown" else "Unknown"
            else:
                best_index, ratio = self.file_matcher.find_best_csv_match(file_key, self.csv_df, threshold=0.6)
                if best_index is None:
                    logging.warning(f"No CSV match for file '{file_path}' (key: {file_key}, best ratio: {ratio:.2f}).")
                    continue
                matched_row = self.csv_df.iloc[best_index]
                predicted_category = matched_row["predicted_genre"] if "predicted_genre" in matched_row else "Unknown"
                csv_prompt = matched_row["title"] + " " + str(matched_row.get("authors", ""))
                combined_prompt = (csv_prompt + " " + file_key).strip()
                new_predicted_category, new_score, _ = self.classifier_engine.classify_text(combined_prompt)
                if new_predicted_category and new_predicted_category != "Unknown":
                    predicted_category = new_predicted_category

            self.file_organizer.move_file(file_path, predicted_category)
            self.file_matcher.remove_file(file_path)
            processed += 1
            if progress_callback:
                progress_callback(processed, total)
