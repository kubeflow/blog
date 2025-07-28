from kfp import dsl, compiler
import json
import os # Import os for environment variables
import time # Import time for sleep

# Define the base image for our pipeline components.
# This image needs Python and pip, and we'll install model-registry inside the component.
BASE_IMAGE = 'python:3.11-slim-buster'

@dsl.component(
    base_image=BASE_IMAGE,
    packages_to_install=['model-registry==0.2.19'] # KFP handles this installation
)
def register_model_to_kubeflow_registry(
    model_name: str,
    model_version_name: str, # This will be used as the 'version' in register_model
    model_artifact_uri: str,
    model_description: str = "A model for demonstration purposes",
    model_author: str = "Data Science Pipelines Team",
    # These parameters are included in the component signature for completeness,
    # but their values are not directly used in this simplified registration logic.
    model_data_type: str = "tabular",
    model_storage_format: str = "pickle",
    model_container_image: str = "my-fake-model-server:latest",
    model_serving_path: str = "/mnt/models/fake_model.pkl",
    model_serving_input_schema: str = '{"type": "object", "properties": {"feature1": {"type": "number"}}}',
    model_serving_output_schema: str = '{"type": "object", "properties": {"prediction": {"type": "number"}}}',
    # New output parameter for the KFP Model artifact
    output_model: dsl.Output[dsl.Model] = None # Will be populated by KFP
) -> str: # Component returns the registered model ID
    """
    KFP component to register a model and version in the Kubeflow Model Registry.
    It demonstrates best practices for model source metadata.
    """
    print("model-registry client is being installed by KFP before this script runs.")

    # Import ModelRegistry client within the component function, as it's installed by KFP
    from model_registry import ModelRegistry
    from model_registry.types import RegisteredModel

    # Model Registry service address within the Kubernetes cluster
    # This uses the internal Kubernetes DNS name.
    MODEL_REGISTRY_SERVER_ADDRESS = "http://model-registry-service.kubeflow.svc.cluster.local"
    MODEL_REGISTRY_PORT = 8080

    # Retrieve authentication token from environment variable (mounted from Kubernetes Secret)
    # In a real scenario, 'MR_AUTH_TOKEN' would be the key in your Secret.
    auth_token = os.environ.get("MR_AUTH_TOKEN", "")
    if not auth_token:
        print("Warning: MR_AUTH_TOKEN environment variable not found. Proceeding without authentication.")

    print(f"Connecting to Model Registry at {MODEL_REGISTRY_SERVER_ADDRESS}:{MODEL_REGISTRY_PORT}")
    registry = ModelRegistry(
        server_address=MODEL_REGISTRY_SERVER_ADDRESS,
        port=MODEL_REGISTRY_PORT,
        author=model_author,
        is_secure=False, # Use False for internal cluster HTTP communication
        user_token=auth_token # Pass the token if available
    )

    try:
        # Best practices for model_source metadata:
        # Use KFP's built-in environment variables for run details.
        # These are injected by the KFP system into the pod.
        pipeline_run_id = os.environ.get("KFP_RUN_ID", "unknown")
        pipeline_name = os.environ.get("KFP_PIPELINE_NAME", "unknown")
        pipeline_namespace = os.environ.get("KFP_POD_NAMESPACE", "unknown")

        # Register the Model and its Version in a single call.
        # The 'version' argument in register_model creates/updates the ModelVersion.
        print(f"Registering model: {model_name} version: {model_version_name} with URI: {model_artifact_uri}")
        registered_model_and_version = registry.register_model(
            name=model_name,
            uri=model_artifact_uri,
            description=model_description,
            model_format_name="custom-format", # Example: "tensorflow", "pytorch", "onnx", "scikit-learn"
            model_format_version="1.0",        # Version of the model format itself
            version=model_version_name,        # The specific model version string (e.g., "v1.0.0")
            owner="Kubeflow Pipelines",        # Owner of the model (e.g., team name)
            author=model_author,               # Author of this specific model version
            metadata={                         # Custom metadata about the model/training
                "training_epochs": 100,
                "accuracy": 0.95,
                "pipeline_run_id": pipeline_run_id,
                "pipeline_name": pipeline_name,
                "pipeline_namespace": pipeline_namespace,
                "kfp_component_name": "register-model-to-kubeflow-registry"
            },
            # Best practices for cross-referencing model source (from KEP):
            model_source_id=pipeline_run_id,           # ID of the KFP pipeline run
            model_source_name=pipeline_name,           # Name of the KFP pipeline
            model_source_class="pipelinerun",          # KFP-specific identifier for run
            model_source_kind="kfp",                   # KFP-specific identifier for source system
            model_source_group=pipeline_namespace,     # Namespace where the pipeline ran
        )
        print(f"Registered Model ID: {registered_model_and_version.id}, Name: {registered_model_and_version.name}")
        # The object returned might be a RegisteredModel or ModelVersion depending on client version.
        # Assuming it's RegisteredModel, we can infer the version was created.

        print(f"Successfully registered model and version in Model Registry.")
        
        # --- NEW: Set metadata on the KFP output model artifact ---
        # Write some dummy content to the output model path
        with open(output_model.path, 'w') as f:
            f.write(f"This is a fake model artifact for {model_name} version {model_version_name}.")
        
        # Set metadata on the KFP output model artifact
        output_model.metadata["registered_model"] = {
            "modelName": registered_model_and_version.name,
            "versionName": model_version_name, # Use the version name passed to component
            "modelID": registered_model_and_version.id,
            # In a real scenario, you'd get the actual modelVersionId from the API response
            # For now, we'll use a placeholder or query it if needed.
            "versionID": "placeholder-version-id", # Model Registry client doesn't return version ID directly from register_model
            "modelRegistryURL": f"http://localhost:{MODEL_REGISTRY_PORT}/models/{registered_model_and_version.id}/versions/{model_version_name}",
            "modelRegistryAPIEndpoint": MODEL_REGISTRY_SERVER_ADDRESS
        }
        print(f"KFP output model artifact metadata set: {output_model.metadata}")

        # Return the registered model ID as a string output
        return registered_model_and_version.id

    except Exception as e:
        print(f"An error occurred during model registration: {e}")
        raise # Re-raise the exception to mark the task as failed

@dsl.pipeline(
    name="Model Registration Pipeline",
    description="A KFP pipeline to demonstrate registering a model in Kubeflow Model Registry."
)
def model_registration_pipeline(
    model_name: str = "MyFakeModel",
    model_version_name: str = "v1.0.0-blog-post", # Unique version for blog post example
    model_artifact_uri: str = "s3://my-model-bucket/fake/v1.0.0/model.pkl",
    model_author: str = "Kubeflow Community"
):
    # Pass the Secret as an environment variable to the component
    register_task = register_model_to_kubeflow_registry(
        model_name=model_name,
        model_version_name=model_version_name,
        model_artifact_uri=model_artifact_uri,
        model_author=model_author,
        output_model=dsl.Output[dsl.Model](), # Pass a KFP Output Model artifact
    )
    # Mount the Secret containing the token as an environment variable
    # 'MR_AUTH_TOKEN' is the environment variable name inside the container
    # 'model-registry-auth' is the name of the Kubernetes Secret
    # 'token' is the key within the Secret that holds the token value
    kfp.kubernetes.use_secret_as_env(
        task=register_task,
        secret_name="model-registry-auth",
        secret_key_to_env={"token": "MR_AUTH_TOKEN"}
    )

    # The KEP proposes a much more automatic way where the KFP Launcher handles credentials.
    # For now, manually passing via env var from secret is the direct method.

    # No return statement here for the pipeline itself

# Compile the pipeline
pipeline_filename = "model_registration_pipeline.yaml"
compiler.Compiler().compile(model_registration_pipeline, pipeline_filename)

print(f"\nPipeline compiled to {pipeline_filename}")
print(f"You can now upload '{pipeline_filename}' to the Kubeflow Pipelines UI.")

# Example of how you might run this locally (commented out)
# from kfp.client import Client
# client = Client(host='http://localhost:8888')
# run = client.create_run_from_pipeline_package(
#     'model_registration_pipeline.yaml',
#     arguments={
#         'model_name': 'MyFakeModel',
#         'model_version_name': 'v1.0.0-blog-post',
#         'model_artifact_uri': 's3://my-model-bucket/fake/v1.0.0/model.pkl',
#         'model_author': 'Kubeflow Community'
#     },
#     experiment_name='Model Registry Blog Post Demo'
# )
# print(f"Run details: {run.url}")

