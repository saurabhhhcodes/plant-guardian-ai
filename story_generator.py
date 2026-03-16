import json
from typing import Dict, Any, List

class StoryGenerator:
    """Helper class to structure plant recovery stories for multimodal output."""
    
    @staticmethod
    def parse_recovery_data(ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured infographic and storyboard data.
        
        Expected output format from Gemini (requested via prompt):
        {
          "infographic": {
            "title": "...",
            "steps": [{"day": 1, "action": "...", "icon": "..."}]
          },
          "video_storyboard": [
            {"scene": 1, "visual": "...", "narration": "..."}
          ]
        }
        """
        try:
            # Find the JSON block if it exists
            start = ai_response.find('{')
            end = ai_response.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = ai_response[start:end]
                return json.loads(json_str)
            return {"error": "Could not parse structured data from AI response"}
        except Exception as e:
            return {"error": f"JSON parsing failed: {str(e)}"}

    @staticmethod
    def get_video_storyboard_html(storyboard: List[Dict[str, Any]]) -> str:
        """Generate HTML representation for the video storyboard carousel/list."""
        html = '<div style="display: flex; overflow-x: auto; gap: 10px; padding: 10px;">'
        for scene in storyboard:
            html += f"""
            <div style="min-width: 200px; background: #262730; border-radius: 10px; padding: 15px; border: 1px solid #4a4a4a;">
                <h4 style="color: #4CAF50; margin-top: 0;">Scene {scene.get('scene', '?')}</h4>
                <p><strong>Visual:</strong> {scene.get('visual', '')}</p>
                <p style="font-style: italic;">"{scene.get('narration', '')}"</p>
            </div>
            """
        html += '</div>'
        return html
