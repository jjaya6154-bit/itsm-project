from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'infra_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itsm.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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
      <title>IT Infra Dashboard</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
      <div class="container-fluid">
        <div class="row">
          <div class="col-2 bg-dark text-white vh-100 p-3">
            <h4>IT Admin</h4>
            <a href="/dashboard" class="text-white d-block my-2">Dashboard</a>
            <a href="/catalog" class="text-white d-block my-2">Catalog</a>
            <a href="/add" class="text-white d-block my-2">Add Asset</a>
            <a href="/backup" class="text-white d-block my-2">Backup DB</a>
            <a href="/logout" class="text-white d-block my-2">Logout</a>
          </div>
          <div class="col-10 p-4">
            <h2>Dashboard</h2>
            <div class="row mt-4 g-3">
              <div class="col-md-3">
                <div class="card text-center text-white bg-primary">
                  <div class="card-body">
                    <h5>Total Assets</h5>
                    <h3>{{total}}</h3>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card text-center text-white bg-success">
                  <div class="card-body">
                    <h5>Available</h5>
                    <h3>{{available}}</h3>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card text-center text-dark bg-warning">
                  <div class="card-body">
                    <h5>In Use</h5>
                    <h3>{{inuse}}</h3>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card text-center text-white bg-danger">
                  <div class="card-body">
                    <h5>Maintenance</h5>
                    <h3>{{maintenance}}</h3>
                  </div>
                </div>
              </div>
            </div>

            <hr>
            <h4>Capacity Management</h4>
            <div class="row g-3">
              <div class="col-md-2"><div class="card p-2 text-center">Servers<br><strong>{{servers}}</strong></div></div>
              <div class="col-md-2"><div class="card p-2 text-center">Laptops<br><strong>{{laptops}}</strong></div></div>
              <div class="col-md-2"><div class="card p-2 text-center">Software<br><strong>{{software}}</strong></div></div>
              <div class="col-md-2"><div class="card p-2 text-center">Apps<br><strong>{{apps}}</strong></div></div>
              <div class="col-md-2"><div class="card p-2 text-center">Routers<br><strong>{{routers}}</strong></div></div>
            </div>
          </div>
        </div>
      </div>
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
    db_path = "itsm.db"
    backup_path = "backup_itsm.db"
    if os.path.exists(db_path):
        with open(db_path, 'rb') as f:
            with open(backup_path, 'wb') as b:
                b.write(f.read())
        return "<h3 class='text-success text-center mt-5'>Backup Created Successfully!</h3>"
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

# ---------------- MAIN ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('admin123'))
            db.session.add(admin)
            db.session.commit()
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)