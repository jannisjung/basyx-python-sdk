import json
import time
import uuid
from threading import Lock

from flask import Flask, Response, request
from werkzeug.serving import make_server
from threading import Thread

from basyx.aas import adapter, model

app = Flask(__name__)

# Store for operation results (handle_id -> result)
operation_results = {}
operation_results_lock = Lock()

def deserialize_basyx_object(basyx_json_str: str) -> object | list[object]:
    return json.loads(basyx_json_str, cls=adapter.json.AASFromJsonDecoder)

def serialize_basyx_object(basyx_obj: object) -> str:
   return json.dumps(basyx_obj, cls=adapter.json.AASToJsonEncoder)

def output_variablify(*basyx_objects: object) -> list:
    return [
        {"value": basyx_object} for basyx_object in basyx_objects
    ]

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def test_operation(path):
    """
    This endpoint responds with the received inputArguments as output arguments, if structured properly as input arguments.
    For async operations, it stores the result and returns a handle_id.
    """
    payload = request.get_json()
    input_args = [item['value'] for item in payload if 'value' in item]
    basyx_input_args = deserialize_basyx_object(json.dumps(input_args))

    output_args = [
        model.Property(
            id_short=arg.id_short if isinstance(arg, model.Property) else "default_output_id_short",
            value_type=model.datatypes.String,
            value=arg.value
            )
            for arg in basyx_input_args
    ]

    return Response(serialize_basyx_object(output_variablify(*output_args)), status=200, mimetype='application/json')

@app.route('/operation', methods=['GET'])
def get_operation_result():
    """
    GET endpoint to retrieve operation results by handleId.
    
    Query parameters:
    - handleId: The handle ID of the operation result to retrieve
    
    Returns:
    - 200: Result is available
    - 202: Result is not ready yet
    - 400: Missing handleId parameter
    - 404: Result not found
    """
    handle_id = request.args.get('handleId')
    
    if not handle_id:
        return Response(json.dumps({"error": "Missing handleId parameter"}), status=400, mimetype='application/json')
    
    with operation_results_lock:
        if handle_id in operation_results:
            result_data = operation_results[handle_id]
            
            # Check if result is ready
            if result_data.get("ready", False):
                # Return the result
                return Response(
                    result_data["result"],
                    status=200,
                    mimetype='application/json'
                )
            else:
                # Result not ready yet
                return Response(json.dumps({"state": "Running"}), status=202, mimetype='application/json')
        else:
            return Response(json.dumps({"error": "Result not found"}), status=404, mimetype='application/json')

@app.route('/invoke-async', methods=['POST'])
def invoke_operation_async():
    """
    POST endpoint to invoke an operation asynchronously.
    Stores the request and returns a handle_id immediately.
    The actual result computation is simulated with a delay.
    """
    payload = request.get_json()
    
    # Generate a unique handle_id
    handle_id = str(uuid.uuid4())
    
    # Parse input arguments
    input_args = [item['value'] for item in payload if 'value' in item]
    basyx_input_args = deserialize_basyx_object(json.dumps(input_args))
    
    # Create output args (same as input for this test)
    output_args = [
        model.Property(
            id_short=arg.id_short if isinstance(arg, model.Property) else "default_output_id_short",
            value_type=model.datatypes.String,
            value=arg.value
            )
            for arg in basyx_input_args
    ]
    
    # Store the result with a "not ready" flag initially
    result_json = serialize_basyx_object(output_variablify(*output_args))
    
    with operation_results_lock:
        operation_results[handle_id] = {
            "ready": False,
            "result": None,  # Will be set after delay
            "result_json": result_json  # Pre-computed result
        }
    
    # Start a background thread to simulate async processing
    def process_operation():
        time.sleep(2)  # Simulate processing time
        with operation_results_lock:
            if handle_id in operation_results:
                operation_results[handle_id]["ready"] = True
                operation_results[handle_id]["result"] = operation_results[handle_id]["result_json"]
    
    Thread(target=process_operation, daemon=True).start()
    
    # Return handle_id immediately
    return Response(json.dumps({"handleId": handle_id}), status=202, mimetype='application/json')


class ServerThread(Thread):
    def __init__(self, app=app):
        Thread.__init__(self)
        self.server = make_server("0.0.0.0", 5001, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print("starting op_server....")
        self.server.serve_forever()

    def shutdown(self):
        print("Stopping op_server...")
        self.server.shutdown()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
