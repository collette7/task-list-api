from flask import Blueprint, request, make_response, abort, Response
from ..db import db
from app.models.task import Task

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")


def validate_task(task_id):
    """
    Validates that a task with the given ID exists.
    Returns the task if it exists, otherwise aborts with 404.
    """
    try:
        task_id = int(task_id)
    except ValueError:
        response = {"error": "Invalid task ID"}
        abort(make_response(response, 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"error": "Task not found"}
        abort(make_response(response, 404))

    return task


@tasks_bp.post("")
def create_task():
    """Create a new task"""
    request_body = request.get_json()
    
    # Validate required fields
    if "title" not in request_body or "description" not in request_body:
        return {"details": "Invalid data"}, 400
    
    try:
        new_task = Task.from_dict(request_body)
    except KeyError:
        return {"details": "Invalid data"}, 400

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201


@tasks_bp.get("")
def get_all_tasks():
    """Get all tasks"""
    query = db.select(Task)
    tasks = db.session.scalars(query)
    
    return [task.to_dict() for task in tasks]


@tasks_bp.get("/<task_id>")
def get_task(task_id):
    """Get a specific task by ID"""
    task = validate_task(task_id)
    
    return {"task": task.to_dict()}


@tasks_bp.put("/<task_id>")
def update_task(task_id):
    """Update a task by ID"""
    task = validate_task(task_id)
    request_body = request.get_json()
    
    if "title" in request_body:
        task.title = request_body["title"]
    if "description" in request_body:
        task.description = request_body["description"]
    
    db.session.commit()
    
    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    """Delete a task by ID"""
    task = validate_task(task_id)
    
    db.session.delete(task)
    db.session.commit()
    
    return Response(status=204, mimetype="application/json")