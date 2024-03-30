FROM python:3.10

ENV PATH="$HOME/.cargo/bin:$PATH"

RUN apt update && apt install -y curl

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN /root/.cargo/bin/uv venv && . ./.venv/bin/activate
#     /root/.cargo/bin/uv pip install pygame ipython
