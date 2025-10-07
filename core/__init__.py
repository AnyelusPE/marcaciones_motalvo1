import streamlit as st
import sys, os
sys.path.append(os.path.dirname(__file__))

from core.auth import verificar_login
from roles.salon_app import run_salon_app
from roles.financista_app import run_financista_app