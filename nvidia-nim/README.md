# Nvidia NIM Recipe

This recipe deploys Nvidia [NIM](https://docs.nvidia.com/nim/) infrastructure, on Kubernetes, with GPUs. Specifically, we will:

 1. Deploy the NVIDIA [GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator) onto Kubernetes so that pods can request GPUs.
 2. Select and deploy an LLM available on Nvidia NIM.
 3. Connect `spice` to the OpenAI compatible NIM LLM.

## Prerequisites

 1. A Kubernetes cluster, with at least 1 GPU node.
    - Ensure that the GPU has a [compute capability](https://developer.nvidia.com/cuda-gpus) of 8.0 or higher.
 2. Local tools
    - `helm`: [install](https://helm.sh/docs/intro/install/)
    - `kubectl`: [install](https://kubernetes.io/docs/tasks/tools/)
    - `spice`: [install](https://docs.spiceai.org/installation)

## Deploying GPU-operator

 1. Add the Nvidia Helm repository

    ```bash
    helm repo add nvidia https://helm.ngc.nvidia.com/nvidia \
        && helm repo update
    ```

 2. Install the GPU Operator

    ```bash
    helm install --wait --generate-name \
        -n gpu-operator --create-namespace \
        nvidia/gpu-operator
    ```

    - For additional `helm` overrides, see [additional values](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html#common-chart-customization-options
).
    - Once the command completes (because of the `--wait`), Kubernetes pods will be able to ask for GPU requests/limits.

For additional details & troubleshooting, see the [official documentation](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html).

## Configuring NIMs

1. Get a NGC API key from Nvidia's NGC [website](https://org.ngc.nvidia.com/setup/personal-keys).

    ```shell
    export NGC_API_KEY=""
    ```

2. Login to Nvidia's Docker registry

    ```shell
    echo "$NGC_API_KEY" | docker login nvcr.io --username '$oauthtoken' --password-stdin
    ```

3. Login to Nvidia's Helm registry

    ```shell
    helm fetch https://helm.ngc.nvidia.com/nim/charts/nim-llm-1.1.2.tgz --username=\$oauthtoken --password=$NGC_API_KEY
    ```

4. Create a secret to use for pulling images from docker registries.

    ```shell
    kubectl create secret \
    docker-registry ngc-secret \
    --docker-server=nvcr.io \
    --docker-username='$oauthtoken' \
    --docker-password=$NGC_API_KEY
    ```

5. Similar to above, create a secret to pull model weights.

    ```shell
    kubectl create secret generic ngc-api --from-literal=NGC_API_KEY=$NGC_API_KEY
    ```

6. Install the Helm chart.

    ```shell
    helm install my-nim nim-llm-1.1.2.tgz -f values.yaml
    ```

    For available models, use [NGC CLI](https://org.ngc.nvidia.com/setup/installers/cli) and run

    ```shell
    ngc registry image list "nvcr.io/nim/*"
    ```

## Connect Spice

1. Add the helm repository

    ```shell
    helm repo add spiceai https://helm.spiceai.org
    helm repo update
    ```

2. Deploy Spice

    ```shell
    helm install spiceai spiceai/spiceai -f spiceai.yaml
    ```

3. Connect to Spice

    ```shell
    kubectl port-forward deployment/spiceai 8090
    ```

4. Chat with `meta/llama3-8b-instruct` via NIM.

    ```shell
    spice chat
    ```

    ```shell
    Using model: nim
    chat> Tell me a joke about the moon.
    ```
