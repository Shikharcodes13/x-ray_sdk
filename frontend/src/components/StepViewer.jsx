import React, { useState } from 'react'
import EvaluationTable from './EvaluationTable'
import JSONViewer from './JSONViewer'
import './StepViewer.css'

function StepViewer({ step }) {
  const [activeTab, setActiveTab] = useState('evaluations')
  const [showFailedOnly, setShowFailedOnly] = useState(false)

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3
    })
  }

  const formatDuration = () => {
    if (!step.ended_at) return 'Running...'
    const duration = new Date(step.ended_at) - new Date(step.started_at)
    if (duration < 1000) return `${duration}ms`
    return `${(duration / 1000).toFixed(3)}s`
  }

  const evaluationCount = step.evaluations?.length || 0
  const passedCount = step.evaluations?.filter(e => e.passed).length || 0
  const failedCount = evaluationCount - passedCount

  return (
    <div className="step-viewer">
      <div className="viewer-header">
        <div>
          <h2 className="step-title">{step.name}</h2>
          <div className="step-info">
            <span className="info-badge">{step.type}</span>
            <span className="info-text">Started: {formatDate(step.started_at)}</span>
            {step.ended_at && (
              <span className="info-text">Ended: {formatDate(step.ended_at)}</span>
            )}
            <span className="info-text">Duration: {formatDuration()}</span>
          </div>
        </div>
        
        {evaluationCount > 0 && (
          <div className="evaluation-stats">
            <div className="stat-item">
              <span className="stat-label">Total</span>
              <span className="stat-value">{evaluationCount}</span>
            </div>
            <div className="stat-item stat-passed">
              <span className="stat-label">Passed</span>
              <span className="stat-value">{passedCount}</span>
            </div>
            <div className="stat-item stat-failed">
              <span className="stat-label">Failed</span>
              <span className="stat-value">{failedCount}</span>
            </div>
          </div>
        )}
      </div>

      <div className="viewer-tabs">
        <button
          className={`tab ${activeTab === 'evaluations' ? 'active' : ''}`}
          onClick={() => setActiveTab('evaluations')}
        >
          Evaluations
          {evaluationCount > 0 && (
            <span className="tab-badge">{evaluationCount}</span>
          )}
        </button>
        <button
          className={`tab ${activeTab === 'input' ? 'active' : ''}`}
          onClick={() => setActiveTab('input')}
        >
          Input
        </button>
        <button
          className={`tab ${activeTab === 'output' ? 'active' : ''}`}
          onClick={() => setActiveTab('output')}
        >
          Output
        </button>
        {step.rules && step.rules.length > 0 && (
          <button
            className={`tab ${activeTab === 'rules' ? 'active' : ''}`}
            onClick={() => setActiveTab('rules')}
          >
            Rules
            <span className="tab-badge">{step.rules.length}</span>
          </button>
        )}
      </div>

      <div className="viewer-content">
        {activeTab === 'evaluations' && (
          <div className="tab-panel">
            {evaluationCount > 0 ? (
              <>
                <div className="filter-controls">
                  <label className="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={showFailedOnly}
                      onChange={(e) => setShowFailedOnly(e.target.checked)}
                    />
                    <span>Show failed only</span>
                  </label>
                </div>
                <EvaluationTable
                  evaluations={step.evaluations}
                  showFailedOnly={showFailedOnly}
                />
              </>
            ) : (
              <div className="empty-state">
                <p>No evaluations recorded for this step</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'input' && (
          <div className="tab-panel">
            <JSONViewer data={step.input} />
          </div>
        )}

        {activeTab === 'output' && (
          <div className="tab-panel">
            <JSONViewer data={step.output} />
          </div>
        )}

        {activeTab === 'rules' && (
          <div className="tab-panel">
            {step.rules && step.rules.length > 0 ? (
              <div className="rules-list">
                {step.rules.map((rule, index) => (
                  <div key={index} className="rule-item">
                    <div className="rule-header">
                      <span className="rule-id">{rule.rule_id}</span>
                      <span className="rule-source">{rule.source}</span>
                    </div>
                    <div className="rule-description">{rule.description}</div>
                    <div className="rule-expression">
                      <code>
                        {rule.operator} {JSON.stringify(rule.value)}
                      </code>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>No rules defined for this step</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default StepViewer

