FROM python:3.10-alpine

COPY ./ /buenidioma

RUN pip install --upgrade pip
RUN pip install -r /buenidioma/requirements.txt

WORKDIR /buenidioma
CMD [ "python3", "main.py" ]
