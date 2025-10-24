-- This file contains all database setup including views, procedures, functions, and triggers

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
    COUNT(DISTINCT prop.freelancer_id) AS total_proposals
FROM Client c
LEFT JOIN Projects p ON c.client_id = p.client_id
LEFT JOIN Proposals prop ON p.project_id = prop.project_id
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
    AVG(r.rating) AS avg_rating,
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
    c.client_name,
    c.client_email
FROM Projects p
JOIN Client c ON p.client_id = c.client_id;

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

-- Procedure: Get Project Proposals
DELIMITER //
CREATE PROCEDURE get_project_proposals(IN input_project_id INT)
BEGIN
    SELECT 
        prop.proposal_id,
        f.freelancer_name,
        prop.proposal_date,
        prop.expected_payment,
        prop.cover_letter
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
        p.project_title,
        pay.amount,
        pay.payment_date,
        pay.payment_status
    FROM Payments pay
    JOIN Projects p ON pay.project_id = p.project_id
    WHERE p.client_id = input_client_id
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

-- ==================== FUNCTIONS ====================

-- Function: Calculate Freelancer Average Rating
DELIMITER //
CREATE FUNCTION get_avg_rating(input_freelancer_id INT)
RETURNS DECIMAL(3,2)
DETERMINISTIC
BEGIN
    DECLARE avg_rating DECIMAL(3,2);
    SELECT AVG(rating) INTO avg_rating
    FROM Reviews
    WHERE freelancer_id = input_freelancer_id;
    RETURN COALESCE(avg_rating, 0);
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

-- ==================== TRIGGERS ====================

-- Trigger: Update project status when payment is completed
DELIMITER //
CREATE TRIGGER after_payment_update
AFTER UPDATE ON Payments
FOR EACH ROW
BEGIN
    IF NEW.payment_status = 'Completed' AND OLD.payment_status != 'Completed' THEN
        -- Log or perform additional actions
        INSERT INTO payment_logs (payment_id, status_change_date) 
        VALUES (NEW.payment_id, NOW());
    END IF;
END //
DELIMITER ;

-- Note: Create payment_logs table if trigger is to be used
-- CREATE TABLE IF NOT EXISTS payment_logs (
--     log_id INT AUTO_INCREMENT PRIMARY KEY,
--     payment_id INT,
--     status_change_date DATETIME
-- );
