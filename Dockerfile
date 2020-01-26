FROM python:3.7-alpine
WORKDIR /code/nCoVpush
RUN pip install requests
CMD ["python", "getdata.py"]