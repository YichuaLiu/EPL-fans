from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
import os
from app import app, bcrypt, db
from app.forms import *
from app.email import send_reset_password_mail
from app.models import User, Post


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ app.route('/', methods=['GET', 'POST'])
@ login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        body = form.text.data
        post = Post(body=body)
        current_user.posts.append(post)
        db.session.commit()
        flash('You have post a new tweet', category='success')
    n_followers = len(current_user.followers)
    n_followed = len(current_user.followed)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 5, False)
    return render_template("index.html", form=form, n_followers=n_followers, n_followed=n_followed, posts=posts)

@ app.route('/user_page/<username>')
@ login_required
def user_page(username):
    user = User.query.filter_by(username=username).first()
    if user:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(page, 5, False)
        return render_template('user_page.html', user=user, posts=posts)
    else:
        return '404'

@ app.route('/follow/<username>')
@ login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user:
        current_user.follow(user)
        db.session.commit()
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(page, 5, False)
        return render_template('user_page.html', user=user, posts=posts)
    else:
        return '404'

@ app.route('/unfollow/<username>')
@ login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user:
        current_user.unfollow(user)
        db.session.commit()
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(page, 5, False)
        return render_template('user_page.html', user=user, posts=posts)
    else:
        return '404'

@ app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = UplaodForm()
    if form.validate_on_submit():
        f = form.photo.data
        if f.filename == '':
            flash('No select file', category='danger')
            return render_template('edit_profile.html', form=form)
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join('app', 'static', 'asset', filename))
            current_user.avatar_img = '/static/asset/' + filename
            db.session.commit()
            return redirect(url_for('user_page', username=current_user.username))
    return render_template('edit_profile.html', form=form)

@ app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        # password = bcrypt.generate_password_hash(form.password.data)
        password = form.password.data
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Congrats, registeration success', category='success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@ app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(username=username).first()
        # if user and bcrypt.check_password_hash(user.password, password):
        check_gate = True
        if len(password) == len(user.password):
            for i in range(len(password)):
                if password[i] != user.password[i]:
                    check_gate = False
        else:
            check_gate = False
        if user and check_gate:
            # 用户存在且匹配
            login_user(user, remember=remember)
            flash('Login success', category='info')
            # if request.args.get('next'):
            #     next_page = request.args.get('next')
            #     print(next_page)
            #     return redirect(url_for(next_page))
            return redirect(url_for('index'))
        flash('User not exists or password not matches', category='danger')
    return render_template('login.html', form=form)

@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@ app.route('/send_password_reset_request', methods=['GET', 'POST'])
def send_password_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = user.generate_reset_password_token()
        send_reset_password_mail(user, token)
        flash('Password reset request mail is sent, please check your mail', category='info')
    return render_template('send_password_reset_request.html', form=form)

@ app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPassword()
    return render_template('reset_password.html', form=form)

@ app.route('/competition', methods=['GET', 'POST'])
@ login_required
def competition():
    form = CompetitionForm()
    if form.validate_on_submit():
        home_team = form.home_team.data
        away_team = form.away_team.data
        if home_team == away_team:
            flash('Same team!', category='danger')
            return redirect(url_for('competition'))
        else:
            club = db.Table('club', db.metadata, autoload=True, autoload_with=db.engine)
            match = db.Table('match', db.metadata, autoload=True, autoload_with=db.engine)
            score = db.Table('score', db.metadata, autoload=True, autoload_with=db.engine)
            home = db.session.query(club).filter(club.c.idClub == home_team)
            away = db.session.query(club).filter(club.c.idClub == away_team)
            for r_home in home:
                home_team_name = r_home.name
            for r_away in away:
                away_team_name = r_away.name
            result_match = db.session.query(match).filter(match.c.home == home_team and match.c.away == away_team)
            match_data = []
            for r in result_match:
                r_season = r.season
                temp_match = r.idMatch
                result_score = db.session.query(score).filter(score.c.fk_score_match == temp_match)
                for rr in result_score:
                    rr_half = rr.half[0] + ' ' + ':' + ' ' + rr.half[-1]
                    rr_full = rr.full[0] + ' ' + ':' + ' ' + rr.full[-1]
                    rr_result = rr.result
                    match_data.append([r_season, rr_half, rr_full, rr_result])
            return render_template('competition_result.html', home_team_name=home_team_name,
                                   away_team_name=away_team_name, match_data=match_data)
    return render_template('competition.html', form=form)

@ app.route('/Club', methods=['GET', 'POST'])
@ login_required
def club():
    form = ClubForm()
    if form.validate_on_submit():
        clubid = form.club.data
        club = db.Table('club', db.metadata, autoload=True, autoload_with=db.engine)
        stadium = db.Table('stadium', db.metadata, autoload=True, autoload_with=db.engine)
        history = db.Table('history', db.metadata, autoload=True, autoload_with=db.engine)
        manage = db.Table('manage', db.metadata, autoload=True, autoload_with=db.engine)
        manager = db.Table('manager', db.metadata, autoload=True, autoload_with=db.engine)
        trans = db.Table('trans', db.metadata, autoload=True, autoload_with=db.engine)
        player = db.Table('player', db.metadata, autoload=True, autoload_with=db.engine)
        club_name = db.session.query(club).filter(club.c.idClub == clubid)
        for r_club_name in club_name:
            name = r_club_name.name
            city = r_club_name.city
        stadium = db.session.query(stadium).filter(stadium.c.fk_stadium_club == clubid)
        for r_stadium in stadium:
            stadium_name = r_stadium.name
            stadium_capacity = r_stadium.capacity
            stadium_opened = r_stadium.opened
        stadium_description = stadium_name + ' is located in ' + city + ' and it is the home of ' + name \
                              + ' since ' + stadium_opened + ', which can contain ' \
                              + stadium_capacity + ' fans watching the game at same time.'
        history = db.session.query(history).filter(history.c.fk_history_club == clubid)
        history_num = 0
        for r_history in history:
            history_num = r_history.num
            history_champion = r_history.champion
        if history_num != 0:
            if len(history_champion) == 0:
                history_description = name + ' has already in the playoff ' + str(history_num) \
                                      + ". But they haven't got a champion yet!"
            else:
                history_description = name + ' has already in the playoff ' + str(history_num) \
                                    + ' times. They won the champion at ' + history_champion + ' season last time!'
        else:
            history_description = name + ' can get good grade in this year!'
        player = db.session.query(player).filter(player.c.fk_player_club == clubid)
        count = 0
        player_info =[]
        player_description = "There is a brief introduction of each player."
        for r_player in player:
            count += 1
            player_name = r_player.name
            player_position = r_player.position
            player_gaols = r_player.goals
            player_wins = r_player.wins
            player_losses = r_player.losses
            if player_wins == 0 and player_losses == 0:
                winning_rate = 0.0
            else:
                winning_rate = round(player_wins/(player_wins + player_losses)*100, 1)
            player_info.append([player_name, player_position, player_gaols,
                                player_wins, player_losses, winning_rate])
        player_sort = []
        while(len(player_info)>0):
            i = 0
            temp = 0
            max_wining_rate = player_info[0][5]
            while i < len(player_info):
                if player_info[i][5] > max_wining_rate:
                    max_wining_rate = player_info[i][5]
                    temp = i
                i += 1
            player_sort.append(player_info.pop(temp))
        if count < 11:
            player_description = "Sorry, we don't have enough data(player)! We only find " + str(count) + ' player(s).'
        trans = db.session.query(trans).filter(trans.c.fk_trans_club == clubid)
        trans_2018 = []
        trans_2017 = []
        trans_2016 = []
        trans_2015 = []
        for r_trans in trans:
            trans_season = r_trans.season
            trans_state = r_trans.state
            trans_times = r_trans.times
            trans_cost = r_trans.cost
            if trans_season == '2015':
                trans_2015.append(['#' + str(len(trans_2015)+1), trans_state, trans_times, trans_cost])
                if len(trans_2015) == 2:
                    if trans_2015[0][1] == 'in':
                        cost_2015 = trans_2015[1][3] - trans_2015[0][3]
                    else:
                        cost_2015 = trans_2015[0][3] - trans_2015[1][3]
                    trans_2015.append(['Sum', '*', trans_2015[0][2] + trans_2015[1][2], cost_2015])
            if trans_season == '2016':
                trans_2016.append(['#' + str(len(trans_2016) + 1), trans_state, trans_times, trans_cost])
                if len(trans_2016) == 2:
                    if trans_2016[0][1] == 'in':
                        cost_2016 = trans_2016[1][3] - trans_2016[0][3]
                    else:
                        cost_2016 = trans_2016[0][3] - trans_2016[1][3]
                    trans_2016.append(['Sum', '*', trans_2016[0][2] + trans_2016[1][2], cost_2016])
            if trans_season == '2017':
                trans_2017.append(['#' + str(len(trans_2017)+1), trans_state, trans_times, trans_cost])
                if len(trans_2017) == 2:
                    if trans_2017[0][1] == 'in':
                        cost_2017 = trans_2017[1][3] - trans_2017[0][3]
                    else:
                        cost_2017 = trans_2017[0][3] - trans_2017[1][3]
                    trans_2017.append(['Sum', '*', trans_2017[0][2] + trans_2017[1][2], cost_2017])
            if trans_season == '2018':
                trans_2018.append(['#' + str(len(trans_2018)+1), trans_state, trans_times, trans_cost])
                if len(trans_2018) == 2:
                    if trans_2018[0][1] == 'in':
                        cost_2018 = trans_2018[1][3] - trans_2018[0][3]
                    else:
                        cost_2018 = trans_2018[0][3] - trans_2018[1][3]
                    trans_2018.append(['Sum', '*', trans_2018[0][2] + trans_2018[1][2], cost_2018])

        def todatetime(time):
            record = []
            datetime = ''
            for i in range(len(time)):
                if time[i] == '-':
                    record.append(i)
            if len(record) == 2:
                datetime = time[(record[0] + 1):record[1]] + '/'
                if time[record[0] - 1] == '1':
                    datetime += time[0:record[0]] + 'st/'
                elif time[record[0] - 1] == '2':
                    datetime += time[0:record[0]] + 'nd/'
                elif time[record[0] - 1] == '3':
                    datetime += time[0:record[0]] + 'rd/'
                else:
                    datetime += time[0:record[0]] + 'th/'
                if time[record[1] + 1] == '0' or time[record[1] + 1] == '1':
                    datetime += '20' + time[record[1] + 1:]
                else:
                    datetime += '19' + time[record[1] + 1:]
            return datetime


        manager_info = []
        manager_description = "Sorry, we can't find current coach!"
        manage = db.session.query(manage).filter(manage.c.fk_manage_club == clubid)
        for r_manage in manage:
            temp_coach = r_manage.idManage
            start = todatetime(r_manage.start)
            end = todatetime(r_manage.end)
            if len(start) != 0 and len(end) == 0:
                end = 'Present*'
            r_manager = db.session.query(manager).filter(manager.c.idManager == temp_coach)
            for rr in r_manager:
                manager_name = rr.name
                nationality = rr.nationality
                length = rr.length
            manager_info.append([manager_name, nationality, start, end, length])
        for i in range(len(manager_info)):
            if manager_info[i][3] == 'Present*':
                manager_description = 'Current coach is ' + manager_info[i][0] + ', who is from ' + manager_info[i][1] \
                                      + '. He(She) is the coach of ' + name + ' from ' + start + '.'
        return render_template('club_result.html', name=name, stadium_description=stadium_description,
                               history_description=history_description, player_info=player_sort,
                               player_description=player_description, trans_2015=trans_2015, trans_2016=trans_2016,
                               trans_2017=trans_2017, trans_2018=trans_2018, manager_info=manager_info,
                               manager_description=manager_description
                               )

    return render_template('club.html', form=form)


