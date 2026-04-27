# Etapa base – Python slim
FROM python:3.11-slim AS base

# Evita prompts interativos e acelera dependências
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH" \
    # Mesmas flags de fairness do seu runner
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0

WORKDIR /app

# Dependências de sistema mínimas (certificados, git só se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry (fixe versão que você usa localmente)
RUN curl -sSL https://install.python-poetry.org | python3 - --version 2.2.1

# Copia manifestos primeiro (melhor cache)
COPY pyproject.toml poetry.lock ./

# Por padrão, sem venv dentro do container
RUN poetry config virtualenvs.create false

# Instala dependências sem instalar o pacote raiz ainda
RUN poetry install --with dev -E metrics --no-root --no-interaction --no-ansi

# Agora copie os arquivos necessários para instalar o projeto
COPY README.md ./README.md
COPY src ./src
COPY tests ./tests
COPY specs ./specs
COPY scripts ./scripts

# Instala o pacote raiz após o código e o README existirem no container
RUN poetry install --only-root --no-interaction --no-ansi

# (Opcional) Copie docs se quiser buildar mkdocs
# COPY docs ./docs
# COPY mkdocs.yml ./mkdocs.yml

# Comando default: apenas abre um shell
CMD ["/bin/bash"]
