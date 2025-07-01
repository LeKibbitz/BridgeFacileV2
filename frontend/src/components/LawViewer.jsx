// src/components/LawViewer.jsx
import React, { useState, useEffect } from 'react'
import { supabase } from '../supabaseClient'

export default function LawViewer({ lawNumber, onBack }) {
  const [law, setLaw] = useState(null)
  const [references, setReferences] = useState([])
  const [loading, setLoading] = useState(true)
  const [breadcrumb, setBreadcrumb] = useState([])

  useEffect(() => {
    if (lawNumber) {
      fetchLaw(lawNumber)
      // Ajouter à l'historique de navigation
      setBreadcrumb(prev => [...prev, { type: 'code', id: lawNumber }])
    }
  }, [lawNumber])

  async function fetchLaw(number) {
    try {
      setLoading(true)
      
      // Récupérer la loi
      const { data: lawData, error: lawError } = await supabase
        .from('code_laws')
        .select('*')
        .eq('law_number', number)
        .single()
      
      if (lawError) throw lawError
      setLaw(lawData)
      
      // Récupérer les références
      const { data: refData, error: refError } = await supabase
        .from('cross_references')
        .select('*')
        .eq('from_type', 'code')
        .eq('from_id', number)
      
      if (refError) throw refError
      setReferences(refData || [])
      
    } catch (error) {
      console.error('Erreur lors du chargement de la loi:', error)
    } finally {
      setLoading(false)
    }
  }

  function navigateTo(type, id) {
    if (type === 'code') {
      fetchLaw(id)
      setBreadcrumb(prev => [...prev, { type, id }])
    } else if (type === 'rnc') {
      // Naviguer vers un article du RNC
      // Implémenter la navigation vers le RNC
    }
  }

  function navigateBack(index) {
    const item = breadcrumb[index]
    setBreadcrumb(breadcrumb.slice(0, index + 1))
    
    if (item.type === 'code') {
      fetchLaw(item.id)
    } else if (item.type === 'rnc') {
      // Naviguer vers un article du RNC
    }
  }

  return (
    <div className="law-viewer">
      {/* Fil d'Ariane */}
      <div className="breadcrumb">
        <span onClick={onBack}>Accueil</span>
        {breadcrumb.map((item, index) => (
          <span key={index}>
            {' > '}
            <a onClick={() => navigateBack(index)}>
              {item.type === 'code' ? `Loi ${item.id}` : `Article ${item.id}`}
            </a>
          </span>
        ))}
      </div>
      
      {loading ? (
        <p>Chargement...</p>
      ) : law ? (
        <div className="law-detail">
          <h2>Loi {law.law_number} - {law.title}</h2>
          <p>Page: {law.page}</p>
          {law.content && <div className="law-content">{law.content}</div>}
          
          {/* Références */}
          {references.length > 0 && (
            <div className="references">
              <h3>Références:</h3>
              <ul>
                {references.map((ref, index) => (
                  <li key={index}>
                    <a onClick={() => navigateTo(ref.to_type, ref.to_id)}>
                      {ref.to_type === 'code' ? `Loi ${ref.to_id}` : `Article ${ref.to_id}`}
                    </a>
                    {ref.context && <span> - {ref.context}</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <p>Loi non trouvée</p>
      )}
    </div>
  )
}
