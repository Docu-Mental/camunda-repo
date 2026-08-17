# Camunda 8 Documentation Workflow

## Overview

This project demonstrates an end-to-end documentation review and publishing workflow built with **Camunda 8**.

The workflow allows an author to:

1. Submit a Markdown document.
2. Automatically validate the document against a configurable list of prohibited terminology.
3. Correct the document if prohibited terminology is detected.
4. Submit the document for human review.
5. Approve or reject the document.
6. Publish an approved document and record its published URL.
7. Receive automated email notifications when correction or rejection is required.

The BPMN model is available here:
![BPMN model](/bpmn/BPMN.png "BPMN model")

The project is intended as a portfolio demonstration of BPMN modelling, Camunda Forms, document handling, Python workers, API integration, conditional process flows, and email automation.

---

## Architecture and Components

The project combines Camunda Cloud/SaaS components with a small Python worker running on the local development machine.

### Camunda 8 Cloud

The following components run in the **Camunda 8 SaaS cluster**:

- **BPMN process** — defines and orchestrates the complete documentation workflow.
- **Submit Document form** — allows the author to enter document metadata and upload a Markdown file.
- **Review Document form** — allows a reviewer to approve or reject the document and enter review comments.
- **Publish Document form** — displays the submitted document and its title and allows the publisher to enter the final published URL.
- **Camunda document storage** — stores the uploaded Markdown document and makes it available to the process and worker.
- **Job execution** — Camunda creates jobs for service tasks and the local worker consumes the document-validation job.
- **Email Connector** — sends correction and rejection notifications by SMTP.
- **Camunda Secrets** — securely stores the Gmail app password used by the Email Connector. The actual password is not stored in the BPMN model.

### Local development machine

The following components run locally:

- **Python terminology-validation worker** — uses the Camunda Orchestration SDK to poll for `validate-document` jobs, retrieve the uploaded document, inspect its contents, and complete the job with the validation results.
- **`prohibited-terms.json`** — an external, editable configuration file containing the prohibited terminology. Keeping the list outside the Python code means terminology can be changed without modifying the worker.
- **Python dependencies** — installed locally using `requirements.txt`.
- **Camunda Orchestration SDK** — installed locally and used by the Python worker to communicate with the Camunda 8 cluster.
- **`.env`** — local configuration containing the Camunda connection credentials. This file is excluded from source control and is never committed to GitHub.

### Source control

The project source files and BPMN/forms are stored in **GitHub**.

Credentials and other secrets are deliberately excluded from the repository.

---

## Main Workflow Paths

The BPMN process has three principal paths. (Note that the videos do not have sound.)

### 1. Invalid terminology detected

**[Watch the prohibited-term workflow video](videos/flow 1 - prohibited terminology detected - no audio.mp4)**

The author submits a Markdown document.

The Python worker:

1. Receives the `validate-document` job from Camunda.
2. Retrieves the uploaded document using the Camunda document API.
3. Reads the Markdown content.
4. Loads the prohibited terminology from `prohibited-terms.json`.
5. Checks the document for prohibited terms.
6. Sets the process variables `prohibitedTermsFound` and `terminologyValid`.

If prohibited terminology is found, the BPMN gateway follows the **No** path to **Request correction**.

An email is then sent to the author containing the prohibited term(s) that were detected.

---

### 2. Document fails review

**[Watch the document-rejection workflow video](videos/flow 2 - document fails review - no audio.mp4)**

If the document passes the terminology check, it proceeds to the **Review document** user task.

The reviewer can select **Rejected** and enter review comments.

The Review form stores:

- `approved = false`
- `reviewComments` — the reviewer's comments

The BPMN gateway follows the **No** path to **Notify author of rejection**.

An email is generated dynamically using the review comments and sent to the author explaining why the document was rejected.

The process then ends on the rejection path.

---

### 3. Document passes review

**[Watch the document-approval workflow video](videos/flow 2 - document passes review - no audio.mp4)**

If the reviewer selects **Approved**:

- `approved = true`

The BPMN gateway follows the **Yes** path to **Publish document**.

The Publish Document form:

- Displays the document title from the original submission.
- Provides a preview/download of the original uploaded Markdown document.
- Allows the publisher to enter the URL where the document has been published.

After the publisher completes the task, the process reaches the successful end event.

---

## Technologies

- Camunda 8
- BPMN 2.0
- Camunda Forms
- Camunda Connectors
- Camunda Document Handling
- Camunda Orchestration SDK for Python
- Python
- JSON
- Markdown
- SMTP / Gmail

## Security

No credentials or passwords are included in this repository.

The Gmail app password is stored as a **Camunda Secret** in the Camunda SaaS cluster. The local `.env` file containing Camunda credentials is excluded from Git using `.gitignore`.

## Project Structure

```text
.
├── BPMN.svg
├── bpmn/
│   └── documentation-process.bpmn
├── forms/
│   ├── submit-document.form
│   ├── review-document.form
│   └── publish-document.form
├── worker/
│   ├── validate_document.py
│   ├── prohibited-terms.json
│   └── requirements.txt
├── videos/
│   ├── invalid-term-detected.mp4
│   ├── document-fails-review.mp4
│   └── document-passes-review.mp4
├── screenshots/
│   ├── various
└── README.md
```
