import os
import pytest
from dotenv import load_dotenv

load_dotenv()

def test_parsing_logic():
    """Verify that the ALLOWED_USER_IDS string parsing logic is solid."""
    # Add a mock ID string to the testing context
    test_ids_str = "111111111, 98765432, abc, 123"
    
    parsed_ids = [
        int(uid.strip()) 
        for uid in test_ids_str.split(",") 
        if uid.strip().isdigit()
    ]
    
    # Assertions
    assert 111111111 in parsed_ids
    assert 98765432 in parsed_ids
    assert 123 in parsed_ids
    assert "abc" not in parsed_ids
    assert len(parsed_ids) == 3

def test_actual_env_owner_id():
    """Verify that the .env BOT_OWNER_ID is a valid numeric string if set."""
    owner_id_str = os.getenv("BOT_OWNER_ID", "")
    if not owner_id_str:
        pytest.skip("BOT_OWNER_ID not set in .env")
    assert owner_id_str.isdigit(), f"BOT_OWNER_ID must be numeric, got {owner_id_str!r}"
