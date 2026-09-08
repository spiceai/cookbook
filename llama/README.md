# Running Llama3 Locally

Works with `v1.0+`

Use the Llama family of models locally from HuggingFace using Spice.

[![Watch the Spice.ai local Llama demo](https://img.youtube.com/vi/ZlV3NX-bsIg/hqdefault.jpg)](https://www.youtube.com/embed/ZlV3NX-bsIg?si=yG2y6Q0Br_fDnQ1l)

## Requirements

- [Spice CLI](https://docs.spiceai.org/getting-started) installed.
- The following environment variables set or configured in `.env`:
  - `SPICE_HUGGINGFACE_API_KEY`
  - Granted access to the [Llama-3.2-3B-Instruct model](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct) on HuggingFace.

For more information, see the [Spice HuggingFace documentation](https://docs.spiceai.org/components/models/huggingface).

## Steps

1. **Initialize a new spicepod:**

   ```shell
   spice init llama-spicepod
   cd llama-spicepod
   ```

2. **Configure the spicepod with the Llama model:**

   Edit the `spicepod.yaml` file to include the Llama model configuration:

   ```yaml
   models:
     - name: llama3
       from: huggingface:huggingface.co/meta-llama/Llama-3.2-3B-Instruct
       params:
         huggingface_token: ${ secrets:SPICE_HUGGINGFACE_API_KEY }
   ```

   An example `spicepod.yml` is also provided in the recipe directory (both
   `spicepod.yaml` and `spicepod.yml` are loaded).

3. **Update `.env` with the HuggingFace variable:**

   Create or update the `.env` file with your HuggingFace API key:

   ```sh
   echo "SPICE_HUGGINGFACE_API_KEY=your_huggingface_api_key" >> .env
   ```

4. **Run the spicepod:**

   ```sh
   spice run
   ```

   The model will download and load. It will be cached at `~/.cache/huggingface` for subsequent use.

5. **Use Spice Chat to interact with the model:**

   You can now start interacting with the Llama model through the Spice Chat interface.

   In a new terminal window run:

   ```sh
   spice chat
   ```

   Enter a question. It will use the locally running Llama model.

   ```sh
   Using model: llama3
   chat> Roughly how much memory do I need to run llama 3.2-3B-instruct locally as GBs?
   Llama 3 is a large transformer model, and its memory requirements can be significant. According to the Hugging Face documentation, the inference memory required for Llama 3-3B can vary depending on the specific use case and settings.

   However, here are some rough estimates:

   - In-app memory usage for Llama 3-3B models is typically in the range of 6-12 GB of memory per instance for inference.
   - For batched inference, Llama-3B-6B (which is the 6GB variant) is suggested to have around 12 GB per run, either in picoraw bytes (GB is the correct unit for your request).
   ```

   You can also interact with the llama model by sending a one-shot chat request through `spice chat <message>`

   ```sh
   spice chat "Roughly how much memory do I need to run llama 3.2-3B-instruct locally as GBs?"
   Using model: llama3
   The amount of memory required to run Llama 3 on a local machine can vary greatly depending on several factors, such as the size of the input dataset, the computational resources, and the specific implementation.

   However, as a rough estimate, the Llama 3 model has a small footprint of around 350 MB to 400 MB in its `model` directory after being installed, plus additional GBs of memory used for in-processing inputs, caching results, and outputting results.

   Assuming an average size of 600 MB, 1 GB, of overall memory usage you could expect be sufficient for mostly small to moderate-sized local training and inference tasks.

   Time: 16.09s (first token 0.53s). Tokens: 197. Prompt: 64. Completion: 133 (8.55/s).
   ```

## Hardware Acceleration

`spice install` (and `curl https://install.spiceai.org | /bin/bash`) auto-detects the
local hardware accelerator and installs the matching runtime build — Metal on Apple
silicon, CUDA on Linux when a supported GPU is present — so no extra step is needed.
Confirm which build is installed with:

```sh
spice version
```

```sh
CLI version:     v2.2.1
Runtime version: v2.2.1+models.metal
```

A `+models.metal` or `+models.cuda_<cc>` suffix on the runtime version means the
accelerated build is in use. To install a CUDA build explicitly on Linux:

```sh
spice install cuda
```

Building from source is only necessary to run an unreleased revision; see
[Building Spice](https://github.com/spiceai/spiceai/blob/trunk/CONTRIBUTING.md#building).
