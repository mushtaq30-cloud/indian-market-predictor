from ..config import settings
import logging
from typing import List, Dict
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

def search_web_for_answer(query: str, max_results: int = 5) -> List[Dict]:
    """Search web using DuckDuckGo - COMPLETELY FREE"""
    try:
        results = []
        with DDGS() as ddgs:
            search_results = ddgs.text(
                keywords=query,
                region='in-en',
                safesearch='moderate',
                max_results=max_results
            )
            
            for r in search_results:
                results.append(r)
        
        logger.info(f"Found {len(results)} web results for: {query[:50]}")
        return results
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []

def get_ai_response(prompt: str, system_prompt: str) -> str:
    """Get AI response using configured provider"""
    try:
        if settings.AI_PROVIDER == "groq" and settings.GROQ_API_KEY:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content
        
        elif settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                system_instruction=system_prompt
            )
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 600
                }
            )
            
            return response.text
        
        elif settings.AI_PROVIDER == "huggingface" and settings.HUGGINGFACE_API_KEY:
            url = f"https://api-inference.huggingface.co/models/{settings.HUGGINGFACE_MODEL}"
            headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
            
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 600,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            return str(result)
        
        else:
            return "AI provider not configured. Please set up Groq, Gemini, or Hugging Face API key."
    
    except Exception as e:
        logger.error(f"AI response error: {e}")
        return f"Unable to generate AI response: {str(e)}"

async def chatbot_response(
    user_question: str,
    context: Dict = None
) -> Dict:
    """
    AI Chatbot with web search - COMPLETELY FREE
    """
    try:
        # Search web for relevant information
        search_query = f"India stock market {user_question}"
        search_results = search_web_for_answer(search_query, max_results=5)
        
        # Build web context
        web_context = ""
        if search_results:
            web_context = "\n\n".join([
                f"**Source {i+1}:** {r.get('title', 'N/A')}\n{r.get('body', 'N/A')[:400]}"
                for i, r in enumerate(search_results[:3])
            ])
        else:
            web_context = "No web results found. Provide general guidance."
        
        # Build market context
        market_context = ""
        if context:
            market_context = f"""
**Current Market Data (Live):**
- Gold: ₹{context.get('gold_price', 'N/A')}/10g
- Silver: ₹{context.get('silver_price', 'N/A')}/kg
- NIFTY 50: {context.get('nifty', 'N/A')}
- Sensex: {context.get('sensex', 'N/A')}
"""
        
        # Create comprehensive prompt
        system_prompt = """You are a helpful AI financial assistant specialized in Indian stock markets, gold, silver, and commodities.

Guidelines:
- Provide accurate, well-researched answers
- Cite sources when possible
- Include relevant data and facts
- Add disclaimers for investment advice
- Keep responses conversational but professional
- Be concise (200-250 words)"""

        user_prompt = f"""User Question: {user_question}

{market_context}

**Latest Information from Web:**
{web_context}

Based on the above information, provide a comprehensive answer to the user's question. Include:
1. Direct answer to their question
2. Supporting facts/data from web sources
3. Relevant market context if applicable
4. Any important disclaimers or warnings

Be helpful and informative!"""

        # Get AI response
        answer = get_ai_response(user_prompt, system_prompt)
        
        # Prepare sources
        sources = [
            {
                "title": r.get('title', 'N/A'),
                "url": r.get('href', '#'),
                "snippet": r.get('body', '')[:150] + "..."
            }
            for r in search_results[:3]
        ]
        
        logger.info(f"Chatbot response generated for: {user_question[:50]}")
        
        return {
            "answer": answer,
            "sources": sources,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return {
            "answer": f"I'm having trouble answering that question right now. Error: {str(e)}",
            "sources": [],
            "timestamp": datetime.now().isoformat()
        }

async def get_quick_tip(asset_type: str) -> str:
    """Generate quick trading tip for dashboard"""
    try:
        tips = {
            "gold": "Gold is a safe-haven asset. Watch RBI policy and rupee movements closely.",
            "silver": "Silver has industrial demand. Monitor global manufacturing data.",
            "stock": "Diversify across sectors. Don't put all eggs in one basket."
        }
        return tips.get(asset_type, "Always do your own research before investing.")
    except:
        return "Market conditions can change rapidly. Stay informed."
