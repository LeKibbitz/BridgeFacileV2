-- BridgeFacile - Schéma de base de données pour l'authentification et les profils utilisateurs
-- =====================================================
--
-- Ce fichier SQL définit la structure de la base de données pour gérer
-- l'authentification et les profils utilisateurs avec différents niveaux d'accès.
--
-- Auteur: BridgeFacile Team
-- Date: 2025-01-07

-- Supprimer les tables si elles existent déjà (pour réinitialisation)
DROP TABLE IF EXISTS user_permissions;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS roles;

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

-- Index pour améliorer les performances
CREATE INDEX idx_user_profiles_role_id ON user_profiles(role_id);
CREATE INDEX idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_permission_id ON user_permissions(permission_id);

-- Fonction pour mettre à jour le timestamp 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour mettre à jour automatiquement 'updated_at'
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

-- Vue pour faciliter l'accès aux utilisateurs avec leurs rôles et permissions
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

-- Insertion des rôles par défaut
INSERT INTO roles (name, description) VALUES
('admin', 'Administrateur avec accès complet'),
('teacher', 'Enseignant avec accès aux cours et à l''arbitrage'),
('student', 'Étudiant avec accès aux cours uniquement'),
('referee', 'Arbitre avec accès à l''arbitrage uniquement'),
('guest', 'Utilisateur invité avec accès limité');

-- Insertion des permissions par défaut
INSERT INTO permissions (name, description) VALUES
('access_courses', 'Accès aux cours et matériels pédagogiques'),
('access_arbitration', 'Accès aux documents d''arbitrage et au Code 2017'),
('manage_users', 'Gestion des utilisateurs'),
('manage_content', 'Gestion du contenu du site'),
('view_analytics', 'Visualisation des statistiques et analyses');

-- Commentaires sur le schéma
COMMENT ON TABLE roles IS 'Rôles utilisateurs définissant les niveaux d''accès généraux';
COMMENT ON TABLE permissions IS 'Permissions spécifiques pouvant être attribuées aux utilisateurs';
COMMENT ON TABLE user_profiles IS 'Profils utilisateurs étendant la table auth.users de Supabase';
COMMENT ON TABLE user_permissions IS 'Relation many-to-many entre utilisateurs et permissions';
COMMENT ON VIEW view_users_with_permissions IS 'Vue consolidée des utilisateurs avec leurs rôles et permissions';

