# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string
from dmgweb_packages.application import app, github, User, db_session

@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    next_url = app.next_url
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        user = User(access_token)
        db_session.add(user)
    user.github_access_token = access_token
    db_session.commit()

    session['user_id'] = user.id
    app.logger.info("Login....")
    #return redirect(url_for('index'))
    app.logger.info("Login : redirect to '{0}'".format(next_url))
    return redirect(next_url)


@app.route('/login')
def login():
    next_url = request.args.get('next') or url_for('index')
    app.next_url = next_url
    if app.GITHUB_AUTH_SKIPPING == True:
        app.logger.warning("Development mode : AUTHENTICATION SKIPPED (see config.json => github>skip")
        # we skip the authentication : 'dev mode'
        return redirect(url_for('index'))
    else:
        # we DO the authentication
        if session.get('user_id', None) is None:
            return github.authorize()
        else:
            return 'Already logged in'




@app.route('/logout')
def logout():
    session.pop('user_id', None)
    app.logger.info("Logout...")
    return redirect(url_for('index'))

