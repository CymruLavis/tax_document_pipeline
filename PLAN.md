# Tax Receipt Email Extraction System

## Purpose

Trying to gather documents and expenses for tax season is a tedious task. Knowing what is deductible and ensuring that receipts are kept in neat order requires significant time and effort.

The purpose of this project is to:
- Automate tax receipt collection
- Reduce manual tax preparation work
- Organize financial documents automatically
- Extract structured financial information from receipts and invoices
- Classify tax-deductible expenses
- Centralize documents from multiple email providers

---

# Background

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
- Lawn maintenance
- Repairs

---

# Goals

## Primary Goals
- Automatically scan emails for tax-related documents
- Download and organize receipts
- Extract structured metadata from receipts
- Categorize deductible expenses
- Reduce tax-season preparation time

## Secondary Goals
- Learn workflow orchestration
- Explore document intelligence systems
- Experiment with AI-assisted extraction and classification
- Build a self-hosted personal automation system

---

# Non-Goals

## Initial Non-Goals
- Full accounting software replacement
- Direct tax filing integration
- Real-time bookkeeping
- Multi-user support
- Cloud-hosted deployment

---

# System Requirements

## Email Service Agnostic

The system must support multiple email providers through a shared internal data model.

Requirements:
- Multiple email platforms must be supported
- A canonical (normalized) email model must exist
- Provider-specific adapters must transform external API data into the canonical model

---

## Desired Extracted Data

The system should extract:
- Date
- Vendor
- Cost
- Description
- Currency
- Tax category
- Confidence score

---

# System Architecture

```text
Temporal Scheduler
        ↓
Email Connectors / Email Ingestion
        ↓
Canonical Email Normalization
        ↓
Receipt Detection / Tax Classification
        ↓
Document Extraction / Parsing
        ↓
Storage Layer
        ↓
Review / Export Layer
```
# Classification Model
- SVM (Support Vector Machine)
  - lightweight
  - fast inference
  - cheap to train
  - won't need GPU
  - criteria for the binary classification of tax deductible or not is highly structured with aviailable information that can make decisions very easy
- We want to tune for high recall with a slightly lower precision
  - This will minimize false negatives meaning the chances of missing an email that is tax deductible will be lower
  - A slightly lower precision means that the chance for a false positive is higher (a non tax deductible email is classified as tax deductible)
    - but this is easy to remedy in the future. Its much more annoying to have to go searching for a missed document

# Data Structures
## Storage Table
OAuth Token Lifecycle
|token_id   | access_token  | refresh_token | expiry    | provider      |
-------------------------------------------------------------------------
| UUID      | str           | str           | datetime  | str           |

Email File Stroage
| id    | provider      | subject       | sender_name   | sender_email  | recieved_at   | body_text     | attatchment_ids       | raw_payload   | file_destination      |
-----------------------------------------------------------------------------------------------------------------------------------------
| str   | str           | str           | str           | str           | datetime      | str           | list[str]                   | dict |  str     |

Reciept Details
| id    | vendor       | total_cost    | date_of_transaction |
-----------------------------------------------------------------
| str   | str           | float         | datetime              |

## Objects
Normalized Email Object
```python
class CanonicalEmail:
    id: str
    provider: str

    subject: str
    sender_email: str
    sender_name: str | None

    received_at: datetime

    body_text: str

    attachment_ids: list[str]

    raw_payload: dict
```



# Order of Operations
1. Create Gmail Client
   1. Oauth App
   2. Token Managment
   3. Gmail Specific Data Objects
   4. Client activities for ingesting data
2. Create Classification Model
   1. Binary Classification for email ingestion
      1. Generate dataset from emails
      2. Create testing pipeline
      3. Linear SVM tuning to determine the best parameters
      4. Final Train
      5. Export trained model
   2. Multi Class Classifier for storage location classification
      1. Generate dataset from emails
      2. Create testing pipeline
      3. Logistic Regression with softmax tuning to determine the best parameters
         1. {
                sender_domain: str
                has_pdf_attachment: bool
                num_attachments: int
                contains_amount: bool
                text: subject + body + attachment_text
                vendor_feature: One hot encoded vector of known vendors. Need to create vendor mapping and extract names/domains to accuratley normalize incoming vendors
                }
      4. Final Train
      5. Export trained model
3. Create Storage system
   1. Generate SQL Alchemy tables
   2. create models for transporting raw data to and from the table
   3. create sync for updating tables if a filepath is manually deleted
4. Temporal workflow
   1. scheduled workflow
   2. activities for ingesting from each source
   3. activities for completing transformations, normalizations, ML inference, sorting, etc
