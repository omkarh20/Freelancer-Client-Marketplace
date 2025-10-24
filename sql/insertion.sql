USE Freelancer_Client_Marketplace;

INSERT INTO Client (client_id, client_name, client_email, client_registration_date) VALUES
(1, 'Alice Johnson', 'alice.johnson@example.com', '2025-01-15'),
(2, 'Bob Smith', 'bob.smith@example.com', '2025-02-20'),
(3, 'Catherine Lee', 'catherine.lee@example.com', '2025-03-05'),
(4, 'David Martinez', 'david.martinez@example.com', '2025-04-18'),
(5, 'Eva Brown', 'eva.brown@example.com', '2025-05-12'),
(6, 'Frank Wilson', 'frank.wilson@example.com', '2025-06-01'),
(7, 'Grace Taylor', 'grace.taylor@example.com', '2025-06-21'),
(8, 'Henry Moore', 'henry.moore@example.com', '2025-07-15'),
(9, 'Isabella Clark', 'isabella.clark@example.com', '2025-08-03'),
(10, 'Jack Walker', 'jack.walker@example.com', '2025-08-25');

INSERT INTO Freelancers (freelancer_id, freelancer_name, freelancer_email, freelancer_registration_date) VALUES
(1, 'Michael Smith', 'michael.smith@example.com', '2025-02-10'),
(2, 'Jennifer Johnson', 'jennifer.johnson@example.com', '2025-02-15'),
(3, 'William Brown', 'william.brown@example.com', '2025-03-01'),
(4, 'Sophia Davis', 'sophia.davis@example.com', '2025-03-10'),
(5, 'James Miller', 'james.miller@example.com', '2025-04-05'),
(6, 'Olivia Wilson', 'olivia.wilson@example.com', '2025-04-12'),
(7, 'Benjamin Moore', 'benjamin.moore@example.com', '2025-05-03'),
(8, 'Emily Taylor', 'emily.taylor@example.com', '2025-05-15'),
(9, 'Daniel Anderson', 'daniel.anderson@example.com', '2025-06-01'),
(10, 'Emma Thomas', 'emma.thomas@example.com', '2025-06-20');

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
(10, 'Project Management', 'Planning and managing projects efficiently', 'Management');

INSERT INTO Projects (project_id, client_id, project_title, project_description, start_date, end_date, budget, project_status) VALUES
(1, 1, 'E-commerce Website', 'Develop a fully functional online store with payment gateway.', '2025-09-01', '2025-11-30', 15000.00, 'In Progress'),
(2, 2, 'Brand Logo Design', 'Create a new logo and branding materials for a startup.', '2025-10-10', '2025-10-25', 2000.00, 'Open'),
(3, 3, 'Data Analytics Dashboard', 'Build a dashboard to visualize sales and customer data.', '2025-08-15', '2025-10-15', 8000.00, 'Completed'),
(4, 4, 'Social Media Campaign', 'Run a marketing campaign across Facebook and Instagram.', '2025-09-10', NULL, 5000.00, 'In Progress'),
(5, 5, 'Mobile App for Booking', 'Develop a mobile app for booking services on-demand.', '2025-10-01', '2026-01-15', 18000.00, 'Open'),
(6, 6, 'SEO Optimization', 'Improve website ranking with SEO best practices.', '2023-07-20', '2025-09-20', 3500.00, 'Completed'),
(7, 7, 'Video Editing for Ads', 'Edit promotional videos for online advertising.', '2025-09-05', NULL, 4000.00, 'In Progress'),
(8, 8, 'Content Writing for Blog', 'Produce regular blog articles on industry topics.', '2025-08-01', '2025-12-31', 3000.00, 'In Progress'),
(9, 9, 'Customer Support Setup', 'Set up a customer support system with ticketing.', '2025-09-15', '2025-11-15', 6000.00, 'Open'),
(10, 10, 'Project Management Tool', 'Develop an internal tool to manage projects efficiently.', '2025-10-05', NULL, 12000.00, 'Open');

INSERT INTO Freelancer_Skills (freelancer_id, skill_id) VALUES
(1, 1),  -- Michael Smith: Web Development
(1, 7),  -- Michael Smith: SEO Optimization
(2, 2),  -- Jennifer Johnson: Graphic Design
(2, 8),  -- Jennifer Johnson: Video Editing
(3, 3),  -- William Brown: Data Analysis
(3, 10), -- William Brown: Project Management
(4, 4),  -- Sophia Davis: Digital Marketing
(4, 7),  -- Sophia Davis: SEO Optimization
(5, 6),  -- James Miller: Mobile App Development
(6, 5),  -- Olivia Wilson: Content Writing
(6, 9),  -- Olivia Wilson: Customer Support
(7, 1),  -- Benjamin Moore: Web Development
(7, 3),  -- Benjamin Moore: Data Analysis
(8, 5),  -- Emily Taylor: Content Writing
(8, 2),  -- Emily Taylor: Graphic Design
(9, 9),  -- Daniel Anderson: Customer Support
(9, 4),  -- Daniel Anderson: Digital Marketing
(10, 10); -- Emma Thomas: Project Management

INSERT INTO Payments (payment_id, project_id, amount, payment_date, payment_status) VALUES
(1, 1, 5000.00, '2025-09-15', 'Completed'),
(2, 3, 8000.00, '2025-10-20', 'Completed'),
(3, 6, 3500.00, '2025-08-15', 'Completed'),
(4, 2, 1000.00, '2025-10-20', 'Pending'),
(5, 4, 1500.00, '2025-09-25', 'Completed'),
(6, 5, 6000.00, '2025-10-10', 'Pending'),
(7, 7, 2000.00, '2025-09-15', 'Failed'),
(8, 8, 1200.00, '2025-08-10', 'Completed'),
(9, 9, 3000.00, '2025-10-05', 'Pending'),
(10, 10, 4000.00, '2025-10-15', 'Pending');

INSERT INTO Proposals (proposal_id, project_id, freelancer_id, proposal_date, cover_letter, expected_payment) VALUES
(1, 1, 1, '2025-08-25', 'Experienced web developer ready to build your e-commerce site.', 14000.00),
(2, 2, 2, '2025-10-05', 'Creative graphic designer eager to design your brand logo.', 1900.00),
(3, 3, 3, '2025-08-10', 'Data analyst with expertise in sales dashboards.', 7500.00),
(4, 4, 4, '2025-09-01', 'Digital marketing specialist to enhance your social media reach.', 4800.00),
(5, 5, 5, '2025-09-28', 'Mobile app developer experienced in booking systems.', 17500.00),
(6, 6, 6, '2025-07-15', 'SEO expert ready to boost your website visibility.', 3400.00),
(7, 7, 2, '2025-09-01', 'Skilled video editor for your promotional ads.', 3900.00),
(8, 8, 8, '2025-07-25', 'Content writer specializing in industry blogs.', 2800.00),
(9, 9, 9, '2025-09-10', 'Customer support specialist to streamline your service.', 5800.00),
(10, 10, 10, '2025-09-20', 'Project manager offering efficient project tracking solutions.', 11500.00);

INSERT INTO Reviews (review_id, client_id, freelancer_id, rating, comments, review_date) VALUES
(1, 1, 1, 5, 'Excellent work on the e-commerce site, delivered on time.', '2025-12-02'),
(2, 2, 2, 4, 'Great logo design, met our expectations.', '2025-11-15'),
(3, 3, 3, 5, 'Data analysis was thorough and insightful.', '2025-10-30'),
(4, 4, 4, 3, 'Good efforts on social media campaign but room for improvement.', '2025-11-20'),
(5, 5, 5, 5, 'Mobile app works flawlessly, very satisfied.', '2025-01-18'),
(6, 6, 6, 4, 'SEO optimization improved traffic significantly.', '2025-10-05'),
(7, 7, 2, 3, 'Video editing was decent but required some revisions.', '2025-10-20'),
(8, 8, 8, 5, 'High quality and engaging blog content provided.', '2025-12-10'),
(9, 9, 9, 4, 'Customer support setup was efficient and responsive.', '2025-11-25'),
(10, 10, 10, 5, 'Project management tool streamlined our workflows.', '2025-01-05');

