#!/bin/bash

# Development helper to regenerate the PDF documentation from the LaTeX source.

DOC_DIR="doc/language"
DOC_FILE="specification.tex"
PDF_FILE="specification.pdf"

# Run pdflatex twice to ensure TOC and links are correct.
pdflatex -interaction=nonstopmode -output-directory="$DOC_DIR" "$DOC_DIR/$DOC_FILE" > /dev/null
pdflatex -interaction=nonstopmode -output-directory="$DOC_DIR" "$DOC_DIR/$DOC_FILE" > /dev/null

if [ $? -eq 0 ]; then
    echo "Documentation generated successfully: $DOC_DIR/$PDF_FILE"

    # Cleanup auxiliary files.
    rm -f "$DOC_DIR"/*.aux "$DOC_DIR"/*.fdb_latexmk "$DOC_DIR"/*.fls "$DOC_DIR"/*.log "$DOC_DIR"/*.out "$DOC_DIR"/*.toc
    echo "Cleanup complete."
else
    echo "Error: Failed to generate documentation."
    exit 1
fi
