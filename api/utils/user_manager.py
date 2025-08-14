# user_manager.py
import json
import os
from typing import Dict, List, Optional

class UserManager:
    def __init__(self, data_file: str = "users.json"):
        self.data_file = data_file
        self.users = self._load_users()
    
    def _load_users(self) -> List[Dict]:
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_users(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def create_user(self, user_data: Dict) -> Dict:
        user_id = len(self.users) + 1
        user = {
            "user_id": user_id,
            "name": user_data.get("name"),
            "group_size": user_data.get("group_size"),
            "preferred_environment": user_data.get("preferred_environment"),
            "budget_range": {
                "min": user_data.get("budget_min"),
                "max": user_data.get("budget_max")
            },
            "travel_dates": user_data.get("travel_dates")
        }
        self.users.append(user)
        self._save_users()
        return user
    
    def edit_profile(self, user_id: int, updates: Dict) -> Optional[Dict]:
        for user in self.users:
            if user["user_id"] == user_id:
                user.update(updates)
                self._save_users()
                return user
        return None
    
    def delete_user(self, user_id: int) -> bool:
        for i, user in enumerate(self.users):
            if user["user_id"] == user_id:
                del self.users[i]
                self._save_users()
                return True
        return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        for user in self.users:
            if user["user_id"] == user_id:
                return user
        return None