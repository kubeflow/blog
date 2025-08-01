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
    # New component inputs for the dynamic values, now correctly used inside the function
    pipeline_run_id: str,
    pipeline_name: str,
    pipeline_namespace: str,
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
    MODEL_REGISTRY_SERVER_ADDRESS = "http://model-registry-service.kubeflow-user-example-com.svc.cluster.local"
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
                "pipeline_run_id": pipeline_run_id,           # Now using the function argument directly
                "pipeline_name": pipeline_name,               # Now using the function argument directly
                "pipeline_namespace": pipeline_namespace,     # Now using the function argument directly
                "kfp_component_name": "register-model-to-kubeflow-registry"
            },
            # Best practices for cross-referencing model source (from KEP):
            model_source_id=pipeline_run_id,           # Now using the function argument directly
            model_source_name=pipeline_name,           # Now using the function argument directly
            model_source_class="pipelinerun",          # KFP-specific identifier for run
            model_source_kind="kfp",                   # KFP-specific identifier for source system
            model_source_group=pipeline_namespace,     # Now using the function argument directly
        )
        print(f"Registered Model ID: {registered_model_and_version.id}, Name: {registered_model_and_version.name}")

        print(f"Successfully registered model and version in Model Registry.")
        
        # Write content to the output model path
        with open(output_model.path, 'w') as f:
            f.write(f"This is a fake model artifact for {model_name} version {model_version_name}.")
        
        # Set metadata on the KFP output model artifact
        output_model.metadata["registered_model"] = {
            "modelName": registered_model_and_version.name,
            "versionName": model_version_name,
            "modelID": registered_model_and_version.id,
            "versionID": "placeholder-version-id",
            "modelRegistryURL": f"http://localhost:{MODEL_REGISTRY_PORT}/models/{registered_model_and_version.id}/versions/{model_version_name}",
            "modelRegistryAPIEndpoint": MODEL_REGISTRY_SERVER_ADDRESS
        }
        print(f"KFP output model artifact metadata set: {output_model.metadata}")

        return registered_model_and_version.id

    except Exception as e:
        print(f"An error occurred during model registration: {e}")
        raise

@dsl.pipeline(
    name="Model Registration Pipeline",
    description="A KFP pipeline to demonstrate registering a model in Kubeflow Model Registry."
)
def model_registration_pipeline(
    model_name: str = "MyFakeModel",
    model_version_name: str = "v1.0.0-blog-post",
    model_artifact_uri: str = "s3://my-model-bucket/fake/v1.0.0/model.pkl",
    model_author: str = "Kubeflow Community"
):
    # Pass dynamic values as explicit component inputs using KFP placeholders
    register_task = register_model_to_kubeflow_registry(
        model_name=model_name,
        model_version_name=model_version_name,
        model_artifact_uri=model_artifact_uri,
        model_author=model_author,
        # PASSING PLACEHOLDERS AS EXPLICIT ARGUMENTS
        pipeline_run_id=dsl.PIPELINE_JOB_NAME_PLACEHOLDER,
        pipeline_name=dsl.PIPELINE_NAME_PLACEHOLDER,
        pipeline_namespace=dsl.KFP_POD_NAMESPACE_PLACEHOLDER,
        output_model=dsl.Output[dsl.Model](),
    )
    # Mount the Secret containing the token as an environment variable
    kfp.kubernetes.use_secret_as_env(
        task=register_task,
        secret_name="model-registry-auth",
        secret_key_to_env={"token": "MR_AUTH_TOKEN"}
    )
    # This ensures the authentication token is available to the component.

# Compile the pipeline
pipeline_filename = "model_registration_pipeline.yaml"
compiler.Compiler().compile(model_registration_pipeline, pipeline_filename)

print(f"\nPipeline compiled to {pipeline_filename}")
print(f"You can now upload '{pipeline_filename}' to the Kubeflow Pipelines UI.")