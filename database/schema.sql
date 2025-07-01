-- BridgeFacile - Schéma de base de données pour les articles de loi
-- =====================================================
--
-- Ce fichier SQL définit la structure de la base de données pour stocker
-- les articles de loi du Code 2017 de bridge et leurs références.
--
-- Auteur: BridgeFacile Team
-- Date: 2025-01-07

-- Supprimer les tables si elles existent déjà (pour réinitialisation)
DROP TABLE IF EXISTS article_references;
DROP TABLE IF EXISTS article_categories;
DROP TABLE IF EXISTS article_metadata;
DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS categories;

-- Table des catégories d'articles
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des articles de loi
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(20) NOT NULL UNIQUE,  -- Identifiant de l'article (ex: "40", "40A", "40.1")
    title TEXT NOT NULL,                     -- Titre de l'article
    content TEXT NOT NULL,                   -- Contenu complet de l'article
    source_file VARCHAR(255),                -- Fichier PDF source
    category_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des métadonnées des articles
CREATE TABLE article_metadata (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    word_count INTEGER DEFAULT 0,            -- Nombre de mots dans l'article
    reference_count INTEGER DEFAULT 0,       -- Nombre de références sortantes
    citation_count INTEGER DEFAULT 0,        -- Nombre de références entrantes
    importance_score FLOAT DEFAULT 0,        -- Score d'importance (basé sur les références)
    complexity_score FLOAT DEFAULT 0,        -- Score de complexité (basé sur le contenu)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des références entre articles
CREATE TABLE article_references (
    id SERIAL PRIMARY KEY,
    source_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    target_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    reference_type VARCHAR(50) DEFAULT 'direct',  -- Type de référence (direct, indirect, etc.)
    context TEXT,                                 -- Contexte de la référence (texte environnant)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_article_id, target_article_id)  -- Éviter les doublons
);

-- Table des catégories d'articles (relation many-to-many)
CREATE TABLE article_categories (
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, category_id)
);

-- Index pour améliorer les performances
CREATE INDEX idx_articles_article_id ON articles(article_id);
CREATE INDEX idx_article_references_source ON article_references(source_article_id);
CREATE INDEX idx_article_references_target ON article_references(target_article_id);
CREATE INDEX idx_article_metadata_article_id ON article_metadata(article_id);
CREATE INDEX idx_article_categories_article_id ON article_categories(article_id);
CREATE INDEX idx_article_categories_category_id ON article_categories(category_id);

-- Fonction pour mettre à jour le timestamp 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour mettre à jour automatiquement 'updated_at'
CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_article_metadata_updated_at
    BEFORE UPDATE ON article_metadata
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Vue pour faciliter l'accès aux articles avec leurs références
CREATE OR REPLACE VIEW view_articles_with_references AS
SELECT 
    a.id,
    a.article_id,
    a.title,
    a.content,
    a.source_file,
    a.is_active,
    m.word_count,
    m.reference_count,
    m.citation_count,
    m.importance_score,
    ARRAY(
        SELECT target.article_id
        FROM article_references ar
        JOIN articles target ON ar.target_article_id = target.id
        WHERE ar.source_article_id = a.id
    ) AS references,
    ARRAY(
        SELECT source.article_id
        FROM article_references ar
        JOIN articles source ON ar.source_article_id = source.id
        WHERE ar.target_article_id = a.id
    ) AS referenced_by,
    ARRAY(
        SELECT c.name
        FROM article_categories ac
        JOIN categories c ON ac.category_id = c.id
        WHERE ac.article_id = a.id
    ) AS categories
FROM 
    articles a
LEFT JOIN 
    article_metadata m ON a.id = m.article_id;

-- Vue pour les statistiques globales
CREATE OR REPLACE VIEW view_article_statistics AS
SELECT
    COUNT(DISTINCT a.id) AS total_articles,
    COUNT(DISTINCT ar.id) AS total_references,
    AVG(m.word_count) AS avg_word_count,
    MAX(m.citation_count) AS max_citations,
    (
        SELECT a.article_id
        FROM articles a
        JOIN article_metadata m ON a.id = m.article_id
        ORDER BY m.citation_count DESC
        LIMIT 1
    ) AS most_cited_article,
    COUNT(DISTINCT c.id) AS total_categories
FROM
    articles a
LEFT JOIN
    article_references ar ON a.id = ar.source_article_id
LEFT JOIN
    article_metadata m ON a.id = m.article_id
LEFT JOIN
    article_categories ac ON a.id = ac.article_id
LEFT JOIN
    categories c ON ac.category_id = c.id;

-- Fonction pour rechercher des articles par contenu
CREATE OR REPLACE FUNCTION search_articles(search_query TEXT)
RETURNS TABLE(
    id INTEGER,
    article_id VARCHAR(20),
    title TEXT,
    content_excerpt TEXT,
    relevance FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.article_id,
        a.title,
        substring(a.content, 1, 200) AS content_excerpt,
        ts_rank_cd(
            to_tsvector('french', a.title || ' ' || a.content),
            to_tsquery('french', search_query)
        ) AS relevance
    FROM
        articles a
    WHERE
        to_tsvector('french', a.title || ' ' || a.content) @@ to_tsquery('french', search_query)
    ORDER BY
        relevance DESC;
END;
$$ LANGUAGE plpgsql;

-- Commentaires sur le schéma
COMMENT ON TABLE articles IS 'Table principale contenant les articles de loi du Code 2017 de bridge';
COMMENT ON TABLE article_references IS 'Table des références entre articles (graphe orienté)';
COMMENT ON TABLE categories IS 'Catégories pour organiser les articles';
COMMENT ON TABLE article_metadata IS 'Métadonnées et statistiques sur les articles';
COMMENT ON TABLE article_categories IS 'Relation many-to-many entre articles et catégories';
COMMENT ON VIEW view_articles_with_references IS 'Vue consolidée des articles avec leurs références';
COMMENT ON VIEW view_article_statistics IS 'Statistiques globales sur les articles et références';
COMMENT ON FUNCTION search_articles IS 'Fonction de recherche plein texte dans les articles';

