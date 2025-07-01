-- BridgeFacile - Schéma de base de données complet
-- =====================================================
--
-- Ce fichier SQL combine tous les schémas pour créer une base de données complète
-- pour le site BridgeFacile, incluant l'authentification, les cours, et les articles de loi.
--
-- Auteur: BridgeFacile Team
-- Date: 2025-01-07

-- Fonction pour mettre à jour le timestamp 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- Schéma pour l'authentification et les profils utilisateurs
-- =====================================================

-- Table des rôles utilisateurs
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des permissions
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des profils utilisateurs
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(100),
    role_id INTEGER REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des permissions utilisateurs
CREATE TABLE user_permissions (
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by UUID REFERENCES user_profiles(id),
    PRIMARY KEY (user_id, permission_id)
);

-- Triggers pour l'authentification
CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_permissions_updated_at
    BEFORE UPDATE ON permissions
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- =====================================================
-- Schéma pour les cours et matériels pédagogiques
-- =====================================================

-- Table des catégories de cours
CREATE TABLE course_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des types de matériels pédagogiques
CREATE TABLE material_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des matériels pédagogiques
CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT,
    file_url VARCHAR(255),
    type_id INTEGER REFERENCES material_types(id),
    is_public BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES user_profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des cours
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES course_categories(id),
    level VARCHAR(50),
    duration INTEGER,  -- Durée en minutes
    price DECIMAL(10, 2),
    max_students INTEGER,
    is_group_course BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,
    instructor_id UUID REFERENCES user_profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des leçons
CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT,
    duration INTEGER,  -- Durée en minutes
    display_order INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des matériels associés aux leçons
CREATE TABLE lesson_materials (
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    material_id INTEGER REFERENCES materials(id) ON DELETE CASCADE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (lesson_id, material_id)
);

-- Table des inscriptions aux cours
CREATE TABLE course_enrollments (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    enrollment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    payment_status VARCHAR(50) DEFAULT 'pending',
    payment_amount DECIMAL(10, 2),
    payment_reference VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des leçons complétées
CREATE TABLE lesson_completions (
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    time_spent INTEGER,  -- Temps passé en secondes
    PRIMARY KEY (user_id, lesson_id)
);

-- Triggers pour les cours
CREATE TRIGGER update_course_categories_updated_at
    BEFORE UPDATE ON course_categories
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_material_types_updated_at
    BEFORE UPDATE ON material_types
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_materials_updated_at
    BEFORE UPDATE ON materials
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_courses_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_lessons_updated_at
    BEFORE UPDATE ON lessons
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_course_enrollments_updated_at
    BEFORE UPDATE ON course_enrollments
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- =====================================================
-- Schéma pour les articles de loi
-- =====================================================

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

-- Triggers pour les articles
CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_article_metadata_updated_at
    BEFORE UPDATE ON article_metadata
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- =====================================================
-- Vues pour faciliter l'accès aux données
-- =====================================================

-- Vue pour les utilisateurs avec leurs permissions
CREATE OR REPLACE VIEW view_users_with_permissions AS
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.display_name,
    r.name AS role_name,
    u.is_active,
    u.last_login,
    ARRAY(
        SELECT p.name
        FROM user_permissions up
        JOIN permissions p ON up.permission_id = p.id
        WHERE up.user_id = u.id
    ) AS permissions
FROM 
    user_profiles u
LEFT JOIN 
    roles r ON u.role_id = r.id;

-- Vue pour les cours avec leurs leçons
CREATE OR REPLACE VIEW view_courses_with_lessons AS
SELECT 
    c.id AS course_id,
    c.title AS course_title,
    c.description AS course_description,
    c.level,
    c.duration AS course_duration,
    c.price,
    c.max_students,
    c.is_group_course,
    c.is_published AS course_published,
    cc.name AS category_name,
    up.display_name AS instructor_name,
    (
        SELECT COUNT(*)
        FROM course_enrollments ce
        WHERE ce.course_id = c.id AND ce.is_active = TRUE
    ) AS enrollment_count,
    ARRAY(
        SELECT json_build_object(
            'id', l.id,
            'title', l.title,
            'description', l.description,
            'duration', l.duration,
            'display_order', l.display_order,
            'is_published', l.is_published
        )
        FROM lessons l
        WHERE l.course_id = c.id
        ORDER BY l.display_order
    ) AS lessons
FROM 
    courses c
LEFT JOIN 
    course_categories cc ON c.category_id = cc.id
LEFT JOIN 
    user_profiles up ON c.instructor_id = up.id;

-- Vue pour les articles avec leurs références
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

-- =====================================================
-- Index pour améliorer les performances
-- =====================================================

-- Index pour l'authentification
CREATE INDEX idx_user_profiles_role_id ON user_profiles(role_id);
CREATE INDEX idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_permission_id ON user_permissions(permission_id);

-- Index pour les cours
CREATE INDEX idx_courses_category_id ON courses(category_id);
CREATE INDEX idx_courses_instructor_id ON courses(instructor_id);
CREATE INDEX idx_lessons_course_id ON lessons(course_id);
CREATE INDEX idx_materials_type_id ON materials(type_id);
CREATE INDEX idx_course_enrollments_course_id ON course_enrollments(course_id);
CREATE INDEX idx_course_enrollments_user_id ON course_enrollments(user_id);
CREATE INDEX idx_lesson_completions_user_id ON lesson_completions(user_id);
CREATE INDEX idx_lesson_completions_lesson_id ON lesson_completions(lesson_id);

-- Index pour les articles
CREATE INDEX idx_articles_article_id ON articles(article_id);
CREATE INDEX idx_article_references_source ON article_references(source_article_id);
CREATE INDEX idx_article_references_target ON article_references(target_article_id);
CREATE INDEX idx_article_metadata_article_id ON article_metadata(article_id);
CREATE INDEX idx_article_categories_article_id ON article_categories(article_id);
CREATE INDEX idx_article_categories_category_id ON article_categories(category_id);

-- =====================================================
-- Données initiales
-- =====================================================

-- Rôles utilisateurs
INSERT INTO roles (name, description) VALUES
('admin', 'Administrateur avec accès complet'),
('teacher', 'Enseignant avec accès aux cours et à l''arbitrage'),
('student', 'Étudiant avec accès aux cours uniquement'),
('referee', 'Arbitre avec accès à l''arbitrage uniquement'),
('guest', 'Utilisateur invité avec accès limité');

-- Permissions
INSERT INTO permissions (name, description) VALUES
('access_courses', 'Accès aux cours et matériels pédagogiques'),
('access_arbitration', 'Accès aux documents d''arbitrage et au Code 2017'),
('manage_users', 'Gestion des utilisateurs'),
('manage_content', 'Gestion du contenu du site'),
('view_analytics', 'Visualisation des statistiques et analyses');

-- Catégories de cours
INSERT INTO course_categories (name, description, display_order) VALUES
('Débutant', 'Cours pour les débutants absolus', 1),
('Intermédiaire', 'Cours pour les joueurs ayant déjà des bases', 2),
('Avancé', 'Cours pour les joueurs expérimentés', 3),
('Compétition', 'Cours pour la préparation aux compétitions', 4),
('Arbitrage', 'Formation à l''arbitrage', 5);

-- Types de matériels pédagogiques
INSERT INTO material_types (name, description, icon) VALUES
('PDF', 'Document PDF', 'file-pdf'),
('Image', 'Image ou diagramme', 'image'),
('Exercice', 'Exercice pratique', 'tasks'),
('Quiz', 'Questionnaire à choix multiples', 'question-circle'),
('Lien', 'Lien vers une ressource externe', 'link');

