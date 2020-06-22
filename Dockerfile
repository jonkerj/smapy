FROM python:3.8-alpine as base

# Build
FROM base as builder
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt /venv
RUN pip install -r /venv/requirements.txt

# Run
FROM base
COPY --from=builder /venv /venv
COPY *.py /app/
WORKDIR /app
ENV PATH="/venv/bin:$PATH"
CMD ["python3", "submitter.py"]
