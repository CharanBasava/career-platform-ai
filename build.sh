#!/usr/bin/env bash

# Install Python dependencies
pip install -r requirements.txt

# Install wkhtmltopdf required for PDF generation
apt-get update
apt-get install -y wkhtmltopdf

# Download spaCy English model for resume parsing
python -m spacy download en_core_web_sm