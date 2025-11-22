import json
import os
from datetime import datetime
from typing import List, Dict, Any

class MockDatabase:
    """Mock database for prototype - replace with real DB in production"""
    
    def __init__(self):
        self.users_file = "data/users.json"
        self.analyses_file = "data/analyses.json"
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensure database files exist"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.analyses_file):
            with open(self.analyses_file, 'w') as f:
                json.dump({}, f)
    
    def save_analysis(self, user_id: str, analysis_data: Dict[str, Any]) -> str:
        """Save analysis results"""
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        with open(self.analyses_file, 'r') as f:
            analyses = json.load(f)
        
        analysis_data['analysis_id'] = analysis_id
        analysis_data['user_id'] = user_id
        analysis_data['timestamp'] = datetime.now().isoformat()
        
        if user_id not in analyses:
            analyses[user_id] = []
        
        analyses[user_id].append(analysis_data)
        
        with open(self.analyses_file, 'w') as f:
            json.dump(analyses, f, indent=2)
        
        return analysis_id
    
    def get_user_analyses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all analyses for a user"""
        with open(self.analyses_file, 'r') as f:
            analyses = json.load(f)
        
        return analyses.get(user_id, [])
    
    def get_analysis(self, user_id: str, analysis_id: str) -> Dict[str, Any]:
        """Get specific analysis"""
        analyses = self.get_user_analyses(user_id)
        for analysis in analyses:
            if analysis.get('analysis_id') == analysis_id:
                return analysis
        return {}

# Global database instance
db = MockDatabase()