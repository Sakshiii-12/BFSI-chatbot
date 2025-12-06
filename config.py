# config.py
APP_TITLE = "BFSI Personal Loan Assistant"

# Demo credentials (change if you want)
CUSTOMER_CREDENTIALS = {
    "customer@nbfc.com": "Customer789"
}

MANAGER_CREDENTIALS = {
    "manager@nbfc.com": "Manager456"
}

def validate_customer_login(email: str, password: str) -> bool:
    # Return True if credentials match a demo customer.
    if not email:
        return False
    return CUSTOMER_CREDENTIALS.get(email.strip().lower()) == (password or "")

def validate_manager_login(email: str, password: str) -> bool:
    # Return True if credentials match a demo manager.
    if not email:
        return False
    return MANAGER_CREDENTIALS.get(email.strip().lower()) == (password or "")
