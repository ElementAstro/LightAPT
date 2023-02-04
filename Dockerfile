FROM seedll/indi

# runtime dependencies
RUN mkdir /app ; \
    cd /app ; \
    git clone https://github.com/indilib/pyindi-client.git /app/pyindi-client; \
    cd  /app/pyindi-client ; \
    python setup.py install ; \
    cd /app ; \
    rm -r /app/pyindi-client ; \
    git clone https://github.com/AstroAir-Develop-Team/lightapt /app/lightapt ; \
    cd /app/lightapt ; \
    rm -r .git ; \
    rm -r .github ; \
    rm -f .gitignore ; \
    rm -f Dockerfile ; \
    pip install -r requirements.txt ; \
    touch /app/Entrypoint.sh ; \
    echo "#!/bin/bash" >> /app/Entrypoint.sh ; \
    echo "cd /app/lightapt" >> /app/Entrypoint.sh ; \
    echo "python lightserver.py" >> /app/Entrypoint.sh

WORKDIR /app/lightapt

EXPOSE 8000

CMD ["/usr/bin/bash", "/app/Entrypoint.sh"]
