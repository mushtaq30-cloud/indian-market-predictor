import React, { useState } from 'react';

const NewsPanel = ({ news }) => {
  const [showAll, setShowAll] = useState(false);
  
  const displayedNews = showAll ? news : news?.slice(0, 5);

  return (
    <div className="news-section">
      <div className="news-header">
        📰 Latest Market News
      </div>

      <ul className="news-list">
        {displayedNews?.map((article, index) => (
          <li key={index} className="news-item">
            <a 
              href={article.link} 
              target="_blank" 
              rel="noopener noreferrer"
              className="news-title"
            >
              {article.title}
            </a>
            <div className="news-meta">
              <span>📌 {article.source}</span>
              {article.published && (
                <span>🕐 {new Date(article.published).toLocaleDateString('en-IN')}</span>
              )}
            </div>
          </li>
        ))}
      </ul>

      {news?.length > 5 && (
        <button 
          onClick={() => setShowAll(!showAll)}
          className="chatbot-send-btn"
          style={{ marginTop: '16px', width: '100%' }}
        >
          {showAll ? 'Show Less' : `Show All (${news.length} articles)`}
        </button>
      )}
    </div>
  );
};

export default NewsPanel;
