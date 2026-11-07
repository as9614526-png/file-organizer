import React, { useState, useEffect } from 'react';
import { 
  FolderOpen, 
  Play, 
  RotateCcw, 
  Sparkles, 
  Search, 
  Terminal, 
  Files, 
  CheckCircle2, 
  AlertCircle,
  FolderTree,
  Eye,
  RefreshCw
} from 'lucide-react';
import CategoryCard from './components/CategoryCard';
import './App.css';

export default function App() {
  const [folder, setFolder] = useState('demo_messy_folder');
  const [recursive, setRecursive] = useState(false);
  const [dryRun, setDryRun] = useState(false);
  const [config, setConfig] = useState({ categories: {}, default_category: 'Other files' });
  const [stats, setStats] = useState({ total_files: 0, category_counts: {}, files: [] });
  const [hasAuditLog, setHasAuditLog] = useState(false);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('console');
  const [loading, setLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);

  const addLog = (type, message) => {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [{ id: Date.now() + Math.random(), time, type, message }, ...prev]);
  };

  // Fetch initial config and check backend
  const fetchConfig = async () => {
    try {
      const res = await fetch('/api/config');
      if (res.ok) {
        const data = await res.json();
        setConfig(data);
        setBackendOnline(true);
      } else {
        setBackendOnline(false);
      }
    } catch {
      setBackendOnline(false);
    }
  };

  // Scan current folder
  const scanFolder = async (targetFolder = folder, isRecursive = recursive) => {
    if (!targetFolder.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder: targetFolder, recursive: isRecursive })
      });
      const data = await res.json();
      if (res.ok) {
        setStats(data);
        setHasAuditLog(data.has_audit_log);
        setBackendOnline(true);
      } else {
        addLog('error', data.error || 'Failed to scan folder.');
      }
    } catch (err) {
      addLog('error', `Connection error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  // Native Browse Folder picker
  const handleBrowse = async () => {
    try {
      addLog('info', 'Opening folder selection dialog...');
      const res = await fetch('/api/browse', { method: 'POST' });
      const data = await res.json();
      if (data.selected) {
        setFolder(data.selected);
        addLog('info', `Selected folder: ${data.selected}`);
        scanFolder(data.selected);
      }
    } catch (err) {
      addLog('error', `Browse error: ${err.message}`);
    }
  };

  // Generate Demo Files
  const handleCreateDemo = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder: 'demo_messy_folder' })
      });
      const data = await res.json();
      if (res.ok) {
        setFolder(data.folder_name);
        addLog('info', `Created demo messy folder with 18 sample files.`);
        await scanFolder(data.folder_name);
      }
    } catch (err) {
      addLog('error', `Demo creation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Run Organization
  const handleOrganize = async () => {
    if (!folder.trim()) return;
    setLoading(true);
    addLog('info', `Starting organization (${dryRun ? 'DRY-RUN' : 'LIVE'})...`);
    try {
      const res = await fetch('/api/organize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder, recursive, dry_run: dryRun })
      });
      const data = await res.json();
      if (res.ok) {
        if (data.moved && data.moved.length > 0) {
          data.moved.forEach((m) => {
            addLog(dryRun ? 'simulated' : 'moved', m);
          });
        }
        if (data.errors && data.errors.length > 0) {
          data.errors.forEach((e) => addLog('error', e));
        }
        addLog('info', `Completed: ${data.moved?.length || 0} moved, ${data.errors?.length || 0} errors.`);
        await scanFolder(folder);
      } else {
        addLog('error', data.error || 'Failed to organize.');
      }
    } catch (err) {
      addLog('error', `Organize error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Run Undo
  const handleUndo = async () => {
    if (!folder.trim()) return;
    setLoading(true);
    addLog('info', `Reverting previous organization session...`);
    try {
      const res = await fetch('/api/undo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder, dry_run: dryRun })
      });
      const data = await res.json();
      if (res.ok) {
        if (data.restored && data.restored.length > 0) {
          data.restored.forEach((r) => addLog('restored', r));
        }
        if (data.errors && data.errors.length > 0) {
          data.errors.forEach((e) => addLog('error', e));
        }
        addLog('info', `Undo completed: ${data.restored?.length || 0} restored.`);
        await scanFolder(folder);
      } else {
        addLog('error', data.error || 'Undo failed.');
      }
    } catch (err) {
      addLog('error', `Undo error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const allCategories = [
    ...Object.keys(config.categories || {}),
    config.default_category || 'Other files'
  ];

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-wrapper">
          <div className="brand-icon-box">
            <FolderTree size={26} color="#ffffff" />
          </div>
          <div>
            <h1 className="brand-title">File Organizer</h1>
            <p className="brand-subtitle">Smart Python & React Automation Suite</p>
          </div>
        </div>

        <div className={`status-badge ${backendOnline ? '' : 'error'}`}>
          <span className="status-dot"></span>
          {backendOnline ? 'Python Backend Online' : 'Backend Disconnected (Port 5000)'}
        </div>
      </header>

      {/* Control Panel */}
      <section className="glass-panel control-section">
        <div className="input-row">
          <div className="path-input-wrapper">
            <Search className="path-input-icon" size={18} />
            <input
              type="text"
              className="path-input"
              value={folder}
              placeholder="Enter folder path (e.g. C:\Users\Downloads)..."
              onChange={(e) => setFolder(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && scanFolder(folder)}
            />
          </div>

          <button className="btn btn-secondary" onClick={handleBrowse} disabled={loading}>
            <FolderOpen size={16} />
            Browse
          </button>

          <button className="btn btn-secondary" onClick={() => scanFolder(folder)} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Scan
          </button>

          <button className="btn btn-demo" onClick={handleCreateDemo} disabled={loading}>
            <Sparkles size={16} />
            Generate Demo Files
          </button>
        </div>

        {/* Options & Action Bar */}
        <div className="action-options-bar">
          <div className="toggles-group">
            <label className="toggle-label">
              <input
                type="checkbox"
                className="toggle-checkbox"
                checked={recursive}
                onChange={(e) => {
                  setRecursive(e.target.checked);
                  scanFolder(folder, e.target.checked);
                }}
              />
              <FolderTree size={16} />
              Recursive Subfolders (-r)
            </label>

            <label className="toggle-label">
              <input
                type="checkbox"
                className="toggle-checkbox"
                checked={dryRun}
                onChange={(e) => setDryRun(e.target.checked)}
              />
              <Eye size={16} />
              Dry-Run Simulation (--dry-run)
            </label>
          </div>

          <div className="actions-group">
            {hasAuditLog && (
              <button 
                className="btn btn-danger" 
                onClick={handleUndo} 
                disabled={loading}
                title="Rollback the last organization session"
              >
                <RotateCcw size={16} />
                Undo Session
              </button>
            )}

            <button 
              className="btn btn-primary" 
              onClick={handleOrganize} 
              disabled={loading || stats.total_files === 0}
            >
              <Play size={16} />
              {dryRun ? 'Simulate Organize' : 'Organize Folder'}
            </button>
          </div>
        </div>
      </section>

      {/* Category Breakdown Cards */}
      <section className="cards-grid">
        {allCategories.map((category) => (
          <CategoryCard
            key={category}
            category={category}
            count={stats.category_counts[category] || 0}
            extensions={config.categories?.[category] || []}
          />
        ))}
      </section>

      {/* Tabbed Console & Discovered Files */}
      <section className="glass-panel results-section">
        <div className="tabs-header">
          <div className="tab-buttons">
            <button
              className={`tab-btn ${activeTab === 'console' ? 'active' : ''}`}
              onClick={() => setActiveTab('console')}
            >
              <Terminal size={15} />
              Activity Log ({logs.length})
            </button>
            <button
              className={`tab-btn ${activeTab === 'files' ? 'active' : ''}`}
              onClick={() => setActiveTab('files')}
            >
              <Files size={15} />
              Files Found ({stats.total_files})
            </button>
          </div>

          {activeTab === 'console' && logs.length > 0 && (
            <button 
              className="tab-btn" 
              onClick={() => setLogs([])}
              style={{ fontSize: '11px' }}
            >
              Clear Logs
            </button>
          )}
        </div>

        {activeTab === 'console' ? (
          <div className="console-box">
            {logs.length === 0 ? (
              <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '30px 0' }}>
                No activity yet. Click "Generate Demo Files" or "Organize Folder" to see real-time updates.
              </div>
            ) : (
              logs.map((log) => (
                <div key={log.id} className="log-line">
                  <span className="log-time">{log.time}</span>
                  <span className={`log-badge ${log.type}`}>
                    [{log.type.toUpperCase()}]
                  </span>
                  <span className="log-msg">{log.message}</span>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="files-table-wrapper">
            {stats.files.length === 0 ? (
              <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '40px 0' }}>
                No unorganized files found in this folder.
              </div>
            ) : (
              <table className="files-table">
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Category</th>
                    <th>Extension</th>
                    <th>Path</th>
                    <th>Size</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.files.map((file, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600 }}>{file.name}</td>
                      <td>
                        <span className="ext-badge" style={{ color: '#f8fafc' }}>
                          {file.category}
                        </span>
                      </td>
                      <td><span className="ext-badge">{file.extension || 'none'}</span></td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{file.rel_path}</td>
                      <td style={{ color: 'var(--text-dim)' }}>
                        {file.size > 1024 * 1024 
                          ? `${(file.size / (1024 * 1024)).toFixed(1)} MB` 
                          : `${(file.size / 1024).toFixed(1)} KB`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

