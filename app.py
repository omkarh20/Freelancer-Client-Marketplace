from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),  
    'database': 'Freelancer_Client_Marketplace'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# AUTHENTICATION ROUTES

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action', 'login')
        
        if action == 'login':
            role = request.form.get('role')
            
            if role == 'admin':
                password = request.form.get('admin_password')
                ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
                
                if password == ADMIN_PASSWORD:
                    session['role'] = 'admin'
                    session['user_id'] = None
                    return redirect(url_for('dashboard_admin'))
                else:
                    flash('Invalid admin password!', 'error')
                    return render_template('login.html', register_mode=False)
            else:
                user_id = request.form.get('user_id')
                if not user_id:
                    flash('Please enter your User ID', 'error')
                    return render_template('login.html', register_mode=False)
                
                session['role'] = role
                session['user_id'] = int(user_id)
                
                if role == 'client':
                    return redirect(url_for('dashboard_client'))
                elif role == 'freelancer':
                    return redirect(url_for('dashboard_freelancer'))
    
    return render_template('login.html', register_mode=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        reg_role = request.form.get('reg_role')
        reg_name = request.form.get('reg_name')
        reg_email = request.form.get('reg_email')
        reg_date = date.today()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if reg_role == 'client':
                cursor.callproc('add_client', [reg_name, reg_email, reg_date])
                conn.commit()
                
                # Get the new client_id
                cursor.execute("SELECT client_id FROM Client WHERE client_email = %s", (reg_email,))
                new_user = cursor.fetchone()
                
                flash(f'Registration successful! Your Client ID is {new_user[0]}. Please login.', 'success')
            
            elif reg_role == 'freelancer':
                cursor.callproc('add_freelancer', [reg_name, reg_email, reg_date])
                conn.commit()
                
                # Get the new freelancer_id
                cursor.execute("SELECT freelancer_id FROM Freelancers WHERE freelancer_email = %s", (reg_email,))
                new_user = cursor.fetchone()
                
                flash(f'Registration successful! Your Freelancer ID is {new_user[0]}. Please login.', 'success')
            
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
            
        except Error as e:
            conn.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            cursor.close()
            conn.close()
    
    return render_template('login.html', register_mode=True)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

# DASHBOARD ROUTES

@app.route('/dashboard/client')
def dashboard_client():
    if 'role' not in session or session['role'] != 'client':
        return redirect(url_for('login'))
    
    client_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Call stored procedure to get client projects
    cursor.callproc('get_client_projects', [client_id])
    projects = []
    for result in cursor.stored_results():
        projects = result.fetchall()
    projects = [p for p in projects if p['project_id'] is not None]
    
    # Get client info using cursor
    cursor.execute("SELECT * FROM Client WHERE client_id = %s", (client_id,))
    client = cursor.fetchone()
    
    # Get active projects count using function
    cursor.execute("SELECT count_active_projects(%s) AS active_count", (client_id,))
    active_count = cursor.fetchone()['active_count']
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard_client.html', 
                         client=client, 
                         projects=projects,
                         active_count=active_count)

@app.route('/dashboard/freelancer')
def dashboard_freelancer():
    if 'role' not in session or session['role'] != 'freelancer':
        return redirect(url_for('login'))
    
    freelancer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Call stored procedure
    cursor.callproc('get_freelancer_projects', [freelancer_id])
    projects = []
    for result in cursor.stored_results():
        projects = result.fetchall()
    projects = [p for p in projects if p['project_id'] is not None]

    # Get freelancer info
    cursor.execute("SELECT * FROM Freelancers WHERE freelancer_id = %s", (freelancer_id,))
    freelancer = cursor.fetchone()
    
    # Get average rating using function
    cursor.execute("SELECT get_avg_rating(%s) AS avg_rating", (freelancer_id,))
    avg_rating = cursor.fetchone()['avg_rating']
    
    # Get skills
    cursor.execute("""
        SELECT s.skill_name 
        FROM Skills s
        JOIN Freelancer_Skills fs ON s.skill_id = fs.skill_id
        WHERE fs.freelancer_id = %s
    """, (freelancer_id,))
    skills = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard_freelancer.html', 
                         freelancer=freelancer, 
                         projects=projects,
                         avg_rating=avg_rating,
                         skills=skills)

@app.route('/dashboard/admin')
def dashboard_admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get statistics using cursor
    cursor.execute("SELECT COUNT(*) AS total FROM Client")
    total_clients = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM Freelancers")
    total_freelancers = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM Projects")
    total_projects = cursor.fetchone()['total']
    
    cursor.execute("SELECT * FROM view_all_projects")
    all_projects = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard_admin.html', 
                         total_clients=total_clients,
                         total_freelancers=total_freelancers,
                         total_projects=total_projects,
                         projects=all_projects)

# PROJECT ROUTES

@app.route('/projects')
def projects():
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'client':
        cursor.execute("""
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT CASE WHEN prop.proposal_status = 'Accepted' 
                                THEN f.freelancer_name END) AS assigned_freelancer
            FROM Projects p
            LEFT JOIN Proposals prop ON p.project_id = prop.project_id
            LEFT JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
            WHERE p.client_id = %s
            GROUP BY p.project_id
            ORDER BY p.project_id DESC
        """, (session['user_id'],))
    elif session['role'] == 'freelancer':
        cursor.execute("""
            SELECT p.*, f.freelancer_name as assigned_freelancer
            FROM Projects p
            JOIN Proposals prop ON p.project_id = prop.project_id
            JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
            WHERE prop.freelancer_id = %s
            ORDER BY p.project_id DESC
        """, (session['user_id'],))
    else:  # admin
        cursor.execute("SELECT * FROM view_all_projects ORDER BY project_id DESC")
    
    projects = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('projects.html', projects=projects)

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if 'role' not in session or session['role'] != 'client':
        flash('Only clients can add projects', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date') if request.form.get('end_date') else None
        budget = float(request.form.get('budget'))
        status = 'Open'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Call stored procedure to add project
            cursor.callproc('add_project', [
                session['user_id'],
                title,
                description,
                start_date,
                end_date,
                budget,
                status
            ])
            conn.commit()
            flash('Project added successfully!', 'success')
            return redirect(url_for('projects'))
        except Error as e:
            conn.rollback()
            flash(f'Error adding project: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('add_project.html')

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get project details
    cursor.execute("SELECT * FROM Projects WHERE project_id = %s", (project_id,))
    project = cursor.fetchone()
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects'))
    
    # Check permissions
    if session['role'] == 'client' and project['client_id'] != session['user_id']:
        flash('You can only edit your own projects', 'error')
        return redirect(url_for('projects'))
    
    if session['role'] == 'freelancer':
        flash('Freelancers cannot edit projects', 'error')
        return redirect(url_for('projects'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date') if request.form.get('end_date') else None
        budget = float(request.form.get('budget'))
        status = request.form.get('status')
        
        try:
            # Call stored procedure to update project
            cursor.callproc('update_project', [
                project_id,
                title,
                description,
                start_date,
                end_date,
                budget,
                status
            ])
            conn.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects'))
        except Error as e:
            conn.rollback()
            flash(f'Error updating project: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    cursor.close()
    conn.close()
    return render_template('edit_project.html', project=project)

@app.route('/delete_project/<int:project_id>')
def delete_project(project_id):
    if 'role' not in session or session['role'] != 'client':
        flash('Only clients can delete projects', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check project ownership
    cursor.execute("SELECT client_id FROM Projects WHERE project_id = %s", (project_id,))
    project = cursor.fetchone()
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects'))
    
    if project['client_id'] != session['user_id']:
        flash('You can only delete your own projects', 'error')
        return redirect(url_for('projects'))
    
    try:
        # Delete related records first (due to foreign keys)
        cursor.execute("DELETE FROM Payments WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM Proposals WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM Projects WHERE project_id = %s", (project_id,))
        conn.commit()
        flash('Project deleted successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error deleting project: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('projects'))

@app.route('/available_projects')
def available_projects():
    if 'role' not in session or session['role'] != 'freelancer':
        flash('Only freelancers can view available projects', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.*, c.client_name,
               (SELECT COUNT(*) FROM Proposals WHERE project_id = p.project_id) as proposal_count
        FROM Projects p
        JOIN Client c ON p.client_id = c.client_id
        LEFT JOIN Proposals prop ON p.project_id = prop.project_id AND prop.freelancer_id = %s
        WHERE p.project_status = 'Open' AND prop.proposal_id IS NULL
        ORDER BY p.project_id DESC
    """, (session['user_id'],))
    
    projects = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('available_projects.html', projects=projects)

# PROPOSAL ROUTES

@app.route('/proposals')
def proposals():
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'freelancer':
        cursor.execute("""
            SELECT prop.*, p.project_title, p.budget 
            FROM Proposals prop
            JOIN Projects p ON prop.project_id = p.project_id
            WHERE prop.freelancer_id = %s
            ORDER BY prop.proposal_id DESC
        """, (session['user_id'],))
    elif session['role'] == 'client':
        cursor.execute("""
            SELECT prop.*, p.project_title, f.freelancer_name 
            FROM Proposals prop
            JOIN Projects p ON prop.project_id = p.project_id
            JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
            WHERE p.client_id = %s
            ORDER BY prop.proposal_id DESC
        """, (session['user_id'],))
    else:  # admin
        cursor.execute("""
            SELECT prop.*, p.project_title, f.freelancer_name, c.client_name 
            FROM Proposals prop
            JOIN Projects p ON prop.project_id = p.project_id
            JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
            JOIN Client c ON p.client_id = c.client_id
            ORDER BY prop.proposal_id DESC
        """)
    
    proposals = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('proposals.html', proposals=proposals)

@app.route('/edit_proposal/<int:proposal_id>', methods=['GET', 'POST'])
def edit_proposal(proposal_id):
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get proposal details
    cursor.execute("""
        SELECT prop.*, p.project_title 
        FROM Proposals prop
        JOIN Projects p ON prop.project_id = p.project_id
        WHERE prop.proposal_id = %s
    """, (proposal_id,))
    proposal = cursor.fetchone()
    
    if not proposal:
        flash('Proposal not found', 'error')
        return redirect(url_for('proposals'))
    
    # Check permissions
    if session['role'] == 'freelancer' and proposal['freelancer_id'] != session['user_id']:
        flash('You can only edit your own proposals', 'error')
        return redirect(url_for('proposals'))
    
    if session['role'] == 'client':
        flash('Clients cannot edit proposals', 'error')
        return redirect(url_for('proposals'))
    
    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter')
        expected_payment = float(request.form.get('expected_payment'))
        
        try:
            # Call stored procedure
            cursor.callproc('update_proposal', [
                proposal_id,
                cover_letter,
                expected_payment
            ])
            conn.commit()
            flash('Proposal updated successfully!', 'success')
            return redirect(url_for('proposals'))
        except Error as e:
            conn.rollback()
            flash(f'Error updating proposal: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    cursor.close()
    conn.close()
    return render_template('edit_proposal.html', proposal=proposal)

@app.route('/manage_proposals/<int:project_id>')
def manage_proposals(project_id):
    if 'role' not in session or session['role'] not in ['client', 'admin']:
        flash('Only clients can manage proposals', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get project details
    cursor.execute("SELECT * FROM Projects WHERE project_id = %s", (project_id,))
    project = cursor.fetchone()
    
    if session['role'] == 'client' and project['client_id'] != session['user_id']:
        flash('You can only manage proposals for your own projects', 'error')
        return redirect(url_for('projects'))
    
    # Get proposals using stored procedure
    cursor.callproc('get_project_proposals', [project_id])
    proposals = []
    for result in cursor.stored_results():
        proposals = result.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('manage_proposals.html', project=project, proposals=proposals)

@app.route('/accept_proposal/<int:proposal_id>')
def accept_proposal(proposal_id):
    if 'role' not in session or session['role'] not in ['client', 'admin']:
        flash('Only clients can accept proposals', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get proposal and project info
    cursor.execute("""
        SELECT prop.*, p.client_id, p.project_id
        FROM Proposals prop
        JOIN Projects p ON prop.project_id = p.project_id
        WHERE prop.proposal_id = %s
    """, (proposal_id,))
    proposal = cursor.fetchone()
    
    if not proposal:
        flash('Proposal not found', 'error')
        return redirect(url_for('proposals'))
    
    if session['role'] == 'client' and proposal['client_id'] != session['user_id']:
        flash('You can only accept proposals for your own projects', 'error')
        return redirect(url_for('proposals'))
    
    try:
        # Call stored procedure to accept proposal
        cursor.callproc('accept_proposal', [proposal_id])
        conn.commit()
        flash('Proposal accepted successfully! Other proposals have been rejected.', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error accepting proposal: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('manage_proposals', project_id=proposal['project_id']))

@app.route('/reject_proposal/<int:proposal_id>')
def reject_proposal(proposal_id):
    if 'role' not in session or session['role'] not in ['client', 'admin']:
        flash('Only clients can reject proposals', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get proposal and project info
    cursor.execute("""
        SELECT prop.*, p.client_id, p.project_id
        FROM Proposals prop
        JOIN Projects p ON prop.project_id = p.project_id
        WHERE prop.proposal_id = %s
    """, (proposal_id,))
    proposal = cursor.fetchone()
    
    if not proposal:
        flash('Proposal not found', 'error')
        return redirect(url_for('proposals'))
    
    if session['role'] == 'client' and proposal['client_id'] != session['user_id']:
        flash('You can only reject proposals for your own projects', 'error')
        return redirect(url_for('proposals'))
    
    try:
        # Call stored procedure to reject proposal
        cursor.callproc('reject_proposal', [proposal_id])
        conn.commit()
        flash('Proposal rejected successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error rejecting proposal: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('manage_proposals', project_id=proposal['project_id']))

@app.route('/submit_proposal/<int:project_id>', methods=['GET', 'POST'])
def submit_proposal(project_id):
    if 'role' not in session or session['role'] != 'freelancer':
        flash('Only freelancers can submit proposals', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter')
        expected_payment = float(request.form.get('expected_payment'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Check if freelancer already submitted a proposal for this project
            cursor.execute("""
                SELECT proposal_id FROM Proposals 
                WHERE project_id = %s AND freelancer_id = %s
            """, (project_id, session['user_id']))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                flash('You have already submitted a proposal for this project', 'error')
                return redirect(url_for('available_projects'))
            
            # Insert the proposal
            cursor.execute("""
                INSERT INTO Proposals (proposal_id, project_id, freelancer_id, proposal_date, 
                                      expected_payment, cover_letter, proposal_status)
                VALUES (
                    (SELECT COALESCE(MAX(proposal_id), 0) + 1 FROM Proposals AS p),
                    %s, %s, CURDATE(), %s, %s, 'Pending'
                )
            """, (project_id, session['user_id'], expected_payment, cover_letter))
            
            conn.commit()
            flash('Proposal submitted successfully!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('proposals'))
            
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f'Error submitting proposal: {str(e)}', 'error')
            return redirect(url_for('available_projects'))
    
    # GET request - show the proposal form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.*, c.client_name 
        FROM Projects p
        JOIN Client c ON p.client_id = c.client_id
        WHERE p.project_id = %s AND p.project_status = 'Open'
    """, (project_id,))
    
    project = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not project:
        flash('Project not found or not available', 'error')
        return redirect(url_for('available_projects'))
    
    return render_template('submit_proposal.html', project=project)

# PAYMENT ROUTES

@app.route('/payments')
def payments():
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'client':
        cursor.callproc('get_payment_history', [session['user_id']])
        payments = []
        for result in cursor.stored_results():
            payments = result.fetchall()
    elif session['role'] == 'freelancer':
        # Get payments for projects where freelancer has accepted proposals
        cursor.execute("""
            SELECT pay.*, p.project_title, f.freelancer_name
            FROM Payments pay
            JOIN Projects p ON pay.project_id = p.project_id
            JOIN Proposals prop ON p.project_id = prop.project_id
            JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
            WHERE prop.freelancer_id = %s AND prop.proposal_status = 'Accepted'
            ORDER BY pay.payment_id DESC
        """, (session['user_id'],))
        payments = cursor.fetchall()
    else:
        cursor.execute("""
            SELECT pay.*, p.project_title, c.client_name,
                   GROUP_CONCAT(DISTINCT CASE WHEN prop.proposal_status = 'Accepted' 
                                THEN f.freelancer_name END) AS freelancer_name
            FROM Payments pay
            JOIN Projects p ON pay.project_id = p.project_id
            JOIN Client c ON p.client_id = c.client_id
            LEFT JOIN Proposals prop ON p.project_id = prop.project_id
            LEFT JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
            GROUP BY pay.payment_id
            ORDER BY pay.payment_id DESC
        """)
        payments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('payments.html', payments=payments)

@app.route('/update_payment_status/<int:payment_id>')
def update_payment_status(payment_id):
    if 'role' not in session or session['role'] != 'freelancer':
        flash('Only freelancers can update payment status', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verify freelancer has access to this payment
    cursor.execute("""
        SELECT pay.* FROM Payments pay
        JOIN Projects p ON pay.project_id = p.project_id
        JOIN Proposals prop ON p.project_id = prop.project_id
        WHERE pay.payment_id = %s 
          AND prop.freelancer_id = %s 
          AND prop.proposal_status = 'Accepted'
    """, (payment_id, session['user_id']))
    payment = cursor.fetchone()
    
    if not payment:
        flash('Payment not found or access denied', 'error')
        return redirect(url_for('payments'))
    
    try:
        cursor.execute("""
            UPDATE Payments 
            SET payment_status = 'Completed'
            WHERE payment_id = %s
        """, (payment_id,))
        conn.commit()
        flash('Payment status updated to Completed', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error updating payment: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('payments'))

# REVIEW ROUTES

@app.route('/reviews')
def reviews():
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    completed_projects = []
    
    if session['role'] == 'freelancer':
        # Freelancers see only their own reviews
        cursor.callproc('get_freelancer_reviews', [session['user_id']])
        reviews = []
        for result in cursor.stored_results():
            reviews = result.fetchall()
    else:
        # Clients and admins see ALL reviews
        cursor.execute("""
            SELECT r.*, c.client_name, f.freelancer_name 
            FROM Reviews r
            JOIN Client c ON r.client_id = c.client_id
            JOIN Freelancers f ON r.freelancer_id = f.freelancer_id
            ORDER BY r.review_id DESC
        """)
        reviews = cursor.fetchall()
        
        # For clients, check if there are completed projects to review
        if session['role'] == 'client':
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM Projects p
                JOIN Proposals prop ON p.project_id = prop.project_id
                WHERE p.client_id = %s 
                  AND p.project_status = 'Completed'
                  AND prop.proposal_status = 'Accepted'
            """, (session['user_id'],))
            completed_projects = cursor.fetchone()['count'] > 0
    
    cursor.close()
    conn.close()
    
    return render_template('reviews.html', reviews=reviews, completed_projects=completed_projects)  

@app.route('/add_review/<int:project_id>', methods=['GET', 'POST'])
def add_review(project_id):
    if 'role' not in session or session['role'] != 'client':
        flash('Only clients can add reviews', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get project and freelancer info from accepted proposal
    cursor.execute("""
        SELECT p.*, f.freelancer_id, f.freelancer_name
        FROM Projects p
        JOIN Proposals prop ON p.project_id = prop.project_id AND prop.proposal_status = 'Accepted'
        JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
        WHERE p.project_id = %s AND p.client_id = %s
    """, (project_id, session['user_id']))
    
    project_data = cursor.fetchone()
    
    if not project_data:
        cursor.close()
        conn.close()
        flash('Invalid project or you are not authorized', 'error')
        return redirect(url_for('projects'))
    
    if project_data['project_status'] != 'Completed':
        cursor.close()
        conn.close()
        flash('You can only review completed projects', 'error')
        return redirect(url_for('projects'))
    
    freelancer_id = project_data['freelancer_id']
    
    # Check if review already exists
    cursor.execute("""
        SELECT * FROM Reviews 
        WHERE client_id = %s AND freelancer_id = %s
    """, (session['user_id'], freelancer_id))
    
    existing_review = cursor.fetchone()
    
    if existing_review:
        cursor.close()
        conn.close()
        flash('You have already reviewed this freelancer', 'error')
        return redirect(url_for('projects'))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comments = request.form.get('comments')
        review_date = date.today()
        
        try:
            # Get next review_id
            cursor.execute("SELECT COALESCE(MAX(review_id), 0) + 1 as next_id FROM Reviews")
            next_id = cursor.fetchone()['next_id']
            
            # Insert review
            cursor.execute("""
                INSERT INTO Reviews (review_id, client_id, freelancer_id, rating, comments, review_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (next_id, session['user_id'], freelancer_id, rating, comments, review_date))
            
            conn.commit()
            flash('Review added successfully!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('projects'))
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f'Error adding review: {str(e)}', 'error')
            return redirect(url_for('add_review', project_id=project_id))
    
    cursor.close()
    conn.close()
    
    # Create project and freelancer objects for template
    project = {
        'project_id': project_data['project_id'],
        'project_title': project_data['project_title']
    }
    freelancer = {
        'freelancer_id': project_data['freelancer_id'],
        'freelancer_name': project_data['freelancer_name']
    }
    
    return render_template('add_review.html', project=project, freelancer=freelancer)



# USER MANAGEMENT ROUTES

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can add clients', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        reg_date = request.form.get('registration_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Call stored procedure
            cursor.callproc('add_client', [name, email, reg_date])
            conn.commit()
            flash('Client added successfully!', 'success')
            return redirect(url_for('dashboard_admin'))
        except Error as e:
            conn.rollback()
            flash(f'Error adding client: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('add_client.html')

@app.route('/add_freelancer', methods=['GET', 'POST'])
def add_freelancer():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can add freelancers', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        reg_date = request.form.get('registration_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Call stored procedure
            cursor.callproc('add_freelancer', [name, email, reg_date])
            conn.commit()
            flash('Freelancer added successfully!', 'success')
            return redirect(url_for('dashboard_admin'))
        except Error as e:
            conn.rollback()
            flash(f'Error adding freelancer: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('add_freelancer.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'role' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'admin':
        flash('Admin profile editing not supported', 'error')
        return redirect(url_for('dashboard_admin'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get current user info
    if session['role'] == 'client':
        cursor.execute("SELECT * FROM Client WHERE client_id = %s", (session['user_id'],))
        user = cursor.fetchone()
        name_field = 'client_name'
        email_field = 'client_email'
        current_skills = []
    else:  # freelancer
        cursor.execute("SELECT * FROM Freelancers WHERE freelancer_id = %s", (session['user_id'],))
        user = cursor.fetchone()
        name_field = 'freelancer_name'
        email_field = 'freelancer_email'
        
        # Get current skills for freelancer
        cursor.execute("""
            SELECT s.skill_id, s.skill_name 
            FROM Skills s
            JOIN Freelancer_Skills fs ON s.skill_id = fs.skill_id
            WHERE fs.freelancer_id = %s
            ORDER BY s.skill_name
        """, (session['user_id'],))
        current_skills = cursor.fetchall()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        try:
            # Update basic profile info
            if session['role'] == 'client':
                cursor.callproc('update_client_profile', [session['user_id'], name, email])
            else:
                cursor.callproc('update_freelancer_profile', [session['user_id'], name, email])
            
            # Handle skills for freelancers
            if session['role'] == 'freelancer':
                # Get skills to remove
                skills_to_remove = request.form.getlist('remove_skill')
                for skill_id in skills_to_remove:
                    cursor.execute("""
                        DELETE FROM Freelancer_Skills 
                        WHERE freelancer_id = %s AND skill_id = %s
                    """, (session['user_id'], skill_id))
                
                # Get new skills to add
                new_skills = request.form.getlist('new_skill[]')
                for skill_name in new_skills:
                    skill_name = skill_name.strip()
                    if skill_name:  # Only process non-empty skills
                        # Check if skill already exists
                        cursor.execute("SELECT skill_id FROM Skills WHERE skill_name = %s", (skill_name,))
                        existing_skill = cursor.fetchone()
                        
                        if existing_skill:
                            skill_id = existing_skill['skill_id']
                        else:
                            # Get next skill_id
                            cursor.execute("SELECT COALESCE(MAX(skill_id), 0) + 1 as next_id FROM Skills")
                            skill_id = cursor.fetchone()['next_id']
                            
                            # Insert new skill
                            cursor.execute("""
                                INSERT INTO Skills (skill_id, skill_name)
                                VALUES (%s, %s)
                            """, (skill_id, skill_name))
                        
                        # Add mapping (if not already exists)
                        cursor.execute("""
                            INSERT IGNORE INTO Freelancer_Skills (freelancer_id, skill_id)
                            VALUES (%s, %s)
                        """, (session['user_id'], skill_id))
            
            conn.commit()
            flash('Profile updated successfully!', 'success')
            
            if session['role'] == 'client':
                return redirect(url_for('dashboard_client'))
            else:
                return redirect(url_for('dashboard_freelancer'))
        except Error as e:
            conn.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    cursor.close()
    conn.close()
    return render_template('edit_profile.html', 
                         user=user, 
                         name_field=name_field, 
                         email_field=email_field,
                         current_skills=current_skills)


# ADMIN VIEWS

@app.route('/admin/clients')
def admin_clients():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can view this page', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all clients with statistics
    cursor.execute("""
        SELECT 
            c.client_id,
            c.client_name,
            c.client_email,
            c.client_registration_date,
            COUNT(DISTINCT p.project_id) AS total_projects,
            COUNT(DISTINCT CASE WHEN p.project_status = 'In Progress' THEN p.project_id END) AS active_projects,
            COUNT(DISTINCT r.review_id) AS reviews_given,
            COALESCE(SUM(CASE WHEN pay.payment_status = 'Completed' THEN pay.amount ELSE 0 END), 0) AS total_spent
        FROM Client c
        LEFT JOIN Projects p ON c.client_id = p.client_id
        LEFT JOIN Reviews r ON c.client_id = r.client_id
        LEFT JOIN Payments pay ON p.project_id = pay.project_id
        GROUP BY c.client_id
        ORDER BY c.client_registration_date DESC
    """)
    
    clients = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin_clients.html', clients=clients)


@app.route('/admin/freelancers')
def admin_freelancers():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can view this page', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all freelancers with statistics
    cursor.execute("""
        SELECT 
            f.freelancer_id,
            f.freelancer_name,
            f.freelancer_email,
            f.freelancer_registration_date,
            GROUP_CONCAT(DISTINCT s.skill_name ORDER BY s.skill_name SEPARATOR ', ') AS skills,
            COUNT(DISTINCT CASE WHEN prop.proposal_status = 'Accepted' THEN p.project_id END) AS completed_projects,
            COUNT(DISTINCT r.review_id) AS reviews_received,
            COALESCE(AVG(r.rating), 0) AS avg_rating,
            COALESCE(SUM(CASE WHEN pay.payment_status = 'Completed' THEN pay.amount ELSE 0 END), 0) AS total_earned
        FROM Freelancers f
        LEFT JOIN Freelancer_Skills fs ON f.freelancer_id = fs.freelancer_id
        LEFT JOIN Skills s ON fs.skill_id = s.skill_id
        LEFT JOIN Proposals prop ON f.freelancer_id = prop.freelancer_id
        LEFT JOIN Projects p ON prop.project_id = p.project_id
        LEFT JOIN Reviews r ON f.freelancer_id = r.freelancer_id
        LEFT JOIN Payments pay ON p.project_id = pay.project_id AND prop.proposal_status = 'Accepted'
        GROUP BY f.freelancer_id
        ORDER BY f.freelancer_registration_date DESC
    """)
    
    freelancers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin_freelancers.html', freelancers=freelancers)


if __name__ == '__main__':
    app.run(debug=True)
