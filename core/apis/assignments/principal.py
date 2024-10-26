from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from core.models.teachers import Teacher
from core.libs.exceptions import FyleError

from .schema import AssignmentSchema, AssignmentGradeSchema, TeacherSchema
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    principal_assignments = Assignment.get_assignments_by_principal()
    principal_assignments_dump = AssignmentSchema().dump(principal_assignments, many=True)
    return APIResponse.respond(data=principal_assignments_dump)


@principal_assignments_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def get_all_teachers(p):
    """Get all teachers"""
    all_teachers = Teacher.get_all_teachers()
    teacher_schema = TeacherSchema(many=True)  # Specify 'many=True' for a list of objects
    all_teachers_dump = teacher_schema.dump(all_teachers)  # Serialize the list of Teacher objects
    return APIResponse.respond(data=all_teachers_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade or re-grade an assignment"""

    # Parse and validate the JSON payload using AssignmentGradeSchema
    grade_data = AssignmentGradeSchema().load(incoming_payload)
    
    # Retrieve the assignment ID and new grade from the payload
    assignment_id = grade_data.id
    new_grade = grade_data.grade

    # Get the assignment by ID
    assignment = Assignment.get_by_id(assignment_id)

    # Check if the assignment is in draft state
    if assignment is None:
        raise FyleError(message='No assignment found with this ID.', status_code=404)
    
    if assignment.state.value == "DRAFT":
        raise FyleError(message='Only submitted or graded assignments can be graded.', status_code=400)

    # Mark the assignment with the new grade
    updated_assignment = Assignment.mark_grade(assignment_id, new_grade, auth_principal=p)

    # Serialize the updated assignment using AssignmentSchema
    updated_assignment_data = AssignmentSchema().dump(updated_assignment)
    
    return APIResponse.respond(data=updated_assignment_data)
