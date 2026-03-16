try:
    from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
except ImportError:
    pipeline = None
    AutoModelForCausalLM = None
    AutoTokenizer = None
import os
from typing import Dict, List, Optional, Any
import json
import base64
import numpy as np
from PIL import Image
import io
import cv2

# LangChain imports


from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
try:
    from langchain_together import TogetherLLM
except ImportError:
    TogetherLLM = None
try:
    from langchain_community.llms import Ollama
except ImportError:
    Ollama = None
try:
    from langchain_cohere import ChatCohere
except ImportError:
    ChatCohere = None
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None
try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None
try:
    from langchain_perplexity import ChatPerplexity
except ImportError:
    ChatPerplexity = None
try:
    from langchain_huggingface import HuggingFaceHub
except ImportError:
    HuggingFaceHub = None
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage, SystemMessage

# ADK imports
import sys
if "/home/saurabh/adk-python/src" not in sys.path:
    sys.path.append("/home/saurabh/adk-python/src")

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

# Local imports
from plant_analysis import PlantImageAnalyzer
from weather_service import WeatherService

class PlantCareAgent:
    """Plant Care Agent that works with multiple LLM providers."""
    
    def __init__(self, api_key: str = None):
        """Initialize the PlantCareAgent.
        
        Args:
            api_key: API key for the Gemini provider.
        """
        self.api_key = api_key
        self.provider = "gemini"
        self.analyzer = PlantImageAnalyzer()
        self.adk_agent = self._init_adk_agent()
        self.runner = Runner(
            app_name="PlantGuardianApp",
            agent=self.adk_agent,
            session_service=InMemorySessionService()
        )
    
    def _init_adk_agent(self) -> Agent:
        """Initialize the ADK Agent with tools and instructions."""
        return Agent(
            name="PlantGuardian",
            model="gemini-2.5-flash",
            instruction="""
            You are PlantGuardian, a premium multimodal AI plant doctor.
            Your goal is to provide expert diagnosis and recovery plans for plants.
            
            When a user uploads an image, you must:
            1. Identify the plant species.
            2. Analyze health using vision and provided context (location/weather).
            3. Generate a recovery infographic roadmap and a video storyboard.
            
            Always respond in a professional, encouraging, and highly detailed manner.
            If you need weather data, use the weather tool if a location is provided.
            """,
            description="Expert plant care assistant with multimodal vision and storytelling capabilities."
        )
    async def analyze_image(self, image_data: str, location: str = None, weather: Dict = None, is_farm: bool = False) -> Dict[str, Any]:
        """
        Analyze a plant image using ADK Runner and multimodal reasoning.
        
        Args:
            image_data: Base64 encoded image string
            location: Optional location name
            weather: Optional weather data dictionary
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Prepare context for ADK
            weather_data = weather
            if not weather_data and location:
                weather_data = WeatherService.get_weather(location)
            
            # Identify plant species and diagnose with multimodal reasoning
            # We use the specialized _diagnose_multimodal helper for now 
            # to maintain the complex JSON structure needed by the UI
            diagnosis_data = self._diagnose_multimodal(image_data, location, weather_data, is_farm)
            species = diagnosis_data.get('species', 'Unknown Plant')

            # Numerical stats (keep OpenCV for technical USP)
            img_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            health_analysis = self.analyzer.analyze_plant_health(img)
            disease_analysis = self.analyzer.detect_diseases(img)
            
            summary = self._generate_analysis_summary(health_analysis, disease_analysis)
            summary['diagnosis'] = diagnosis_data.get('diagnosis', 'No diagnosis available')
            summary['weather_context'] = diagnosis_data.get('weather_context', 'No weather context')
            
            recovery_story = diagnosis_data.get('recovery_story', {})
            
            return {
                'status': 'success',
                'health_analysis': health_analysis,
                'disease_analysis': disease_analysis,
                'summary': summary,
                'recovery_story': recovery_story,
                'species': species,
                'message': 'Advanced ADK-powered diagnosis complete.'
            }
        except Exception as e:
            import traceback
            return {
                'status': 'error',
                'message': f'Error in ADK diagnosis: {str(e)}'
            }

    def _diagnose_multimodal(self, image_data: str, location: str = None, weather: Dict = None, is_farm: bool = False) -> Dict[str, Any]:
        """Perform multimodal diagnosis using Gemini 1.5 Pro with weather and location context."""
        try:
            weather_str = ""
            if weather:
                weather_str = f"""
                Current Weather in {location}:
                - Temperature: {weather.get('temp_C')}C
                - Humidity: {weather.get('humidity')}%
                - Condition: {weather.get('weatherDesc')}
                - Rainfall: {weather.get('precipMM')}mm
                """
            
            # Fetch regional soil data
            soil_context = WeatherService.get_soil_insights(location) if location else "General loam context."
            
            farm_context = ""
            if is_farm:
                farm_context = """
                AGRICULTURAL FARM MODE ACTIVE:
                - Analyze for large-scale crop issues (Monoculture pests, irrigation uniformity).
                - Consider mineral runoff and regional soil salinity.
                - Suggest tractor-accessible or drone-based remediation if applicable.
                - Focus on yield impact.
                """

            prompt = f"""
            Identify the plant species and diagnose its health from this image.
            
            {weather_str}
            Location: {location if location else "Unspecified"}
            
            Contextual Requirements:
            1. Consider typical regional soil characteristics for {location if location else "the user's region"} (e.g., pH, texture, mineral content).
            2. Analyze how the local climate and soil conditions interact with this specific plant species.
            3. Provide a expert-level diagnosis based on the visual symptoms in the image AND the provided environmental context.

            Provide the output in the following JSON format:
            {{
                "species": "Scientific and Common Name",
                "diagnosis": "Detailed breakdown of health issues, including soil/climate factors",
                "recovery_story": {{
                    "infographic": {{
                        "title": "Plant Recovery Roadmap",
                        "steps": [
                            {{"day": 1, "action": "Immediate Action", "icon": "emoji"}},
                            {{"day": 3, "action": "Intermediate Care", "icon": "emoji"}},
                            {{"day": 7, "action": "Long-term Maintenance", "icon": "emoji"}}
                        ]
                    }}
                }}
            }}
            
            Be professional, highly specific, and actionable. Avoid generic advice.
            """

            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Prepare image part
            img_part = {
                "mime_type": "image/jpeg",
                "data": base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
            }
            
            response = model.generate_content(
                [prompt, img_part],
                generation_config={"response_mime_type": "application/json"}
            )
            
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in multimodal diagnosis: {e}")
            return {
                "species": "Unknown Plant",
                "diagnosis": "Failed to generate diagnosis.",
                "weather_context": "No context available.",
                "recovery_story": {}
            }

    def _generate_analysis_summary(self, health_analysis: Dict, disease_analysis: Dict) -> Dict:
        """Generate a summary of the plant health analysis.
        
        Args:
            health_analysis: Dictionary containing health metrics
            disease_analysis: Dictionary containing disease metrics
            
        Returns:
            Dictionary with analysis summary
        """
        # Determine overall health status
        health_score = health_analysis.get('healthy_percentage', 0)
        
        if health_score > 70:
            health_status = "Healthy"
            health_emoji = "🟢"
        elif health_score > 40:
            health_status = "Moderately Healthy"
            health_emoji = "🟡"
        else:
            health_status = "Unhealthy"
            health_emoji = "🔴"
        
        # Check for disease indicators
        disease_detected = False
        disease_warnings = []
        
        for disease, percentage in disease_analysis.items():
            if isinstance(percentage, (int, float)) and percentage > 10:
                disease_detected = True
                disease_name = disease.replace('_', ' ').title()
                disease_warnings.append(f"{disease_name}: {percentage:.1f}%")
        
        # Create summary dictionary
        summary = {
            'health_status': f"{health_emoji} {health_status}",
            'health_score': f"{health_score:.1f}%",
            'yellow_leaves': f"{health_analysis.get('yellow_percentage', 0):.1f}%",
            'brown_leaves': f"{health_analysis.get('brown_percentage', 0):.1f}%",
            'disease_detected': disease_detected,
            'disease_warnings': disease_warnings,
            'timestamp': self._get_current_timestamp()
        }
        
        return summary
    
    def _identify_plant_species(self, image_data: str) -> str:
        """Identify the plant species using the LLM."""
        try:
            # Set a flag to indicate a vision model is needed
            self._is_vision_request = True
            # Create a prompt for the LLM
            prompt = "Identify the plant species in this image. Provide the common and scientific name."
            
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            img_part = {"mime_type": "image/jpeg", "data": base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)}
            response = model.generate_content([prompt, img_part])
            return response.text.strip()
        except Exception:
            return "Could not identify plant species."
        finally:
            # Reset the flag
            self._is_vision_request = False

    def _generate_care_recommendations(self, health_analysis: Dict, disease_analysis: Dict, species: str) -> List[str]:
        """Generate care recommendations using the LLM.
        
        Args:
            health_analysis: Dictionary containing health metrics
            disease_analysis: Dictionary containing disease metrics
            species: The identified plant species
            
        Returns:
            List of care recommendations
        """
        # Create a prompt for the LLM
        prompt = f"""
        Based on the following health analysis for a {species} plant, provide 3-5 specific care recommendations:
        
        Health Analysis:
        - Healthy percentage: {health_analysis.get('healthy_percentage', 0):.1f}%
        - Yellowing percentage: {health_analysis.get('yellow_percentage', 0):.1f}%
        - Browning percentage: {health_analysis.get('brown_percentage', 0):.1f}%
        
        Disease Analysis:
        {disease_analysis}
        
        Please provide actionable recommendations that address the specific issues detected.
        Focus on watering, lighting, fertilizing, and any disease treatment if needed.
        """
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            recommendations = response.text.strip().split('\n')
            # Filter out empty lines and return as list
            return [rec.strip() for rec in recommendations if rec.strip()]
        except Exception as e:
            # Fallback to default recommendations if LLM fails
            return self._get_default_recommendations(health_analysis, disease_analysis)
    
    def _get_default_recommendations(self, health_analysis: Dict, disease_analysis: Dict) -> List[str]:
        """Get default care recommendations when LLM is not available.
        
        Args:
            health_analysis: Dictionary containing health metrics
            disease_analysis: Dictionary containing disease metrics
            
        Returns:
            List of care recommendations
        """
        recommendations = []
        
        # Watering recommendations
        if health_analysis.get('yellow_percentage', 0) > 30:
            recommendations.append("Check watering schedule - yellowing leaves may indicate overwatering.")
        
        # Nutrient recommendations
        if health_analysis.get('brown_percentage', 0) > 20:
            recommendations.append("Consider fertilizing - browning leaves may indicate nutrient deficiency.")
        
        # Disease recommendations
        disease_detected = any(percentage > 10 for key, percentage in disease_analysis.items() if key.endswith('_percentage'))
        if disease_detected:
            recommendations.append("Treat for detected diseases to prevent further spread.")
        
        # Default care tips
        if not recommendations:
            recommendations.extend([
                "Your plant looks healthy! Continue with your current care routine.",
                "Regularly check for pests and remove dead leaves.",
                "Ensure proper drainage to prevent root rot."
            ])
        
        return recommendations
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def chat(self, message: str, chat_history: list = None) -> str:
        """Process a chat message using ADK Runner."""
        try:
            # In a real ADK app, we'd use sessions, but for Streamlit 
            # we can use the invoke method for stateless-like turns 
            # or pass the history as events.
            from google.genai import types
            
            app_name = self.runner.app_name
            user_id = "default_user"
            session_id = "chat_session"

            # Ensure session exists for ADK
            session = await self.runner.session_service.get_session(
                app_name=app_name, 
                user_id=user_id, 
                session_id=session_id
            )
            if not session:
                await self.runner.session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )

            response = self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=message)])
            )
            
            # Extract text from response events
            full_text = ""
            async for event in response:
                if hasattr(event, "content") and event.content:
                    if isinstance(event.content, str):
                        full_text += event.content
                    elif hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text"):
                                full_text += part.text
                elif hasattr(event, "text") and event.text:
                    full_text += event.text
            
            return full_text if full_text else "I am processing your request..."
        except Exception as e:
            return f"ADK Error: {str(e)}"
    
    def get_care_instructions(self, plant_type: str) -> str:
        """Get care instructions for a specific plant type.
        
        Args:
            plant_type: Name of the plant species
            
        Returns:
            Care instructions as a string
        """
        # Create a prompt for the LLM
        prompt = f"""
        Provide care instructions for a {plant_type} plant. Include information about:
        - Watering needs
        - Light requirements
        - Soil preferences
        - Temperature and humidity preferences
        - Fertilization schedule
        - Common problems and solutions
        
        Format the response as a clear, structured guide.
        """
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating care instructions: {str(e)}"

# For testing
if __name__ == "__main__":
    # This is just for testing purposes
    agent = PlantCareAgent()
    print("Plant Care Agent initialized successfully!")