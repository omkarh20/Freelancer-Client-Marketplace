USE Freelancer_Client_Marketplace;

-- Insert Clients (registration dates are before project creation)
INSERT INTO Client (client_id, client_name, client_email, client_registration_date) VALUES
(1, 'Alice Johnson', 'alice.johnson@example.com', '2024-01-15'),
(2, 'Bob Smith', 'bob.smith@example.com', '2024-02-20'),
(3, 'Catherine Lee', 'catherine.lee@example.com', '2024-03-05'),
(4, 'David Martinez', 'david.martinez@example.com', '2024-04-18'),
(5, 'Eva Brown', 'eva.brown@example.com', '2024-05-12'),
(6, 'Frank Wilson', 'frank.wilson@example.com', '2024-06-01'),
(7, 'Grace Taylor', 'grace.taylor@example.com', '2024-06-21'),
(8, 'Henry Moore', 'henry.moore@example.com', '2024-07-15'),
(9, 'Isabella Clark', 'isabella.clark@example.com', '2024-08-03'),
(10, 'Jack Walker', 'jack.walker@example.com', '2024-08-25'),
(11, 'Laura Davis', 'laura.davis@example.com', '2024-09-10'),
(12, 'Michael Chen', 'michael.chen@example.com', '2024-10-05');

-- Insert Freelancers (varied registration dates before proposals)
INSERT INTO Freelancers (freelancer_id, freelancer_name, freelancer_email, freelancer_registration_date) VALUES
(1, 'Michael Smith', 'michael.smith@example.com', '2024-02-10'),
(2, 'Jennifer Johnson', 'jennifer.johnson@example.com', '2024-02-15'),
(3, 'William Brown', 'william.brown@example.com', '2024-03-01'),
(4, 'Sophia Davis', 'sophia.davis@example.com', '2024-03-10'),
(5, 'James Miller', 'james.miller@example.com', '2024-04-05'),
(6, 'Olivia Wilson', 'olivia.wilson@example.com', '2024-04-12'),
(7, 'Benjamin Moore', 'benjamin.moore@example.com', '2024-05-03'),
(8, 'Emily Taylor', 'emily.taylor@example.com', '2024-05-15'),
(9, 'Daniel Anderson', 'daniel.anderson@example.com', '2024-06-01'),
(10, 'Emma Thomas', 'emma.thomas@example.com', '2024-06-20'),
(11, 'Ryan Garcia', 'ryan.garcia@example.com', '2024-07-10'),
(12, 'Sophia Martinez', 'sophia.martinez@example.com', '2024-08-15');

-- Insert Skills
INSERT INTO Skills (skill_id, skill_name, skill_description, skill_category) VALUES
(1, 'Web Development', 'Building responsive and dynamic websites', 'Development'),
(2, 'Graphic Design', 'Creating visual content and graphics', 'Design'),
(3, 'Data Analysis', 'Analyzing and interpreting complex data sets', 'Analytics'),
(4, 'Digital Marketing', 'Promoting brands through digital channels', 'Marketing'),
(5, 'Content Writing', 'Writing engaging articles, blogs, and copy', 'Writing'),
(6, 'Mobile App Development', 'Developing applications for mobile devices', 'Development'),
(7, 'SEO Optimization', 'Improving website rankings in search engines', 'Marketing'),
(8, 'Video Editing', 'Editing and producing video content', 'Design'),
(9, 'Customer Support', 'Providing support and assistance to customers', 'Support'),
(10, 'Project Management', 'Planning and managing projects efficiently', 'Management'),
(11, 'UI/UX Design', 'Designing user interfaces and experiences', 'Design'),
(12, 'Database Management', 'Managing and optimizing databases', 'Development');

-- Insert Projects (varied per client, consistent dates)
INSERT INTO Projects (project_id, client_id, project_title, project_description, start_date, end_date, budget, project_status) VALUES
-- Client 1 (Alice) - 3 projects
(1, 1, 'E-commerce Website', 'Develop a fully functional online store with payment gateway.', '2025-01-20', '2025-04-30', 15000.00, 'In Progress'),
(2, 1, 'Mobile Shopping App', 'Create a companion mobile app for the e-commerce store.', '2025-06-01', NULL, 20000.00, 'Open'),
(3, 1, 'Brand Redesign', 'Complete brand identity redesign including logo and materials.', '2024-11-10', '2025-01-15', 5000.00, 'Completed'),

-- Client 2 (Bob) - 1 project
(4, 2, 'Brand Logo Design', 'Create a new logo and branding materials for a startup.', '2025-10-10', '2025-11-10', 2000.00, 'Open'),

-- Client 3 (Catherine) - 2 projects
(5, 3, 'Data Analytics Dashboard', 'Build a dashboard to visualize sales and customer data.', '2025-02-15', '2025-05-15', 8000.00, 'Completed'),
(6, 3, 'Sales Forecasting Tool', 'AI-powered sales prediction system.', '2025-08-01', NULL, 12000.00, 'Open'),

-- Client 4 (David) - 2 projects
(7, 4, 'Social Media Campaign', 'Run a marketing campaign across Facebook and Instagram.', '2025-03-10', '2025-06-30', 5000.00, 'In Progress'),
(8, 4, 'Website SEO Optimization', 'Improve website ranking with SEO best practices.', '2025-07-20', '2025-09-20', 3500.00, 'Completed'),

-- Client 5 (Eva) - 1 project
(9, 5, 'Mobile App for Booking', 'Develop a mobile app for booking services on-demand.', '2025-09-01', '2026-01-15', 18000.00, 'Open'),

-- Client 6 (Frank) - 1 project  
(10, 6, 'Corporate Website', 'Professional corporate website with CMS.', '2024-12-01', '2025-03-15', 7000.00, 'Completed'),

-- Client 7 (Grace) - 2 projects
(11, 7, 'Video Editing for Ads', 'Edit promotional videos for online advertising.', '2025-05-05', '2025-08-30', 4000.00, 'In Progress'),
(12, 7, 'Social Media Content', 'Create engaging social media content package.', '2025-10-01', NULL, 3000.00, 'Open'),

-- Client 8 (Henry) - 1 project
(13, 8, 'Content Writing for Blog', 'Produce regular blog articles on industry topics.', '2025-04-01', '2025-10-31', 3000.00, 'In Progress'),

-- Client 9 (Isabella) - 1 project
(14, 9, 'Customer Support Setup', 'Set up a customer support system with ticketing.', '2025-08-15', '2025-10-15', 6000.00, 'Open'),

-- Client 10 (Jack) - 2 projects
(15, 10, 'Project Management Tool', 'Develop an internal tool to manage projects efficiently.', '2025-09-05', NULL, 12000.00, 'Open'),
(16, 10, 'Inventory System', 'Database-driven inventory management system.', '2025-07-01', '2025-09-30', 9000.00, 'Completed');

-- Insert Freelancer_Skills (varied - some have 1, some have 5)
INSERT INTO Freelancer_Skills (freelancer_id, skill_id) VALUES
-- Michael Smith: 5 skills
(1, 1), (1, 7), (1, 11), (1, 12), (1, 6),
-- Jennifer Johnson: 2 skills
(2, 2), (2, 8),
-- William Brown: 3 skills
(3, 3), (3, 10), (3, 12),
-- Sophia Davis: 2 skills
(4, 4), (4, 7),
-- James Miller: 1 skill
(5, 6),
-- Olivia Wilson: 3 skills
(6, 5), (6, 9), (6, 4),
-- Benjamin Moore: 4 skills
(7, 1), (7, 3), (7, 11), (7, 12),
-- Emily Taylor: 2 skills
(8, 5), (8, 2),
-- Daniel Anderson: 2 skills
(9, 9), (9, 4),
-- Emma Thomas: 1 skill
(10, 10),
-- Ryan Garcia: 3 skills
(11, 1), (11, 6), (11, 11),
-- Sophia Martinez: 2 skills
(12, 2), (12, 11);

-- Insert Proposals (multiple proposals for some projects, none for others)
-- Dates are after project start, before acceptance
INSERT INTO Proposals (proposal_id, project_id, freelancer_id, proposal_date, cover_letter, expected_payment, proposal_status) VALUES
-- Project 1 (E-commerce) - Accepted proposal
(1, 1, 1, '2025-01-18', 'Experienced web developer ready to build your e-commerce site with 5+ years experience.', 15000.00, 'Accepted'),
(2, 1, 7, '2025-01-19', 'Full-stack developer specializing in e-commerce solutions.', 14500.00, 'Rejected'),

-- Project 2 (Mobile Shopping App) - Multiple pending
(3, 2, 5, '2025-06-03', 'Mobile app developer experienced in e-commerce apps.', 18000.00, 'Pending'),
(4, 2, 11, '2025-06-04', 'Expert in React Native with portfolio of shopping apps.', 19500.00, 'Pending'),

-- Project 3 (Brand Redesign) - Completed project with accepted proposal
(5, 3, 2, '2024-11-08', 'Creative designer with strong branding portfolio.', 5000.00, 'Accepted'),

-- Project 4 (Brand Logo) - Multiple pending (just opened)
(6, 4, 2, '2025-10-11', 'Creative graphic designer eager to design your brand logo.', 1900.00, 'Pending'),
(7, 4, 12, '2025-10-12', 'Award-winning designer specializing in brand identity.', 2000.00, 'Pending'),
(8, 4, 8, '2025-10-13', 'Minimalist design specialist for modern brands.', 1800.00, 'Pending'),

-- Project 5 (Data Analytics) - Completed with accepted
(9, 5, 3, '2025-02-12', 'Data analyst with expertise in sales dashboards and BI tools.', 8000.00, 'Accepted'),

-- Project 6 (Sales Forecasting) - Pending proposals
(10, 6, 3, '2025-08-03', 'Data scientist with ML expertise for forecasting.', 11500.00, 'Pending'),

-- Project 7 (Social Media Campaign) - Accepted
(11, 7, 4, '2025-03-08', 'Digital marketing specialist to enhance your social media reach.', 5000.00, 'Accepted'),

-- Project 8 (SEO) - Completed with accepted
(12, 8, 4, '2025-07-18', 'SEO expert ready to boost your website visibility.', 3500.00, 'Accepted'),

-- Project 9 (Mobile Booking App) - Multiple pending
(13, 9, 5, '2025-09-03', 'Mobile app developer experienced in booking systems.', 17500.00, 'Pending'),
(14, 9, 11, '2025-09-05', 'Cross-platform app developer with 50+ apps published.', 18000.00, 'Pending'),

-- Project 10 (Corporate Website) - Completed with accepted
(15, 10, 1, '2024-11-28', 'Professional web developer for corporate sites.', 7000.00, 'Accepted'),

-- Project 11 (Video Editing) - Accepted
(16, 11, 2, '2025-05-03', 'Skilled video editor for your promotional ads.', 4000.00, 'Accepted'),

-- Project 12 (Social Media Content) - Pending
(17, 12, 8, '2025-10-03', 'Content creator with social media expertise.', 2800.00, 'Pending'),
(18, 12, 6, '2025-10-04', 'Professional writer and content strategist.', 3000.00, 'Pending'),

-- Project 13 (Content Writing) - Accepted
(19, 13, 8, '2025-03-30', 'Content writer specializing in industry blogs.', 3000.00, 'Accepted'),

-- Project 14 (Customer Support) - No proposals yet

-- Project 15 (Project Management Tool) - Pending
(20, 15, 10, '2025-09-07', 'Project manager offering efficient project tracking solutions.', 11500.00, 'Pending'),

-- Project 16 (Inventory System) - Completed with accepted
(21, 16, 7, '2025-06-28', 'Database expert for inventory management systems.', 9000.00, 'Accepted');

-- Insert Payments (only for projects that have started or completed)
-- Payment dates are after project start, status matches project status
INSERT INTO Payments (payment_id, project_id, amount, payment_date, payment_status) VALUES
-- Project 1 (In Progress) - Partial payment
(1, 1, 7500.00, '2025-02-01', 'Completed'),
(2, 1, 5000.00, '2025-10-15', 'Pending'),

-- Project 3 (Completed) - Full payment
(3, 3, 5000.00, '2025-01-18', 'Completed'),

-- Project 5 (Completed) - Full payment
(4, 5, 8000.00, '2025-05-20', 'Completed'),

-- Project 7 (In Progress) - Partial payment
(5, 7, 2500.00, '2025-04-15', 'Completed'),
(6, 7, 1000.00, '2025-10-10', 'Pending'),

-- Project 8 (Completed) - Full payment
(7, 8, 3500.00, '2025-09-25', 'Completed'),

-- Project 10 (Completed) - Full payment
(8, 10, 7000.00, '2025-03-20', 'Completed'),

-- Project 11 (In Progress) - Partial payment
(9, 11, 2000.00, '2025-06-15', 'Completed'),
(10, 11, 1500.00, '2025-10-05', 'Pending'),

-- Project 13 (In Progress) - Partial payment
(11, 13, 1500.00, '2025-05-15', 'Completed'),

-- Project 16 (Completed) - Full payment
(12, 16, 9000.00, '2025-10-05', 'Completed');

-- Insert Reviews (only for completed projects, dates after project end)
INSERT INTO Reviews (review_id, client_id, freelancer_id, rating, comments, review_date) VALUES
(1, 1, 2, 5, 'Excellent brand redesign work, very creative and professional.', '2025-01-20'),
(2, 3, 3, 5, 'Data analysis was thorough and insightful. Dashboard exceeded expectations.', '2025-05-20'),
(3, 4, 4, 4, 'Great SEO work, our traffic improved significantly within 2 months.', '2025-09-30'),
(4, 6, 1, 5, 'Professional corporate website delivered on time with great attention to detail.', '2025-03-25'),
(5, 10, 7, 5, 'Inventory system works flawlessly. Very satisfied with the database design.', '2025-10-10');
