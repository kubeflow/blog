from kfp import dsl, compiler
import json
import os
import time
import kfp

# Import available KFP placeholders - some may not exist in all versions
try:
    from kfp.dsl import PIPELINE_JOB_ID_PLACEHOLDER, PIPELINE_JOB_NAME_PLACEHOLDER
    # PIPELINE_JOB_NAMESPACE_PLACEHOLDER may not exist, we'll use a fallback
    PIPELINE_JOB_NAMESPACE_PLACEHOLDER = "{{workflow.namespace}}"
except ImportError:
    # Fallback to string placeholders if DSL constants don't exist
    PIPELINE_JOB_ID_PLACEHOLDER = "{{workflow.uid}}"
    PIPELINE_JOB_NAME_PLACEHOLDER = "{{workflow.name}}"
    PIPELINE_JOB_NAMESPACE_PLACEHOLDER = "{{workflow.namespace}}"

# NOTE: You have successfully installed kfp-kubernetes-1.5.0
# This provides Kubernetes-specific functionality not included in the core KFP SDK

# Define the base image for our pipeline components
BASE_IMAGE = 'python:3.11-slim-buster'

@dsl.component(
    base_image=BASE_IMAGE,
    packages_to_install=['model-registry==0.2.19']
)
def register_model_to_kubeflow_registry(
    model_name: str,
    model_version_name: str,
    model_artifact_uri: dsl.Input[dsl.Model],
    pipeline_run_id: str,
    pipeline_name: str,
    pipeline_namespace: str,
    model_registry_api_url: str = "http://model-registry-service.kubeflow.svc.cluster.local:8080",
    model_registry_name: str = "",
    model_description: str = "A model for demonstration purposes",
    model_author: str = "Data Science Pipelines Team",
    output_model: dsl.Output[dsl.Model] = None
) -> str:
    """
    KFP component to register a model and version in the Kubeflow Model Registry.
    This implementation follows the EXACT pattern from opendatahub-io/ilab-on-ocp
    utils/components.py lines 195-273 for proven reliability and best practices.
    """
    print("model-registry client is being installed by KFP before this script runs.")

    # Import required modules - following opendatahub-io/ilab-on-ocp pattern
    import urllib.parse
    import time
    from model_registry import ModelRegistry
    from model_registry.types import RegisteredModel

   
    model_registry_api_url_parsed = urllib.parse.urlparse(model_registry_api_url)
    model_registry_api_url_port = model_registry_api_url_parsed.port
    if model_registry_api_url_port:
        model_registry_api_server_address = model_registry_api_url.replace(
            model_registry_api_url_parsed.netloc,
            model_registry_api_url_parsed.hostname,
        )
    else:
        if model_registry_api_url_parsed.scheme == "http":
            model_registry_api_url_port = 80
        else:
            model_registry_api_url_port = 443
        model_registry_api_server_address = model_registry_api_url
    if not model_registry_api_url_parsed.scheme:
        model_registry_api_server_address = (
            "https://" + model_registry_api_server_address
        )

    # Retrieve authentication token from environment variable
    token = os.environ.get("MR_AUTH_TOKEN", "")
    if not token:
        print("Warning: MR_AUTH_TOKEN environment variable not found. Proceeding without authentication.")

    print(f"Connecting to Model Registry at {model_registry_api_server_address}:{model_registry_api_url_port}")

   
    tries = 0
    while True:
        try:
            tries += 1
            registry = ModelRegistry(
                server_address=model_registry_api_server_address,
                port=model_registry_api_url_port,
                author=model_author,  
                user_token=token,
            )
            registered_model = registry.register_model(
                name=model_name,
                version=model_version_name,
                uri=model_artifact_uri,
                model_format_name="custom-format",  
                model_format_version="1.0",
            
                model_source_id=pipeline_run_id,      # run_id parameter
                model_source_name=pipeline_name,      # run_name parameter  
                model_source_class="pipelinerun",     # KFP-specific identifier
                model_source_kind="kfp",              # KFP-specific identifier
                model_source_group=pipeline_namespace, # pod_namespace equivalent
            )
            break
        except Exception as e:
            if tries >= 3:
                raise
            print(f"Failed to register the model on attempt {tries}/3: {e}")
            time.sleep(1)
    
    # Get the model version ID to add as metadata on the output model artifact
    tries = 0
    while True:
        try:
            tries += 1
            model_version_id = registry.get_model_version(
                model_name, model_version_name
            ).id
            break
        except Exception as e:
            if tries >= 3:
                raise
            print(f"Failed to get the model version ID on attempt {tries}/3: {e}")
            time.sleep(1)
    
    # If model_registry_name is not provided, parse it from the URL
    if not model_registry_name:
        model_registry_name = urllib.parse.urlparse(
            model_registry_api_url
        ).hostname.split(".")[0]
        if model_registry_name.endswith("-rest"):
            model_registry_name = model_registry_name[: -len("-rest")]

    print(f"Successfully registered model - ID: {registered_model.id}, Name: {registered_model.name}")
    print(f"Model version ID: {model_version_id}")
    
    # Write content to the output model path (simulating a model artifact)
    with open(output_model.path, 'w') as f:
        f.write(f"This is a model artifact for {model_name} version {model_version_name}.")
    
    
    output_model.metadata["registered_model"] = {
        "modelName": model_name,
        "versionName": model_version_name,
        "modelID": registered_model.id,
        "versionID": model_version_id,  # Real version ID from API
        "modelRegistryURL": f"{model_registry_api_server_address}:{model_registry_api_url_port}/models/{registered_model.id}/versions/{model_version_id}",
        "modelRegistryAPIEndpoint": model_registry_api_server_address,
        "modelRegistryName": model_registry_name,
        "registrationTimestamp": time.time(),
        "pipelineSource": {
            "runId": pipeline_run_id,
            "pipelineName": pipeline_name,
            "namespace": pipeline_namespace
        }
    }
    
    print(f"KFP output model artifact metadata set: {output_model.metadata}")
    
    return registered_model.id

@dsl.component(
    base_image=BASE_IMAGE,
    packages_to_install=['scikit-learn==1.3.0', 'pandas==2.0.3']
)
def train_iris_model(
    output_model: dsl.Output[dsl.Model]
) -> str:
    """
    Simple component that trains an Iris classification model.
    This demonstrates a realistic pipeline that produces a model to register.
    """
    import pickle
    import pandas as pd
    from sklearn.datasets import load_iris
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    import json
    
    # Load and prepare the Iris dataset
    iris = load_iris()
    X, y = iris.data, iris.target
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train a simple Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Calculate accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model trained with accuracy: {accuracy:.4f}")
    
    # Save the model
    with open(output_model.path, 'wb') as f:
        pickle.dump(model, f)
    
    # Set model metadata
    output_model.metadata = {
        "accuracy": accuracy,
        "model_type": "RandomForestClassifier",
        "n_estimators": 100,
        "dataset": "iris",
        "features": iris.feature_names,
        "target_classes": iris.target_names.tolist()
    }
    
    return f"s3://my-model-bucket/iris-models/run-{hash(str(accuracy))}/model.pkl"

@dsl.pipeline(
    name="Iris Model Registration Pipeline - Following opendatahub-io/ilab-on-ocp Pattern",
    description="A KFP pipeline that trains an Iris model and registers it in Kubeflow Model Registry using the exact pattern from opendatahub-io/ilab-on-ocp."
)
def iris_model_registration_pipeline(
    model_name: str = "iris-classifier",
    model_version_name: str = "v1.0.0",
    model_author: str = "Data Science Pipelines Team",
    model_registry_api_url: str = "http://model-registry-service.kubeflow.svc.cluster.local:8080"
):
   
    # Step 1: Train the model
    train_task = train_iris_model()
    
    # Step 2: Register the model 
    register_task = register_model_to_kubeflow_registry(
        model_name=model_name,
        model_version_name=model_version_name,
        model_artifact_uri=train_task.outputs["output_model"],  # Reference output by name
        model_author=model_author,
        model_description=f"Random Forest classifier trained on Iris dataset",
        model_registry_api_url=model_registry_api_url,
        # EXACT PATTERN: Use proper KFP placeholders
        pipeline_run_id=PIPELINE_JOB_ID_PLACEHOLDER,        # run_id parameter
        pipeline_name=PIPELINE_JOB_NAME_PLACEHOLDER,        # run_name parameter  
        pipeline_namespace=PIPELINE_JOB_NAMESPACE_PLACEHOLDER,  # namespace context
    )
    
    # Import the kfp-kubernetes extension for secret handling
    from kfp.kubernetes import use_secret_as_env
    
    # Mount the Secret containing the Model Registry auth token
    use_secret_as_env(
        register_task,
        secret_name="model-registry-auth",
        secret_key_to_env={"token": "MR_AUTH_TOKEN"}
    )
    
    # Set task display names for better UI experience
    train_task.set_display_name("Train Iris Model")
    register_task.set_display_name("Register Model in Registry")
    
    # Ensure registration happens after training
    register_task.after(train_task)

# Compile the pipeline
pipeline_filename = "iris_model_registration_pipeline_opendatahub_pattern.yaml"
compiler.Compiler().compile(iris_model_registration_pipeline, pipeline_filename)

print(f"\nPipeline compiled to {pipeline_filename}")
print(f"You can now upload '{pipeline_filename}' to the Kubeflow Pipelines UI.")
print("\n" + "="*80)

