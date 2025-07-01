// src/components/CodeLaws.jsx
import React, { useState, useEffect } from 'react'
import { supabase } from '../supabaseClient'

export default function CodeLaws() {
  const [laws, setLaws] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLaws()
  }, [])

  async function fetchLaws() {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('code_laws')
        .select('*')
        .order('law_number')
      
      if (error) throw error
      setLaws(data || [])
    } catch (error) {
      console.error('Erreur lors du chargement des lois:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="code-laws-container">
      <h2>Code International du Bridge</h2>
      {loading ? (
        <p>Chargement des lois...</p>
      ) : (
        <div className="laws-list">
          {laws.map((law) => (
            <div key={law.id} className="law-item">
              <h3>Loi {law.law_number} - {law.title}</h3>
              <p>Page: {law.page}</p>
              {law.content && <div className="law-content">{law.content}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
