from flask import Flask, render_template, url_for, request, session, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, user_logged_in
from passlib.context import CryptContext
from flask_session import Session
from flask_weasyprint import HTML, render_pdf
import json
from yaask.forms import LoginForm, RegisterForm, SubmitForm, QuizForm, SubmitForm2, GenerateForm, FilterForm
from yaask.auth import OAuthSignIn, GoogleSignIn
import math
from yaask.models import *
from yaask import app

SCHEMES = 'pbkdf2_sha256'
pwd_context = CryptContext(
    schemes=[SCHEMES],
    default=SCHEMES,
    pbkdf2_sha256__default_rounds=30000
    )

secret_key='hello_bhai'

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	# Flask-Login function
	if not current_user.is_anonymous():
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous():
		return redirect(url_for('home'))
	oauth = OAuthSignIn.get_provider(provider)
	name,username,email = oauth.callback()

	if email is None:
	# I need a valid email address for my user identification
		flash('Authentication failed.')
		return redirect(url_for('home'))

	# Look if the user already exists
	que=User.query.filter(User.email == email).first()
	email=str(email)
	if( que is None):
		user = User(
			name=name,
			username=username,
			email=email,
			phone_no="",
			password=os.getrandom(10, os.GRND_NONBLOCK),
			score=0
		)
		db.session.add(user)
		db.session.commit()
	else:
		user=que
	print (user)
	login_user(user)
	return redirect(url_for('home'))


def getStandings():
	users = User.query.order_by(User.score.desc())
	return users

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error=""
	if current_user is not None and current_user.is_authenticated():
		return redirect(url_for('home'))
	form = LoginForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(username=request.form['username']).first()
			if user is not None and pwd_context.verify(request.form['password'], user.password):
				login_user(user)
				flash('You have been logged in.')
				return redirect(url_for('home'))
			else:
				error = ' * Invalid Credentials'
		else:
			error = ' * Invalid Credentials'
			render_template('login.html', form=form, error=error)
	return render_template('login.html', form=form, error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	error=""
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User(
				name=form.name.data,
				username=form.username.data,
				email=form.email.data,
				phone_no=form.phone_no.data,
				password=form.password.data,
				score=0
			)
			que=User.query.filter(User.email == user.email).first()
			quee=User.query.filter(User.username == user.username).first()
			if(que is not None):
				error=" * email already registered"
			elif(quee is not None):
				error=" * username already taken"
			else:
				db.session.add(user)
				db.session.commit()
				login_user(user)
				return redirect(url_for('home'))

	return render_template('register.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out')
	return redirect(url_for('home'))

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
	try:
		form = SubmitForm()
		form1= SubmitForm2()
		if form1.validate_on_submit():
			print ("idhr")
			tags=request.form.getlist('select_tag')
			print(tags)
			questiondata = Questions(
				question=form1.question1.data,
				option1=-1,
				option2=-1,
				option3=-1,
				option4=-1,
				answer=form1.answer1.data,
				creatorid=current_user.id,
				category=form1.category1.data,
				difficulty=form1.difficulty1.data,
				question_score=0,
				comment=form1.comment1.data,
				tags=tags,
			)
			x=questiondata.question
			x=x.replace("{tex}","\[")
			x=x.replace("{/tex}","\]")
			questiondata.question=x

			db.session.add(questiondata)
			db.session.commit()
			return render_template('display_int.html', question_to_display=questiondata)
			
		if form.validate_on_submit():
			print ("udhr")
			tags=request.form.getlist('select_tag')
			print(tags)
			questiondata = Questions(
				question=form.question.data,
				option1=form.option1.data,
				option2=form.option2.data,
				option3=form.option3.data,
				option4=form.option4.data,
				answer=form.answer.data,
				creatorid=current_user.id,
				category=form.category.data,
				difficulty=form.difficulty.data,
				question_score=0,
				comment=form.comment.data,
				tags=tags,
			)
			x=questiondata.question
			x=x.replace("{tex}","\[")
			x=x.replace("{/tex}","\]")
			questiondata.question=x
			
			print ("question data-------------> ",questiondata.question)
			
			db.session.add(questiondata)
			db.session.commit()
			return render_template('display_mcq.html', question_to_display=questiondata)
		f = open("yaask/tag.txt", "r")
		x= (f.read())
		ini=0
		tag=[]
		for i in range (0,len(x)):
			if (x[i]=='\n'):
				tag.append(x[ini:i])
				ini=i+1
		tag.append(x[ini:len(x)])
		return render_template('submit.html', form=form, form1=form1, tag=tag)
	except:
		return redirect(url_for('login'))
	

@app.route('/display', methods=['GET', 'POST'])
@login_required
def display():
	form= FilterForm()
	if request.method== 'GET':
		subject=request.args.get('subject')
		tag=request.args.get('tag')
		difficulty=request.args.get('difficulty')
		page=request.args.get('page')
		pg=page
		form = FilterForm(subject=subject, tags=tag, difficulty=difficulty)
		if(page is None):
			questions_to_display = Questions.query.filter().all()
			limit= math.ceil(len(questions_to_display)/20)
			questions_to_display=questions_to_display[0:20]
			return render_template('display.html', questions_to_display=questions_to_display, pg=1,limit=limit, form=form, subject=subject, tags=tag, difficulty=difficulty)
		else:
			questions_to_display = Questions.query.filter().all()
			if(subject != 'all' and (subject is not None) and (subject != '') and (subject != 'None') ):
				questions_to_display=list(filter(lambda x:x.category == subject, questions_to_display)) 
			if(tag != 'all' and (tag is not None) and (tag != '')  and (tag != 'None') ):
				questions_to_display=list(filter(lambda x:x.tags == tag, questions_to_display)) 
			if(difficulty != 'all' and (difficulty is not None) and (difficulty != '') and (difficulty != 'None')  ):
				questions_to_display=list(filter(lambda x:x.difficulty == difficulty, questions_to_display)) 
			limit= math.ceil(len(questions_to_display)/20)
			page=int(page)
			page-=1
			page*=20
			questions_to_display=questions_to_display[page:page+20]
			return render_template('display.html', questions_to_display=questions_to_display, pg = pg, limit=limit, form=form, subject=subject, tags=tag, difficulty=difficulty)

	if request.method== 'POST':
		subject=form.subject.data
		tag=form.tags.data
		difficulty=form.difficulty.data
		questions_to_display = Questions.query.filter().all()
		if(subject != 'all'):
			questions_to_display=list(filter(lambda x:x.category == subject, questions_to_display)) 
		if(tag!= 'all'):
			questions_to_display=list(filter(lambda x:x.tags == tag, questions_to_display)) 
		if(difficulty!= 'all'):	
			questions_to_display=list(filter(lambda x:x.difficulty == difficulty, questions_to_display)) 
		limit= math.ceil(len(questions_to_display)/20)
		questions_to_display=questions_to_display[0:20]
		return render_template('display.html', questions_to_display=questions_to_display, pg=1,limit=limit, form=form, subject=subject, tags=tag, difficulty=difficulty)
	

@app.route('/display/<string:category>')
@login_required
def categorywise(category):
	categoryList = ['math',
		'chemistry',
		'physics',
		'biology',
		'other',]
	page=request.args.get('page')
	pg=page
	if category in categoryList:
		if(page is None):
			questions_to_display = Questions.query.filter().filter( Questions.category == category ).all()
			limit= len(questions_to_display)/20
			questions_to_display=questions_to_display[0:20]
			return render_template('display.html', questions_to_display=questions_to_display, cat=category, pg=1,limit=limit)
		else:
			questions_to_display = Questions.query.filter().filter( Questions.category == category ).all()
			limit= len(questions_to_display)/20
			questions_to_display=questions_to_display[0:20]
			return render_template('display.html', questions_to_display=questions_to_display, cat=category, pg=1,limit=limit)
			page=int(page)
			page-=1
			page*=20
			questions_to_display=questions_to_display[page:page+20]
			return render_template('display.html', questions_to_display=questions_to_display, cat=category, pg=pg,limit=limit)
			
	else:
		questions_to_display = Questions.query.filter().all()
		flash('Please enter a url where the category is any one of' + str(categoryList))
		return redirect(url_for('display.html', questions_to_display=questions_to_display))

@app.route('/editquestions', methods=['GET', 'POST'])
@login_required
def editquestions():
	try:
		qid=request.args.get('qid')
		print (qid)
		delet=Questions.query.filter(Questions.questionid==qid).one()
		db.session.delete(delet)
		db.session.commit()
		questions_to_display = Questions.query.filter(Questions.creatorid == str(current_user.id)).all()
		return render_template('individual_questions.html', questions_to_display=questions_to_display)
	except:
		questions_to_display = Questions.query.filter(Questions.creatorid == str(current_user.id)).all()
		return render_template('individual_questions.html', questions_to_display=questions_to_display)



@app.route('/score')
@login_required
def scoreboard():
	#To allow sorting by username just do an ajax request back to score board with argument (like /score/#username then /score/#score)
	users = User.query.order_by(User.score.desc())
	return render_template('scoreboard.html', users=users)


@app.route('/test', methods=['GET','POST'])
@login_required
def test():
	categoryList = ['math',
		'chemistry',
		'physics',
		'biology',
		'other',]
	#To allow sorting by username just do an ajax request back to score board with argument (like /score/#username then /score/#score)
	if request.method == 'GET':
		db.session.commit()
		questions_to_display = Questions.query.filter().all()
		return render_template('test.html', questions_to_display=questions_to_display, categoryList=categoryList)

	if request.method == 'POST':		
		questions_to_display = Questions.query.filter().all()
		selected=[]
		for question in questions_to_display:
			check=request.form.get(str(question.questionid))
			if check=="checked":
				selected.append(question.questionid)
		
		random_questions=[]
		for category in categoryList:
			n=request.form[category]
			# print (n, category)
			if  len(n)>0:
				temp=Questions.query.filter( ~Questions.questionid.in_(selected)).filter(Questions.category==category).order_by(Questions.question_score).limit(n).all()
			# print (selected)
				for t in temp:
					selected.append(t.questionid)
		# print (selected)
		for question in random_questions:
			print (question.question, question.question_score)
			selected.append(question.questionid)
		
		for question in questions_to_display:
			check=request.form.get(str(question.questionid))
			if check=="checked":
				question.question_score=question.question_score+1
				db.session.commit()
	
		for question in random_questions:
			question.question_score=question.question_score+1
			db.session.commit()
	
		testdata = Test(
			creatorid=current_user.id,
			selected=selected,
		)
		db.session.add(testdata)
		db.session.commit()
		session['selected']=selected
		session['testid']=testdata.testid
		questions_to_display = Questions.query.filter( Questions.questionid.in_(selected) ).all()
		
		return redirect(url_for('generated_test'))



@app.route('/preview-test', methods=['GET','POST'])
@login_required
def preview_test():
	if request.method=='GET':
		id=current_user.id
		test= Test.query.filter(Test.creatorid==id).all()
		return render_template ("preview-test.html",test=test)

	if request.method=='POST':
		print ("post")
		try:
			x=request.form['button']
			session['testid']=x
			return redirect(url_for('generated_test'))

		except:
			x=request.form['delete']
			delet=Test.query.filter(Test.testid==x).one()
			print (delet)
			db.session.delete(delet)
			print ("deleted")
			db.session.commit()
			return redirect(url_for('preview_test'))
		


@app.route('/generated_test', methods=['GET','POST'])
@login_required
def generated_test():
	testid=session.get('testid')
	z=Test.query.filter(Test.testid==testid).one()
	selected=z.selected
	form = GenerateForm()
	return render_template('chose_test.html',testid=testid,form=form)


@app.route('/online_test', methods=['GET','POST'])
@login_required
def online_test():
	if request.method=='GET':
		id=request.args.get('id')
		selected=Test.query.filter(Test.testid==id).one()
		selected=selected.selected
		questions_to_display = Questions.query.filter( Questions.questionid.in_(selected) ).all()
		return render_template("online_test.html",questions_to_display=questions_to_display,id=id)
	if request.method=='POST':
		id=request.args.get('id')
		selected=Test.query.filter(Test.testid==id).one()
		selected=selected.selected
		print (selected)
		score=0
		questions_to_display = Questions.query.filter( Questions.questionid.in_(selected) ).all()
		quest={}
		for x in selected:
			x=str(x)
			z=request.form[x]

			answer=Questions.query.filter(Questions.questionid==x).one()
			ans=answer.answer
			
			if ((answer.option1=='-1') and (answer.option2=='-1') and (answer.option3=='-1') and (answer.option4=='-1')):
				try:
					z=str(int(float(z)))
				except:
					z=""
				ans=str(int(float(ans)))
				if(len(z)==0):
					quest[answer]='N'
					pass
				elif (z==ans):
					quest[answer]='C'
					score=score+4
				else:
					quest[answer]='W'
					score=score-1
		
			else:
				if(z=='N'):
					quest[answer]='N'
					pass
				elif (z==ans):
					quest[answer]='C'
					score=score+4
				else:
					quest[answer]='W'
					score=score-1
		
		for x in quest:
			print (x,quest[x])
		return  render_template('result.html',score=score,questions_to_display=quest)

@app.route('/print_test', methods=['GET','POST'])
@login_required
def print_test():
	selected=session.get('selected')
	questions_to_display = Questions.query.filter( Questions.questionid.in_(selected) ).all()
	form= GenerateForm()
	name=form.name.data.upper()
	time=form.time.data
	institution=form.institution.data.upper()
	html= render_template("generate.html",questions_to_display=questions_to_display,name=name, time=time, institution=institution)
	return render_pdf(HTML(string=html))
