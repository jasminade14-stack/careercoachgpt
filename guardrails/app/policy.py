import re

# Diskriminierende Patterns
BANNED_PATTERNS = [
    "because you are a woman",
    "because you are a man",
    "because you are muslim",
    "because you are christian",
    "because of your ethnicity",
    "because of your race",
    "because of your gender",
    "because of your age",
    "because of your disability",
    "due to your religion",
]

# PII Patterns
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
}

def policy_check(text: str) -> list[str]:
    """
    Checks text for policy violations:
    1. Discriminatory language
    2. PII leakage
    3. Inappropriate content
    """
    lower = text.lower()
    violations = []
    
    # 1. Check discriminatory patterns
    for pattern in BANNED_PATTERNS:
        if pattern in lower:
            violations.append(f"Discriminatory reasoning detected: '{pattern}'")
    
    # 2. Check for PII
    for pii_type, regex in PII_PATTERNS.items():
        if re.search(regex, text):
            violations.append(f"PII detected: {pii_type}")
    
    # 3. Check for unprofessional language (optional)
    unprofessional_words = ['stupid', 'dumb', 'idiot', 'useless']
    found_unprofessional = [word for word in unprofessional_words if word in lower]
    if found_unprofessional:
        violations.append(f"Unprofessional language: {', '.join(found_unprofessional)}")
    
    return violations