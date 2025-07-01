// src/components/RncArticles.jsx
import React, { useState, useEffect } from 'react'
import { supabase } from '../supabaseClient'

export default function RncArticles() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchArticles()
  }, [])

  async function fetchArticles() {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('rnc_articles')
        .select('*')
        .order('article_number')
      
      if (error) throw error
      setArticles(data || [])
    } catch (error) {
      console.error('Erreur lors du chargement des articles:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rnc-articles-container">
      <h2>Règlement National des Compétitions</h2>
      {loading ? (
        <p>Chargement des articles...</p>
      ) : (
        <div className="articles-list">
          {articles.map((article) => (
            <div key={article.id} className="article-item">
              <h3>Article {article.article_number} - {article.title}</h3>
              <p>Page: {article.page}</p>
              {article.content && <div className="article-content">{article.content}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
