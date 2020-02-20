from flask import Flask,request,url_for,redirect,render_template,g
import sqlite3
from datetime import datetime
app=Flask(__name__)
def connect_db():
    sql=sqlite3.connect('E:/PythonPycharm/FoodTrackerApp/food_log.db')
    sql.row_factory=sqlite3.Row# to display result in form of dictionary instead of tuples
    return sql
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db=connect_db()# g means global
    return g.sqlite_db
@app.teardown_appcontext# to close database after each route
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()
@app.route("/",methods=['POST','GET'])
def index():
    db = get_db()
    if request.method=='POST':
        database_date=datetime.strptime(request.form['date'],"%Y-%m-%d")
        print(database_date)
        final_database_date=datetime.strftime(database_date,"%Y%m%d")
        print(final_database_date)
        db.execute("insert into log_date(entry_date) values(?)",[final_database_date])
        db.commit()
    cursor=db.execute("select entry_date from log_date")
    results=cursor.fetchall()
    formatted_results=[]
    for i in results:
        d=datetime.strptime(str(i['entry_date']),"%Y%m%d")# actual format of date
        single_date={}
        single_date['total']=total_nutrients(d)
        single_date['entry_date']=datetime.strftime(d,"%B %d,%Y")# special format to convert to
        formatted_results.append(single_date)
    return render_template("home.html",dates=formatted_results)
@app.route("/view/<date>",methods=['POST','GET'])
def view(date):
    f_date = datetime.strptime(date, "%B %d,%Y")
    dated = datetime.strftime(f_date, "%Y%m%d")
    print(dated)
    db = get_db()

    cursor = db.execute('select id,name from food ')
    food_results= cursor.fetchall()

    cur = db.execute("select id,entry_date from log_date where entry_date= '" + dated + "'")
    result = cur.fetchone()
    pretty_result=dict()
    d=datetime.strptime(str(result['entry_date']),"%Y%m%d")
    total_calories={}
    total_calories['fats']=0
    total_calories['carbohydrates'] = 0
    total_calories['protein'] = 0
    total_calories['calories'] = 0

    pretty_result['entry_date']=datetime.strftime(d,"%B %d,%Y")
    if request.method == "POST":
        item = request.form['food-select']
        print(item)
        for x in food_results:
            if x['name'] == item:
                id_of_food = x['id']
        print(result['id'])
        print(id_of_food)
        db.execute("insert into food_date(food_id,log_date_id) values(?,?)", [id_of_food, result['id']])
        db.commit()


    food_ids=db.execute("select food_id from food_date where log_date_id= ' "+str(result['id'])+"' ").fetchall()
    food_items=list()
    print(food_ids)
    for i in range(len(food_ids)):
        print(str(food_ids[i]['food_id']))
        total_calories
        food_items.append(db.execute("select name,protein,carbohydrates,fats,calories from food where id ='" +str(food_ids[i]['food_id'])+"'").fetchone())

    print(food_items)
    for i in food_items:
        total_calories['fats'] += i['fats']
        total_calories['carbohydrates'] += i['carbohydrates']
        total_calories['protein'] += i['protein']
        total_calories['calories'] += i['calories']

    return render_template("day.html",total=total_calories,date=pretty_result['entry_date'],foods=food_results,food_items=food_items)
@app.route("/food",methods=['POST','GET'])
def food():
    db = get_db()
    if request.method=="POST":
        name=request.form['food-name']
        protein=int(request.form['protein'])
        fats=int(request.form['fats'])
        carbohydrates=int(request.form['carbohydrates'])
        calories=protein*4 + carbohydrates*4 +fats*9
        db.execute('insert into food(name,protein,carbohydrates,fats,calories) values(?,?,?,?,?)' ,[name,protein,carbohydrates,fats,calories])
        db.commit()

    cur=db.execute("select name,protein,carbohydrates,fats,calories from food")
    results=cur.fetchall()
    return render_template("add_food.html",foods=results)


def total_nutrients(date):
    dated=datetime.strftime(date,"%Y%m%d")
    db = get_db()
    print(dated)
    date_id=db.execute("select id from log_date where entry_date =(?)",[dated] ).fetchone()
    print(date_id)
    total_calories = {}
    total_calories['fats'] = 0
    total_calories['carbohydrates'] = 0
    total_calories['protein'] = 0
    total_calories['calories'] = 0
    food_ids = db.execute("select food_id from food_date where log_date_id= ' " + str(date_id['id']) + "' ").fetchall()
    food_items = list()
    print(food_ids)
    for i in range(len(food_ids)):
        print(str(food_ids[i]['food_id']))
        total_calories
        food_items.append(db.execute("select name,protein,carbohydrates,fats,calories from food where id ='" + str(
            food_ids[i]['food_id']) + "'").fetchone())

    print(food_items)
    for i in food_items:
        total_calories['fats'] += i['fats']
        total_calories['carbohydrates'] += i['carbohydrates']
        total_calories['protein'] += i['protein']
        total_calories['calories'] += i['calories']
    return total_calories
if __name__=="__main__":
     app.run(debug=True)