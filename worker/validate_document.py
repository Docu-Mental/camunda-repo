import asyncio
import json
from pathlib import Path

from camunda_orchestration_sdk import (
    CamundaAsyncClient,
    ConnectedJobContext,
    WorkerConfig,
)


# Load prohibited terminology when worker starts
with open(
    Path(__file__).parent / "prohibited-terms.json",
    encoding="utf-8"
) as f:
    prohibited_terms = json.load(f)["prohibitedTerms"]


async def validate_document(job: ConnectedJobContext) -> dict[str, object]:
    variables = job.variables.to_dict()

    # Get the document reference from the process variables
    document_info = variables["documentFile"][0]

    document_id = document_info["documentId"]
    store_id = document_info["storeId"]
    content_hash = document_info["contentHash"]

    # Retrieve the document using the worker's existing client
    document = await job.client.get_document(
        document_id=document_id,
        store_id=store_id,
        content_hash=content_hash,
    )

    # Decode Markdown
    content = document.payload.read().decode("utf-8")

    # Check for prohibited terminology (case-insensitive)
    content_lower = content.lower()

    found_terms = [
        term
        for term in prohibited_terms
        if term.lower() in content_lower
    ]

    terminology_valid = len(found_terms) == 0

    print("\nDocument validation")
    print("-------------------")
    print(f"Title: {variables.get('title')}")
    print(f"File: {document_info['metadata']['fileName']}")
    print(f"Prohibited terms found: {found_terms}")
    print(f"Terminology valid: {terminology_valid}")

    return {
        "terminologyValid": terminology_valid,
        "prohibitedTermsFound": found_terms,
    }


async def main() -> None:
    async with CamundaAsyncClient() as client:
        config = WorkerConfig(
            job_type="validate-document",
            job_timeout_milliseconds=30_000,
        )

        client.create_job_worker(
            config=config,
            callback=validate_document,
        )

        print("Worker started.")
        print("Waiting for validate-document jobs...")

        await client.run_workers()


if __name__ == "__main__":
    asyncio.run(main())