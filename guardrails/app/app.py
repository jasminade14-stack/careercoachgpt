from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.policy import policy_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CareerCoach Guardrails")

class TextValidationRequest(BaseModel):
    text: str

class ValidationResponse(BaseModel):
    status: str
    is_valid: bool
    validated_text: Optional[str] = None
    violations: Optional[List[str]] = None

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "guardrails"}

@app.post("/validate_text", response_model=ValidationResponse)
def validate_text(payload: TextValidationRequest):
    """
    Validates text against career coaching policies.
    Blocks discriminatory or biased content.
    """
    text = payload.text
    
    logger.info(f"Validating text (length: {len(text)})")
    
    violations = policy_check(text)
    
    if violations:
        logger.warning(f"Policy violations detected: {violations}")
        return ValidationResponse(
            status="VIOLATION",
            is_valid=False,
            validated_text=None,
            violations=violations
        )
    
    logger.info("Text passed validation")
    return ValidationResponse(
        status="OK",
        is_valid=True,
        validated_text=text,
        violations=None
    )

# Backward compatibility - alte Route
@app.post("/validate_text_strict")
def validate_text_strict(payload: dict):
    """
    Strict mode - raises HTTPException on violation
    """
    text = payload.get("text")
    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Field 'text' must be a string.")

    violations = policy_check(text)
    if violations:
        raise HTTPException(status_code=400, detail={
            "error": "POLICY_VIOLATION",
            "violations": violations
        })

    return {
        "status": "OK",
        "validated_text": text
    }