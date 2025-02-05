import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import logging

from models.organizer import EbookOrganizer
from models.classifier import ClassifierEngine
from utility.prompt import build_prompt
from config import CANDIDATE_LABELS_WITH_DESCRIPTIONS


class OrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ebook Organizer")
        self.root.geometry("650x550")

        # File and folder paths.
        self.metadata_csv = tk.StringVar(value="G:/All Books/My books.csv")
        self.source_folder = tk.StringVar(value="G:/All Books/PDF's")
        self.target_base_folder = tk.StringVar(value="G:/All Books/Organized_PDFs")
        self.duplicates_folder = tk.StringVar(value="G:/All Books/PDF Duplicates")

        # Progress indicator.
        self.progress_var = tk.DoubleVar(value=0)

        # Candidate labels with descriptions.
        self.candidate_labels_with_descriptions = CANDIDATE_LABELS_WITH_DESCRIPTIONS

        # Options.
        self.use_file_only = tk.BooleanVar(value=False)
        self.organize_by_author = tk.BooleanVar(value=True)  # Default: organize by author

        # New: Option to use a custom classification tag.
        self.use_custom_tag = tk.BooleanVar(value=False)
        self.desired_category = tk.StringVar(value="Romance")
        self.threshold = tk.DoubleVar(value=0.7)

        self.create_widgets()
        self.update_custom_tag_state()  # Set initial state for custom tag controls.

    def create_widgets(self):
        # Use a frame for file/folder inputs.
        input_frame = tk.Frame(self.root)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(input_frame, text="Metadata CSV:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.metadata_csv, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(input_frame, text="Browse", command=self.browse_metadata).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(input_frame, text="Source Folder:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.source_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(input_frame, text="Browse", command=self.browse_source).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(input_frame, text="Target Folder:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.target_base_folder, width=50).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(input_frame, text="Browse", command=self.browse_target).grid(row=2, column=2, padx=5, pady=5)

        tk.Label(input_frame, text="Duplicates Folder:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.duplicates_folder, width=50).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(input_frame, text="Browse", command=self.browse_duplicates).grid(row=3, column=2, padx=5, pady=5)

        # Options frame.
        options_frame = tk.Frame(self.root)
        options_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        tk.Checkbutton(options_frame, text="Use file metadata only (ignore CSV metadata)",
                       variable=self.use_file_only).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        tk.Checkbutton(options_frame, text="Organize by Author",
                       variable=self.organize_by_author).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        tk.Checkbutton(options_frame, text="Use Custom Classification Tag",
                       variable=self.use_custom_tag, command=self.update_custom_tag_state).grid(row=2, column=0,
                                                                                                columnspan=2,
                                                                                                sticky="w", padx=5,
                                                                                                pady=5)

        # Custom tag controls.
        tk.Label(options_frame, text="Desired Category:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.desired_category_entry = tk.Entry(options_frame, textvariable=self.desired_category, width=20)
        self.desired_category_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(options_frame, text="Threshold (0-1):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.threshold_scale = tk.Scale(options_frame, variable=self.threshold, from_=0.0, to=1.0, resolution=0.01,
                                        orient="horizontal", length=200)
        self.threshold_scale.grid(row=4, column=1, padx=5, pady=5)

        # Progress and status.
        progress_frame = tk.Frame(self.root)
        progress_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate",
                                            variable=self.progress_var)
        self.progress_bar.grid(row=0, column=0, columnspan=3, padx=5, pady=20)
        self.status_label = tk.Label(progress_frame, text="Idle")
        self.status_label.grid(row=1, column=0, columnspan=3)

        tk.Button(self.root, text="Start Organizing", command=self.start_organizing).grid(row=3, column=0, pady=10)

    def update_custom_tag_state(self):
        """Enable or disable custom tag controls based on the checkbox."""
        if self.use_custom_tag.get():
            self.desired_category_entry.config(state="normal")
            self.threshold_scale.config(state="normal")
        else:
            self.desired_category_entry.config(state="disabled")
            self.threshold_scale.config(state="disabled")

    def browse_metadata(self):
        filename = filedialog.askopenfilename(title="Select Metadata CSV", filetypes=[("CSV Files", "*.csv")])
        if filename:
            self.metadata_csv.set(filename)

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder.set(folder)

    def browse_target(self):
        folder = filedialog.askdirectory(title="Select Target Folder")
        if folder:
            self.target_base_folder.set(folder)

    def browse_duplicates(self):
        folder = filedialog.askdirectory(title="Select Duplicates Folder")
        if folder:
            self.duplicates_folder.set(folder)

    def update_progress(self, current, total):
        percent = (current / total) * 100
        self.progress_var.set(percent)
        self.status_label.config(text=f"Processed {current} of {total}")

    def start_organizing(self):
        self.status_label.config(text="Starting...")
        threading.Thread(target=self.run_organizer, daemon=True).start()

    def run_organizer(self):
        try:
            organizer = EbookOrganizer(
                metadata_csv=self.metadata_csv.get(),
                source_folder=self.source_folder.get(),
                target_base_folder=self.target_base_folder.get(),
                duplicates_folder=self.duplicates_folder.get(),
                common_extensions=[".epub", ".pdf", ".mobi"],
                candidate_labels=list(self.candidate_labels_with_descriptions.keys()),
                classifier_engine=ClassifierEngine(list(self.candidate_labels_with_descriptions.keys()), device=0),
                use_file_only=self.use_file_only.get(),
                organize_by_author=self.organize_by_author.get()
            )
            # Load CSV data and ensure match_key exists.
            csv_df = pd.read_csv(self.metadata_csv.get())
            if "match_key" not in csv_df.columns:
                csv_df["match_key"] = csv_df.apply(
                    lambda row: (str(row["title"]) + " " + str(row.get("authors", ""))).lower().strip(),
                    axis=1
                )
            organizer.csv_df = csv_df

            total = len(organizer.file_matcher.candidate_files)
            processed = 0
            batch_size = 16  # Adjust batch size as needed.
            batch_prompts = []
            batch_file_paths = []
            for file_path in organizer.file_matcher.candidate_files[:]:
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in [".epub", ".pdf", ".mobi"]:
                    continue

                title, author, _ = organizer.metadata_extractor.get_book_metadata(file_path)
                if not title:
                    title = os.path.splitext(os.path.basename(file_path))[0]
                file_key = (title + " " + author).lower().strip()
                if not file_key:
                    file_key = os.path.splitext(os.path.basename(file_path))[0].lower().strip()

                # If organizing by author, skip classification and use the author directly.
                if self.organize_by_author.get():
                    folder_name = author if author else "Unknown Author"
                    organizer.file_organizer.move_file(file_path, folder_name)
                    organizer.file_matcher.remove_file(file_path)
                    processed += 1
                    self.root.after(0, self.update_progress, processed, total)
                    continue

                # Prepare the classification prompt.
                if self.use_file_only.get():
                    prompt = file_key
                    print("DEBUG: Prompt (file-only):", prompt)
                else:
                    best_index, ratio = organizer.file_matcher.find_best_csv_match(file_key, organizer.csv_df,
                                                                                   threshold=0.6)
                    if best_index is None:
                        logging.warning(
                            f"No CSV match for file '{file_path}' (key: {file_key}, best ratio: {ratio:.2f}). Using file metadata only.")
                        prompt = file_key
                    else:
                        matched_row = organizer.csv_df.iloc[best_index]
                        csv_prompt = matched_row["title"] + " " + str(matched_row.get("authors", ""))
                        prompt = build_prompt(csv_prompt, file_key, self.candidate_labels_with_descriptions)
                    print("DEBUG: Prompt:", prompt)

                # Append prompt and file path to batch.
                batch_prompts.append(prompt)
                batch_file_paths.append(file_path)

                # Process the batch if reached the desired batch size.
                if len(batch_prompts) >= batch_size:
                    results = organizer.classifier_engine.classify_texts(batch_prompts, batch_size=len(batch_prompts))
                    for i, res in enumerate(results):
                        # If custom tag usage is enabled, check if desired tag confidence meets threshold.
                        if self.use_custom_tag.get():
                            desired = self.desired_category.get().strip().lower()
                            threshold_val = self.threshold.get()
                            desired_conf = None
                            for lbl, score in zip(res["labels"], res["scores"]):
                                if lbl.lower() == desired:
                                    desired_conf = score
                                    break
                            if desired_conf is not None and desired_conf >= threshold_val:
                                predicted_category = self.desired_category.get().strip()
                            else:
                                predicted_category = res["labels"][0] if res["labels"][0] != "Unknown" else "Unknown"
                        else:
                            predicted_category = res["labels"][0] if res["labels"][0] != "Unknown" else "Unknown"
                        organizer.file_organizer.move_file(batch_file_paths[i], predicted_category)
                        organizer.file_matcher.remove_file(batch_file_paths[i])
                    processed += len(batch_prompts)
                    self.root.after(0, self.update_progress, processed, total)
                    batch_prompts = []
                    batch_file_paths = []

            # Process any remaining prompts.
            if batch_prompts:
                results = organizer.classifier_engine.classify_texts(batch_prompts, batch_size=len(batch_prompts))
                for i, res in enumerate(results):
                    if self.use_custom_tag.get():
                        desired = self.desired_category.get().strip().lower()
                        threshold_val = self.threshold.get()
                        desired_conf = None
                        for lbl, score in zip(res["labels"], res["scores"]):
                            if lbl.lower() == desired:
                                desired_conf = score
                                break
                        if desired_conf is not None and desired_conf >= threshold_val:
                            predicted_category = self.desired_category.get().strip()
                        else:
                            predicted_category = res["labels"][0] if res["labels"][0] != "Unknown" else "Unknown"
                    else:
                        predicted_category = res["labels"][0] if res["labels"][0] != "Unknown" else "Unknown"
                    organizer.file_organizer.move_file(batch_file_paths[i], predicted_category)
                    organizer.file_matcher.remove_file(batch_file_paths[i])
                processed += len(batch_prompts)
                self.root.after(0, self.update_progress, processed, total)

            self.root.after(0, self.status_label.config, {"text": "Organizing complete!"})
            messagebox.showinfo("Done", "Files have been organized.")
        except Exception as e:
            logging.error(f"Error during organization: {e}")
            self.root.after(0, self.status_label.config, {"text": "Error occurred."})
            messagebox.showerror("Error", f"An error occurred: {e}")