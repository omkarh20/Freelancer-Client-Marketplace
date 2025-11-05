-- Database: Freelancer-Client Marketplace

DROP DATABASE IF EXISTS Freelancer_Client_Marketplace;

CREATE DATABASE Freelancer_Client_Marketplace;

USE Freelancer_Client_Marketplace;

-- 1. Client Table
CREATE TABLE Client (
    client_id           INT PRIMARY KEY,
    client_name         VARCHAR(100) NOT NULL,
    client_email        VARCHAR(100) UNIQUE NOT NULL,
    client_registration_date DATE NOT NULL
);

-- 2. Freelancers Table
CREATE TABLE Freelancers (
    freelancer_id       INT PRIMARY KEY,
    freelancer_name     VARCHAR(100) NOT NULL,
    freelancer_email    VARCHAR(100) UNIQUE NOT NULL,
    freelancer_registration_date DATE NOT NULL
);

-- 3. Skills Table
CREATE TABLE Skills (
    skill_id            INT PRIMARY KEY,
    skill_name          VARCHAR(100) UNIQUE NOT NULL,
    skill_description   VARCHAR(255),
    skill_category      VARCHAR(50)
);

-- 4. Projects Table (using ENUM)
CREATE TABLE Projects (
    project_id          INT PRIMARY KEY,
    client_id           INT NOT NULL,
    project_title       VARCHAR(255) NOT NULL,
    project_description TEXT,
    start_date          DATE,
    end_date            DATE,
    budget              DECIMAL(10, 2) NOT NULL CHECK (budget > 0),
    project_status      ENUM('Open', 'In Progress', 'Completed', 'Canceled') NOT NULL DEFAULT 'Open',
    FOREIGN KEY (client_id) REFERENCES Client(client_id)
);

-- 5. Payments Table (using ENUM)
CREATE TABLE Payments (
    payment_id          INT PRIMARY KEY,
    project_id          INT NOT NULL,
    amount              DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    payment_date        DATE NOT NULL,
    payment_status      ENUM('Pending', 'Completed', 'Failed') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
);

-- 6. Proposals Table (using ENUM for proposal_status)
CREATE TABLE Proposals (
    proposal_id         INT PRIMARY KEY,
    project_id          INT NOT NULL,
    freelancer_id       INT NOT NULL,
    proposal_date       DATE NOT NULL,
    cover_letter        TEXT,
    expected_payment    DECIMAL(10, 2) NOT NULL CHECK (expected_payment > 0),
    proposal_status     ENUM('Pending', 'Accepted', 'Rejected') NOT NULL DEFAULT 'Pending',
    UNIQUE (project_id, freelancer_id),
    FOREIGN KEY (project_id) REFERENCES Projects(project_id),
    FOREIGN KEY (freelancer_id) REFERENCES Freelancers(freelancer_id)
);

-- 7. Reviews Table
CREATE TABLE Reviews (
    review_id           INT PRIMARY KEY,
    client_id           INT NOT NULL,
    freelancer_id       INT NOT NULL,
    rating              INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comments            TEXT,
    review_date         DATE NOT NULL,
    UNIQUE (client_id, freelancer_id),
    FOREIGN KEY (client_id) REFERENCES Client(client_id),
    FOREIGN KEY (freelancer_id) REFERENCES Freelancers(freelancer_id)
);

-- 8. Freelancer_Skills Table (Junction Table)
CREATE TABLE Freelancer_Skills (
    freelancer_id       INT NOT NULL,
    skill_id            INT NOT NULL,
    PRIMARY KEY (freelancer_id, skill_id),
    FOREIGN KEY (freelancer_id) REFERENCES Freelancers(freelancer_id),
    FOREIGN KEY (skill_id) REFERENCES Skills(skill_id)
);
