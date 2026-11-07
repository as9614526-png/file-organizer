import React from 'react';
import { 
  Image as ImageIcon, 
  FileText, 
  Video, 
  Music, 
  FolderArchive,
  Folder
} from 'lucide-react';

const CATEGORY_STYLES = {
  Images: {
    icon: ImageIcon,
    color: '#ec4899',
    bgColor: 'rgba(236, 72, 153, 0.15)',
    glowColor: 'rgba(236, 72, 153, 0.3)'
  },
  Documents: {
    icon: FileText,
    color: '#38bdf8',
    bgColor: 'rgba(56, 189, 248, 0.15)',
    glowColor: 'rgba(56, 189, 248, 0.3)'
  },
  Videos: {
    icon: Video,
    color: '#fb923c',
    bgColor: 'rgba(251, 146, 60, 0.15)',
    glowColor: 'rgba(251, 146, 60, 0.3)'
  },
  Audio: {
    icon: Music,
    color: '#34d399',
    bgColor: 'rgba(52, 211, 153, 0.15)',
    glowColor: 'rgba(52, 211, 153, 0.3)'
  },
  'Other files': {
    icon: FolderArchive,
    color: '#a78bfa',
    bgColor: 'rgba(167, 139, 250, 0.15)',
    glowColor: 'rgba(167, 139, 250, 0.3)'
  }
};

export default function CategoryCard({ category, count = 0, extensions = [] }) {
  const style = CATEGORY_STYLES[category] || {
    icon: Folder,
    color: '#94a3b8',
    bgColor: 'rgba(148, 163, 184, 0.15)',
    glowColor: 'rgba(148, 163, 184, 0.3)'
  };
  const Icon = style.icon;

  return (
    <div className="glass-panel category-card animate-fade">
      <div className="card-top">
        <div 
          className="card-icon-wrapper"
          style={{ background: style.bgColor, color: style.color }}
        >
          <Icon size={20} />
        </div>
        <div className="card-count" style={{ color: count > 0 ? style.color : 'inherit' }}>
          {count}
        </div>
      </div>
      <div className="card-name">{category}</div>
      <div className="card-extensions">
        {extensions.length > 0 ? (
          extensions.slice(0, 5).map((ext) => (
            <span key={ext} className="ext-badge">
              {ext}
            </span>
          ))
        ) : (
          <span className="ext-badge">unmatched</span>
        )}
        {extensions.length > 5 && (
          <span className="ext-badge">+{extensions.length - 5}</span>
        )}
      </div>
    </div>
  );
}

