from jahan.jahan import Jahan, TemplateResponse, Response
from .models import session_local, Base, engine, Employee

app = Jahan(__name__)

db = session_local()
Base.metadata.create_all(bind=engine)
 
# @app.add_route(r'/$')
# def index(request):
#     print(request)
#     return Response(f'<b>Hello how are you Faishal </b>!')

# Get all the employees
@app.add_route(r'/$')
def get_employees(request):
   context = []
   for class_instance in db.query(Employee).all():
      context.append({"name": vars(class_instance)["name"], 
                      "position": vars(class_instance)["position"],
                      "contact": vars(class_instance)["contact"],
                      "age": vars(class_instance)["age"],
                      "salary": vars(class_instance)["salary"]})
   db.close() 
   return TemplateResponse(template='templates/employees.html', 
                           context={"employees": context}, status=200)


# Add employee in the database
@app.add_route(r'/add/employee/$')
def add_employee(request):
    post_data = request.get_post
    if request.method == 'POST':
          print("I AM CALLED")
          print(post_data)
          _record = Employee(name=post_data["name"], 
                             position=post_data["position"], 
                             contact=post_data["contact"],
                             age=post_data["age"],
                             salary=post_data["salary"])
          db.add(_record)
          db.commit()
          db.close()
          return TemplateResponse(template='templates/add_employee.html', status=200)
    return TemplateResponse(template='templates/add_employee.html', status=200)

application = app.application

if __name__ == "__main__":
    app.run()
