from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from functools import wraps
import os, random, string, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'abh-worldwide-secret-key-2025'

# ─── EMAIL CONFIG ─────────────────────────────────────────
ADMIN_EMAIL     = 'aliyuabdullahiabubakar02@gmail.com'
SMTP_SENDER     = 'aliyuabdullahiabubakar02@gmail.com'
SMTP_APP_PASS   = 'vfjfzzmvidkrsyvv'
SMTP_HOST       = 'smtp.gmail.com'
SMTP_PORT       = 587
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///abh_worldwide.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ─── MODELS ───────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='staff')
    phone = db.Column(db.String(20), default='')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), default='')
    products = db.relationship('Product', backref='cat', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    unit_type = db.Column(db.String(50), default='Pieces')
    quantity = db.Column(db.Float, default=0)
    buying_price = db.Column(db.Float, default=0)
    selling_price = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    amount_paid = db.Column(db.Float, default=0)
    supplier_name = db.Column(db.String(100), default='')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def amount_remaining(self): return max(0, self.total_cost - self.amount_paid)
    @property
    def payment_status(self):
        if self.total_cost <= 0: return 'Fully Paid'
        if self.amount_paid <= 0: return 'Not Paid'
        if self.amount_paid >= self.total_cost: return 'Fully Paid'
        return 'Partially Paid'
    @property
    def expected_revenue(self): return self.selling_price * self.quantity
    @property
    def expected_profit(self): return (self.selling_price - self.buying_price) * self.quantity
    @property
    def stock_status(self):
        if self.quantity >= 50: return 'high'
        if self.quantity >= 20: return 'medium'
        return 'low'
    def to_dict(self):
        return {
            'id': self.id, 'name': self.name,
            'category_id': self.category_id,
            'category_name': self.cat.name if self.cat else '',
            'unit_type': self.unit_type, 'quantity': self.quantity,
            'buying_price': self.buying_price, 'selling_price': self.selling_price,
            'total_cost': self.total_cost, 'amount_paid': self.amount_paid,
            'amount_remaining': self.amount_remaining,
            'payment_status': self.payment_status,
            'supplier_name': self.supplier_name,
            'expected_revenue': self.expected_revenue,
            'expected_profit': self.expected_profit,
            'stock_status': self.stock_status,
        }

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    other_names = db.Column(db.String(80), default='')
    shop_name = db.Column(db.String(150), default='')
    nickname = db.Column(db.String(80), default='')
    phone = db.Column(db.String(20), default='')
    address = db.Column(db.String(200), default='')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    @property
    def full_name(self): return f"{self.first_name} {self.last_name}"
    @property
    def total_debt(self): return sum(s.balance_due for s in self.sales if s.balance_due > 0)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_no = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subtotal = db.Column(db.Float, default=0)
    amount_paid = db.Column(db.Float, default=0)
    balance_due = db.Column(db.Float, default=0)
    payment_status = db.Column(db.String(20), default='Paid')
    payment_method = db.Column(db.String(20), default='Cash')  # Cash / Transfer / POS
    notes = db.Column(db.String(300), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')
    customer = db.relationship('Customer', backref='sales')
    staff = db.relationship('User', backref='sales')

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(150))
    quantity = db.Column(db.Float, default=1)
    unit_price = db.Column(db.Float, default=0)
    original_price = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    product = db.relationship('Product', backref='sale_items')

class DebtPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─── DECORATORS ───────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if 'user_id' not in session:
            if request.is_json: return jsonify({'error': 'Not authenticated'}), 401
            return redirect(url_for('login'))
        return f(*a, **kw)
    return dec

def admin_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if session.get('role') != 'admin':
            return jsonify({'error': 'Admin only'}), 403
        return f(*a, **kw)
    return dec

def gen_receipt():
    last = Sale.query.order_by(Sale.id.desc()).first()
    return f"RCP-{((last.id if last else 0) + 1):05d}"

# ─── PAGES ────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        d = request.get_json()
        user = User.query.filter_by(username=d.get('username','')).first()
        if not user or not user.check_password(d.get('password','')):
            return jsonify({'success': False, 'error': 'Invalid username or password'})
        if not user.active:
            return jsonify({'success': False, 'error': 'This account is deactivated'})
        tab = d.get('tab','admin')
        if tab == 'admin' and user.role != 'admin':
            return jsonify({'success': False, 'error': 'Use Staff Login for staff accounts'})
        if tab == 'staff' and user.role == 'admin':
            return jsonify({'success': False, 'error': 'Use Admin Login for the admin account'})
        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = user.full_name
        return jsonify({'success': True, 'role': user.role})
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── FORGOT PASSWORD ──────────────────────────────────────

def send_otp_email(temp_password):
    """Send temporary password to the hardcoded admin email via Gmail SMTP."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'ABH System — Your Temporary Password'
        msg['From']    = SMTP_SENDER
        msg['To']      = ADMIN_EMAIL

        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:2rem;background:#f1f5f9;border-radius:12px">
          <div style="background:#0f172a;border-radius:10px;padding:1.5rem;text-align:center;margin-bottom:1.5rem">
            <h2 style="color:#fff;margin:0;font-size:1rem">ABH WORLDWIDE MULTIPURPOSE COMPANY</h2>
            <p style="color:#94a3b8;margin:.3rem 0 0;font-size:.8rem">Inventory &amp; Sales Management System</p>
          </div>
          <div style="background:#fff;border-radius:10px;padding:1.5rem">
            <p style="color:#374151;margin-bottom:1rem">Your temporary password has been generated.</p>
            <div style="background:#f8fafc;border:2px dashed #e2e8f0;border-radius:8px;padding:1.2rem;text-align:center;margin-bottom:1.2rem">
              <div style="font-size:.75rem;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.4rem">Temporary Password</div>
              <div style="font-size:2rem;font-weight:800;letter-spacing:.15em;color:#1a56db;font-family:monospace">{temp_password}</div>
            </div>
            <p style="color:#374151;font-size:.85rem;margin-bottom:.5rem">
              <strong>What to do:</strong>
            </p>
            <ol style="color:#374151;font-size:.85rem;padding-left:1.2rem;margin:0">
              <li style="margin-bottom:.3rem">Go to the login page</li>
              <li style="margin-bottom:.3rem">Select <strong>Admin Login</strong></li>
              <li style="margin-bottom:.3rem">Enter your username and this temporary password</li>
              <li>Go to <strong>My Profile</strong> and set a new permanent password</li>
            </ol>
            <div style="margin-top:1.2rem;padding:.75rem;background:#fef9c3;border-radius:6px;font-size:.78rem;color:#854d0e">
              ⚠️ This password is active until you change it. Please update it immediately after logging in.
            </div>
          </div>
          <p style="text-align:center;color:#94a3b8;font-size:.72rem;margin-top:1rem">
            ABH Worldwide Multipurpose Company — Automated System Message
          </p>
        </div>
        """

        msg.attach(MIMEText(html_body, 'html'))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_SENDER, SMTP_APP_PASS)
            server.sendmail(SMTP_SENDER, ADMIN_EMAIL, msg.as_string())
        return True
    except Exception as e:
        print(f'Email send error: {e}')
        return False

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """Generate a temporary password, update admin DB record, send via email."""
    # Find the admin user
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        return jsonify({'success': False, 'error': 'No admin account found'})

    # Generate a strong readable temporary password: ABH-XXXX-XXXX
    chars = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choices(chars, k=4))
    part2 = ''.join(random.choices(chars, k=4))
    temp_password = f'ABH-{part1}-{part2}'

    # Update the admin password in the database (only the hash — no schema change)
    admin.set_password(temp_password)
    db.session.commit()

    # Send the email
    sent = send_otp_email(temp_password)
    if sent:
        return jsonify({'success': True, 'message': f'A temporary password has been sent to {ADMIN_EMAIL}'})
    else:
        # Email failed — still succeeded in resetting, but warn
        return jsonify({'success': False, 'error': 'Password was reset but email could not be sent. Check your internet connection and try again.'})

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

# ─── API: SESSION ─────────────────────────────────────────

@app.route('/api/me')
@login_required
def api_me():
    u = User.query.get(session['user_id'])
    return jsonify({'id':u.id,'name':u.full_name,'username':u.username,'role':u.role,'phone':u.phone or ''})

@app.route('/api/me/update', methods=['POST'])
@login_required
def api_me_update():
    d = request.get_json()
    u = User.query.get(session['user_id'])
    if d.get('full_name'): u.full_name = d['full_name']
    if d.get('username'):
        ex = User.query.filter_by(username=d['username']).first()
        if ex and ex.id != u.id: return jsonify({'success':False,'error':'Username taken'})
        u.username = d['username']
    if 'phone' in d: u.phone = d['phone']
    if d.get('new_password'):
        if not u.check_password(d.get('current_password','')):
            return jsonify({'success':False,'error':'Current password incorrect'})
        u.set_password(d['new_password'])
    db.session.commit()
    session['name'] = u.full_name
    return jsonify({'success': True})

# ─── API: CATEGORIES ──────────────────────────────────────

@app.route('/api/categories', methods=['GET','POST'])
@login_required
def api_categories():
    if request.method == 'POST':
        d = request.get_json()
        if Category.query.filter_by(name=d['name']).first():
            return jsonify({'success':False,'error':'Category already exists'})
        c = Category(name=d['name'], description=d.get('description',''))
        db.session.add(c); db.session.commit()
        return jsonify({'success':True,'id':c.id})
    cats = Category.query.order_by(Category.name).all()
    return jsonify([{'id':c.id,'name':c.name,'description':c.description,'product_count':len([p for p in c.products if p.active])} for c in cats])

@app.route('/api/categories/<int:cid>', methods=['PUT','DELETE'])
@login_required
def api_category(cid):
    c = Category.query.get_or_404(cid)
    if request.method == 'DELETE':
        active_prods = [p for p in c.products if p.active]
        if active_prods: return jsonify({'success':False,'error':'Cannot delete: category has products'})
        db.session.delete(c); db.session.commit()
        return jsonify({'success':True})
    d = request.get_json()
    c.name = d.get('name', c.name)
    c.description = d.get('description', c.description)
    db.session.commit()
    return jsonify({'success':True})

# ─── API: PRODUCTS ────────────────────────────────────────

@app.route('/api/products', methods=['GET','POST'])
@login_required
def api_products():
    if request.method == 'POST':
        d = request.get_json()
        p = Product(
            name=d['name'], category_id=int(d['category_id']),
            unit_type=d.get('unit_type','Pieces'),
            quantity=float(d.get('quantity',0)),
            buying_price=float(d.get('buying_price',0)),
            selling_price=float(d.get('selling_price',0)),
            total_cost=float(d.get('total_cost',0)),
            amount_paid=float(d.get('amount_paid',0)),
            supplier_name=d.get('supplier_name','')
        )
        db.session.add(p); db.session.commit()
        return jsonify({'success':True,'id':p.id})
    q = request.args.get('q','').lower()
    cat_id = request.args.get('category_id')
    query = Product.query.filter_by(active=True)
    if cat_id: query = query.filter_by(category_id=int(cat_id))
    if q: query = query.filter(Product.name.ilike(f'%{q}%'))
    return jsonify([p.to_dict() for p in query.order_by(Product.name).all()])

@app.route('/api/products/<int:pid>', methods=['GET','PUT','DELETE'])
@login_required
def api_product(pid):
    p = Product.query.get_or_404(pid)
    if request.method == 'DELETE':
        p.active = False; db.session.commit()
        return jsonify({'success':True})
    if request.method == 'GET':
        return jsonify(p.to_dict())
    d = request.get_json()
    for f in ['name','unit_type','supplier_name']:
        if f in d: setattr(p, f, d[f])
    for f in ['quantity','buying_price','selling_price','total_cost','amount_paid']:
        if f in d: setattr(p, f, float(d[f]))
    if 'category_id' in d: p.category_id = int(d['category_id'])
    db.session.commit()
    return jsonify({'success':True})

# ─── API: CUSTOMERS ───────────────────────────────────────

@app.route('/api/customers', methods=['GET','POST'])
@login_required
def api_customers():
    if request.method == 'POST':
        d = request.get_json()
        c = Customer(
            first_name=d['first_name'], last_name=d['last_name'],
            other_names=d.get('other_names',''), shop_name=d.get('shop_name',''),
            nickname=d.get('nickname',''), phone=d.get('phone',''), address=d.get('address','')
        )
        db.session.add(c); db.session.commit()
        return jsonify({'success':True,'id':c.id})
    q = request.args.get('q','').lower()
    query = Customer.query.filter_by(active=True)
    if q:
        query = query.filter(db.or_(
            Customer.first_name.ilike(f'%{q}%'), Customer.last_name.ilike(f'%{q}%'),
            Customer.shop_name.ilike(f'%{q}%'), Customer.nickname.ilike(f'%{q}%'),
            Customer.phone.ilike(f'%{q}%')
        ))
    return jsonify([{'id':c.id,'first_name':c.first_name,'last_name':c.last_name,
        'other_names':c.other_names,'shop_name':c.shop_name,'nickname':c.nickname,
        'phone':c.phone,'address':c.address,'full_name':c.full_name,'total_debt':c.total_debt
    } for c in query.order_by(Customer.first_name).all()])

@app.route('/api/customers/<int:cid>', methods=['PUT','DELETE'])
@login_required
def api_customer(cid):
    c = Customer.query.get_or_404(cid)
    if request.method == 'DELETE':
        c.active = False; db.session.commit(); return jsonify({'success':True})
    d = request.get_json()
    for f in ['first_name','last_name','other_names','shop_name','nickname','phone','address']:
        if f in d: setattr(c, f, d[f])
    db.session.commit()
    return jsonify({'success':True})

@app.route('/api/customers/<int:cid>/debts')
@login_required
def api_customer_debts(cid):
    sales = Sale.query.filter_by(customer_id=cid).filter(Sale.balance_due > 0).all()
    return jsonify([{'sale_id':s.id,'receipt_no':s.receipt_no,'subtotal':s.subtotal,
        'amount_paid':s.amount_paid,'balance_due':s.balance_due,
        'payment_method':s.payment_method or 'Cash',
        'date':s.created_at.strftime('%Y-%m-%d %H:%M')} for s in sales])

@app.route('/api/customers/<int:cid>/history')
@login_required
def api_customer_history(cid):
    sales = Sale.query.filter_by(customer_id=cid).order_by(Sale.created_at.desc()).all()
    return jsonify([{'sale_id':s.id,'receipt_no':s.receipt_no,'subtotal':s.subtotal,
        'amount_paid':s.amount_paid,'balance_due':s.balance_due,
        'payment_status':s.payment_status,'payment_method':s.payment_method or 'Cash',
        'item_count':len(s.items),
        'date':s.created_at.strftime('%Y-%m-%d %H:%M')} for s in sales])

@app.route('/api/debts/pay', methods=['POST'])
@login_required
def api_pay_debt():
    d = request.get_json()
    sale = Sale.query.get_or_404(d['sale_id'])
    amount = float(d['amount'])
    if amount > sale.balance_due + 0.01:
        return jsonify({'success':False,'error':'Payment exceeds balance'})
    sale.amount_paid += amount
    sale.balance_due = max(0, sale.balance_due - amount)
    if sale.balance_due <= 0:
        sale.balance_due = 0; sale.payment_status = 'Paid'
    dp = DebtPayment(sale_id=sale.id, customer_id=sale.customer_id,
                     amount=amount, recorded_by=session['user_id'], notes=d.get('notes',''))
    db.session.add(dp); db.session.commit()
    return jsonify({'success':True,'new_balance':sale.balance_due})

# ─── API: SALES ───────────────────────────────────────────

@app.route('/api/sales', methods=['GET','POST'])
@login_required
def api_sales():
    if request.method == 'POST':
        d = request.get_json()
        items = d.get('items', [])
        if not items: return jsonify({'success':False,'error':'Cart is empty'})
        subtotal = sum(float(i['total']) for i in items)
        amount_paid = float(d.get('amount_paid', subtotal))
        balance_due = max(0, subtotal - amount_paid)
        pstatus = 'Paid' if balance_due <= 0 else ('Partial' if amount_paid > 0 else 'Credit')
        sale = Sale(
            receipt_no=gen_receipt(), customer_id=d.get('customer_id') or None,
            staff_id=session['user_id'], subtotal=subtotal,
            amount_paid=amount_paid, balance_due=balance_due,
            payment_status=pstatus,
            payment_method=d.get('payment_method','Cash'),
            notes=d.get('notes','')
        )
        db.session.add(sale); db.session.flush()
        for item in items:
            prod = Product.query.get(int(item['product_id']))
            if not prod or prod.quantity < float(item['quantity']):
                db.session.rollback()
                return jsonify({'success':False,'error':f'Insufficient stock for {item["product_name"]}'})
            prod.quantity -= float(item['quantity'])
            si = SaleItem(sale_id=sale.id, product_id=prod.id,
                product_name=item['product_name'], quantity=float(item['quantity']),
                unit_price=float(item['unit_price']), original_price=float(item.get('original_price', item['unit_price'])),
                total=float(item['total']))
            db.session.add(si)
        db.session.commit()
        return jsonify({'success':True,'sale_id':sale.id,'receipt_no':sale.receipt_no})

    page = int(request.args.get('page',1))
    q = request.args.get('q','')
    date_from = request.args.get('date_from','')
    date_to = request.args.get('date_to','')
    staff_id = request.args.get('staff_id','')
    query = Sale.query
    if q: query = query.filter(Sale.receipt_no.ilike(f'%{q}%'))
    if date_from: query = query.filter(Sale.created_at >= date_from)
    if date_to: query = query.filter(Sale.created_at <= date_to + ' 23:59:59')
    if staff_id: query = query.filter_by(staff_id=int(staff_id))
    pag = query.order_by(Sale.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return jsonify({'sales':[{'id':s.id,'receipt_no':s.receipt_no,
        'customer':s.customer.full_name if s.customer else 'Walk-in',
        'staff':s.staff.full_name if s.staff else '',
        'subtotal':s.subtotal,'amount_paid':s.amount_paid,'balance_due':s.balance_due,
        'payment_status':s.payment_status,'payment_method':s.payment_method or 'Cash',
        'date':s.created_at.strftime('%Y-%m-%d %H:%M'),
        'item_count':len(s.items)} for s in pag.items],
        'total':pag.total,'pages':pag.pages})

@app.route('/api/sales/<int:sid>')
@login_required
def api_sale(sid):
    s = Sale.query.get_or_404(sid)
    return jsonify({'id':s.id,'receipt_no':s.receipt_no,
        'customer':{'id':s.customer.id,'name':s.customer.full_name,'phone':s.customer.phone} if s.customer else None,
        'staff':s.staff.full_name if s.staff else '',
        'subtotal':s.subtotal,'amount_paid':s.amount_paid,'balance_due':s.balance_due,
        'payment_status':s.payment_status,'payment_method':s.payment_method or 'Cash',
        'notes':s.notes,
        'date':s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'items':[{'product_name':i.product_name,'quantity':i.quantity,
            'unit_price':i.unit_price,'original_price':i.original_price,'total':i.total} for i in s.items]})

# ─── API: STAFF ───────────────────────────────────────────

@app.route('/api/staff', methods=['GET','POST'])
@login_required
def api_staff():
    if request.method == 'POST':
        d = request.get_json()
        if User.query.filter_by(username=d['username']).first():
            return jsonify({'success':False,'error':'Username already exists'})
        u = User(full_name=d['full_name'], username=d['username'], phone=d.get('phone',''), role='staff')
        u.set_password(d.get('password','1234'))
        db.session.add(u); db.session.commit()
        return jsonify({'success':True,'id':u.id})
    users = User.query.filter_by(role='staff').order_by(User.full_name).all()
    return jsonify([{'id':u.id,'full_name':u.full_name,'username':u.username,'phone':u.phone,'active':u.active} for u in users])

@app.route('/api/staff/<int:uid>', methods=['PUT','DELETE'])
@login_required
def api_staff_member(uid):
    u = User.query.get_or_404(uid)
    if request.method == 'DELETE':
        u.active = False; db.session.commit(); return jsonify({'success':True})
    d = request.get_json()
    if 'full_name' in d: u.full_name = d['full_name']
    if 'phone' in d: u.phone = d['phone']
    if 'active' in d: u.active = bool(d['active'])
    if d.get('password'): u.set_password(d['password'])
    db.session.commit()
    return jsonify({'success':True})

# ─── API: DASHBOARD ───────────────────────────────────────

@app.route('/api/dashboard')
@login_required
def api_dashboard():
    from sqlalchemy import func, extract
    today = date.today().isoformat()
    prods = Product.query.filter_by(active=True).all()
    all_sales = Sale.query.all()
    today_sales = Sale.query.filter(Sale.created_at >= today).all()
    monthly = db.session.query(
        extract('month', Sale.created_at).label('month'),
        extract('year', Sale.created_at).label('year'),
        func.sum(Sale.subtotal).label('total'),
        func.count(Sale.id).label('count')
    ).group_by('year','month').order_by('year','month').limit(6).all()
    top = db.session.query(
        SaleItem.product_name,
        func.sum(SaleItem.quantity).label('qty'),
        func.sum(SaleItem.total).label('rev')
    ).group_by(SaleItem.product_name).order_by(func.sum(SaleItem.quantity).desc()).limit(5).all()
    low = [p.to_dict() for p in prods if p.quantity < 20]
    return jsonify({
        'total_products': len(prods),
        'total_stock_units': sum(p.quantity for p in prods),
        'total_sales': len(all_sales),
        'total_revenue_realized': sum(s.subtotal for s in all_sales),
        'total_expected_revenue': sum(p.expected_revenue for p in prods),
        'total_expected_profit': sum(p.expected_profit for p in prods),
        'today_revenue': sum(s.amount_paid for s in today_sales),
        'today_sales_count': len(today_sales),
        'total_debts': sum(s.balance_due for s in all_sales),
        'low_stock_count': len(low),
        'staff_count': User.query.filter_by(role='staff', active=True).count(),
        'monthly_sales': [{'month':int(m.month),'year':int(m.year),'total':float(m.total),'count':int(m.count)} for m in monthly],
        'top_products': [{'name':t.product_name,'qty':float(t.qty),'revenue':float(t.rev)} for t in top],
        'low_stock': low[:6]
    })

# ─── API: REPORTS ─────────────────────────────────────────

@app.route('/api/reports')
@login_required
def api_reports():
    from sqlalchemy import func
    prods = Product.query.filter_by(active=True).all()
    all_sales = Sale.query.all()
    daily = db.session.query(
        func.date(Sale.created_at).label('day'),
        func.count(Sale.id).label('txns'),
        func.sum(Sale.subtotal).label('subtotal'),
        func.sum(Sale.amount_paid).label('paid'),
        func.sum(Sale.balance_due).label('balance')
    ).group_by('day').order_by(func.date(Sale.created_at).desc()).limit(30).all()
    by_staff = db.session.query(
        User.full_name, func.count(Sale.id).label('txns'), func.sum(Sale.subtotal).label('rev')
    ).join(Sale, Sale.staff_id == User.id).group_by(User.id).all()
    return jsonify({
        'summary': {
            'total_expected_revenue': sum(p.expected_revenue for p in prods),
            'total_expected_profit': sum(p.expected_profit for p in prods),
            'total_realized': sum(s.subtotal for s in all_sales),
            'total_debt': sum(s.balance_due for s in all_sales),
            'total_transactions': len(all_sales),
        },
        'daily': [{'day':str(d.day),'txns':d.txns,'subtotal':float(d.subtotal or 0),'paid':float(d.paid or 0),'balance':float(d.balance or 0)} for d in daily],
        'by_staff': [{'name':s.full_name,'txns':s.txns,'revenue':float(s.rev or 0)} for s in by_staff],
        'products': [p.to_dict() for p in prods]
    })

# ─── SEED ─────────────────────────────────────────────────

def seed():
    """Create the Super Admin account on first run only. No sample data."""
    if User.query.first(): return
    admin = User(full_name='Super Admin', username='admin', role='admin', phone='')
    admin.set_password('admin1234')
    db.session.add(admin)
    db.session.commit()
    print("✅ System ready. Super Admin account created.")
    print("   Username : admin")
    print("   Password : admin1234")
    print("   Please log in and change your password via My Profile.")

def migrate_db():
    """Add any missing columns to existing databases (safe to run on old DBs)."""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'abh_worldwide.db')
    if not os.path.exists(db_path):
        # Try current directory
        db_path = os.path.join(os.path.dirname(__file__), 'abh_worldwide.db')
    if not os.path.exists(db_path):
        return  # Fresh DB, db.create_all() will handle it
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # Check if payment_method column exists
        cur.execute("PRAGMA table_info(sale)")
        cols = [row[1] for row in cur.fetchall()]
        if 'payment_method' not in cols:
            cur.execute("ALTER TABLE sale ADD COLUMN payment_method VARCHAR(20) DEFAULT 'Cash'")
            conn.commit()
            print("✅ Migrated: added payment_method column to sale table")
        conn.close()
    except Exception as e:
        print(f"Migration note: {e}")

def get_local_ip():
    """Get this machine's LAN IP address."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

if __name__ == '__main__':
    with app.app_context():
        migrate_db()
        db.create_all()
        seed()
    import webbrowser, threading
    local_ip = get_local_ip()
    port = 5000
    local_url  = f'http://localhost:{port}'
    network_url = f'http://{local_ip}:{port}'
    # Open browser on this machine after 1.5s
    threading.Timer(1.5, lambda: webbrowser.open(local_url)).start()
    # Write a network shortcut file other devices can use
    try:
        with open('CONNECT_FROM_OTHER_DEVICE.html', 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta http-equiv="refresh" content="2;url={network_url}">
<title>Connecting to ABH System...</title>
<style>
  body{{font-family:Arial,sans-serif;background:#0f172a;color:#fff;display:flex;
       align-items:center;justify-content:center;min-height:100vh;margin:0;text-align:center}}
  .box{{background:#1e293b;border-radius:16px;padding:2.5rem 3rem;max-width:400px}}
  .icon{{font-size:3rem;margin-bottom:1rem}}
  h1{{font-size:1.2rem;margin-bottom:.5rem}}
  p{{color:#94a3b8;font-size:.85rem;margin-bottom:1.5rem}}
  .url{{background:#0f172a;border-radius:8px;padding:.75rem 1rem;font-family:monospace;
        font-size:1rem;color:#38bdf8;word-break:break-all}}
  a{{display:inline-block;margin-top:1.5rem;background:#1a56db;color:#fff;padding:.7rem 2rem;
     border-radius:8px;text-decoration:none;font-weight:700}}
</style></head>
<body><div class="box">
  <div class="icon">🌐</div>
  <h1>ABH WORLDWIDE<br>MULTIPURPOSE COMPANY</h1>
  <p>Connecting to the server on this network...<br>Redirecting automatically in 2 seconds.</p>
  <div class="url">{network_url}</div>
  <a href="{network_url}">Open Now →</a>
</div></body></html>""")
    except Exception:
        pass
    border = "=" * 58
    print(f"\n{border}")
    print("  ABH WORLDWIDE MULTIPURPOSE COMPANY")
    print("  Inventory & Sales Management System")
    print(border)
    print(f"  THIS COMPUTER  →  {local_url}")
    print(f"  OTHER DEVICES  →  {network_url}")
    print(border)
    print("  HOW TO CONNECT OTHER DEVICES:")
    print("  1. Make sure they are on the SAME WiFi as this computer")
    print(f"  2. Open any browser and go to:  {network_url}")
    print("  OR: Copy 'CONNECT_FROM_OTHER_DEVICE.html' to the other")
    print("      device and double-click it — it will auto-connect.")
    print(border)
    print("  Press Ctrl+C to stop the server.")
    print(f"{border}\n")
    app.run(debug=False, port=port, host='0.0.0.0')
