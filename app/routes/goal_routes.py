from flask import Blueprint, request, make_response, abort, Response
from ..db import db
from app.models.goal import Goal
from app.models.task import Task

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        response = {"message": "Invalid task ID"}
        abort(make_response(response, 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"message": "Task not found"}
        abort(make_response(response, 404))

    return task


def validate_goal(goal_id):
    try:
        goal_id = int(goal_id)
    except ValueError:
        response = {"message": "Invalid goal ID"}
        abort(make_response(response, 400))

    query = db.select(Goal).where(Goal.id == goal_id)
    goal = db.session.scalar(query)

    if not goal:
        response = {"message": "Goal not found"}
        abort(make_response(response, 404))

    return goal


@goals_bp.post("")
def create_goal():
    """Create a new goal"""
    request_body = request.get_json()

    # Required fields
    if "title" not in request_body:
        return {"details": "Invalid data"}, 400

    try:
        new_goal = Goal.from_dict(request_body)
    except KeyError:
        return {"details": "Invalid data"}, 400

    db.session.add(new_goal)
    db.session.commit()

    return {"goal": new_goal.to_dict()}, 201


@goals_bp.get("")
def get_all_goals():
    """Get all goals"""
    query = db.select(Goal)
    goals = db.session.scalars(query)

    return [goal.to_dict() for goal in goals]


@goals_bp.get("/<goal_id>")
def get_goal(goal_id):
    """Get a specific goal by ID"""
    goal = validate_goal(goal_id)

    return {"goal": goal.to_dict()}


@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    """Update a goal by ID"""
    goal = validate_goal(goal_id)
    request_body = request.get_json()

    if "title" in request_body:
        goal.title = request_body["title"]

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    """Delete a goal by ID"""
    goal = validate_goal(goal_id)

    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@goals_bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    """Get all tasks associated with a specific goal"""
    goal = validate_goal(goal_id)

    response = {
        "id": goal.id,
        "title": goal.title,
        "tasks": [task.to_dict() for task in goal.tasks]
    }

    return response


@goals_bp.post("/<goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    """Associate multiple tasks with a goal"""
    goal = validate_goal(goal_id)
    request_body = request.get_json()

    if "task_ids" not in request_body:
        return {"message": "Missing task_ids field"}, 400

    goal.tasks = []

    # Add each task from the task_ids list
    for task_id in request_body["task_ids"]:
        task = validate_task(task_id)
        goal.tasks.append(task)

    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }