import os
import json
import pytest
from stirlingpdf_assistant.utils.user_manager import UserManager

@pytest.fixture
def test_user_manager():
    """Fixture to set up and tear down a UserManager for tests."""
    test_file = "test_users.json"
    owner_id = 1144140918
    if os.path.exists(test_file):
        os.remove(test_file)
    
    manager = UserManager(test_file, owner_id)
    yield manager
    
    # Cleanup after the test
    if os.path.exists(test_file):
        os.remove(test_file)

def test_owner_always_added(test_user_manager):
    """The owner ID should always be in the authorized list."""
    assert test_user_manager.is_authorized(test_user_manager.owner_id)

def test_add_remove_user(test_user_manager):
    """Adding and removing a user should work correctly and persist."""
    new_id = 99887766
    
    # Add
    assert test_user_manager.add_user(new_id) is True
    assert test_user_manager.is_authorized(new_id) is True
    
    # Verify persistence by reloading a new manager instance
    reloaded_manager = UserManager(test_user_manager.file_path, test_user_manager.owner_id)
    assert reloaded_manager.is_authorized(new_id) is True
    
    # Remove
    assert test_user_manager.remove_user(new_id) is True
    assert test_user_manager.is_authorized(new_id) is False

def test_remove_owner_fails(test_user_manager):
    """The owner ID should be protected from removal."""
    owner_id = test_user_manager.owner_id
    assert test_user_manager.remove_user(owner_id) is False
    assert test_user_manager.is_authorized(owner_id) is True
