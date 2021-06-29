import uuid
import json  
from flask import Flask, request

memory = {}

app = Flask(__name__)

@app.route('/healthCheck')
def healthCheck():
    return "healthy", 201

@app.route('/put')
def put():
    str_key = request.args.get('str_key')
    data = request.args.get('data')
    expiration_date = request.args.get('expiration_date')
    memory["str_key"] = {
        "data": data,
        "expiration_date": expiration_date
    }
    return "YAY", 201


# @app.route('/exit')
# def exit():
#     id = request.args.get("ticketId")
#     ticket_str = r.get(id)
#     if ticket_str is None:
#         return "No such ticket", 404

#     ticket = json.loads(ticket_str)

#     if "exit" in ticket:
#         return ticket_str, 406

#     entry_time = datetime.fromisoformat(ticket["entry"])
#     exit = datetime.now()
#     diff_in_minutes = int((exit - entry_time).total_seconds() / 60)
#     charges = diff_in_minutes / 15
#     if diff_in_minutes % 15 != 0:
#         charges += 1
    
#     ticket["exit"] = exit.isoformat()
#     ticket["chargs"] = charges
#     ticket["total_cost"] = charges * 2.5

#     r.set(id, json.dumps(ticket))

#     return ticket

