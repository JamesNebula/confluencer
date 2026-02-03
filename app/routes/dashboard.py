from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.forms import TradeEntryForm
from app.models import TradeHistory
from sqlalchemy import func

# Create blueprint (no URL prefix - routes will be at root level)
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    """
    Main dashboard page with trading statistics and recent trades.
    
    Displays:
        - Account balance
        - Total P/L
        - Win rate
        - Recent trades (last 10)
        - Quick stats
    """
    if current_user.is_authenticated:
    # Get user's recent trades (last 10)
        recent_trades = TradeHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(
            TradeHistory.created_at.desc()
        ).limit(10).all()

        # Calculate overall statistics
        total_trades = TradeHistory.query.filter_by(user_id=current_user.id).count()

        # Get all closed trades
        closed_trades = TradeHistory.query.filter_by(
            user_id=current_user.id,
            status='CLOSED'
        ).all()

        # Calculate win rate
        if closed_trades:
            winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
            win_rate = round((len(winning_trades) / len(closed_trades)) * 100, 2)
        else:
            win_rate = 0.0

        # Calculate total P/L
        total_pnl = sum(t.pnl for t in closed_trades if t.pnl) if closed_trades else 0.0
        total_pnl = round(total_pnl, 2)

        # Calculate P/L as percentage of account
        if current_user.account_balance and current_user.account_balance > 0:
            total_pnl_pct = round((total_pnl / current_user.account_balance) * 100, 2)
        else:
            total_pnl_pct = 0.0

        # Calculate open trades count
        open_trades_count = TradeHistory.query.filter_by(
            user_id=current_user.id,
            status='OPEN'
        ).count()

        # Calculate average win and average loss
        winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl and t.pnl < 0]

        avg_win = round(sum(t.pnl for t in winning_trades) / len(winning_trades), 2) if winning_trades else 0.0
        avg_loss = round(sum(t.pnl for t in losing_trades) / len(losing_trades), 2) if losing_trades else 0.0

        # Calculate profit factor (Gross Profit / Gross Loss)
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0.0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 1.0  # Avoid division by zero
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else 0.0

        return render_template('dashboard/index.html',
                             title='Dashboard',
                             recent_trades=recent_trades,
                             total_trades=total_trades,
                             open_trades_count=open_trades_count,
                             win_rate=win_rate,
                             total_pnl=total_pnl,
                             total_pnl_pct=total_pnl_pct,
                             avg_win=avg_win,
                             avg_loss=avg_loss,
                             profit_factor=profit_factor)
    else:
        return render_template('public/landing.html', title='Confluencer')


@dashboard_bp.route('/trade-history')
@login_required
def trade_history():
    """
    Full trade history page with pagination.
    """
    # Get page number from query string, default to 1
    page = request.args.get('page', 1, type=int)
    
    # Paginate trades (20 per page)
    trades_pagination = TradeHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        TradeHistory.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('dashboard/trade_history.html',
                         title='Trade History',
                         trades=trades_pagination)


@dashboard_bp.route('/add-trade', methods=['GET', 'POST'])
@login_required
def add_trade():
    """
    Add a new trade to the database.
    
    GET: Display trade entry form
    POST: Process form and save trade
    """
    form = TradeEntryForm()
    
    if form.validate_on_submit():
        # Create new trade
        trade = TradeHistory(
            user_id=current_user.id,
            currency_pair=form.currency_pair.data.upper(),
            direction=form.direction.data.upper(),
            entry_price=form.entry_price.data,
            stop_loss=form.stop_loss.data,
            take_profit=form.take_profit.data,
            position_size=form.position_size.data,
            notes=form.notes.data,
            status='OPEN'  # Trade starts as open
        )
        
        # Add to database
        db.session.add(trade)
        db.session.commit()
        
        flash(f'Trade {trade.direction} {trade.currency_pair} added successfully!', 'success')
        return redirect(url_for('dashboard.trade_history'))
    
    return render_template('dashboard/add_trade.html',
                         title='Add Trade',
                         form=form)


@dashboard_bp.route('/close-trade/<int:trade_id>', methods=['POST'])
@login_required
def close_trade(trade_id):
    """
    Close an open trade by setting exit price and calculating P/L.
    
    Args:
        trade_id (int): ID of trade to close
    """
    trade = TradeHistory.query.get_or_404(trade_id)
    
    # Security check: Ensure user owns this trade
    if trade.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.trade_history'))
    
    # Check if trade is already closed
    if trade.status != 'OPEN':
        flash('Trade is already closed.', 'warning')
        return redirect(url_for('dashboard.trade_history'))
    
    # Get exit price from form
    exit_price = request.form.get('exit_price')
    
    if not exit_price:
        flash('Exit price is required.', 'danger')
        return redirect(url_for('dashboard.trade_history'))
    
    try:
        trade.exit_price = float(exit_price)
    except ValueError:
        flash('Invalid exit price.', 'danger')
        return redirect(url_for('dashboard.trade_history'))
    
    # Calculate P/L
    trade.calculate_pnl()
    
    # Commit to database
    db.session.commit()
    
    # Flash success message with P/L
    pnl_sign = '+' if trade.pnl > 0 else ''
    flash(f'Trade closed! P/L: {pnl_sign}${trade.pnl:.2f}', 'success')
    return redirect(url_for('dashboard.trade_history'))