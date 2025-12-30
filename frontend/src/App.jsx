import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ExecutionList from './components/ExecutionList'
import ExecutionView from './components/ExecutionView'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <h1 className="logo">
              <span className="logo-icon">🔍</span>
              X-Ray Debugger
            </h1>
            <div className="header-subtitle">Execution Tracking & Analysis</div>
          </div>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<ExecutionList />} />
            <Route path="/execution/:id" element={<ExecutionView />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

