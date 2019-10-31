"""
Controls pages directly related to the overall competitions
"""
from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.database.models import Competition
from app.competition import bp
from app.competition.forms import CompetitionForm

@bp.route('/')
@login_required
def competitions_overview():
    """Lists all competitions"""
    comps = [competition.to_json() for competition in Competition.query.all()]
    return render_template('competition/index.html', title="Competitions", competitions=comps)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def competition_create():
    """Creates a competition"""
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
