import uuid
import json  
from datetime import datetime
from flask import Flask, request


r = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)

@app.route('/')
def healthCheck():
    return true

@app.route('/entry')
def enter():
    plate = request.args.get('plate')
    parkingLot = request.args.get('parkingLot')
    id = str(uuid.uuid4())
    ticket = {"id": id, 
              "plate": plate, 
              "parkingLot": parkingLot, 
              "entry": datetime.now().isoformat() }
    r.set(id, json.dumps(ticket))
    return id, 201


@app.route('/exit')
def exit():
    id = request.args.get("ticketId")
    ticket_str = r.get(id)
    if ticket_str is None:
        return "No such ticket", 404

    ticket = json.loads(ticket_str)

    if "exit" in ticket:
        return ticket_str, 406

    entry_time = datetime.fromisoformat(ticket["entry"])
    exit = datetime.now()
    diff_in_minutes = int((exit - entry_time).total_seconds() / 60)
    charges = diff_in_minutes / 15
    if diff_in_minutes % 15 != 0:
        charges += 1
    
    ticket["exit"] = exit.isoformat()
    ticket["chargs"] = charges
    ticket["total_cost"] = charges * 2.5

    r.set(id, json.dumps(ticket))

    return ticket

