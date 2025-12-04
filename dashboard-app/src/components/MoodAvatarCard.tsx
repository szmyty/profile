import React from 'react';
import type { MoodData } from '../types';
import { Card } from './Card';
import '../styles/MoodAvatarCard.css';

interface MoodAvatarCardProps {
  data: MoodData | null;
  gradient?: string[];
}

export const MoodAvatarCard: React.FC<MoodAvatarCardProps> = ({ data, gradient }) => {
  if (!data) {
    return <Card title="😊 Mood" gradient={gradient}>
      <p className="no-data">Mood data not available</p>
    </Card>;
  }

  const getMoodColor = (score: number) => {
    if (score >= 80) return 'var(--color-high)';
    if (score >= 50) return 'var(--color-medium)';
    return 'var(--color-low)';
  };

  return (
    <Card title="😊 Current Mood" gradient={gradient}>
      <div className="mood-content">
        <div className="mood-emoji">{data.emoji}</div>
        
        <div className="mood-description">{data.description}</div>
        
        <div className="mood-score">
          <div className="score-bar">
            <div 
              className="score-fill" 
              style={{ 
                width: `${data.score}%`,
                backgroundColor: getMoodColor(data.score)
              }}
            />
          </div>
          <div className="score-text" style={{ color: getMoodColor(data.score) }}>
            {data.score}/100
          </div>
        </div>

        <div className="mood-timestamp">
          Updated: {new Date(data.timestamp).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </Card>
  );
};
