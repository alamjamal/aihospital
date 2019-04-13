
from flask import render_template, request, redirect,flash,url_for,session,abort
from app import app, db
from app.models import Employee_login,Patient_login,Patient_data,Heart_data,Disease_Present_Data
#from werkzeug.security import generate_password_hash, check_password_hash
import urllib.request
import simplejson as json
import pickle
import pandas as pd
with open(f'model/NBmodel.pkl', 'rb') as f:
    model = pickle.load(f)

@app.context_processor
def utility_processor():
    def thingspeek():
        datafromwebsite=urllib.request.urlopen("https://api.thingspeak.com/channels/744886/fields/1/last.txt");
        select=datafromwebsite.read();
        data = json.loads(select)
        # a=data['field1']
        # return a
        return data
    return dict(thingspeek=thingspeek)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/userheartpredict')
def userheartpredict():
    return render_template('userheartpredict.html')


@app.route('/heartpredict', methods=['POST'])
def heartpredict():
    pid = request.form.get('pid')
    pat = Heart_data.query.filter_by(pid=pid).first() #when we use .all() then use for loop to itrate
    input_variables = pd.DataFrame([[pat.age, pat.sex, pat.cp,pat.trestbps,pat.chol, pat.fbs,pat.restecg,pat.thalach,pat.exang,pat.oldpeak,pat.slope,pat.ca,pat.thal]],
                                    columns=['age', 'sex', 'cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal'],
                                    dtype=float,
                                    index=['input'])

    # Get the model's prediction
    #df = df.reset_index()
    print(input_variables.head())
    prediction = model.predict(input_variables)[0]
    dat=Disease_Present_Data(disease=int(prediction),pid=pid)
    db.session.add(dat)
    db.session.commit()
    return render_template('adminheartpredict.html',prediction=prediction)




@app.route('/admindiseasedetails')
def admindiseasedetails():
    if not session.get('logged_in'):
        return redirect(url_for('elogin'))
    else:
        data=Disease_Present_Data.query.all()

        return render_template('admindiseasedetails.html',disease_data=data)


@app.route('/deletedisease/<string:id>', methods=['GET'])
def deletedisease(id):
    id=int(id)
    pat=Disease_Present_Data.query.filter_by(did=id).first()
    db.session.delete(pat)
    flash("Record Has Been Deleted Successfully")
    db.session.commit()
    return redirect(url_for('admindiseasedetails'))






@app.route('/showpatientgraph')
def showpatientgraph():
    return render_template('adminblank.html')

@app.route('/elogin')
def elogin():
	if session.get('logged_in'):
		return redirect(url_for('showpatient'))
	else:
		return render_template('employeelogin.html')



@app.route('/elogin', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = Employee_login.query.filter_by(email=email).first()
    session['user'] = email
    if user:
    	if(user.password==password):
    		session['logged_in'] = True
    		return redirect(url_for('showpatientgraph'))
    		#login_user(user, remember=remember)
    		#data=Patient_data.query.all()
    		#return render_template('addpatient.html',patient_data=data)

    	else:
    		flash('Please check your password and try again.')
    		return redirect(url_for('elogin'))
    else:
    	flash('Please check your email  and try again.')
    	return redirect(url_for('elogin'))    

    # if the above check passes, then we know the user has the right credentials
    # login_user(user, remember=remember)
    # return redirect(url_for('about'))

    # if login_user(user):
    #     return redirect(url_for('about'))


@app.route('/showpatient')
def showpatient():
	if not session.get('logged_in'):
		return redirect(url_for('elogin'))
	else:
		data=Patient_data.query.all()
		return render_template('addpatient.html',patient_data=data)


@app.route('/addpatient', methods=['POST'])
def addpatient():
    patient_data =Patient_data(name=request.form.get('name'), email=request.form.get('email'),phone=request.form.get('phone'))
    db.session.add(patient_data)
    flash("Record Has Been Added Successfully")
    db.session.commit()
    return redirect(url_for('showpatient'))


@app.route('/updatepatient', methods=['GET','POST'])
def updatepatient():
	id = request.form.get('id')
	name = request.form.get('name')
	email = request.form.get('email')
	phone = request.form.get('phone')
	pat = Patient_data.query.filter_by(id=id).first()
	pat.name=name
	pat.email=email
	pat.phone=phone
	db.session.commit()
	flash("Record Has Been Updated Successfully")
	return redirect(url_for('showpatient'))



@app.route('/deletepatient/<string:email>', methods=['GET'])
def deletepatient(email):
    pat=Patient_data.query.filter_by(email=email).first()
    db.session.delete(pat)
    flash("Record Has Been Deleted Successfully")
    db.session.commit()
    return redirect(url_for('showpatient'))


@app.route('/shownotadded')
def shownotadded():
    if not session.get('logged_in'):
        return redirect(url_for('elogin'))
    else:
        data=Patient_data.query.filter_by(added='No').all()
        # pid=1
        # datafromwebsite=urllib.request.urlopen("https://api.thingspeak.com/channels/744886/fields/1/%s.txt" %pid);
        # select=datafromwebsite.read();
        # iotdata = json.loads(select)
        # print(iotdata['field1'])

        return render_template('shownotadded.html',patient_data=data)


@app.route('/showadded')
def showadded():
    if not session.get('logged_in'):
        return redirect(url_for('elogin'))
    else:
        data=Patient_data.query.filter_by(added='Yes').all() 
        # d=Patient_data.query.filter_by(id=1).first()
        return render_template('showadded.html',patient_data=data)





@app.route('/addheartdisease', methods=['POST'])
def addheartdisease():
    pid=request.form.get('pid')
    disease_data =Heart_data(age=request.form.get('age'), sex=request.form.get('sex'),cp=request.form.get('cp'),trestbps=request.form.get('trestbps'),chol=request.form.get('chol'),fbs=request.form.get('fbs'),restecg=request.form.get('restecg'),thalach=request.form.get('thalach'),exang=request.form.get('exang'),oldpeak=request.form.get('oldpeak'),slope=request.form.get('slope'),ca=request.form.get('ca'),thal=request.form.get('thal'),pid=request.form.get('pid'))
    pat = Patient_data.query.filter_by(id=pid).first()
    pat.added='Yes'
    db.session.add(disease_data)
    flash("Record Has Been Added Successfully")
    db.session.commit()
    return redirect(url_for('shownotadded'))




@app.route('/updateheartdisease', methods=['GET','POST'])
def updateheartdisease():
    id = request.form.get('id')
    age = request.form.get('age')
    sex = request.form.get('sex')
    cp = request.form.get('cp')
    trestbps = request.form.get('trestbps')
    chol = request.form.get('chol')
    fbs = request.form.get('fbs')
    restecg = request.form.get('restecg')
    thalach = request.form.get('thalach')
    exang = request.form.get('exang')
    oldpeak = request.form.get('oldpeak')
    slope = request.form.get('slope')
    ca = request.form.get('ca')
    thal = request.form.get('thal')
    print(age)
    pat = Heart_data.query.filter_by(id=id).first()
    print(pat.age)
    pat.age=age
    pat.sex=sex
    pat.cp=cp
    pat.trestbps=trestbps
    pat.chol=chol
    pat.fbs=fbs
    pat.restecg=restecg
    pat.thalach=thalach
    pat.exang=exang
    pat.oldpeak=oldpeak
    pat.slope=slope
    pat.ca=ca
    pat.thal=thal  
    db.session.commit()
    flash("Record Has Been Updated Successfully")
    return redirect(url_for('showadded'))













@app.route('/plogin')
def pplogin():
    if session.get('plogged_in'):
        return redirect(url_for('usermainpage'))
    else:
        return render_template('patientlogin.html')




@app.route('/plogin',methods=['POST'])
def plogin():
    email = request.form.get('email')
    phone = request.form.get('phone')
    remember = True if request.form.get('remember') else False
    puser = Patient_data.query.filter_by(email=email).first()
    if puser:
        if(puser.phone==phone):
            print('i m in phone==phone')
            session['plogged_in'] = True
            #return redirect(url_for('usermainpage'))
            #login_user(user, remember=remember)
            #data=Patient_data.query.all()
            data = Disease_Present_Data.query.filter_by(pid=puser.id).first()
            session['disease']=data.disease
            return render_template('usermainpage.html')
        else:
            flash('Please check your phone details and try again.')
            return redirect(url_for('plogin'))
    else:
        flash('Please check your email details and try again.')
        return redirect(url_for('plogin'))  



@app.route('/usermainpage')
def usermainpage():  
    return render_template('usermainpage.html')









@app.route("/logout")
def logout():
    session['plogged_in'] = False
    session['logged_in'] = False
    return redirect(url_for('index'))










@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404



if __name__=='__main__':
	app.run()