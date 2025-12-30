import React from 'react'
import './JSONViewer.css'

function JSONViewer({ data }) {
  const formatJSON = (obj) => {
    if (obj === null || obj === undefined) {
      return 'null'
    }
    return JSON.stringify(obj, null, 2)
  }

  const isEmpty = (obj) => {
    if (!obj) return true
    if (typeof obj !== 'object') return false
    return Object.keys(obj).length === 0
  }

  if (isEmpty(data)) {
    return (
      <div className="json-empty">
        <p>No data available</p>
      </div>
    )
  }

  return (
    <div className="json-viewer">
      <pre className="json-content">{formatJSON(data)}</pre>
    </div>
  )
}

export default JSONViewer

