import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

function CodeLaws() {
  const [laws, setLaws] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLaws();
  }, []);

  const fetchLaws = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('code_laws')
        .select('*')
        .order('law_number::integer');
      
      if (error) throw error;
      console.log('Lois récupérées:', data?.length);
      setLaws(data || []);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>BridgeFacile - Arbitrage</h2>
      <h3>Code International du Bridge 2017</h3>
      <p>📚 {laws.length} lois disponibles</p>
      
      {loading && <p>Chargement...</p>}
      
      <div>
        {laws.map((law) => (
          <div key={law.id} style={{ padding: '15px', border: '1px solid #ddd', margin: '10px 0', borderRadius: '8px' }}>
            <h4>Loi {law.law_number} - {law.title}</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>{law.section}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CodeLaws;
