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
      console.log('Fetching laws...');
      const { data, error } = await supabase
        .from('code_laws')
        .select('*')
        .order('law_number::integer');

      console.log('Data received:', data);
      if (error) {
        console.error('Error:', error);
        throw error;
      }
      
      setLaws(data || []);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Code International du Bridge 2017</h2>
      <p>📚 {laws.length} lois trouvées</p>
      <button onClick={fetchLaws}>🔄 Recharger</button>
      
      {loading && <p>Chargement...</p>}
      
      <div>
        {laws.map((law) => (
          <div key={law.id} style={{ padding: '10px', border: '1px solid #ddd', margin: '5px 0' }}>
            <h4>Loi {law.law_number} - {law.title}</h4>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CodeLaws;
