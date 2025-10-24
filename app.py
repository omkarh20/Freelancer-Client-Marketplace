from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Omkar123',  
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

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        user_id = request.form.get('user_id')
        
        session['role'] = role
        session['user_id'] = int(user_id)
        
        if role == 'client':
            return redirect(url_for('dashboard_client'))
        elif role == 'freelancer':
            return redirect(url_for('dashboard_freelancer'))
        elif role == 'admin':
            return redirect(url_for('dashboard_admin'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

# ==================== DASHBOARD ROUTES ====================

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
    
    cursor.execute("SELECT * FROM view_all_projects LIMIT 10")
    all_projects = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard_admin.html', 
                         total_clients=total_clients,
                         total_freelancers=total_freelancers,
                         total_projects=total_projects,
                         projects=all_projects)

# ==================== PROJECT ROUTES ====================

@app.route('/projects')
def projects():
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'client':
        cursor.execute("""
            SELECT * FROM Projects WHERE client_id = %s ORDER BY project_id DESC
        """, (session['user_id'],))
    elif session['role'] == 'freelancer':
        cursor.execute("""
            SELECT p.* FROM Projects p
            JOIN Proposals prop ON p.project_id = prop.project_id
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
        status = request.form.get('status')
        
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

# ==================== PROPOSAL ROUTES ====================

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

# ==================== PAYMENT ROUTES ====================

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
    else:
        cursor.execute("""
            SELECT pay.*, p.project_title, c.client_name 
            FROM Payments pay
            JOIN Projects p ON pay.project_id = p.project_id
            JOIN Client c ON p.client_id = c.client_id
            ORDER BY pay.payment_id DESC
        """)
        payments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('payments.html', payments=payments)

# ==================== REVIEW ROUTES ====================

@app.route('/reviews')
def reviews():
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'freelancer':
        cursor.callproc('get_freelancer_reviews', [session['user_id']])
        reviews = []
        for result in cursor.stored_results():
            reviews = result.fetchall()
    else:
        cursor.execute("""
            SELECT r.*, c.client_name, f.freelancer_name 
            FROM Reviews r
            JOIN Client c ON r.client_id = c.client_id
            JOIN Freelancers f ON r.freelancer_id = f.freelancer_id
            ORDER BY r.review_id DESC
        """)
        reviews = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reviews.html', reviews=reviews)

# ==================== USER MANAGEMENT ROUTES ====================

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
    else:  # freelancer
        cursor.execute("SELECT * FROM Freelancers WHERE freelancer_id = %s", (session['user_id'],))
        user = cursor.fetchone()
        name_field = 'freelancer_name'
        email_field = 'freelancer_email'
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        try:
            if session['role'] == 'client':
                cursor.callproc('update_client_profile', [session['user_id'], name, email])
            else:
                cursor.callproc('update_freelancer_profile', [session['user_id'], name, email])
            
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
    return render_template('edit_profile.html', user=user, name_field=name_field, email_field=email_field)

if __name__ == '__main__':
    app.run(debug=True)
