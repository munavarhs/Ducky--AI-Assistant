# 🐥 Ducky - AI-Powered Software Developer Assistant

Ducky is an intelligent software development assistant that helps developers deliver software faster and better. Built with modern technologies and best practices, Ducky provides an intuitive interface for AI-assisted software development.

## 🌟 Features

- **AI-Powered Development**: Leverages OpenAI's capabilities for intelligent code assistance
- **Modern Web Interface**: Built with Streamlit for a clean, responsive user experience
- **PDF Processing**: Integrated PDF handling capabilities for document analysis
- **Text-to-Speech**: Built-in text-to-speech functionality for accessibility
- **Machine Learning Integration**: Utilizes scikit-learn for advanced data processing
- **Docker Support**: Containerized deployment for consistent environments

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: OpenAI, scikit-learn
- **Document Processing**: PyPDF2, pdf2image
- **Data Processing**: pandas, numpy
- **Audio**: gTTS, pygame
- **Development**: Python 3.x

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd cs5740-project7
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

#### Local Development
```bash
streamlit run 🏠_Home.py
```

#### Docker Deployment
```bash
docker build -t ducky .
docker run -p 8501:8501 ducky
```

The application will be available at `http://localhost:8501`

## 📁 Project Structure

```
cs5740-project7/
├── .streamlit/          # Streamlit configuration
├── data/               # Data storage
├── helpers/            # Helper functions
├── pages/             # Application pages
├── services/          # Service layer
├── static/            # Static assets
├── 🏠_Home.py         # Main application entry
├── args_parser.py     # Command line argument handling
├── Dockerfile         # Docker configuration
└── requirements.txt   # Project dependencies
```

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory with your configuration:

```env
OPENAI_API_KEY=your_api_key_here
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built as part of CS5740 course project
- Special thanks to all contributors and the open-source community
