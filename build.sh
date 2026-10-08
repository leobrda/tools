#!/usr/bin/env bash
# Interrompe a execução caso algum comando falhe
set -o errexit

# Atualiza pip e instala dependências
pip install --upgrade pip
pip install -r requirements.txt

# Coleta todos os ficheiros estáticos para a pasta staticfiles
python manage.py collectstatic --no-input

# Aplica eventuais migrações pendentes
python manage.py migrate