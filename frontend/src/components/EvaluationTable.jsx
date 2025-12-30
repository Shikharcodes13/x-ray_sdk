import React from 'react'
import './EvaluationTable.css'

function EvaluationTable({ evaluations, showFailedOnly }) {
  const filteredEvaluations = showFailedOnly
    ? evaluations.filter(e => !e.passed)
    : evaluations

  const formatValue = (value) => {
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2)
    }
    return String(value)
  }

  return (
    <div className="evaluation-table-container">
      <table className="evaluation-table">
        <thead>
          <tr>
            <th>Entity ID</th>
            <th>Value</th>
            <th>Status</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {filteredEvaluations.length === 0 ? (
            <tr>
              <td colSpan="4" className="empty-message">
                {showFailedOnly
                  ? 'No failed evaluations'
                  : 'No evaluations to display'}
              </td>
            </tr>
          ) : (
            filteredEvaluations.map((evaluation, index) => (
              <tr
                key={`${evaluation.entity_id}-${index}`}
                className={evaluation.passed ? 'passed' : 'failed'}
              >
                <td className="entity-id">
                  <code>{evaluation.entity_id}</code>
                </td>
                <td className="value-cell">
                  <pre>{formatValue(evaluation.value)}</pre>
                </td>
                <td className="status-cell">
                  <span
                    className={`status-badge ${evaluation.passed ? 'passed' : 'failed'}`}
                  >
                    {evaluation.passed ? '✓ Pass' : '✗ Fail'}
                  </span>
                </td>
                <td className="reason-cell">{evaluation.reason}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export default EvaluationTable

