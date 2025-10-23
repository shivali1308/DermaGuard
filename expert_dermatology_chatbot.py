from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

print("🚀 Starting Dermaguard AI with Groq Cloud API...")

# Groq API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"
MODEL_NAME = "llama3-8b-8192"

# Enhanced dermatology knowledge base with more detail
DERMATOLOGY_KNOWLEDGE = {
    "skin_rash": {
        "description": "A skin rash is any area of irritated or swollen skin. Rashes can be itchy, painful, red, or cause blisters.",
        "common_causes": [
            "Contact dermatitis (from irritants like poison ivy, cosmetics, or metals)",
            "Eczema (atopic dermatitis) - dry, itchy patches often in skin folds",
            "Psoriasis - thick red patches with silvery scales",
            "Hives (urticaria) - raised, itchy welts from allergic reactions",
            "Viral infections like measles or chickenpox",
            "Fungal infections like ringworm",
            "Heat rash (prickly heat)"
        ],
        "treatment": [
            "Identify and avoid triggers/allergens",
            "Use cool compresses to relieve itching",
            "Apply over-the-counter hydrocortisone cream",
            "Use fragrance-free moisturizers",
            "Take antihistamines for allergic rashes",
            "Keep the area clean and dry"
        ],
        "when_to_see_doctor": [
            "Rash covers large area of body",
            "Fever accompanies the rash",
            "Rash appears infected (pus, yellow crust)",
            "Rash doesn't improve in 2-3 days",
            "You have difficulty breathing or swallowing"
        ]
    },
    "itching": {
        "description": "Itching (pruritus) is an uncomfortable sensation that makes you want to scratch.",
        "common_causes": [
            "Dry skin (xerosis) - most common cause",
            "Eczema or atopic dermatitis",
            "Allergic reactions",
            "Insect bites or stings",
            "Fungal infections",
            "Psoriasis",
            "Liver or kidney disease (if widespread)",
            "Medication reactions"
        ],
        "treatment": [
            "Moisturize regularly with fragrance-free creams",
            "Take lukewarm (not hot) showers",
            "Use gentle, soap-free cleansers",
            "Apply cool compresses to itchy areas",
            "Use over-the-counter hydrocortisone cream",
            "Take oral antihistamines like cetirizine or loratadine",
            "Wear loose, cotton clothing"
        ],
        "when_to_see_doctor": [
            "Itching lasts more than 2 weeks",
            "Itching affects your entire body",
            "Itching is severe and disrupts sleep",
            "You have other symptoms like weight loss, fatigue, or fever"
        ]
    },
    "acne": {
        "description": "Acne occurs when hair follicles become plugged with oil and dead skin cells, causing pimples, blackheads, and whiteheads.",
        "types": [
            "Whiteheads (closed plugged pores)",
            "Blackheads (open plugged pores)",
            "Papules (small red, tender bumps)",
            "Pustules (papules with pus at tips)",
            "Nodules (large, painful lumps under skin)",
            "Cysts (painful, pus-filled lumps under skin)"
        ],
        "treatment": [
            "Wash face twice daily with gentle cleanser",
            "Use over-the-counter treatments with benzoyl peroxide or salicylic acid",
            "Avoid picking or squeezing pimples",
            "Use non-comedogenic (won't clog pores) products",
            "Shampoo regularly if you have oily hair",
            "Avoid touching your face throughout the day"
        ],
        "when_to_see_doctor": [
            "Over-the-counter products don't help after 2-3 months",
            "Acne is severe with cysts and nodules",
            "Acne is causing scarring or dark spots",
            "Acne is affecting your self-esteem"
        ]
    },
    "sunburn": {
        "description": "Sunburn is red, painful skin that feels hot to the touch, caused by too much exposure to ultraviolet (UV) light.",
        "symptoms": [
            "Pinkness or redness",
            "Skin that feels warm or hot to touch",
            "Pain, tenderness, and itching",
            "Swelling",
            "Small fluid-filled blisters",
            "Headache, fever, nausea if severe"
        ],
        "treatment": [
            "Take cool baths or showers",
            "Apply aloe vera or moisturizer",
            "Take ibuprofen or aspirin for pain and inflammation",
            "Drink extra water to prevent dehydration",
            "Don't break blisters - let them heal naturally",
            "Use hydrocortisone cream for itching",
            "Stay out of the sun while healing"
        ],
        "prevention": [
            "Use broad-spectrum sunscreen SPF 30+",
            "Reapply sunscreen every 2 hours and after swimming",
            "Wear protective clothing, hats, and sunglasses",
            "Seek shade between 10 AM and 4 PM",
            "Avoid tanning beds"
        ]
    }
}

class GroqDermatologyAI:
    def __init__(self):
        self.conversation_history = []
        self.api_key = GROQ_API_KEY
        
    def create_system_prompt(self):
        return f"""You are Dermaguard AI, an expert dermatology assistant with extensive medical knowledge. Your role is to provide COMPREHENSIVE, DETAILED, and EDUCATIONAL information about skin health while maintaining empathy and professionalism.

MEDICAL KNOWLEDGE BASE:
{json.dumps(DERMATOLOGY_KNOWLEDGE, indent=2)}

CRITICAL INSTRUCTIONS FOR DETAILED RESPONSES:

1. RESPONSE LENGTH & DEPTH:
   - Provide thorough, multi-paragraph responses (6-10 paragraphs when appropriate)
   - Break down complex topics into detailed sections
   - Include background information to educate the user
   - Explain the "why" behind recommendations, not just the "what"
   - Use specific medical terminology with clear explanations

2. RESPONSE STRUCTURE (use this format for detailed answers):
   a) EMPATHETIC OPENING: Acknowledge their concern and validate their feelings
   b) DETAILED EXPLANATION: Provide comprehensive information about the condition
   c) CAUSES & MECHANISMS: Explain what causes the condition and how it develops
   d) SYMPTOMS TO WATCH FOR: List detailed symptoms and variations
   e) TREATMENT OPTIONS: Provide extensive treatment information with explanations
   f) HOME CARE TIPS: Include specific, actionable advice
   g) PREVENTION STRATEGIES: Offer detailed prevention methods
   h) WHEN TO SEEK CARE: Clear guidelines for medical attention
   i) PROFESSIONAL DISCLAIMER: Emphasize the importance of consulting a dermatologist

3. EDUCATIONAL APPROACH:
   - Explain medical concepts in accessible language
   - Provide context and background information
   - Include "why" certain treatments work
   - Mention different severity levels and variations
   - Discuss risk factors and contributing factors
   - Explain the connection between symptoms and underlying causes

4. SPECIFIC DETAILS TO INCLUDE:
   - Timeline expectations (how long treatments take to work)
   - Specific product types and active ingredients
   - Step-by-step care instructions
   - What to expect during healing process
   - Common mistakes to avoid
   - Lifestyle factors that may contribute
   - Environmental triggers to consider

5. SAFETY & DISCLAIMERS:
   - NEVER diagnose - only provide educational information
   - Always emphasize professional consultation
   - Mention when immediate medical attention is needed
   - Note limitations of general advice
   - Encourage documentation of symptoms

6. TONE & STYLE:
   - Be warm, empathetic, and supportive
   - Use conversational yet professional language
   - Show genuine concern for the user's wellbeing
   - Be encouraging and reassuring
   - Avoid being overly technical but maintain medical accuracy

EXAMPLE OF DETAILED RESPONSE STYLE:
Instead of: "Use moisturizer for dry skin."
Say: "Moisturizing is crucial for managing dry skin, and the type of moisturizer you choose matters significantly. Look for products containing humectants like hyaluronic acid or glycerin, which draw moisture into the skin, combined with occlusives like petrolatum or dimethicone that seal in that moisture. Apply moisturizer immediately after bathing while your skin is still slightly damp - this traps water in the outer layers of your skin. For best results, use a thicker cream or ointment rather than a lotion, especially during dry winter months or in low-humidity environments."

Remember: Users seeking health information deserve comprehensive, educational responses that empower them to make informed decisions while encouraging professional medical consultation.

Recent conversation context: {self.conversation_history[-4:] if self.conversation_history else 'This is the first message'}
"""
    
    def query_groq(self, user_message):
        """Query Groq API with enhanced parameters for detailed responses"""
        try:
            print(f"🔍 DEBUG: Starting Groq API call...")
            print(f"🔍 DEBUG: API Key starts with: {self.api_key[:20]}...")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = self.create_system_prompt()
            print(f"🔍 DEBUG: System prompt length: {len(system_prompt)} characters")
            
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                "temperature": 0.8,  # Increased for more creative, detailed responses
                "max_tokens": 2048,  # DOUBLED from 1024 to allow longer responses
                "top_p": 0.95,  # Increased for more diverse vocabulary
                "stream": False
            }
            
            print(f"🔍 DEBUG: Sending request to Groq API...")
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            
            print(f"🔍 DEBUG: Response status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ DEBUG: Groq API SUCCESS! Response received.")
                assistant_response = result["choices"][0]["message"]["content"]
                print(f"✅ DEBUG: Assistant response length: {len(assistant_response)} characters")
                return assistant_response
            else:
                print(f"❌ DEBUG: Groq API ERROR: {response.status_code}")
                print(f"❌ DEBUG: Error response: {response.text}")
                return self.get_fallback_response(user_message)
                
        except requests.exceptions.Timeout:
            print(f"❌ DEBUG: Groq API timeout - request took too long")
            return self.get_fallback_response(user_message)
        except requests.exceptions.ConnectionError:
            print(f"❌ DEBUG: Groq API connection error - check internet")
            return self.get_fallback_response(user_message)
        except Exception as e:
            print(f"💥 DEBUG: Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, user_message):
        """Enhanced fallback response with more detail"""
        print(f"🔄 DEBUG: Using fallback response for: {user_message}")
        topic = analyze_question(user_message)
        knowledge = DERMATOLOGY_KNOWLEDGE.get(topic, {})
        
        if knowledge:
            response = f"I understand you're asking about {topic.replace('_', ' ')}.\n\n"
            response += f"{knowledge['description']}\n\n"
            
            if 'common_causes' in knowledge:
                response += "Common causes include:\n"
                for cause in knowledge['common_causes'][:3]:
                    response += f"• {cause}\n"
                response += "\n"
            
            if 'treatment' in knowledge:
                response += "General care recommendations:\n"
                for treatment in knowledge['treatment'][:3]:
                    response += f"• {treatment}\n"
                response += "\n"
            
            response += "Please remember to consult a dermatologist for personalized medical advice and proper diagnosis. They can provide treatment options specific to your situation."
            return response
        else:
            return "I'm here to help with dermatology questions. Could you tell me more about your skin concern? I can provide detailed information about conditions like rashes, acne, itching, sunburn, and other skin issues. Remember, I provide educational information only - always consult a doctor for medical advice."
    
    def chat(self, user_message):
        """Main chat method"""
        print(f"💬 DEBUG: Received user message: '{user_message}'")
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Get Groq response
        response = self.query_groq(user_message)
        
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep history manageable
        if len(self.conversation_history) > 12:
            self.conversation_history = self.conversation_history[-12:]
        
        print(f"💬 DEBUG: Sending response (length: {len(response)} chars)")
        return response

# Initialize the AI
derm_ai = GroqDermatologyAI()

def analyze_question(user_question):
    """Analyze the user's question and determine the topic"""
    question_lower = user_question.lower()
    
    if any(word in question_lower for word in ['rash', 'redness', 'hives', 'eruption']):
        return "skin_rash"
    elif any(word in question_lower for word in ['itch', 'itchy', 'pruritus']):
        return "itching"
    elif any(word in question_lower for word in ['burn', 'sunburn', 'sun burn']):
        return "sunburn"
    elif any(word in question_lower for word in ['acne', 'pimple', 'zit', 'blackhead']):
        return "acne"
    elif any(word in question_lower for word in ['melanoma', 'skin cancer']):
        return "melanoma"
    elif any(word in question_lower for word in ['eczema', 'atopic']):
        return "eczema"
    else:
        return "general"

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dermaguard AI - Detailed Responses</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .chat-container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #059669, #10b981);
                color: white;
                padding: 25px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.2em;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
            }
            .cloud-badge {
                background: rgba(255,255,255,0.2);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                margin-top: 10px;
                display: inline-block;
            }
            .chat-messages {
                height: 600px;
                overflow-y: auto;
                padding: 20px;
                background: #f8fafc;
            }
            .message {
                margin: 15px 0;
                padding: 15px 20px;
                border-radius: 15px;
                line-height: 1.6;
                max-width: 85%;
                white-space: pre-wrap;
            }
            .user-message {
                background: #3b82f6;
                color: white;
                margin-left: auto;
                border-bottom-right-radius: 5px;
            }
            .bot-message {
                background: white;
                border: 2px solid #e2e8f0;
                border-bottom-left-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .input-area {
                padding: 20px;
                background: white;
                border-top: 1px solid #e2e8f0;
                display: flex;
                gap: 10px;
            }
            #message-input {
                flex: 1;
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            #message-input:focus {
                border-color: #3b82f6;
            }
            #send-button {
                padding: 15px 25px;
                background: #059669;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;
            }
            #send-button:hover {
                background: #047857;
            }
            .disclaimer {
                padding: 15px;
                background: #fef3c7;
                border-top: 1px solid #f59e0b;
                text-align: center;
                font-size: 14px;
                color: #92400e;
            }
            .typing-indicator {
                padding: 10px 20px;
                color: #6b7280;
                font-style: italic;
            }
            .speed-badge {
                background: #10b981;
                color: white;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 0.8em;
                margin-left: 10px;
            }
            .debug-info {
                background: #f1f5f9;
                padding: 10px;
                border-top: 1px solid #e2e8f0;
                font-size: 12px;
                color: #64748b;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="header">
                <h1>🧬 Dermaguard AI</h1>
                <p>Comprehensive Dermatology Assistant</p>
                <div class="cloud-badge">
                    ⚡ Enhanced for Detailed Responses
                </div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message bot-message">
                    <strong>Dermaguard:</strong> Hello! I'm your comprehensive dermatology assistant powered by Groq Cloud AI. I provide detailed, educational information about skin conditions including rashes, acne, itching, sunburn, eczema, and more.<br><br>
                    I'm designed to give you thorough explanations, including causes, symptoms, treatment options, and prevention strategies. Feel free to ask detailed questions!<br><br>
                    <em>Remember: I provide educational information only - always consult a dermatologist for medical diagnosis and treatment.</em>
                </div>
            </div>
            
            <div class="input-area">
                <input type="text" id="message-input" placeholder="Ask detailed questions about skin concerns..." autocomplete="off">
                <button id="send-button">Send</button>
            </div>
            
            <div class="debug-info" id="debug-info">
                Debug: API Status - Ready | Enhanced Mode: 2048 tokens | Detailed Responses: ON
            </div>
            
            <div class="disclaimer">
                ⚕️ Disclaimer: This AI provides educational information only. It is not a substitute for professional medical advice. Always consult a qualified healthcare provider for medical concerns.
            </div>
        </div>

        <script>
            const chatMessages = document.getElementById('chat-messages');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const debugInfo = document.getElementById('debug-info');

            function addMessage(message, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                messageDiv.innerHTML = isUser ? 
                    `<strong>You:</strong> ${message}` : 
                    `<strong>Dermaguard:</strong> ${message}`;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function showTypingIndicator() {
                const typingDiv = document.createElement('div');
                typingDiv.className = 'typing-indicator';
                typingDiv.id = 'typing-indicator';
                typingDiv.innerHTML = '<strong>Dermaguard:</strong> Preparing detailed response... <span class="speed-badge">⚡ Groq</span>';
                chatMessages.appendChild(typingDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function hideTypingIndicator() {
                const typingIndicator = document.getElementById('typing-indicator');
                if (typingIndicator) {
                    typingIndicator.remove();
                }
            }

            function updateDebugInfo(status, details = '') {
                debugInfo.textContent = `Debug: ${status} | ${details}`;
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                addMessage(message, true);
                messageInput.value = '';
                sendButton.disabled = true;
                sendButton.textContent = 'Thinking...';
                updateDebugInfo('API Call - Requesting detailed response...');
                
                showTypingIndicator();

                try {
                    const startTime = Date.now();
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });

                    const data = await response.json();
                    const responseTime = Date.now() - startTime;
                    const charCount = data.response.length;
                    
                    hideTypingIndicator();
                    updateDebugInfo('API Status - Success', `${charCount} chars | ${responseTime}ms`);
                    
                    addMessage(data.response + ` <span class="speed-badge">${charCount} chars • ${responseTime}ms</span>`);
                } catch (error) {
                    hideTypingIndicator();
                    updateDebugInfo('API Status - Network Error', 'Check internet connection');
                    addMessage('Sorry, I encountered an error. Please check your internet connection and try again.');
                } finally {
                    sendButton.disabled = false;
                    sendButton.textContent = 'Send';
                }
            }

            sendButton.addEventListener('click', sendMessage);
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            messageInput.focus();
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    
    if not user_message:
        return jsonify({"response": "Please enter a question about skin health."})
    
    try:
        bot_response = derm_ai.chat(user_message)
        return jsonify({"response": bot_response})
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            "response": "I'm experiencing technical difficulties. Please try again in a moment."
        })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "system": "Dermaguard AI - Enhanced Detailed Mode",
        "model": MODEL_NAME,
        "max_tokens": 2048,
        "conversation_history_length": len(derm_ai.conversation_history),
        "api_provider": "Groq",
        "speed": "Ultra Fast ⚡"
    })

@app.route('/test-api')
def test_api():
    """Test endpoint to check if Groq API is working"""
    test_message = "Tell me about acne in detail"
    result = derm_ai.query_groq(test_message)
    return jsonify({
        "test_message": test_message,
        "response": result,
        "response_length": len(result),
        "api_working": not result.startswith("I understand you're asking about")
    })

if __name__ == '__main__':
    print("🚀 Dermaguard AI - Enhanced Detailed Mode")
    print("📚 Using model:", MODEL_NAME)
    print("🎯 Max tokens: 2048 (Enhanced)")
    print("🔑 API Key starts with:", GROQ_API_KEY[:20] + "...")
    print("🔗 Health check: http://localhost:5006/health")
    print("🧪 API Test: http://localhost:5006/test-api")
    print("💬 Chat interface: http://localhost:5006")
    print("\n✨ ENHANCED MODE: Detailed, comprehensive responses enabled")
    print("🔍 Debug mode: ON - Check terminal for detailed logs")
    
    app.run(debug=True, port=5006, host='0.0.0.0')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5006))
    app.run(host='0.0.0.0', port=port, debug=False)