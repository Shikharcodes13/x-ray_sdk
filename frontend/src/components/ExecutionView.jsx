import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import Timeline from './Timeline'
import StepViewer from './StepViewer'
import './ExecutionView.css'

function ExecutionView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [execution, setExecution] = useState(null)
  const [selectedStep, setSelectedStep] = useState(null)
  const [selectedStepId, setSelectedStepId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const selectedStepIdRef = useRef(null)

  // Keep ref in sync with state
  useEffect(() => {
    selectedStepIdRef.current = selectedStepId
  }, [selectedStepId])

  useEffect(() => {
    fetchExecution()
    const interval = setInterval(fetchExecution, 2000) // Poll for updates
    return () => clearInterval(interval)
  }, [id])

  const fetchExecution = async () => {
    try {
      const response = await axios.get(`/api/executions/${id}`)
      setExecution(response.data)
      setError(null)
      
      const currentStepId = selectedStepIdRef.current
      
      // Update selectedStep to point to the new step object if we have a selectedStepId
      if (currentStepId && response.data.steps?.length > 0) {
        const updatedStep = response.data.steps.find(step => step.step_id === currentStepId)
        if (updatedStep) {
          setSelectedStep(updatedStep)
        } else {
          // Step was removed, clear selection
          setSelectedStep(null)
          setSelectedStepId(null)
        }
      } else if (!currentStepId && response.data.steps?.length > 0) {
        // Auto-select first step if none selected
        setSelectedStep(response.data.steps[0])
        setSelectedStepId(response.data.steps[0].step_id)
      }
    } catch (err) {
      setError('Failed to fetch execution')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleStepSelect = (step) => {
    setSelectedStep(step)
    setSelectedStepId(step.step_id)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
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
        <p>Loading execution...</p>
      </div>
    )
  }

  if (error || !execution) {
    return (
      <div className="error-container">
        <p className="error-message">{error || 'Execution not found'}</p>
        <button onClick={() => navigate('/')} className="back-button">
          Back to List
        </button>
      </div>
    )
  }

  return (
    <div className="execution-view">
      <div className="view-header">
        <button onClick={() => navigate('/')} className="back-button">
          ← Back
        </button>
        <div className="header-info">
          <h1 className="execution-title">{execution.name}</h1>
          <div className="execution-meta">
            <span
              className="status-badge"
              style={{ color: getStatusColor(execution.status) }}
            >
              {execution.status}
            </span>
            <span className="meta-item">
              ID: <code>{execution.execution_id}</code>
            </span>
            <span className="meta-item">
              Started: {formatDate(execution.started_at)}
            </span>
            {execution.ended_at && (
              <span className="meta-item">
                Duration:{' '}
                {Math.round(
                  (new Date(execution.ended_at) - new Date(execution.started_at)) / 1000
                )}s
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="view-content">
        <div className="timeline-panel">
          <Timeline
            steps={execution.steps || []}
            selectedStep={selectedStep}
            onStepSelect={handleStepSelect}
          />
        </div>
        
        <div className="details-panel">
          {selectedStep ? (
            <StepViewer step={selectedStep} />
          ) : (
            <div className="no-selection">
              <p>Select a step to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ExecutionView

