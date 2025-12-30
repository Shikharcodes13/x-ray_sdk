import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import './ExecutionList.css'

function ExecutionList() {
  const [executions, setExecutions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchExecutions()
    const interval = setInterval(fetchExecutions, 2000) // Poll every 2 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchExecutions = async () => {
    try {
      const response = await axios.get('/api/executions')
      setExecutions(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch executions')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✓'
      case 'failed':
        return '✗'
      case 'running':
        return '⟳'
      default:
        return '○'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'var(--accent-green)'
      case 'failed':
        return 'var(--accent-red)'
      case 'running':
        return 'var(--accent-blue)'
      default:
        return 'var(--text-secondary)'
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading executions...</p>
      </div>
    )
  }

  if (error && executions.length === 0) {
    return (
      <div className="error-container">
        <p className="error-message">{error}</p>
        <button onClick={fetchExecutions} className="retry-button">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="execution-list">
      <div className="list-header">
        <h2>Executions</h2>
        <div className="execution-count">{executions.length} total</div>
      </div>
      
      {executions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <p>No executions yet</p>
          <p className="empty-subtitle">Start tracking executions using the X-Ray SDK</p>
        </div>
      ) : (
        <div className="executions-grid">
          {executions.map((execution) => (
            <div
              key={execution.execution_id}
              className="execution-card"
              onClick={() => navigate(`/execution/${execution.execution_id}`)}
            >
              <div className="card-header">
                <div className="card-title">
                  <span
                    className="status-indicator"
                    style={{ color: getStatusColor(execution.status) }}
                  >
                    {getStatusIcon(execution.status)}
                  </span>
                  <span className="execution-name">{execution.name}</span>
                </div>
                <div className="card-meta">
                  <span className="execution-id">
                    {execution.execution_id.substring(0, 8)}...
                  </span>
                </div>
              </div>
              
              <div className="card-body">
                <div className="card-info">
                  <div className="info-item">
                    <span className="info-label">Steps:</span>
                    <span className="info-value">{execution.steps?.length || 0}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Started:</span>
                    <span className="info-value">{formatDate(execution.started_at)}</span>
                  </div>
                  {execution.ended_at && (
                    <div className="info-item">
                      <span className="info-label">Duration:</span>
                      <span className="info-value">
                        {Math.round(
                          (new Date(execution.ended_at) - new Date(execution.started_at)) / 1000
                        )}s
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ExecutionList

