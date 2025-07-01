// src/App.jsx
import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ArbitragePage from './pages/ArbitragePage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>BridgeFacile</h1>
          <nav>
            <ul>
              <li><a href="/">Accueil</a></li>
              <li><a href="/cours">Cours</a></li>
              <li><a href="/arbitrage">Arbitrage</a></li>
            </ul>
          </nav>
        </header>
        
        <main>
          <Routes>
            <Route path="/" element={<div>Page d'accueil</div>} />
            <Route path="/cours" element={<div>Page des cours</div>} />
            <Route path="/arbitrage" element={<ArbitragePage />} />
          </Routes>
        </main>
        
        <footer>
          <p>&copy; 2025 BridgeFacile - Tous droits réservés</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
