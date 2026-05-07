from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, emit
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import os
import secrets
import socket
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.exc import IntegrityError

# Initialize Flask app
app = Flask(__name__)

AWST_TZ = ZoneInfo('Australia/Perth')

# Configuration
app.config['SECRET_KEY'] = os.urandom(24).hex() #protects user sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shindig.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='threading')

def get_share_url(path):
    """Generate a shareable URL using the network hostname instead of localhost"""
    # Get the hostname that can be accessed over the network
    try:
        hostname = socket.gethostname()
        # Try to get the actual IP address
        ip_address = socket.gethostbyname(hostname)
        # If it's still localhost, try to find the machine's actual network IP
        if ip_address.startswith('127.'):
            # Fallback: try to get the network-accessible hostname
            try:
                # This gets the local network IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
                s.close()
            except:
                # If all else fails, use localhost
                ip_address = "127.0.0.1"
    except:
        ip_address = "127.0.0.1"
    
    scheme = request.scheme or 'http'
    port = request.environ.get('SERVER_PORT', '5001')
    return f"{scheme}://{ip_address}:{port}{path}"

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=True)
    is_private = db.Column(db.Boolean, default=True, nullable=False)
    selected_tabs = db.Column(db.Text, default='[]', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', backref=db.backref('events', lazy=True))

    def __repr__(self):
        return f'<Event {self.title}>'


class EventParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('participant_links', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User')


class EventVoteOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('vote_options', lazy=True, cascade='all, delete-orphan'))


class EventVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey('event_vote_option.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    option = db.relationship('EventVoteOption', backref=db.backref('votes', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User')


class EventExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    paid_by = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('expenses', lazy=True, cascade='all, delete-orphan'))


class EventChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('checklist_items', lazy=True, cascade='all, delete-orphan'))


class EventDiscussionMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('discussion_messages', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User')


class EventInviteToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True, nullable=False)

    event = db.relationship('Event', backref=db.backref('invite_tokens', lazy=True, cascade='all, delete-orphan'))


class EventJoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('join_requests', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User')

# Create tables
with app.app_context():
    db.create_all()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def format_awst(dt):
    if dt is None:
        return ''
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(AWST_TZ).strftime('%d %b %Y %I:%M %p AWST')


@app.template_filter('awst_datetime')
def awst_datetime_filter(value):
    return format_awst(value)


def get_or_create_event_invite(event):
    invite = EventInviteToken.query.filter_by(event_id=event.id, active=True).order_by(EventInviteToken.created_at.desc()).first()
    if invite is not None:
        return invite

    while True:
        token = secrets.token_urlsafe(16)
        invite = EventInviteToken(event_id=event.id, token=token)
        db.session.add(invite)
        try:
            db.session.commit()
            return invite
        except IntegrityError:
            db.session.rollback()


def render_event_dashboard(event, active_tab='overview', allow_invite_access=False, invite_token=None):
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    is_owner = event.user_id == session['user_id']

    if event.is_private and not (is_owner or participant or allow_invite_access):
        abort(403)

    participants = EventParticipant.query.filter_by(event_id=event.id).order_by(EventParticipant.created_at.asc()).all()
    vote_options = EventVoteOption.query.filter_by(event_id=event.id).order_by(EventVoteOption.created_at.asc()).all()
    expenses = EventExpense.query.filter_by(event_id=event.id).order_by(EventExpense.created_at.asc()).all()
    checklist_items = EventChecklistItem.query.filter_by(event_id=event.id).order_by(EventChecklistItem.created_at.asc()).all()
    discussion_messages = EventDiscussionMessage.query.filter_by(event_id=event.id).order_by(EventDiscussionMessage.created_at.desc()).all()
    expense_total = sum(expense.amount for expense in expenses)

    user_vote = None
    if vote_options:
        user_vote = EventVote.query.join(EventVoteOption).filter(
            EventVote.user_id == session['user_id'],
            EventVoteOption.event_id == event.id
        ).first()

    pending_requests = []
    if is_owner:
        pending_requests = EventJoinRequest.query.filter_by(event_id=event.id, status='pending').order_by(EventJoinRequest.created_at.asc()).all()

    invite_link = None
    if is_owner:
        invite = get_or_create_event_invite(event)
        invite_token = invite.token
        invite_link = get_share_url(f'/invite/{invite_token}')

    return render_template(
        'EVENT_DASHBOARD_FINAL.html',
        username=session.get('username'),
        event=event,
        participants=participants,
        vote_options=vote_options,
        expenses=expenses,
        expense_total=expense_total,
        checklist_items=checklist_items,
        discussion_messages=discussion_messages,
        current_participant=participant,
        current_vote=user_vote,
        active_tab=active_tab,
        share_url=invite_link,
        invite_token=invite_token,
        show_join_modal=allow_invite_access and event.is_private and not is_owner and participant is None,
        pending_requests=pending_requests,
        event_is_owner=is_owner,
    )

# ============ ROUTES ============

@app.route('/')
def index():
    """Root page - redirect to dashboard if logged in, else show root page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('ROOT-PAGE.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login page"""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user signup"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validation
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already taken'}), 409

    # Create new user
    try:
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()

        # Log the user in
        session['user_id'] = new_user.id
        session['username'] = new_user.username

        return jsonify({'success': True, 'message': 'Account created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    """Protected dashboard page"""
    user_id = session['user_id']
    owned_events = Event.query.filter_by(user_id=user_id).all()
    joined_events = (
        Event.query
        .join(EventParticipant, Event.id == EventParticipant.event_id)
        .filter(EventParticipant.user_id == user_id, Event.user_id != user_id)
        .all()
    )

    events_by_id = {}
    for event in owned_events + joined_events:
        event.is_owner = event.user_id == user_id
        events_by_id[event.id] = event

    events = sorted(events_by_id.values(), key=lambda event: event.start_datetime)

    now = datetime.utcnow()
    upcoming_count = sum(1 for event in events if event.start_datetime >= now)
    past_count = sum(1 for event in events if event.end_datetime < now)

    visible_event_ids = list(events_by_id.keys())
    event_rsvp_counts = {}
    if visible_event_ids:
        rsvp_rows = (
            db.session.query(EventParticipant.event_id, db.func.count(EventParticipant.id))
            .filter(EventParticipant.event_id.in_(visible_event_ids), EventParticipant.user_id != user_id)
            .group_by(EventParticipant.event_id)
            .all()
        )
        event_rsvp_counts = {event_id: count for event_id, count in rsvp_rows}
    total_rsvps = sum(event_rsvp_counts.values())

    stats = {
        'upcoming': upcoming_count,
        'past': past_count,
        'rsvp': total_rsvps,
        'total': len(events),
    }

    return render_template(
        'dashboard.html',
        username=session.get('username'),
        events=events,
        stats=stats,
        event_rsvp_counts=event_rsvp_counts,
    )


@app.route('/event-dashboard/<int:event_id>')
@login_required
def event_dashboard(event_id):
    """Event-specific dashboard page"""
    event = Event.query.get_or_404(event_id)
    active_tab = request.args.get('tab', 'overview')
    return render_event_dashboard(event, active_tab=active_tab)


@app.route('/invite/<string:token>')
@login_required
def invite_event(token):
    invite = EventInviteToken.query.filter_by(token=token, active=True).first_or_404()
    active_tab = request.args.get('tab', 'overview')
    return render_event_dashboard(invite.event, active_tab=active_tab, allow_invite_access=True, invite_token=token)


@app.route('/events/new')
@login_required
def new_event():
    """Event creation page"""
    return render_template('event_creation.html')


@app.route('/events', methods=['POST'])
@login_required
def create_event():
    """Create a new event from the event creation form"""
    data = request.get_json(silent=True) or request.form

    title = (data.get('title') or '').strip()
    location = (data.get('location') or '').strip()
    description = (data.get('description') or '').strip()
    start_date = (data.get('start_date') or '').strip()
    start_time = (data.get('start_time') or '').strip()
    end_date = (data.get('end_date') or '').strip()
    end_time = (data.get('end_time') or '').strip()
    is_private = str(data.get('is_private', 'true')).lower() in {'true', '1', 'yes', 'on'}

    selected_tabs = data.get('selected_tabs', [])
    if isinstance(selected_tabs, str):
        try:
            selected_tabs = json.loads(selected_tabs)
        except json.JSONDecodeError:
            selected_tabs = [selected_tabs] if selected_tabs else []

    if not title:
        return jsonify({'success': False, 'message': 'Event name is required'}), 400

    if not start_date or not start_time:
        return jsonify({'success': False, 'message': 'Start date and time are required'}), 400

    try:
        start_datetime = datetime.fromisoformat(f'{start_date}T{start_time}')
        if end_date:
            if end_time:
                end_datetime = datetime.fromisoformat(f'{end_date}T{end_time}')
            else: 
                end_datetime = datetime.fromisoformat(f'end_date')
            if end_datetime < start_datetime:
                return jsonify({'success': False, 'message': 'End date and time must be after the start date and time'}), 400
        else:     
            end_datetime = None
            
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date or time format'}), 400

    event = Event(
        user_id=session['user_id'],
        title=title,
        location=location,
        description=description,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        is_private=is_private,
        selected_tabs=json.dumps(selected_tabs),
    )

    db.session.add(event)
    db.session.commit()

    owner_participant = EventParticipant(event_id=event.id, user_id=session['user_id'])
    db.session.add(owner_participant)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Event created successfully',
        'event_id': event.id,
        'redirect_url': url_for('dashboard')
    }), 201


@app.route('/event-dashboard/<int:event_id>/join', methods=['POST'])
@login_required
def join_event(event_id):
    event = Event.query.get_or_404(event_id)
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if event.is_private and event.user_id != session['user_id'] and participant is None:
        abort(403)
    if participant is None:
        new_participant = EventParticipant(event_id=event.id, user_id=session['user_id'])
        db.session.add(new_participant)
        db.session.commit()
    return redirect(url_for('event_dashboard', event_id=event.id, tab='participants'))


@app.route('/invite/<string:token>/request-join', methods=['POST'])
@login_required
def request_join_event(token):
    invite = EventInviteToken.query.filter_by(token=token, active=True).first_or_404()
    event = invite.event
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if participant or event.user_id == session['user_id']:
        return jsonify({'success': False, 'message': 'You are already a participant.'}), 400

    existing_request = EventJoinRequest.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if existing_request and existing_request.status == 'pending':
        return jsonify({'success': False, 'message': 'Join request already pending.'}), 400

    if existing_request is None:
        existing_request = EventJoinRequest(event_id=event.id, user_id=session['user_id'], status='pending')
        db.session.add(existing_request)
    else:
        existing_request.status = 'pending'

    db.session.commit()
    return jsonify({'success': True, 'message': 'Request sent to host.'}), 200


@app.route('/event-dashboard/<int:event_id>/join-requests/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_join_request(event_id, request_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != session['user_id']:
        abort(403)

    join_request = EventJoinRequest.query.filter_by(id=request_id, event_id=event.id).first_or_404()
    join_request.status = 'approved'

    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=join_request.user_id).first()
    if participant is None:
        db.session.add(EventParticipant(event_id=event.id, user_id=join_request.user_id))

    db.session.commit()
    return redirect(url_for('event_dashboard', event_id=event.id, tab='participants'))


@app.route('/event-dashboard/<int:event_id>/join-requests/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_join_request(event_id, request_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != session['user_id']:
        abort(403)

    join_request = EventJoinRequest.query.filter_by(id=request_id, event_id=event.id).first_or_404()
    join_request.status = 'rejected'
    db.session.commit()
    return redirect(url_for('event_dashboard', event_id=event.id, tab='participants'))


@app.route('/event-dashboard/<int:event_id>/vote-options', methods=['POST'])
@login_required
def add_vote_option(event_id):
    event = Event.query.get_or_404(event_id)
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if event.is_private and event.user_id != session['user_id'] and participant is None:
        abort(403)
    title = (request.form.get('title') or '').strip()
    if title:
        db.session.add(EventVoteOption(event_id=event.id, title=title))
        db.session.commit()
    return redirect(url_for('event_dashboard', event_id=event.id, tab='voting'))


@app.route('/event-dashboard/<int:event_id>/vote/<int:option_id>', methods=['POST'])
@login_required
def cast_vote(event_id, option_id):
    event = Event.query.get_or_404(event_id)
    option = EventVoteOption.query.filter_by(id=option_id, event_id=event.id).first_or_404()
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if event.is_private and event.user_id != session['user_id'] and participant is None:
        abort(403)

    existing_vote = EventVote.query.join(EventVoteOption).filter(
        EventVote.user_id == session['user_id'],
        EventVoteOption.event_id == event.id,
    ).first()
    if existing_vote:
        db.session.delete(existing_vote)
        db.session.commit()

    db.session.add(EventVote(option_id=option.id, user_id=session['user_id']))
    db.session.commit()
    return redirect(url_for('event_dashboard', event_id=event.id, tab='voting'))


@app.route('/event-dashboard/<int:event_id>/expenses', methods=['POST'])
@login_required
def add_expense(event_id):
    event = Event.query.get_or_404(event_id)
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if event.is_private and event.user_id != session['user_id'] and participant is None:
        abort(403)
    title = (request.form.get('title') or '').strip()
    amount_raw = (request.form.get('amount') or '').strip()
    try:
        amount = float(amount_raw)
    except ValueError:
        amount = 0.0
    if title:
        db.session.add(EventExpense(event_id=event.id, title=title, amount=amount, paid_by=session.get('username')))
        db.session.commit()
    return redirect(url_for('event_dashboard', event_id=event.id, tab='expenses'))


@app.route('/event-dashboard/<int:event_id>/checklist', methods=['POST'])
@login_required
def add_checklist_item(event_id):
    event = Event.query.get_or_404(event_id)
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if event.is_private and event.user_id != session['user_id'] and participant is None:
        abort(403)
    title = (request.form.get('title') or '').strip()
    if title:
        db.session.add(EventChecklistItem(event_id=event.id, title=title))
        db.session.commit()
    return redirect(url_for('event_dashboard', event_id=event.id, tab='checklist'))


@app.route('/event-dashboard/<int:event_id>/discussion', methods=['POST'])
@login_required
def add_discussion_message(event_id):
    event = Event.query.get_or_404(event_id)
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if event.is_private and event.user_id != session['user_id'] and participant is None:
        abort(403)

    content = (request.form.get('content') or '').strip()
    if content:
        db.session.add(EventDiscussionMessage(event_id=event.id, user_id=session['user_id'], content=content))
        db.session.commit()

    return redirect(url_for('event_dashboard', event_id=event.id, tab='discussion'))


def _can_access_event(event, user_id):
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=user_id).first()
    if event.is_private and event.user_id != user_id and participant is None:
        return False
    return True


@socketio.on('join_event_room')
def handle_join_event_room(data):
    if 'user_id' not in session:
        emit('discussion_error', {'message': 'Authentication required.'})
        return

    event_id_raw = (data or {}).get('event_id')
    try:
        event_id = int(event_id_raw)
    except (TypeError, ValueError):
        emit('discussion_error', {'message': 'Invalid event id.'})
        return

    event = Event.query.get(event_id)
    if event is None or not _can_access_event(event, session['user_id']):
        emit('discussion_error', {'message': 'Access denied for this event.'})
        return

    join_room(f'event_{event.id}')


@socketio.on('post_discussion_message')
def handle_post_discussion_message(data):
    if 'user_id' not in session:
        emit('discussion_error', {'message': 'Authentication required.'})
        return

    payload = data or {}
    event_id_raw = payload.get('event_id')
    content = (payload.get('content') or '').strip()

    try:
        event_id = int(event_id_raw)
    except (TypeError, ValueError):
        emit('discussion_error', {'message': 'Invalid event id.'})
        return

    if not content:
        emit('discussion_error', {'message': 'Message cannot be empty.'})
        return

    event = Event.query.get(event_id)
    if event is None or not _can_access_event(event, session['user_id']):
        emit('discussion_error', {'message': 'Access denied for this event.'})
        return

    message = EventDiscussionMessage(event_id=event.id, user_id=session['user_id'], content=content)
    db.session.add(message)
    db.session.commit()

    username = session.get('username') or 'Unknown'
    message_payload = {
        'username': username,
        'content': message.content,
        'created_at': format_awst(message.created_at),
    }
    emit('new_discussion_message', message_payload, room=f'event_{event.id}')


@app.route('/event-dashboard/<int:event_id>/checklist/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_checklist_item(event_id, item_id):
    event = Event.query.get_or_404(event_id)
    item = EventChecklistItem.query.filter_by(id=item_id, event_id=event.id).first_or_404()
    participant = EventParticipant.query.filter_by(event_id=event.id, user_id=session['user_id']).first()
    if event.is_private and event.user_id != session['user_id'] and participant is None:
        abort(403)
    item.completed = not item.completed
    db.session.commit()
    return redirect(url_for('event_dashboard', event_id=event.id, tab='checklist'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/user')
def get_user():
    """API endpoint to get current user info"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
    return jsonify({'error': 'Not logged in'}), 401

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))