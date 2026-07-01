# GovDocs-AI

> An AI-powered document assistant that helps users understand U.S. government documents in plain English.

## Overview

Government paperwork can be difficult to understand, especially for immigrants, international students, and first-time applicants. **GovDocs-AI** is designed to simplify that experience by analyzing official government documents, extracting important information, identifying deadlines, and providing explanations backed by official government resources.

The initial MVP focuses on **USCIS documents** commonly encountered by international students and immigrants.

## Features (MVP)

* Upload USCIS documents (PDF or image)
* OCR-powered text extraction
* Automatic document classification
* Plain-English summaries
* Deadline and appointment detection
* Required action extraction
* Links to official USCIS resources
* AI-powered Q&A grounded in official documentation
* Structured document metadata extraction

## Planned Document Support

* Form I-20
* Form I-94
* Form I-797 (Notice of Action)
* Form I-766 (Employment Authorization Document)

Future releases may support documents from:

* IRS
* DMV
* FAFSA
* Social Security Administration
* Medicare
* Department of Veterans Affairs

## Tech Stack

### Frontend

* Next.js
* React
* TypeScript

### Backend

* FastAPI
* Python

### AI & Data

* OpenAI API
* OCR (Google Document AI or AWS Textract)
* Retrieval-Augmented Generation (RAG)
* PostgreSQL
* pgvector

## Project Goals

This project aims to:

* Simplify government paperwork using AI
* Help users understand official documents without replacing professional legal advice
* Reduce confusion around immigration and government processes
* Build a scalable platform that can support multiple U.S. government agencies

## Repository Structure

```text
docs/          Project documentation
data/          Sample documents and labels
prompts/       AI prompts
frontend/      Web application (planned)
backend/       API and AI services (planned)
```

## Current Status

🚧 Early Development

The current focus is:

* Defining the MVP
* Collecting sample USCIS documents
* Designing the system architecture
* Creating structured extraction schemas
* Building a labeled document dataset

## Disclaimer

GovDocs-AI is intended for informational purposes only.

It does **not** provide legal, tax, financial, or immigration advice. Users should always verify information using official government resources or consult a qualified professional when necessary.

## License

This project is currently under active development.
