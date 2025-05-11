from flask import Blueprint, request, make_response, abort, Response
from ..db import db
from app.models.task import Task
from datetime import datetime
import requests
import os

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# Slack API
SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', 'task-notifications')

def send_slack_notification(message):
    if not SLACK_API_TOKEN:
        print("Warning: SLACK_API_TOKEN not configured.")
        return False

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": SLACK_CHANNEL,
        "text": message
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("ok"):
            return True
        else:
            print(f"Slack API error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"Error sending Slack notification: {str(e)}")
        return False


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
    sort_param = request.args.get("sort")

    query = db.select(Task)

    # sort by title
    if sort_param == "asc":
        query = query.order_by(Task.title.asc())
    elif sort_param == "desc":
        query = query.order_by(Task.title.desc())

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


@tasks_bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    """Mark a task as complete"""
    task = validate_task(task_id)

    task.completed_at = datetime.now()
    db.session.commit()

    # Send Slack notification when a task is marked complete
    notification_message = f"Someone just completed the task {task.title}"
    send_slack_notification(notification_message)

    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    """Mark a task as incomplete"""
    task = validate_task(task_id)

    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")