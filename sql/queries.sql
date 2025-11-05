USE Freelancer_Client_Marketplace;

-- ==================== SELECT QUERIES ====================

-- List all Clients
SELECT * FROM Client;

-- List all freelancers who registered after April 2025
SELECT * FROM Freelancers WHERE freelancer_registration_date > '2025-04-01';

-- Find all projects with status 'Open'
SELECT * FROM Projects WHERE project_status = 'Open';

-- Get all freelancers and their skills
SELECT f.freelancer_name, s.skill_name
FROM Freelancers f
JOIN Freelancer_Skills fs ON f.freelancer_id = fs.freelancer_id
JOIN Skills s ON fs.skill_id = s.skill_id
ORDER BY f.freelancer_name;

-- Count number of projects per client
SELECT c.client_name, COUNT(p.project_id) AS total_projects
FROM Client c
LEFT JOIN Projects p ON c.client_id = p.client_id
GROUP BY c.client_id
ORDER BY total_projects DESC;

-- Show all proposals related to 'E-commerce Website' project
SELECT p.proposal_id, f.freelancer_name, p.cover_letter, p.proposal_status
FROM Proposals p
JOIN Freelancers f ON p.freelancer_id = f.freelancer_id
JOIN Projects pr ON p.project_id = pr.project_id
WHERE pr.project_title = 'E-commerce Website';

-- For each freelancer, list total number of reviews and average rating
SELECT f.freelancer_name, 
       COUNT(r.review_id) AS review_count, 
       COALESCE(AVG(r.rating), 0) AS avg_rating
FROM Freelancers f
LEFT JOIN Reviews r ON f.freelancer_id = r.freelancer_id
GROUP BY f.freelancer_id
ORDER BY avg_rating DESC;

-- Find total payments (sum) received for each project (with project title)
SELECT pr.project_title, 
       COUNT(pay.payment_id) AS num_payments,
       SUM(pay.amount) AS total_payments
FROM Projects pr
LEFT JOIN Payments pay ON pr.project_id = pay.project_id
GROUP BY pr.project_id
HAVING total_payments > 0
ORDER BY total_payments DESC;

-- List all projects that have not ended yet
SELECT * FROM Projects 
WHERE end_date IS NULL OR end_date > CURDATE()
ORDER BY start_date;

-- List freelancers who have never received a review
SELECT freelancer_name, freelancer_email
FROM Freelancers
WHERE freelancer_id NOT IN (SELECT freelancer_id FROM Reviews);

-- List clients and total paid payments for their projects
SELECT c.client_name, 
       COALESCE(SUM(pay.amount), 0) AS total_paid
FROM Client c
LEFT JOIN Projects p ON c.client_id = p.client_id
LEFT JOIN Payments pay ON p.project_id = pay.project_id
WHERE pay.payment_status = 'Completed' OR pay.payment_status IS NULL
GROUP BY c.client_id
ORDER BY total_paid DESC;

-- List all projects involving freelancers with the skill 'Web Development'
SELECT DISTINCT pr.project_title, pr.project_status
FROM Projects pr
JOIN Proposals prop ON pr.project_id = prop.project_id
JOIN Freelancer_Skills fs ON prop.freelancer_id = fs.freelancer_id
JOIN Skills s ON fs.skill_id = s.skill_id
WHERE s.skill_name = 'Web Development';

-- Find freelancers who have more than one skill
SELECT f.freelancer_name, COUNT(fs.skill_id) AS skill_count
FROM Freelancers f
JOIN Freelancer_Skills fs ON f.freelancer_id = fs.freelancer_id
GROUP BY f.freelancer_id
HAVING COUNT(fs.skill_id) > 1
ORDER BY skill_count DESC;

-- Find projects with pending or failed payments
SELECT DISTINCT pr.project_title, pr.project_status, pay.payment_status
FROM Projects pr
JOIN Payments pay ON pr.project_id = pay.project_id
WHERE pay.payment_status IN ('Pending', 'Failed');

-- List clients with more than one project
SELECT c.client_name, COUNT(p.project_id) AS projects
FROM Client c
JOIN Projects p ON c.client_id = p.client_id
GROUP BY c.client_id
HAVING COUNT(p.project_id) > 1
ORDER BY projects DESC;

-- List proposals where expected payment exceeds project budget
SELECT prop.proposal_id, pr.project_title, 
       prop.expected_payment, pr.budget,
       (prop.expected_payment - pr.budget) AS excess_amount
FROM Proposals prop
JOIN Projects pr ON prop.project_id = pr.project_id
WHERE prop.expected_payment > pr.budget;

-- Display freelancer(s) with the highest average rating
SELECT f.freelancer_name, AVG(r.rating) AS avg_rating
FROM Freelancers f
JOIN Reviews r ON f.freelancer_id = r.freelancer_id
GROUP BY f.freelancer_id
HAVING AVG(r.rating) = (
    SELECT MAX(sub.avg_rating)
    FROM (
        SELECT AVG(r2.rating) AS avg_rating
        FROM Reviews r2
        GROUP BY r2.freelancer_id
    ) sub
);

-- List each project along with its client and assigned freelancers (if any)
SELECT pr.project_title, c.client_name, 
       f.freelancer_name, prop.proposal_status
FROM Projects pr
JOIN Client c ON pr.client_id = c.client_id
LEFT JOIN Proposals prop ON pr.project_id = prop.project_id
LEFT JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
ORDER BY pr.project_id;

-- Count of each unique skill among all freelancers
SELECT s.skill_name, COUNT(fs.freelancer_id) AS freelancer_count
FROM Skills s
LEFT JOIN Freelancer_Skills fs ON s.skill_id = fs.skill_id
GROUP BY s.skill_id
ORDER BY freelancer_count DESC;

-- Projects where at least one review exists for the working freelancer
SELECT DISTINCT pr.project_title
FROM Projects pr
JOIN Proposals prop ON pr.project_id = prop.project_id
JOIN Reviews rev ON prop.freelancer_id = rev.freelancer_id 
    AND pr.client_id = rev.client_id;

-- Show projects with accepted proposals and their freelancers
SELECT p.project_title, f.freelancer_name, 
       prop.expected_payment, p.project_status
FROM Projects p
JOIN Proposals prop ON p.project_id = prop.project_id
JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
WHERE prop.proposal_status = 'Accepted'
ORDER BY p.project_id;

-- ==================== UPDATE QUERIES ====================

-- Update client email address
UPDATE Client 
SET client_email = 'alice.j.new@example.com'
WHERE client_id = 1;

-- Update freelancer profile information
UPDATE Freelancers
SET freelancer_name = 'Michael J. Smith',
    freelancer_email = 'michael.j.smith@example.com'
WHERE freelancer_id = 1;

-- Update project budget and end date
UPDATE Projects
SET budget = 16000.00,
    end_date = '2025-05-30'
WHERE project_id = 1;

-- Update project status to Completed
UPDATE Projects
SET project_status = 'Completed',
    end_date = '2025-10-20'
WHERE project_id = 11;

-- Update proposal cover letter
UPDATE Proposals
SET cover_letter = 'Updated: Experienced web developer with 7+ years building e-commerce platforms using React and Node.js.'
WHERE proposal_id = 1;

-- Update proposal expected payment (for pending proposals only)
UPDATE Proposals
SET expected_payment = 17000.00
WHERE proposal_id = 3 AND proposal_status = 'Pending';

-- Update payment status to Completed
UPDATE Payments
SET payment_status = 'Completed'
WHERE payment_id = 2;

-- Update skill description
UPDATE Skills
SET skill_description = 'Building modern, responsive, and scalable websites using latest frameworks'
WHERE skill_id = 1;

-- Update multiple clients' registration dates (bulk update)
UPDATE Client
SET client_registration_date = DATE_SUB(client_registration_date, INTERVAL 30 DAY)
WHERE client_id IN (1, 2, 3);

-- Update project status for all Open projects that started more than 30 days ago
UPDATE Projects
SET project_status = 'In Progress'
WHERE project_status = 'Open' 
  AND start_date < DATE_SUB(CURDATE(), INTERVAL 30 DAY)
  AND project_id IN (SELECT project_id FROM Proposals WHERE proposal_status = 'Accepted');

-- Update freelancer email domain for specific freelancers
UPDATE Freelancers
SET freelancer_email = REPLACE(freelancer_email, '@example.com', '@freelancepro.com')
WHERE freelancer_id IN (1, 2, 3);

-- Add skill to existing freelancer
INSERT INTO Freelancer_Skills (freelancer_id, skill_id)
VALUES (10, 3)
ON DUPLICATE KEY UPDATE freelancer_id = freelancer_id;

-- Update review comments
UPDATE Reviews
SET comments = 'Outstanding work! Exceeded all expectations with creative solutions and timely delivery.'
WHERE review_id = 1;

-- ==================== DELETE QUERIES ====================

-- Delete a specific pending proposal
DELETE FROM Proposals
WHERE proposal_id = 17 AND proposal_status = 'Pending';

-- Delete a specific skill assignment from a freelancer
DELETE FROM Freelancer_Skills
WHERE freelancer_id = 10 AND skill_id = 3;

-- Delete pending payments for canceled projects
DELETE FROM Payments
WHERE project_id IN (
    SELECT project_id FROM Projects WHERE project_status = 'Canceled'
) AND payment_status = 'Pending';

-- Delete a specific client who has no projects (safe delete)
DELETE FROM Client
WHERE client_id = 12 
  AND client_id NOT IN (SELECT DISTINCT client_id FROM Projects);

