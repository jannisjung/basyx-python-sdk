import json
import logging
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import SkipTest

import requests
from basyx.aas import adapter, model

from basyx_client.operation_handle import OperationHandle
from basyx_client.submodel import SubmodelClient
from basyx_client.utils import to_base64_urlencoded

from _operation_server import ServerThread

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


class TestSubmodelClientIntegration(unittest.TestCase):
    """This test class assumes that there is a running BaSyx server at localhost:8081. (since we are testing in a docker container, we are using the containername the basyx environment)

    Tests for SubmodelClient operation invocation methods (invoke_operation, invoke_operation_async, get_operation_result).
    """
    TEST_IDS = {
        "test_id1": "test_id:9f3c2a8e-7b41-4d6f-a2c9-5e8b1f3d7a6c",
        "test_id2": "test_id:c7e4b2d9-3a6f-4f81-b5d2-8c1a9e7f4b63",
    }

    SUBMODEL_TEST_IDS = {
        "submodel_id1": "test_id:9f3c2a8e-7b41-4d6f-a2c9-5e8b1f3d7a6d",
        "submodel_id2": "test_id:c7e4b2d9-3a6f-4f81-b5d2-8c1a9e7f4b64",
    }

    def setUp(self):
        self.base_url = "http://aas-env:8081"

        # Check if basyx server is available
        try:
            response = requests.get(f"{self.base_url}/shells", timeout=3)
            if response.status_code != 200:
                raise SkipTest(f"BaSyx server not available at {self.base_url} (status: {response.status_code})")
        except requests.RequestException as e:
            raise SkipTest(f"BaSyx server not available at {self.base_url} (error: {e})") from e

        self.client = SubmodelClient(self.base_url)
        self.default_submodel = self._create_submodel()

        # Start a simple HTTP server for operation delegation testing
        self.operation_endpoint = "http://aas-env:5001/TestOperation"

    def tearDown(self):
        try:
            self._wipe_repo()
        except Exception as e:
            logger.warning(f"Error during repo cleanup: {e}")
        finally:
            # Stop the operation server
            if hasattr(self, 'op_server'):
                self.op_server.shutdown()

    def _create_submodel(self, submodel_id=None) -> model.Submodel:
        """Create a basic submodel for testing."""
        if submodel_id is None:
            submodel_id = self.SUBMODEL_TEST_IDS["submodel_id1"]
        return model.Submodel(
            id_=submodel_id,
            id_short="TEST_SUBMODEL"
        )

    def _create_operation_submodel(self, submodel_id, operation_endpoint: str | None = None) -> model.Submodel:
        """Create a submodel with an operation element for testing operation invocation.

        The operation has:
        - idShort: "TestOperation"
        - One input variable: "inputValue" (String)
        - One output variable: "outputValue" (String)
        - One inoutput variable: "inoutputValue" (String)

        :param submodel_id: The ID for the submodel
        :param operation_endpoint: Optional HTTP endpoint URL for operation delegation.
                                   If provided, a qualifier with type 'operationDelegation' is added.
        """

        # Create operation with the variables
        # Note: Operation uses input_variable, output_variable, in_output_variable (singular, not plural)
        operation_kwargs = {
            "id_short": "TestOperation",
            "input_variable": [],
            "output_variable": [],
            "in_output_variable": [],
            "semantic_id": model.ExternalReference((model.Key(type_=model.KeyTypes.GLOBAL_REFERENCE,
                                                              value='http://acplt.org/Operations/TestOperation'),))
        }

        # Add invocationDelegation qualifier if endpoint is provided
        if operation_endpoint:
            operation_kwargs["qualifier"] = [
                model.Qualifier(
                    type_='invocationDelegation',
                    value_type=model.datatypes.String,
                    value=operation_endpoint
                )
            ]

        operation = model.Operation(**operation_kwargs)

        # Create submodel with the operation
        return model.Submodel(
            id_=submodel_id,
            id_short="TEST_SUBMODEL_WITH_OPERATION",
            submodel_element=[operation]
        )

    def _wipe_repo(self):
        """Delete all test submodels from the repository."""
        logger.info("Wiping test submodels...")

        # Delete test submodels using predefined IDs
        try:
            for submodel_id in self.SUBMODEL_TEST_IDS.values():
                try:
                    encoded_id = to_base64_urlencoded(submodel_id)
                    endpoint = f"{self.base_url}/submodels/{encoded_id}"
                    response = requests.delete(endpoint, timeout=3)
                    if response.status_code == 204:
                        logger.info(f'Deleted test submodel: "{submodel_id}"')
                except requests.RequestException as e:
                    logger.warning(f"Failed to delete test submodel {submodel_id}: {e}")
        except Exception as e:
            logger.warning(f"Error during test submodel cleanup: {e}")

    def test_invoke_operation_sync(self):
        """Test synchronous operation invocation with operationDelegation."""
        # start operation server
        self.op_server = ServerThread()
        self.op_server.start()
        time.sleep(2)

        test_id_shorts = ["inputValue", "inputValue2"]

        test_submodel = self._create_operation_submodel(self.SUBMODEL_TEST_IDS["submodel_id2"], "http://basyx-client:5001/TestOperation")
        self.assertTrue(self.client.create_submodel(test_submodel))

        input_variable = model.Property(
            id_short=test_id_shorts[0],
            value_type=model.datatypes.String,
            value="input success",
        )

        input_variable2 = model.Property(
            id_short=test_id_shorts[1],
            value_type=model.datatypes.String,
            value="input success2",
        )

        result = self.client.invoke_operation(test_submodel, "TestOperation", [input_variable, input_variable2])
        self.assertIn("outputArguments", result)


        output_arguments = result["outputArguments"]
        self.assertTrue(len(output_arguments) == 2)

        for argument in output_arguments:
            self.assertIn(argument.id_short, test_id_shorts)


    def test_invoke_operation_async(self):
        """Test asynchronous operation invocation with operationDelegation.

        FIXME: This test is currently skipped because the async operation invocation
        mechanism requires further investigation. The Eclipse BaSyx server's expected
        endpoint structure and response format for async operations needs to be clarified.

        TODO: Implement proper async operation invocation test once the endpoint
        structure is understood. The current implementation assumes:
        - POST to /invoke-async endpoint
        - GET /operation?handleId=<handle_id> for result retrieval

        The test should verify:
        1. invoke_operation_async() returns an OperationHandle
        2. get_operation_result() can retrieve results using the handle
        3. Proper handling of async operation states (pending, completed, failed)
        """
        raise SkipTest("Async operation invocation mechanism needs further investigation")

#         # Start operation server
#         self.op_server = ServerThread()
#         self.op_server.start()
#         time.sleep(2)
# 
#         test_submodel = self._create_operation_submodel(self.SUBMODEL_TEST_IDS["submodel_id2"], "http://basyx-client:5001/TestOperation")
#         self.assertTrue(self.client.create_submodel(test_submodel))
# 
#         input_variable = model.Property(
#             id_short="inputValue",
#             value_type=model.datatypes.String,
#             value="async input success",
#         )
# 
#         # Test async invocation - should return OperationHandle
#         handle = self.client.invoke_operation_async(test_submodel, "TestOperation", [input_variable])
#         self.assertIsNotNone(handle)
#         self.assertIsInstance(handle, OperationHandle)
#         self.assertIsNotNone(handle.handle_id)
# 
#         # Wait for operation to complete (simulated delay is 2 seconds)
#         time.sleep(3)
# 
#         # Get the result using the handle
#         result = self.client.get_operation_result(test_submodel, "TestOperation", handle)
#         self.assertIsNotNone(result)
#         self.assertIn("outputArguments", result)
#         self.assertIn("inoutputArguments", result)

    def test_invoke_operation_with_inoutput(self):
        """Test operation invocation with inoutput arguments and operationDelegation."""
        # Start operation server
        self.op_server = ServerThread()
        self.op_server.start()
        time.sleep(2)

        test_submodel = self._create_operation_submodel(self.SUBMODEL_TEST_IDS["submodel_id2"], "http://basyx-client:5001/TestOperation")
        self.assertTrue(self.client.create_submodel(test_submodel))

        inoutput_variable = model.Property(
            id_short="inoutputValue",
            value_type=model.datatypes.String,
            value="inoutput test",
        )

        # Test invocation with inoutput arguments
        result = self.client.invoke_operation(test_submodel, "TestOperation", inoutput_arguments=[inoutput_variable])
        self.assertIsNotNone(result)
        self.assertIn("outputArguments", result)
        self.assertIn("inoutputArguments", result)

    def test_invoke_operation_no_arguments(self):
        """Test operation invocation without any arguments and operationDelegation."""
        # Start operation server
        self.op_server = ServerThread()
        self.op_server.start()
        time.sleep(2)

        test_submodel = self._create_operation_submodel(self.SUBMODEL_TEST_IDS["submodel_id2"], "http://basyx-client:5001/TestOperation")
        self.assertTrue(self.client.create_submodel(test_submodel))

        # Test invocation without arguments
        result = self.client.invoke_operation(test_submodel, "TestOperation")
        self.assertIsNotNone(result)
        self.assertIn("outputArguments", result)
        self.assertIn("inoutputArguments", result)


if __name__ == "__main__":
    unittest.main()
