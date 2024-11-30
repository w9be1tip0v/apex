import json
import logging
import os
from pathlib import Path
from typing import List, Optional

import PyPDF2
import yaml
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.runnables import RunnableSequence
from langchain_xai import ChatXAI

from prompts import get_summary_prompt

# =========================
# Configuration and Logging Setup
# =========================


class Config:
    """Class to load and maintain configuration settings."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initializes the Config class with a given configuration path.

        Args:
            config_path (str): Path to the configuration file. Defaults to "config.yaml".
        """
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Loads configuration from a YAML file and resolves environment variables."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        # Replace environment variable placeholders with actual values
        config = self.resolve_env_variables(config)
        return config

    def resolve_env_variables(self, config: dict) -> dict:
        """Resolve environment variable placeholders in the configuration."""
        if isinstance(config, dict):
            for key, value in config.items():
                config[key] = self.resolve_env_variables(value)
        elif isinstance(config, list):
            config = [self.resolve_env_variables(item) for item in config]
        elif (
            isinstance(config, str) and config.startswith("${") and config.endswith("}")
        ):
            env_var = config[2:-1]
            env_value = os.getenv(env_var)
            if not env_value:
                raise EnvironmentError(f"Environment variable '{env_var}' is not set.")
            return env_value
        return config


def setup_logging(log_file: str, log_level: str):
    """Set up logging."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


# =========================
# PDF Processing Classes
# =========================


class PDFExtractor:
    """Class to extract text from PDF files."""

    @staticmethod
    def extract_text(pdf_path: Path) -> str:
        """Extract text from the specified PDF file.

        Args:
            pdf_path (Path): Path to the PDF file.

        Returns:
            str: Extracted text.
        """
        logger.info(f"Extracting text from PDF file: {pdf_path}")
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(reader.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        logger.debug(f"Extracted text from page {page_num}.")
            logger.info(f"Completed text extraction from PDF: {pdf_path}")
            return text
        except Exception as e:
            logger.error(
                f"Error occurred while extracting text from PDF '{pdf_path}': {e}"
            )
            raise


class PDFAnalyzer:
    """Class to manage PDF analysis and save results."""

    def __init__(
        self, chat_xai: ChatXAI, prompt_template: PromptTemplate, max_length: int
    ):
        """Initialize the PDFAnalyzer.

        Args:
            chat_xai (ChatXAI): Instance of ChatXAI.
            prompt_template (PromptTemplate): Prompt template.
            max_length (int): Maximum length of the summary.
        """
        self.chain = RunnableSequence(prompt_template, chat_xai)
        self.max_length = max_length

    def analyze_text(self, text: str) -> dict:
        """Analyze the extracted text and return the results along with token usage.

        Args:
            text (str): Text to analyze.

        Returns:
            dict: Analysis results and token usage.
        """
        logger.info("Analyzing text using the Grok AI model.")
        try:
            with get_openai_callback() as cb:
                summary = self.chain.invoke({"document": text})
                logger.info("Text analysis completed.")
                logger.info(f"Tokens used: {cb.total_tokens}")

            summary_text = getattr(summary, "content", str(summary))

            if len(summary_text) > self.max_length:
                summary_text = summary_text[: self.max_length]
                logger.warning(
                    f"Summary exceeded the maximum length of {self.max_length} characters and was truncated."
                )

            return {"summary": summary_text, "used_tokens": cb.total_tokens}
        except Exception as e:
            logger.error(f"Error occurred during text analysis: {e}")
            raise

    @staticmethod
    def save_to_json(data: dict, output_path: Path):
        """Save analysis results to a JSON file.

        Args:
            data (dict): Data to save.
            output_path (Path): Path to save the JSON file.
        """
        logger.info(f"Saving analysis results to JSON file: {output_path}")
        try:
            with open(output_path, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            logger.info(f"Successfully saved JSON file: {output_path}")
        except Exception as e:
            logger.error(f"Error occurred while saving JSON file '{output_path}': {e}")
            raise


# =========================
# Main Processing Function
# =========================


def load_configuration(config_path: str = "config.yaml") -> dict:
    """Load configuration from a YAML file.

    Args:
        config_path (str, optional): Path to the configuration file. Default is "config.yaml".

    Returns:
        dict: Configuration dictionary.
    """
    config_loader = Config(config_path)
    return config_loader.config


def main():
    """Main processing function."""
    logger.info("Starting the application.")

    config = load_configuration()
    max_length = config.get("summary", {}).get("max_length", 500)

    input_dir = Path(config["directories"]["input"])
    output_dir = Path(config["directories"]["output"])
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Input directory: {input_dir.resolve()}")
    logger.info(f"Output directory: {output_dir.resolve()}")

    chat_xai = ChatXAI(
        xai_api_key=config["xai"]["api_key"],
        model="grok-beta",
        temperature=0.7,
    )

    template = get_summary_prompt(max_length=max_length)

    analyzer = PDFAnalyzer(
        chat_xai=chat_xai, prompt_template=template, max_length=max_length
    )

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}.")
        return

    for pdf_path in pdf_files:
        try:
            output_json_path = output_dir / f"{pdf_path.stem}_summary.json"

            if output_json_path.exists():
                logger.info(
                    f"Skipping {pdf_path.name} as {output_json_path.name} already exists."
                )
                continue

            logger.info(f"Processing PDF: {pdf_path.name}")
            extractor = PDFExtractor()
            pdf_text = extractor.extract_text(pdf_path)

            analysis_result = analyzer.analyze_text(pdf_text)

            result = {
                "input_pdf": str(pdf_path.resolve()),
                "prompt": template.template.strip(),
                "summary": analysis_result["summary"],
                "used_tokens": analysis_result["used_tokens"],
            }

            analyzer.save_to_json(result, output_json_path)

            logger.info(f"Successfully processed and saved: {output_json_path.name}")

        except Exception as e:
            logger.error(f"Failed to process PDF '{pdf_path.name}': {e}")
            continue

    logger.info("Application processing completed.")


if __name__ == "__main__":
    load_dotenv()

    try:
        initial_config = load_configuration()
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        exit(1)

    setup_logging(
        log_file=initial_config.get("logging", {}).get("log_file", "app.log"),
        log_level=initial_config.get("logging", {}).get("log_level", "INFO"),
    )
    logger = logging.getLogger(__name__)

    try:
        main()
    except Exception as e:
        logger.critical(f"A critical error occurred during application execution: {e}")
        exit(1)
