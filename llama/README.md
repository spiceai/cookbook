# Running Llama3 Locally

Use the Llama family of models locally from HuggingFace using Spice.

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

   Edit the `spicepod.yml` file to include the Llama model configuration:

   ```yaml
   models:
     - name: llama3
       from: huggingface:huggingface.co/meta-llama/Llama-3.2-3B-Instruct
       params:
         hf_token: ${ secrets:SPICE_HUGGINGFACE_API_KEY }
   ```

   An example `spicepod.yml` is also provided in the recipe directory.

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

## Optional: Enable Hardware Acceleration

If you have the required hardware (NVIDIA GPU or Apple M-series processor), you can build and run Spice with hardware acceleration.

See [Building Spice](https://github.com/spiceai/spiceai/blob/trunk/CONTRIBUTING.md#building) for general instructions to build Spice from source.

### For NVIDIA GPU (CUDA)

1. **Install CUDA Toolkit:**

Follow the [CUDA Toolkit installation guide](https://developer.nvidia.com/cuda-downloads) to install the appropriate version for your system.

2. **Build Spice with CUDA support:**

```sh
git clone git@github.com:spiceai/spiceai.git
cd spiceai
make install-with-models-cuda
```

### For Apple M-series (Metal)

1. **Ensure you have the latest macOS updates:**

   Make sure your macOS is up to date to leverage the latest Metal support.

2. **Build Spice with Metal support:**

```sh
git clone git@github.com:spiceai/spiceai.git
cd spiceai
make install-with-models-metal
```
