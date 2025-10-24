USE Freelancer_Client_Marketplace;

-- List all Clients
SELECT * FROM Client;

-- List all freelancers who registered after April 2025
SELECT * FROM freelancers WHERE freelancer_registration_date > '2025-04-01';

-- Find all projects with status 'Open'
SELECT * FROM Projects WHERE project_status = 'Open';

-- Get all freelancers and their skills
SELECT f.freelancer_name, s.skill_name 
FROM Freelancers f 
JOIN Freelancer_Skills fs ON f.freelancer_id = fs.freelancer_id
JOIN Skills s ON fs.skill_id = s.skill_id;

-- Count number of projects per client
SELECT c.client_name, COUNT(p.project_id) AS total_projects
FROM Client c
LEFT JOIN Projects p ON c.client_id = p.client_id
GROUP BY c.client_id;

-- Show all proposals related to 'E-commerce Website' project
SELECT p.proposal_id, f.freelancer_name, p.cover_letter
FROM Proposals p
JOIN Freelancers f ON p.freelancer_id = f.freelancer_id
JOIN Projects pr ON p.project_id = pr.project_id
WHERE pr.project_title = 'E-commerce Website';

-- For each freelancer, list total number of reviews and average rating
SELECT f.freelancer_name, COUNT(r.review_id) AS review_count, AVG(r.rating) AS avg_rating
FROM Freelancers f
LEFT JOIN Reviews r ON f.freelancer_id = r.freelancer_id
GROUP BY f.freelancer_id;

-- Find total payments (sum) received for each project (with project title)
SELECT pr.project_title, COUNT(*) AS Num_payments,SUM(pay.amount) AS total_payments
FROM Projects pr
JOIN Payments pay ON pr.project_id = pay.project_id
GROUP BY pr.project_id;

-- List all projects that have not ended yet
SELECT * FROM Projects WHERE end_date IS NULL OR end_date > CURDATE();

-- List freelancers who have never received a review
SELECT freelancer_name
FROM Freelancers
WHERE freelancer_id NOT IN (SELECT freelancer_id FROM Reviews);

-- List clients and total paid payments for their projects
SELECT c.client_name, SUM(pay.amount) AS total_paid
FROM Client c
JOIN Projects p ON c.client_id = p.client_id
JOIN Payments pay ON p.project_id = pay.project_id
WHERE pay.payment_status = 'Completed'
GROUP BY c.client_id;

-- List all projects involving freelancers with the skill 'Web Development'
SELECT DISTINCT pr.project_title
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
HAVING COUNT(fs.skill_id) > 1;

-- Find projects with pending or failed payments
SELECT DISTINCT pr.project_title
FROM Projects pr
JOIN Payments pay ON pr.project_id = pay.project_id
WHERE pay.payment_status IN ('Pending', 'Failed');

-- List clients with more than two projects
SELECT c.client_name, COUNT(p.project_id) AS projects
FROM Client c
JOIN Projects p ON c.client_id = p.client_id
GROUP BY c.client_id
HAVING COUNT(p.project_id) > 2;

-- List proposals where expected payment exceeds project budget
SELECT prop.proposal_id, pr.project_title, prop.expected_payment, pr.budget
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
SELECT pr.project_title, c.client_name, f.freelancer_name
FROM Projects pr
JOIN Client c ON pr.client_id = c.client_id
LEFT JOIN Proposals prop ON pr.project_id = prop.project_id
LEFT JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id;

-- Count of each unique skill among all freelancers
SELECT s.skill_name, COUNT(fs.freelancer_id) AS freelancer_count
FROM Skills s
LEFT JOIN Freelancer_Skills fs ON s.skill_id = fs.skill_id
GROUP BY s.skill_id;

-- Projects where at least one review exists for the working freelancer
SELECT DISTINCT pr.project_title
FROM Projects pr
JOIN Proposals prop ON pr.project_id = prop.project_id
JOIN Reviews rev ON prop.freelancer_id = rev.freelancer_id AND pr.client_id = rev.client_id;
