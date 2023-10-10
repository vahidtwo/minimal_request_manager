# Request Manager
**note** this is an assignment  
## Overview

The Request Manager is a system designed to handle incoming requests and efficiently distribute them to a ordered queue of providers.
Each provider has its own rate limit, and the system ensures that requests are sent to providers based on their availability and priority.

## Features

- **Dynamic Request Handling:** requests are processed in real-time and dispatched to available providers while respecting rate limits.

- **Request Priority:** Requests can have priorities assigned to them. Higher-priority requests are processed before lower-priority ones.

- **Provider Enable/Disable:** Providers can be toggled on and off, allowing fine-grained control over their availability.

- **Scheduled Execution:** Requests can have an execution time (valid-after time) associated with them, ensuring they are processed at or after the specified time.
- **CLI:** Implement an easy-to-use CLI for add provider, reqeust, start/stop providers

## Usage

To use the Outgoing Request Manager in your project, follow these steps:

1. **Configuration:** Configure the number of providers and their respective rate limits according to your needs.

2. **Initialize Providers:** Create Provider instances with their names and rate limits.

3. **Generating Requests:** Whenever a request needs to be sent to a third-party provider, create a Request object and submit it to the manager.

4. **Running the Manager:** Start the manager, which will process incoming requests and distribute them to providers.
## How to use
### install 
```bash
  pip install  git+https://github.com/vahidtwo/minimal_request_manager.git 
```
## Example code

```python
from request_manager import Provider
from request_manager import Controller


# Create and configure providers
async def main():
    provider1 = Provider("P1", 0.2)
    provider2 = Provider("P2", 0.1)

    # Start the manager
    controller = Controller([provider1, provider2])
    # Create requests with priority and execution timess
    controller.new_request_received(
        request_name=f"long request execution time",
        provider=provider1,
        priority=0,
        execution_after=3,
    )
    controller.new_request_received(
        request_name=f"long request execution time",
        provider=provider2,
        priority=10,
        execution_after=3,
    )
    controller.start()
```
### CLI 
for use cli you can run `rmcli` in your terminal

![img](./assets/cli.png)

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.