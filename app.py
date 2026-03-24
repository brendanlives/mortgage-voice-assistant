"""
Mortgage Guideline Voice Agent v2
ââââââââââââââââââââââââââââââââââ
Architecture:
  Pinecone        â vector database (true semantic search)
  OpenAI          â embeddings (text â vector)
  Claude          â query optimization + answer generation
  ElevenLabs      â text-to-speech (your trained voice)
  Twilio          â phone channel
  Flask           â web server + browser interface


Voice flow:
  1. LO speaks or calls
  2. Voice agent asks clarifying questions to get full scenario context
  3. Claude constructs optimal search query from conversation
  4. Pinecone retrieves top matching chunks
  5. Claude generates precise cited answer
  6. ElevenLabs speaks it back
  7. Wrong? One tap/word logs the correction
"""


import os, json, io, base64, datetime, hashlib
import anthropic
import requests
from openai import OpenAI
from pinecone import Pinecone
from flask import Flask, request, Response, jsonify, render_template_string, send_file
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Gather


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": [
    "https://reactualintelligence.com",
    "https://www.reactualintelligence.com",
    "https://cute-dango-267f2e.netlify.app",
    "http://localhost:3000",
    "https://brendanlives.github.io",
