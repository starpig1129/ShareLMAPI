# ShareLMAPI
English | [中文](README_CN.md)

ShareLMAPI is a local language model sharing API that uses FastAPI to provide interfaces, allowing different programs to share the same local model, reducing resource consumption. It supports streaming generation and various model configuration methods.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Client Usage](#client-usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

- Support for multiple model loading methods: default, BitsAndBytes quantization, PEFT
- Support for streaming and non-streaming text generation
- Support for dialogue history and system prompts
- Easy to configure and extend
- Flexible model server URL configuration

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ShareLMAPI.git
cd ShareLMAPI
```

### 2. Install dependencies

Dependencies can be installed using Conda or Pip.

Using Conda:

```bash
conda env create -f environment.yml
conda activate ShareLMAPI
```

Using Pip:

```bash
pip install -r requirements.txt
```

### 3. Install for local development

If you plan to develop this package, use the following command to install it:

```bash
pip install -e .
```

## Configuration

1. Navigate to the `configs` directory and open `model_config.yaml`.
2. Modify the configuration according to your needs. You can specify:
   - Model name
   - Loading method (default, bitsandbytes, or peft)
   - Device (CPU or CUDA)
   - Other model-specific settings
   - Model server URL

Example configuration:

```yaml
model:
  name: "gpt-2"
  loading_method: "default"
  default:
    device: "cuda"
  bitsandbytes:
    device: "cuda"
    quantization_config:
      quant_type: "nf4"
      load_in_4bit: True
      bnb_4bit_quant_type: "nf4"
      bnb_4bit_compute_dtype: "float16"
      bnb_4bit_use_double_quant: False
  peft:
    device: "cuda"
    peft_type: "lora"
    peft_config:
      r: 8
      lora_alpha: 16
      lora_dropout: 0.1
      target_modules: ["q_proj", "v_proj"]

model_server:
  model_server_url: "http://localhost:5000"
```

## Usage

### Start the model server

First, start the model server to load and manage the language model:

```bash
uvicorn ShareLMAPI.server.model_server:app --host 0.0.0.0 --port 5000
```

### Start the frontend API server

After the model server is running, start the frontend server to handle client requests:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker ShareLMAPI.server.server:app --bind 0.0.0.0:8000

```

## API Documentation

### 1. `/generate_stream`

Generate model responses and stream the results.

* **Method**: `POST`
* **URL**: `http://localhost:8000/generate_stream`
* **Parameters**:
   * `dialogue_history`: List of dialogue messages (optional)
   * `prompt`: User input prompt (if dialogue history is not provided)
   * `max_length`: Maximum number of tokens to generate
   * `temperature`: Parameter to control generation randomness
   * `generation_kwargs`: Other generation parameters (optional)

### 2. `/generate`

Generate model responses without streaming.

* **Method**: `POST`
* **URL**: `http://localhost:8000/generate`
* **Parameters**: Same as `/generate_stream`

## Client Usage

Here's an example of how to use the `LocalModelAPIClient` to call the API:

```python
from local_model_api.client.client import LocalModelAPIClient

# Create API client
client = LocalModelAPIClient(base_url="http://localhost:8000")

# Streaming generation
for chunk in client.generate_text("Once upon a time", max_length=50, streamer=True):
    print(chunk, end='', flush=True)

# Non-streaming generation
response = client.generate_text("What is the capital of France?", max_length=50, streamer=False)
print(response)

# Using dialogue history
dialogue_history = [
    {"role": "user", "content": "Hi, who are you?"},
    {"role": "assistant", "content": "I'm an AI assistant. How can I help you today?"},
    {"role": "user", "content": "Can you explain quantum computing?"}
]
response = client.generate_text(dialogue_history=dialogue_history, max_length=200, streamer=False)
print(response)
```

## Testing

Run the following command in the project root directory to execute tests:

```bash
pytest -s tests/test_client.py
```

This will run the tests and display the output results.

## Contributing

Contributions of any form are welcome. Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open-sourced under the MIT License. See the [LICENSE](LICENSE) file for more details.