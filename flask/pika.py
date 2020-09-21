from flask import Flask,redirect,session,url_for,request,Response,render_template,flash,session
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,DateField,TextAreaField,SubmitField,HiddenField,IntegerField
from wtforms.validators import InputRequired,Length
from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from flask_pymongo import pymongo,PyMongo,ObjectId
import json
import pymongo

app=Flask(__name__)

Bootstrap(app)

app.config['SECRET_KEY']='secret'

class SignupForm(FlaskForm):
   
    name = StringField('Name',validators=[InputRequired()])
    mail = StringField('E-mail',validators=[InputRequired()])
    password = PasswordField('Password',validators=[InputRequired()])
 
class LoginForm(FlaskForm):

    log_mail = StringField('E-mail',validators=[InputRequired()])
    log_password = PasswordField('Password',validators=[InputRequired()]) 


class InsertMovieForm(FlaskForm):

    title=StringField("Title",validators=[InputRequired()])
    release_date=StringField("Release Date",validators=[InputRequired()])
    description=TextAreaField("Description",validators=[InputRequired()])
    screening_dates=StringField("Screening Dates",validators=[InputRequired()])


class DeleteMovieForm(FlaskForm):
    deltitle=StringField("Movie",validators=[InputRequired()])

class FindMovieForm(FlaskForm):
    f_title=StringField("Find Movie to update",validators=[InputRequired()])

class UpdateMovieForm(FlaskForm):
    prev_title=HiddenField()
    u_title=StringField("Title",validators=[InputRequired()])
    u_release_date=StringField("Release date",validators=[InputRequired()])
    u_description=StringField("Description",validators=[InputRequired()])
    u_screening_dates=StringField("Screening dates",validators=[InputRequired()])
    
class AddAdminForm(FlaskForm):
    admin_name=StringField("Name",validators=[InputRequired()])
    admin_mail=StringField("E-mail",validators=[InputRequired()])
    admin_password=PasswordField("Password",validators=[InputRequired()])

class SearchMovieForm(FlaskForm):
    s_movie=StringField("Movie Title",validators=[InputRequired()])

class BuyTicketForm(FlaskForm):
    t_ticket_num=IntegerField(validators=[InputRequired()])
    t_title=HiddenField()
    t_screening_date=HiddenField()
    t_movie_id=HiddenField()
    t_sits_left=HiddenField()


try :
    client = MongoClient('mongodb',
        port=27017,
        serverSelectionTimeoutMS=10000
    )
    db=client['InfoCinemas']
    movies=db['movies']
    users=db['users']

except:
    print("Cannot connect to db")


@app.route('/',methods=['GET', 'POST'])
def sign_up_page():
  
    users=db['users']
    
    form=SignupForm()
    login=LoginForm()
    if form.validate:
        if request.form.get("submit","")=="Signup":
            existing = users.find_one({"mail":form.mail.data})
            if existing is None:
                    flash("User '{}' successfuly signed up.".format(form.name.data),"sign")
                    user={"name":form.name.data,"mail":form.mail.data,"password":form.password.data,"movies_seen":[],"admin":"no"}
                    users.insert_one(user)
                    
            else:
                flash("E-mail '{}' is already registered!".format(form.mail.data),"not_sign")
        
        elif request.form.get("submit","")=="Login":
            existing = users.find_one({"mail":login.log_mail.data})
            
            if existing is not None:
            
                passwordcheck=users.find_one({"mail":login.log_mail.data,"password":login.log_password.data})

                if passwordcheck is None:
                    flash("Wrong Password.","danger2")
                else:
                    user=passwordcheck['name']
                    if  passwordcheck['admin']=='no':
                        session.clear()
                        session['mail']=passwordcheck['mail']
                        session['USER']=True           
                        session['ADMIN']=False         
                        return redirect(url_for('user_home',logged_user=passwordcheck['name']))
                    else:
                        session.clear()
                        session['ADMIN']=True
                        session['USER']=False
                        session['mail']=passwordcheck['mail']
                        return redirect(url_for('admin_home',logged_user=passwordcheck['name']))

            else:
                flash("User doesn't exist.","danger2")
        else:
            session.clear()
            session['USER']=False 
            session['ADMIN']=False 
    return render_template("home_page.html",form=form,login=login)


@app.route("/admin/<logged_user>",methods=['POST','GET'])
def admin_home(logged_user):
    
    if 'mail' in session and session['ADMIN']==True:
       
        if request.form.get("choose","")=="Insert":
            return redirect(url_for('insert_movie',logged_user=logged_user))
        
        elif request.form.get("choose","")=="Update":
            return redirect(url_for('update_movie',logged_user=logged_user))
        
        elif request.form.get("choose","")=="Delete":
            return redirect(url_for('delete_movie',logged_user=logged_user))
        
        elif request.form.get("choose","")=="Admin":
            return redirect(url_for('add_admin',logged_user=logged_user))
        
        elif request.form.get("submit","")=='Home' and request.method=='POST':
            return redirect(url_for("admin_home",logged_user=logged_user)) 

        elif request.form.get("submit","")=='log_out' and request.method=='POST':
            session.clear()
            return redirect(url_for("sign_up_page")) 
        
        return render_template("admin_home.html",logged_user=logged_user)
    else:
        return render_template("error.html")

@app.route("/admin/<logged_user>/insert_movie",methods=['POST',"GET"])
def insert_movie(logged_user):
    if 'mail' in session and session['ADMIN']==True:
    
        insertmovieform=InsertMovieForm()
        
        if request.form.get("submit","")=='log_out' and request.method=='POST':
            session.clear()
            return redirect(url_for("sign_up_page"))

        if request.form.get("submit","")=="Insert_movie" and insertmovieform.validate_on_submit and request.method=='POST':    
            scr=[]
            screenings=insertmovieform.screening_dates.data.split(",")
            for x in screenings:
                scr.append({'screening_date':x,'sits_left':'50'})
            new_movie={"title":insertmovieform.title.data,"release_date":insertmovieform.release_date.data,
            "description":insertmovieform.description.data,"screening_dates":scr}
        
            movies.insert_one(new_movie)
            flash("Movie succesfully inserted to database.","insert")
        
        elif request.form.get("submit","")=='Home' and request.method=='POST':
           
            return redirect(url_for("admin_home",logged_user=logged_user)) 
        
        return render_template("insert_movie.html",logged_user=logged_user,insertmovieform=insertmovieform)
    
    else:
        return render_template("error.html")
@app.route("/admin/<logged_user>/update_movie",methods=['POST','GET'])
def update_movie(logged_user):
    
    if 'mail' in session and session['ADMIN']==True:
        findmovieform=FindMovieForm()
        updatemovieform=UpdateMovieForm()

        if request.form.get("submit","")=='log_out' and request.method=='POST':
                    session.clear()
                    return redirect(url_for("sign_up_page"))
       
        if request.form.get("submit","")=='Home' and request.method=='POST':
            return redirect(url_for("admin_home",logged_user=logged_user)) 
       
        if request.form.get("submit","")=='Find_movie' and findmovieform.validate_on_submit and request.method=='POST':
            
            if movies.find_one({"title":findmovieform.f_title.data}):
            
                x=movies.find_one({"title":findmovieform.f_title.data})
                a=x['title']
                b=x['release_date']
                c=x['description']
                d=x['screening_dates']
                flash(a,'vars1')
                flash(b,'vars2')
                flash(c,'vars3')
                e=''
                
                for ar in range(len(d)):
                    if ar==len(d)-1:
                        e+=d[ar]['screening_date']
                        break
                    e+=d[ar]['screening_date']+str(",")

                flash(e,'vars4')
                
            else:
                flash("Movie not found.","not_found")
        
        elif request.form.get("submit","")=='Update_movie' and updatemovieform.validate_on_submit and request.method=='POST':
                
                new_screenings=updatemovieform.u_screening_dates.data.split(",")
                scr=[]

                for  new_screening in new_screenings:
                    scr.append({"screening_date":new_screening,"sits_left":"50"})

                db.movies.update_one({"title":updatemovieform.prev_title.data},
                {'$set':{"title":updatemovieform.u_title.data,"release_date":updatemovieform.u_release_date.data,
                "description":updatemovieform.u_description.data,"screening_dates":scr}})
                flash("Movie successfully updated.","updated")
        
        return render_template("update_movie.html",logged_user=logged_user,findmovieform=findmovieform,updatemovieform=updatemovieform)
    
    else:
    
      return render_template("error.html")
@app.route("/admin/<logged_user>/delete_movie",methods=["POST","GET"])
def delete_movie(logged_user):
    
    if 'mail' in session and session['ADMIN']==True:
    
        deletemovieform=DeleteMovieForm()
       
        if request.form.get("submit","")=='Home' and request.method=='POST':
            return redirect(url_for("admin_home",logged_user=logged_user))     
       
        if request.form.get("submit","")=='Delete_movie' and deletemovieform.validate_on_submit and request.method=='POST':
    
            if movies.find_one({"title":deletemovieform.deltitle.data}):
                db.movies.delete_one({"title":deletemovieform.deltitle.data})
                flash("Movie succesfully deleted.","delete")
    
            else:
    
                flash("Movie not found.","delete2")
    
    
        if request.form.get("submit","")=='log_out' and request.method=='POST':
    
            session.clear()
            return redirect(url_for("sign_up_page")) 
    
        return render_template("delete_movie.html",logged_user=logged_user,deletemovieform=deletemovieform)
    
    else:
    
        return render_template("error.html")
@app.route("/admin/<logged_user>/add_admin",methods=['POST','GET'])
def add_admin(logged_user):
    
    if 'mail' in session and session['ADMIN']==True:    
        addadminform=AddAdminForm()

        if request.form.get("submit","")=='log_out' and request.method=='POST':
            session.clear()
            return redirect(url_for("sign_up_page")) 
       
        if request.form.get("submit","")=='Home' and request.method=='POST':
            return redirect(url_for("admin_home",logged_user=logged_user)) 
       
        if request.form.get("submit","")=='Add_admin' and addadminform.validate_on_submit and request.method=='POST':
            existing = users.find_one({"mail":addadminform.admin_mail.data})
    
            if existing is None:
                    flash( "Admin {} succesfully registered.".format(addadminform.admin_name.data),"success")
                    admin={"name":addadminform.admin_name.data,"mail":addadminform.admin_mail.data,"password":addadminform.admin_password.data,"admin":"yes"}
                    users.insert_one(admin)
    
            else:
                flash("Someone has already registered with this e-mail!","danger")
    
        return render_template("add_admin.html",logged_user=logged_user,addadminform=addadminform)
   
    else:
        return render_template("error.html")       
@app.route("/user_home/<logged_user>",methods=["POST","GET"])
def user_home(logged_user):
    
    if 'mail' in session and session['USER']==True :
   
        searchmovieform=SearchMovieForm()
        buyticketform=BuyTicketForm()
        
        if request.form.get("submit","")=='Search_movie' and searchmovieform.validate_on_submit and request.method=='POST':   
            
            if movies.find_one({"title":searchmovieform.s_movie.data}):
                
                movie=movies.find({"title":searchmovieform.s_movie.data})
                flash(movie,"movie_info")
                
            else:
            
                flash("No movie with this title.","not_found")

        elif request.form.get("submit","")=='choose_movie' and buyticketform.validate_on_submit  and request.method=='POST':  

            ticket_num=buyticketform.t_ticket_num.data
            title=buyticketform.t_title.data
            screening_date=buyticketform.t_screening_date.data
            movie_id=buyticketform.t_movie_id.data
            sits_left=buyticketform.t_sits_left.data

            if int(sits_left)<int(ticket_num):
                flash("Invalid amount of tickets.","invalid")
            
            else:
                session['movie_id']=movie_id
                session['ticket_num']=ticket_num
                session['title']=title
                session['screening_date']=screening_date

                flash(title,'title')
                flash(screening_date,'screening_date')
                flash(ticket_num,'ticket_num')
    
        elif request.form.get("submit","")=='submit_order' and request.method=='POST': 
            movie=movies.find_one({"_id" : ObjectId(session['movie_id'])})         
            dates=movie['screening_dates']
   
            for date in dates:
   
                if date['screening_date']==session['screening_date']:
                    
                    sits_left=int(date['sits_left'])-int(session['ticket_num'])
                    db.movies.update_one({"title":session['title'],"screening_dates.screening_date":session['screening_date']},{'$set':{'screening_dates.$.sits_left':sits_left}})

                    db.users.update_one({"mail":session['mail']},{'$push':{'movies_seen':[session['movie_id'],session['ticket_num']]}})
                    
                    flash("Book successful.",'book')
                    
        elif request.form.get("submit","")=='history' and request.method=='POST':       
            
            return redirect(url_for("user_history",logged_user=logged_user))
        
        elif request.form.get("submit","")=='log_out' and request.method=='POST':
   
            session.clear()
            return redirect(url_for("sign_up_page"))    

        return render_template("user_home.html",logged_user=logged_user,searchmovieform=searchmovieform,buyticketform=buyticketform)       
   
    else:
        return render_template("error.html")
        
@app.route("/user_history/<logged_user>",methods=['POST','GET'])
def user_history(logged_user):
    if 'mail' in session and session['USER']==True:
   
        user=users.find_one({'mail':session['mail']})
        movies_seen=user['movies_seen']
        movs=[]
   
        if movies_seen:
   
            for mov in movies_seen:
                x=movies.find_one({"_id" : ObjectId(mov[0])})
   
                if x is not None:
                    movs.append([x['title'],mov[1]])
   
                else:
                    movs.append(['This movie was removed from Cinemas Database',mov[1]])
   
            flash(movs,'movies_seen')
   
        else:
   
            flash('No Movies Booked','no_movies')
   
        if request.form.get("submit","")=='log_out' and request.method=='POST':
            session.clear()
            return redirect(url_for("sign_up_page")) 
                     
        elif request.form.get("submit","")=='home' and request.method=='POST':       
            
            return redirect(url_for("user_home",logged_user=logged_user)) 
        
        return render_template("user_history.html",logged_user=logged_user)
        
        
    
    else:
        return render_template("error.html")
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001,debug=True)