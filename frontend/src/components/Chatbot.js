import React, { useState, useRef, useEffect } from 'react';
import { chatbotQuery } from '../services/api';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: '👋 Hi! I\'m your AI financial assistant. Ask me anything about Indian stock markets, gold, silver, or investment strategies!',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      type: 'user',
      text: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatbotQuery(input);
      
      const botMessage = {
        type: 'bot',
        text: response.answer,
        sources: response.sources,
        timestamp: new Date(response.timestamp)
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'bot',
        text: '❌ Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Chatbot error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedQuestions = [
    'What is the current gold price trend?',
    'Should I invest in Nifty 50 now?',
    'Tell me about silver price movements',
    'What factors affect gold prices in India?'
  ];

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <span style={{ fontSize: '2rem' }}>🤖</span>
        <div>
          <div className="chatbot-title">AI Financial Assistant</div>
          <div style={{ fontSize: '0.85rem', color: '#718096' }}>
            Powered by AI with live web search
          </div>
        </div>
      </div>

      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`message ${msg.type === 'user' ? 'message-user' : ''}`}
          >
            <div className={`message-bubble ${msg.type === 'user' ? 'user-bubble' : 'bot-bubble'}`}>
              {msg.text}
            </div>
            
            {msg.sources && msg.sources.length > 0 && (
              <div className="message-sources">
                <strong>📚 Sources:</strong>
                {msg.sources.map((source, idx) => (
                  <a 
                    key={idx}
                    href={source.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="source-link"
                  >
                    {idx + 1}. {source.title}
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}
        
        {loading && (
          <div className="message">
            <div className="message-bubble bot-bubble">
              <div className="loading-spinner" style={{ padding: '10px' }}>
                <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px', color: '#718096' }}>
            💡 Try asking:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => setInput(question)}
                style={{
                  padding: '8px 16px',
                  background: '#edf2f7',
                  border: 'none',
                  borderRadius: '16px',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  transition: 'background 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.background = '#e2e8f0'}
                onMouseLeave={(e) => e.target.style.background = '#edf2f7'}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="chatbot-input-area">
        <input
          type="text"
          className="chatbot-input"
          placeholder="Ask me anything about markets..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <button 
          className="chatbot-send-btn" 
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? '⏳' : '📤'} Send
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
