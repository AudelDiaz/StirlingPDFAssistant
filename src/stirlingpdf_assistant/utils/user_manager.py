import os
import json
import logging
from typing import Set

class UserManager:
    """Manages persistent list of authorized users."""
    def __init__(self, file_path: str, owner_id: int):
        self.file_path = file_path
        self.owner_id = owner_id
        self.allowed_ids: Set[int] = set()
        self.settings = {}
        self.load()

    def load(self):
        """Load allowed IDs from JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    self.allowed_ids = set(data.get("allowed_ids", []))
                    self.settings = data.get("settings", {})
            except Exception as e:
                logging.error(f"Error loading users file: {e}")
        
        # Always ensure the owner is authorized
        if self.owner_id:
            self.allowed_ids.add(self.owner_id)

    def save(self):
        """Save current allowed IDs to JSON file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump({
                    "allowed_ids": list(self.allowed_ids),
                    "settings": self.settings
                }, f)
        except Exception as e:
            logging.error(f"Error saving users file: {e}")

    def add_user(self, user_id: int) -> bool:
        if user_id not in self.allowed_ids:
            self.allowed_ids.add(user_id)
            self.save()
            return True
        return False

    def remove_user(self, user_id: int) -> bool:
        if user_id == self.owner_id:
            return False # Cannot remove the owner
        if user_id in self.allowed_ids:
            self.allowed_ids.remove(user_id)
            self.save()
            return True
        return False

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self.allowed_ids

    # --- Settings Management ---
    
    def get_setting(self, key: str, default: any = None) -> any:
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: any):
        self.settings[key] = value
        self.save()
