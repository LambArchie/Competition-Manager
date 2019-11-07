"""
Controls pages directly related to the overall competitions
"""
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.database.models import Competition
from app.competition import bp
from app.competition.forms import CompetitionForm
from app.admin.routes import check_permissions

@bp.route('/')
@login_required
def competitions_overview():
    """Lists all competitions"""
    comps = [competition.to_json() for competition in Competition.query.all()]
    return render_template('competition/index.html', title="Competitions", competitions=comps,
                           admin=current_user.admin)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def competition_create():
    """Creates a competition"""
    check_permissions()
    form = CompetitionForm()
    if form.validate_on_submit():
        competition = Competition(name=form.name.data,
                                  body=form.body.data
                                 )
        db.session.add(competition)
        db.session.commit()
        flash('Competition created successfully')
        return redirect(url_for('competition.categories_overview', comp_id=competition.id))
    return render_template('competition/competitionCreate.html', title='Create Competition',
                           form=form)

@bp.route('/<int:comp_id>/edit', methods=['GET', 'POST'])
@login_required
def competition_edit(comp_id):
    """Edits a submission"""
    competition = Competition.query.filter_by(id=comp_id).first_or_404()
    form = CompetitionForm()
    check_permissions()
    if request.method == 'GET':
        form.name.data = competition.name
        form.body.data = competition.body
    if form.validate_on_submit():
        competition.name = form.name.data
        competition.body = form.body.data
        db.session.commit()
        flash('Competition edited successfully')
        return redirect(url_for('competition.categories_overview', comp_id=comp_id))
    return render_template('competition/competitionEdit.html', title='Edit Competition', form=form)
