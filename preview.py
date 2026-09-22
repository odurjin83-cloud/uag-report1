"""Local demonstration with isolated synthetic data, never the operational database."""
import os
from pathlib import Path
import sqlite3
from datetime import date,timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from catalog import DEPARTMENTS,FUNCTIONS

ROOT=Path(__file__).resolve().parent
application=create_app({'DATABASE':str(ROOT/'tmp'/'design-demo.db')})
application.config['DEMO']=True
db=sqlite3.connect(application.config['DATABASE'])
if not db.execute('SELECT 1 FROM users').fetchone():
    for email,role,dept in [('demo@uag.mn','admin','Бүх хэлтэс'),('it@uag.mn','user','МТХэлтэс')]:
        db.execute('INSERT INTO users(email,password,role,department) VALUES (?,?,?,?)',(email,generate_password_hash('UagDemo2026!'),role,dept))
    today=date.today(); monday=today-timedelta(days=today.weekday()+7)
    tasks=[['Архивын баримтыг цахим хэлбэрт шилжүүлэх','Компанийн танилцуулгын эх бэлтгэл','Орон нутгийн уулзалтын бэлтгэл'],['Гэрээний төсөлд эрх зүйн дүгнэлт гаргах','Дотоод журмын шинэчлэл','Гэрээний хэрэгжилтийг хянах'],['Ээлжийн ажилтны тээвэр зохицуулах','Автобусны техникийн үзлэг','Оффисын хангамжийн захиалга'],['Төв оффисын сүлжээний тохиргоо','Төслийн талбайн камерын үйлчилгээ','ERP хэрэглэгчийн хүсэлт шийдвэрлэх'],['Кемпийн засвар үйлчилгээ','Өрөөний бэлэн байдлыг шалгах','Хоол үйлдвэрлэлийн хяналт']]
    for i,dept in enumerate(DEPARTMENTS):
        for j,name in enumerate(tasks[i]):
            day=(monday+timedelta(days=j)).isoformat()
            value=[100,75,50][j] if i%2 else [100,100,50][j]
            db.execute('INSERT INTO reports(department,report_date,report_day,func_area,task_desc,task_result,progress,assignee,status,issue,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',(dept,day,day,FUNCTIONS[dept][min(j,len(FUNCTIONS[dept])-1)],name,'Туршилтын өгөгдөл. Ажлын үр дүнгийн тэмдэглэл.',str(value)+'%','Туршилтын ажилтан','approved' if j<2 else 'submitted','Холбогдох төлөвлөгөөг батлуулах шаардлагатай.' if i in (0,3) and j==2 else '',day))
    db.commit()
db.close()
@application.context_processor
def demo_context():return {'demo':True}
if __name__=='__main__':application.run(host='127.0.0.1',port=5012,debug=False)
