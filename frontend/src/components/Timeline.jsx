import React from 'react'
import './Timeline.css'

function Timeline({ steps, selectedStep, onStepSelect }) {
  const getStepStatus = (step) => {
    if (!step.ended_at) return 'running'
    if (step.evaluations?.some(e => !e.passed)) return 'warning'
    return 'completed'
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✓'
      case 'warning':
        return '⚠'
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
      case 'warning':
        return 'var(--accent-yellow)'
      case 'running':
        return 'var(--accent-blue)'
      default:
        return 'var(--text-secondary)'
    }
  }

  const formatDuration = (step) => {
    if (!step.ended_at) return '...'
    const duration = new Date(step.ended_at) - new Date(step.started_at)
    if (duration < 1000) return `${duration}ms`
    return `${(duration / 1000).toFixed(2)}s`
  }

  return (
    <div className="timeline">
      <div className="timeline-header">
        <h3>Steps Timeline</h3>
        <div className="step-count">{steps.length} steps</div>
      </div>
      
      <div className="timeline-list">
        {steps.map((step, index) => {
          const status = getStepStatus(step)
          const isSelected = selectedStep?.step_id === step.step_id
          const evaluationCount = step.evaluations?.length || 0
          const passedCount = step.evaluations?.filter(e => e.passed).length || 0
          const failedCount = evaluationCount - passedCount

          return (
            <div
              key={step.step_id}
              className={`timeline-item ${isSelected ? 'selected' : ''}`}
              onClick={() => onStepSelect(step)}
            >
              <div className="timeline-connector">
                <div
                  className="status-dot"
                  style={{ 
                    backgroundColor: getStatusColor(status),
                    borderColor: getStatusColor(status)
                  }}
                >
                  <span className="status-icon">{getStatusIcon(status)}</span>
                </div>
                {index < steps.length - 1 && (
                  <div className="connector-line"></div>
                )}
              </div>
              
              <div className="timeline-content">
                <div className="step-header">
                  <span className="step-number">#{index + 1}</span>
                  <span className="step-name">{step.name}</span>
                </div>
                
                <div className="step-meta">
                  <span className="step-type">{step.type}</span>
                  <span className="step-duration">{formatDuration(step)}</span>
                </div>
                
                {evaluationCount > 0 && (
                  <div className="step-evaluations">
                    <span className="eval-count">
                      {evaluationCount} evaluations
                    </span>
                    {failedCount > 0 && (
                      <span className="eval-failed">
                        {failedCount} failed
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Timeline

