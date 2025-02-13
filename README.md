# Ebook Organizer Application (AI generated README)

##WIP

## Overview

The Ebook Organizer Application streamlines the organization of your ebook files by leveraging metadata exported from Calibre (in CSV format), file-based metadata extraction (from EPUBs and PDFs), and a zero-shot classification pipeline using Hugging Face's transformers. The application supports two primary modes:

1. **Predicted Genre Mode:**  
   Uses fuzzy matching of CSV metadata combined with file metadata to automatically assign a genre. Files are moved into subfolders based on the predicted genre.

2. **Custom Classification Tag Mode:**  
   Allows you to specify a custom genre (e.g., "Romance") and a confidence threshold via the GUI. When enabled, only files that meet or exceed the threshold for the custom tag are moved directly into the target directory (without creating a subfolder). Files that do not meet the threshold remain in their original location.

Additionally, you can choose to:
- Use file metadata only (ignoring CSV data).
- Organize by author name instead of genre.

**Please note:** The program recursively processes all folders within the source directory.

A Tkinter-based graphical user interface (GUI) provides an easy way to configure options, select folders and files, and monitor progress.

## Features

- **Metadata Extraction:**  
  Extracts metadata from EPUB and PDF files, with graceful handling of problematic PDF files.
  
- **CSV Fuzzy Matching:**  
  Matches file metadata with CSV data exported from Calibre using fuzzy string matching.

- **Zero-Shot Classification:**  
  Uses Hugging Face's `facebook/bart-large-mnli` model for genre classification, with support for batch processing to maximize GPU efficiency.

- **Custom Classification Tag Mode:**  
  Allows you to override the default classification by specifying a custom genre and a confidence threshold. When enabled, only files that meet the threshold are moved directly to the target directory.

- **User-Friendly GUI:**  
  A clean, organized Tkinter interface for selecting files, configuring options, and monitoring progress.

## Requirements

- **Python 3.x**
- **Python packages:**
  - pandas
  - requests
  - ebooklib
  - transformers
  - PyPDF2
  - tkinter (usually included with Python)
- (Optional) CUDA-enabled GPU for faster transformer inference

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/tasnaps/FileCategorizer.git
   cd FileCategorizer
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install Required Packages:**

   Ensure you have a `requirements.txt` file (if not, create one with the required packages) and run:

   ```bash
   pip install -r requirements.txt
   ```

## Directory Structure

```
FileCategorizer/
├── config.py
├── main.py
├── README.md
├── requirements.txt
├── ui.py
├── models/
│   ├── __init__.py
│   ├── classifier.py
│   ├── extractor.py
│   ├── matcher.py
│   └── organizer.py
└── utility/
    ├── __init__.py
    └── prompt.py
```

- **config.py:** Contains candidate genres with descriptions.
- **main.py:** The entry point that launches the Tkinter GUI.
- **ui.py:** Contains the GUI (Tkinter) code.
- **models/:** Holds core logic (metadata extraction, classification, matching, and file organization).
- **utility/:** Contains helper functions such as the prompt builder.

## Usage

1. **Run the Application:**

   ```bash
   python main.py
   ```

2. **Using the GUI:**

   - **Input Fields:**
     - **Metadata CSV:** Path to the Calibre-exported metadata CSV file.
     - **Source Folder:** Folder containing your ebook files.
     - **Target Folder:** Folder where organized files will be moved.
     - **Duplicates Folder:** Folder where duplicates will be moved.
     
   - **Options:**
     - **Use file metadata only:** If checked, the application ignores CSV metadata.
     - **Organize by Author:** If checked, files are organized by the extracted author.
     - **Use Custom Classification Tag:** When checked, the following controls are enabled:
       - **Desired Category:** Enter the custom genre (e.g., "Romance").
       - **Threshold (0-1):** Adjust the confidence threshold. In custom mode, if a file’s confidence score for the custom tag is equal to or above the threshold, the file is moved directly to the target directory. Otherwise, the file remains in its original location.
       
   - **Start Organizing:**  
     Click the "Start Organizing" button. The progress bar and status label will update as files are processed.

3. **Logging and Debugging:**
   - The console displays debug information (including the generated classification prompts) and any errors or warnings during processing.
   - Check the logs for PDF extraction warnings, fuzzy matching results, and classification details.

## Troubleshooting

- **Missing Logs:**  
  Ensure the logging level is set to INFO or lower and that no external libraries override your logging configuration.

- **PDF Extraction Errors:**  
  Some PDFs may be corrupt or non-standard. These files are logged and skipped.

- **Performance:**  
  Files are processed in batches (default size 32) to maximize efficiency. Adjust the batch size in `ui.py` if necessary.

- **GPU Warnings:**  
  If you see warnings about sequential pipeline usage on the GPU, consider using batch processing or fine-tuning your model parameters.

## Future Enhancements

- Transition to a database for metadata storage.
- Improve fuzzy matching with advanced algorithms.
- Fine-tune the classification model on a domain-specific dataset.
- Add support for additional ebook formats.
- Implement a feedback mechanism for manual corrections.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions, bug reports, or contributions, please open an issue or submit a pull request on GitHub.
