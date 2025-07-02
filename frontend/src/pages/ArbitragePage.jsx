// src/pages/ArbitragePage.jsx
import React, { useState } from 'react'
import CodeLaws from '../components/CodeLaws'
import RncArticles from '../components/RncArticles'
import LawViewer from '../components/LawViewer'

export default function ArbitragePage() {
  const [activeTab, setActiveTab] = useState('code')
  const [selectedLaw, setSelectedLaw] = useState(null)
  const [selectedArticle, setSelectedArticle] = useState(null)

  return (
    <div className="arbitrage-page">
      <h1>TEST = Documentation d'Arbitrage</h1>
      
      <div className="tabs">
        <button 
          className={activeTab === 'code' ? 'active' : ''} 
          onClick={() => setActiveTab('code')}
        >
          Code International
        </button>
        <button 
          className={activeTab === 'rnc' ? 'active' : ''} 
          onClick={() => setActiveTab('rnc')}
        >
          RNC
        </button>
        <button 
          className={activeTab === 'categories' ? 'active' : ''} 
          onClick={() => setActiveTab('categories')}
        >
          Catégories d'Enchères
        </button>
      </div>
      
      <div className="content">
        {activeTab === 'code' && !selectedLaw && <CodeLaws onSelectLaw={setSelectedLaw} />}
        {activeTab === 'rnc' && !selectedArticle && <RncArticles onSelectArticle={setSelectedArticle} />}
        {activeTab === 'code' && selectedLaw && <LawViewer lawNumber={selectedLaw} onBack={() => setSelectedLaw(null)} />}
        {/* Ajouter les composants pour les autres onglets */}
      </div>
    </div>
  )
}
