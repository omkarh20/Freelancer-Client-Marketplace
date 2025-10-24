from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Omkar123',  # Change to your MySQL password
    'database': 'freelancer_client_marketplace'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - select role and enter ID"""
    if request.method == 'POST':
        role = request.form.get('role')
        user_id = request.form.get('user_id')
        
        # Store in session
        session['role'] = role
        session['user_id'] = int(user_id)
        
        # Redirect based on role
        if role == 'client':
            return redirect(url_for('dashboard_client'))
        elif role == 'freelancer':
            return redirect(url_for('dashboard_freelancer'))
        elif role == 'admin':
            return redirect(url_for('dashboard_admin'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard/client')
def dashboard_client():
    """Client dashboard"""
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
    
    # Get client info
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
    """Freelancer dashboard"""
    if 'role' not in session or session['role'] != 'freelancer':
        return redirect(url_for('login'))
    
    freelancer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Call stored procedure to get freelancer projects
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
    """Admin dashboard - view all data"""
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get statistics
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

@app.route('/projects')
def projects():
    """View all projects (filtered by role)"""
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'client':
        cursor.execute("""
            SELECT * FROM Projects WHERE client_id = %s
        """, (session['user_id'],))
    elif session['role'] == 'freelancer':
        cursor.execute("""
            SELECT p.* FROM Projects p
            JOIN Proposals prop ON p.project_id = prop.project_id
            WHERE prop.freelancer_id = %s
        """, (session['user_id'],))
    else:  # admin
        cursor.execute("SELECT * FROM view_all_projects")
    
    projects = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('projects.html', projects=projects)

@app.route('/payments')
def payments():
    """View payments"""
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
            SELECT pay.*, p.project_title 
            FROM Payments pay
            JOIN Projects p ON pay.project_id = p.project_id
        """)
        payments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('payments.html', payments=payments)

@app.route('/proposals')
def proposals():
    """View proposals"""
    if 'role' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'freelancer':
        cursor.execute("""
            SELECT prop.*, p.project_title 
            FROM Proposals prop
            JOIN Projects p ON prop.project_id = p.project_id
            WHERE prop.freelancer_id = %s
        """, (session['user_id'],))
    else:
        cursor.execute("""
            SELECT prop.*, p.project_title, f.freelancer_name 
            FROM Proposals prop
            JOIN Projects p ON prop.project_id = p.project_id
            JOIN Freelancers f ON prop.freelancer_id = f.freelancer_id
        """)
    
    proposals = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('proposals.html', proposals=proposals)

@app.route('/reviews')
def reviews():
    """View reviews"""
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
        """)
        reviews = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reviews.html', reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True)
