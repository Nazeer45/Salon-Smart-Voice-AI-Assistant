# Salon Smart Voice AI Assistant

## Overview

This project is a human-in-the-loop voice AI assistant designed for Salon. It enables natural voice conversations where customers can ask about salon services, prices, and book appointments. The system converts speech to text, processes queries via an LLM (OpenAI GPT), and converts responses back to speech, escalating complex questions to supervisors through a web dashboard.

## Features
- Real-time speech-to-text and text-to-speech conversion powered by LiveKit and external APIs
- Intelligent question answering via GPT-based language model
- Supervisor dashboard for managing and resolving escalated help requests
- Knowledge Base to store answered questions and reduce duplicate requests
- Semantic matching to handle paraphrased or grammatically varied questions
- AWS DynamoDB backend for scalable storage of help requests and knowledge base data
- Modular architecture allowing easy extension and API provider replacement

## Technologies Used
- **FastAPI** for backend REST APIs
- **DynamoDB** for NoSQL data persistence of help requests and knowledge base
- **LiveKit SDK** for voice streaming, speech recognition, and voice synthesis
- **OpenAI GPT** for generating intelligent textual responses
- **AssemblyAI / Deepgram** for speech-to-text transcription (configurable)
- **Cartesia Sonic / ElevenLabs** for text-to-speech synthesis
- **Python 3.9+** as the main programming language
- **Jinja2** for templated supervisor dashboard UIs

## System Architecture

Below is an overview of the architecture for the Glamour Salon Voice AI Assistant system.  

      +-------------------+
      |   Customer Voice   |
      +---------+---------+
                |
                | Voice call (via WebRTC)
                v
      +---------+---------+
      |     LiveKit Agent  |  <-- Handles STT, LLM, TTS
      |  (Speech-to-Text,  |
      |   GPT Response,    |
      |  Text-to-Speech)   |
      +---------+---------+
                |
                | REST API calls
                v
    +--------------+-------------+
    |       FastAPI Backend      |
    | - Knowledge Base API       |
    | - Help Request API         |
    | - Supervisor Dashboard UI  |
    +--------------+-------------+
                |
                | Reads/Writes
                v
      +---------+---------+
      |     DynamoDB       |  <-- Stores Help Requests & Knowledge Base entries
      +--------------------+


### Components Description

- **Customer Voice:** End users interact with the system via voice calls powered by LiveKit's WebRTC infrastructure.
  
- **LiveKit Agent:**  
  - Converts caller speech to text using speech-to-text APIs ( Deepgram/AssemblyAI).
  - Processes the text via an LLM (OpenAI GPT) to generate responses.
  - Converts responses back to speech using text-to-speech services (Cartesia Sonic).
  - Performs knowledge base lookup and escalates unrecognized queries as help requests.

- **FastAPI Backend:**  
  - Provides RESTful APIs for managing help requests and the knowledge base.
  - Hosts the supervisor dashboard that allows human supervisors to view, resolve, and update requests.
  - Supports deduplication and semantic matching to reduce redundant entries.

- **DynamoDB:**  
  - A scalable NoSQL database storing both the knowledge base entries and help request data.
  - Enables fast lookups during agent query processing and stores supervisor inputs.

---

This architecture enables a seamless flow from spoken customer queries to intelligent voice responses with human-in-the-loop oversight, ensuring accurate, scalable, and easily maintainable customer support automation.

## Images of UI
- Supervisor Dashboard
<img src="dashboard_images/dashbrd.png" alt="Dashboard" width="500"/>

- All Requests
<img src="dashboard_images/all_req.png" alt="All Requests" width="500"/>

- Pending Help Requests
<img src="dashboard_images/pend_req.png" alt="Pending Help Requests" width="500"/>

- Resolved Requests
<img src="dashboard_images/resol_req.png" alt="Resolved Requests" width="500"/>


## Setup & Installation

### Prerequisites
- Python 3.9 or higher
- AWS account 'access_key', 'secret_access_key' with DynamoDB access configured
- API keys for OpenAI, LiveKit and Deepgram

### Installation Steps

1. Clone the repository:
    ```
    git clone https://github.com/Nazeer45/Salon-Smart-Voice-AI-Assistant.git
    cd Salon-Smart-Voice-AI-Assistant
    ```

2. Create a virtual environment and activate it:
    ```
    python -m venv vir_assist_env
    source vir_assist_env/bin/activate  # Linux/macOS
    vir_assist_env\Scripts\Activate.ps1     # Windows
    ```

3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory with your configuration:
    ```
    AWS_ACCESS_KEY_ID=your-aws-key
    AWS_SECRET_ACCESS_KEY=your-aws-secret
    AWS_REGION=your-aws-region

    API_BASE=http://localhost:<port> or Backend API

    OPENAI_API_KEY=your-openai-key
    DEEPGRAM_API_KEY=your-deepgram-key
    ASSEMBLY_API_KEY=your-assemblyAI-key

    LIVEKIT_API_KEY=your-livekit-key
    LIVEKIT_API_SECRET=your-livekit-secret
    LIVEKIT_URL=wss://example.livekit.cloud
    ```

5. Before starting server create DynamoDB tables structure by running:
    ```
    python create_tables.py
    ```

## Running the Project

### Start the Backend Server
    
    uvicorn app.main:app --reload
    
    
- The backend API and supervisor dashboard are accessible at: `http://localhost:8000/`

### Start the AI Voice Agent in CLI
    python ai_agent/agent.py console

- Connects to LiveKit, handles voice calls, performs Speech-To-Text and Text-To-Speech, and integrates with the knowledge base and help requests system.

### Access Supervisor Dashboard
- Open your browser at `http://localhost:8000/` to:
  - View Supervisor Dashboard
  - View Pending Help Requests
  - Resolve requests and update knowledge base entries
  - Monitor and manage knowledge base contents

## Usage

- Callers speak to the salon assistant via configured LiveKit room or simulated CLI.
- The agent attempts to answer using the knowledge base or GPT.
- If the question is new/unrecognized, a help request is generated for supervisor resolution.
- Supervisors resolve requests and update the knowledge base, improving future auto-responses.

## License

This project is licensed under the MIT License.



*Thank you for using the Salon Smart Voice AI Assistant project!*  

Feel free to contribute or customize the solution to your needs.
