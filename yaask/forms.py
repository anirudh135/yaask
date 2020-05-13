from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, BooleanField, IntegerField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.fields.html5 import EmailField
from wtforms import validators


class RegisterForm(Form):
	name = TextField(
		'name',
		validators=[DataRequired()]
	)
	username = TextField(
		'username',
		validators=[DataRequired(), Length(min=3, max=25)]
	)

	email = EmailField('Email address', [validators.DataRequired(), validators.Email()])

	phone_no = TextField(
		'phone number',
		validators=[DataRequired(), Length(min=12, max=13)]
	)
	password = PasswordField(
		'password',
		validators=[DataRequired(), Length(min=3, max=25)]
	)
	confirm = PasswordField(
		'confirm',
		validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
	)

class LoginForm(Form):
	username = TextField('username', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])

class SubmitForm(Form):
	question = CKEditorField('question', validators=[DataRequired()])
	option1 = TextField('option1', validators=[DataRequired()])
	option2 = TextField('option2', validators=[DataRequired()])
	option3 = TextField('option3', validators=[DataRequired()])
	option4 = TextField('option4', validators=[DataRequired()])
	answer = SelectField(
		'answer', 
		choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], 
		validators=[DataRequired()]
	)
	category = SelectField(
		'category', 
		choices=[('math', 'Math'), ('chemistry', 'Chemistry'), ('physics', 'Physics'), ('biology', 'Biology'), ('other', 'Other')], 
		validators=[DataRequired()]
	)
	difficulty = SelectField(
		'Difficulty', 
		choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
		validators=[DataRequired()]
	)
	comment = TextField('comment')


class SubmitForm2(Form):
	question1 = CKEditorField('question', validators=[DataRequired()])
	answer1 = FloatField('answer', validators=[DataRequired()])
	category1 = SelectField(
		'category', 
		choices=[('math', 'Math'), ('chemistry', 'Chemistry'), ('physics', 'Physics'), ('biology', 'Biology'), ('other', 'Other')], 
		validators=[DataRequired()]
	)
	difficulty1 = SelectField(
		'Difficulty', 
		choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
		validators=[DataRequired()]
	)
	comment1 = TextField('comment')

class QuizForm(Form):
	attempted_answer = SelectField(
		'attempted_answer',
		choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
		validators=[DataRequired()]
	)

class GenerateForm(Form):
	name = TextField('name', validators=[DataRequired()])
	time = IntegerField('time', validators=[DataRequired()])
	institution = TextField('institution', validators=[DataRequired()])


class FilterForm(Form):
	f = open("yaask/tag.txt", "r")
	x= (f.read())
	ini=0
	tag=[]
	tag.append(('all','All Tags'))
	for i in range (0,len(x)):
		if (x[i]=='\n'):
			tag.append((x[ini:i],x[ini:i]))
			ini=i+1
	tag.append((x[ini:len(x)],x[ini:len(x)]))
	subject = SelectField(
		'Subject', 
		choices=[('all','All Subjects'), ('math', 'Math'), ('chemistry', 'Chemistry'), ('physics', 'Physics'), ('biology', 'Biology'), ('other', 'Other')], 
		validators=[DataRequired()]
	)
	tags = SelectField(
		'Tags', 
		choices=tag,
		validators=[DataRequired()]
	)
	difficulty = SelectField(
		'Difficulty', 
		choices=[('all','All Difficulties'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
		validators=[DataRequired()]
	)
	