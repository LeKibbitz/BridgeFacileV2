-- BridgeFacile - Schéma de base de données pour les cours
-- =====================================================
--
-- Ce fichier SQL définit la structure de la base de données pour gérer
-- les cours, leçons, et matériels pédagogiques.
--
-- Auteur: BridgeFacile Team
-- Date: 2025-01-07

-- Supprimer les tables si elles existent déjà (pour réinitialisation)
DROP TABLE IF EXISTS course_enrollments;
DROP TABLE IF EXISTS lesson_completions;
DROP TABLE IF EXISTS lesson_materials;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS course_categories;
DROP TABLE IF EXISTS materials;
DROP TABLE IF EXISTS material_types;

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

-- Index pour améliorer les performances
CREATE INDEX idx_courses_category_id ON courses(category_id);
CREATE INDEX idx_courses_instructor_id ON courses(instructor_id);
CREATE INDEX idx_lessons_course_id ON lessons(course_id);
CREATE INDEX idx_materials_type_id ON materials(type_id);
CREATE INDEX idx_course_enrollments_course_id ON course_enrollments(course_id);
CREATE INDEX idx_course_enrollments_user_id ON course_enrollments(user_id);
CREATE INDEX idx_lesson_completions_user_id ON lesson_completions(user_id);
CREATE INDEX idx_lesson_completions_lesson_id ON lesson_completions(lesson_id);

-- Fonction pour mettre à jour le timestamp 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour mettre à jour automatiquement 'updated_at'
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

-- Vue pour faciliter l'accès aux cours avec leurs leçons
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

-- Vue pour les statistiques des cours
CREATE OR REPLACE VIEW view_course_statistics AS
SELECT
    c.id AS course_id,
    c.title AS course_title,
    COUNT(DISTINCT ce.user_id) AS total_students,
    COUNT(DISTINCT CASE WHEN ce.completion_date IS NOT NULL THEN ce.user_id END) AS completed_students,
    AVG(EXTRACT(EPOCH FROM (ce.completion_date - ce.enrollment_date)) / 86400) AS avg_completion_days,
    SUM(ce.payment_amount) AS total_revenue
FROM
    courses c
LEFT JOIN
    course_enrollments ce ON c.id = ce.course_id
GROUP BY
    c.id, c.title;

-- Insertion des catégories de cours par défaut
INSERT INTO course_categories (name, description, display_order) VALUES
('Débutant', 'Cours pour les débutants absolus', 1),
('Intermédiaire', 'Cours pour les joueurs ayant déjà des bases', 2),
('Avancé', 'Cours pour les joueurs expérimentés', 3),
('Compétition', 'Cours pour la préparation aux compétitions', 4),
('Arbitrage', 'Formation à l''arbitrage', 5);

-- Insertion des types de matériels pédagogiques
INSERT INTO material_types (name, description, icon) VALUES
('PDF', 'Document PDF', 'file-pdf'),
('Image', 'Image ou diagramme', 'image'),
('Exercice', 'Exercice pratique', 'tasks'),
('Quiz', 'Questionnaire à choix multiples', 'question-circle'),
('Lien', 'Lien vers une ressource externe', 'link');

-- Commentaires sur le schéma
COMMENT ON TABLE course_categories IS 'Catégories pour organiser les cours';
COMMENT ON TABLE material_types IS 'Types de matériels pédagogiques disponibles';
COMMENT ON TABLE materials IS 'Matériels pédagogiques réutilisables';
COMMENT ON TABLE courses IS 'Cours proposés par les instructeurs';
COMMENT ON TABLE lessons IS 'Leçons composant les cours';
COMMENT ON TABLE lesson_materials IS 'Association entre leçons et matériels';
COMMENT ON TABLE course_enrollments IS 'Inscriptions des utilisateurs aux cours';
COMMENT ON TABLE lesson_completions IS 'Suivi des leçons complétées par les utilisateurs';
COMMENT ON VIEW view_courses_with_lessons IS 'Vue consolidée des cours avec leurs leçons';
COMMENT ON VIEW view_course_statistics IS 'Statistiques sur les cours et les inscriptions';

