-- Enhanced Database Setup with Triggers, Procedures, Functions, and Views

USE Freelancer_Client_Marketplace;

-- ==================== VIEWS ====================

-- View: Client Projects Overview
CREATE OR REPLACE VIEW view_client_projects AS
SELECT 
    c.client_id,
    c.client_name,
    p.project_id,
    p.project_title,
    p.project_status,
    p.budget,
    COUNT(DISTINCT prop.freelancer_id) AS total_proposals,
    COUNT(DISTINCT CASE WHEN prop.proposal_status = 'Accepted' THEN prop.freelancer_id END) AS accepted_proposals,
    GROUP_CONCAT(DISTINCT CASE WHEN prop.proposal_status = 'Accepted' THEN f.freelancer_name END) AS assigned_freelancer
FROM Client c
LEFT JOIN Projects p ON c.client_id = p.client_id
LEFT JOIN Proposals prop ON p.project_id = prop.project_id
LEFT JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id AND prop.proposal_status = 'Accepted'
GROUP BY c.client_id, p.project_id;

-- View: Freelancer Active Projects
CREATE OR REPLACE VIEW view_freelancer_projects AS
SELECT 
    f.freelancer_id,
    f.freelancer_name,
    p.project_id,
    p.project_title,
    p.project_status,
    prop.expected_payment,
    prop.proposal_status,
    c.client_name
FROM Freelancers f
JOIN Proposals prop ON f.freelancer_id = prop.freelancer_id
JOIN Projects p ON prop.project_id = p.project_id
JOIN Client c ON p.client_id = c.client_id;

-- View: Freelancer Ratings
CREATE OR REPLACE VIEW view_freelancer_ratings AS
SELECT 
    f.freelancer_id,
    f.freelancer_name,
    COALESCE(AVG(r.rating), 0) AS avg_rating,
    COUNT(r.review_id) AS total_reviews
FROM Freelancers f
LEFT JOIN Reviews r ON f.freelancer_id = r.freelancer_id
GROUP BY f.freelancer_id;

-- View: Project Payment Status
CREATE OR REPLACE VIEW view_project_payments AS
SELECT 
    p.project_id,
    p.project_title,
    p.budget,
    COALESCE(SUM(pay.amount), 0) AS total_paid,
    p.budget - COALESCE(SUM(pay.amount), 0) AS remaining
FROM Projects p
LEFT JOIN Payments pay ON p.project_id = pay.project_id AND pay.payment_status = 'Completed'
GROUP BY p.project_id;

-- View: All Projects with Details
CREATE OR REPLACE VIEW view_all_projects AS
SELECT 
    p.project_id,
    p.project_title,
    p.project_description,
    p.budget,
    p.project_status,
    p.start_date,
    p.end_date,
    c.client_id,
    c.client_name,
    c.client_email,
    GROUP_CONCAT(DISTINCT CASE WHEN prop.proposal_status = 'Accepted' THEN f.freelancer_name END) AS assigned_freelancer
FROM Projects p
JOIN Client c ON p.client_id = c.client_id
LEFT JOIN Proposals prop ON p.project_id = prop.project_id AND prop.proposal_status = 'Accepted'
LEFT JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
GROUP BY p.project_id;

-- ==================== STORED PROCEDURES ====================

-- Procedure: Get Client Projects
DELIMITER //
CREATE PROCEDURE get_client_projects(IN input_client_id INT)
BEGIN
    SELECT * FROM view_client_projects WHERE client_id = input_client_id;
END //
DELIMITER ;

-- Procedure: Get Freelancer Projects
DELIMITER //
CREATE PROCEDURE get_freelancer_projects(IN input_freelancer_id INT)
BEGIN
    SELECT * FROM view_freelancer_projects WHERE freelancer_id = input_freelancer_id;
END //
DELIMITER ;

-- Procedure: Get Project Proposals with Status
DELIMITER //
CREATE PROCEDURE get_project_proposals(IN input_project_id INT)
BEGIN
    SELECT 
        prop.proposal_id,
        prop.freelancer_id,
        f.freelancer_name,
        f.freelancer_email,
        prop.proposal_date,
        prop.expected_payment,
        prop.cover_letter,
        prop.proposal_status
    FROM Proposals prop
    JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
    WHERE prop.project_id = input_project_id;
END //
DELIMITER ;

-- Procedure: Get Payment History
DELIMITER //
CREATE PROCEDURE get_payment_history(IN input_client_id INT)
BEGIN
    SELECT 
        pay.payment_id,
        p.project_id,
        p.project_title,
        pay.amount,
        pay.payment_date,
        pay.payment_status,
        GROUP_CONCAT(DISTINCT CASE WHEN prop.proposal_status = 'Accepted' THEN f.freelancer_name END) AS freelancer_name
    FROM Payments pay
    JOIN Projects p ON pay.project_id = p.project_id
    LEFT JOIN Proposals prop ON p.project_id = prop.project_id AND prop.proposal_status = 'Accepted'
    LEFT JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
    WHERE p.client_id = input_client_id
    GROUP BY pay.payment_id
    ORDER BY pay.payment_date DESC;
END //
DELIMITER ;

-- Procedure: Get Freelancer Reviews
DELIMITER //
CREATE PROCEDURE get_freelancer_reviews(IN input_freelancer_id INT)
BEGIN
    SELECT 
        r.review_id,
        c.client_name,
        r.rating,
        r.comments,
        r.review_date
    FROM Reviews r
    JOIN Client c ON r.client_id = c.client_id
    WHERE r.freelancer_id = input_freelancer_id
    ORDER BY r.review_date DESC;
END //
DELIMITER ;

-- Procedure: Add New Client
DELIMITER //
CREATE PROCEDURE add_client(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_reg_date DATE
)
BEGIN
    INSERT INTO Client (client_id, client_name, client_email, client_registration_date)
    VALUES (
        (SELECT COALESCE(MAX(client_id), 0) + 1 FROM Client AS c),
        p_name,
        p_email,
        p_reg_date
    );
END //
DELIMITER ;

-- Procedure: Add New Freelancer
DELIMITER //
CREATE PROCEDURE add_freelancer(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_reg_date DATE
)
BEGIN
    INSERT INTO Freelancers (freelancer_id, freelancer_name, freelancer_email, freelancer_registration_date)
    VALUES (
        (SELECT COALESCE(MAX(freelancer_id), 0) + 1 FROM Freelancers AS f),
        p_name,
        p_email,
        p_reg_date
    );
END //
DELIMITER ;

-- Procedure: Add New Project
DELIMITER //
CREATE PROCEDURE add_project(
    IN p_client_id INT,
    IN p_title VARCHAR(255),
    IN p_description TEXT,
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_budget DECIMAL(10,2),
    IN p_status VARCHAR(20)
)
BEGIN
    INSERT INTO Projects (project_id, client_id, project_title, project_description, 
                         start_date, end_date, budget, project_status)
    VALUES (
        (SELECT COALESCE(MAX(project_id), 0) + 1 FROM Projects AS pr),
        p_client_id,
        p_title,
        p_description,
        p_start_date,
        p_end_date,
        p_budget,
        p_status
    );
END //
DELIMITER ;

-- Procedure: Update Client Profile
DELIMITER //
CREATE PROCEDURE update_client_profile(
    IN p_client_id INT,
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100)
)
BEGIN
    UPDATE Client
    SET client_name = p_name,
        client_email = p_email
    WHERE client_id = p_client_id;
END //
DELIMITER ;

-- Procedure: Update Freelancer Profile
DELIMITER //
CREATE PROCEDURE update_freelancer_profile(
    IN p_freelancer_id INT,
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100)
)
BEGIN
    UPDATE Freelancers
    SET freelancer_name = p_name,
        freelancer_email = p_email
    WHERE freelancer_id = p_freelancer_id;
END //
DELIMITER ;

-- Procedure: Update Project
DELIMITER //
CREATE PROCEDURE update_project(
    IN p_project_id INT,
    IN p_title VARCHAR(255),
    IN p_description TEXT,
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_budget DECIMAL(10,2),
    IN p_status VARCHAR(20)
)
BEGIN
    UPDATE Projects
    SET project_title = p_title,
        project_description = p_description,
        start_date = p_start_date,
        end_date = p_end_date,
        budget = p_budget,
        project_status = p_status
    WHERE project_id = p_project_id;
END //
DELIMITER ;

-- Procedure: Update Proposal
DELIMITER //
CREATE PROCEDURE update_proposal(
    IN p_proposal_id INT,
    IN p_cover_letter TEXT,
    IN p_expected_payment DECIMAL(10,2)
)
BEGIN
    UPDATE Proposals
    SET cover_letter = p_cover_letter,
        expected_payment = p_expected_payment
    WHERE proposal_id = p_proposal_id;
END //
DELIMITER ;

-- Procedure: Accept Proposal
DELIMITER //
CREATE PROCEDURE accept_proposal(IN p_proposal_id INT)
BEGIN
    DECLARE v_project_id INT;
    
    SELECT project_id INTO v_project_id
    FROM Proposals
    WHERE proposal_id = p_proposal_id;
    
    UPDATE Proposals
    SET proposal_status = 'Accepted'
    WHERE proposal_id = p_proposal_id;
    
    UPDATE Proposals
    SET proposal_status = 'Rejected'
    WHERE project_id = v_project_id 
      AND proposal_id != p_proposal_id
      AND proposal_status = 'Pending';
    
    UPDATE Projects
    SET project_status = 'In Progress'
    WHERE project_id = v_project_id;
END //
DELIMITER ;

-- Procedure: Reject Proposal
DELIMITER //
CREATE PROCEDURE reject_proposal(IN p_proposal_id INT)
BEGIN
    UPDATE Proposals
    SET proposal_status = 'Rejected'
    WHERE proposal_id = p_proposal_id;
END //
DELIMITER ;

-- ==================== FUNCTIONS ====================

-- Function: Calculate Freelancer Average Rating
DELIMITER //
CREATE FUNCTION get_avg_rating(input_freelancer_id INT)
RETURNS DECIMAL(3,2)
DETERMINISTIC
BEGIN
    DECLARE avg_rating DECIMAL(3,2);
    SELECT COALESCE(AVG(rating), 0) INTO avg_rating
    FROM Reviews
    WHERE freelancer_id = input_freelancer_id;
    RETURN avg_rating;
END //
DELIMITER ;

-- Function: Count Active Projects for Client
DELIMITER //
CREATE FUNCTION count_active_projects(input_client_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE project_count INT;
    SELECT COUNT(*) INTO project_count
    FROM Projects
    WHERE client_id = input_client_id AND project_status IN ('Open', 'In Progress');
    RETURN project_count;
END //
DELIMITER ;

-- Function: Count Pending Proposals for Project
DELIMITER //
CREATE FUNCTION count_pending_proposals(input_project_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE proposal_count INT;
    SELECT COUNT(*) INTO proposal_count
    FROM Proposals
    WHERE project_id = input_project_id AND proposal_status = 'Pending';
    RETURN proposal_count;
END //
DELIMITER ;

-- ==================== TRIGGERS ====================

-- Trigger: Auto-update project status when proposal is accepted
DELIMITER //
CREATE TRIGGER after_proposal_accept
AFTER UPDATE ON Proposals
FOR EACH ROW
BEGIN
    IF NEW.proposal_status = 'Accepted' AND OLD.proposal_status != 'Accepted' THEN
        UPDATE Projects
        SET project_status = 'In Progress'
        WHERE project_id = NEW.project_id AND project_status = 'Open';
    END IF;
END //
DELIMITER ;

-- Trigger: Validate project budget on insert
DELIMITER //
CREATE TRIGGER before_project_insert
BEFORE INSERT ON Projects
FOR EACH ROW
BEGIN
    IF NEW.budget <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Project budget must be greater than 0';
    END IF;
END //
DELIMITER ;

-- Trigger: Validate payment amount
DELIMITER //
CREATE TRIGGER before_payment_insert
BEFORE INSERT ON Payments
FOR EACH ROW
BEGIN
    DECLARE project_budget DECIMAL(10,2);
    
    SELECT budget INTO project_budget
    FROM Projects
    WHERE project_id = NEW.project_id;
    
    IF NEW.amount > project_budget THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Payment amount cannot exceed project budget';
    END IF;
END //
DELIMITER ;

-- Trigger: Ensure review date is after project end date
DELIMITER //
CREATE TRIGGER before_review_insert
BEFORE INSERT ON Reviews
FOR EACH ROW
BEGIN
    DECLARE latest_project_end DATE;
    
    -- Get the latest end date of completed projects between this client and freelancer
    SELECT MAX(p.end_date) INTO latest_project_end
    FROM Projects p
    JOIN Proposals prop ON p.project_id = prop.project_id
    WHERE p.client_id = NEW.client_id 
      AND prop.freelancer_id = NEW.freelancer_id
      AND p.project_status = 'Completed'
      AND p.end_date IS NOT NULL;
    
    -- If a completed project exists, ensure review is after project end
    IF latest_project_end IS NOT NULL AND NEW.review_date < latest_project_end THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Review date cannot be before project end date';
    END IF;
END //
DELIMITER ;

-- Trigger: Prevent payment for projects that haven't started
DELIMITER //
CREATE TRIGGER validate_payment_project_status
BEFORE INSERT ON Payments
FOR EACH ROW
BEGIN
    DECLARE proj_status VARCHAR(20);
    DECLARE proj_start DATE;
    
    SELECT project_status, start_date INTO proj_status, proj_start
    FROM Projects
    WHERE project_id = NEW.project_id;
    
    -- Prevent completed payments for Open projects
    IF proj_status = 'Open' AND NEW.payment_status = 'Completed' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot mark payment as completed for projects that have not started';
    END IF;
    
    -- Ensure payment date is after project start
    IF NEW.payment_date < proj_start THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Payment date cannot be before project start date';
    END IF;
END //
DELIMITER ;

-- Trigger: Ensure client registration before project creation
DELIMITER //
CREATE TRIGGER validate_client_project_dates
BEFORE INSERT ON Projects
FOR EACH ROW
BEGIN
    DECLARE client_reg DATE;
    
    SELECT client_registration_date INTO client_reg
    FROM Client
    WHERE client_id = NEW.client_id;
    
    IF NEW.start_date < client_reg THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Project start date cannot be before client registration date';
    END IF;
END //
DELIMITER ;
