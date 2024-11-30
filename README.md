# Apex Project

## Overview

The Apex project is a Python-based application designed for automated processing and analysis of PDF documents. 
It provides functionalities to extract text from PDFs, generate concise summaries using an AI model, and store the results in JSON format.

## Features

- **PDF Text Extraction**: Extracts textual content from PDF files using the PyPDF2 library.
- **AI-Powered Summarization**: Utilizes the ChatXAI API to generate concise summaries of PDF content.
- **JSON Output**: Saves the processed results, including summaries and metadata, into a structured JSON format.
- **Environment Variable Support**: Supports configuration via YAML files and environment variables.
- **Logging**: Provides detailed logging for debugging and monitoring.

## Requirements

- Python 3.8 or higher
- Required Python libraries are listed in `requirements.txt`.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/apex.git
   cd apex
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the project root and define necessary environment variables.

5. Update the configuration:
   - Edit `config.yaml` to specify input/output directories and other settings.

## Usage

1. Place PDF files in the input directory specified in `config.yaml`.

2. Run the main script:

   ```bash
   python main.py
   ```

3. Check the output directory for JSON files containing the summaries and other results.

## Configuration

- All configurations are managed via the `config.yaml` file. Replace placeholders with appropriate values, especially:
  - API keys for ChatXAI.
  - Directories for input/output files.
  - Logging settings.

## Logging

- Logs are stored in the file specified in the configuration (`app.log` by default).
- Adjust the log level (`INFO`, `DEBUG`, etc.) in the `config.yaml` file as needed.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Add feature-name"`).
4. Push to your fork (`git push origin feature-name`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions or feedback, please contact [your email address].