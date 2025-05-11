from flask import Blueprint, request, make_response, abort, Response
from ..db import db
from app.models.goal import Goal

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


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