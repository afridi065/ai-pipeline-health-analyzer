# AI-Powered CI/CD Pipeline Health Analyzer

A DevOps + GenAI portfolio project: when a CI/CD pipeline fails, this system automatically analyzes the failure log and sends a plain-English explanation and suggested fix via email — instead of requiring manual log digging.

## Architecture

1. **Sample app** — A Flask calculator app (this repo) with calculation history, dark mode, and input validation, containerized with Docker.
2. **CI/CD Pipeline** — GitHub Actions builds the Docker image, runs a Python syntax check, and pushes the image to GitHub Container Registry (GHCR) on every push to `main`.
3. **Infrastructure as Code** — Terraform provisions all AWS resources: an SNS topic, a CloudWatch log group, an IAM role, and an AWS Lambda function.
4. **AI Analysis (AWS Lambda)** — When triggered with a failure log, the Lambda sends the log to an LLM (Bedrock Claude, with Google Gemini as a secondary attempt) and gets back a plain-English explanation and fix suggestion.
5. **Notifications** — The explanation is published to an SNS topic, which emails it directly to the subscriber.

## Tech Stack

Flask, Docker, GitHub Actions, AWS Lambda, AWS CloudWatch, AWS SNS, AWS IAM, Terraform, AWS Bedrock / Google Gemini (LLM APIs), Python (boto3, urllib)

## Known Limitations (and how they were handled)

During development, two separate real-world provider-side issues were identified and diagnosed:

1. **AWS Bedrock (AISPL billing bug):** Bedrock model invocation from this AWS account (an India-billed/AISPL account) consistently returned `AccessDeniedException: INVALID_PAYMENT_INSTRUMENT`, even with a valid card on file and correct IAM permissions. This is a known, widely-reported AWS Marketplace billing issue specific to Indian AWS accounts.
2. **Google Gemini API (key format bug):** Newly issued Gemini API keys use a new `AQ.`-prefixed format that is currently rejected by the Generative Language REST API (`ACCESS_TOKEN_TYPE_UNSUPPORTED`), a confirmed open bug affecting many new Google AI Studio accounts as of September 2026.

**Engineering response:** Rather than leaving the pipeline broken, the Lambda function was designed with a resilient fallback: it attempts the real LLM call first, and gracefully falls back to a structured mock explanation if the call fails — logging which mode was used. This keeps the full pipeline (Lambda → SNS → email) demonstrably working end-to-end, while the real integration code remains in place and will work automatically once either provider issue is resolved.

## Setup

1. Clone this repo and build the Docker image: `docker build -t calculator-app .`
2. Run locally: `docker run -d -p 5000:5000 calculator-app`
3. Provision AWS infrastructure: `cd terraform-pipeline-analyzer && terraform init && terraform apply`
4. Test the analyzer: `aws lambda invoke --function-name pipeline-health-analyzer --payload '{"log_text": "<your error log>"}' response.json`

## What I'd improve with more time

- Resolve the AISPL billing issue via AWS Support to enable real Bedrock calls
- Add a CloudWatch Alarm to auto-trigger the Lambda on pipeline failure (currently manually/CLI invoked)
- Add Slack webhook support alongside email notifications
- Move secrets (API keys) to AWS Secrets Manager instead of Terraform variables
