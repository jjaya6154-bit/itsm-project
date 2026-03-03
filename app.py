from flask import send_file
from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Secret key
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///database.db"   # ✅ Removed instance/
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Create tables automatically
with app.app_context():
    db.create_all()

# ✅ Login Manager Setup (ONLY THIS ONCE)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ---------------- MODELS ----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    status = db.Column(db.String(100))
    created_at = db.Column(db.String(100))

# ---------------- LOGIN ----------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/dashboard')
        return "Invalid Credentials"
    
    return render_template_string("""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>IT Infra Login</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
      <div class="container">
        <div class="row justify-content-center mt-5">
          <div class="col-md-4 p-4 shadow bg-white rounded">
            <h3 class="text-center mb-4">IT Infra Admin Login</h3>
            <form method="POST">
              <div class="mb-3">
                <label>Username</label>
                <input type="text" class="form-control" name="username" required>
              </div>
              <div class="mb-3">
                <label>Password</label>
                <input type="password" class="form-control" name="password" required>
              </div>
              <div class="d-grid">
                <button class="btn btn-primary">Login</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </body>
    </html>
    """)

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
@login_required
def dashboard():
    total = Asset.query.count()
    available = Asset.query.filter_by(status='Available').count()
    inuse = Asset.query.filter_by(status='In Use').count()
    maintenance = Asset.query.filter_by(status='Maintenance').count()

    servers = Asset.query.filter_by(category='Server').count()
    laptops = Asset.query.filter_by(category='Laptop').count()
    software = Asset.query.filter_by(category='Software').count()
    apps = Asset.query.filter_by(category='App').count()
    routers = Asset.query.filter_by(category='Router').count()

    return render_template_string("""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>IT Infra Dashboard</title>

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

  <style>
    body {
        background: linear-gradient(to right, #1e3c72, #2a5298);
        min-height: 100vh;
        overflow-x: hidden;
    }

    .sidebar {
        background-color: #0f1c3f;
        min-height: 100vh;
    }

    .sidebar a {
        color: white;
        text-decoration: none;
        display: block;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 5px;
    }

    .sidebar a:hover {
        background-color: #1e3c72;
    }

    .card {
        border-radius: 15px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        transition: 0.3s;
    }

    .card:hover {
        transform: translateY(-5px);
    }

    .main-container {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
    }

    @media (max-width: 768px) {
        .sidebar {
            min-height: auto;
        }
    }
  </style>
</head>

<body>

<div class="container-fluid">
  <div class="row">

    <!-- Sidebar -->
    <nav class="col-md-2 col-lg-2 d-md-block sidebar collapse show p-3">
      <h5 class="text-white text-center mb-4">IT ADMIN</h5>
      <a href="/dashboard">Dashboard</a>
      <a href="/catalog">Catalog</a>
      <a href="/add">Add Asset</a>
      <a href="/backup">Backup DB</a>
      <a href="/logout">Logout</a>
    </nav>

    <!-- Main -->
    <main class="col-md-10 col-lg-10 ms-sm-auto px-md-4 py-4">
      <div class="main-container">

        <h2 class="mb-4 text-primary fw-bold">IT Infrastructure Dashboard</h2>

        <!-- Stats -->
        <div class="row g-4">

          <div class="col-12 col-sm-6 col-lg-3">
            <div class="card text-center p-3">
              <h6>Total Assets</h6>
              <h3>{{total}}</h3>
            </div>
          </div>

          <div class="col-12 col-sm-6 col-lg-3">
            <div class="card text-center p-3">
              <h6>Available</h6>
              <h3>{{available}}</h3>
            </div>
          </div>

          <div class="col-12 col-sm-6 col-lg-3">
            <div class="card text-center p-3">
              <h6>In Use</h6>
              <h3>{{inuse}}</h3>
            </div>
          </div>

          <div class="col-12 col-sm-6 col-lg-3">
            <div class="card text-center p-3">
              <h6>Maintenance</h6>
              <h3>{{maintenance}}</h3>
            </div>
          </div>

        </div>

        <hr class="my-4">

        <!-- Capacity -->
        <h4 class="text-primary fw-bold mb-3">Capacity Overview</h4>

        <div class="row g-3">

          <div class="col-6 col-md-4 col-lg-2">
            <div class="card text-center p-2">
              Servers<br><strong>{{servers}}</strong>
            </div>
          </div>

          <div class="col-6 col-md-4 col-lg-2">
            <div class="card text-center p-2">
              Laptops<br><strong>{{laptops}}</strong>
            </div>
          </div>

          <div class="col-6 col-md-4 col-lg-2">
            <div class="card text-center p-2">
              Software<br><strong>{{software}}</strong>
            </div>
          </div>

          <div class="col-6 col-md-4 col-lg-2">
            <div class="card text-center p-2">
              Apps<br><strong>{{apps}}</strong>
            </div>
          </div>

          <div class="col-6 col-md-4 col-lg-2">
            <div class="card text-center p-2">
              Routers<br><strong>{{routers}}</strong>
            </div>
          </div>

        </div>

      </div>
    </main>

  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
""", total=total, available=available, inuse=inuse,
   maintenance=maintenance, servers=servers, laptops=laptops,
   software=software, apps=apps, routers=routers)

# ---------------- ADD ASSET ----------------
@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.method == 'POST':
        asset = Asset(
            name=request.form['name'],
            category=request.form['category'],
            status=request.form['status'],
            created_at=str(datetime.datetime.now())
        )
        db.session.add(asset)
        db.session.commit()
        return redirect('/catalog')

    return render_template_string("""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Add Asset</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
      <div class="container mt-5">
        <div class="card p-4 shadow">
          <h3>Add Asset</h3>
          <form method='POST'>
            <div class="mb-3">
              <label>Name</label>
              <input name='name' class="form-control" required>
            </div>
            <div class="mb-3">
              <label>Category</label>
              <select name='category' class="form-select" required>
                <option>Server</option>
                <option>Laptop</option>
                <option>Software</option>
                <option>App</option>
                <option>Router</option>
              </select>
            </div>
            <div class="mb-3">
              <label>Status</label>
              <select name='status' class="form-select" required>
                <option>Available</option>
                <option>In Use</option>
                <option>Maintenance</option>
              </select>
            </div>
            <button class="btn btn-primary">Add</button>
            <a href="/dashboard" class="btn btn-secondary">Cancel</a>
          </form>
        </div>
      </div>
    </body>
    </html>
    """)

# ---------------- CATALOG ----------------
@app.route('/catalog')
@login_required
def catalog():
    assets = Asset.query.all()
    return render_template_string("""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Catalog</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
      <div class="container mt-5">
        <h3>Asset Catalog</h3>
        <a href='/dashboard' class="btn btn-secondary mb-3">Back</a>
        <table class="table table-bordered table-striped">
          <thead class="table-dark">
            <tr>
              <th>Name</th><th>Category</th><th>Status</th><th>Date</th><th>Action</th>
            </tr>
          </thead>
          <tbody>
            {% for a in assets %}
            <tr>
              <td>{{a.name}}</td>
              <td>{{a.category}}</td>
              <td>{{a.status}}</td>
              <td>{{a.created_at}}</td>
              <td><a href='/delete/{{a.id}}' class="btn btn-danger btn-sm">Delete</a></td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </body>
    </html>
    """, assets=assets)

# ---------------- BACKUP ----------------
@app.route('/backup')
@login_required
def backup():
    db_path = os.path.join(app.instance_path, "itsm.db")
    backup_path = os.path.join(app.instance_path, "backup_itsm.db")

    if os.path.exists(db_path):
        with open(db_path, 'rb') as f:
            with open(backup_path, 'wb') as b:
                b.write(f.read())

        return send_file(
            backup_path,
            as_attachment=True
        )

    return "<h3 class='text-danger text-center mt-5'>Database not found</h3>"

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    asset = Asset.query.get(id)
    db.session.delete(asset)
    db.session.commit()
    return redirect('/catalog')

# ---------------- LOGOUT ----------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# ---------------- DATABASE INIT ----------------
with app.app_context():
    db.create_all()

    # Create default admin
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123')
        )
        db.session.add(admin)

    # Add sample assets if table is empty
    if not Asset.query.first():
        sample_assets = [
            Asset(name="Main Web Server", category="Server", status="Available", created_at=str(datetime.datetime.now())),
            Asset(name="HR Laptop 01", category="Laptop", status="In Use", created_at=str(datetime.datetime.now())),
            Asset(name="Finance Software", category="Software", status="Available", created_at=str(datetime.datetime.now())),
            Asset(name="CRM Application", category="App", status="Maintenance", created_at=str(datetime.datetime.now())),
            Asset(name="Core Router", category="Router", status="Available", created_at=str(datetime.datetime.now()))
        ]

        db.session.add_all(sample_assets)

    db.session.commit()

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)