-- AgnaYI Real Estate CRM - Complete PostgreSQL Database Schema
-- Production-grade with indexes, enums, JSONB for flexibility, constraints
-- Run: psql -f schema.sql postgres

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy search on names/locations

-- Enums
CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'site_visit_scheduled', 'negotiation', 'closed_won', 'closed_lost');
CREATE TYPE property_type AS ENUM ('residential_apartment', 'residential_villa', 'residential_plot', 'commercial_office', 'commercial_shop', 'commercial_warehouse');
CREATE TYPE property_status AS ENUM ('available', 'under_negotiation', 'sold', 'rented');
CREATE TYPE client_type AS ENUM ('buyer', 'seller');
CREATE TYPE deal_stage AS ENUM ('inquiry', 'site_visit', 'negotiation', 'agreement_signed', 'registration', 'closed');
CREATE TYPE activity_type AS ENUM ('call', 'sms', 'email', 'note', 'status_change', 'visit');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'overdue');
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'agent');
CREATE TYPE notification_type AS ENUM ('task_due', 'lead_assigned', 'deal_stage_change', 'followup', 'performance');

-- Users/Agents
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    profile_photo TEXT,  -- S3 URL
    role user_role NOT NULL,
    specialization TEXT[],
    is_active BOOLEAN DEFAULT true,
    date_joined TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Leads
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    budget_min DECIMAL(12,2),
    budget_max DECIMAL(12,2),
    location_pref JSONB,  -- {city: '', area: '', pincode: ''}
    property_type_pref property_type[],
    source VARCHAR(100),  -- 'website', 'ads', 'referral', 'whatsapp', 'n8n'
    notes TEXT,
    status lead_status DEFAULT 'new',
    score INTEGER CHECK (score >= 0 AND score <= 100) DEFAULT 0,
    assigned_to UUID REFERENCES users(id),
    client_id UUID REFERENCES clients(id),  -- After qualification
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_leads_phone_email ON leads(phone, COALESCE(email, ''));  -- Duplicate detection
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_assigned ON leads(assigned_to);
CREATE INDEX idx_leads_score ON leads(score DESC);
CREATE INDEX idx_leads_phone_trgm ON leads USING gin (phone gin_trgm_ops);

-- Properties
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    location JSONB NOT NULL,  -- {city, area, pincode, lat, lng}
    price DECIMAL(12,2) NOT NULL,
    size_sqft DECIMAL(10,2),
    rooms INTEGER,
    floors INTEGER,
    amenities TEXT[],  -- ['parking', 'gym', ...]
    facing_direction VARCHAR(50),
    floor_number INTEGER,
    year_built INTEGER,
    images JSONB DEFAULT '[]'::JSONB,  -- [{url: S3, is_primary: true}]
    status property_status DEFAULT 'available',
    virtual_tour_url TEXT,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_location_trgm ON properties USING gin ((location->>'city') gin_trgm_ops);
CREATE INDEX idx_properties_price ON properties(price);
CREATE INDEX idx_properties_type ON properties((location->>'type'));

-- Property-Agent M:M
CREATE TABLE property_agents (
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (property_id, agent_id)
);

-- Clients
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type client_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    preferences JSONB,  -- {budget, localities[], types[], timeline}
    tags TEXT[],
    sentiment_history JSONB DEFAULT '[]'::JSONB,
    birthday DATE,
    lead_origin UUID REFERENCES leads(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_clients_type ON clients(type);
CREATE INDEX idx_clients_phone ON clients(phone);

-- Deals
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500),
    stage deal_stage DEFAULT 'inquiry',
    expected_close_date DATE,
    commission_pct DECIMAL(5,2),
    commission_flat DECIMAL(12,2),
    probability INTEGER DEFAULT 50 CHECK (probability BETWEEN 0 AND 100),
    documents JSONB DEFAULT '[]'::JSONB,  -- S3 URLs + categories
    property_id UUID REFERENCES properties(id),
    client_id UUID REFERENCES clients(id),
    agent_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP
);

CREATE INDEX idx_deals_stage ON deals(stage);
CREATE INDEX idx_deals_agent ON deals(agent_id);
CREATE INDEX idx_deals_client ON deals(client_id);

-- Activities (Polymorphic timeline)
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type activity_type NOT NULL,
    content JSONB NOT NULL,  -- {duration, outcome, message, etc.}
    lead_id UUID REFERENCES leads(id),
    client_id UUID REFERENCES clients(id),
    deal_id UUID REFERENCES deals(id),
    user_id UUID REFERENCES users(id) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activities_created ON activities(created_at DESC);
CREATE INDEX idx_activities_lead ON activities(lead_id);
CREATE INDEX idx_activities_client ON activities(client_id);
CREATE INDEX idx_activities_deal ON activities(deal_id);

-- Tasks/Followups
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    priority task_priority DEFAULT 'medium',
    status task_status DEFAULT 'pending',
    assigned_to UUID REFERENCES users(id),
    lead_id UUID REFERENCES leads(id),
    deal_id UUID REFERENCES deals(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_due ON tasks(due_date);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type notification_type NOT NULL,
    title VARCHAR(255),
    message TEXT,
    data JSONB,
    is_read BOOLEAN DEFAULT false,
    user_id UUID REFERENCES users(id),
    related_id UUID,  -- lead/deal/task id
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE not is_read;

-- Agent Performance Targets
CREATE TABLE agent_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES users(id),
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    target_deals INTEGER DEFAULT 0,
    target_revenue DECIMAL(12,2) DEFAULT 0,
    achieved_deals INTEGER DEFAULT 0,
    achieved_revenue DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(agent_id, year, month)
);

-- Property Views/Analytics
CREATE TABLE property_views (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id),
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(255),  -- For anon views
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_property_views_property ON property_views(property_id);

-- Webhook Logs (n8n)
CREATE TABLE webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100),  -- new_lead, lead_updated
    payload JSONB,
    status VARCHAR(50),  -- success, failed
    response TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_webhook_logs_event ON webhook_logs(event_type);
CREATE INDEX idx_webhook_logs_created ON webhook_logs(created_at DESC);

-- Property Recommendations
CREATE TABLE property_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id),
    property_id UUID REFERENCES properties(id),
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(client_id, property_id)
);

-- Triggers: Update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to main tables
CREATE TRIGGER update_leads_updated BEFORE UPDATE ON leads FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_properties_updated BEFORE UPDATE ON properties FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
-- ... (similar for clients, deals, etc.)

-- Indexes for performance
CREATE INDEX CONCURRENTLY idx_activities_user_created ON activities(user_id, created_at DESC);

-- Sample Data Insert (for testing)
INSERT INTO users (email, password_hash, first_name, last_name, role) VALUES 
('admin@agnayi.com', '$2b$12$...', 'Admin', 'User', 'admin'),
('agent1@agnayi.com', '$2b$12$...', 'John', 'Doe', 'agent');

-- Mermaid ERD (paste into mermaid.live for visual)
```
erDiagram
    USERS ||--o{ LEADS : "assigned_to"
    USERS ||--o{ PROPERTIES : "manages"
    USERS ||--o{ DEALS : "agent"
    USERS ||--o{ ACTIVITIES : "performed_by"
    USERS ||--o{ TASKS : "assigned_to"
    LEADS ||--o{ ACTIVITIES : "has"
    LEADS ||--o{ TASKS : "related"
    PROPERTIES ||--o{ DEALS : "involves"
    CLIENTS ||--o{ DEALS : "party"
    CLIENTS ||--o{ ACTIVITIES : "has"
    DEALS ||--o{ ACTIVITIES : "has"
    DEALS ||--o{ TASKS : "related"
```
```

