# Purpose

Trying to gather documents and expenses for tax season is a tedious task. Knowing what is deductible and ensuring that receipts are kept in neat order requires significant time and effort. The purpose of this project is to automate the ingestion, classification, extraction, and organization of tax-deductible receipts and financial documents from multiple email providers.

## The system will:
- Connect to multiple email providers
- Detect receipt and financial-document-related emails
- Extract structured financial information
- Classify tax relevance
- Store documents and metadata in an organized manner
- Support long-term retrieval and review for tax filing


## Tax Deductible Expenses
### Personal Income
- Medical expenses
- RRSP contribution receipts
- TFSA / FHSA contribution receipts
- Professional membership / union dues
- Moving costs
- Charity donations
- Rent receipts
- Utilities
- Gas
- Hydro
- Internet
- Renters insurance
- Pet insurance
- Travel / lodging

### Property Income
- Rental income
- Utilities
- Property tax
- House insurance
- Maintenance
- Repairs

## System Requirements

Email Service Agnostic: The system must support multiple email providers through a shared internal data model.

Requirements:
- Multiple email platforms must be supported
- A normalized email model must exist
- Provider-specific adapters must transform external API data into the canonical model